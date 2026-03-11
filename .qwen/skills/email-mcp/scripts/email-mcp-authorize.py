#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email MCP Authorize - OAuth authorization for Gmail API.

Usage:
    python email-mcp-authorize.py /path/to/credentials.json
"""

import sys
import json
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Gmail API libraries not installed.")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)


SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']


def authorize(credentials_path: str, token_path: str = 'token.json'):
    """Run OAuth flow and save token."""
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
    
    print("Starting Gmail OAuth authorization...")
    print("A browser window will open for authorization.")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        SCOPES
    )
    
    creds = flow.run_local_server(port=0)
    
    # Save credentials
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    
    print(f"\n✓ Authorization successful!")
    print(f"Token saved to: {token_path}")
    print("\nYou can now use the Email MCP server.")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python email-mcp-authorize.py /path/to/credentials.json")
        sys.exit(1)
    
    credentials_path = sys.argv[1]
    authorize(credentials_path)


if __name__ == '__main__':
    main()
