#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new important/unread messages.

Creates action files in Needs_Action folder for Qwen Code to process.

Setup:
1. Make sure credentials.json is in vault root
2. Run authorization: python authorize_gmail.py credentials.json
3. Run watcher: python gmail_watcher.py /path/to/vault

Usage:
    python gmail_watcher.py /path/to/vault --interval 120
"""

import os
import sys
import argparse
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API not installed. Install with:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """Watcher for Gmail - monitors unread/important messages."""
    
    # Scopes for Gmail API
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(
        self, 
        vault_path: str, 
        check_interval: int = 120,
        max_results: int = 10,
        dry_run: bool = False
    ):
        """
        Initialize Gmail Watcher.
        
        Args:
            vault_path: Path to Obsidian vault (should contain credentials.json)
            check_interval: Seconds between checks (default: 120)
            max_results: Max messages to fetch per check (default: 10)
            dry_run: If True, log but don't create files
        """
        super().__init__(vault_path, check_interval)
        
        self.vault_path = Path(vault_path)
        self.credentials_path = self.vault_path / 'credentials.json'
        self.token_path = self.vault_path / 'token.json'
        self.max_results = max_results
        self.dry_run = dry_run
        
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        if not GMAIL_AVAILABLE:
            self.logger.error("Gmail API not available")
            return False
        
        if not self.credentials_path.exists():
            self.logger.error(f"Credentials file not found: {self.credentials_path}")
            self.logger.info("Run: python authorize_gmail.py credentials.json")
            return False
        
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
                self.logger.info("Loaded existing token")
            except Exception as e:
                self.logger.warning(f"Could not load token: {e}")
                creds = None
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("Refreshed expired token")
                except RefreshError:
                    self.logger.warning("Token expired, re-authorization required")
                    self.logger.info("Run: python authorize_gmail.py credentials.json")
                    return False
            else:
                self.logger.error("No valid credentials.")
                self.logger.info("Run: python authorize_gmail.py credentials.json")
                return False
        
        # Build service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            
            # Test connection
            profile = self.service.users().getProfile().execute()
            self.logger.info(f"Connected to: {profile['emailAddress']}")
            return True
        except Exception as e:
            self.logger.error(f"Could not build Gmail service: {e}")
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for new unread Gmail messages."""
        if not self.service:
            return []
        
        try:
            # Search for unread messages
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
        """Create action file for a Gmail message."""
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
            body = self._extract_body(payload, msg)
            
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
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would create: {filename}")
                return None
            
            filepath = self._create_markdown_file(filename, content)
            
            # Log processed ID
            self._save_processed_id(message['id'])
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def _extract_body(self, payload: Dict, msg: Dict) -> str:
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
        return msg.get('snippet', 'No content available')
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        invalid = '<>:"/\\|？*'
        for char in invalid:
            text = text.replace(char, '_')
        return text.strip()[:50]
    
    def run(self):
        """Run the watcher with periodic checks."""
        self.logger.info(f"Starting Gmail Watcher")
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval}s")
        self.logger.info(f"Max results: {self.max_results}")
        
        if self.dry_run:
            self.logger.info("DRY RUN MODE - No files will be created")
        
        if not self.service:
            self.logger.error("Gmail service not available. Run authorization first.")
            return
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f"Found {len(items)} new message(s)")
                        for item in items:
                            try:
                                self.create_action_file(item)
                            except Exception as e:
                                self.logger.error(f"Error creating action file: {e}")
                    else:
                        self.logger.debug("No new messages")
                    
                except Exception as e:
                    self.logger.error(f"Error in check loop: {e}")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Gmail Watcher stopped by user")


def main():
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')
    parser.add_argument('--max-results', type=int, default=10, help='Max messages per check')
    parser.add_argument('--dry-run', action='store_true', help='Log but don\'t create files')
    
    args = parser.parse_args()
    
    watcher = GmailWatcher(
        vault_path=args.vault_path,
        check_interval=args.interval,
        max_results=args.max_results,
        dry_run=args.dry_run
    )
    
    if watcher.service:
        watcher.run()
    else:
        print("\nGmail Watcher not started. Please run authorization first:")
        print(f"  python authorize_gmail.py {args.vault_path}/credentials.json")
        sys.exit(1)


if __name__ == '__main__':
    main()
