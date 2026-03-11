#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo MCP Server - Odoo ERP integration for AI Employee.

Provides tools for:
- Creating invoices
- Managing customers
- Recording payments
- Generating reports
- Accounting operations

Usage:
    python odoo-mcp-server.py --host localhost --port 8770
"""

import sys
import json
import argparse
import logging
from typing import Optional, List, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Odoo JSON-RPC API
try:
    import xmlrpc.client
    ODOO_AVAILABLE = True
except ImportError:
    ODOO_AVAILABLE = False
    print("xmlrpc not available. Install with: pip install xmlrpcclient")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OdooMCP')


class OdooClient:
    """Odoo JSON-RPC/XML-RPC client."""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Odoo."""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                raise Exception("Authentication failed. Check credentials.")
            logger.info(f"Authenticated with Odoo as user ID: {self.uid}")
        except Exception as e:
            logger.error(f"Odoo authentication failed: {e}")
            raise
    
    def execute(self, model: str, method: str, *args, **kwargs):
        """Execute an Odoo model method."""
        try:
            models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            return models.execute_kw(
                self.db, self.uid, self.password,
                model, method, *args, **kwargs
            )
        except Exception as e:
            logger.error(f"Odoo execute failed ({model}.{method}): {e}")
            raise
    
    def search_read(self, model: str, domain: List = None, fields: List = None, limit: int = 80):
        """Search and read records from Odoo."""
        return self.execute(model, 'search_read', domain or [], fields or [], limit=limit)
    
    def list_customers(self, limit: int = 5) -> Dict:
        """List customers from Odoo (read-only, works on trial)."""
        try:
            customers = self.search_read('res.partner', 
                domain=[('customer_rank', '>', 0)], 
                fields=['name', 'email', 'phone'], 
                limit=limit)
            logger.info(f"Listed {len(customers)} customers")
            return {'success': True, 'customers': customers, 'count': len(customers)}
        except Exception as e:
            logger.error(f"Failed to list customers: {e}")
            return {'success': False, 'error': str(e)}

    def create_invoice(self, partner_id: int, invoice_date: str, items: List[Dict]) -> Dict:
        """Create a customer invoice."""
        try:
            # Create invoice
            invoice_data = {
                'move_type': 'out_invoice',
                'partner_id': partner_id,
                'invoice_date': invoice_date,
                'invoice_line_ids': []
            }

            # Add line items
            for item in items:
                invoice_data['invoice_line_ids'].append((0, 0, {
                    'product_id': item.get('product_id'),
                    'name': item.get('name', 'Service'),
                    'quantity': item.get('quantity', 1),
                    'price_unit': item.get('price_unit', 0),
                }))

            # Wrap in list for Odoo Online API
            invoice_id = self.execute('account.move', 'create', [invoice_data])
            logger.info(f"Created invoice ID: {invoice_id}")

            return {'success': True, 'invoice_id': invoice_id}
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_customer(self, name: str, email: str = '', phone: str = '') -> Dict:
        """Create a new customer."""
        try:
            customer_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'customer_rank': 1
            }
            # Wrap in list for Odoo Online API
            customer_id = self.execute('res.partner', 'create', [customer_data])
            logger.info(f"Created customer ID: {customer_id}")
            return {'success': True, 'customer_id': customer_id}
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            return {'success': False, 'error': str(e)}
    
    def record_payment(self, invoice_id: int, amount: float, payment_date: str) -> Dict:
        """Record a payment for an invoice."""
        try:
            # Create payment register - wrap in list for Odoo Online
            payment_data = {
                'move_ids': [(4, invoice_id)],
                'amount': amount,
                'payment_date': payment_date,
            }
            payment_id = self.execute('account.payment.register', 'create', [payment_data])

            # Create payment
            self.execute('account.payment.register', 'action_create_payments', [payment_id])

            logger.info(f"Recorded payment for invoice {invoice_id}")
            return {'success': True, 'payment_id': payment_id}
        except Exception as e:
            logger.error(f"Failed to record payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_revenue_report(self, date_from: str, date_to: str) -> Dict:
        """Get revenue report for date range."""
        try:
            # Search for paid invoices in date range
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', date_from),
                ('invoice_date', '<=', date_to)
            ]
            
            invoices = self.search_read('account.move', domain, ['name', 'amount_total', 'invoice_date', 'state'])
            
            total_revenue = sum(inv['amount_total'] for inv in invoices)
            
            return {
                'success': True,
                'period': f"{date_from} to {date_to}",
                'total_revenue': total_revenue,
                'invoice_count': len(invoices),
                'invoices': invoices
            }
        except Exception as e:
            logger.error(f"Failed to get revenue report: {e}")
            return {'success': False, 'error': str(e)}


