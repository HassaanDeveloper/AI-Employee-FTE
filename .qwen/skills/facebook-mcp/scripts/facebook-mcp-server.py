#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook/Instagram MCP Server - Social media integration for AI Employee.

Provides tools for:
- Posting to Facebook Page
- Posting to Instagram
- Getting insights/analytics
- Managing comments

Usage:
    python facebook-mcp-server.py --port 8771
"""

import sys
import json
import argparse
import logging
import time
from typing import Optional, List, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

# Facebook SDK
try:
    import facebook
    FACEBOOK_AVAILABLE = True
except ImportError:
    FACEBOOK_AVAILABLE = False
    print("Facebook SDK not available. Install with: pip install facebook-sdk")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FacebookMCP')


class FacebookClient:
    """Facebook Graph API client."""

    def __init__(self, access_token: str, page_id: str = None):
        self.access_token = access_token
        self.page_id = page_id or '993926910480113'  # Default to user's page
        self.instagram_id = None
        
        # Initialize Facebook Graph API (version parameter removed - SDK uses default)
        try:
            self.graph = facebook.GraphAPI(access_token=access_token)
            logger.info(f"Facebook Client initialized for Page: {self.page_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Facebook Graph API: {e}")
            raise
        
        # Try to get Instagram account (optional)
        self._get_instagram_account()
    
    def _get_instagram_account(self):
        """Get connected Instagram Business account (optional)."""
        try:
            page_info = self.graph.get_object(self.page_id, fields='instagram_business_account')
            if page_info.get('instagram_business_account'):
                self.instagram_id = page_info['instagram_business_account']['id']
                logger.info(f"Connected to Instagram: {self.instagram_id}")
        except Exception as e:
            logger.debug(f"Instagram not connected (this is optional): {e}")
    
    def post_to_facebook(self, message: str, link: str = None) -> Dict:
        """Post to Facebook Page."""
        try:
            if not self.page_id:
                return {'success': False, 'error': 'No Facebook page connected'}
            
            post_data = {'message': message}
            if link:
                post_data['link'] = link
            
            result = self.graph.put_object(self.page_id, 'feed', **post_data)
            logger.info(f"Posted to Facebook: {result}")
            
            return {'success': True, 'post_id': result.get('id')}
        except Exception as e:
            logger.error(f"Facebook post failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_to_instagram(self, caption: str, image_url: str) -> Dict:
        """Post to Instagram Business account."""
        try:
            if not self.instagram_id:
                return {'success': False, 'error': 'No Instagram account connected'}
            
            # Step 1: Create media container
            container = self.graph.post_object(
                self.instagram_id,
                'media',
                image_url=image_url,
                caption=caption
            )
            
            # Step 2: Publish the media
            time.sleep(2)  # Wait for container to be ready
            self.graph.post_object(
                self.instagram_id,
                'media_publish',
                creation_id=container['id']
            )
            
            logger.info(f"Posted to Instagram: {container}")
            return {'success': True, 'container_id': container.get('id')}
        except Exception as e:
            logger.error(f"Instagram post failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_insights(self, metric: str = 'page_impressions', days: int = 7) -> Dict:
        """Get Facebook Page insights."""
        try:
            if not self.page_id:
                return {'success': False, 'error': 'No Facebook page connected'}
            
            # Calculate date range
            until_date = datetime.now()
            since_date = until_date - timedelta(days=days)
            
            insights = self.graph.get_object(
                self.page_id,
                fields=f'insights.metric({metric}).since({since_date.strftime("%Y-%m-%d")}).until({until_date.strftime("%Y-%m-%d")})'
            )
            
            return {
                'success': True,
                'metric': metric,
                'period': f"{since_date.strftime('%Y-%m-%d')} to {until_date.strftime('%Y-%m-%d')}",
                'data': insights
            }
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_posts(self, limit: int = 10) -> Dict:
        """Get recent posts from Facebook Page."""
        try:
            if not self.page_id:
                return {'success': False, 'error': 'No Facebook page connected'}
            
            posts = self.graph.get_connections(self.page_id, 'feed', limit=limit)
            
            return {
                'success': True,
                'posts': posts.get('data', [])
            }
        except Exception as e:
            logger.error(f"Failed to get posts: {e}")
            return {'success': False, 'error': str(e)}


class FacebookMCPServer:
    """Facebook MCP Server for AI Employee."""

    def __init__(self, access_token: str, page_id: str = '993926910480113'):
        self.client = FacebookClient(access_token, page_id)
    
    def post_to_facebook(self, message: str, link: str = None) -> Dict:
        return self.client.post_to_facebook(message, link)
    
    def post_to_instagram(self, caption: str, image_url: str) -> Dict:
        return self.client.post_to_instagram(caption, image_url)
    
    def get_insights(self, metric: str = 'page_impressions', days: int = 7) -> Dict:
        return self.client.get_insights(metric, days)
    
    def get_posts(self, limit: int = 10) -> Dict:
        return self.client.get_posts(limit)
    
    def list_tools(self) -> List[Dict]:
        """List available MCP tools."""
        return [
            {
                'name': 'post_to_facebook',
                'description': 'Post to Facebook Page',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'description': 'Post message'},
                        'link': {'type': 'string', 'description': 'Optional link to share'}
                    },
                    'required': ['message']
                }
            },
            {
                'name': 'post_to_instagram',
                'description': 'Post to Instagram Business account',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'caption': {'type': 'string', 'description': 'Instagram caption'},
                        'image_url': {'type': 'string', 'description': 'Image URL to post'}
                    },
                    'required': ['caption', 'image_url']
                }
            },
            {
                'name': 'get_insights',
                'description': 'Get Facebook Page insights',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'metric': {'type': 'string', 'description': 'Metric name (e.g., page_impressions)'},
                        'days': {'type': 'number', 'description': 'Number of days to look back'}
                    },
                    'required': ['metric']
                }
            },
            {
                'name': 'get_posts',
                'description': 'Get recent posts from Facebook Page',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'number', 'description': 'Number of posts to retrieve'}
                    }
                }
            }
        ]


def handle_request(server: FacebookMCPServer, request: dict) -> dict:
    """Handle MCP JSON-RPC request."""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    def create_response(result):
        return {'jsonrpc': '2.0', 'id': request_id, 'result': result}
    
    def create_error(error, code=-32603):
        return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': code, 'message': error}}
    
    try:
        if method == 'tools/list':
            return create_response({'tools': server.list_tools()})
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name == 'post_to_facebook':
                result = server.post_to_facebook(
                    arguments.get('message'),
                    arguments.get('link')
                )
            elif tool_name == 'post_to_instagram':
                result = server.post_to_instagram(
                    arguments.get('caption'),
                    arguments.get('image_url')
                )
            elif tool_name == 'get_insights':
                result = server.get_insights(
                    arguments.get('metric', 'page_impressions'),
                    arguments.get('days', 7)
                )
            elif tool_name == 'get_posts':
                result = server.get_posts(arguments.get('limit', 10))
            else:
                return create_error(f"Unknown tool: {tool_name}")
            
            return create_response({'content': [{'type': 'text', 'text': json.dumps(result)}]})
        
        elif method == 'initialize':
            return create_response({
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'serverInfo': {'name': 'facebook-mcp', 'version': '1.0.0'}
            })
        
        else:
            return create_error(f"Unknown method: {method}")
    
    except Exception as e:
        return create_error(str(e))


class MCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP requests."""
    
    def __init__(self, *args, server_instance=None, **kwargs):
        self.server_instance = server_instance
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        try:
            request = json.loads(body)
            response = handle_request(self.server_instance, request)
        except json.JSONDecodeError:
            response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Invalid JSON'}}
        except Exception as e:
            response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32603, 'message': str(e)}}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {args[0]}")


def run_server(host: str, port: int, access_token: str, page_id: str):
    """Run the Facebook MCP Server."""
    if not FACEBOOK_AVAILABLE:
        logger.error("Facebook SDK not installed. Install with: pip install facebook-sdk")
        sys.exit(1)

    try:
        server = FacebookMCPServer(access_token, page_id)
        logger.info(f"Facebook MCP Server initialized for Page: {page_id}")
    except Exception as e:
        logger.error(f"Failed to initialize Facebook: {e}")
        sys.exit(1)

    def handler_factory(*args, **kwargs):
        MCPHandler(*args, server_instance=server, **kwargs)

    httpd = HTTPServer((host, port), handler_factory)
    logger.info(f"Facebook MCP Server running on http://{host}:{port}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Facebook MCP Server")
        httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(description='Facebook MCP Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8771, help='Server port')
    parser.add_argument('--access-token', required=True, help='Facebook Page Access Token')
    parser.add_argument('--page-id', default='993926910480113', help='Facebook Page ID (default: 993926910480113)')

    args = parser.parse_args()

    run_server(args.host, args.port, args.access_token, args.page_id)


if __name__ == '__main__':
    main()
