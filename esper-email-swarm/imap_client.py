"""
ESPER Email Swarm - IMAP Client

Handles IMAP connections and email fetching.
Supports common IMAP providers (Gmail, Outlook, iCloud, etc.)
"""

from __future__ import annotations

import imaplib
import os
from typing import List, Tuple, Optional
import getpass


class IMAPClient:
    """
    IMAP email client for fetching messages.
    
    Example:
        >>> client = IMAPClient('imap.gmail.com', 'user@gmail.com')
        >>> messages = client.fetch_messages(limit=10)
        >>> for msg_id, raw_email in messages:
        ...     print(f"Processing message {msg_id}")
    """
    
    def __init__(
        self,
        host: str,
        username: str,
        password: Optional[str] = None,
        use_ssl: bool = True,
    ):
        """
        Initialize IMAP client.
        
        Args:
            host: IMAP server hostname (e.g., 'imap.gmail.com')
            username: Email address or username
            password: Password or app-specific password (if None, will check env or prompt)
            use_ssl: Whether to use SSL/TLS (recommended)
        """
        self.host = host
        self.username = username
        self.use_ssl = use_ssl
        
        # Get password from environment or prompt
        if password is None:
            password = os.environ.get('IMAP_PASSWORD')
            if password is None:
                password = getpass.getpass(f"Password for {username}: ")
        
        self.password = password
        self.connection: Optional[imaplib.IMAP4_SSL] = None
    
    def connect(self) -> None:
        """
        Establish connection to IMAP server.
        
        Raises:
            imaplib.IMAP4.error: If connection or authentication fails
        """
        if self.use_ssl:
            self.connection = imaplib.IMAP4_SSL(self.host)
        else:
            self.connection = imaplib.IMAP4(self.host)
        
        self.connection.login(self.username, self.password)
    
    def disconnect(self) -> None:
        """Close IMAP connection"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except Exception:
                pass
            self.connection = None
    
    def fetch_messages(
        self,
        mailbox: str = 'INBOX',
        limit: int = 10,
        search_criteria: str = 'ALL',
    ) -> List[Tuple[str, str]]:
        """
        Fetch messages from specified mailbox.
        
        Args:
            mailbox: Mailbox name (default: 'INBOX')
            limit: Maximum number of messages to fetch
            search_criteria: IMAP search criteria (default: 'ALL')
                Examples: 'UNSEEN', 'FROM "user@example.com"', 'SUBJECT "urgent"'
        
        Returns:
            List of (message_id, raw_email_string) tuples
            
        Raises:
            ValueError: If not connected
            imaplib.IMAP4.error: If mailbox selection or search fails
        """
        if not self.connection:
            raise ValueError("Not connected. Call connect() first.")
        
        # Select mailbox
        status, _ = self.connection.select(mailbox, readonly=True)
        if status != 'OK':
            raise imaplib.IMAP4.error(f"Failed to select mailbox: {mailbox}")
        
        # Search for messages
        status, data = self.connection.search(None, search_criteria)
        if status != 'OK':
            raise imaplib.IMAP4.error(f"Search failed with criteria: {search_criteria}")
        
        message_ids = data[0].split()
        
        # Get most recent N messages
        message_ids = message_ids[-limit:] if len(message_ids) > limit else message_ids
        
        messages: List[Tuple[str, str]] = []
        
        for msg_id in message_ids:
            try:
                # Fetch email
                status, msg_data = self.connection.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                raw_bytes = msg_data[0][1]
                raw_str = raw_bytes.decode('utf-8', errors='ignore')
                
                messages.append((msg_id.decode(), raw_str))
                
            except Exception as e:
                # Log but continue processing other messages
                print(f"Warning: Failed to fetch message {msg_id}: {e}")
                continue
        
        return messages
    
    def __enter__(self):
        """Context manager support"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.disconnect()
        return False


def fetch_imap_messages(
    host: str,
    username: str,
    password: Optional[str] = None,
    mailbox: str = 'INBOX',
    limit: int = 10,
    search_criteria: str = 'ALL',
) -> List[Tuple[str, str]]:
    """
    Convenience function to fetch messages without managing connection.
    
    This is a simpler interface for one-off fetches.
    
    Args:
        host: IMAP server hostname
        username: Email address or username
        password: Password (if None, checks env or prompts)
        mailbox: Mailbox to fetch from (default: 'INBOX')
        limit: Maximum number of messages
        search_criteria: IMAP search string
        
    Returns:
        List of (message_id, raw_email_string) tuples
        
    Example:
        >>> messages = fetch_imap_messages(
        ...     'imap.gmail.com',
        ...     'user@gmail.com',
        ...     limit=5
        ... )
    """
    with IMAPClient(host, username, password) as client:
        return client.fetch_messages(mailbox, limit, search_criteria)


# Common IMAP server configurations
IMAP_SERVERS = {
    'gmail': {
        'host': 'imap.gmail.com',
        'port': 993,
        'ssl': True,
        'notes': 'Requires app-specific password if 2FA enabled',
    },
    'outlook': {
        'host': 'outlook.office365.com',
        'port': 993,
        'ssl': True,
        'notes': 'Works for Outlook.com and Office 365',
    },
    'yahoo': {
        'host': 'imap.mail.yahoo.com',
        'port': 993,
        'ssl': True,
        'notes': 'Requires app-specific password',
    },
    'icloud': {
        'host': 'imap.mail.me.com',
        'port': 993,
        'ssl': True,
        'notes': 'Requires app-specific password',
    },
    'aol': {
        'host': 'imap.aol.com',
        'port': 993,
        'ssl': True,
        'notes': 'May require app-specific password',
    },
}


def get_imap_config(provider: str) -> dict:
    """
    Get IMAP configuration for common email providers.
    
    Args:
        provider: Provider name (gmail, outlook, yahoo, icloud, aol)
        
    Returns:
        Dictionary with host, port, ssl settings
        
    Raises:
        ValueError: If provider not recognized
        
    Example:
        >>> config = get_imap_config('gmail')
        >>> client = IMAPClient(config['host'], 'user@gmail.com')
    """
    provider_lower = provider.lower()
    if provider_lower not in IMAP_SERVERS:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Available: {', '.join(IMAP_SERVERS.keys())}"
        )
    
    return IMAP_SERVERS[provider_lower].copy()
