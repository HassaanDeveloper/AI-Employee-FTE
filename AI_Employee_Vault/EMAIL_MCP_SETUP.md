# Email MCP Server - Complete Setup Guide

## Overview

The Email MCP Server allows your AI Employee to **send emails** via Gmail API.

```
QWEN CODE → ORCHESTRATOR → Email MCP Server → Gmail API → Email Sent
```

---

## Architecture

```
┌─────────────────┐
│  Qwen Code      │ (decides to send reply)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │ (extracts email details)
└────────┬────────┘
         │ (JSON-RPC call)
         ▼
┌─────────────────┐
│ Email MCP Server│ (port 8765)
│ (localhost:8765)│
└────────┬────────┘
         │ (Gmail API)
         ▼
┌─────────────────┐
│  Gmail API      │ (sends email)
└─────────────────┘
```

---

## Setup Steps

### Step 1: Prerequisites

Make sure these exist:
- `credentials.json` in vault root
- `token.json` in vault root (created by `authorize_gmail.py`)

### Step 2: Start Email MCP Server

**Terminal 1:**
```bash
cd E:\AI-Employee-FTE\.qwen\skills\email-mcp\scripts

python email-mcp-server.py --vault E:\AI-Employee-FTE\AI_Employee_Vault --port 8765
```

**Expected output:**
```
INFO:EmailMCP:Gmail authentication successful
INFO:EmailMCP:Email MCP server running on http://localhost:8765
```

**Keep this terminal open!**

### Step 3: Test MCP Server

**Terminal 2:**
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts

python test-email-mcp.py
```

**Expected output:**
```
Testing Email MCP Server...
Sending test email...
Response:
{
  "success": true,
  "message_id": "..."
}
[OK] Email sent successfully via MCP Server!
```

### Step 4: Run Orchestrator

**Terminal 2 (after test):**
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts

python orchestrator.py .. --interval 30
```

The Orchestrator now uses the Email MCP Server to send emails!

---

## Full Workflow Example

### 1. Email Arrives

Someone sends an email to your Gmail:
```
From: client@example.com
Subject: Invoice Request
Body: Can you send the invoice?
```

### 2. Gmail Watcher Detects It

```bash
# Terminal 3
python gmail_watcher.py .. --interval 120
```

Creates: `Needs_Action/EMAIL_*_Invoice_Request.md`

### 3. Orchestrator Processes It

```bash
# Terminal 2
python orchestrator.py .. --interval 30
```

Qwen Code reads the email and decides to send a reply.

### 4. Approval Request Created

Qwen Code creates: `Pending_Approval/EMAIL_reply_client.md`

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Re: Invoice Request
body: Here is your invoice...
---

Move to /Approved to send.
```

### 5. You Approve

Move the file from `Pending_Approval/` to `Approved/`

### 6. Orchestrator Sends Email

Orchestrator detects approved file and calls Email MCP Server:

```
POST http://localhost:8765/mcp
{
  "method": "tools/call",
  "params": {
    "name": "send_email",
    "arguments": {
      "to": "client@example.com",
      "subject": "Re: Invoice Request",
      "body": "Here is your invoice..."
    }
  }
}
```

### 7. Email Sent!

```
INFO: Sending email to client@example.com via Email MCP Server
INFO: Email sent successfully! Message ID: 19cbea07cbc06512
```

File moved to `Done/`

---

## Commands Reference

### Start Email MCP Server
```bash
cd E:\AI-Employee-FTE\.qwen\skills\email-mcp\scripts
python email-mcp-server.py --vault E:\AI-Employee-FTE\AI_Employee_Vault --port 8765
```

### Test Email MCP Server
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python test-email-mcp.py
```

### Send Custom Test Email
```bash
python test-email-mcp.py send \
  --to "recipient@example.com" \
  --subject "Test Subject" \
  --body "Test message body"
```

### Run Orchestrator
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python orchestrator.py .. --interval 30
```

---

## Running All Components

For full AI Employee operation, open **4 terminal windows**:

### Terminal 1: Email MCP Server
```bash
cd E:\AI-Employee-FTE\.qwen\skills\email-mcp\scripts
python email-mcp-server.py --vault E:\AI-Employee-FTE\AI_Employee_Vault --port 8765
```

### Terminal 2: Orchestrator
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python orchestrator.py .. --interval 30
```

### Terminal 3: Gmail Watcher
```bash
python gmail_watcher.py .. --interval 120
```

### Terminal 4: (Optional) LinkedIn Watcher
```bash
python linkedin_watcher.py .. --interval 300
```

---

## Troubleshooting

### "Connection refused" on port 8765

**Email MCP Server not running. Start it:**
```bash
cd E:\AI-Employee-FTE\.qwen\skills\email-mcp\scripts
python email-mcp-server.py --vault E:\AI-Employee-FTE\AI_Employee_Vault --port 8765
```

### "Gmail authentication failed"

**Re-authorize Gmail:**
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python authorize_gmail.py ..\credentials.json
```

### "Missing email fields"

**Check approval file has correct frontmatter:**
```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Re: Invoice
body: Here is your invoice...
---
```

---

## Status Check

| Component | Status | Command to Verify |
|-----------|--------|-------------------|
| Email MCP Server | ✅ Running | `python test-email-mcp.py` |
| Orchestrator | ✅ Integrated | Check logs for "via Email MCP Server" |
| Gmail Watcher | ✅ Working | Sends email to `Needs_Action/` |
| Approval Workflow | ✅ Ready | Create file in `Pending_Approval/` |

---

## Quick Test: Send Email via Approval

### Step 1: Create Approval Request

Create file: `Pending_Approval/TEST_EMAIL.md`

```markdown
---
type: approval_request
action: send_email
to: oneminuteclips03@gmail.com
subject: Test from AI Employee
body: This is a test email sent via the Email MCP Server!
created: 2026-03-04T00:00:00Z
---

Move to /Approved to send.
```

### Step 2: Move to Approved

```bash
move E:\AI-Employee-FTE\AI_Employee_Vault\Pending_Approval\TEST_EMAIL.md E:\AI-Employee-FTE\AI_Employee_Vault\Approved\
```

### Step 3: Check Orchestrator Logs

Orchestrator should detect and send the email within 30 seconds!

---

**Your AI Employee can now SEND emails!** 🎉
