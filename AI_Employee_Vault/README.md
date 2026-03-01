# AI Employee - Bronze Tier

> **Your Personal AI Employee - Local-First, Agent-Driven Automation**

This is a **Bronze Tier** implementation of the Personal AI Employee hackathon. It provides the foundational layer for autonomous task management using Qwen Code and Obsidian.

## Features (Bronze Tier)

- ✅ **Obsidian Vault** with proper folder structure
- ✅ **Dashboard.md** - Real-time summary of activities
- ✅ **Company Handbook** - Rules of engagement
- ✅ **Business Goals** - Track objectives and metrics
- ✅ **Filesystem Watcher** - Monitors drop folder for new files
- ✅ **Gmail Watcher** - Monitors Gmail for new messages (optional)
- ✅ **Orchestrator** - Triggers Qwen Code to process items
- ✅ **Human-in-the-Loop** - Approval workflow for sensitive actions

## Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | Reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Knowledge base (optional for viewing) |

## Quick Start

### 1. Set Up Python Environment

```bash
# Navigate to vault scripts folder
cd AI_Employee_Vault/scripts

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt
```

### 2. Verify Qwen Code

```bash
# Check Qwen Code is installed
qwen --version

# If not installed, follow installation instructions at:
# https://github.com/QwenLM/Qwen
```

### 3. Start the Orchestrator

```bash
# Run in dry-run mode first (safe test)
python orchestrator.py .. --dry-run --once

# Run continuously (processes items every 30 seconds)
python orchestrator.py .. --interval 30
```

### 4. Start Watchers (Optional)

In separate terminal windows:

```bash
# Filesystem Watcher (monitors Inbox folder)
python filesystem_watcher.py ..

# Gmail Watcher (requires Gmail API setup)
python gmail_watcher.py ..
```

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Objectives and metrics
├── Inbox/                    # Drop folder for new files
├── Needs_Action/             # Items requiring attention
├── Plans/                    # Qwen-generated plans
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions (triggers execution)
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Logs/                     # Activity logs
├── Accounting/               # Financial records
├── Briefings/                # CEO briefings
└── scripts/
    ├── base_watcher.py       # Base watcher class
    ├── gmail_watcher.py      # Gmail monitor
    ├── filesystem_watcher.py # File drop monitor
    └── orchestrator.py       # Master process
```

## How It Works

### Perception → Reasoning → Action Flow

1. **Watcher detects new item** (file dropped in Inbox, new Gmail message)
2. **Creates action file** in `Needs_Action/` folder
3. **Orchestrator picks up** the action file
4. **Qwen Code processes** the item and creates a plan
5. **If approval needed** → Creates file in `Pending_Approval/`
6. **Human reviews** and moves to `Approved/` or `Rejected/`
7. **Action executed** and file moved to `Done/`
8. **Dashboard updated** with completion status

### Example: Processing a Dropped File

```bash
# 1. Drop a file in the Inbox folder
cp document.pdf AI_Employee_Vault/Inbox/

# 2. Filesystem Watcher detects it and creates:
#    Needs_Action/FILE_abc123_document.md

# 3. Orchestrator triggers Qwen Code to process it

# 4. Qwen reads the file, understands the request, and:
#    - Creates a plan in Plans/
#    - Executes actions or requests approval

# 5. After completion, file moves to Done/
```

## Gmail Watcher Setup (Optional)

To enable Gmail monitoring:

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`

### 2. Configure

```bash
# Place credentials.json in vault root
cp ~/Downloads/credentials.json AI_Employee_Vault/

# Run authorization
cd AI_Employee_Vault/scripts
python gmail_watcher.py .. --auth
```

### 3. Start Gmail Watcher

```bash
python gmail_watcher.py .. --interval 120
```

## Orchestrator Commands

```bash
# Run once (test mode)
python orchestrator.py /path/to/vault --once

# Run continuously (default: 30s interval)
python orchestrator.py /path/to/vault --interval 30

# Dry-run mode (log but don't execute)
python orchestrator.py /path/to/vault --dry-run

# Specify model
python orchestrator.py /path/to/vault --model qwen-code
```

## Watcher Commands

```bash
# Filesystem Watcher
python filesystem_watcher.py /path/to/vault --interval 30

# Gmail Watcher
python gmail_watcher.py /path/to/vault --interval 120 --max-results 10
```

## Approval Workflow

For sensitive actions (payments, new contacts, bulk emails):

1. **Qwen creates** `Pending_Approval/ACTION_Description.md`
2. **You review** the file contents
3. **To approve**: Move file to `Approved/` folder
4. **To reject**: Move file to `Rejected/` folder
5. **Orchestrator executes** approved actions automatically

## Logs

Activity logs are stored in `Logs/` folder:

- `YYYY-MM-DD_activity.json` - All orchestrator activities
- `YYYY-MM-DD_processed.json` - Processed item IDs (prevents duplicates)

## Troubleshooting

### Qwen Code not found

```bash
# Verify installation
qwen --version

# Install if needed:
# Follow instructions at https://github.com/QwenLM/Qwen
```

### Watcher not detecting files

```bash
# Check folder permissions
# Ensure Inbox folder exists and is writable

# Run with verbose logging
python filesystem_watcher.py /path/to/vault --interval 10
```

### Gmail API errors

```bash
# Re-authorize
python gmail_watcher.py /path/to/vault --auth

# Check credentials.json is in vault root
# Check token.json was created
```

## Next Steps (Silver Tier)

To upgrade to Silver Tier, add:

- [ ] Second watcher (WhatsApp or LinkedIn)
- [ ] MCP server integration (email sending)
- [ ] Scheduled tasks (cron/Task Scheduler)
- [ ] Weekly CEO Briefing generation
- [ ] Error recovery and retry logic

## Security Notes

- **Never commit** credentials or tokens to version control
- Use `.env` file for sensitive configuration
- Run in `--dry-run` mode when testing new features
- Review all approval requests before approving

## Resources

- [Hackathon Blueprint](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://github.com/QwenLM/Qwen)
- [Obsidian Help](https://help.obsidian.md/)

---

*AI Employee v0.1 - Bronze Tier*
