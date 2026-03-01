#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new important/unread messages.

Creates action files in Needs_Action folder for Claude Code to process.

Setup Requirements:
1. Enable Gmail API: https://developers.google.com/gmail/api/quickstart/python
2. Download credentials.json and place in vault root
3. Run once to authorize: python gmail_watcher.py --auth
4. Token file will be saved as token.json

Usage:
    python gmail_watcher.py /path/to/vault
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Gmail API imports (optional - graceful fallback if not installed)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """Watcher for Gmail - monitors unread/important messages."""
    
    # Scopes for Gmail API
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(
        self, 
        vault_path: str, 
        credentials_path: Optional[str] = None,
        check_interval: int = 120,
        max_results: int = 10
    ):
        """
        Initialize Gmail Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to credentials.json (default: vault/credentials.json)
            check_interval: Seconds between checks (default: 120)
            max_results: Max messages to fetch per check (default: 10)
        """
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path) if credentials_path else self.vault_path / 'credentials.json'
        self.token_path = self.vault_path / 'token.json'
        self.max_results = max_results
        
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        if not GMAIL_AVAILABLE:
            self.logger.error("Gmail API not available")
            return False
        
        if not self.credentials_path.exists():
            self.logger.error(f"Credentials file not found: {self.credentials_path}")
            self.logger.info("Please download credentials.json from Google Cloud Console")
            return False
        
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                self.logger.warning(f"Could not load token: {e}")
                creds = None
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    self.logger.warning("Token expired, re-authentication required")
                    self.token_path.unlink(missing_ok=True)
                    return False
            else:
                self.logger.error("No valid credentials. Run with --auth flag to authorize.")
                return False
        
        # Build service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Gmail authentication successful")
            return True
        except Exception as e:
            self.logger.error(f"Could not build Gmail service: {e}")
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread/important Gmail messages.
        
        Returns:
            List of message dictionaries
        """
        if not self.service:
            return []
        
        try:
            # Search for unread messages (optionally filter by important)
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=self.max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            # Try to re-authenticate
            self._authenticate()
            return []
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        """
        Create action file for a Gmail message.
        
        Args:
            message: Gmail message dict with 'id' key
            
        Returns:
            Path to created file
        """
        try:
            # Fetch full message
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            payload = msg.get('payload', {})
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}
            
            # Extract body
            body = self._extract_body(payload)
            
            # Determine priority
            priority = 'high' if headers.get('importance', '').lower() == 'high' else 'normal'
            
            # Create content
            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', datetime.now().isoformat())
            
            content = f'''---
type: email
from: {from_email}
subject: {subject}
received: {datetime.now().isoformat()}
message_date: {date}
priority: {priority}
status: pending
gmail_id: {message['id']}
---

# Email: {subject}

**From:** {from_email}  
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Priority:** {priority}

## Content

{body}

## Suggested Actions

- [ ] Read and understand the email
- [ ] Reply to sender (requires approval for new contacts)
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Create follow-up task if needed

## Notes

*Add your notes here*

---
*Created by Gmail Watcher*
'''
            
            # Create filename
            safe_subject = self._sanitize_filename(subject[:50])
            filename = f"EMAIL_{message['id']}_{safe_subject}.md"
            
            filepath = self._create_markdown_file(filename, content)
            
            # Log processed ID
            self._save_processed_id(message['id'])
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract plain text body from message payload."""
        # Try plain text first
        if payload.get('mimeType', '').startswith('text/plain'):
            body = payload.get('body', {}).get('data', '')
            if body:
                import base64
                return base64.urlsafe_b64decode(body).decode('utf-8', errors='replace')
        
        # Try parts (multipart messages)
        parts = payload.get('parts', [])
        for part in parts:
            if part.get('mimeType', '').startswith('text/plain'):
                body = part.get('body', {}).get('data', '')
                if body:
                    import base64
                    return base64.urlsafe_b64decode(body).decode('utf-8', errors='replace')
        
        # Fallback to snippet
        return payload.get('body', {}).get('data', '')
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        # Remove/replace invalid characters
        invalid = '<>:"/\\|？*'
        for char in invalid:
            text = text.replace(char, '_')
        return text.strip()[:50]


def auth_flow(vault_path: str):
    """Run OAuth authorization flow for Gmail API."""
    if not GMAIL_AVAILABLE:
        print("Gmail API not installed. Install with:")
        print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return
    
    vault = Path(vault_path)
    credentials_path = vault / 'credentials.json'
    token_path = vault / 'token.json'
    
    if not credentials_path.exists():
        print(f"Error: credentials.json not found in {vault_path}")
        print("\nSetup instructions:")
        print("1. Go to: https://developers.google.com/gmail/api/quickstart/python")
        print("2. Click 'Enable the Gmail API'")
        print("3. Download credentials.json")
        print("4. Place it in your vault folder")
        return
    
    print("Starting Gmail OAuth authorization...")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        GmailWatcher.SCOPES
    )
    
    creds = flow.run_local_server(port=0)
    
    # Save credentials
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    
    print(f"Authorization successful! Token saved to: {token_path}")
    print("You can now run the Gmail watcher.")


def main():
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--auth', action='store_true', help='Run OAuth authorization')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')
    parser.add_argument('--max-results', type=int, default=10, help='Max messages per check')
    
    args = parser.parse_args()
    
    if args.auth:
        auth_flow(args.vault_path)
        return
    
    watcher = GmailWatcher(
        vault_path=args.vault_path,
        check_interval=args.interval,
        max_results=args.max_results
    )
    
    if watcher.service:
        watcher.run()
    else:
        print("Failed to initialize Gmail watcher. Run with --auth flag first.")
        sys.exit(1)


if __name__ == '__main__':
    main()
