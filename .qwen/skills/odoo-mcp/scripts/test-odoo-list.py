#!/usr/bin/env python3
"""Test Odoo MCP - List Customers (Read-Only)"""

import urllib.request
import json

SERVER_URL = 'http://localhost:8770/mcp'

def list_customers(limit=5):
    """List customers from Odoo"""
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "list_customers",
            "arguments": {
                "limit": limit
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
    print("Testing Odoo MCP Server - List Customers")
    print("=" * 60)
    print()
    print("This will show existing customers in your Odoo...")
    print()
    
    result = list_customers(5)
    
    print("Response from Odoo:")
    print(json.dumps(result, indent=2))
    print()
    
    if 'result' in result:
        print("[OK] Odoo MCP Server is working!")
    else:
        print("[ERROR] Could not connect to Odoo")
    
    print("=" * 60)
