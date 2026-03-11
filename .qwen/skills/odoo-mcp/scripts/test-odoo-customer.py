#!/usr/bin/env python3
"""Test Odoo MCP - Create Customer"""

import urllib.request
import json

SERVER_URL = 'http://localhost:8770/mcp'

def create_customer(name, email='', phone=''):
    """Create customer via Odoo MCP Server"""
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_customer",
            "arguments": {
                "name": name,
                "email": email,
                "phone": phone
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
    print("Testing Odoo MCP Server - Create Customer")
    print("=" * 60)
    print()
    
    # Test customer details
    name = "Test Customer - AI Employee Demo"
    email = "test@aiemployee.com"
    phone = "+92-300-1234567"
    
    print(f"Creating customer: {name}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print()
    
    # Create customer
    result = create_customer(name, email, phone)
    
    print("Response from Odoo:")
    print(json.dumps(result, indent=2))
    print()
    
    # Check if successful
    if 'result' in result:
        result_text = json.loads(result['result']['content'][0]['text'])
        if result_text.get('success'):
            print(f"[OK] Customer created successfully!")
            print(f"Customer ID: {result_text.get('customer_id')}")
            print()
            print("Check your Odoo at: https://hassuu1.odoo.com")
            print("Go to: Invoicing → Customers → Find your customer")
        else:
            print(f"[ERROR] Failed to create customer: {result_text}")
    else:
        print(f"[ERROR] Unexpected response: {result}")
    
    print()
    print("=" * 60)
