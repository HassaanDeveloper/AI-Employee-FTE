#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail API Authorization - First-time setup for Gmail Watcher.

This script will:
1. Open a browser window
2. Ask you to log in to your Google account
3. Request permission to read and send emails
4. Save the token for future use

Usage:
    python authorize_gmail.py /path/to/credentials.json
"""

import sys
import os
from pathlib import Path

# Suppress warnings
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
except ImportError:
    print("Gmail API libraries not installed.")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)


# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


def authorize(credentials_path: str, token_path: str = 'token.json'):
    """
    Run OAuth authorization flow for Gmail API.
    
    Args:
        credentials_path: Path to credentials.json from Google Cloud Console
        token_path: Path to save the authorization token
    """
    credentials_path = Path(credentials_path)
    token_path = Path(token_path)
    
    if not credentials_path.exists():
        print(f"Error: credentials.json not found at {credentials_path}")
        print("\nSetup instructions:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        return False
    
    print("=" * 60)
    print("Gmail API Authorization")
    print("=" * 60)
    print()
    print("A browser window will open for authorization.")
    print("Log in with your Google account and grant permissions.")
    print("Close the browser when done.")
    print()
    
    creds = None
    
    # Try to load existing token
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            if creds and creds.valid:
                print("[OK] Valid token already exists!")
                # Test the connection
                try:
                    service = build('gmail', 'v1', credentials=creds)
                    profile = service.users().getProfile().execute()
                    print(f"Connected to: {profile['emailAddress']}")
                    return True
                except Exception as e:
                    print(f"Existing token invalid: {e}")
                    creds = None
        except Exception as e:
            print(f"Could not load existing token: {e}")
            creds = None
    
    # If no valid credentials, get new ones
    if not creds:
        print("Starting OAuth flow...")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES
        )
        creds = flow.run_local_server(port=0, open_browser=True)
    
    # Save the credentials
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    
    print()
    print("=" * 60)
    print("Authorization successful!")
    print("=" * 60)
    print()
    print(f"Token saved to: {token_path}")
    print()
    
    # Test the connection
    print("Testing Gmail connection...")
    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile().execute()
        print(f"Connected to: {profile['emailAddress']}")
        print()
        print("You can now run the Gmail Watcher:")
        print(f"  python gmail_watcher.py {credentials_path.parent}")
    except Exception as e:
        print(f"Connection test failed: {e}")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python authorize_gmail.py /path/to/credentials.json")
        print()
        print("Or run without arguments if credentials.json is in current directory:")
        print("  python authorize_gmail.py")
        sys.exit(1)
    
    credentials_path = sys.argv[1]
    vault_path = Path(credentials_path).parent
    
    # Save token in same directory as credentials
    token_path = vault_path / 'token.json'
    
    authorize(str(credentials_path), str(token_path))


if __name__ == '__main__':
    main()
