#!/usr/bin/env python3
"""
ESPER Email Swarm - Backward Compatible Entry Point

This file maintains backward compatibility with the original
single-file implementation. The actual code now lives in the
esper_email_swarm package for better organization.

Usage:
    python esper_email_swarm.py --email sample.eml
    python esper_email_swarm.py --imap --host imap.gmail.com --user you@gmail.com

All the original functionality is preserved, but the code is now
modular, testable, and maintainable.
"""

import sys

# Import from the package
from esper_email_swarm.cli import main

if __name__ == '__main__':
    sys.exit(main())
