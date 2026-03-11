#!/usr/bin/env python3
"""Simple Facebook Test - Check Token Validity"""

import urllib.request
import json

# Test Facebook Graph API directly (without MCP Server)
def test_token(token):
    """Test if token is valid by getting user info"""
    
    url = f"https://graph.facebook.com/v18.0/me?access_token={token}&fields=id,name,email"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    print("=" * 60)
    print("Facebook Token Test")
    print("=" * 60)
    print()
    
    # Your token
    token = "EAANKfSpr4JIBQ2rqAojZC6yvIFRBdRfHa3acAgJ6ogQp80bybgZCMSZBLRqqLOEef8S1R3SdmZAZBS3HS2S7cnfF12bZA6HF0Vpf3ZAqR4ZAnkgF37E4JUDhiXMMKBtdocZBBBVcW89pd8Gtufi2UMwYjsx1BUpAiyQJ4tz7UbMZAu81kCCOUU5z51Khjj7q5bfFZBuW3ZCkqYcX4JOtpSzEOgXp8qkxPQdrprI2g07MvnF2ArLAzLXnT9P2ItnflFMltan0P2MfgNzELA5ZAkroAsfgv"
    
    print("Testing your Facebook access token...")
    print()
    
    result = test_token(token)
    
    print("Result:")
    print(json.dumps(result, indent=2))
    print()
    
    if 'id' in result:
        print(f"[OK] Token is valid!")
        print(f"User ID: {result.get('id')}")
        print(f"Name: {result.get('name')}")
        print()
        print("NOTE: This is a USER token. To post to Facebook Pages,")
        print("you need a PAGE access token.")
        print()
        print("Get Page Token:")
        print("1. Go to: https://developers.facebook.com/tools/explorer/")
        print("2. Click 'Get Token' → 'Get Page Access Token'")
        print("3. Select your Facebook Page")
        print("4. Copy the new token and restart Facebook MCP Server")
    else:
        print(f"[ERROR] Token is invalid: {result}")
    
    print("=" * 60)
