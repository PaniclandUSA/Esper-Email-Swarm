"""
ESPER-STACK Email Management Swarm

A semantic operating system for email that understands meaning, not just keywords.

This package implements:
- Multi-agent VSE (Volume-Semantic-Encoding) semantic analysis
- PICTOGRAM-256 topological hashing for semantic fingerprints
- Benevolent fusion with ethical invariants (Volume 5)
- Deterministic routing (98%+ consistency)
- Complete auditability (full packet inspection)

Usage:
    from esper_email_swarm import process_email, EmailAnalysis
    
    analysis = process_email(raw_email_text)
    print(analysis.pretty())
    
Or via CLI:
    python -m esper_email_swarm --email sample.eml
    python esper_email_swarm.py --imap --host imap.gmail.com --user you@gmail.com

Part of the literacy liberation mission:
"Teaching a neighbor to read is a labor of love."
— The Cyrano de Bergerac Foundation
"""

__version__ = "2.0.0"
__author__ = "John Panic"
__license__ = "MIT"

from .model import (
    VSEPacket,
    EmailAnalysis,
    EmailMetadata,
    IntentSpine,
    AffectLattice,
)
from .agents import analyze_email_agents
from .router import route_email, benevolence_clamp
from .processor import process_email, process_email_file

__all__ = [
    # Core processing
    "process_email",
    "process_email_file",
    # Models
    "VSEPacket",
    "EmailAnalysis", 
    "EmailMetadata",
    "IntentSpine",
    "AffectLattice",
    # Agent system
    "analyze_email_agents",
    # Routing
    "route_email",
    "benevolence_clamp",
    # Metadata
    "__version__",
    "__author__",
    "__license__",
]
