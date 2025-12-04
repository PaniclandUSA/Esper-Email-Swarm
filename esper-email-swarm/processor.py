"""
ESPER Email Swarm - Email Processor

Handles email parsing, body extraction, and orchestrates the analysis pipeline.
"""

from __future__ import annotations

import email
from email.header import decode_header
from typing import Dict, Optional

from .model import EmailMetadata, EmailAnalysis
from .agents import analyze_email_agents
from .router import route_email


def process_email(raw_email: str) -> EmailAnalysis:
    """
    Process a raw email string through the full ESPER pipeline.
    
    This is the main entry point for email analysis:
    1. Parse email headers and body
    2. Run 5-agent semantic analysis
    3. Perform benevolent fusion and routing
    4. Return complete analysis with auditability
    
    Args:
        raw_email: Raw RFC822 email string
        
    Returns:
        EmailAnalysis with complete routing decision
        
    Example:
        >>> with open('email.eml', 'r') as f:
        ...     raw = f.read()
        >>> analysis = process_email(raw)
        >>> print(analysis.pretty())
    """
    # Parse email
    msg = email.message_from_string(raw_email)
    
    # Extract metadata
    metadata = EmailMetadata(
        sender=_decode_header_value(msg.get('From', '')),
        subject=_decode_header_value(msg.get('Subject', '')),
        date=msg.get('Date', ''),
        message_id=msg.get('Message-ID', ''),
        to=_decode_header_value(msg.get('To', '')),
    )
    
    # Extract body
    body = _extract_body(msg)
    
    # Combine for agent analysis
    # Include subject in analysis (important semantic signal)
    full_text = f"From: {metadata.sender}\nSubject: {metadata.subject}\n\n{body}"
    
    # Create metadata dict for agents
    metadata_dict = {
        'sender': metadata.sender,
        'subject': metadata.subject,
        'date': metadata.date,
    }
    
    # Run agent swarm
    packets = analyze_email_agents(full_text, metadata_dict)
    
    # Perform benevolent fusion and routing
    analysis = route_email(packets, metadata)
    
    return analysis


def process_email_file(filepath: str) -> EmailAnalysis:
    """
    Process an email from a file (.eml format).
    
    Args:
        filepath: Path to .eml file
        
    Returns:
        EmailAnalysis with complete routing decision
        
    Example:
        >>> analysis = process_email_file('examples/urgent.eml')
        >>> print(f"Route to: {analysis.routing_folder}")
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw_email = f.read()
    return process_email(raw_email)


def _decode_header_value(header: str) -> str:
    """
    Decode email header with proper encoding handling.
    
    Email headers can be encoded in various character sets.
    This function handles decoding safely.
    
    Args:
        header: Raw header string
        
    Returns:
        Decoded string in UTF-8
    """
    if not header:
        return ""
    
    try:
        decoded_parts = decode_header(header)
        result = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                # Decode bytes with specified encoding or UTF-8 fallback
                charset = encoding or 'utf-8'
                try:
                    result += part.decode(charset, errors='replace')
                except (UnicodeDecodeError, LookupError):
                    result += part.decode('utf-8', errors='replace')
            else:
                result += part
        
        return result
    except Exception:
        # Fallback: return as-is if decoding fails
        return header


def _extract_body(msg: email.message.Message) -> str:
    """
    Extract email body, handling multipart messages and different content types.
    
    This handles:
    - Plain text emails
    - HTML emails (strips HTML tags)
    - Multipart emails (text/plain preferred over text/html)
    - Various encodings
    
    Args:
        msg: Parsed email message
        
    Returns:
        Email body as plain text string
    """
    body = ""
    
    if msg.is_multipart():
        # For multipart messages, prefer text/plain over text/html
        text_parts = []
        html_parts = []
        
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            
            # Skip attachments
            if 'attachment' in content_disposition:
                continue
            
            try:
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                
                charset = part.get_content_charset() or 'utf-8'
                text = payload.decode(charset, errors='replace')
                
                if content_type == 'text/plain':
                    text_parts.append(text)
                elif content_type == 'text/html':
                    html_parts.append(text)
                    
            except Exception:
                continue
        
        # Prefer plain text
        if text_parts:
            body = '\n\n'.join(text_parts)
        elif html_parts:
            # Use HTML but strip tags
            body = _strip_html('\n\n'.join(html_parts))
    else:
        # Single-part message
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='replace')
                
                # Strip HTML if content type is text/html
                if msg.get_content_type() == 'text/html':
                    body = _strip_html(body)
        except Exception:
            # Fallback to string payload
            body = str(msg.get_payload())
    
    # Cap body length for performance (keep first 8000 chars)
    # This is sufficient for semantic analysis while preventing
    # extremely long emails from slowing processing
    return body[:8000]


def _strip_html(html: str) -> str:
    """
    Strip HTML tags from text (simple implementation).
    
    For full HTML parsing, you could use BeautifulSoup,
    but this simple regex approach works for most emails.
    
    Args:
        html: HTML string
        
    Returns:
        Plain text with HTML tags removed
    """
    import re
    
    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    html = re.sub(r'<[^>]+>', '', html)
    
    # Decode HTML entities
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&amp;', '&')
    html = html.replace('&quot;', '"')
    html = html.replace('&#39;', "'")
    
    # Clean up whitespace
    html = re.sub(r'\n\s*\n', '\n\n', html)
    
    return html.strip()
