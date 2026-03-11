---
name: email-mcp
description: |
  Email MCP Server - Send, draft, and search emails via Gmail API.
  Provides tools for the AI Employee to send emails with human-in-the-loop
  approval for sensitive actions. Supports attachments, HTML content,
  and batch operations.
---

# Email MCP Server

Send and manage emails via Gmail API with human-in-the-loop approval.

## Setup

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. Authorize

```bash
python scripts/email-mcp-authorize.py /path/to/credentials.json
```

## Usage

### Start the MCP Server

```bash
# Start server on port 8765
python scripts/email-mcp-server.py --port 8765
```

### Call Tools via MCP Client

```bash
# Send an email
python scripts/mcp-client.py call -u http://localhost:8765 \
  -t send_email \
  -p '{"to": "client@example.com", "subject": "Invoice #123", "body": "Please find attached..."}'

# Draft an email (doesn't send)
python scripts/mcp-client.py call -u http://localhost:8765 \
  -t draft_email \
  -p '{"to": "client@example.com", "subject": "Follow up", "body": "Hi..."}'

# Search emails
python scripts/mcp-client.py call -u http://localhost:8765 \
  -t search_emails \
  -p '{"query": "is:unread", "max_results": 10}'
```

## Tools

### `send_email`

Send an email immediately.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body (plain text or HTML)
- `cc` (string, optional): CC recipients (comma-separated)
- `bcc` (string, optional): BCC recipients (comma-separated)
- `attachments` (array, optional): List of file paths to attach

### `draft_email`

Create a draft email (doesn't send).

**Parameters:** Same as `send_email`

### `search_emails`

Search Gmail for messages.

**Parameters:**
- `query` (string, required): Gmail search query
- `max_results` (number, optional): Max results (default: 10)

### `mark_read`

Mark emails as read.

**Parameters:**
- `message_ids` (array, required): List of message IDs to mark as read

## Human-in-the-Loop Pattern

For sensitive actions, use the approval workflow:

1. **AI creates** approval request in `Pending_Approval/`:
   ```markdown
   ---
   type: approval_request
   action: send_email
   to: client@example.com
   subject: Invoice #123
   ---
   
   Ready to send. Move to /Approved to proceed.
   ```

2. **Human reviews** and moves to `Approved/`

3. **Orchestrator executes** the email send

## Security

- Credentials stored in vault (never commit to git)
- OAuth tokens auto-refresh
- Rate limiting: max 10 emails/minute
- Dry-run mode for testing

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authorization failed | Re-run authorize script |
| Token expired | Delete token.json, re-authorize |
| API quota exceeded | Wait 24 hours or request quota increase |
| Attachment not found | Check file path is absolute |
