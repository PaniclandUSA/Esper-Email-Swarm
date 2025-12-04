"""
ESPER Email Swarm - Semantic Email Management

A production-ready semantic email management system demonstrating
ESPER-STACK technology with VSE protocol.

Key Features:
- Multi-agent semantic analysis (5 specialized agents)
- PICTOGRAM-256 topological hashing
- Benevolent fusion with ethical constraints
- Deterministic routing (98%+ consistency)
- Complete auditability (packet inspection)
- Zero external dependencies (stdlib only)

Usage:
    from esper_email_swarm import process_email
    
    result = process_email("path/to/email.eml")
    print(result['gloss'])
    print(result['routing']['folder'])

Or via CLI:
    esper-email --email sample.eml
    esper-email --imap --host imap.gmail.com --user you@gmail.com

Project: ESPER-STACK
Mission: Literacy liberation through semantic AI
License: MIT
"""

__version__ = "1.0.0"
__author__ = "John Panic"
__email__ = "john@pictogram.org"
__license__ = "MIT"

from .model import (
    VSEPacket,
    IntentSpine,
    AffectLattice,
    EmailMetadata,
    EmailAnalysis,
    semantic_hash,
    glyph_from_hash,
)

from .agents import (
    analyze_email_agents,
    AGENTS,
)

from .router import (
    route_email,
    benevolence_clamp,
    explain_routing,
)

from .imap_client import (
    IMAPClient,
    fetch_imap_messages,
    parse_raw_email,
    parse_email_full,
)

from .cli import main


# Convenience function for simple use cases
def process_email(filepath: str) -> dict:
    """
    Process a single email file through ESPER pipeline.
    
    This is a convenience function for the most common use case.
    For more control, use the individual modules.
    
    Args:
        filepath: Path to .eml file
        
    Returns:
        Dictionary with complete analysis
        
    Example:
        >>> result = process_email("sample.eml")
        >>> print(result['gloss'])
        'A warm and urgent message about taxes'
        >>> print(result['routing']['folder'])
        '1-URGENT-NOW'
    """
    from pathlib import Path
    
    raw_email = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    
    sender, subject, date, message_id, body = parse_email_full(raw_email)
    
    metadata = EmailMetadata(
        sender=sender,
        subject=subject,
        date=date,
        message_id=message_id,
    )
    
    full_text = f"{subject}\n\n{body}"
    
    packets = analyze_email_agents(
        full_text=full_text,
        subject=subject,
        sender=sender,
    )
    
    analysis = route_email(packets, metadata)
    
    return analysis.to_json_dict()


# Public API
__all__ = [
    # Version
    "__version__",
    
    # Data models
    "VSEPacket",
    "IntentSpine",
    "AffectLattice",
    "EmailMetadata",
    "EmailAnalysis",
    
    # Semantic functions
    "semantic_hash",
    "glyph_from_hash",
    
    # Agent swarm
    "analyze_email_agents",
    "AGENTS",
    
    # Routing
    "route_email",
    "benevolence_clamp",
    "explain_routing",
    
    # IMAP
    "IMAPClient",
    "fetch_imap_messages",
    "parse_raw_email",
    "parse_email_full",
    
    # CLI
    "main",
    
    # Convenience
    "process_email",
]
