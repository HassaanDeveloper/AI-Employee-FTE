# Silver Tier Setup Guide

## Overview

Silver Tier adds the following capabilities to your AI Employee:

1. **Gmail Watcher** - Monitors Gmail for new messages
2. **LinkedIn Watcher** - Monitors LinkedIn for notifications
3. **Plan Generator** - Creates action plans for tasks
4. **Scheduled Tasks** - Windows Task Scheduler integration
5. **CEO Briefing Generator** - Weekly business reports

## Prerequisites

Make sure you have:
- Python 3.13+ installed
- Qwen Code installed and working
- AI Employee Vault set up (Bronze Tier complete)

## Step 1: Install Dependencies

```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault

# Install all required packages
pip install -r requirements.txt
```

## Step 2: Setup Gmail Watcher

### 2.1 Verify credentials.json

Make sure `credentials.json` from Google Cloud Console is in the vault root:

```
AI_Employee_Vault/
├── credentials.json    ← Must be here
├── scripts/
└── ...
```

### 2.2 Authorize Gmail API

Run the authorization script:

```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts

# This will open a browser window
python authorize_gmail.py ..\credentials.json
```

**What happens:**
1. Browser opens to Google login
2. Log in with your Gmail account
3. Grant permissions to read/send emails
4. Token is saved as `token.json` in vault root

**Expected output:**
```
✓ Authorization successful!
✓ Connected to: your-email@gmail.com
```

### 2.3 Test Gmail Watcher

```bash
# Run in dry-run mode first
python gmail_watcher.py .. --dry-run --interval 30

# If no errors, run for real
python gmail_watcher.py .. --interval 120
```

## Step 3: Setup LinkedIn Watcher

### 3.1 Create LinkedIn Session

```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts

# Create session (opens browser for login)
python linkedin_watcher.py .. --create-session
```

**What happens:**
1. Browser opens to LinkedIn login
2. Log in to your LinkedIn account
3. Wait for feed to load
4. Close the browser

### 3.2 Test LinkedIn Watcher

```bash
# Run in dry-run mode
python linkedin_watcher.py .. --dry-run --interval 60

# Run for real (checks every 5 minutes)
python linkedin_watcher.py .. --interval 300
```

## Step 4: Setup Plan Generator

The Plan Generator is automatically used by the Orchestrator. Test it:

```bash
# Create a test plan
python plan_generator.py .. --task "Process client invoice request"
```

Check `Plans/` folder for the generated plan.

## Step 5: Setup Scheduled Tasks (Windows)

### 5.1 Install Scheduled Tasks

```bash
python scheduled_tasks.py install --vault ..
```

This creates:
- **Daily Briefing** - 8:00 AM every day
- **Weekly Audit** - Monday 9:00 AM
- **Health Check** - Every hour

### 5.2 Verify Tasks

```bash
# List all AI Employee tasks
python scheduled_tasks.py list --vault ..
```

### 5.3 Manual Test - Generate CEO Briefing

```bash
python ceo_briefing.py ..
```

Check `Briefings/` folder for the generated report.

## Step 6: Start All Watchers

Open **separate terminal windows** for each:

### Terminal 1: Orchestrator
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python orchestrator.py .. --interval 30
```

### Terminal 2: Gmail Watcher
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python gmail_watcher.py .. --interval 120
```

### Terminal 3: LinkedIn Watcher
```bash
cd E:\AI-Employee-FTE\AI_Employee_Vault\scripts
python linkedin_watcher.py .. --interval 300
```

## Verification Checklist

- [ ] Gmail authorization successful
- [ ] Gmail Watcher creates files in `Needs_Action/`
- [ ] LinkedIn session created
- [ ] LinkedIn Watcher creates files in `Needs_Action/`
- [ ] Orchestrator processes files and moves to `Done/`
- [ ] Dashboard.md is updated
- [ ] Scheduled tasks installed (optional)

## Troubleshooting

### Gmail Watcher Issues

**"Credentials file not found"**
- Make sure `credentials.json` is in vault root
- Check file name is exactly `credentials.json`

**"Token expired"**
- Re-run: `python authorize_gmail.py ..\credentials.json`

**"Gmail API not available"**
- Run: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

### LinkedIn Watcher Issues

**"Session not found"**
- Run: `python linkedin_watcher.py .. --create-session`

**"Playwright not installed"**
- Run: `pip install playwright`
- Run: `playwright install chromium`

### General Issues

**"Module not found"**
- Activate virtual environment if using one
- Run: `pip install -r requirements.txt`

**Watcher not creating files**
- Check `Needs_Action/` folder exists
- Run with `--dry-run` to test
- Check logs in `Logs/` folder

## Next Steps

After Silver Tier is working:

1. **Monitor** the `Needs_Action/` folder for new items
2. **Review** action files created by watchers
3. **Approve** sensitive actions by moving files to `Approved/`
4. **Check** Dashboard.md for activity summary
5. **Read** CEO Briefings in `Briefings/` folder

## Gold Tier Preview

To upgrade to Gold Tier, you'll add:
- Odoo accounting integration
- Facebook/Instagram posting
- Twitter (X) integration
- Ralph Wiggum loop for persistence
- Comprehensive error recovery

---

*AI Employee v0.2 - Silver Tier*
