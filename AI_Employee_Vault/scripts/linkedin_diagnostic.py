#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Session Diagnostic - Check if LinkedIn session is valid.

Usage:
    python linkedin_diagnostic.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

session_path = Path(__file__).parent.parent / 'linkedin-session'

print("=" * 60)
print("LinkedIn Session Diagnostic")
print("=" * 60)
print()

if not session_path.exists():
    print(f"ERROR: Session folder not found: {session_path}")
    print("Run: python linkedin_watcher.py .. --create-session")
    sys.exit(1)

print(f"Session folder: {session_path}")
print(f"Session folder exists: {session_path.exists()}")
print()

with sync_playwright() as p:
    print("Launching browser with saved session...")
    
    try:
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,  # Show browser so you can see what's happening
            channel='chrome',
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )
        print("Browser launched")
    except Exception as e:
        print(f"Chrome channel failed: {e}")
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,
            args=['--no-sandbox']
        )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("Navigating to LinkedIn...")
    print("(Watch the browser window)")
    print()
    
    try:
        page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
        print(f"Page loaded!")
        
        # Wait for page to stabilize
        import time
        time.sleep(2)
        
        print(f"Title: {page.title()}")
        print(f"URL: {page.url}")
        print()
        
        # Check if logged in by looking for feed elements
        is_logged_in = False
        
        # Check for feed content (only visible when logged in)
        feed_selector = '[data-test-fed-update]'
        try:
            feed_elements = page.query_selector_all(feed_selector)
            if len(feed_elements) > 0:
                is_logged_in = True
                print(f"[OK] Found {len(feed_elements)} feed items - LOGGED IN")
        except:
            pass
        
        # Check for login button (visible when NOT logged in)
        if not is_logged_in:
            login_selector = 'button[type="submit"]'
            try:
                login_buttons = page.query_selector_all(login_selector)
                if len(login_buttons) > 0:
                    print("[ERROR] Login form detected - NOT LOGGED IN")
                    print()
                    print("The session has expired or is invalid.")
                    print("Please log in manually in the browser window.")
                    print("After logging in and seeing your feed, close the browser.")
                    
                    # Wait for user to log in
                    try:
                        page.wait_for_event('close', timeout=120000)
                    except:
                        pass
                    browser.close()
                    sys.exit(0)
            except:
                pass
        
        # If logged in, check notifications
        if is_logged_in or 'feed' in page.url:
            print("[OK] Session appears valid")
            print()
            
            # Navigate to notifications
            print("Checking notifications...")
            page.goto('https://www.linkedin.com/notifications/', wait_until='domcontentloaded')
            time.sleep(3)
            
            # Take screenshot for debugging
            page.screenshot(path='linkedin-debug.png')
            print("Screenshot saved to: linkedin-debug.png")
            
            # Try different selectors
            selectors_to_try = [
                '[data-test-notification-item]',
                '.notification-item',
                '[class*="notification"]',
                'ul[aria-label="Notifications"] li'
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = page.query_selector_all(selector)
                    if len(elements) > 0:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        break
                except:
                    continue
            else:
                print("No notification elements found with any selector")
                print()
                print("This could mean:")
                print("  1. No new notifications")
                print("  2. LinkedIn changed their HTML structure")
                print("  3. Session needs re-authentication")
        
    except PlaywrightTimeout:
        print("[ERROR] Page load timeout (30 seconds)")
        print("LinkedIn may be blocking the connection")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    print()
    print("Close the browser window when done...")
    try:
        page.wait_for_event('close', timeout=60000)
    except:
        pass  # User closed browser or timeout
    
    # Try to close browser (may already be closed)
    try:
        browser.close()
        print("Diagnostic complete")
    except:
        print("Diagnostic complete (browser was already closed)")