class OdooMCPServer:
    """Odoo MCP Server for AI Employee."""
    
    def __init__(self, odoo_url: str, odoo_db: str, odoo_user: str, odoo_password: str):
        self.odoo = OdooClient(odoo_url, odoo_db, odoo_user, odoo_password)
    
    def create_invoice(self, partner_id: int, invoice_date: str, items: List[Dict]) -> Dict:
        return self.odoo.create_invoice(partner_id, invoice_date, items)
    
    def create_customer(self, name: str, email: str = '', phone: str = '') -> Dict:
        return self.odoo.create_customer(name, email, phone)
    
    def record_payment(self, invoice_id: int, amount: float, payment_date: str) -> Dict:
        return self.odoo.record_payment(invoice_id, amount, payment_date)
    
    def get_revenue_report(self, date_from: str, date_to: str) -> Dict:
        return self.odoo.get_revenue_report(date_from, date_to)
    
    def list_tools(self) -> List[Dict]:
        """List available MCP tools."""
        return [
            {
                'name': 'list_customers',
                'description': 'List customers from Odoo (read-only)',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'number', 'description': 'Number of customers to list'}
                    }
                }
            },
            {
                'name': 'create_invoice',
                'description': 'Create a customer invoice in Odoo',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'partner_id': {'type': 'number', 'description': 'Customer ID'},
                        'invoice_date': {'type': 'string', 'description': 'Invoice date (YYYY-MM-DD)'},
                        'items': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'quantity': {'type': 'number'},
                                    'price_unit': {'type': 'number'}
                                }
                            }
                        }
                    },
                    'required': ['partner_id', 'invoice_date', 'items']
                }
            },
            {
                'name': 'create_customer',
                'description': 'Create a new customer in Odoo',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'description': 'Customer name'},
                        'email': {'type': 'string', 'description': 'Email address'},
                        'phone': {'type': 'string', 'description': 'Phone number'}
                    },
                    'required': ['name']
                }
            },
            {
                'name': 'record_payment',
                'description': 'Record a payment for an invoice',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'invoice_id': {'type': 'number', 'description': 'Invoice ID'},
                        'amount': {'type': 'number', 'description': 'Payment amount'},
                        'payment_date': {'type': 'string', 'description': 'Payment date (YYYY-MM-DD)'}
                    },
                    'required': ['invoice_id', 'amount', 'payment_date']
                }
            },
            {
                'name': 'get_revenue_report',
                'description': 'Get revenue report for date range',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'date_from': {'type': 'string', 'description': 'Start date (YYYY-MM-DD)'},
                        'date_to': {'type': 'string', 'description': 'End date (YYYY-MM-DD)'}
                    },
                    'required': ['date_from', 'date_to']
                }
            }
        ]


def handle_request(server: OdooMCPServer, request: dict) -> dict:
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

            if tool_name == 'list_customers':
                result = server.list_customers(
                    arguments.get('limit', 5)
                )
            elif tool_name == 'create_invoice':
                result = server.create_invoice(
                    arguments.get('partner_id'),
                    arguments.get('invoice_date'),
                    arguments.get('items', [])
                )
            elif tool_name == 'create_customer':
                result = server.create_customer(
                    arguments.get('name'),
                    arguments.get('email', ''),
                    arguments.get('phone', '')
                )
            elif tool_name == 'record_payment':
                result = server.record_payment(
                    arguments.get('invoice_id'),
                    arguments.get('amount'),
                    arguments.get('payment_date')
                )
            elif tool_name == 'get_revenue_report':
                result = server.get_revenue_report(
                    arguments.get('date_from'),
                    arguments.get('date_to')
                )
            else:
                return create_error(f"Unknown tool: {tool_name}")
            
            return create_response({'content': [{'type': 'text', 'text': json.dumps(result)}]})
        
        elif method == 'initialize':
            return create_response({
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'serverInfo': {'name': 'odoo-mcp', 'version': '1.0.0'}
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


def run_server(host: str, port: int, odoo_url: str, odoo_db: str, odoo_user: str, odoo_password: str):
    """Run the Odoo MCP Server."""
    if not ODOO_AVAILABLE:
        logger.error("xmlrpcclient not installed. Install with: pip install xmlrpcclient")
        sys.exit(1)
    
    try:
        server = OdooMCPServer(odoo_url, odoo_db, odoo_user, odoo_password)
        logger.info(f"Odoo MCP Server initialized")
    except Exception as e:
        logger.error(f"Failed to connect to Odoo: {e}")
        logger.info("Make sure Odoo is running: docker-compose up -d")
        sys.exit(1)
    
    # Create handler with server instance
    def handler_factory(*args, **kwargs):
        MCPHandler(*args, server_instance=server, **kwargs)
    
    httpd = HTTPServer((host, port), handler_factory)
    logger.info(f"Odoo MCP Server running on http://{host}:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Odoo MCP Server")
        httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(description='Odoo MCP Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8770, help='Server port')
    parser.add_argument('--odoo-url', default='http://localhost:8069', help='Odoo URL')
    parser.add_argument('--odoo-db', default='odoo_db', help='Odoo database name')
    parser.add_argument('--odoo-user', default='admin', help='Odoo username')
    parser.add_argument('--odoo-password', default='admin', help='Odoo password')
    
    args = parser.parse_args()
    
    run_server(
        args.host,
        args.port,
        args.odoo_url,
        args.odoo_db,
        args.odoo_user,
        args.odoo_password
    )


if __name__ == '__main__':
    main()
