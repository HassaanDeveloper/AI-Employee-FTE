#!/usr/bin/env python3
"""
Facebook Personal Profile Post Helper

Facebook API does NOT support personal profile posting.
This script helps you post manually.

Usage:
    python facebook-personal-post.py "Your message here"
"""

import sys
import webbrowser
from datetime import datetime

def create_post_file(message):
    """Create a post file in Approved folder"""
    from pathlib import Path
    
    vault_path = Path(__file__).parent.parent.parent / 'AI_Employee_Vault' / 'Approved'
    vault_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'FB_PERSONAL_POST_{timestamp}.md'
    filepath = vault_path / filename
    
    content = f'''---
type: approval_request
action: post_to_facebook_personal
message: {message}
created: {datetime.now().isoformat()}
status: manual_post_required
note: Facebook API does not support personal profile posting
---

# Facebook Personal Profile Post

**Message:**
{message}

## Instructions

1. **Copy the message above**
2. **Open:** https://www.facebook.com/
3. **Paste in "What's on your mind?" box**
4. **Click Post**
5. **Move this file to Done/ folder**

---
*Created by AI Employee - Manual Post Required*
'''
    
    filepath.write_text(content, encoding='utf-8')
    return filepath

def open_facebook():
    """Open Facebook in browser"""
    webbrowser.open('https://www.facebook.com/')

if __name__ == '__main__':
    print("=" * 60)
    print("Facebook Personal Profile Post Helper")
    print("=" * 60)
    print()
    print("NOTE: Facebook API does NOT support personal profile posting.")
    print("This helper creates a post file for manual posting.")
    print()
    
    # Get message
    if len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
    else:
        message = "AI Employee Gold Tier is LIVE! Full automation working. #AI #Automation"
    
    print(f"Message: {message}")
    print()
    
    # Create post file
    filepath = create_post_file(message)
    print(f"[OK] Post file created: {filepath}")
    print()
    
    # Ask to open Facebook
    response = input("Open Facebook in browser to post? (y/n): ")
    if response.lower() == 'y':
        open_facebook()
        print()
        print("After posting manually, move the file to Done/ folder")
    
    print()
    print("=" * 60)
