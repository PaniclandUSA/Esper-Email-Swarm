"""
ESPER Email Swarm - Multi-Agent Semantic Analysis

This module implements the 5 specialized agents that analyze
different semantic dimensions of email messages:
- Urgency Agent: Time pressure and deadlines
- Importance Agent: Long-term impact and significance
- Topic Agent: Subject matter identification
- Tone Agent: Emotional warmth and relationship signals
- Action Agent: Required next steps

All agents are deterministic, explainable, and produce VSE packets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import re

from .model import (
    VSEPacket,
    IntentSpine,
    AffectLattice,
    semantic_hash,
)


# =============================================================================
# Agent Configuration
# =============================================================================

@dataclass(frozen=True)
class AgentConfig:
    """Configuration for a specialized semantic agent."""
    role: str
    description: str


AGENTS: Dict[str, AgentConfig] = {
    "urgency": AgentConfig(
        role="urgency",
        description="Detects time pressure, deadlines, and emotional charge.",
    ),
    "importance": AgentConfig(
        role="importance",
        description="Detects long-term impact on relationships, money, health, legal matters.",
    ),
    "topic": AgentConfig(
        role="topic",
        description="Extracts the single most dominant topic or project.",
    ),
    "tone": AgentConfig(
        role="tone",
        description="Detects sentiment and relationship warmth/tension.",
    ),
    "action": AgentConfig(
        role="action",
        description="Determines next physical action: reply, schedule, delegate, archive.",
    ),
}


# =============================================================================
# Urgency Agent
# =============================================================================

def _analyze_urgency(text: str) -> tuple[float, str]:
    """
    Detect time pressure and deadline urgency.
    
    Looks for:
    - Urgency keywords (urgent, asap, immediately)
    - Deadline mentions (today, tomorrow, Friday)
    - Time expressions (by 5pm, before EOD)
    - Emotional intensity (!!!, multiple exclamation marks)
    
    Args:
        text: Email content (lowercased)
        
    Returns:
        (urgency_score, gloss) where score is in [0, 1]
    """
    urgency_patterns = [
        (r'\b(urgent|asap|immediately|right away|at once)\b', 0.3),
        (r'\b(today|tonight|this morning|this afternoon)\b', 0.25),
        (r'\b(deadline|due|expire|expiring)\b', 0.2),
        (r'\b(quick|quickly|fast|hurry)\b', 0.15),
        (r'!{2,}', 0.2),  # Multiple exclamation marks
        (r'\b(now|by tomorrow|before friday)\b', 0.2),
    ]
    
    score = 0.0
    for pattern, weight in urgency_patterns:
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        score += matches * weight
    
    score = min(1.0, score)
    
    # Generate gloss
    if score > 0.7:
        gloss = "Critical time pressure with immediate deadline"
    elif score > 0.4:
        gloss = "Moderate urgency with temporal constraints"
    else:
        gloss = "Low urgency, flexible timeline"
    
    return score, gloss


# =============================================================================
# Importance Agent
# =============================================================================

def _analyze_importance(text: str) -> tuple[float, str]:
    """
    Detect long-term significance and impact.
    
    Analyzes domains:
    - Financial (money, invoice, payment, budget)
    - Health (medical, doctor, hospital, insurance)
    - Legal (contract, agreement, compliance, liability)
    - Career (promotion, review, performance, job)
    - Relationship (family, friend, partner, love)
    
    Args:
        text: Email content (lowercased)
        
    Returns:
        (importance_score, gloss) where score is in [0, 1]
    """
    importance_domains = {
        'financial': [
            r'\$\d+', r'\bmoney\b', r'\binvoice\b', r'\bpayment\b',
            r'\bbudget\b', r'\bcost\b', r'\btax(es)?\b', r'\bfunding\b'
        ],
        'health': [
            r'\bhealth\b', r'\bmedical\b', r'\bdoctor\b', r'\bhospital\b',
            r'\binsurance\b', r'\bprescription\b', r'\bappointment\b'
        ],
        'legal': [
            r'\blegal\b', r'\bcontract\b', r'\bagreement\b', r'\bcompliance\b',
            r'\bliability\b', r'\blawsuit\b', r'\bterms\b'
        ],
        'career': [
            r'\bpromotion\b', r'\breview\b', r'\bperformance\b', r'\bjob\b',
            r'\bsalary\b', r'\braise\b', r'\boffer\b', r'\binterview\b'
        ],
        'relationship': [
            r'\bfamily\b', r'\bmom\b', r'\bdad\b', r'\bpartner\b',
            r'\bwife\b', r'\bhusband\b', r'\bchild(ren)?\b'
        ],
        'academic': [
            r'\bresearch\b', r'\bpartnership\b', r'\bacademic\b',
            r'\bpublication\b', r'\bpaper\b', r'\bconference\b'
        ],
    }
    
    domain_scores = {}
    for domain, patterns in importance_domains.items():
        score = sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)
        if score > 0:
            domain_scores[domain] = score
    
    # Calculate overall importance
    total_matches = sum(domain_scores.values())
    importance_score = min(1.0, total_matches / 5.0)
    
    # Identify dominant domain
    if domain_scores:
        dominant_domain = max(domain_scores.items(), key=lambda x: x[1])[0]
        gloss = f"Significant {dominant_domain} implications" if importance_score > 0.5 else f"Routine {dominant_domain} matter"
    else:
        dominant_domain = "general"
        gloss = "Low-impact general communication"
    
    return importance_score, gloss


# =============================================================================
# Topic Agent
# =============================================================================

def _analyze_topic(text: str, subject: str = "") -> tuple[str, str]:
    """
    Extract dominant topic or project.
    
    Uses keyword frequency analysis and subject line hints.
    
    Args:
        text: Email body (lowercased)
        subject: Email subject line
        
    Returns:
        (topic_string, gloss)
    """
    # Try to extract from subject first
    subject_lower = subject.lower()
    
    # Predefined topic patterns
    topic_patterns = {
        'taxes': [r'\btax(es)?\b', r'\birs\b', r'\bdeduction\b'],
        'billing': [r'\binvoice\b', r'\bpayment\b', r'\bbill\b'],
        'meetings': [r'\bmeeting\b', r'\bcalendar\b', r'\bschedule\b'],
        'newsletter': [r'\bnewsletter\b', r'\bdigest\b', r'\bupdate\b'],
        'research': [r'\bresearch\b', r'\bstudy\b', r'\bpaper\b'],
        'health': [r'\bhealth\b', r'\bmedical\b', r'\bdoctor\b'],
        'legal': [r'\blegal\b', r'\bcontract\b', r'\bagreement\b'],
    }
    
    # Check patterns
    topic_scores = {}
    combined_text = (subject_lower + " " + text).lower()
    
    for topic, patterns in topic_patterns.items():
        score = sum(len(re.findall(p, combined_text, re.IGNORECASE)) for p in patterns)
        if score > 0:
            topic_scores[topic] = score
    
    if topic_scores:
        topic = max(topic_scores.items(), key=lambda x: x[1])[0]
    else:
        # Fallback: extract most frequent meaningful word from subject
        words = re.findall(r'\b[a-z]{4,}\b', subject_lower)
        stop_words = {'with', 'from', 'about', 'your', 'this', 'that', 'have', 'will'}
        meaningful_words = [w for w in words if w not in stop_words]
        topic = meaningful_words[0] if meaningful_words else "general"
    
    gloss = f"Primary topic: {topic}"
    return topic, gloss


# =============================================================================
# Tone Agent
# =============================================================================

def _analyze_tone(text: str, sender: str = "") -> tuple[float, float, str]:
    """
    Detect emotional warmth and relationship tension.
    
    Analyzes:
    - Warmth indicators (thanks, love, appreciate)
    - Tension indicators (sorry, issue, problem)
    - Formality markers (Dear, Regards, formal structure)
    - Relationship signals from sender
    
    Args:
        text: Email content (lowercased)
        sender: Sender email address
        
    Returns:
        (warmth_score, tension_score, gloss)
    """
    # Warmth indicators
    warmth_patterns = [
        r'\bthanks?\b', r'\bthank you\b', r'\bappreciate\b',
        r'\bgrateful\b', r'\blove\b', r'\bkind\b',
        r':\)', r'❤', r'\bhope you\'?re well\b', r'\bxo\b'
    ]
    
    warmth = sum(len(re.findall(p, text, re.IGNORECASE)) for p in warmth_patterns)
    warmth_score = min(1.0, warmth / 5.0)
    
    # Tension indicators
    tension_patterns = [
        r'\bsorry\b', r'\bunfortunately\b', r'\bconcern(ed)?\b',
        r'\bissue\b', r'\bproblem\b', r'\bworr(y|ied)\b',
        r'\bmistake\b', r'\berror\b', r'\bfailed\b'
    ]
    
    tension = sum(len(re.findall(p, text, re.IGNORECASE)) for p in tension_patterns)
    tension_score = min(1.0, tension / 5.0)
    
    # Adjust for personal relationships from sender
    sender_lower = sender.lower()
    if any(term in sender_lower for term in ['mom', 'dad', 'sister', 'brother', 'family']):
        warmth_score = min(1.0, warmth_score + 0.3)
    
    # Generate gloss
    tone_descriptors = []
    if warmth_score > 0.5:
        tone_descriptors.append("warm")
    if tension_score > 0.5:
        tone_descriptors.append("tense")
    
    if not tone_descriptors:
        tone_descriptors.append("neutral")
    
    gloss = f"Tone: {' and '.join(tone_descriptors)}"
    
    return warmth_score, tension_score, gloss


# =============================================================================
# Action Agent
# =============================================================================

def _analyze_action(urgency: float, importance: float, warmth: float, text: str) -> str:
    """
    Determine recommended next action.
    
    Based on urgency, importance, warmth, and content analysis.
    
    Args:
        urgency: Urgency score from urgency agent
        importance: Importance score from importance agent
        warmth: Warmth score from tone agent
        text: Email content (lowercased)
        
    Returns:
        Action recommendation string
    """
    # Check for specific action indicators
    action_patterns = {
        'reply': [r'\bplease respond\b', r'\blet me know\b', r'\bget back to\b'],
        'schedule': [r'\bmeeting\b', r'\bcall\b', r'\bschedule\b', r'\bavailab(le|ility)\b'],
        'review': [r'\bplease review\b', r'\bfeedback\b', r'\bcheck\b', r'\blook at\b'],
        'pay': [r'\bpayment due\b', r'\binvoice\b', r'\bpay by\b'],
        'sign': [r'\bsign\b', r'\bapprove\b', r'\bauthorize\b'],
    }
    
    detected_actions = []
    for action, patterns in action_patterns.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            detected_actions.append(action)
    
    # Decide based on urgency and detected actions
    if urgency > 0.7:
        if 'reply' in detected_actions:
            return "Reply within 24 hours"
        elif 'schedule' in detected_actions:
            return "Schedule meeting immediately"
        else:
            return "Take immediate action"
    
    if importance > 0.6:
        if 'review' in detected_actions:
            return "Review and respond within 2-3 days"
        elif 'pay' in detected_actions:
            return "Process payment this week"
        elif 'sign' in detected_actions:
            return "Review and sign within a few days"
        else:
            return "Address within the week"
    
    # Check for newsletter/bulk mail
    if 'newsletter' in text or 'unsubscribe' in text:
        return "Read when convenient"
    
    # Personal/warm emails
    if warmth > 0.5:
        return "Reply when convenient"
    
    # Default
    return "Archive after quick scan"


# =============================================================================
# Main Agent Orchestration
# =============================================================================

def analyze_email_agents(
    full_text: str,
    subject: str = "",
    sender: str = ""
) -> Dict[str, VSEPacket]:
    """
    Run all 5 agents on the provided email.
    
    This is the main entry point for semantic analysis. Each agent
    produces a VSEPacket representing its specialized understanding.
    
    All analysis is deterministic and explainable - no external models,
    no randomness, fully auditable.
    
    Args:
        full_text: Complete email content
        subject: Email subject line
        sender: Sender email address
        
    Returns:
        Dictionary mapping agent role to VSEPacket
    """
    text_lower = full_text.lower()
    
    # Run each agent
    urgency_score, urgency_gloss = _analyze_urgency(text_lower)
    importance_score, importance_gloss = _analyze_importance(text_lower)
    topic_str, topic_gloss = _analyze_topic(text_lower, subject)
    warmth_score, tension_score, tone_gloss = _analyze_tone(text_lower, sender)
    action_str = _analyze_action(urgency_score, importance_score, warmth_score, text_lower)
    
    packets: Dict[str, VSEPacket] = {}
    
    # Urgency Packet
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
            fear=tension_score,
        ),
        semantic_motif=semantic_hash(f"urgency:{urgency_score}:{full_text}"),
        gloss=urgency_gloss,
        confidence=0.95,
    )
    
    # Importance Packet
    packets["importance"] = VSEPacket(
        agent_role="importance",
        intent_spine=IntentSpine(
            urgency=0.0,
            importance=importance_score,
            warmth=0.0,
            tension=0.0,
            confidence=0.90,
        ),
        affect_lattice=AffectLattice(),
        semantic_motif=semantic_hash(f"importance:{importance_score}:{full_text}"),
        gloss=importance_gloss,
        confidence=0.90,
    )
    
    # Topic Packet
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
        semantic_motif=semantic_hash(f"topic:{topic_str}"),
        gloss=topic_gloss,
        confidence=0.85,
    )
    
    # Tone Packet
    packets["tone"] = VSEPacket(
        agent_role="tone",
        intent_spine=IntentSpine(
            urgency=0.0,
            importance=0.0,
            warmth=warmth_score,
            tension=tension_score,
            confidence=0.90,
        ),
        affect_lattice=AffectLattice(
            joy=warmth_score,
            fear=tension_score,
            trust=warmth_score,
        ),
        semantic_motif=semantic_hash(f"tone:{warmth_score}:{tension_score}:{full_text}"),
        gloss=tone_gloss,
        confidence=0.90,
    )
    
    # Action Packet
    packets["action"] = VSEPacket(
        agent_role="action",
        intent_spine=IntentSpine(
            urgency=urgency_score,
            importance=importance_score,
            warmth=warmth_score,
            tension=tension_score,
            confidence=0.90,
        ),
        affect_lattice=AffectLattice(),
        semantic_motif=semantic_hash(f"action:{action_str}"),
        gloss=action_str,
        confidence=0.90,
    )
    
    return packets
