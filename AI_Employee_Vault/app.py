#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Employee FTE - Web Dashboard for Replit
Share this link with the world!
"""

import gradio as gr
import os
from pathlib import Path
from datetime import datetime

# Vault paths
VAULT_PATH = Path(os.environ.get('VAULT_PATH', '.'))
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
DONE = VAULT_PATH / 'Done'
LOGS = VAULT_PATH / 'Logs'

def get_vault_status():
    """Get current vault status"""
    needs_action_count = len(list(NEEDS_ACTION.glob('*.md'))) if NEEDS_ACTION.exists() else 0
    done_count = len(list(DONE.glob('*.md'))) if DONE.exists() else 0
    
    return f"""
    ### 📊 Vault Status
    
    - **Items in Needs_Action:** {needs_action_count}
    - **Items in Done:** {done_count}
    - **Vault Path:** {VAULT_PATH.absolute()}
    """

def get_recent_activity():
    """Get recent activity from logs"""
    if not LOGS.exists():
        return "No logs found"
    
    log_files = sorted(LOGS.glob('*_activity.json'), reverse=True)[:1]
    if not log_files:
        return "No activity logs"
    
    import json
    try:
        with open(log_files[0], 'r') as f:
            data = json.load(f)
            activities = data.get('activities', [])[-10:]
            
            activity_text = ""
            for activity in activities:
                timestamp = activity.get('timestamp', 'Unknown')
                action = activity.get('action_type', 'Unknown')
                result = activity.get('result', 'Unknown')
                activity_text += f"- [{timestamp}] {action}: {result}\n"
            
            return activity_text if activity_text else "No recent activity"
    except Exception as e:
        return f"Error reading logs: {e}"

def run_watcher():
    """Simulate running a watcher"""
    return """
    ✅ Watcher started!
    
    **Note:** On Replit, watchers run for demo purposes only.
    For 24/7 operation, run locally on your PC.
    
    **To run locally:**
    ```bash
    git clone https://github.com/HassaanDeveloper/AI-Employee-FTE.git
    cd AI-Employee-FTE/AI_Employee_Vault
    pip install -r requirements.txt
    python gmail_watcher.py .. --interval 120
    ```
    """

def create_test_email():
    """Create a test email action file"""
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"DEMO_EMAIL_{timestamp}.md"
    filepath = NEEDS_ACTION / filename
    
    content = f"""---
type: email
from: demo@example.com
subject: Demo Email from Replit
received: {datetime.now().isoformat()}
priority: normal
status: pending
---

# Demo Email

This is a test email created from the Replit demo.

## Suggested Actions

- [ ] Review this demo
- [ ] Check out the full version on GitHub
- [ ] Star the repository!

---
*Created by AI Employee FTE Demo*
"""
    
    filepath.write_text(content, encoding='utf-8')
    
    return f"""
    ✅ Test email created!
    
    **File:** `{filename}`
    **Location:** `Needs_Action/`
    
    In production, this would be processed by the Orchestrator and Qwen Code!
    """

def get_tier_info():
    """Get information about AI Employee tiers"""
    return """
    ## 🏆 AI Employee Tiers
    
    ### 🥉 Bronze Tier (Foundation)
    - ✅ Obsidian vault with Dashboard
    - ✅ Gmail Watcher
    - ✅ Filesystem Watcher
    - ✅ Orchestrator
    
    ### 🥈 Silver Tier (Functional)
    - ✅ All Bronze features
    - ✅ Email MCP Server
    - ✅ Facebook MCP Server
    - ✅ CEO Briefing Generator
    
    ### 🥇 Gold Tier (Autonomous)
    - ✅ All Silver features
    - ✅ Odoo ERP Integration
    - ✅ Comprehensive audit logging
    - ✅ Error recovery
    
    ### 🏆 Platinum Tier (Cloud)
    - ✅ All Gold features
    - ✅ Cloud Agent
    - ✅ Local Agent
    - ✅ Vault sync via Git
    
    **This Demo:** Shows Silver Tier functionality
    **Full Version:** Runs 24/7 on your local PC (FREE!)
    """

# Create Gradio Interface
with gr.Blocks(title="AI Employee FTE", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 AI Employee FTE
    
    **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**
    
    This is a **demo** of the AI Employee FTE system. For full 24/7 operation, run it locally on your PC!
    
    **GitHub:** [github.com/HassaanDeveloper/AI-Employee-FTE](https://github.com/HassaanDeveloper/AI-Employee-FTE)
    """)
    
    with gr.Tab("📊 Dashboard"):
        status_output = gr.Markdown()
        refresh_btn = gr.Button("🔄 Refresh Status")
        refresh_btn.click(fn=get_vault_status, outputs=status_output)
    
    with gr.Tab("📧 Demo Actions"):
        gr.Markdown("""
        ### Try AI Employee Features
        
        Create a test email to see how the system works!
        """)
        demo_output = gr.Textbox(label="Demo Output", lines=10)
        with gr.Row():
            create_email_btn = gr.Button("📧 Create Test Email")
            watcher_btn = gr.Button("▶️ Run Watcher (Demo)")
        
        create_email_btn.click(fn=create_test_email, outputs=demo_output)
        watcher_btn.click(fn=run_watcher, outputs=demo_output)
    
    with gr.Tab("📈 Activity Log"):
        activity_output = gr.Textbox(label="Recent Activity", lines=15)
        refresh_activity_btn = gr.Button("🔄 Refresh Activity")
        refresh_activity_btn.click(fn=get_recent_activity, outputs=activity_output)
    
    with gr.Tab("🏆 Tiers"):
        tier_output = gr.Markdown()
        refresh_tier_btn = gr.Button("🔄 Refresh Tier Info")
        refresh_tier_btn.click(fn=get_tier_info, outputs=tier_output)
    
    gr.Markdown("""
    ---
    
    ## 🚀 Get Started
    
    ### Run Locally (FREE, 24/7)
    
    ```bash
    # Clone repository
    git clone https://github.com/HassaanDeveloper/AI-Employee-FTE.git
    cd AI-Employee-FTE/AI_Employee_Vault
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Configure (add your credentials.json and .env)
    
    # Run
    python orchestrator.py .. --interval 30
    python gmail_watcher.py .. --interval 120
    ```
    
    **Cost:** $0/month forever
    
    ### Share
    
    - **GitHub:** [github.com/HassaanDeveloper/AI-Employee-FTE](https://github.com/HassaanDeveloper/AI-Employee-FTE)
    - **License:** MIT (Open Source)
    - **Made by:** Hassaan Developer
    
    ---
    
    **Built with ❤️ using Gradio + Python + Qwen Code**
    """)

# Load initial data
demo.load(get_vault_status, outputs=status_output)
demo.load(get_recent_activity, outputs=activity_output)
demo.load(get_tier_info, outputs=tier_output)

if __name__ == "__main__":
    # Get host and port from Replit environment
    host = os.environ.get('REPL_HOST', '0.0.0.0')
    port = int(os.environ.get('REPL_PORT', '7860'))
    
    print("🚀 Starting AI Employee FTE Dashboard...")
    print(f"📊 Dashboard URL: https://{host}:{port}")
    print("🌐 Share this URL with the world!")
    
    demo.launch(server_name=host, server_port=port)
