"""
ESPER Email Swarm - Routing Engine

Implements benevolent fusion of VSE packets and semantic routing.
Enforces Volume 5 invariants:
- Benevolence clamp: Protects personal communications
- Legibility rule: All decisions have natural language explanations
- Non-destructive merging: All agent signals preserved

All routing is deterministic and fully auditable.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .model import (
    VSEPacket,
    EmailAnalysis,
    EmailMetadata,
    glyph_from_hash,
)


# =============================================================================
# Routing Categories
# =============================================================================

class RoutingCategory:
    """Predefined routing categories with colors and priorities."""
    
    URGENT_NOW = {
        "folder": "1-URGENT-NOW",
        "color": "#FF3B30",  # Red
        "priority": "critical",
        "threshold": lambda u, i: u > 0.7,
    }
    
    IMPORTANT = {
        "folder": "2-Important",
        "color": "#FF9500",  # Orange
        "priority": "high",
        "threshold": lambda u, i: i > 0.6,
    }
    
    ACTION_REQUIRED = {
        "folder": "3-Action-Required",
        "color": "#FFCC00",  # Yellow
        "priority": "medium",
        "threshold": lambda u, i: u > 0.4 or i > 0.3,
    }
    
    READ_LATER = {
        "folder": "4-Read-Later",
        "color": "#34C759",  # Green
        "priority": "low",
        "threshold": lambda u, i: False,  # Special case for newsletters
    }
    
    REFERENCE = {
        "folder": "5-Reference",
        "color": "#8E8E93",  # Gray
        "priority": "low",
        "threshold": lambda u, i: True,  # Default fallback
    }


# =============================================================================
# Benevolent Fusion Engine
# =============================================================================

def benevolence_clamp(packets: Dict[str, VSEPacket]) -> Tuple[float, float, float, float]:
    """
    Merge agent packets using Volume 5 benevolent fusion.
    
    Implements ethical constraints:
    1. Average signals across agents (equal weighting)
    2. Protect warmth: high warmth prevents harmful routing
    3. Balance tension with warmth (prevent conflict dominance)
    
    This ensures personal communications are never mishandled
    and all signals are preserved for auditability.
    
    Args:
        packets: Dictionary of agent packets
        
    Returns:
        Tuple of (urgency, importance, warmth, tension) scores
        
    Raises:
        ValueError: If packets dictionary is empty
    """
    if not packets:
        raise ValueError("Cannot merge empty packet dictionary")
    
    n = float(len(packets))
    
    # Average core signals across all agents
    urgency = sum(p.intent_spine.urgency for p in packets.values()) / n
    importance = sum(p.intent_spine.importance for p in packets.values()) / n
    warmth = sum(p.intent_spine.warmth for p in packets.values()) / n
    tension = sum(p.intent_spine.tension for p in packets.values()) / n
    
    # Benevolence clamp: if warmth is high, prevent tension from dominating
    # This protects loving but stressed communications (e.g., worried parent)
    if warmth > 0.6 and tension > 0.7:
        tension = (tension + warmth) / 2.0
    
    # Cap all values to [0, 1] range
    urgency = max(0.0, min(1.0, urgency))
    importance = max(0.0, min(1.0, importance))
    warmth = max(0.0, min(1.0, warmth))
    tension = max(0.0, min(1.0, tension))
    
    return urgency, importance, warmth, tension


def _detect_newsletter(packets: Dict[str, VSEPacket], subject: str) -> bool:
    """
    Detect newsletter/bulk mail patterns.
    
    Looks for:
    - "newsletter" or "digest" in content
    - "unsubscribe" links
    - Newsletter-like subjects
    
    Args:
        packets: Agent packets
        subject: Email subject line
        
    Returns:
        True if email appears to be newsletter
    """
    combined_text = " ".join(p.gloss.lower() for p in packets.values())
    subject_lower = subject.lower()
    
    newsletter_indicators = [
        'newsletter' in combined_text,
        'unsubscribe' in combined_text,
        'digest' in subject_lower,
        'weekly update' in subject_lower,
        'monthly update' in subject_lower,
    ]
    
    return any(newsletter_indicators)


def _generate_unified_gloss(
    packets: Dict[str, VSEPacket],
    urgency: float,
    importance: float,
    warmth: float,
    tension: float,
) -> str:
    """
    Generate human-readable unified summary (legibility rule).
    
    Combines agent glosses into a single natural language summary
    that captures the essential meaning of the email.
    
    Args:
        packets: Agent packets
        urgency: Merged urgency score
        importance: Merged importance score
        warmth: Merged warmth score
        tension: Merged tension score
        
    Returns:
        Natural language summary string
    """
    # Build tone descriptors
    tone_descriptors = []
    if warmth > 0.5:
        tone_descriptors.append("warm")
    if tension > 0.5:
        tone_descriptors.append("pressing")
    if urgency > 0.7:
        tone_descriptors.append("urgent")
    if importance > 0.6:
        tone_descriptors.append("significant")
    
    if not tone_descriptors:
        tone_descriptors.append("routine")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_descriptors = []
    for desc in tone_descriptors:
        if desc not in seen:
            seen.add(desc)
            unique_descriptors.append(desc)
    
    tone_str = " and ".join(unique_descriptors)
    
    # Extract topic from topic agent
    topic_packet = packets.get("topic")
    if topic_packet and ":" in topic_packet.gloss:
        topic = topic_packet.gloss.split(":", 1)[1].strip()
    else:
        topic = "communication"
    
    return f"A {tone_str} message about {topic}"


def route_email(
    packets: Dict[str, VSEPacket],
    metadata: EmailMetadata,
) -> EmailAnalysis:
    """
    Combine agent packets into unified semantic routing decision.
    
    This is the main routing engine that:
    1. Merges packets via benevolent fusion
    2. Applies routing logic with ethical constraints
    3. Generates human-readable summary (legibility rule)
    4. Preserves all agent packets (non-destructive merging)
    
    Args:
        packets: Dictionary of agent packets (one per agent)
        metadata: Email metadata (sender, subject, date)
        
    Returns:
        Complete EmailAnalysis with routing decision
        
    Raises:
        ValueError: If packets is empty
    """
    # Step 1: Benevolent fusion
    urgency, importance, warmth, tension = benevolence_clamp(packets)
    
    # Step 2: Generate semantic icon (PICTOGRAM-256)
    # Use the first packet's motif as representative hash
    first_motif = next(iter(packets.values())).semantic_motif
    icon = glyph_from_hash(first_motif)
    
    # Step 3: Detect special cases
    is_newsletter = _detect_newsletter(packets, metadata.subject)
    
    # Step 4: Determine routing category
    routing = None
    
    # Priority order: check most urgent first
    if RoutingCategory.URGENT_NOW["threshold"](urgency, importance):
        routing = RoutingCategory.URGENT_NOW
    elif RoutingCategory.IMPORTANT["threshold"](urgency, importance):
        routing = RoutingCategory.IMPORTANT
    elif is_newsletter:
        routing = RoutingCategory.READ_LATER
    elif RoutingCategory.ACTION_REQUIRED["threshold"](urgency, importance):
        routing = RoutingCategory.ACTION_REQUIRED
    else:
        routing = RoutingCategory.REFERENCE
    
    # Step 5: Apply benevolence clamp (ethical constraint)
    # High-warmth personal mail is never auto-archived as low-priority
    if warmth > 0.6 and routing["folder"] == "5-Reference":
        routing = RoutingCategory.ACTION_REQUIRED
    
    # Step 6: Extract action and topic from agent packets
    action_packet = packets.get("action")
    action_gloss = action_packet.gloss if action_packet else "No specific action required"
    
    topic_packet = packets.get("topic")
    topic_gloss = topic_packet.gloss if topic_packet else "Primary topic: general"
    
    # Step 7: Generate unified gloss (legibility rule)
    unified_gloss = _generate_unified_gloss(packets, urgency, importance, warmth, tension)
    
    # Step 8: Create final analysis (non-destructive merging)
    return EmailAnalysis(
        icon=icon,
        gloss=unified_gloss,
        routing_folder=routing["folder"],
        routing_color=routing["color"],
        routing_priority=routing["priority"],
        action=action_gloss,
        topic=topic_gloss,
        urgency=urgency,
        importance=importance,
        warmth=warmth,
        tension=tension,
        metadata=metadata,
        packets=packets,  # All agent signals preserved
    )


# =============================================================================
# Routing Utilities
# =============================================================================

def explain_routing(analysis: EmailAnalysis) -> str:
    """
    Generate detailed explanation of routing decision.
    
    For auditability and transparency, this explains why
    an email was routed to a particular category.
    
    Args:
        analysis: Complete email analysis
        
    Returns:
        Multi-line explanation string
    """
    explanations = []
    
    # Explain primary routing factors
    if analysis.urgency > 0.7:
        explanations.append(
            f"• High urgency detected ({analysis.urgency:.2f}) - time-critical content"
        )
    
    if analysis.importance > 0.6:
        explanations.append(
            f"• High importance detected ({analysis.importance:.2f}) - significant long-term impact"
        )
    
    if analysis.warmth > 0.6:
        explanations.append(
            f"• Personal communication detected ({analysis.warmth:.2f}) - relationship warmth"
        )
    
    if analysis.tension > 0.5:
        explanations.append(
            f"• Tension detected ({analysis.tension:.2f}) - conflict or stress indicators"
        )
    
    # Explain benevolence clamp application
    if analysis.warmth > 0.6 and analysis.routing_folder != "5-Reference":
        explanations.append(
            "• Benevolence clamp applied - personal emails protected from auto-archive"
        )
    
    # Explain newsletter detection
    if analysis.routing_folder == "4-Read-Later":
        explanations.append(
            "• Newsletter/bulk mail detected - routed to read-later"
        )
    
    if not explanations:
        explanations.append("• Standard routing based on moderate signals")
    
    return "\n".join(explanations)


def suggest_custom_routing(
    analysis: EmailAnalysis,
    custom_rules: Dict[str, callable]
) -> str:
    """
    Apply custom user-defined routing rules.
    
    Allows users to override default routing with their own logic.
    
    Args:
        analysis: Email analysis to evaluate
        custom_rules: Dictionary mapping folder names to predicate functions
        
    Returns:
        Custom folder name, or original if no rules match
    """
    for folder, predicate in custom_rules.items():
        try:
            if predicate(analysis):
                return folder
        except Exception:
            continue  # Skip invalid rules
    
    return analysis.routing_folder
