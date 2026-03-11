#!/usr/bin/env python3
"""Quick test for Odoo MCP Server"""

import urllib.request
import json

print("Testing Odoo MCP Server...")
print("-" * 50)

request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "create_customer",
        "arguments": {
            "name": "Test Customer",
            "email": "test@example.com"
        }
    }
}

data = json.dumps(request).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:8770/mcp',
    data=data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        print('Result:', json.dumps(result, indent=2))
except Exception as e:
    print(f'Error: {e}')
