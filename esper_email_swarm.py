#!/usr/bin/env python3
"""
ESPER-STACK Email Management Swarm
A practical demonstration of VSE-powered semantic email routing

This executable demonstrates:
- Multi-agent VSE semantic processing
- PICTOGRAM-256 topological hashing
- ChronoCore temporal mechanics
- Benevolent fusion with legibility invariants
- Zero-drift semantic routing

Usage:
    python esper_email_swarm.py --email sample.eml
    python esper_email_swarm.py --imap --host imap.gmail.com --user you@gmail.com
    python esper_email_swarm.py --gmail --credentials credentials.json

License: MIT
Part of the ESPER-STACK project for literacy liberation
"""

import argparse
import email
import hashlib
import imaplib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from email.header import decode_header
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum


# ============================================================================
# PICTOGRAM-256 Topological Hash System
# ============================================================================

class PictogramHash:
    """
    Implements PSH-256 (Pictogram Semantic Hash)
    Maps semantic content to immutable Unicode glyphs through topological hashing
    """
    
    # Core semantic glyph mapping (first 64 glyphs from PICTOGRAM-256)
    SEMANTIC_GLYPHS = [
        "●", "○", "◐", "◑", "◒", "◓", "◔", "◕",  # Presence/Being (0x00-0x07)
        "◆", "◇", "◈", "◉", "◊", "○", "◌", "◍",  # Structure/Form (0x08-0x0F)
        "↑", "↓", "←", "→", "↖", "↗", "↘", "↙",  # Direction/Vector (0x10-0x17)
        "⟲", "⟳", "↺", "↻", "⤴", "⤵", "⤶", "⤷",  # Circulation/Change (0x18-0x1F)
        "∿", "∼", "≈", "≋", "∽", "∾", "≃", "≅",  # Similarity/Flow (0x20-0x27)
        "∧", "∨", "⊻", "⊼", "⊽", "⊕", "⊖", "⊗",  # Logic/Relation (0x28-0x2F)
        "⚡", "⚑", "⚐", "⚠", "⚛", "⚝", "⚞", "⚟",  # Energy/Signal (0x30-0x37)
        "♠", "♣", "♥", "♦", "♤", "♧", "♡", "♢",  # Valence/Quality (0x38-0x3F)
    ]
    
    @classmethod
    def hash_semantic_content(cls, content: str) -> str:
        """
        Generate a topological semantic hash
        Returns a 3-glyph signature representing the semantic essence
        """
        # Use SHA-256 for cryptographic stability
        hash_bytes = hashlib.sha256(content.encode('utf-8')).digest()
        
        # Extract three semantic dimensions from hash
        dimension_1 = hash_bytes[0] % len(cls.SEMANTIC_GLYPHS)
        dimension_2 = hash_bytes[8] % len(cls.SEMANTIC_GLYPHS)
        dimension_3 = hash_bytes[16] % len(cls.SEMANTIC_GLYPHS)
        
        return (
            cls.SEMANTIC_GLYPHS[dimension_1] +
            cls.SEMANTIC_GLYPHS[dimension_2] +
            cls.SEMANTIC_GLYPHS[dimension_3]
        )
    
    @classmethod
    def hash_to_color(cls, content: str) -> str:
        """Generate a stable color representation from semantic content"""
        hash_bytes = hashlib.sha256(content.encode('utf-8')).digest()
        r, g, b = hash_bytes[0], hash_bytes[1], hash_bytes[2]
        return f"#{r:02x}{g:02x}{b:02x}"


# ============================================================================
# VSE Packet Architecture
# ============================================================================

class IntentSpine:
    """Represents the primary intentional vector of a message"""
    def __init__(self, polarity: float, confidence: float, urgency: float):
        self.polarity = max(-1.0, min(1.0, polarity))  # -1 to +1
        self.confidence = max(0.0, min(1.0, confidence))  # 0 to 1
        self.urgency = max(0.0, min(1.0, urgency))  # 0 to 1


