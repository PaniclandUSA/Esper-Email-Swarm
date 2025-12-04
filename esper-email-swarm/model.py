"""
ESPER Email Swarm - Data Models

Defines the core VSE packet structures and email analysis models.
Implements PICTOGRAM-256 semantic hashing and glyph generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import textwrap


@dataclass
class IntentSpine:
    """
    Primary intentional vector of communication.
    
    This is a simplified VSE intent representation focused on email semantics.
    In full ESPER-STACK, this would connect to deeper intentional hierarchies.
    """
    urgency: float = 0.0        # 0–1: time pressure, deadlines
    importance: float = 0.0     # 0–1: long-term impact (career, health, money)
    warmth: float = 0.0         # -1 to 1: relationship warmth/coldness
    tension: float = 0.0        # 0–1: conflict, stress, pressure
    confidence: float = 0.0     # 0–1: agent's certainty in this assessment
    
    def __post_init__(self):
        """Clamp values to valid ranges"""
        self.urgency = max(0.0, min(1.0, self.urgency))
        self.importance = max(0.0, min(1.0, self.importance))
        self.warmth = max(-1.0, min(1.0, self.warmth))
        self.tension = max(0.0, min(1.0, self.tension))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class AffectLattice:
    """
    Emotional dimensions of communication.
    
    This is a simplified affect model. Full ESPER-STACK would include
    more nuanced emotional topology.
    """
    joy: float = 0.0
    sorrow: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    trust: float = 0.0
    surprise: float = 0.0
    
    def __post_init__(self):
        """Clamp all values to [0, 1]"""
        for attr in ['joy', 'sorrow', 'anger', 'fear', 'trust', 'surprise']:
            value = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, value)))


@dataclass
class VSEPacket:
    """
    Volume-Semantic-Encoding Packet
    
    The fundamental unit of meaning in ESPER-STACK. Each agent produces
    one packet representing its analysis of a specific semantic dimension.
    
    Attributes:
        agent_role: Which agent created this packet (urgency, importance, etc.)
        intent_spine: Primary intentional vector
        affect_lattice: Emotional dimensions
        semantic_motif: Cryptographic hash (SHA-256) of semantic content
        gloss: Human-readable poetic summary (legibility rule)
        confidence: Agent's confidence in this analysis
        timestamp: When this packet was created
    """
    agent_role: str
    intent_spine: IntentSpine
    affect_lattice: AffectLattice
    semantic_motif: bytes
    gloss: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_json_dict(self) -> Dict[str, Any]:
        """Serialize packet to JSON-compatible dictionary"""
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


@dataclass
class EmailMetadata:
    """Basic email metadata extracted from headers"""
    sender: str
    subject: str
    date: Optional[str] = None
    message_id: Optional[str] = None
    to: Optional[str] = None


@dataclass
class EmailAnalysis:
    """
    Final merged analysis used in CLI/JSON output.
    
    This is the result of benevolent fusion across all agent packets,
    representing the semantic understanding of the email.
    """
    icon: str                    # PICTOGRAM-256 3-glyph semantic signature
    gloss: str                   # Human-readable summary
    routing_folder: str          # Semantic folder (1-URGENT-NOW, etc.)
    routing_color: str           # Hex color for visual routing
    routing_priority: str        # critical, high, medium, low
    action: str                  # Recommended next action
    topic: str                   # Primary topic/project
    urgency: float               # Merged urgency score
    importance: float            # Merged importance score
    warmth: float                # Merged warmth score
    tension: float               # Merged tension score
    metadata: EmailMetadata      # Original email metadata
    packets: Dict[str, VSEPacket]  # Individual agent packets (auditability)

    def pretty(self) -> str:
        """
        Generate human-readable terminal output.
        
        This implements the legibility rule from Volume 5:
        Every decision must be comprehensible to humans.
        """
        bar = "=" * 70
        
        # Create visual metric bars
        def metric_bar(value: float, width: int = 20) -> str:
            filled = int(value * width)
            return "█" * filled + " " * (width - filled)
        
        metrics = (
            f"   Urgency:    {metric_bar(self.urgency)} {self.urgency:0.2f}\n"
            f"   Importance: {metric_bar(self.importance)} {self.importance:0.2f}\n"
            f"   Warmth:     {metric_bar(self.warmth)} {self.warmth:0.2f}\n"
            f"   Tension:    {metric_bar(self.tension)} {self.tension:0.2f}"
        )
        
        output = f"""
{bar}
  {self.icon}  ESPER Email Analysis
{bar}

