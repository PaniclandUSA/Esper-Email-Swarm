"""
ESPER Email Swarm - Routing Engine

Implements benevolent fusion (Volume 5 invariants) and semantic routing.

Volume 5 Invariants:
1. Benevolence Clamp - Prevents malicious or harmful routing
2. Legibility Rule - Every decision has human-readable explanation
3. Non-Destructive Merging - All agent signals preserved
"""

from __future__ import annotations

from typing import Dict, Tuple
from .model import (
    VSEPacket,
    EmailAnalysis,
    EmailMetadata,
    glyph_from_hash,
)


# ============================================================================
# Benevolent Fusion (Volume 5)
# ============================================================================

def benevolence_clamp(packets: Dict[str, VSEPacket]) -> Tuple[float, float, float, float]:
    """
    Merge agent packets using Volume 5 invariants.
    
    This implements ethical packet fusion that:
    1. Averages signals across agents (democratic fusion)
    2. Protects warmth: high relationship warmth prevents harmful routing
    3. Balances tension: prevents tension from dominating warm communication
    4. Preserves all original signals (non-destructive)
    
    Args:
        packets: Dictionary of agent role → VSE packet
        
    Returns:
        Tuple of (urgency, importance, warmth, tension) merged scores
        
    Raises:
        ValueError: If no packets provided
    """
    if not packets:
        raise ValueError("Cannot perform benevolent fusion on empty packet set")
    
    n = float(len(packets))
    
    # Democratic averaging across all agents
    urgency = sum(p.intent_spine.urgency for p in packets.values()) / n
    importance = sum(p.intent_spine.importance for p in packets.values()) / n
    warmth = sum(p.intent_spine.warmth for p in packets.values()) / n
    tension = sum(p.intent_spine.tension for p in packets.values()) / n
    
    # Benevolence clamp: protect high-warmth communication
    # If warmth is very high, prevent tension from dominating
    if warmth > 0.6 and tension > 0.7:
        # Blend tension with warmth to soften harsh routing
        tension = (tension + warmth) / 2.0
    
    # Ensure values stay in valid ranges
    urgency = max(0.0, min(1.0, urgency))
    importance = max(0.0, min(1.0, importance))
    warmth = max(-1.0, min(1.0, warmth))
    tension = max(0.0, min(1.0, tension))
    
    return urgency, importance, warmth, tension


# ============================================================================
# Semantic Routing
# ============================================================================

# Routing categories with their semantic thresholds
ROUTING_CATEGORIES = {
    '1-URGENT-NOW': {
        'color': '#FF3B30',      # Red
        'priority': 'critical',
        'threshold_urgency': 0.7,
        'description': 'Critical time pressure requiring immediate action',
    },
    '2-Important': {
        'color': '#FF9500',      # Orange
        'priority': 'high',
        'threshold_importance': 0.6,
        'description': 'Significant long-term impact requiring attention',
    },
    '3-Action-Required': {
        'color': '#FFCC00',      # Yellow
        'priority': 'medium',
        'threshold_urgency': 0.4,
        'threshold_importance': 0.3,
        'description': 'Moderate priority requiring eventual response',
    },
    '4-Read-Later': {
        'color': '#34C759',      # Green
        'priority': 'low',
        'keywords': ['newsletter', 'unsubscribe', 'digest', 'update'],
        'description': 'Informational content for later review',
    },
    '5-Reference': {
        'color': '#8E8E93',      # Gray
        'priority': 'low',
        'description': 'Archive-worthy, low-urgency information',
    },
}


def route_email(
    packets: Dict[str, VSEPacket],
    metadata: EmailMetadata,
) -> EmailAnalysis:
    """
    Combine agent packets into unified semantic routing decision.
    
    This implements the full routing pipeline:
    1. Benevolent fusion to merge signals
    2. Newsletter/bulk mail detection
    3. Threshold-based routing
    4. Benevolence protection for personal mail
    5. Glyph generation for semantic fingerprint
    
    Args:
        packets: Dictionary of VSE packets from all agents
        metadata: Email metadata (sender, subject, date)
        
    Returns:
        EmailAnalysis with complete routing decision and auditability
    """
    # Step 1: Benevolent fusion
    urgency, importance, warmth, tension = benevolence_clamp(packets)
    
    # Step 2: Generate PICTOGRAM-256 semantic fingerprint
    # Combine all agent motifs for topologically stable glyph
    combined_motif = b''.join(p.semantic_motif for p in packets.values())
    icon = glyph_from_hash(combined_motif[:32])  # Use first 32 bytes (SHA-256 size)
    
    # Step 3: Extract agent-specific insights
    topic_packet = packets.get('topic')
    topic_gloss = topic_packet.gloss if topic_packet else "Primary topic: general"
    
    action_packet = packets.get('action')
    action_gloss = action_packet.gloss if action_packet else "No action required"
    
    tone_packet = packets.get('tone')
    
    # Step 4: Newsletter/bulk mail detection
    # Check for newsletter markers in glosses and content
    body_text = ' '.join(p.gloss for p in packets.values()).lower()
    subject_lower = metadata.subject.lower()
    sender_lower = metadata.sender.lower()
    
    is_newsletter = any([
        'newsletter' in body_text,
        'unsubscribe' in body_text,
        'digest' in subject_lower,
        'weekly' in subject_lower and 'update' in subject_lower,
        'newsletter@' in sender_lower,
        'noreply@' in sender_lower,
    ])
    
    # Step 5: Determine routing category
    folder = '5-Reference'  # Default
    color = ROUTING_CATEGORIES['5-Reference']['color']
    priority = ROUTING_CATEGORIES['5-Reference']['priority']
    
    # Apply routing thresholds (in priority order)
    if urgency > ROUTING_CATEGORIES['1-URGENT-NOW']['threshold_urgency']:
        folder = '1-URGENT-NOW'
        color = ROUTING_CATEGORIES['1-URGENT-NOW']['color']
        priority = ROUTING_CATEGORIES['1-URGENT-NOW']['priority']
        
    elif importance > ROUTING_CATEGORIES['2-Important']['threshold_importance']:
        folder = '2-Important'
        color = ROUTING_CATEGORIES['2-Important']['color']
        priority = ROUTING_CATEGORIES['2-Important']['priority']
        
    elif is_newsletter:
        folder = '4-Read-Later'
        color = ROUTING_CATEGORIES['4-Read-Later']['color']
        priority = ROUTING_CATEGORIES['4-Read-Later']['priority']
        
    elif (urgency > ROUTING_CATEGORIES['3-Action-Required']['threshold_urgency'] or
          importance > ROUTING_CATEGORIES['3-Action-Required']['threshold_importance']):
        folder = '3-Action-Required'
        color = ROUTING_CATEGORIES['3-Action-Required']['color']
        priority = ROUTING_CATEGORIES['3-Action-Required']['priority']
    
    # Step 6: Benevolence clamp for personal communications
    # High-warmth personal mail should never be auto-archived as low-priority
    if warmth > 0.6 and folder == '5-Reference':
        folder = '3-Action-Required'
        color = ROUTING_CATEGORIES['3-Action-Required']['color']
        priority = ROUTING_CATEGORIES['3-Action-Required']['priority']
    
    # Step 7: Generate unified gloss (legibility rule)
    # Create human-readable summary of the email's meaning
    gloss = _generate_unified_gloss(
        packets=packets,
        urgency=urgency,
        importance=importance,
        warmth=warmth,
        tension=tension,
        topic_gloss=topic_gloss,
    )
    
    # Step 8: Return complete analysis with full auditability
    return EmailAnalysis(
        icon=icon,
        gloss=gloss,
        routing_folder=folder,
        routing_color=color,
        routing_priority=priority,
        action=action_gloss,
        topic=topic_gloss,
        urgency=urgency,
        importance=importance,
        warmth=warmth,
        tension=tension,
        metadata=metadata,
        packets=packets,  # Non-destructive: all agent packets preserved
    )


