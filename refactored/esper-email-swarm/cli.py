"""
ESPER Email Swarm - Command Line Interface

Provides command-line entry point for ESPER email analysis.
Supports:
- Single email file processing
- IMAP inbox processing
- JSON export
- Verbose output
- Batch processing
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict

from .agents import analyze_email_agents
from .router import route_email
from .model import EmailMetadata, EmailAnalysis
from .imap_client import fetch_imap_messages, parse_email_full


# =============================================================================
# Email Processing
# =============================================================================

def process_raw_email(raw_email: str) -> Dict:
    """
    Process a single raw email through the ESPER pipeline.
    
    Steps:
    1. Parse email headers and body
    2. Run 5-agent semantic analysis
    3. Apply benevolent fusion and routing
    4. Return JSON-serializable result
    
    Args:
        raw_email: Complete raw email string (RFC822 format)
        
    Returns:
        Dictionary with analysis results
    """
    from .imap_client import parse_email_full
    
    # Parse email
    sender, subject, date, message_id, body = parse_email_full(raw_email)
    
    metadata = EmailMetadata(
        sender=sender,
        subject=subject,
        date=date,
        message_id=message_id,
    )
    
    # Combine subject and body for analysis
    full_text = f"{subject}\n\n{body}"
    
    # Run agent swarm
    packets = analyze_email_agents(
        full_text=full_text,
        subject=subject,
        sender=sender,
    )
    
    # Route with benevolent fusion
    analysis = route_email(packets, metadata)
    
    # Return JSON-serializable dict
    return analysis.to_json_dict()


def read_email_file(filepath: str) -> str:
    """
    Read email file from disk.
    
    Args:
        filepath: Path to .eml file
        
    Returns:
        Raw email string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file can't be read
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"Email file not found: {filepath}")
    
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        raise IOError(f"Failed to read email file: {e}")


# =============================================================================
# Output Formatting
# =============================================================================

def print_analysis(result: Dict, verbose: bool = False) -> None:
    """
    Print email analysis to stdout in human-readable format.
    
    Args:
        result: Analysis result dictionary
        verbose: If True, show detailed agent packets
    """
    bar = "=" * 70
    
    # Format metric bars
    urgency_bar = "█" * int(result["urgency"] * 20)
    importance_bar = "█" * int(result["importance"] * 20)
    warmth_bar = "█" * int(result["warmth"] * 20)
    tension_bar = "█" * int(result["tension"] * 20)
    
    # Main output
    print(f"""
{bar}
  {result['icon']}  ESPER Email Analysis
{bar}

📧 From: {result['metadata']['sender']}
📝 Subject: {result['metadata']['subject']}
📅 Date: {result['metadata']['date'] or 'Unknown'}

💡 {result['gloss']}

📁 Routing: {result['routing']['folder']}
🎨 Priority: {result['routing']['priority'].upper()}
🎯 Action: {result['action']}

📊 Metrics:
   Urgency:    {urgency_bar} {result['urgency']:.2f}
   Importance: {importance_bar} {result['importance']:.2f}
   Warmth:     {warmth_bar} {result['warmth']:.2f}
   Tension:    {tension_bar} {result['tension']:.2f}

{bar}
""")
    
    # Verbose mode: show agent packets
    if verbose:
        print("🔬 Agent Packets:\n")
        for packet_data in result.get('packets', {}).values():
            role = packet_data['agent_role']
            gloss = packet_data['gloss']
            confidence = packet_data['packet_confidence']
            print(f"   • {role.capitalize()}: {gloss} (confidence: {confidence:.2f})")
        print(f"\n{bar}\n")


def export_json(results: List[Dict], output_path: str) -> None:
    """
    Export analysis results to JSON file.
    
    Args:
        results: List of analysis result dictionaries
        output_path: Path to output JSON file
    """
    path = Path(output_path)
    
    # If single result, unwrap from list
    data = results[0] if len(results) == 1 else results
    
    try:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"✅ Results exported to {output_path}")
    except Exception as e:
        print(f"❌ Failed to export JSON: {e}", file=sys.stderr)


# =============================================================================
# Command Line Interface
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="esper-email",
        description="ESPER-STACK semantic email swarm with VSE-style routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process a single email file:
    esper-email --email sample.eml
  
  Process IMAP inbox:
    esper-email --imap --host imap.gmail.com --user you@gmail.com --limit 10
  
  Export to JSON:
    esper-email --email sample.eml --json output.json
  
  Verbose analysis:
    esper-email --email sample.eml --verbose

Environment Variables:
  IMAP_PASSWORD - IMAP password (alternative to --password)
        """
    )
    
    # Input source (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--email",
        metavar="FILE",
        help="Path to .eml file to process"
    )
    input_group.add_argument(
        "--imap",
        action="store_true",
        help="Process messages from IMAP inbox"
    )
    
    # IMAP options
    imap_group = parser.add_argument_group("IMAP options")
    imap_group.add_argument(
        "--host",
        help="IMAP server hostname (e.g., imap.gmail.com)"
    )
    imap_group.add_argument(
        "--user",
        help="IMAP username/email address"
    )
    imap_group.add_argument(
        "--password",
        help="IMAP password (or set IMAP_PASSWORD env var)"
    )
    imap_group.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of messages to fetch (default: 10)"
    )
    imap_group.add_argument(
        "--mailbox",
        default="INBOX",
        help="Mailbox to fetch from (default: INBOX)"
    )
    
    # Output options
    output_group = parser.add_argument_group("output options")
    output_group.add_argument(
        "--json",
        dest="json_output",
        metavar="FILE",
        help="Export results to JSON file"
    )
    output_group.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed agent packet analysis"
    )
    output_group.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (use with --json)"
    )
    
    return parser


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """
    Validate command-line arguments.
    
    Args:
        args: Parsed arguments
        parser: Argument parser for error reporting
        
    Raises:
        SystemExit: If validation fails
    """
    # Validate IMAP arguments
    if args.imap:
        if not args.host or not args.user:
            parser.error("--imap requires --host and --user")
    
    # Validate file exists
    if args.email:
        if not Path(args.email).exists():
            parser.error(f"Email file not found: {args.email}")


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for CLI.
    
    Args:
        argv: Command-line arguments (for testing)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Validate arguments
    try:
        validate_args(args, parser)
    except SystemExit:
        return 1
    
    results: List[Dict] = []
    
    try:
        # Process emails
        if args.email:
            # Single file mode
            raw_email = read_email_file(args.email)
            result = process_raw_email(raw_email)
            results.append(result)
        
        elif args.imap:
            # IMAP mode
            print(f"📬 Connecting to {args.host}...", file=sys.stderr)
            
            messages = fetch_imap_messages(
                host=args.host,
                user=args.user,
                password=args.password,
                mailbox=args.mailbox,
                limit=args.limit,
            )
            
            print(f"📧 Processing {len(messages)} messages...\n", file=sys.stderr)
            
            for msg_id, raw_email in messages:
                try:
                    result = process_raw_email(raw_email)
                    result['metadata']['imap_id'] = msg_id
                    results.append(result)
                except Exception as e:
                    print(f"⚠️  Failed to process message {msg_id}: {e}", file=sys.stderr)
                    continue
        
        # Output results
        if not args.quiet:
            for result in results:
                print_analysis(result, verbose=args.verbose)
        
        # Export JSON if requested
        if args.json_output:
            export_json(results, args.json_output)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user", file=sys.stderr)
        return 130
    
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
