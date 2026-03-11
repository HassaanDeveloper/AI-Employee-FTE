#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email MCP Server - Gmail API server for AI Employee.

Provides tools for sending, drafting, and searching emails.
Uses MCP (Model Context Protocol) for communication.

Usage:
    python email-mcp-server.py --port 8765
"""

import sys
import json
import base64
import argparse
import logging
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("Gmail API libraries not installed.")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EmailMCP')

SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']


class EmailMCPServer:
    """Email MCP Server for Gmail operations."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.credentials_path = self.vault_path / 'credentials.json'
        self.token_path = self.vault_path / 'token.json'
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        if not EMAIL_AVAILABLE:
            return False
        
        creds = None
        
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            except Exception as e:
                logger.warning(f"Could not load token: {e}")
                creds = None
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Token refresh failed: {e}")
                    return False
            else:
                logger.error("No valid credentials. Run email-mcp-authorize.py first.")
                return False
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail authentication successful")
            return True
        except Exception as e:
            logger.error(f"Could not build Gmail service: {e}")
            return False
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: Optional[str] = None, bcc: Optional[str] = None,
                   attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send an email."""
        if not self.service:
            return {'error': 'Not authenticated'}
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Add body
            message.attach(MIMEText(body, 'html' if '<' in body else 'plain'))
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    try:
                        part = MIMEBase('application', 'octet-stream')
                        with open(filepath, 'rb') as f:
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{Path(filepath).name}"'
                        )
                        message.attach(part)
                    except Exception as e:
                        logger.warning(f"Could not attach {filepath}: {e}")
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent to {to}, message ID: {sent_message['id']}")
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId']
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {'error': str(e)}
    
    def draft_email(self, to: str, subject: str, body: str,
                    cc: Optional[str] = None, attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a draft email."""
        if not self.service:
            return {'error': 'Not authenticated'}
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = body
            
            if cc:
                message['cc'] = cc
            
            message.attach(MIMEText(body, 'html' if '<' in body else 'plain'))
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    try:
                        part = MIMEBase('application', 'octet-stream')
                        with open(filepath, 'rb') as f:
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{Path(filepath).name}"'
                        )
                        message.attach(part)
                    except Exception as e:
                        logger.warning(f"Could not attach {filepath}: {e}")
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create draft
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            logger.info(f"Draft created, ID: {draft['id']}")
            
            return {
                'success': True,
                'draft_id': draft['id'],
                'message_id': draft['message']['id']
            }
            
        except Exception as e:
            logger.error(f"Error creating draft: {e}")
            return {'error': str(e)}
    
    def search_emails(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search for emails."""
        if not self.service:
            return {'error': 'Not authenticated'}
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full details for each message
            email_list = []
            for msg in messages[:max_results]:
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
                email_list.append({
                    'id': msg['id'],
                    'from': headers.get('From', ''),
                    'to': headers.get('To', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', ''),
                    'snippet': full_msg.get('snippet', '')
                })
            
            return {
                'success': True,
                'count': len(email_list),
                'messages': email_list
            }
            
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return {'error': str(e)}
    
    def mark_read(self, message_ids: List[str]) -> Dict[str, Any]:
        """Mark emails as read."""
        if not self.service:
            return {'error': 'Not authenticated'}
        
        try:
            for msg_id in message_ids:
                self.service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            
            logger.info(f"Marked {len(message_ids)} messages as read")
            
            return {
                'success': True,
                'marked_count': len(message_ids)
            }
            
        except Exception as e:
            logger.error(f"Error marking as read: {e}")
            return {'error': str(e)}


# MCP Server implementation
def create_mcp_response(result: Any, request_id: Any) -> dict:
    """Create JSON-RPC response."""
    return {
        'jsonrpc': '2.0',
        'id': request_id,
        'result': result
    }


def create_error_response(error: str, code: int, request_id: Any) -> dict:
    """Create JSON-RPC error response."""
    return {
        'jsonrpc': '2.0',
        'id': request_id,
        'error': {
            'code': code,
            'message': error
        }
    }


def handle_request(server: EmailMCPServer, request: dict) -> dict:
    """Handle MCP request."""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    try:
        if method == 'tools/list':
            return create_mcp_response({
                'tools': [
                    {
                        'name': 'send_email',
                        'description': 'Send an email via Gmail',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'to': {'type': 'string', 'description': 'Recipient email'},
                                'subject': {'type': 'string', 'description': 'Email subject'},
                                'body': {'type': 'string', 'description': 'Email body'},
                                'cc': {'type': 'string', 'description': 'CC recipients'},
                                'attachments': {'type': 'array', 'items': {'type': 'string'}}
                            },
                            'required': ['to', 'subject', 'body']
                        }
                    },
                    {
                        'name': 'draft_email',
                        'description': 'Create a draft email',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'to': {'type': 'string'},
                                'subject': {'type': 'string'},
                                'body': {'type': 'string'},
                                'cc': {'type': 'string'}
                            },
                            'required': ['to', 'subject', 'body']
                        }
                    },
                    {
                        'name': 'search_emails',
                        'description': 'Search Gmail for messages',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'query': {'type': 'string', 'description': 'Gmail search query'},
                                'max_results': {'type': 'number', 'default': 10}
                            },
                            'required': ['query']
                        }
                    },
                    {
                        'name': 'mark_read',
                        'description': 'Mark emails as read',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'message_ids': {'type': 'array', 'items': {'type': 'string'}}
                            },
                            'required': ['message_ids']
                        }
                    }
                ]
            }, request_id)
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name == 'send_email':
                result = server.send_email(
                    to=arguments.get('to'),
                    subject=arguments.get('subject'),
                    body=arguments.get('body'),
                    cc=arguments.get('cc'),
                    attachments=arguments.get('attachments')
                )
            elif tool_name == 'draft_email':
                result = server.draft_email(
                    to=arguments.get('to'),
                    subject=arguments.get('subject'),
                    body=arguments.get('body'),
                    cc=arguments.get('cc')
                )
            elif tool_name == 'search_emails':
                result = server.search_emails(
                    query=arguments.get('query'),
                    max_results=arguments.get('max_results', 10)
                )
            elif tool_name == 'mark_read':
                result = server.mark_read(
                    message_ids=arguments.get('message_ids', [])
                )
            else:
                return create_error_response(f"Unknown tool: {tool_name}", -32601, request_id)
            
            return create_mcp_response({'content': [{'type': 'text', 'text': json.dumps(result)}]}, request_id)
        
        elif method == 'initialize':
            return create_mcp_response({
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'serverInfo': {'name': 'email-mcp', 'version': '1.0.0'}
            }, request_id)
        
        else:
            return create_error_response(f"Unknown method: {method}", -32601, request_id)
            
    except Exception as e:
        return create_error_response(str(e), -32603, request_id)


def run_http_server(server: EmailMCPServer, port: int):
    """Run MCP server over HTTP."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class MCPHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            
            try:
                request = json.loads(body)
                response = handle_request(server, request)
            except json.JSONDecodeError:
                response = create_error_response("Invalid JSON", -32700, None)
            except Exception as e:
                response = create_error_response(str(e), -32603, request.get('id'))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        def log_message(self, format, *args):
            logger.info(f"{self.address_string()} - {args[0]}")
    
    httpd = HTTPServer(('localhost', port), MCPHandler)
    logger.info(f"Email MCP server running on http://localhost:{port}")
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--vault', default='.', help='Path to vault')
    parser.add_argument('--port', type=int, default=8765, help='Server port')
    
    args = parser.parse_args()
    
    server = EmailMCPServer(args.vault)
    
    if not server.service:
        logger.error("Failed to authenticate. Run email-mcp-authorize.py first.")
        sys.exit(1)
    
    run_http_server(server, args.port)


if __name__ == '__main__':
    main()