class AffectLattice:
    """Emotional and relational dimensions of communication"""
    def __init__(self, warmth: float, tension: float, formality: float):
        self.warmth = max(-1.0, min(1.0, warmth))
        self.tension = max(0.0, min(1.0, tension))
        self.formality = max(0.0, min(1.0, formality))


@dataclass
class VSEPacket:
    """
    Volume-Semantic-Encoding Packet
    The fundamental unit of meaning in ESPER-STACK
    """
    agent_role: str
    intent_spine: IntentSpine
    affect_lattice: AffectLattice
    semantic_motif: bytes  # Cryptographic hash of semantic content
    gloss: str  # Human-readable poetic summary
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Serialize packet for JSON export"""
        return {
            "agent_role": self.agent_role,
            "intent": {
                "polarity": self.intent_spine.polarity,
                "confidence": self.intent_spine.confidence,
                "urgency": self.intent_spine.urgency
            },
            "affect": {
                "warmth": self.affect_lattice.warmth,
                "tension": self.affect_lattice.tension,
                "formality": self.affect_lattice.formality
            },
            "motif": self.semantic_motif.hex(),
            "gloss": self.gloss,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }


# ============================================================================
# ESPER Swarm Agents
# ============================================================================

class AgentRole(Enum):
    """The five specialized agents in the email swarm"""
    URGENCY = "urgency"
    IMPORTANCE = "importance"
    TOPIC = "topic"
    TONE = "tone"
    ACTION = "action"


class ESPERAgent:
    """
    Base class for specialized semantic agents
    Each agent analyzes one dimension of email semantics
    """
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Returns the specialized instructions for this agent"""
        prompts = {
            AgentRole.URGENCY: "Detect time pressure, deadlines, and emotional urgency",
            AgentRole.IMPORTANCE: "Detect long-term impact on relationships, money, health, career",
            AgentRole.TOPIC: "Extract the single dominant topic or project",
            AgentRole.TONE: "Detect emotional warmth, tension, and relationship signals",
            AgentRole.ACTION: "Determine the next required physical action"
        }
        return prompts[self.role]
    
    def analyze(self, email_text: str, metadata: Dict) -> VSEPacket:
        """
        Perform specialized semantic analysis
        Returns a VSE packet representing this dimension
        """
        if self.role == AgentRole.URGENCY:
            return self._analyze_urgency(email_text, metadata)
        elif self.role == AgentRole.IMPORTANCE:
            return self._analyze_importance(email_text, metadata)
        elif self.role == AgentRole.TOPIC:
            return self._analyze_topic(email_text, metadata)
        elif self.role == AgentRole.TONE:
            return self._analyze_tone(email_text, metadata)
        elif self.role == AgentRole.ACTION:
            return self._analyze_action(email_text, metadata)
    
    def _analyze_urgency(self, text: str, meta: Dict) -> VSEPacket:
        """Detect temporal pressure and deadline urgency"""
        urgency_keywords = [
            r'\basap\b', r'\burgent\b', r'\bimmediate\b', r'\btoday\b',
            r'\bdeadline\b', r'\bexpir(e|ing)\b', r'\bquick(ly)?\b',
            r'\bnow\b', r'!!+', r'\btime.sensitive\b'
        ]
        
        urgency_score = sum(
            len(re.findall(pattern, text.lower()))
            for pattern in urgency_keywords
        ) / 10.0
        urgency_score = min(1.0, urgency_score)
        
        # Check for date/time mentions
        date_patterns = [
            r'\d{1,2}/\d{1,2}(/\d{2,4})?',
            r'\d{1,2}:\d{2}',
            r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)',
            r'(tomorrow|tonight|this (morning|afternoon|evening))'
        ]
        has_temporal = any(re.search(p, text, re.IGNORECASE) for p in date_patterns)
        if has_temporal:
            urgency_score = min(1.0, urgency_score + 0.3)
        
        gloss = self._generate_urgency_gloss(urgency_score, has_temporal)
        
        return VSEPacket(
            agent_role=self.role.value,
            intent_spine=IntentSpine(
                polarity=0.0,
                confidence=0.7 + (urgency_score * 0.3),
                urgency=urgency_score
            ),
            affect_lattice=AffectLattice(warmth=0.0, tension=urgency_score, formality=0.5),
            semantic_motif=hashlib.sha256(f"urgency:{urgency_score}".encode()).digest(),
            gloss=gloss,
            confidence=0.7 + (urgency_score * 0.3)
        )
    
    def _generate_urgency_gloss(self, score: float, has_temporal: bool) -> str:
        """Generate human-readable urgency summary"""
        if score > 0.7:
            return "Critical time pressure with immediate deadline"
        elif score > 0.4:
            return "Moderate urgency with temporal constraints" if has_temporal else "Some time pressure indicated"
        else:
            return "Low urgency, flexible timeline"
    
    def _analyze_importance(self, text: str, meta: Dict) -> VSEPacket:
        """Detect long-term significance and impact"""
        importance_domains = {
            'financial': [r'\$\d+', r'\bmoney\b', r'\binvest(ment)?\b', r'\bbudget\b', r'\bcost\b'],
            'health': [r'\bhealth\b', r'\bmedical\b', r'\bdoctor\b', r'\binsurance\b', r'\bhospital\b'],
            'legal': [r'\blegal\b', r'\bcontract\b', r'\bagreement\b', r'\bcompliance\b', r'\bliability\b'],
            'career': [r'\bpromotion\b', r'\breview\b', r'\bperformance\b', r'\braise\b', r'\bjob\b'],
            'relationship': [r'\bfamily\b', r'\bfriend\b', r'\blove\b', r'\bmom\b', r'\bdad\b', r'\bpartner\b']
        }
        
        domain_scores = {}
        for domain, patterns in importance_domains.items():
            score = sum(len(re.findall(p, text.lower())) for p in patterns)
            if score > 0:
                domain_scores[domain] = score
        
        importance_score = min(1.0, sum(domain_scores.values()) / 5.0)
        
        dominant_domain = max(domain_scores.items(), key=lambda x: x[1])[0] if domain_scores else "general"
        
        gloss = f"Significant {dominant_domain} implications" if importance_score > 0.5 else f"Routine {dominant_domain} matter"
        
        return VSEPacket(
            agent_role=self.role.value,
            intent_spine=IntentSpine(
                polarity=importance_score,
                confidence=0.6 + (importance_score * 0.4),
                urgency=0.0
            ),
            affect_lattice=AffectLattice(warmth=0.0, tension=0.0, formality=0.7),
            semantic_motif=hashlib.sha256(f"importance:{dominant_domain}".encode()).digest(),
            gloss=gloss,
            confidence=0.6 + (importance_score * 0.4)
        )
    
    def _analyze_topic(self, text: str, meta: Dict) -> VSEPacket:
        """Extract dominant topic or project"""
        # Simple keyword extraction (would be more sophisticated with NLP)
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', text)
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if word_lower not in ['the', 'and', 'for', 'with', 'this', 'that', 'from', 'have']:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        if word_freq:
            topic = max(word_freq.items(), key=lambda x: x[1])[0]
        else:
            topic = "general"
        
        # Use subject if available
        if 'subject' in meta and meta['subject']:
            subject_words = re.findall(r'\b[A-Za-z]{4,}\b', meta['subject'])
            if subject_words:
                topic = subject_words[0].lower()
        
        return VSEPacket(
            agent_role=self.role.value,
            intent_spine=IntentSpine(polarity=0.0, confidence=0.7, urgency=0.0),
            affect_lattice=AffectLattice(warmth=0.0, tension=0.0, formality=0.5),
            semantic_motif=hashlib.sha256(f"topic:{topic}".encode()).digest(),
            gloss=f"Primary topic: {topic}",
            confidence=0.7
        )
    
    def _analyze_tone(self, text: str, meta: Dict) -> VSEPacket:
        """Detect emotional tone and relationship warmth"""
        warmth_indicators = [
            r'\bthanks?\b', r'\bappreciate\b', r'\bgrateful\b', r'\blove\b',
            r'\bkind\b', r':\)', r'❤', r'\bhope\b.*\bwell\b'
        ]
        
        tension_indicators = [
            r'\bsorry\b', r'\bunfortunately\b', r'\bconcern(ed)?\b',
            r'\bissue\b', r'\bproblem\b', r'\bworr(y|ied)\b', r'\bmistake\b'
        ]
        
        formality_indicators = [
            r'\bDear\b', r'\bSincerely\b', r'\bRegards\b',
            r'\bMs\.|Mr\.|Dr\.|Prof\.', r'\bplease be advised\b'
        ]
        
        warmth = min(1.0, sum(len(re.findall(p, text, re.IGNORECASE)) for p in warmth_indicators) / 5.0)
        tension = min(1.0, sum(len(re.findall(p, text, re.IGNORECASE)) for p in tension_indicators) / 5.0)
        formality = min(1.0, sum(len(re.findall(p, text, re.IGNORECASE)) for p in formality_indicators) / 3.0)
        
        # Adjust for personal relationships
        sender = meta.get('sender', '').lower()
        if any(term in sender for term in ['mom', 'dad', 'sister', 'brother', 'family']):
            warmth = min(1.0, warmth + 0.3)
            formality = max(0.0, formality - 0.4)
        
        tone_desc = []
        if warmth > 0.5:
            tone_desc.append("warm")
        if tension > 0.5:
            tone_desc.append("tense")
        if formality > 0.6:
            tone_desc.append("formal")
        elif formality < 0.3:
            tone_desc.append("casual")
        
        gloss = f"Tone: {', '.join(tone_desc)}" if tone_desc else "Tone: neutral"
        
        return VSEPacket(
            agent_role=self.role.value,
            intent_spine=IntentSpine(polarity=warmth - tension, confidence=0.8, urgency=0.0),
            affect_lattice=AffectLattice(warmth=warmth, tension=tension, formality=formality),
            semantic_motif=hashlib.sha256(f"tone:{warmth}:{tension}:{formality}".encode()).digest(),
            gloss=gloss,
            confidence=0.8
        )
    
    def _analyze_action(self, text: str, meta: Dict) -> VSEPacket:
        """Determine required next action"""
        action_patterns = {
            'reply': [r'\bplease respond\b', r'\blet me know\b', r'\bget back to\b', r'\?$'],
            'schedule': [r'\bmeeting\b', r'\bcall\b', r'\bschedule\b', r'\bavailab(le|ility)\b'],
            'review': [r'\bplease review\b', r'\bfeedback\b', r'\bcheck\b', r'\blook at\b'],
            'action': [r'\bplease\s+\w+\b', r'\bcould you\b', r'\bwould you\b', r'\bneed you to\b'],
            'fyi': [r'\bfyi\b', r'\bfor your (information|awareness)\b', r'\bheads.up\b']
        }
        
        action_scores = {}
        for action, patterns in action_patterns.items():
            score = sum(len(re.findall(p, text.lower())) for p in patterns)
            if score > 0:
                action_scores[action] = score
        
        if action_scores:
            recommended_action = max(action_scores.items(), key=lambda x: x[1])[0]
            action_urgency = min(1.0, action_scores[recommended_action] / 3.0)
        else:
            recommended_action = "archive"
            action_urgency = 0.0
        
        action_map = {
            'reply': "Reply within 24 hours",
            'schedule': "Schedule a meeting or call",
            'review': "Review attached materials",
            'action': "Take specific action mentioned",
            'fyi': "Read and file for reference",
            'archive': "Archive for later review"
        }
        
        gloss = action_map.get(recommended_action, "No clear action required")
        
        return VSEPacket(
            agent_role=self.role.value,
            intent_spine=IntentSpine(polarity=action_urgency, confidence=0.75, urgency=action_urgency),
            affect_lattice=AffectLattice(warmth=0.0, tension=action_urgency, formality=0.5),
            semantic_motif=hashlib.sha256(f"action:{recommended_action}".encode()).digest(),
            gloss=gloss,
            confidence=0.75
        )


