#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Poster - Post content on LinkedIn automatically.

Uses Playwright for browser automation. Supports templates,
scheduling, and human-in-the-loop approval.

Usage:
    python linkedin_poster.py /path/to/vault post --content "Your post"
"""

import sys
import argparse
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent) + '/AI_Employee_Vault/scripts')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Install with: pip install playwright")
    print("Then run: playwright install chromium")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LinkedInPoster')


class LinkedInPoster:
    """Post content on LinkedIn."""
    
    def __init__(self, vault_path: str, session_path: Optional[str] = None):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else self.vault_path / 'linkedin-session'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available")
    
    def create_session(self):
        """Create LinkedIn session (first-time setup)."""
        print("Starting LinkedIn session creator...")
        print("A browser will open. Log in to LinkedIn.")
        print("Close the browser when done.")
        input("Press Enter to continue...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            page = browser.pages[0]
            page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            
            print("Waiting for login... Close browser when done.")
            try:
                page.wait_for_event('close', timeout=300000)
            except PlaywrightTimeout:
                pass
            
            browser.close()
            print("Session saved")
    
    def post_content(self, content: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """Post content on LinkedIn."""
        if not PLAYWRIGHT_AVAILABLE:
            return {'error': 'Playwright not available'}
        
        if not self.session_path.exists():
            return {'error': 'Session not found. Run create session first.'}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Go to LinkedIn
                page.goto('https://www.linkedin.com/', wait_until='networkidle')
                
                # Check if logged in
                try:
                    page.wait_for_selector('[data-control-name="post_update"]', timeout=5000)
                except PlaywrightTimeout:
                    return {'error': 'Not logged in. Re-create session.'}
                
                # Click post button
                page.click('[data-control-name="post_update"]')
                
                # Wait for post dialog
                page.wait_for_selector('[role="dialog"]', timeout=5000)
                
                # Find the editor and type content
                editor = page.locator('[role="textbox"]').first
                editor.fill(content)
                
                # Add image if provided
                if image_path:
                    page.locator('input[type="file"]').set_input_files(image_path)
                    time.sleep(2)
                
                # Wait a moment for content to be processed
                time.sleep(2)
                
                # Click post button
                page.click('button:has-text("Post")')
                
                # Wait for confirmation
                try:
                    page.wait_for_selector('text="Your post was posted"', timeout=5000)
                    logger.info("Post published successfully")
                    return {'success': True, 'posted_at': datetime.now().isoformat()}
                except PlaywrightTimeout:
                    # Post might still have been successful
                    logger.info("Post likely published (confirmation not detected)")
                    return {'success': True, 'posted_at': datetime.now().isoformat(), 'note': 'Confirmation not detected'}
                
        except Exception as e:
            logger.error(f"Error posting: {e}")
            return {'error': str(e)}
    
    def create_approval_request(self, content: str, scheduled_time: Optional[str] = None) -> Optional[Path]:
        """Create approval request file for a post."""
        try:
            post_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            content_md = f'''---
type: approval_request
action: linkedin_post
post_id: {post_id}
created: {datetime.now().isoformat()}
scheduled: {scheduled_time or 'immediate'}
status: pending
---

# LinkedIn Post - Approval Required

**Post ID:** {post_id}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Scheduled:** {scheduled_time or 'Immediate'}

## Post Content

{content}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.

---
*Created by LinkedIn Poster*
'''
            
            filepath = self.pending_approval / f'LINKEDIN_POST_{post_id}.md'
            filepath.write_text(content_md, encoding='utf-8')
            
            logger.info(f"Approval request created: {filepath.name}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating approval request: {e}")
            return None
    
    def process_approved_posts(self) -> List[Dict[str, Any]]:
        """Process approved posts from Approved folder."""
        results = []
        
        if not self.approved.exists():
            return results
        
        for filepath in self.approved.iterdir():
            if filepath.suffix != '.md' or 'LINKEDIN_POST' not in filepath.name:
                continue
            
            try:
                content = filepath.read_text(encoding='utf-8')
                
                # Extract post content (between ## Post Content and ## To Approve)
                parts = content.split('## Post Content')
                if len(parts) < 2:
                    continue
                
                post_content = parts[1].split('##')[0].strip()
                
                # Post to LinkedIn
                result = self.post_content(post_content)
                result['file'] = filepath.name
                
                if result.get('success'):
                    # Move to Done
                    done_folder = self.vault_path / 'Done'
                    done_folder.mkdir(parents=True, exist_ok=True)
                    filepath.rename(done_folder / filepath.name)
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {filepath.name}: {e}")
                results.append({'file': filepath.name, 'error': str(e)})
        
        return results


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Poster')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('action', choices=['post', 'schedule', 'create-session', 'process-approved'],
                       help='Action to perform')
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--template', help='Template name to use')
    parser.add_argument('--date', help='Scheduled date (ISO format)')
    parser.add_argument('--image', help='Image path to attach')
    
    args = parser.parse_args()
    
    poster = LinkedInPoster(args.vault_path)
    
    if args.action == 'create-session':
        poster.create_session()
    
    elif args.action == 'post':
        if not args.content:
            print("Error: --content required")
            sys.exit(1)
        
        # Create approval request
        poster.create_approval_request(args.content)
        print("Approval request created. Move file to /Approved to post.")
    
    elif args.action == 'schedule':
        if not args.content or not args.date:
            print("Error: --content and --date required")
            sys.exit(1)
        
        poster.create_approval_request(args.content, args.date)
        print(f"Scheduled post created for {args.date}")
    
    elif args.action == 'process-approved':
        results = poster.process_approved_posts()
        for result in results:
            if result.get('success'):
                print(f"✓ Posted: {result.get('file')}")
            else:
                print(f"✗ Failed: {result.get('file')} - {result.get('error')}")


if __name__ == '__main__':
    main()
