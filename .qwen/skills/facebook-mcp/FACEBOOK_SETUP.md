# Facebook MCP Server - Gold Tier Setup Guide

## ✅ Your Facebook App Review is APPROVED!

Your manual test proved it works:
- ✅ Posted to: https://www.facebook.com/pages/993926910480113
- ✅ Post ID: `993926910480113_122095924947074655`
- ✅ Message: "Hello from AI employee"

---

## Quick Start

### Step 1: Get Your Page Access Token

**Go to:** https://developers.facebook.com/tools/explorer/

1. **Select your App**
2. **Click:** "Get Token" → "Get Page Access Token"
3. **Select your Page:** 993926910480113
4. **Allow permissions**
5. **Copy the LONG token** (350+ characters)

### Step 2: Add Token to .env File

**Edit:** `E:\AI-Employee-FTE\AI_Employee_Vault\.env`

Replace `YOUR_PAGE_ACCESS_TOKEN_HERE` with your actual token:

```env
FACEBOOK_PAGE_ID=993926910480113
FACEBOOK_ACCESS_TOKEN=EAANKfSpr4JIBQ... (your full long token)
```

### Step 3: Start Facebook MCP Server

```bash
cd E:\AI-Employee-FTE\.qwen\skills\facebook-mcp\scripts

python facebook-mcp-server.py \
  --access-token YOUR_PAGE_ACCESS_TOKEN \
  --page-id 993926910480113 \
  --port 8771
```

**Expected output:**
```
INFO:Facebook Client initialized for Page: 993926910480113
INFO:Facebook MCP Server running on http://localhost:8771
```

**Keep this terminal open!**

### Step 4: Test the Server

**Open a NEW terminal:**

```bash
cd E:\AI-Employee-FTE\.qwen\skills\facebook-mcp\scripts

python test-facebook.py
```

**Expected output:**
```
[OK] Facebook MCP Server is working!
Found X posts
```

### Step 5: Make a Test Post

```bash
python post-facebook-test.py
```

**Expected output:**
```
[OK] Post published successfully!
Post ID: 993926910480113_xxxxxxxx
```

**Check your Facebook Page!** The post should be live.

---

## Integration with AI Employee

### Automatic Posting via Approval Workflow

#### Step 1: Create Approval Request

Create file: `E:\AI-Employee-FTE\AI_Employee_Vault\Pending_Approval\FB_POST_001.md`

```markdown
---
type: approval_request
action: post_to_facebook
message: "🚀 AI Employee Gold Tier is LIVE! Full automation with email, Odoo, and Facebook posting. #AI #Automation"
---

Move to /Approved to post.
```

#### Step 2: Approve

Move the file to `Approved/` folder:

```bash
move E:\AI-Employee-FTE\AI_Employee_Vault\Pending_Approval\FB_POST_001.md E:\AI-Employee-FTE\AI_Employee_Vault\Approved\
```

#### Step 3: Run Orchestrator

```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts

python orchestrator.py .. --once
```

The orchestrator will:
1. Detect the approved post
2. Call Facebook MCP Server
3. Post to your Facebook Page
4. Move file to `Done/`

---

## Full Gold Tier - All Services Running

### Terminal 1: Odoo MCP Server
```bash
cd E:\AI-Employee-FTE\.qwen\skills\odoo-mcp\scripts
python odoo-mcp-server.py --port 8770 --odoo-url https://hassuu1.odoo.com --odoo-db hassuu1 --odoo-user mohammedhassaan449@gmail.com --odoo-password YOUR_ODOO_PASSWORD
```

### Terminal 2: Email MCP Server
```bash
cd E:\AI-Employee-FTE\.qwen\skills\email-mcp\scripts
python email-mcp-server.py --vault E:\AI-Employee-FTE\AI_Employee_Vault --port 8765
```

### Terminal 3: Facebook MCP Server ⭐
```bash
cd E:\AI-Employee-FTE\.qwen\skills\facebook-mcp\scripts
python facebook-mcp-server.py --access-token YOUR_PAGE_TOKEN --page-id 993926910480113 --port 8771
```

### Terminal 4: Orchestrator
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python orchestrator.py .. --interval 30
```

### Terminal 5: Gmail Watcher
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python gmail_watcher.py .. --interval 120
```

---

## Troubleshooting

### Server won't start

**Check:**
1. Facebook SDK installed: `pip install facebook-sdk`
2. Port 8771 not in use: `netstat -ano | findstr :8771`
3. Token is valid (not expired)

### Getting "Invalid token" error

**Solution:**
1. Token expired - get a new one from Graph API Explorer
2. Make sure it's a Page Access Token (not User Token)
3. Token should be 350+ characters long

### Posts not appearing on Facebook

**Check:**
1. Facebook Page admin permissions
2. Token has `pages_manage_posts` permission
3. Check Facebook Page: https://www.facebook.com/pages/993926910480113

---

## Summary

| Component | Status |
|-----------|--------|
| ✅ Facebook App Review | Approved |
| ✅ Facebook Page | Connected (993926910480113) |
| ✅ MCP Server | Fixed - posts directly to Page ID |
| ✅ Test Posting | Works via Graph API Explorer |
| ⏳ Full Automation | Ready - just add your Page Access Token |

---

**Your Gold Tier Facebook integration is ready!**

**Just add your Page Access Token to .env and start the server!** 🎉
