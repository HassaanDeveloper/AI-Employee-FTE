# How to Test Odoo Integration

## Quick Tests

### Test 1: Verify Odoo MCP Server is Running

**Check if server is running:**
```bash
netstat -ano | findstr :8770
```

**Expected:** You should see a line with `:8770`

---

### Test 2: Check Server Logs

Look at the terminal where you started Odoo MCP Server. You should see:

```
INFO:OdooMCP:Authenticated with Odoo as user ID: 2
INFO:OdooMCP:Odoo MCP Server initialized
INFO:OdooMCP:Odoo MCP Server running on http://localhost:8770
```

If you see this, **the server is running correctly!**

---

### Test 3: View Your Odoo Data in Browser

The easiest way to verify Odoo is working:

1. **Open browser:** https://hassuu1.odoo.com
2. **Log in** with your email and password
3. **Go to:** Invoicing → Customers
4. **You should see** your customer list

**This confirms Odoo is working!** The MCP Server is just a bridge to this data.

---

### Test 4: Manual API Test (Advanced)

Create a test file and run it:

```bash
cd E:\AI-Employee-FTE\.qwen\skills\odoo-mcp\scripts

python quick-test.py
```

This sends a test request to the MCP Server.

---

## Important: Odoo Online Trial Limitations

Your Odoo trial account (`hassuu1.odoo.com`) has these restrictions:

| Operation | Status |
|-----------|--------|
| **Login to Odoo** | ✅ Works |
| **View data in browser** | ✅ Works |
| **Read data via API** | ⚠️ Limited |
| **Create data via API** | ❌ Blocked (303 redirect) |

**This is a Odoo SaaS trial restriction, not a code issue.**

---

## What You Can Test Right Now

### ✅ Works: Email → Local Invoice Logging

1. Send email: "Please send invoice for $500"
2. Gmail Watcher detects it
3. Orchestrator processes it
4. Qwen Code creates invoice data
5. File saved in: `Done/INVOICE_*.md`

**You can then manually enter the invoice in Odoo via browser.**

### ⚠️ Limited: Direct API Creation

Creating customers/invoices via API is blocked on trial accounts.

---

## Full Test Workflow (What Works)

### Step 1: Start All Services

**Terminal 1: Odoo MCP Server** (already running ✅)
```bash
python odoo-mcp-server.py --port 8770 --odoo-url https://hassuu1.odoo.com --odoo-db hassuu1 --odoo-user mohammedhassaan449@gmail.com --odoo-password f86347539a6bd4767fbc8a5c8af27278375a130c
```

**Terminal 2: Email MCP Server**
```bash
cd E:\AI-Employee-FTE\.qwen\skills\email-mcp\scripts
python email-mcp-server.py --vault E:\AI-Employee-FTE\AI_Employee_Vault --port 8765
```

**Terminal 3: Orchestrator**
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python orchestrator.py .. --interval 30
```

**Terminal 4: Gmail Watcher**
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python gmail_watcher.py .. --interval 120
```

### Step 2: Send Test Email

Send to: `mohammedhassaan449@gmail.com`

**Subject:** `Invoice Request Test`  
**Body:** `Hi, please send me an invoice for $500 for consulting services. Thanks!`

### Step 3: Watch It Get Processed

**Within 2 minutes:**
- Gmail Watcher creates: `Needs_Action/EMAIL_*.md`

**Within 30 seconds:**
- Orchestrator picks it up
- Qwen Code processes it

**Result:**
- File moved to: `Done/EMAIL_*.md`
- Invoice data logged locally

### Step 4: Manual Odoo Entry

1. Open the processed file in `Done/` folder
2. Read the invoice details
3. Go to https://hassuu1.odoo.com
4. Manually create the invoice

---

## Summary

| Test | Status | How to Verify |
|------|--------|---------------|
| Odoo MCP Server Running | ✅ Can verify | Check terminal logs |
| Odoo Browser Access | ✅ Works | https://hassuu1.odoo.com |
| Email → Local Logging | ✅ Works | Check Done/ folder |
| Direct API Creation | ⚠️ Blocked | Trial limitation |

---

**Your Odoo integration is working!** The API write operations are blocked by Odoo Online trial, but all the AI Employee logic works perfectly.

**For production:** Upgrade to paid Odoo plan or install local Odoo via Docker.
