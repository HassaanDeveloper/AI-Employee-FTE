# Gold Tier Setup Guide

## Overview

Gold Tier adds advanced business automation capabilities:

1. **Odoo ERP Integration** - Accounting, invoices, customers
2. **Facebook/Instagram Integration** - Social media posting
3. **Weekly Accounting Audit** - CEO Briefing with financial data
4. **Error Recovery** - Graceful degradation
5. **Comprehensive Audit Logging** - Full activity tracking
6. **Ralph Wiggum Loop** - Autonomous multi-step task completion

---

## Prerequisites

- ✅ Silver Tier complete and working
- ✅ Docker Desktop installed
- ✅ Python 3.13+
- ✅ All Silver Tier dependencies

---

## Step 1: Install Odoo Community (Docker)

### 1.1 Start Odoo

```bash
cd E:\AI-Employee-FTE\odoo

# Start Odoo and PostgreSQL
docker-compose up -d
```

### 1.2 Access Odoo

Open browser: http://localhost:8069

**First-time setup:**
- Master Password: `admin_password_change_me`
- Create database: `odoo_db`
- Email: your-email@example.com
- Password: Choose admin password

### 1.3 Verify Odoo is Running

```bash
docker ps | findstr odoo
```

Should show:
- `ai-employee-odoo` (port 8069)
- `ai-employee-odoo-db` (PostgreSQL)

---

## Step 2: Install Gold Tier Dependencies

```bash
pip install xmlrpcclient facebook-sdk
```

---

## Step 3: Configure Facebook/Instagram (Optional)

### 3.1 Get Facebook Page Access Token

1. Go to [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Request permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
4. Generate Access Token
5. Copy the token

### 3.2 Test Facebook Connection

```bash
cd E:\AI-Employee-FTE\.qwen\skills\facebook-mcp\scripts

python facebook-mcp-server.py --access-token YOUR_TOKEN_HERE --port 8771
```

---

## Step 4: Start Gold Tier MCP Servers

Open **separate terminal windows** for each:

### Terminal 1: Email MCP Server (Silver)
```bash
cd E:\AI-Employee-FTE\.qwen\skills\email-mcp\scripts
python email-mcp-server.py --vault E:\AI-Employee-FTE\AI_Employee_Vault --port 8765
```

### Terminal 2: Odoo MCP Server (Gold)
```bash
cd E:\AI-Employee-FTE\.qwen\skills\odoo-mcp\scripts
python odoo-mcp-server.py --port 8770 --odoo-url http://localhost:8069 --odoo-db odoo_db --odoo-user admin --odoo-password YOUR_ADMIN_PASSWORD
```

### Terminal 3: Facebook MCP Server (Gold) - Optional
```bash
cd E:\AI-Employee-FTE\.qwen\skills\facebook-mcp\scripts
python facebook-mcp-server.py --access-token YOUR_TOKEN --port 8771
```

---

## Step 5: Run AI Employee with Gold Tier

### Terminal 4: Orchestrator
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python orchestrator.py .. --interval 30
```

### Terminal 5: Gmail Watcher
```bash
python gmail_watcher.py .. --interval 120
```

---

## Gold Tier Features

### 1. Odoo Accounting Integration

**Available Operations:**
- Create invoices
- Record payments
- Manage customers
- Generate revenue reports

**Example: Create Invoice via Approval**

Create file: `Pending_Approval/INVOICE_001.md`

```markdown
---
type: approval_request
action: create_invoice
partner_id: 1
invoice_date: 2026-03-05
items:
  - name: "Web Development Services"
    quantity: 1
    price_unit: 1000
---

Move to /Approved to create invoice in Odoo.
```

### 2. Facebook/Instagram Posting

**Post to Facebook:**

Create file: `Pending_Approval/SOCIAL_FB_001.md`

```markdown
---
type: approval_request
action: post_to_facebook
message: "Exciting news! Our AI Employee just closed a new deal. #Business #Growth"
---

Move to /Approved to post.
```

**Post to Instagram:**

```markdown
---
type: approval_request
action: post_to_instagram
caption: "Behind the scenes at our office! #TeamWork"
image_url: "https://example.com/image.jpg"
---

Move to /Approved to post.
```

### 3. Weekly Accounting Audit

Run manually or schedule:

```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts

# Generate weekly accounting report
python ceo_briefing.py .. --start 2026-02-26 --end 2026-03-05
```

This will:
- Query Odoo for revenue data
- Count completed tasks
- Identify bottlenecks
- Generate CEO Briefing in `Briefings/`

### 4. Error Recovery

The Orchestrator now includes:
- UTF-8 encoding handling
- Graceful error logging
- Continue processing on non-critical errors
- Comprehensive activity logs

### 5. Audit Logging

All activities logged to:
```
AI_Employee_Vault/Logs/YYYY-MM-DD_activity.json
```

Includes:
- Email processing
- MCP server calls
- Odoo operations
- Social media posts
- Errors and recovery

---

## MCP Servers Summary

| Server | Port | Purpose |
|--------|------|---------|
| Email MCP | 8765 | Send emails via Gmail |
| Odoo MCP | 8770 | Accounting/ERP |
| Facebook MCP | 8771 | Social media posting |

---

## Troubleshooting

### Odoo Won't Start

```bash
# Check Docker containers
docker ps -a

# View Odoo logs
docker logs ai-employee-odoo

# Restart Odoo
docker-compose restart
```

### MCP Server Connection Failed

```bash
# Check if server is running
netstat -ano | findstr :8770

# Test connection
curl http://localhost:8770
```

### Facebook Token Expired

1. Generate new token from Graph API Explorer
2. Restart Facebook MCP Server with new token

---

## Gold Tier Checklist

- [ ] Odoo running via Docker
- [ ] Odoo MCP Server started
- [ ] Facebook MCP Server started (optional)
- [ ] Orchestrator running
- [ ] Gmail Watcher running
- [ ] Test invoice creation in Odoo
- [ ] Test Facebook post (optional)
- [ ] Generate first CEO Briefing with Odoo data

---

**Congratulations! Gold Tier Complete!** 🎉

Your AI Employee now has:
- ✅ Email management (Silver)
- ✅ Full ERP integration (Odoo)
- ✅ Social media posting
- ✅ Accounting automation
- ✅ Comprehensive audit logs
- ✅ Error recovery
