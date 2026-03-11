#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher - Monitors LinkedIn for new notifications and messages.

Uses Playwright for browser automation. Creates action files in
Needs_Action folder for Qwen Code to process.

Setup:
1. Install Playwright: pip install playwright
2. Install browsers: playwright install chromium
3. Create session: python create_linkedin_session.py
4. Run watcher: python linkedin_watcher.py /path/to/vault

Usage:
    python linkedin_watcher.py /path/to/vault --interval 300
"""

import sys
import argparse
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory for base_watcher import
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")


class LinkedInWatcher(BaseWatcher):
    """Watcher for LinkedIn - monitors notifications and messages."""
    
    # Keywords that indicate important LinkedIn activity
    DEFAULT_KEYWORDS = [
        'message', 'connection', 'job', 'post', 'comment',
        'like', 'share', 'follower', 'opportunity', 'hiring'
    ]
    
    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        check_interval: int = 300,
        keywords: Optional[List[str]] = None,
        dry_run: bool = False
    ):
        """
        Initialize LinkedIn Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to LinkedIn session folder
            check_interval: Seconds between checks (default: 300)
            keywords: List of keywords to detect
            dry_run: If True, log but don't create files
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else self.vault_path / 'linkedin-session'
        self.keywords = keywords if keywords else self.DEFAULT_KEYWORDS
        self.dry_run = dry_run
        
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available")
        
        if not self.session_path.exists():
            self.logger.warning(f"Session path not found: {self.session_path}")
            self.logger.info("Run: python create_linkedin_session.py")
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check LinkedIn for new notifications."""
        if not PLAYWRIGHT_AVAILABLE:
            return []
        
        if not self.session_path.exists():
            self.logger.warning("LinkedIn session not found")
            return []
        
        notifications = []
        
        try:
            with sync_playwright() as p:
                # Try Chrome channel first (more trusted by LinkedIn)
                try:
                    browser = p.chromium.launch_persistent_context(
                        str(self.session_path),
                        headless=True,
                        channel='chrome',  # Use installed Chrome
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--no-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-features=IsolateOrigins,site-per-process'
                        ]
                    )
                except Exception as e:
                    self.logger.debug(f"Chrome channel not available, using Chromium: {e}")
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
                
                # Navigate to LinkedIn notifications with longer timeout
                self.logger.debug("Navigating to LinkedIn...")
                page.goto('https://www.linkedin.com/notifications/', wait_until='domcontentloaded', timeout=30000)
                
                # Wait a bit for page to load
                time.sleep(3)
                
                try:
                    # Find notification items
                    notification_elements = page.query_selector_all(
                        '[data-test-notification-item]'
                    )
                    
                    self.logger.info(f"Found {len(notification_elements)} notification elements")
                    
                    for notif in notification_elements[:10]:  # Limit to 10
                        try:
                            # Extract notification data
                            notif_type = self._extract_type(notif)
                            actor = self._extract_actor(notif)
                            text = self._extract_text(notif)
                            timestamp = datetime.now().isoformat()
                            
                            # Check if contains our keywords
                            text_lower = text.lower()
                            found_keywords = [kw for kw in self.keywords if kw in text_lower]
                            
                            if found_keywords:
                                # Create unique ID
                                notif_id = f"{notif_type}_{hash(text) % 10000}"
                                
                                if notif_id not in self.processed_ids:
                                    notifications.append({
                                        'id': notif_id,
                                        'type': notif_type,
                                        'actor': actor,
                                        'text': text,
                                        'keywords': found_keywords,
                                        'timestamp': timestamp
                                    })
                        except Exception as e:
                            self.logger.debug(f"Error processing notification: {e}")
                            continue
                    
                except Exception as e:
                    self.logger.error(f"Error finding notifications: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking LinkedIn: {e}")
        
        return notifications
    
    def _extract_type(self, element) -> str:
        """Extract notification type."""
        try:
            # Try to get type from attribute or text
            notif_type = element.get_attribute('data-test-notification-type')
            if notif_type:
                return notif_type
            
            # Fallback to class name
            class_name = element.get_attribute('class')
            if 'message' in class_name.lower():
                return 'message'
            elif 'connection' in class_name.lower():
                return 'connection'
        except:
            pass
        return 'unknown'
    
    def _extract_actor(self, element) -> str:
        """Extract the person/entity who triggered the notification."""
        try:
            # Look for actor name in the element
            actor_elem = element.query_selector('[data-test-actor-name]')
            if actor_elem:
                return actor_elem.inner_text().strip()
            
            # Fallback to any link text
            links = element.query_selector_all('a')
            if links:
                return links[0].inner_text().strip()[:50]
        except:
            pass
        return "Unknown"
    
    def _extract_text(self, element) -> str:
        """Extract notification text."""
        try:
            text_elem = element.query_selector('[data-test-notification-content]')
            if text_elem:
                return text_elem.inner_text().strip()[:200]
            
            # Fallback to full text
            return element.inner_text().strip()[:200]
        except:
            return "No content available"
    
    def create_action_file(self, notification: Dict[str, Any]) -> Optional[Path]:
        """Create action file for a LinkedIn notification."""
        try:
            content = f'''---
type: linkedin
notification_type: {notification['type']}
from: {notification['actor']}
received: {notification['timestamp']}
priority: normal
status: pending
keywords: {','.join(notification['keywords'])}
linkedin_id: {notification['id']}
---

# LinkedIn Notification

**Type:** {notification['type']}  
**From:** {notification['actor']}  
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Keywords:** {', '.join(notification['keywords'])}

## Notification Content

{notification['text']}

## Suggested Actions

- [ ] Review the notification
- [ ] Respond if appropriate (connection request, message)
- [ ] Engage with post (like, comment, share)
- [ ] Archive after processing

## Notes

*Add your notes here*

---
*Created by LinkedIn Watcher*
'''
            
            # Create filename
            safe_type = self._sanitize_filename(notification['type'])
            safe_actor = self._sanitize_filename(notification['actor'][:20])
            filename = f"LINKEDIN_{safe_type}_{safe_actor}_{notification['id'][-6:]}.md"
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would create: {filename}")
                return None
            
            filepath = self._create_markdown_file(filename, content)
            
            # Log processed notification
            self._save_processed_id(notification['id'])
            
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
        self.logger.info(f"Starting LinkedIn Watcher")
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
                        self.logger.info(f"Found {len(items)} new notification(s)")
                        for item in items:
                            try:
                                self.create_action_file(item)
                            except Exception as e:
                                self.logger.error(f"Error creating action file: {e}")
                    else:
                        self.logger.debug("No new notifications")
                    
                except Exception as e:
                    self.logger.error(f"Error in check loop: {e}")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("LinkedIn Watcher stopped by user")


def create_session(session_path: Path):
    """Create LinkedIn session (first-time setup)."""
    print("=" * 60)
    print("LinkedIn Session Creator")
    print("=" * 60)
    print()
    print("A browser window will open. Log in to LinkedIn.")
    print("Navigate to your feed and wait for it to fully load.")
    print("Then close the browser window.")
    print()
    print("NOTE: If you get a security error, try:")
    print("  1. Update Playwright: pip install --upgrade playwright")
    print("  2. Update browsers: playwright install chrome")
    print()
    input("Press Enter to continue...")
    
    if not PLAYWRIGHT_AVAILABLE:
        print("Playwright not installed. Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return
    
    with sync_playwright() as p:
        # Try Chrome first (more trusted by LinkedIn), fallback to Chromium
        try:
            browser = p.chromium.launch_persistent_context(
                str(session_path),
                headless=False,
                channel='chrome',  # Use installed Chrome
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-extensions',
                    '--disable-background-networking',
                    '--disable-sync',
                    '--disable-translate',
                    '--metrics-recording-only',
                    '--no-first-run',
                    '--safebrowsing-disable-auto-update',
                ]
            )
        except Exception as e:
            print(f"Chrome not found, using Chromium: {e}")
            browser = p.chromium.launch_persistent_context(
                str(session_path),
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
        
        page = browser.pages[0]
        page.goto('https://www.linkedin.com/login', wait_until='networkidle')
        
        print("Waiting for login... Close browser when done.")
        try:
            page.wait_for_event('close', timeout=300000)
        except PlaywrightTimeout:
            pass
        except Exception:
            pass  # Browser may have been closed manually
        
        # Try to close browser (may already be closed)
        try:
            browser.close()
            print("Session saved")
        except Exception:
            print("Session saved (browser was already closed)")


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--keywords', help='Comma-separated list of keywords')
    parser.add_argument('--session-path', help='Custom session path')
    parser.add_argument('--dry-run', action='store_true', help='Log but don\'t create files')
    parser.add_argument('--create-session', action='store_true', help='Create new LinkedIn session')
    
    args = parser.parse_args()
    
    vault = Path(args.vault_path)
    session_path = Path(args.session_path) if args.session_path else vault / 'linkedin-session'
    
    if args.create_session:
        session_path.mkdir(parents=True, exist_ok=True)
        create_session(session_path)
        return
    
    keywords = args.keywords.split(',') if args.keywords else None
    
    watcher = LinkedInWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path,
        check_interval=args.interval,
        keywords=keywords,
        dry_run=args.dry_run
    )
    
    if watcher.session_path.exists():
        watcher.run()
    else:
        print("\nLinkedIn session not found. Create one first:")
        print(f"  python linkedin_watcher.py {args.vault_path} --create-session")
        sys.exit(1)


if __name__ == '__main__':
    main()
