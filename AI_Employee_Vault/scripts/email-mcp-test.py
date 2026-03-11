#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email MCP Client - Test client for Email MCP Server.

Usage:
    python email-mcp-test.py send --to "test@example.com" --subject "Test" --body "Hello"
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '.qwen/skills/browsing-with-playwright/scripts'))

try:
    from mcp_client import MCPClient, HTTPTransport
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP Client not available. Make sure mcp-client.py exists in browsing-with-playwright/scripts")


def send_email(server_url: str, to: str, subject: str, body: str):
    """Send an email via MCP server."""
    if not MCP_AVAILABLE:
        print("MCP Client not available")
        return
    
    try:
        transport = HTTPTransport(server_url)
        client = MCPClient(transport)
        
        # Call send_email tool
        result = client.call_tool('send_email', {
            'to': to,
            'subject': subject,
            'body': body
        })
        
        print("Email sent successfully!")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error sending email: {e}")


def list_tools(server_url: str):
    """List available tools on MCP server."""
    if not MCP_AVAILABLE:
        print("MCP Client not available")
        return
    
    try:
        transport = HTTPTransport(server_url)
        client = MCPClient(transport)
        
        tools = client.list_tools()
        
        print("Available tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        
    except Exception as e:
        print(f"Error listing tools: {e}")


def main():
    parser = argparse.ArgumentParser(description='Email MCP Test Client')
    parser.add_argument('action', choices=['send', 'list', 'draft'], help='Action to perform')
    parser.add_argument('--server', default='http://localhost:8765', help='MCP server URL')
    parser.add_argument('--to', help='Recipient email address')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_tools(args.server)
    elif args.action == 'send':
        if not args.to or not args.subject or not args.body:
            print("Error: --to, --subject, and --body required for send action")
            sys.exit(1)
        send_email(args.server, args.to, args.subject, args.body)
    elif args.action == 'draft':
        print("Draft action not implemented yet")


if __name__ == '__main__':
    main()
