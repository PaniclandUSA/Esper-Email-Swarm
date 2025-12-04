"""
ESPER Email Swarm - Core Data Models

This module defines the fundamental data structures for VSE-style
semantic email analysis:
- IntentSpine: Primary intentional vectors
- AffectLattice: Emotional dimensions
- VSEPacket: Semantic analysis unit
- EmailAnalysis: Final routing decision
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib


# =============================================================================
# PICTOGRAM-256 Semantic Hashing
# =============================================================================

def semantic_hash(text: str) -> bytes:
    """
    Generate stable cryptographic hash of semantic content.
    
    This is a placeholder for full PICTOGRAM-256 topological hashing.
    Uses SHA-256 for cryptographic stability and collision resistance.
    
    Args:
        text: Content to hash
        
    Returns:
        32-byte hash digest
    """
    return hashlib.sha256(text.encode("utf-8")).digest()


def glyph_from_hash(motif: bytes) -> str:
    """
    Generate 3-glyph semantic signature from hash.
    
    Maps hash bytes to PICTOGRAM-256 glyphs representing:
    - Dimension 1: Presence/Being (bytes[0])
    - Dimension 2: Direction/Vector (bytes[8])
    - Dimension 3: Flow/Relation (bytes[16])
    
    This is simplified for demonstration. Full PICTOGRAM-256 uses
    topological mapping across 256 semantic primitives.
    
    Args:
        motif: SHA-256 hash digest
        
    Returns:
        3-character Unicode glyph sequence
    """
    # PICTOGRAM-256 core semantic glyphs (first 64 primitives)
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
    
    # Extract three semantic dimensions from different regions of hash
    # This ensures independence between dimensions
    dimension_1 = motif[0] % len(SEMANTIC_GLYPHS)
    dimension_2 = motif[8] % len(SEMANTIC_GLYPHS)
    dimension_3 = motif[16] % len(SEMANTIC_GLYPHS)
    
    return (
        SEMANTIC_GLYPHS[dimension_1] +
        SEMANTIC_GLYPHS[dimension_2] +
        SEMANTIC_GLYPHS[dimension_3]
    )


# =============================================================================
# VSE Data Structures
# =============================================================================

@dataclass
class IntentSpine:
    """
    Primary intentional vector of communication.
    
    Represents the sender's core intent along multiple dimensions.
    All values normalized to [0, 1] range for consistency.
    
    Attributes:
        urgency: Time pressure, deadline proximity (0=none, 1=critical)
        importance: Long-term impact significance (0=trivial, 1=crucial)
        warmth: Relationship warmth, emotional connection (0=cold, 1=warm)
        tension: Conflict, stress, negative pressure (0=calm, 1=tense)
        confidence: Agent's certainty in assessment (0=uncertain, 1=certain)
    """
    urgency: float = 0.0
    importance: float = 0.0
    warmth: float = 0.0
    tension: float = 0.0
    confidence: float = 0.0
    
    def __post_init__(self):
        """Validate all values are in [0, 1] range."""
        for field_name in ['urgency', 'importance', 'warmth', 'tension', 'confidence']:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be in [0, 1], got {value}")


@dataclass
class AffectLattice:
    """
    Emotional and relational dimensions of communication.
    
    Represents the affective quality of the message across
    six primary emotional axes. Values normalized to [0, 1].
    
    Attributes:
        joy: Happiness, delight, positive emotion
        sorrow: Sadness, grief, loss
        anger: Frustration, irritation, rage
        fear: Anxiety, worry, apprehension
        trust: Confidence, reliability, faith
        surprise: Unexpectedness, novelty, shock
    """
    joy: float = 0.0
    sorrow: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    trust: float = 0.0
    surprise: float = 0.0
    
    def __post_init__(self):
        """Validate all values are in [0, 1] range."""
        for field_name in ['joy', 'sorrow', 'anger', 'fear', 'trust', 'surprise']:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be in [0, 1], got {value}")


@dataclass
class VSEPacket:
    """
    Volume-Semantic-Encoding packet: fundamental unit of meaning.
    
    Each agent produces one VSEPacket representing its specialized
    semantic analysis. Packets are cryptographically stable and
    fully auditable.
    
    Attributes:
        agent_role: Which agent created this packet
        intent_spine: Primary intentional vector
        affect_lattice: Emotional dimensions
        semantic_motif: Cryptographic hash of semantic content (immutable)
        gloss: Human-readable poetic summary (legibility rule)
        confidence: Agent's certainty in analysis
        timestamp: When packet was created
    """
    agent_role: str
    intent_spine: IntentSpine
    affect_lattice: AffectLattice
    semantic_motif: bytes
    gloss: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate confidence is in [0, 1] range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")
    
    def to_json_dict(self) -> Dict[str, Any]:
        """
        Serialize packet to JSON-compatible dictionary.
        
        Returns:
            Dictionary with all packet data, ready for JSON export
        """
        return {
            "agent_role": self.agent_role,
            "intent": {
                "urgency": self.intent_spine.urgency,
                "importance": self.intent_spine.importance,
                "warmth": self.intent_spine.warmth,
                "tension": self.intent_spine.tension,
                "confidence": self.intent_spine.confidence,
            },
            "affect": {
                "joy": self.affect_lattice.joy,
                "sorrow": self.affect_lattice.sorrow,
                "anger": self.affect_lattice.anger,
                "fear": self.affect_lattice.fear,
                "trust": self.affect_lattice.trust,
                "surprise": self.affect_lattice.surprise,
            },
            "semantic_motif": self.semantic_motif.hex(),
            "gloss": self.gloss,
            "packet_confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Email Data Structures
# =============================================================================

@dataclass
class EmailMetadata:
    """
    Essential email metadata extracted from headers.
    
    Attributes:
        sender: From header (email address)
        subject: Subject line
        date: Date header (ISO format string)
        message_id: Unique message identifier
    """
    sender: str
    subject: str
    date: Optional[str] = None
    message_id: Optional[str] = None


@dataclass
class EmailAnalysis:
    """
    Final semantic analysis and routing decision.
    
    This is the merged output from all agent packets, representing
    the complete understanding of the email's meaning and appropriate
    handling.
    
    Attributes:
        icon: 3-glyph PICTOGRAM-256 semantic signature
        gloss: Human-readable summary (legibility rule)
        routing_folder: Semantic category folder
        routing_color: Visual priority color (hex)
        routing_priority: Priority level (critical/high/medium/low)
        action: Recommended next action
        topic: Primary topic/project
        urgency: Overall urgency score [0, 1]
        importance: Overall importance score [0, 1]
        warmth: Overall warmth score [0, 1]
        tension: Overall tension score [0, 1]
        metadata: Email headers
        packets: All agent packets (non-destructive merging)
    """
    icon: str
    gloss: str
    routing_folder: str
    routing_color: str
    routing_priority: str
    action: str
    topic: str
    urgency: float
    importance: float
    warmth: float
    tension: float
    metadata: EmailMetadata
    packets: Dict[str, VSEPacket]
    
    def to_json_dict(self) -> Dict[str, Any]:
        """
        Serialize analysis to JSON-compatible dictionary.
        
        Returns:
            Complete analysis in JSON format
        """
        return {
            "icon": self.icon,
            "gloss": self.gloss,
            "routing": {
                "folder": self.routing_folder,
                "color": self.routing_color,
                "priority": self.routing_priority,
            },
            "urgency": self.urgency,
            "importance": self.importance,
            "warmth": self.warmth,
            "tension": self.tension,
            "action": self.action,
            "topic": self.topic,
            "metadata": {
                "subject": self.metadata.subject,
                "sender": self.metadata.sender,
                "date": self.metadata.date,
                "message_id": self.metadata.message_id,
            },
            "packets": {
                role: packet.to_json_dict() 
                for role, packet in self.packets.items()
            },
        }
    
    def pretty_print(self) -> str:
        """
        Generate human-readable formatted output.
        
        Returns:
            Multi-line formatted string for terminal display
        """
        bar = "=" * 70
        
        # Format metric bars
        urgency_bar = "█" * int(self.urgency * 20)
        importance_bar = "█" * int(self.importance * 20)
        warmth_bar = "█" * int(self.warmth * 20)
        tension_bar = "█" * int(self.tension * 20)
        
        output = f"""
{bar}
  {self.icon}  ESPER Email Analysis
{bar}

📧 From: {self.metadata.sender}
📝 Subject: {self.metadata.subject}
📅 Date: {self.metadata.date or 'Unknown'}

💡 {self.gloss}

📁 Routing: {self.routing_folder}
🎨 Priority: {self.routing_priority.upper()}
🎯 Action: {self.action}

📊 Metrics:
   Urgency:    {urgency_bar} {self.urgency:.2f}
   Importance: {importance_bar} {self.importance:.2f}
   Warmth:     {warmth_bar} {self.warmth:.2f}
   Tension:    {tension_bar} {self.tension:.2f}

{bar}
"""
        return output.strip()
