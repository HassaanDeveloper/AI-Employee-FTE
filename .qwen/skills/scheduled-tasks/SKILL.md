---
name: scheduled-tasks
description: |
  Schedule recurring tasks for the AI Employee using Windows Task Scheduler
  or cron (Linux/Mac). Automate daily briefings, weekly audits, and
  periodic cleanups.
---

# Scheduled Tasks

Schedule recurring AI Employee operations.

## Windows Setup

### Create Scheduled Task

```powershell
# Daily Briefing at 8:00 AM
schtasks /Create /TN "AI_Employee_Daily_Briefing" /TR "python C:\path\to\ceo_briefing.py C:\path\to\vault" /SC DAILY /ST 08:00

# Weekly Audit every Monday at 9:00 AM
schtasks /Create /TN "AI_Employee_Weekly_Audit" /TR "python C:\path\to\weekly_audit.py C:\path\to\vault" /SC WEEKLY /D MON /ST 09:00

# Hourly orchestrator health check
schtasks /Create /TN "AI_Employee_Health_Check" /TR "python C:\path\to\health_check.py C:\path\to\vault" /SC HOURLY
```

### Manage Tasks

```powershell
# List all AI Employee tasks
schtasks /Query /TN "AI_Employee*"

# Run task manually
schtasks /Run /TN "AI_Employee_Daily_Briefing"

# Delete task
schtasks /Delete /TN "AI_Employee_Daily_Briefing" /F
```

## Linux/Mac Setup

### Create Cron Jobs

```bash
# Edit crontab
crontab -e

# Add entries:
# Daily briefing at 8 AM
0 8 * * * /usr/bin/python3 /path/to/ceo_briefing.py /path/to/vault

# Weekly audit every Monday 9 AM
0 9 * * 1 /usr/bin/python3 /path/to/weekly_audit.py /path/to/vault

# Hourly health check
0 * * * * /usr/bin/python3 /path/to/health_check.py /path/to/vault
```

### Manage Cron Jobs

```bash
# List cron jobs
crontab -l

# Edit cron jobs
crontab -e

# Remove all cron jobs
crontab -r
```

## Scheduled Operations

| Task | Frequency | Purpose |
|------|-----------|---------|
| Daily Briefing | Daily 8 AM | Generate CEO briefing |
| Weekly Audit | Weekly Monday | Business performance review |
| Health Check | Hourly | Verify watchers running |
| Log Cleanup | Weekly | Archive old logs |
| Subscription Audit | Monthly | Review software costs |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check user permissions |
| Python not found | Use full path to python.exe |
| Access denied | Run as administrator |
| Task runs but fails | Check working directory |
