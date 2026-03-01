# AI-Employee-FTE Project Context

## Project Overview

This is a **hackathon project** for building a "Personal AI Employee" (Digital FTE - Full-Time Equivalent) - an autonomous AI agent system that manages personal and business affairs 24/7. The project uses **Claude Code** as the reasoning engine and **Obsidian** (local Markdown) as the dashboard/memory.

**Core Concept:** A local-first, agent-driven automation system where lightweight Python "Watcher" scripts monitor inputs (Gmail, WhatsApp, filesystems) and trigger Claude Code to reason and act via MCP (Model Context Protocol) servers.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   WATCHERS      │────▶│  CLAUDE CODE    │────▶│   MCP SERVERS   │
│ (Python Scripts)│     │  (Reasoning)    │     │ (Actions)       │
│ - Gmail         │     │  - Reads vault  │     │ - Browser       │
│ - WhatsApp      │     │  - Creates plans│     │ - Email         │
│ - Filesystem    │     │  - Ralph Loop   │     │ - Calendar      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   OBSIDIAN      │
                        │   (Vault/GUI)   │
                        │ - Dashboard.md  │
                        │ - Needs_Action/ │
                        │ - Done/         │
                        └─────────────────┘
```

## Key Components

### 1. Watchers (Perception Layer)
Lightweight Python scripts that run continuously, monitoring various inputs:
- **Gmail Watcher:** Monitors unread/important emails
- **WhatsApp Watcher:** Uses Playwright to monitor WhatsApp Web
- **Filesystem Watcher:** Watches drop folders for new files

### 2. Ralph Wiggum Loop (Persistence)
A Stop hook pattern that keeps Claude Code working autonomously until tasks are complete by re-injecting prompts when the agent tries to exit prematurely.

### 3. MCP Servers (Action Layer)
Model Context Protocol servers provide Claude with "hands" to interact with external systems:
- **Playwright MCP:** Browser automation (navigate, click, fill forms, screenshots)
- **Email MCP:** Send/draft/search emails
- **Browser MCP:** Web automation for payment portals, etc.

### 4. Human-in-the-Loop (HITL)
For sensitive actions, Claude writes approval request files to `/Pending_Approval/` instead of acting directly. User moves files to `/Approved/` to trigger actions.

## Directory Structure

```
AI-Employee-FTE/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json          # Skill version tracking
├── .qwen/skills/
│   └── browsing-with-playwright/
│       ├── SKILL.md          # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool schemas
│       └── scripts/
│           ├── mcp-client.py      # Universal MCP client (HTTP + stdio)
│           ├── start-server.sh    # Start Playwright MCP server
│           ├── stop-server.sh     # Stop Playwright MCP server
│           └── verify.py          # Server health check
└── .gitattributes
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts |
| Node.js | v24+ LTS | MCP servers |

### Playwright MCP Server

```bash
# Start server (port 8808)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py list \
  --url http://localhost:8808

# Call a tool (navigate)
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  --url http://localhost:8808 \
  --tool browser_navigate \
  --params '{"url": "https://example.com"}'

# Take screenshot
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  --url http://localhost:8808 \
  --tool browser_take_screenshot \
  --params '{"type": "png", "fullPage": true}'

# Get page snapshot (accessibility tree)
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  --url http://localhost:8808 \
  --tool browser_snapshot \
  --params '{}'
```

### Common Browser Automation Workflow

```bash
# 1. Navigate
mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# 2. Get snapshot to find element refs
mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'

# 3. Click element (using ref from snapshot)
mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Submit button", "ref": "e42"}'

# 4. Type text
mcp-client.py call -u http://localhost:8808 -t browser_type \
  -p '{"element": "Search input", "ref": "e15", "text": "hello", "submit": true}'

# 5. Wait for condition
mcp-client.py call -u http://localhost:8808 -t browser_wait_for \
  -p '{"text": "Success"}'
```

## Development Conventions

### Obsidian Vault Structure

```
Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1/Q2 objectives
├── Inbox/                    # New items to process
├── Needs_Action/             # Items requiring attention
├── In_Progress/<agent>/      # Claimed by specific agent
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions (triggers execution)
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Plans/                    # Claude-generated plans
├── Briefings/                # CEO briefings
└── Accounting/               # Bank transactions
```

### Agent Skills Pattern

All AI functionality should be implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - reusable, modular components that Claude can invoke.

### Watcher Pattern

All watchers follow the `BaseWatcher` abstract class:

```python
class BaseWatcher(ABC):
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        '''Main loop'''
```

### Approval Workflow

For sensitive actions (payments, sending emails):

1. Claude writes to `/Pending_Approval/ACTION_Description_Date.md`
2. User reviews and moves file to `/Approved/` or `/Rejected/`
3. Orchestrator detects approved files and triggers MCP actions
4. Results logged to `/Done/`

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_...md` | Complete architectural blueprint with templates |
| `skills-lock.json` | Tracks installed skill versions |
| `mcp-client.py` | Universal MCP client supporting HTTP and stdio transports |
| `SKILL.md` | Playwright browser automation skill documentation |
| `playwright-tools.md` | Complete MCP tool schema reference (22 tools) |

## Hackathon Tiers

| Tier | Requirements | Estimated Time |
|------|--------------|----------------|
| **Bronze** | Obsidian vault, 1 watcher, Claude reading/writing | 8-12 hours |
| **Silver** | 2+ watchers, MCP server, HITL workflow, scheduling | 20-30 hours |
| **Gold** | Full integration, Odoo accounting, Ralph loop, audit logging | 40+ hours |
| **Platinum** | Cloud deployment, domain specialization, A2A upgrade | 60+ hours |

## Troubleshooting

### Playwright MCP Server Issues

```bash
# Check if server is running
pgrep -f "@playwright/mcp"

# Restart server
bash scripts/stop-server.sh && bash scripts/start-server.sh

# Check port 8808 is available
netstat -ano | findstr :8808
```

### Common Browser Automation Errors

| Error | Solution |
|-------|----------|
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Form not submitting | Use `"submit": true` with `browser_type` |
| Server not responding | Restart: `stop-server.sh && start-server.sh` |

## Resources

- [Claude Code Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Ralph Wiggum Stop Hook](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [MCP Server Documentation](https://modelcontextprotocol.io/)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