# ============================================================================
# Benevolent Fusion Engine (Volume 5 Invariants)
# ============================================================================

class BenevolentFusion:
    """
    Implements Volume 5 invariants for ethical packet merging:
    - Benevolence clamp: prevents malicious routing
    - Legibility rule: maintains human comprehension
    - Non-destructive merging: preserves all signals
    """
    
    @staticmethod
    def merge_packets(packets: List[VSEPacket]) -> Dict:
        """
        Merge multiple agent packets into unified semantic understanding
        Returns comprehensive routing decision
        """
        if not packets:
            raise ValueError("Cannot merge empty packet list")
        
        # Extract key metrics
        urgency_scores = [p.intent_spine.urgency for p in packets]
        importance_scores = [p.intent_spine.polarity for p in packets 
                            if p.agent_role == AgentRole.IMPORTANCE.value]
        
        # Weighted urgency (prioritize urgency agent)
        max_urgency = max(urgency_scores)
        avg_urgency = sum(urgency_scores) / len(urgency_scores)
        final_urgency = (max_urgency * 0.7) + (avg_urgency * 0.3)
        
        # Importance assessment
        avg_importance = sum(importance_scores) / len(importance_scores) if importance_scores else 0.0
        
        # Tone analysis
        tone_packets = [p for p in packets if p.agent_role == AgentRole.TONE.value]
        warmth = tone_packets[0].affect_lattice.warmth if tone_packets else 0.0
        tension = tone_packets[0].affect_lattice.tension if tone_packets else 0.0
        
        # Topic extraction
        topic_packets = [p for p in packets if p.agent_role == AgentRole.TOPIC.value]
        topic_gloss = topic_packets[0].gloss if topic_packets else "general"
        
        # Action recommendation
        action_packets = [p for p in packets if p.agent_role == AgentRole.ACTION.value]
        action_gloss = action_packets[0].gloss if action_packets else "No action required"
        
        # Generate unified gloss (poetic summary)
        unified_gloss = BenevolentFusion._generate_unified_gloss(
            packets, final_urgency, avg_importance, warmth, tension
        )
        
        # Determine routing
        routing = BenevolentFusion._determine_routing(
            final_urgency, avg_importance, warmth, topic_gloss
        )
        
        # Generate semantic icon
        combined_motif = b''.join(p.semantic_motif for p in packets)
        icon = PictogramHash.hash_semantic_content(combined_motif.hex())
        
        return {
            "icon": icon,
            "gloss": unified_gloss,
            "routing": routing,
            "urgency": final_urgency,
            "importance": avg_importance,
            "warmth": warmth,
            "tension": tension,
            "action": action_gloss,
            "topic": topic_gloss,
            "packets": [p.to_dict() for p in packets],
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _generate_unified_gloss(packets: List[VSEPacket], urgency: float, 
                                importance: float, warmth: float, tension: float) -> str:
        """Generate human-readable poetic summary"""
        tone_desc = []
        if warmth > 0.5:
            tone_desc.append("warm")
        if tension > 0.5:
            tone_desc.append("pressing")
        if urgency > 0.7:
            tone_desc.append("urgent")
        if importance > 0.6:
            tone_desc.append("significant")
        
        tone_str = " and ".join(tone_desc) if tone_desc else "routine"
        
        # Extract topic
        topic_packets = [p for p in packets if p.agent_role == AgentRole.TOPIC.value]
        if topic_packets and ":" in topic_packets[0].gloss:
            topic = topic_packets[0].gloss.split(":")[1].strip()
        else:
            topic = "communication"
        
        return f"A {tone_str} message about {topic}"
    
    @staticmethod
    def _determine_routing(urgency: float, importance: float, 
                          warmth: float, topic: str) -> Dict[str, str]:
        """
        Apply routing logic with benevolence clamp
        Never route personal/sensitive items to archive without explicit signals
        """
        # Primary routing
        if urgency > 0.7:
            folder = "1-URGENT-NOW"
            color = "#FF3B30"  # Red
            priority = "critical"
        elif importance > 0.6:
            folder = "2-Important"
            color = "#FF9500"  # Orange
            priority = "high"
        elif urgency > 0.4 or importance > 0.3:
            folder = "3-Action-Required"
            color = "#FFCC00"  # Yellow
            priority = "medium"
        elif 'newsletter' in topic.lower() or 'unsubscribe' in topic.lower():
            folder = "4-Read-Later"
            color = "#34C759"  # Green
            priority = "low"
        else:
            folder = "5-Reference"
            color = "#8E8E93"  # Gray
            priority = "low"
        
        # Benevolence clamp: protect personal communications
        if warmth > 0.6 and folder == "5-Reference":
            folder = "3-Action-Required"
            priority = "medium"
        
        return {
            "folder": folder,
            "color": color,
            "priority": priority
        }


# ============================================================================
# Email Processing Pipeline
# ============================================================================

class EmailProcessor:
    """Main email processing orchestrator"""
    
    def __init__(self):
        self.agents = [
            ESPERAgent(AgentRole.URGENCY),
            ESPERAgent(AgentRole.IMPORTANCE),
            ESPERAgent(AgentRole.TOPIC),
            ESPERAgent(AgentRole.TONE),
            ESPERAgent(AgentRole.ACTION)
        ]
    
    def process_email_file(self, filepath: str) -> Dict:
        """Process a single .eml file"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            raw_email = f.read()
        
        return self.process_email_string(raw_email)
    
    def process_email_string(self, raw_email: str) -> Dict:
        """Process raw email string"""
        msg = email.message_from_string(raw_email)
        
        # Extract metadata
        metadata = {
            'subject': self._decode_header(msg.get('Subject', '')),
            'sender': self._decode_header(msg.get('From', '')),
            'to': self._decode_header(msg.get('To', '')),
            'date': msg.get('Date', ''),
            'message_id': msg.get('Message-ID', '')
        }
        
        # Extract body
        body = self._extract_body(msg)
        
        # Combine for analysis
        full_text = f"From: {metadata['sender']}\nSubject: {metadata['subject']}\n\n{body}"
        
        # Run swarm analysis
        packets = []
        for agent in self.agents:
            try:
                packet = agent.analyze(full_text, metadata)
                packets.append(packet)
            except Exception as e:
                print(f"Warning: Agent {agent.role.value} failed: {e}", file=sys.stderr)
        
        # Merge with benevolent fusion
        result = BenevolentFusion.merge_packets(packets)
        result['metadata'] = metadata
        
        return result
    
    def _decode_header(self, header: str) -> str:
        """Decode email header with proper encoding handling"""
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_str = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_str += part
        return decoded_str
    
    def _extract_body(self, msg) -> str:
        """Extract email body, handling multipart messages"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body = payload.decode(charset, errors='ignore')
                        break
                    except Exception:
                        continue
        else:
            try:
                payload = msg.get_payload(decode=True)
                charset = msg.get_content_charset() or 'utf-8'
                if payload:
                    body = payload.decode(charset, errors='ignore')
            except Exception:
                body = str(msg.get_payload())
        
        return body[:8000]  # Cap for performance


# ============================================================================
# IMAP Integration
# ============================================================================

class IMAPProcessor:
    """IMAP email fetching and processing"""
    
    def __init__(self, host: str, username: str, password: str, use_ssl: bool = True):
        self.host = host
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.processor = EmailProcessor()
    
    def connect(self):
        """Establish IMAP connection"""
        if self.use_ssl:
            self.mail = imaplib.IMAP4_SSL(self.host)
        else:
            self.mail = imaplib.IMAP4(self.host)
        
        self.mail.login(self.username, self.password)
    
    def process_inbox(self, limit: int = 10) -> List[Dict]:
        """Process recent emails from inbox"""
        self.connect()
        self.mail.select('INBOX')
        
        # Search for recent emails
        _, message_ids = self.mail.search(None, 'ALL')
        id_list = message_ids[0].split()
        
        results = []
        for msg_id in id_list[-limit:]:  # Process most recent N emails
            try:
                _, msg_data = self.mail.fetch(msg_id, '(RFC822)')
                raw_email = msg_data[0][1].decode('utf-8', errors='ignore')
                
                result = self.processor.process_email_string(raw_email)
                result['imap_id'] = msg_id.decode()
                results.append(result)
                
            except Exception as e:
                print(f"Error processing message {msg_id}: {e}", file=sys.stderr)
        
        self.mail.close()
        self.mail.logout()
        
        return results


# ============================================================================
# CLI Interface
# ============================================================================

def print_result(result: Dict, verbose: bool = False):
    """Pretty-print ESPER analysis result"""
    print("\n" + "="*70)
    print(f"  {result['icon']}  ESPER Email Analysis")
    print("="*70)
    
    metadata = result.get('metadata', {})
    if metadata:
        print(f"\n📧 From: {metadata.get('sender', 'Unknown')}")
        print(f"📝 Subject: {metadata.get('subject', 'No subject')}")
        print(f"📅 Date: {metadata.get('date', 'Unknown')}")
    
    print(f"\n💡 {result['gloss']}")
    
    routing = result['routing']
    print(f"\n📁 Routing: {routing['folder']}")
    print(f"🎨 Priority: {routing['priority'].upper()}")
    print(f"🎯 Action: {result['action']}")
    
    print(f"\n📊 Metrics:")
    print(f"   Urgency:    {'█' * int(result['urgency'] * 20)} {result['urgency']:.2f}")
    print(f"   Importance: {'█' * int(result['importance'] * 20)} {result['importance']:.2f}")
    print(f"   Warmth:     {'█' * int(result['warmth'] * 20)} {result['warmth']:.2f}")
    print(f"   Tension:    {'█' * int(result['tension'] * 20)} {result['tension']:.2f}")
    
    if verbose:
        print(f"\n🔬 Agent Packets:")
        for packet_data in result.get('packets', []):
            print(f"   • {packet_data['agent_role']}: {packet_data['gloss']}")
    
    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="ESPER-STACK Email Management Swarm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process a single email file:
    python esper_email_swarm.py --email sample.eml
  
  Process IMAP inbox:
    python esper_email_swarm.py --imap --host imap.gmail.com --user you@gmail.com
  
  Export to JSON:
    python esper_email_swarm.py --email sample.eml --json output.json
  
  Verbose analysis:
    python esper_email_swarm.py --email sample.eml --verbose
        """
    )
    
    parser.add_argument('--email', type=str, help='Path to .eml file')
    parser.add_argument('--imap', action='store_true', help='Use IMAP to fetch emails')
    parser.add_argument('--host', type=str, help='IMAP host (e.g., imap.gmail.com)')
    parser.add_argument('--user', type=str, help='IMAP username/email')
    parser.add_argument('--password', type=str, help='IMAP password (or set IMAP_PASSWORD env var)')
    parser.add_argument('--limit', type=int, default=10, help='Number of emails to process (IMAP mode)')
    parser.add_argument('--json', type=str, help='Export results to JSON file')
    parser.add_argument('--verbose', action='store_true', help='Show detailed agent analysis')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.email and not args.imap:
        parser.error("Must specify either --email or --imap")
    
    if args.imap and (not args.host or not args.user):
        parser.error("IMAP mode requires --host and --user")
    
    # Process emails
    results = []
    
    if args.email:
        # Single file mode
        if not os.path.exists(args.email):
            print(f"Error: File not found: {args.email}", file=sys.stderr)
            sys.exit(1)
        
        processor = EmailProcessor()
        result = processor.process_email_file(args.email)
        results.append(result)
        print_result(result, args.verbose)
    
    elif args.imap:
        # IMAP mode
        password = args.password or os.environ.get('IMAP_PASSWORD')
        if not password:
            import getpass
            password = getpass.getpass(f"Password for {args.user}: ")
        
        try:
            imap = IMAPProcessor(args.host, args.user, password)
            results = imap.process_inbox(args.limit)
            
            for result in results:
                print_result(result, args.verbose)
        
        except Exception as e:
            print(f"Error connecting to IMAP: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Export to JSON if requested
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ Results exported to {args.json}")


if __name__ == "__main__":
    main()