📧 From: {self.metadata.sender}
📝 Subject: {self.metadata.subject}
📅 Date: {self.metadata.date or "Unknown"}

💡 {self.gloss}

📁 Routing: {self.routing_folder}
🎨 Priority: {self.routing_priority.upper()}
🎯 Action: {self.action}

📊 Metrics:
{metrics}

{bar}
"""
        return output.strip()
    
    def to_json_dict(self) -> Dict[str, Any]:
        """Serialize complete analysis to JSON"""
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
                "to": self.metadata.to,
            },
            "packets": [p.to_json_dict() for p in self.packets.values()],
        }


# ============================================================================
# PICTOGRAM-256 Semantic Hashing
# ============================================================================

def semantic_hash(text: str) -> bytes:
    """
    Generate cryptographically stable semantic hash.
    
    Uses SHA-256 to ensure:
    - Same content always produces same hash
    - Collision resistance
    - Irreversibility (semantic privacy)
    
    This is the foundation for PICTOGRAM-256 binding.
    """
    return hashlib.sha256(text.encode("utf-8")).digest()


# PICTOGRAM-256 Core Semantic Glyphs (64 primitives)
PICTOGRAM_GLYPHS = [
    # 0x00-0x07: Presence/Being
    "●", "○", "◐", "◑", "◒", "◓", "◔", "◕",
    # 0x08-0x0F: Structure/Form
    "◆", "◇", "◈", "◉", "◊", "⬙", "◌", "◍",
    # 0x10-0x17: Direction/Vector
    "↑", "↓", "←", "→", "↖", "↗", "↘", "↙",
    # 0x18-0x1F: Circulation/Change
    "⟲", "⟳", "↺", "↻", "⤴", "⤵", "⤶", "⤷",
    # 0x20-0x27: Similarity/Flow
    "∿", "∼", "≈", "≋", "∽", "∾", "≃", "≅",
    # 0x28-0x2F: Logic/Relation
    "∧", "∨", "⊻", "⊼", "⊽", "⊕", "⊖", "⊗",
    # 0x30-0x37: Energy/Signal
    "⚡", "⚑", "⚐", "⚠", "⚛", "⚝", "⚞", "⚟",
    # 0x38-0x3F: Valence/Quality
    "♠", "♣", "♥", "♦", "♤", "♧", "♡", "♢",
]


def glyph_from_hash(motif: bytes) -> str:
    """
    Generate 3-glyph PICTOGRAM-256 signature from semantic hash.
    
    This creates a visual semantic fingerprint that is:
    - Topologically stable (same meaning → same glyph)
    - Cryptographically bound (SHA-256 based)
    - Human readable (visual distinction)
    - Collision resistant (64³ = 262,144 combinations)
    
    The three glyphs represent three semantic dimensions extracted
    from different parts of the hash, providing a topological
    representation of meaning.
    
    Args:
        motif: 32-byte SHA-256 hash of semantic content
        
    Returns:
        3-character glyph sequence (e.g., "⚡⊻≃")
    """
    if len(motif) < 3:
        # Fallback for short hashes
        motif = motif + b'\x00' * (3 - len(motif))
    
    # Extract three semantic dimensions from different hash regions
    # This provides topological separation
    dimension_1 = motif[0] % len(PICTOGRAM_GLYPHS)
    dimension_2 = motif[8] % len(PICTOGRAM_GLYPHS)
    dimension_3 = motif[16] % len(PICTOGRAM_GLYPHS)
    
    return (
        PICTOGRAM_GLYPHS[dimension_1] +
        PICTOGRAM_GLYPHS[dimension_2] +
        PICTOGRAM_GLYPHS[dimension_3]
    )


def glyph_to_color(glyph: str) -> str:
    """
    Generate stable color from glyph for visual routing.
    
    This provides consistent color mapping for the same semantic signature,
    enabling visual pattern recognition in email interfaces.
    """
    # Hash the glyph to get stable color
    hash_bytes = hashlib.sha256(glyph.encode('utf-8')).digest()
    r, g, b = hash_bytes[0], hash_bytes[1], hash_bytes[2]
    return f"#{r:02x}{g:02x}{b:02x}"
