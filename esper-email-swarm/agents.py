"""
ESPER Email Swarm - Agent System

Implements the 5-agent semantic swarm:
- Urgency Agent: Detects time pressure and deadlines
- Importance Agent: Assesses long-term impact
- Topic Agent: Extracts dominant subject matter
- Tone Agent: Analyzes emotional qualities
- Action Agent: Determines required next steps

Each agent produces a VSE packet representing its specialized analysis.
The agents are deterministic (same input → same output) and fully auditable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime

from .model import (
    VSEPacket,
    IntentSpine,
    AffectLattice,
    semantic_hash,
)


@dataclass(frozen=True)
class AgentConfig:
    """Configuration for a specialized semantic agent"""
    role: str
    description: str
    system_prompt: str


# Agent configurations (these define the "personality" of each agent)
AGENTS: Dict[str, AgentConfig] = {
    "urgency": AgentConfig(
        role="urgency",
        description="Detects time pressure, deadlines, and emotional charge",
        system_prompt="You detect temporal urgency, deadline pressure, and time-sensitive signals in communication.",
    ),
    "importance": AgentConfig(
        role="importance",
        description="Detects long-term impact on relationships, money, health, career, legal matters",
        system_prompt="You assess long-term significance and impact across life domains: career, finances, health, relationships, legal.",
    ),
    "topic": AgentConfig(
        role="topic",
        description="Extracts the single most dominant topic or project",
        system_prompt="You identify the primary subject matter and semantic domain of communication.",
    ),
    "tone": AgentConfig(
        role="tone",
        description="Detects sentiment, relationship warmth, tension, and formality",
        system_prompt="You analyze emotional tone, relationship warmth, conflict signals, and communication formality.",
    ),
    "action": AgentConfig(
        role="action",
        description="Determines the next required physical action",
        system_prompt="You decide what concrete action the recipient should take: reply, schedule, delegate, archive, etc.",
    ),
}


# ============================================================================
# Urgency Agent
# ============================================================================

# Urgency keywords with weighted importance
URGENCY_KEYWORDS = {
    'critical': 1.0,
    'urgent': 0.9,
    'emergency': 1.0,
    'asap': 0.9,
    'immediately': 0.9,
    'today': 0.7,
    'tonight': 0.7,
    'deadline': 0.8,
    'due': 0.6,
    'expiring': 0.7,
    'expires': 0.7,
    'time-sensitive': 0.8,
    'time sensitive': 0.8,
    'quickly': 0.5,
    'quick': 0.5,
    'rush': 0.7,
    'hurry': 0.6,
}

# Temporal patterns that indicate deadlines
TEMPORAL_PATTERNS = [
    r'\d{1,2}/\d{1,2}(/\d{2,4})?',  # Date: 12/15 or 12/15/2024
    r'\d{1,2}:\d{2}\s*[ap]m',        # Time: 3:30 pm
    r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',  # Days
    r'(tomorrow|tonight|this\s+(morning|afternoon|evening|week))',  # Relative time
    r'by\s+(tomorrow|tonight|friday|next\s+week)',  # Deadline phrases
    r'before\s+\d{1,2}[:/]\d{1,2}', # Before time
    r'(in|within)\s+\d+\s+(hour|day|week)s?',  # Within timeframe
]


def analyze_urgency(text: str, metadata: Dict) -> Tuple[float, float, str]:
    """
    Analyze temporal urgency and deadline pressure.
    
    Returns:
        (urgency_score, tension_score, gloss)
    """
    text_lower = text.lower()
    
    # Score keyword urgency (weighted)
    urgency_score = 0.0
    keyword_count = 0
    for keyword, weight in URGENCY_KEYWORDS.items():
        count = text_lower.count(keyword)
        if count > 0:
            urgency_score += weight * min(count, 3)  # Cap at 3 occurrences
            keyword_count += count
    
    # Normalize by occurrence count
    if keyword_count > 0:
        urgency_score = min(1.0, urgency_score / 3.0)
    
    # Check for temporal patterns (deadline indicators)
    has_temporal = False
    temporal_count = 0
    for pattern in TEMPORAL_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            has_temporal = True
            temporal_count += len(matches)
    
    # Boost urgency if temporal patterns present
    if has_temporal:
        urgency_score = min(1.0, urgency_score + 0.3)
    
    # Check for exclamation marks (emotional urgency)
    exclamation_count = text.count('!')
    if exclamation_count >= 2:
        urgency_score = min(1.0, urgency_score + 0.2)
    
    # Tension correlates with urgency
    tension_score = min(1.0, urgency_score * 0.8)
    
    # Generate gloss
    if urgency_score > 0.7:
        gloss = "Critical time pressure with immediate deadline"
    elif urgency_score > 0.4:
        gloss = "Moderate urgency with temporal constraints" if has_temporal else "Some time pressure indicated"
    else:
        gloss = "Low urgency, flexible timeline"
    
    return urgency_score, tension_score, gloss


# ============================================================================
# Importance Agent
# ============================================================================

# Domain-specific keywords indicating long-term importance
IMPORTANCE_DOMAINS = {
    'financial': {
        'keywords': ['invoice', 'payment', 'bill', 'tax', 'taxes', 'budget', 'cost', 'price', 
                     'money', 'dollar', 'invest', 'investment', 'loan', 'debt', 'salary', 'raise'],
        'weight': 0.9,
    },
    'health': {
        'keywords': ['health', 'medical', 'doctor', 'hospital', 'insurance', 'prescription',
                     'appointment', 'diagnosis', 'treatment', 'therapy', 'surgery'],
        'weight': 1.0,
    },
    'legal': {
        'keywords': ['legal', 'contract', 'agreement', 'compliance', 'liability', 'lawsuit',
                     'attorney', 'lawyer', 'court', 'regulation', 'policy'],
        'weight': 0.95,
    },
    'career': {
        'keywords': ['promotion', 'review', 'performance', 'job', 'offer', 'hire', 'interview',
                     'career', 'resignation', 'termination', 'salary', 'position'],
        'weight': 0.85,
    },
    'relationship': {
        'keywords': ['family', 'friend', 'mom', 'dad', 'mother', 'father', 'sister', 'brother',
                     'partner', 'spouse', 'child', 'parent', 'relative'],
        'weight': 0.8,
    },
    'academic': {
        'keywords': ['research', 'publication', 'paper', 'study', 'grant', 'funding',
                     'conference', 'presentation', 'thesis', 'dissertation', 'academic'],
        'weight': 0.85,
    },
}


def analyze_importance(text: str, metadata: Dict) -> Tuple[float, str, str]:
    """
    Analyze long-term importance across life domains.
    
    Returns:
        (importance_score, dominant_domain, gloss)
    """
    text_lower = text.lower()
    
    # Score each domain
    domain_scores: Dict[str, float] = {}
    for domain, config in IMPORTANCE_DOMAINS.items():
        score = 0
        for keyword in config['keywords']:
            count = text_lower.count(keyword)
            if count > 0:
                score += count * config['weight']
        if score > 0:
            domain_scores[domain] = score
    
    # Calculate overall importance
    if domain_scores:
        # Get dominant domain
        dominant_domain = max(domain_scores.items(), key=lambda x: x[1])[0]
        total_score = sum(domain_scores.values())
        importance_score = min(1.0, total_score / 5.0)
    else:
        dominant_domain = "general"
        importance_score = 0.0
    
    # Generate gloss
    if importance_score > 0.6:
        gloss = f"Significant {dominant_domain} implications with long-term impact"
    elif importance_score > 0.3:
        gloss = f"Moderate {dominant_domain} matter requiring attention"
    else:
        gloss = f"Routine {dominant_domain} communication"
    
    return importance_score, dominant_domain, gloss


# ============================================================================
# Topic Agent
# ============================================================================

def analyze_topic(text: str, metadata: Dict) -> Tuple[str, str]:
    """
    Extract dominant topic or project.
    
    Returns:
        (topic, gloss)
    """
    text_lower = text.lower()
    
    # Try importance domains first (most specific)
    for domain, config in IMPORTANCE_DOMAINS.items():
        for keyword in config['keywords']:
            if keyword in text_lower:
                return domain, f"Primary topic: {domain}"
    
    # Extract from subject line if available
    subject = metadata.get('subject', '')
    if subject:
        # Remove common prefixes
        subject_clean = re.sub(r'^(re:|fwd:|fw:)\s*', '', subject, flags=re.IGNORECASE).strip()
        
        # Extract first meaningful word (4+ chars)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', subject_clean)
        if words:
            topic = words[0].lower()
            return topic, f"Primary topic: {topic}"
    
    # Fallback: extract common nouns from body
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text_lower)
    
    # Filter out common stop words
    stop_words = {'that', 'this', 'with', 'from', 'have', 'will', 'your', 'they',
                  'been', 'were', 'said', 'would', 'there', 'their', 'what', 'about'}
    
    word_freq: Dict[str, int] = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    if word_freq:
        topic = max(word_freq.items(), key=lambda x: x[1])[0]
        return topic, f"Primary topic: {topic}"
    
    return "general", "Primary topic: general communication"


# ============================================================================
# Tone Agent
# ============================================================================

WARMTH_INDICATORS = [
    'thanks', 'thank you', 'appreciate', 'grateful', 'gratitude',
    'love', 'loving', 'loved', 'dear', 'kind', 'kindly',
    'hope you', 'hope all is well', 'hope you\'re well',
    'best wishes', 'best regards', 'warm regards',
    'cheers', 'xo', 'hugs', '❤', '💕', '🙏', '😊',
]

TENSION_INDICATORS = [
    'sorry', 'apologize', 'unfortunately', 'regret', 'concern', 'concerned',
    'worry', 'worried', 'issue', 'problem', 'trouble', 'difficult',
    'disappointed', 'frustrat', 'upset', 'angry', 'unacceptable',
    'mistake', 'error', 'wrong', 'incorrect', 'failed',
]

FORMALITY_INDICATORS = [
    'dear sir', 'dear madam', 'to whom', 'sincerely', 'regards',
    'respectfully', 'cordially', 'please be advised', 'kindly note',
    'herein', 'pursuant', 'whereas', 'hereby',
    'mr.', 'ms.', 'mrs.', 'dr.', 'prof.',
]


def analyze_tone(text: str, metadata: Dict) -> Tuple[float, float, float, str]:
    """
    Analyze emotional tone and relationship warmth.
    
    Returns:
        (warmth, tension, formality, gloss)
    """
    text_lower = text.lower()
    
    # Calculate warmth
    warmth_count = sum(1 for indicator in WARMTH_INDICATORS if indicator in text_lower)
    warmth = min(1.0, warmth_count / 5.0)
    
    # Calculate tension
    tension_count = sum(1 for indicator in TENSION_INDICATORS if indicator in text_lower)
    tension = min(1.0, tension_count / 5.0)
    
    # Calculate formality
    formality_count = sum(1 for indicator in FORMALITY_INDICATORS if indicator in text_lower)
    formality = min(1.0, formality_count / 3.0)
    
    # Adjust for personal relationships (in sender)
    sender = metadata.get('sender', '').lower()
    personal_indicators = ['mom', 'dad', 'mother', 'father', 'sister', 'brother', 
                          'family', 'friend', 'personal']
    if any(ind in sender for ind in personal_indicators):
        warmth = min(1.0, warmth + 0.3)
        formality = max(0.0, formality - 0.4)
    
    # Generate gloss
    tone_descriptors = []
    if warmth > 0.5:
        tone_descriptors.append("warm")
    if tension > 0.5:
        tone_descriptors.append("tense")
    if formality > 0.6:
        tone_descriptors.append("formal")
    elif formality < 0.3:
        tone_descriptors.append("casual")
    
    if not tone_descriptors:
        tone_descriptors.append("neutral")
    
    gloss = f"Tone: {' and '.join(tone_descriptors)}"
    
    return warmth, tension, formality, gloss


# ============================================================================
# Action Agent
# ============================================================================

ACTION_PATTERNS = {
    'reply': {
        'patterns': [
            r'please\s+(respond|reply|get\s+back)',
            r'let\s+me\s+know',
            r'waiting\s+to\s+hear',
            r'looking\s+forward\s+to\s+your',
            r'\?$',  # Ends with question
        ],
        'action': 'Reply within 24 hours',
    },
    'schedule': {
        'patterns': [
            r'meeting', r'call', r'schedule', r'calendar',
            r'available', r'availability', r'book\s+a\s+time',
            r'let\'s\s+meet', r'coffee', r'lunch', r'dinner',
        ],
        'action': 'Schedule a meeting or call',
    },
    'review': {
        'patterns': [
            r'please\s+review', r'feedback', r'look\s+at',
            r'check\s+out', r'take\s+a\s+look', r'attached',
            r'document', r'draft', r'proposal',
        ],
        'action': 'Review attached materials or document',
    },
    'task': {
        'patterns': [
            r'please\s+\w+', r'could\s+you', r'would\s+you',
            r'can\s+you', r'need\s+you\s+to', r'action\s+required',
        ],
        'action': 'Take specific action mentioned in email',
    },
    'fyi': {
        'patterns': [
            r'fyi', r'for\s+your\s+information', r'heads\s+up',
            r'just\s+letting\s+you\s+know', r'wanted\s+to\s+inform',
            r'update', r'newsletter',
        ],
        'action': 'Read and file for reference',
    },
}


def analyze_action(text: str, metadata: Dict, urgency: float, importance: float) -> Tuple[str, str]:
    """
    Determine required next action.
    
    Returns:
        (action_category, action_gloss)
    """
    text_lower = text.lower()
    
    # Score each action type
    action_scores: Dict[str, int] = {}
    for action_type, config in ACTION_PATTERNS.items():
        score = 0
        for pattern in config['patterns']:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            score += len(matches)
        if score > 0:
            action_scores[action_type] = score
    
    # Determine primary action
    if action_scores:
        primary_action = max(action_scores.items(), key=lambda x: x[1])[0]
        action_gloss = ACTION_PATTERNS[primary_action]['action']
    else:
        # Fallback based on urgency/importance
        if urgency > 0.7:
            action_gloss = "Reply within 24 hours"
        elif importance > 0.6:
            action_gloss = "Schedule response in next few days"
        else:
            action_gloss = "Archive after review"
    
    return action_gloss, action_gloss


# ============================================================================
# Main Agent Orchestrator
# ============================================================================

def analyze_email_agents(full_text: str, metadata: Optional[Dict] = None) -> Dict[str, VSEPacket]:
    """
    Run all 5 agents on the provided email text.
    
    This is deliberately heuristic and deterministic:
    - No external API calls
    - No randomness
    - Fully explainable
    - Same input → same output
    
    Args:
        full_text: Complete email text (headers + body)
        metadata: Optional metadata dict with sender, subject, date
        
    Returns:
        Dictionary mapping agent role to VSE packet
    """
    if metadata is None:
        metadata = {}
    
    # Run each agent
    urgency_score, tension_score, urgency_gloss = analyze_urgency(full_text, metadata)
    importance_score, domain, importance_gloss = analyze_importance(full_text, metadata)
    topic, topic_gloss = analyze_topic(full_text, metadata)
    warmth, tone_tension, formality, tone_gloss = analyze_tone(full_text, metadata)
    action_str, action_gloss = analyze_action(full_text, metadata, urgency_score, importance_score)
    
    packets: Dict[str, VSEPacket] = {}
    
    # Urgency packet
    packets["urgency"] = VSEPacket(
        agent_role="urgency",
        intent_spine=IntentSpine(
            urgency=urgency_score,
            importance=0.0,
            warmth=0.0,
            tension=tension_score,
            confidence=0.95,
        ),
        affect_lattice=AffectLattice(
            fear=tension_score * 0.8,
        ),
        semantic_motif=semantic_hash(f"urgency:{urgency_score}:{full_text[:100]}"),
        gloss=urgency_gloss,
        confidence=0.95,
    )
    
    # Importance packet
    packets["importance"] = VSEPacket(
        agent_role="importance",
        intent_spine=IntentSpine(
            urgency=0.0,
            importance=importance_score,
            warmth=0.0,
            tension=0.0,
            confidence=0.9,
        ),
        affect_lattice=AffectLattice(),
        semantic_motif=semantic_hash(f"importance:{domain}:{full_text[:100]}"),
        gloss=importance_gloss,
        confidence=0.9,
    )
    
    # Topic packet
    packets["topic"] = VSEPacket(
        agent_role="topic",
        intent_spine=IntentSpine(
            urgency=0.0,
            importance=0.0,
            warmth=0.0,
            tension=0.0,
            confidence=0.85,
        ),
        affect_lattice=AffectLattice(),
        semantic_motif=semantic_hash(f"topic:{topic}"),
        gloss=topic_gloss,
        confidence=0.85,
    )
    
    # Tone packet
    packets["tone"] = VSEPacket(
        agent_role="tone",
        intent_spine=IntentSpine(
            urgency=0.0,
            importance=0.0,
            warmth=warmth,
            tension=tone_tension,
            confidence=0.9,
        ),
        affect_lattice=AffectLattice(
            joy=warmth * 0.9,
            fear=tone_tension * 0.7,
            trust=warmth * 0.8,
        ),
        semantic_motif=semantic_hash(f"tone:{warmth}:{tone_tension}:{formality}"),
        gloss=tone_gloss,
        confidence=0.9,
    )
    
    # Action packet
    packets["action"] = VSEPacket(
        agent_role="action",
        intent_spine=IntentSpine(
            urgency=urgency_score,
            importance=importance_score,
            warmth=warmth,
            tension=0.0,
            confidence=0.9,
        ),
        affect_lattice=AffectLattice(),
        semantic_motif=semantic_hash(f"action:{action_str}"),
        gloss=action_gloss,
        confidence=0.9,
    )
    
    return packets
