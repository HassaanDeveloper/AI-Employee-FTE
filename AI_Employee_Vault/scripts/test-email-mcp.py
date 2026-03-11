#!/usr/bin/env python3
"""Test sending email via MCP Server"""

import json
import urllib.request

SERVER_URL = 'http://localhost:8765/mcp'

def send_email(to, subject, body):
    """Send email via MCP server using JSON-RPC"""
    
    # MCP JSON-RPC request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "send_email",
            "arguments": {
                "to": to,
                "subject": subject,
                "body": body
            }
        }
    }
    
    # Send request
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
            print("Response:")
            print(json.dumps(result, indent=2))
            return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    print("Testing Email MCP Server...")
    print("Sending test email...")
    
    # Send test email
    result = send_email(
        to="oneminuteclips03@gmail.com",  # Send back to the test sender
        subject="Re: Salam - AI Employee Test",
        body="Walaikum Assalam! This is a test email sent via the Email MCP Server. - AI Employee"
    )
    
    if result and 'result' in result:
        print("\n[OK] Email sent successfully via MCP Server!")
        print(f"Message ID: {result['result']['content'][0]['text']}")
    else:
        print("\n[ERROR] Failed to send email")
