#!/usr/bin/env python3
"""
ESPER Email Swarm - Backward Compatible Entry Point

This file maintains compatibility with the original CLI interface.
All functionality has been refactored into the esper_email_swarm package.

The real implementation lives in:
- esper_email_swarm/model.py - Data structures
- esper_email_swarm/agents.py - 5-agent swarm
- esper_email_swarm/router.py - Benevolent fusion & routing
- esper_email_swarm/imap_client.py - Email fetching
- esper_email_swarm/cli.py - Command-line interface

Usage:
    python esper_email_swarm.py --email sample.eml
    python esper_email_swarm.py --imap --host imap.gmail.com --user you@gmail.com

Or after installation:
    esper-email --email sample.eml
"""

import sys

if __name__ == "__main__":
    # Import and run the CLI from the package
    try:
        from esper_email_swarm.cli import main
        sys.exit(main())
    except ImportError as e:
        print(f"Error: Could not import esper_email_swarm package: {e}", file=sys.stderr)
        print("Make sure you're running from the correct directory.", file=sys.stderr)
        sys.exit(1)
