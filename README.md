# 🤖 AI Employee FTE - Personal Autonomous AI Assistant

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

[![Gold Tier](https://img.shields.io/badge/Tier-Gold-brightgreen)](https://github.com/HassaanDeveloper/AI-Employee-FTE)
[![Platinum Tier](https://img.shields.io/badge/Tier-Platinum-brightgreen)](https://github.com/HassaanDeveloper/AI-Employee-FTE)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue)](https://www.python.org/downloads/)
[![Qwen Code](https://img.shields.io/badge/AI-Qwen%20Code-orange)](https://github.com/QwenLM/Qwen)
[![Odoo](https://img.shields.io/badge/Odoo-16.0-green)](https://www.odoo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tiers](#-tiers)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Skills](#-skills)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**AI Employee FTE** is a comprehensive, local-first autonomous AI agent system that manages your personal and business affairs 24/7. Built with **Qwen Code** as the reasoning engine and **Obsidian** as the knowledge base, it proactively handles emails, social media, accounting, and more.

### Key Capabilities

- 📧 **Gmail Automation** - Monitor and respond to emails automatically
- 📘 **Facebook Posting** - Auto-post to Facebook Pages
- 💼 **Odoo ERP Integration** - Full accounting and CRM integration
- 📅 **CEO Briefings** - Weekly business intelligence reports
- ✅ **Approval Workflow** - Human-in-the-loop for sensitive actions
- 🔄 **24/7 Cloud Deployment** - Deploy on Odoo.sh or Oracle Cloud

---

## ✨ Features

### Bronze Tier (Foundation)
- ✅ Obsidian vault with Dashboard.md
- ✅ Company Handbook with rules of engagement
- ✅ Filesystem Watcher for drop folder monitoring
- ✅ Gmail Watcher for email monitoring
- ✅ Orchestrator for task processing
- ✅ Human-in-the-loop approval workflow

### Silver Tier (Functional Assistant)
- ✅ All Bronze features plus:
- ✅ Email MCP Server for sending emails
- ✅ Facebook MCP Server for social media posting
- ✅ Plan Generator for action plans
- ✅ Scheduled Tasks (Windows Task Scheduler / cron)
- ✅ CEO Briefing Generator
- ✅ LinkedIn Watcher (optional)

### Gold Tier (Autonomous Employee)
- ✅ All Silver features plus:
- ✅ Odoo Community ERP integration
- ✅ Odoo MCP Server for accounting operations
- ✅ Comprehensive audit logging
- ✅ Error recovery and graceful degradation
- ✅ Ralph Wiggum Loop for persistence
- ✅ Full cross-domain integration

### Platinum Tier (Cloud Deployment)
- ✅ All Gold features plus:
- ✅ Cloud Agent for 24/7 operation
- ✅ Local Agent for approvals
- ✅ Vault sync via Git
- ✅ Security rules (secrets never sync)
- ✅ Health monitoring and auto-restart
- ✅ Work-zone specialization

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    WATCHERS (Senses)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Gmail        │ │ Facebook     │ │ Filesystem   │   │
│  │ Watcher      │ │ Watcher      │ │ Watcher      │   │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘   │
└─────────┼────────────────┼────────────────┼────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR (Brain)                  │
│           Qwen Code + Obsidian Vault + MCP              │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Email MCP    │ │ Facebook MCP │ │ Odoo MCP     │
│ (Send)       │ │ (Post)       │ │ (Accounting) │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🎖 Tiers

| Tier | Time | Description |
|------|------|-------------|
| 🥉 **Bronze** | 8-12 hours | Foundation with basic watchers |
| 🥈 **Silver** | 20-30 hours | Functional assistant with MCP servers |
| 🥇 **Gold** | 40+ hours | Autonomous employee with Odoo |
| 🏆 **Platinum** | 60+ hours | Cloud deployment 24/7 |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Qwen Code installed
- Obsidian (optional, for viewing)
- Gmail API credentials
- Facebook Page Access Token (for social posting)

### 1. Clone Repository

```bash
git clone https://github.com/HassaanDeveloper/AI-Employee-FTE.git
cd AI-Employee-FTE
```

### 2. Install Dependencies

```bash
cd AI_Employee_Vault
pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
# Copy credentials.json to vault root
cp credentials.json AI_Employee_Vault/

# Authorize Gmail API
cd AI_Employee_Vault/scripts
python authorize_gmail.py ../credentials.json
```

### 4. Start AI Employee

```bash
# Terminal 1: Orchestrator
python orchestrator.py .. --interval 30

# Terminal 2: Gmail Watcher
python gmail_watcher.py .. --interval 120
```

---

## 📦 Installation

### Step 1: Install Python Dependencies

```bash
cd AI_Employee_Vault
pip install -r requirements.txt
```

### Step 2: Install Playwright (for Facebook)

```bash
playwright install chromium
```

### Step 3: Setup Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download `credentials.json`
5. Run authorization:

```bash
python authorize_gmail.py credentials.json
```

### Step 4: Setup Facebook (Optional)

1. Go to [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Get Page Access Token
3. Add to `.env` file:

```env
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_access_token
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in vault root:

```env
# Gmail
GMAIL_CREDENTIALS_PATH=credentials.json

# Facebook
FACEBOOK_PAGE_ID=993926910480113
FACEBOOK_ACCESS_TOKEN=your_token_here

# Odoo
ODOO_URL=https://your-company.odoo.com
ODOO_DB=your_db
ODOO_USER=your_email
ODOO_PASSWORD=your_password
```

### Company Handbook

Edit `Company_Handbook.md` to customize rules:

```markdown
## Email Rules
- Always reply to clients within 24 hours
- Flag emails containing "urgent" for immediate attention
- Auto-archive newsletters
```

---

## 📖 Usage

### Start All Services

```bash
# Terminal 1: Email MCP Server
python email-mcp-server.py --vault .. --port 8765

# Terminal 2: Facebook MCP Server
python facebook-mcp-server.py --access-token YOUR_TOKEN --page-id YOUR_PAGE_ID --port 8771

# Terminal 3: Orchestrator
python orchestrator.py .. --interval 30

# Terminal 4: Gmail Watcher
python gmail_watcher.py .. --interval 120
```

### Create Approval Request

Create file in `Pending_Approval/`:

```markdown
---
type: approval_request
action: post_to_facebook
message: "Exciting news! #AI #Automation"
---

Move to /Approved to post.
```

### Generate CEO Briefing

```bash
python ceo_briefing.py .. --start 2026-03-01 --end 2026-03-07
```

---

## 📁 Project Structure

```
AI-Employee-FTE/
├── AI_Employee_Vault/           # Main vault directory
│   ├── scripts/                 # Python scripts
│   │   ├── base_watcher.py     # Base watcher class
│   │   ├── gmail_watcher.py    # Gmail monitor
│   │   ├── orchestrator.py     # Main orchestrator
│   │   └── ...
│   ├── Needs_Action/           # Items to process
│   ├── Done/                   # Completed tasks
│   ├── Pending_Approval/       # Awaiting approval
│   ├── Approved/               # Approved actions
│   ├── Logs/                   # Activity logs
│   ├── Dashboard.md            # Real-time summary
│   ├── Company_Handbook.md     # Rules
│   ├── Business_Goals.md       # Objectives
│   └── requirements.txt        # Python deps
├── PLATINUM_TIER/              # Platinum Tier files
│   ├── cloud_agent.py          # Cloud Agent
│   ├── local_agent.py          # Local Agent
│   └── ODOO_SH_DEPLOYMENT.md   # Deployment guide
├── .qwen/skills/               # Qwen Code skills
│   ├── browsing-with-playwright/
│   ├── email-mcp/
│   ├── facebook-mcp/
│   └── ...
├── credentials.json            # Gmail API creds
└── README.md                   # This file
```

---

## 🛠 Skills

All AI functionality is implemented as [Qwen Code Skills](https://github.com/QwenLM/Qwen):

| Skill | Purpose | Status |
|-------|---------|--------|
| `browsing-with-playwright` | Browser automation | ✅ Complete |
| `email-mcp` | Send emails via Gmail | ✅ Complete |
| `facebook-mcp` | Post to Facebook | ✅ Complete |
| `odoo-mcp` | Odoo ERP integration | ✅ Complete |
| `ceo-briefing-generator` | Weekly reports | ✅ Complete |
| `scheduled-tasks` | Task scheduling | ✅ Complete |

---

## 🌐 Deployment

### Odoo.sh (Recommended - No Credit Card)

1. Go to [Odoo.sh](https://www.odoo.sh/)
2. Start free trial
3. Follow `PLATINUM_TIER/ODOO_SH_DEPLOYMENT.md`

### Oracle Cloud (Requires Credit Card)

1. Go to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Create VM instance
3. Follow `PLATINUM_TIER/ORACLE_CLOUD_DEPLOYMENT.md`

### Local (Free Forever)

Just run the scripts locally - no deployment needed!

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation:** See `PLATINUM_TIER/` folder
- **Issues:** Open an issue on GitHub
- **Email:** hassaan.developer@example.com

---

## 🎉 Acknowledgments

- [Qwen Code](https://github.com/QwenLM/Qwen) for AI reasoning
- [Obsidian](https://obsidian.md/) for knowledge base
- [Odoo](https://www.odoo.com/) for ERP integration
- [Playwright](https://playwright.dev/) for browser automation

---

**Built with ❤️ by Hassaan Developer**

[![GitHub](https://img.shields.io/github/stars/HassaanDeveloper/AI-Employee-FTE?style=social)](https://github.com/HassaanDeveloper/AI-Employee-FTE/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/HassaanDeveloper/AI-Employee-FTE?style=social)](https://github.com/HassaanDeveloper/AI-Employee-FTE/network/members)
