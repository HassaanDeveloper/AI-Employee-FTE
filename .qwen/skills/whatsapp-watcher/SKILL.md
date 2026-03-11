---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for new messages containing urgent keywords.
  Creates action files in Needs_Action folder for Claude/Qwen Code to process.
  Uses Playwright for browser automation. Requires WhatsApp Web session.
---

# WhatsApp Watcher

Monitor WhatsApp Web for urgent messages and create action files for the AI Employee.

## Setup

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. Create WhatsApp Session

First time setup - creates a persistent browser session:

```bash
# Run session creator
python scripts/create-whatsapp-session.py /path/to/vault
```

This opens a browser where you scan the QR code with your WhatsApp app.

### 3. Start the Watcher

```bash
python scripts/whatsapp_watcher.py /path/to/vault --interval 60
```

## How It Works

1. **Monitors** WhatsApp Web every 60 seconds (configurable)
2. **Detects** unread messages with urgent keywords
3. **Creates** action files in `Needs_Action/` folder
4. **Logs** processed messages to prevent duplicates

## Urgent Keywords

Default keywords that trigger action files:
- urgent
- asap
- invoice
- payment
- help
- pricing
- quote

Customize in `scripts/whatsapp_watcher.py` or via `--keywords` flag.

## Usage

```bash
# Basic usage
python scripts/whatsapp_watcher.py /path/to/vault

# Custom check interval (30 seconds)
python scripts/whatsapp_watcher.py /path/to/vault --interval 30

# Custom keywords
python scripts/whatsapp_watcher.py /path/to/vault --keywords "urgent,asap,important"

# Dry-run mode (don't create files, just log)
python scripts/whatsapp_watcher.py /path/to/vault --dry-run
```

## Output Files

Creates files in `Needs_Action/`:

```markdown
---
type: whatsapp
from: +1234567890
contact: John Doe
received: 2026-03-01T10:30:00Z
priority: high
status: pending
keywords: invoice,payment
---

# WhatsApp Message

**From:** John Doe (+1234567890)
**Received:** 2026-03-01 10:30

## Message Content

"Hey, can you send me the invoice for last month?"

## Suggested Actions

- [ ] Read and understand the message
- [ ] Generate and send invoice (requires approval)
- [ ] Reply to sender
- [ ] Mark as done after processing
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code expired | Re-run session creator |
| No messages detected | Check WhatsApp Web is loaded |
| Session not found | Run create-whatsapp-session.py |
| Browser won't open | Run `playwright install chromium` |

## Security Notes

- Session data stored locally in vault
- Never share session files
- Log out from WhatsApp Web when not in use
- Be aware of WhatsApp's terms of service
