"""
ESPER Email Swarm - IMAP Client & Email Parsing

Utilities for fetching emails via IMAP and parsing email messages.
Handles:
- IMAP connection and authentication
- Message fetching with pagination
- Email header decoding
- MIME multipart parsing
- Body text extraction
"""

from __future__ import annotations

from typing import List, Tuple, Optional
import imaplib
import email
from email.header import decode_header
import os


# =============================================================================
# IMAP Client
# =============================================================================

class IMAPClient:
    """
    IMAP email client with connection management.
    
    Handles secure connection, authentication, and message fetching
    from IMAP servers (Gmail, Outlook, etc.).
    """
    
    def __init__(
        self,
        host: str,
        user: str,
        password: Optional[str] = None,
        use_ssl: bool = True,
    ):
        """
        Initialize IMAP client.
        
        Args:
            host: IMAP server hostname (e.g., imap.gmail.com)
            user: Email username/address
            password: Password or app-specific password (if None, reads from env)
            use_ssl: Use SSL/TLS connection (default: True)
        """
        self.host = host
        self.user = user
        self.password = password or os.environ.get("IMAP_PASSWORD", "")
        self.use_ssl = use_ssl
        self.conn: Optional[imaplib.IMAP4_SSL] = None
    
    def connect(self) -> None:
        """
        Establish connection to IMAP server.
        
        Raises:
            imaplib.IMAP4.error: If connection or authentication fails
        """
        if self.use_ssl:
            self.conn = imaplib.IMAP4_SSL(self.host)
        else:
            self.conn = imaplib.IMAP4(self.host)
        
        self.conn.login(self.user, self.password)
    
    def disconnect(self) -> None:
        """Close IMAP connection gracefully."""
        if self.conn:
            try:
                self.conn.close()
                self.conn.logout()
            except Exception:
                pass  # Connection may already be closed
            finally:
                self.conn = None
    
    def fetch_messages(
        self,
        mailbox: str = "INBOX",
        limit: int = 10,
        search_criteria: str = "ALL",
    ) -> List[Tuple[str, str]]:
        """
        Fetch messages from specified mailbox.
        
        Args:
            mailbox: Mailbox name (default: "INBOX")
            limit: Maximum number of messages to fetch
            search_criteria: IMAP search criteria (default: "ALL")
            
        Returns:
            List of (message_id, raw_email_string) tuples
            
        Raises:
            ValueError: If not connected
            imaplib.IMAP4.error: If IMAP operation fails
        """
        if not self.conn:
            raise ValueError("Not connected. Call connect() first.")
        
        # Select mailbox
        status, _ = self.conn.select(mailbox)
        if status != "OK":
            raise imaplib.IMAP4.error(f"Failed to select mailbox: {mailbox}")
        
        # Search for messages
        status, data = self.conn.search(None, search_criteria)
        if status != "OK":
            return []
        
        # Get message IDs (most recent first)
        message_ids = data[0].split()
        message_ids = message_ids[-limit:]  # Take last N messages
        
        messages: List[Tuple[str, str]] = []
        
        for msg_id in message_ids:
            try:
                # Fetch message
                status, msg_data = self.conn.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue
                
                # Extract raw email
                raw_bytes = msg_data[0][1]
                raw_str = raw_bytes.decode(errors="ignore")
                
                messages.append((msg_id.decode(), raw_str))
            
            except Exception as e:
                # Skip messages that fail to fetch
                print(f"Warning: Failed to fetch message {msg_id}: {e}")
                continue
        
        return messages
    
    def __enter__(self):
        """Context manager support."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.disconnect()


def fetch_imap_messages(
    host: str,
    user: str,
    password: Optional[str] = None,
    mailbox: str = "INBOX",
    limit: int = 10,
) -> List[Tuple[str, str]]:
    """
    Convenience function for fetching IMAP messages.
    
    Automatically handles connection and disconnection.
    
    Args:
        host: IMAP server hostname
        user: Email username/address
        password: Password (if None, reads from IMAP_PASSWORD env var)
        mailbox: Mailbox to fetch from (default: "INBOX")
        limit: Maximum messages to fetch (default: 10)
        
    Returns:
        List of (message_id, raw_email_string) tuples
    """
    with IMAPClient(host, user, password) as client:
        return client.fetch_messages(mailbox, limit)


# =============================================================================
# Email Parsing
# =============================================================================

def decode_header_value(header_value: str) -> str:
    """
    Decode email header with proper encoding handling.
    
    Email headers can be encoded in various character sets.
    This properly decodes them to Unicode strings.
    
    Args:
        header_value: Raw header value
        
    Returns:
        Decoded Unicode string
    """
    if not header_value:
        return ""
    
    decoded_parts = decode_header(header_value)
    result = ""
    
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                result += part.decode(encoding or "utf-8", errors="ignore")
            except (LookupError, UnicodeDecodeError):
                result += part.decode("utf-8", errors="ignore")
        else:
            result += str(part)
    
    return result


def extract_body_text(msg: email.message.Message, max_length: int = 10000) -> str:
    """
    Extract plain text body from email message.
    
    Handles both simple and multipart messages. Prioritizes
    text/plain parts, falls back to text/html if needed.
    
    Args:
        msg: Parsed email message
        max_length: Maximum body length to extract (default: 10000 chars)
        
    Returns:
        Plain text body content
    """
    body = ""
    
    if msg.is_multipart():
        # Handle multipart messages
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
            
            # Prioritize text/plain
            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body = payload.decode(charset, errors="ignore")
                        break  # Found text/plain, stop looking
                except Exception:
                    continue
            
            # Fallback to text/html if no text/plain found
            elif content_type == "text/html" and not body:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body = payload.decode(charset, errors="ignore")
                        # Continue looking for text/plain
                except Exception:
                    continue
    else:
        # Handle simple (non-multipart) messages
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="ignore")
        except Exception:
            body = str(msg.get_payload())
    
    # Limit body length for performance
    return body[:max_length]


def parse_raw_email(raw_email: str) -> Tuple[str, str, str, str]:
    """
    Parse raw email string into components.
    
    Extracts essential metadata from email headers.
    
    Args:
        raw_email: Complete raw email message (RFC822 format)
        
    Returns:
        Tuple of (sender, subject, date, message_id)
    """
    msg = email.message_from_string(raw_email)
    
    sender = decode_header_value(msg.get("From", ""))
    subject = decode_header_value(msg.get("Subject", ""))
    date = msg.get("Date", "")
    message_id = msg.get("Message-ID", "")
    
    return sender, subject, date, message_id


def parse_email_full(raw_email: str) -> Tuple[str, str, str, str, str]:
    """
    Parse raw email into components including body.
    
    Args:
        raw_email: Complete raw email message
        
    Returns:
        Tuple of (sender, subject, date, message_id, body_text)
    """
    msg = email.message_from_string(raw_email)
    
    sender = decode_header_value(msg.get("From", ""))
    subject = decode_header_value(msg.get("Subject", ""))
    date = msg.get("Date", "")
    message_id = msg.get("Message-ID", "")
    body = extract_body_text(msg)
    
    return sender, subject, date, message_id, body


# =============================================================================
# Email Validation
# =============================================================================

def is_valid_email_address(email_addr: str) -> bool:
    """
    Simple email address validation.
    
    Args:
        email_addr: Email address string
        
    Returns:
        True if format appears valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email_addr))


def extract_email_address(from_header: str) -> str:
    """
    Extract email address from From header.
    
    From headers often contain name and email like:
    "John Doe <john@example.com>"
    
    Args:
        from_header: Raw From header value
        
    Returns:
        Just the email address part
    """
    import re
    
    # Try to extract email from angle brackets
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1)
    
    # If no angle brackets, assume entire string is email
    return from_header.strip()


# =============================================================================
# Testing Utilities
# =============================================================================

def create_test_email(
    sender: str = "test@example.com",
    subject: str = "Test Email",
    body: str = "This is a test email.",
    date: str = "Wed, 4 Dec 2024 12:00:00 -0500",
) -> str:
    """
    Create a simple test email in RFC822 format.
    
    Useful for testing without connecting to real IMAP server.
    
    Args:
        sender: From address
        subject: Subject line
        body: Email body
        date: Date header
        
    Returns:
        Raw email string
    """
    return f"""From: {sender}
To: recipient@example.com
Subject: {subject}
Date: {date}
Message-ID: <test-{hash(body)}@example.com>
Content-Type: text/plain; charset=utf-8

{body}
"""
