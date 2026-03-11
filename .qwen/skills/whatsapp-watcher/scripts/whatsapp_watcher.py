#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Monitors WhatsApp Web for urgent messages.

Creates action files in Needs_Action folder for messages containing
urgent keywords like "invoice", "payment", "urgent", etc.

Usage:
    python whatsapp_watcher.py /path/to/vault --interval 60
"""

import sys
import argparse
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory for base_watcher import
sys.path.insert(0, str(Path(__file__).parent.parent.parent) + '/AI_Employee_Vault/scripts')

from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Install with: pip install playwright")
    print("Then run: playwright install chromium")


class WhatsAppWatcher(BaseWatcher):
    """Watcher for WhatsApp Web - monitors for urgent messages."""
    
    # Default keywords that indicate urgent messages
    DEFAULT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'quote']
    
    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        check_interval: int = 60,
        keywords: Optional[List[str]] = None,
        dry_run: bool = False
    ):
        """
        Initialize WhatsApp Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to WhatsApp session folder
            check_interval: Seconds between checks (default: 60)
            keywords: List of urgent keywords to detect
            dry_run: If True, log but don't create files
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else self.vault_path / 'whatsapp-session'
        self.keywords = keywords if keywords else self.DEFAULT_KEYWORDS
        self.dry_run = dry_run
        
        # Track processed message IDs
        self.processed_messages: set = set()
        
        # Load previously processed messages
        self._load_processed_messages()
        
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available")
        
        if not self.session_path.exists():
            self.logger.warning(f"Session path not found: {self.session_path}")
            self.logger.info("Run: python scripts/create-whatsapp-session.py /path/to/vault")
    
    def _load_processed_messages(self):
        """Load processed message IDs from log file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}_whatsapp.json'
        
        if log_file.exists():
            import json
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    self.processed_messages = set(data.get('processed', []))
                    self.logger.info(f"Loaded {len(self.processed_messages)} processed messages")
            except Exception as e:
                self.logger.warning(f"Could not load processed messages: {e}")
    
    def _save_processed_message(self, message_id: str):
        """Save a processed message ID."""
        import json
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}_whatsapp.json'
        
        self.processed_messages.add(message_id)
        
        try:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {'processed': []}
            
            data['processed'] = list(self.processed_messages)
            
            with open(log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save processed message: {e}")
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new urgent messages.
        
        Returns:
            List of message dictionaries
        """
        if not PLAYWRIGHT_AVAILABLE:
            return []
        
        if not self.session_path.exists():
            self.logger.warning("WhatsApp session not found")
            return []
        
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with saved session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to WhatsApp Web
                page.goto('https://web.whatsapp.com', wait_until='networkidle')
                
                try:
                    # Wait for chat list
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                except PlaywrightTimeout:
                    self.logger.warning("WhatsApp Web not loaded properly")
                    browser.close()
                    return []
                
                # Find all chat items with unread messages
                try:
                    chat_elements = page.query_selector_all('[aria-label*="unread"]')
                    
                    for chat in chat_elements:
                        try:
                            # Extract chat info
                            chat_text = chat.inner_text()
                            
                            # Check if contains urgent keywords
                            chat_text_lower = chat_text.lower()
                            found_keywords = [kw for kw in self.keywords if kw in chat_text_lower]
                            
                            if found_keywords:
                                # Extract contact name and message
                                contact = self._extract_contact(chat)
                                message_text = self._extract_message(chat)
                                timestamp = datetime.now().isoformat()
                                
                                # Create unique message ID
                                message_id = f"{contact}_{timestamp[:10]}_{hash(message_text) % 10000}"
                                
                                if message_id not in self.processed_messages:
                                    messages.append({
                                        'id': message_id,
                                        'contact': contact,
                                        'message': message_text,
                                        'keywords': found_keywords,
                                        'timestamp': timestamp
                                    })
                        except Exception as e:
                            self.logger.debug(f"Error processing chat: {e}")
                            continue
                    
                except Exception as e:
                    self.logger.error(f"Error finding unread messages: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
        
        return messages
    
    def _extract_contact(self, chat) -> str:
        """Extract contact name from chat element."""
        try:
            # Try to get contact name from aria-label or selector
            aria_label = chat.get_attribute('aria-label')
            if aria_label:
                # Extract name from aria-label
                return aria_label.split(',')[0].replace('unread', '').strip()
        except:
            pass
        return "Unknown Contact"
    
    def _extract_message(self, chat) -> str:
        """Extract last message text from chat element."""
        try:
            # Try various selectors for message text
            selectors = [
                '[data-testid="chat-cell-message-text"]',
                'span[dir="auto"]',
                '.message-text'
            ]
            
            for selector in selectors:
                element = chat.query_selector(selector)
                if element:
                    return element.inner_text().strip()
        except:
            pass
        
        # Fallback to full chat text
        return chat.inner_text()[:200]
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        """
        Create action file for a WhatsApp message.
        
        Args:
            message: Message dictionary
            
        Returns:
            Path to created file
        """
        try:
            content = f'''---
type: whatsapp
from: {message['contact']}
received: {message['timestamp']}
priority: high
status: pending
keywords: {','.join(message['keywords'])}
whatsapp_id: {message['id']}
---

# WhatsApp Message

**From:** {message['contact']}  
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Priority:** High (urgent keywords detected)  
**Keywords:** {', '.join(message['keywords'])}

## Message Content

{message['message']}

## Suggested Actions

- [ ] Read and understand the message
- [ ] Reply to sender (requires approval for new contacts)
- [ ] Take necessary action based on keywords
- [ ] Archive after processing

## Notes

*Add your notes here*

---
*Created by WhatsApp Watcher*
'''
            
            # Create filename
            safe_contact = self._sanitize_filename(message['contact'][:30])
            filename = f"WHATSAPP_{safe_contact}_{message['id'][-6:]}.md"
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would create: {filename}")
                return None
            
            filepath = self._create_markdown_file(filename, content)
            
            # Log processed message
            self._save_processed_message(message['id'])
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        invalid = '<>:"/\\|？*'
        for char in invalid:
            text = text.replace(char, '_')
        return text.strip()
    
    def run(self):
        """Run the watcher with periodic checks."""
        self.logger.info(f"Starting WhatsApp Watcher")
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Session: {self.session_path}")
        self.logger.info(f"Keywords: {', '.join(self.keywords)}")
        self.logger.info(f"Interval: {self.check_interval}s")
        
        if self.dry_run:
            self.logger.info("DRY RUN MODE - No files will be created")
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f"Found {len(items)} urgent message(s)")
                        for item in items:
                            try:
                                self.create_action_file(item)
                            except Exception as e:
                                self.logger.error(f"Error creating action file: {e}")
                    else:
                        self.logger.debug("No new urgent messages")
                    
                except Exception as e:
                    self.logger.error(f"Error in check loop: {e}")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("WhatsApp Watcher stopped by user")


def main():
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--keywords', help='Comma-separated list of urgent keywords')
    parser.add_argument('--session-path', help='Custom session path')
    parser.add_argument('--dry-run', action='store_true', help='Log but don\'t create files')
    
    args = parser.parse_args()
    
    keywords = args.keywords.split(',') if args.keywords else None
    
    watcher = WhatsAppWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path,
        check_interval=args.interval,
        keywords=keywords,
        dry_run=args.dry_run
    )
    
    watcher.run()


if __name__ == '__main__':
    main()
