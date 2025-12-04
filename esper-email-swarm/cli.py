"""
ESPER Email Swarm - Command Line Interface

Provides user-friendly CLI for email analysis with multiple output formats.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List

from .processor import process_email, process_email_file
from .imap_client import IMAPClient, get_imap_config, IMAP_SERVERS
from .router import explain_routing
from . import __version__


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        argv: Command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        prog='esper-email',
        description='ESPER-STACK Semantic Email Management Swarm',
        epilog='"Teaching a neighbor to read is a labor of love." - The Cyrano de Bergerac Foundation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'ESPER Email Swarm v{__version__}',
    )
    
    # Input source (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--email',
        metavar='PATH',
        help='Path to a single .eml file to process',
    )
    input_group.add_argument(
        '--imap',
        action='store_true',
        help='Fetch and process messages from IMAP server',
    )
    
    # IMAP options
    imap_group = parser.add_argument_group('IMAP options')
    imap_group.add_argument(
        '--host',
        help='IMAP server hostname (e.g., imap.gmail.com)',
    )
    imap_group.add_argument(
        '--user',
        help='IMAP username or email address',
    )
    imap_group.add_argument(
        '--password',
        help='IMAP password (or use IMAP_PASSWORD env var)',
    )
    imap_group.add_argument(
        '--provider',
        choices=list(IMAP_SERVERS.keys()),
        help='Use pre-configured IMAP settings for common providers',
    )
    imap_group.add_argument(
        '--mailbox',
        default='INBOX',
        help='Mailbox to fetch from (default: INBOX)',
    )
    imap_group.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of messages to fetch (default: 10)',
    )
    imap_group.add_argument(
        '--search',
        default='ALL',
        metavar='CRITERIA',
        help='IMAP search criteria (default: ALL). Examples: UNSEEN, FROM "user@example.com"',
    )
    
    # Output options
    output_group = parser.add_argument_group('Output options')
    output_group.add_argument(
        '--json',
        dest='json_out',
        metavar='PATH',
        help='Write JSON output to file',
    )
    output_group.add_argument(
        '--format',
        choices=['pretty', 'json', 'minimal'],
        default='pretty',
        help='Output format (default: pretty)',
    )
    output_group.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed agent packet analysis',
    )
    output_group.add_argument(
        '--explain',
        action='store_true',
        help='Show detailed routing decision explanation',
    )
    output_group.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress all output except errors',
    )
    
    args = parser.parse_args(argv)
    
    # Validate IMAP arguments
    if args.imap:
        if args.provider:
            # Use provider config
            config = get_imap_config(args.provider)
            if not args.host:
                args.host = config['host']
        
        if not args.host or not args.user:
            parser.error('--imap requires --host and --user (or use --provider)')
    
    # Process emails
    try:
        results = []
        
        if args.email:
            # Single file mode
            if not Path(args.email).exists():
                print(f"Error: File not found: {args.email}", file=sys.stderr)
                return 1
            
            analysis = process_email_file(args.email)
            results.append(analysis)
            
        elif args.imap:
            # IMAP mode
            if not args.quiet:
                print(f"Connecting to {args.host}...", file=sys.stderr)
            
            with IMAPClient(args.host, args.user, args.password) as client:
                messages = client.fetch_messages(
                    mailbox=args.mailbox,
                    limit=args.limit,
                    search_criteria=args.search,
                )
                
                if not args.quiet:
                    print(f"Processing {len(messages)} messages...", file=sys.stderr)
                
                for msg_id, raw_email in messages:
                    try:
                        analysis = process_email(raw_email)
                        results.append(analysis)
                    except Exception as e:
                        print(f"Warning: Failed to process message {msg_id}: {e}", file=sys.stderr)
                        continue
        
        # Output results
        if not args.quiet:
            _display_results(results, args)
        
        # Write JSON if requested
        if args.json_out:
            _write_json(results, args.json_out)
            if not args.quiet:
                print(f"\n✅ Results exported to {args.json_out}", file=sys.stderr)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _display_results(results: List, args: argparse.Namespace) -> None:
    """Display results based on format option"""
    
    for i, analysis in enumerate(results):
        if i > 0:
            print()  # Blank line between results
        
        if args.format == 'pretty':
            # Pretty terminal output
            print(analysis.pretty())
            
            if args.verbose:
                # Show individual agent packets
                print("\n🔬 Agent Packet Analysis:")
                for role, packet in analysis.packets.items():
                    print(f"\n   {role.upper()} Agent:")
                    print(f"      Gloss: {packet.gloss}")
                    print(f"      Confidence: {packet.confidence:.2f}")
                    print(f"      Urgency: {packet.intent_spine.urgency:.2f}")
                    print(f"      Importance: {packet.intent_spine.importance:.2f}")
                    print(f"      Warmth: {packet.intent_spine.warmth:.2f}")
            
            if args.explain:
                # Show routing explanation
                print("\n" + explain_routing(analysis))
        
        elif args.format == 'json':
            # JSON output to stdout
            print(json.dumps(analysis.to_json_dict(), indent=2))
        
        elif args.format == 'minimal':
            # Minimal one-line output
            print(f"{analysis.icon} [{analysis.routing_folder}] {analysis.metadata.subject}")


def _write_json(results: List, filepath: str) -> None:
    """Write results to JSON file"""
    
    # If single result, write as object; if multiple, write as array
    if len(results) == 1:
        data = results[0].to_json_dict()
    else:
        data = [r.to_json_dict() for r in results]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _print_help_imap() -> None:
    """Print helpful IMAP setup information"""
    print("""
IMAP Setup Guide
================

Gmail:
  1. Enable IMAP in Gmail settings
  2. Generate app-specific password: https://myaccount.google.com/apppasswords
  3. Use: --provider gmail --user you@gmail.com
  
Outlook/Office365:
  --provider outlook --user you@outlook.com

iCloud:
  1. Generate app-specific password: https://appleid.apple.com/account/manage
  2. Use: --provider icloud --user you@icloud.com

Yahoo:
  1. Generate app-specific password in account settings
  2. Use: --provider yahoo --user you@yahoo.com

Environment Variable:
  export IMAP_PASSWORD="your_app_password"
  
Then ESPER won't prompt for password.
""")


if __name__ == '__main__':
    sys.exit(main())
