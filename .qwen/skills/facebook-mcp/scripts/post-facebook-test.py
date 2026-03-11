#!/usr/bin/env python3
"""Test Facebook Post"""

import urllib.request
import json

SERVER_URL = 'http://localhost:8771/mcp'

def post_to_facebook(message, link=None):
    """Post to Facebook via MCP Server"""
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "post_to_facebook",
            "arguments": {
                "message": message,
                "link": link
            }
        }
    }
    
    data = json.dumps(request).encode('utf-8')
    req = urllib.request.Request(
        SERVER_URL,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    print("=" * 60)
    print("Posting to Facebook")
    print("=" * 60)
    print()
    
    # Test post
    message = "Testing my AI Employee Gold Tier! Automation AI"
    
    print("Posting:", message)
    print()
    
    result = post_to_facebook(message)
    
    print("Response:")
    print(json.dumps(result, indent=2))
    print()
    
    if 'result' in result:
        result_text = json.loads(result['result']['content'][0]['text'])
        if result_text.get('success'):
            print("[OK] Post published successfully!")
            print(f"Post ID: {result_text.get('post_id')}")
            print()
            print("Check your Facebook Page to see the post!")
        else:
            print(f"[ERROR] {result_text.get('error')}")
    else:
        print(f"[ERROR] {result}")
    
    print("=" * 60)
