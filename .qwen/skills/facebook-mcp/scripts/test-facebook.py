#!/usr/bin/env python3
"""Test Facebook MCP Server"""

import urllib.request
import json

SERVER_URL = 'http://localhost:8771/mcp'

def test_facebook_connection():
    """Test Facebook connection by getting recent posts"""
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_posts",
            "arguments": {
                "limit": 3
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
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Facebook MCP Server")
    print("=" * 60)
    print()
    print("Getting recent posts from your Facebook Page...")
    print()
    
    result = test_facebook_connection()
    
    print("Response:")
    print(json.dumps(result, indent=2))
    print()
    
    if 'result' in result:
        print("[OK] Facebook MCP Server is working!")
    else:
        print("[ERROR] Check your access token")
    
    print("=" * 60)