def _generate_unified_gloss(
    packets: Dict[str, VSEPacket],
    urgency: float,
    importance: float,
    warmth: float,
    tension: float,
    topic_gloss: str,
) -> str:
    """
    Generate human-readable poetic summary (legibility rule).
    
    This implements the legibility invariant: every routing decision
    must be comprehensible to humans without technical knowledge.
    
    Args:
        packets: All agent packets
        urgency: Merged urgency score
        importance: Merged importance score
        warmth: Merged warmth score
        tension: Merged tension score
        topic_gloss: Topic summary from topic agent
        
    Returns:
        Natural language summary of email meaning
    """
    # Build tone descriptor list
    tone_descriptors = []
    
    if warmth > 0.5:
        tone_descriptors.append("warm")
    elif warmth < -0.3:
        tone_descriptors.append("cold")
    
    if urgency > 0.7:
        tone_descriptors.append("urgent")
    elif urgency > 0.4:
        tone_descriptors.append("time-sensitive")
    
    if importance > 0.6:
        tone_descriptors.append("significant")
    elif importance > 0.3:
        tone_descriptors.append("important")
    
    if tension > 0.5:
        tone_descriptors.append("tense")
    
    # Extract topic from gloss
    if ":" in topic_gloss:
        topic = topic_gloss.split(":", 1)[1].strip()
    else:
        topic = "communication"
    
    # Construct gloss
    if not tone_descriptors:
        tone_str = "routine"
    else:
        # Avoid repetition
        tone_descriptors = list(dict.fromkeys(tone_descriptors))  # Remove duplicates
        tone_str = " and ".join(tone_descriptors)
    
    return f"A {tone_str} message about {topic}"


# ============================================================================
# Routing Explanation (for debugging/auditability)
# ============================================================================

def explain_routing(analysis: EmailAnalysis) -> str:
    """
    Generate detailed explanation of routing decision.
    
    This is for debugging and auditability - showing exactly why
    an email was routed to a particular folder.
    
    Args:
        analysis: Complete email analysis
        
    Returns:
        Multi-line explanation of routing logic
    """
    lines = [
        "Routing Decision Explanation:",
        "=" * 50,
        f"Final Routing: {analysis.routing_folder}",
        f"Priority: {analysis.routing_priority}",
        "",
        "Merged Signals:",
        f"  Urgency:    {analysis.urgency:.2f}",
        f"  Importance: {analysis.importance:.2f}",
        f"  Warmth:     {analysis.warmth:.2f}",
        f"  Tension:    {analysis.tension:.2f}",
        "",
        "Agent Contributions:",
    ]
    
    for role, packet in analysis.packets.items():
        lines.append(f"  {role.upper()}:")
        lines.append(f"    Gloss: {packet.gloss}")
        lines.append(f"    Confidence: {packet.confidence:.2f}")
    
    lines.extend([
        "",
        "Routing Logic Applied:",
    ])
    
    # Explain which threshold triggered
    if analysis.urgency > 0.7:
        lines.append(f"  ✓ Urgency {analysis.urgency:.2f} > 0.7 → URGENT-NOW")
    elif analysis.importance > 0.6:
        lines.append(f"  ✓ Importance {analysis.importance:.2f} > 0.6 → Important")
    elif analysis.warmth > 0.6 and analysis.routing_folder == '3-Action-Required':
        lines.append(f"  ✓ Warmth {analysis.warmth:.2f} > 0.6 → Benevolence clamp activated")
        lines.append(f"    (Prevented auto-archive of personal communication)")
    
    return "\n".join(lines)
