#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create WhatsApp Session - First-time setup for WhatsApp Watcher.

Opens a browser where you scan the QR code with your WhatsApp app.
Session is saved for future use by the watcher.

Usage:
    python create-whatsapp-session.py /path/to/vault
"""

import sys
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def create_session(session_path: Path, timeout: int = 60):
    """
    Create a WhatsApp Web session.
    
    Args:
        session_path: Path to save session data
        timeout: Seconds to wait for QR code scan
    """
    print("Starting WhatsApp session creator...")
    print(f"Session will be saved to: {session_path}")
    print("")
    print("Instructions:")
    print("1. A browser window will open with WhatsApp Web")
    print("2. Open WhatsApp on your phone")
    print("3. Go to Settings > Linked Devices > Link a Device")
    print("4. Scan the QR code")
    print("5. Wait for chat list to load, then close the browser")
    print("")
    input("Press Enter to continue...")
    
    with sync_playwright() as p:
        # Launch browser with persistent context
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,  # Show browser for QR code scanning
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        page = browser.pages[0]
        
        print("Navigating to WhatsApp Web...")
        page.goto('https://web.whatsapp.com', wait_until='networkidle')
        
        print("Waiting for you to scan the QR code...")
        
        try:
            # Wait for chat list to appear (means logged in)
            page.wait_for_selector('[data-testid="chat-list"]', timeout=timeout * 1000)
            print("\n✓ Successfully logged in!")
            print("Session saved. You can close the browser.")
        except PlaywrightTimeout:
            print("\n✗ Timeout: QR code not scanned in time")
            print("Please run the script again")
        
        # Keep browser open until user closes it
        print("\nClose the browser window when done...")
        try:
            page.wait_for_event('close', timeout=300000)  # 5 min max
        except PlaywrightTimeout:
            pass
        
        browser.close()
        print("Session creator finished")


def main():
    parser = argparse.ArgumentParser(description='Create WhatsApp Web session')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--session-path', help='Custom session path (default: vault/whatsapp-session)')
    parser.add_argument('--timeout', type=int, default=60, help='QR code scan timeout in seconds')
    
    args = parser.parse_args()
    
    vault = Path(args.vault_path)
    session_path = Path(args.session_path) if args.session_path else vault / 'whatsapp-session'
    
    # Create session directory
    session_path.mkdir(parents=True, exist_ok=True)
    
    create_session(session_path, args.timeout)


if __name__ == '__main__':
    main()
