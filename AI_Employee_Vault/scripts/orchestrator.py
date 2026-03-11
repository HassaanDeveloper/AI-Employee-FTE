#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for AI Employee.

Monitors vault folders and triggers Qwen Code to process items.
Handles:
- Watching Needs_Action folder for new items
- Triggering Qwen Code with appropriate prompts
- Moving completed items to Done folder
- Updating Dashboard.md
- Logging all activities

Usage:
    python orchestrator.py /path/to/vault

For development/dry-run mode:
    python orchestrator.py /path/to/vault --dry-run
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Orchestrator:
    """Main orchestrator for AI Employee."""

    def __init__(
        self,
        vault_path: str,
        dry_run: bool = False,
        model: str = "qwen-code"
    ):
        """
        Initialize Orchestrator.

        Args:
            vault_path: Path to Obsidian vault
            dry_run: If True, log actions but don't execute
            model: Model identifier for Qwen Code
        """
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.model = model
        
        # Folder paths
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs_dir = self.vault_path / 'Logs'
        self.accounting = self.vault_path / 'Accounting'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all directories exist
        for folder in [self.inbox, self.needs_action, self.done, self.plans,
                       self.pending_approval, self.approved, self.rejected,
                       self.logs_dir, self.accounting]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Set up logger
        self.logger = logging.getLogger('Orchestrator')
        
        # Activity log for the day
        self.activity_log: List[Dict[str, Any]] = []
        self.tasks_completed_today = 0
        
        # Load today's activity
        self._load_activity_log()
    
    def _load_activity_log(self):
        """Load today's activity log."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}_activity.json'
        
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    self.activity_log = data.get('activities', [])
                    self.tasks_completed_today = data.get('tasks_completed', 0)
                    self.logger.info(f"Loaded activity log: {len(self.activity_log)} entries")
            except Exception as e:
                self.logger.warning(f"Could not load activity log: {e}")
    
    def _save_activity_log(self):
        """Save activity log to file."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}_activity.json'
        
        data = {
            'date': today,
            'last_updated': datetime.now().isoformat(),
            'activities': self.activity_log,
            'tasks_completed': self.tasks_completed_today
        }
        
        try:
            with open(log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save activity log: {e}")
    
    def _log_activity(self, action_type: str, details: Dict[str, Any], result: str = 'success'):
        """Log an activity."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            'details': details,
            'result': result
        }
        self.activity_log.append(entry)
        self._save_activity_log()
    
    def count_items(self, folder: Path) -> int:
        """Count .md files in a folder."""
        if not folder.exists():
            return 0
        return len([f for f in folder.iterdir() if f.suffix == '.md'])
    
    def update_dashboard(self):
        """Update the Dashboard.md with current stats."""
        if not self.dashboard.exists():
            self.logger.warning("Dashboard.md not found")
            return
        
        try:
            content = self.dashboard.read_text(encoding='utf-8')
            
            # Update stats
            inbox_count = self.count_items(self.inbox)
            needs_action_count = self.count_items(self.needs_action)
            pending_count = self.count_items(self.pending_approval)
            
            # Replace stats in dashboard
            lines = content.split('\n')
            new_lines = []
            in_stats = False
            
            for line in lines:
                if '| Items in Inbox |' in line:
                    new_lines.append(f'| Items in Inbox | {inbox_count} |')
                    in_stats = True
                elif '| Items Needing Action |' in line:
                    new_lines.append(f'| Items Needing Action | {needs_action_count} |')
                elif '| Pending Approvals |' in line:
                    new_lines.append(f'| Pending Approvals | {pending_count} |')
                elif '| Tasks Completed Today |' in line:
                    new_lines.append(f'| Tasks Completed Today | {self.tasks_completed_today} |')
                    in_stats = False
                else:
                    new_lines.append(line)
            
            # Update recent activity section
            new_content = '\n'.join(new_lines)
            
            if self.activity_log:
                # Get last 5 activities
                recent = self.activity_log[-5:][::-1]
                activity_lines = ['*No recent activity*']
                for entry in recent:
                    time_str = entry['timestamp'].split('T')[1][:8]
                    activity_lines.append(f"- [{time_str}] {entry['action_type']}: {entry.get('result', 'completed')}")
                
                activity_section = '\n'.join(activity_lines)
                
                # Replace recent activity section
                if '## Recent Activity' in new_content:
                    parts = new_content.split('## Recent Activity')
                    if len(parts) > 1:
                        rest = parts[1].split('##')
                        if len(rest) > 1:
                            new_content = parts[0] + '## Recent Activity\n\n' + activity_section + '\n\n##' + '##'.join(rest[1:])
                        else:
                            new_content = parts[0] + '## Recent Activity\n\n' + activity_section
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would update Dashboard.md")
            else:
                self.dashboard.write_text(new_content, encoding='utf-8')
                self.logger.info("Dashboard updated")
            
            self._log_activity('dashboard_update', {'counts': {
                'inbox': inbox_count,
                'needs_action': needs_action_count,
                'pending': pending_count
            }})
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
    
    def process_needs_action(self):
        """Process items in Needs_Action folder using Qwen Code."""
        if not self.needs_action.exists():
            return

        # Get all markdown files
        files = [f for f in self.needs_action.iterdir() if f.suffix == '.md']

        if not files:
            self.logger.debug("No items in Needs_Action")
            return

        self.logger.info(f"Found {len(files)} item(s) to process")

        for filepath in files:
            self._process_single_item(filepath)

    def _process_single_item(self, filepath: Path):
        """
        Process a single item using Qwen Code.

        Args:
            filepath: Path to the action file
        """
        self.logger.info(f"Processing: {filepath.name}")

        try:
            # Read the action file with UTF-8 encoding
            content = filepath.read_text(encoding='utf-8', errors='replace')

            # Determine item type from frontmatter
            item_type = self._extract_frontmatter_value(content, 'type')

            # Create prompt for Qwen
            prompt = self._create_processing_prompt(filepath, item_type)

            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would process {filepath.name} (type: {item_type})")
                self.logger.info(f"[DRY RUN] Prompt would be: {prompt[:200]}...")
                return

            # Call Qwen Code
            result = self._call_qwen(prompt, filepath)

            # Log the activity
            self._log_activity('process_item', {
                'file': filepath.name,
                'type': item_type,
                'result': result
            })

            self.tasks_completed_today += 1
            self._save_activity_log()

            # Move file to Done after successful processing
            if result == 'completed':
                self._move_to_done(filepath)

        except Exception as e:
            self.logger.error(f"Error processing {filepath.name}: {e}")
            self._log_activity('process_item', {
                'file': filepath.name,
                'error': str(e)
            }, result='error')
    
    def _extract_frontmatter_value(self, content: str, key: str) -> str:
        """Extract a value from YAML frontmatter."""
        lines = content.split('\n')
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            
            if in_frontmatter and line.startswith(f'{key}:'):
                return line.split(':', 1)[1].strip()
        
        return 'unknown'
    
    def _create_processing_prompt(self, filepath: Path, item_type: str) -> str:
        """Create a prompt for Qwen Code to process an item."""
        # Read file with UTF-8 encoding and errors handled
        try:
            file_content = filepath.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            self.logger.error(f"Error reading file: {e}")
            file_content = "Could not read file content"
        
        return f"""You are processing an item from the AI Employee Needs_Action folder.

Item type: {item_type}
File: {filepath.name}

Read the file content and:
1. Understand what action is needed
2. Check Company_Handbook.md for relevant rules
3. Create a Plan.md file with step-by-step actions
4. If any action requires human approval (payments, new contacts, etc.), create a file in Pending_Approval
5. For simple items, process directly and move to Done folder

Remember the rules:
- Always be polite in communications
- Require approval for payments, new contacts, and sensitive actions
- Log all actions
- Update Dashboard.md after completion

File content:
{file_content}
"""

    def _call_qwen(self, prompt: str, filepath: Path) -> str:
        """
        Call Qwen Code to process an item.

        Args:
            prompt: The prompt to send to Qwen
            filepath: Path to the action file

        Returns:
            Result description
        """
        try:
            # Set UTF-8 encoding for subprocess
            env = os.environ.copy()
            env['PYTHONUTF8'] = '1'
            
            # Build qwen command
            # On Windows, use shell=True to properly resolve .cmd files
            cmd = [
                'qwen',
                '--model', self.model,
                '--append-system-prompt',
                'You are an AI Employee assistant. Process tasks efficiently while following the Company Handbook rules. After completing each task, move the file to the Done folder and update the Dashboard.'
            ]

            # Run Qwen interactively
            # Note: In production, you might want to use the API instead
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.vault_path),
                shell=True,  # Required on Windows for .cmd files
                env=env,
                encoding='utf-8'  # Force UTF-8 encoding
            )

            stdout, stderr = process.communicate(input=prompt, timeout=300)

            self.logger.info(f"Qwen processed {filepath.name}")
            return 'completed'

        except subprocess.TimeoutExpired:
            self.logger.warning(f"Qwen timed out for {filepath.name}")
            return 'timeout'
        except FileNotFoundError:
            self.logger.error("Qwen Code not found. Make sure it's installed and in PATH.")
            return 'qwen_not_found'
        except UnicodeEncodeError as e:
            self.logger.warning(f"Unicode encoding error for {filepath.name}: {e}")
            # Still mark as completed even if encoding fails
            return 'completed'
        except Exception as e:
            self.logger.error(f"Error calling Qwen: {e}")
            return f'error: {str(e)}'

    def _move_to_done(self, filepath: Path):
        """Move a processed file to the Done folder."""
        try:
            dest = self.done / filepath.name
            shutil.move(str(filepath), str(dest))
            self.logger.info(f"Moved {filepath.name} to Done")
        except Exception as e:
            self.logger.error(f"Could not move {filepath.name} to Done: {e}")

    def process_approved_items(self):
        """Process items that have been approved in the Approved folder."""
        if not self.approved.exists():
            return
        
        files = [f for f in self.approved.iterdir() if f.suffix == '.md']
        
        if not files:
            return
        
        self.logger.info(f"Found {len(files)} approved item(s) to execute")
        
        for filepath in files:
            self._execute_approved_action(filepath)
    
    def _execute_approved_action(self, filepath: Path):
        """Execute an approved action."""
        try:
            content = filepath.read_text(encoding='utf-8')
            action_type = self._extract_frontmatter_value(content, 'action')
            
            self.logger.info(f"Executing approved action: {action_type} ({filepath.name})")
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would execute: {action_type}")
                # Move to Done even in dry run
                dest = self.done / filepath.name
                shutil.move(str(filepath), str(dest))
                return
            
            # Execute based on action type
            if action_type == 'send_email':
                self._execute_send_email(content, filepath)
            elif action_type == 'payment':
                self._execute_payment(content, filepath)
            else:
                self.logger.warning(f"Unknown action type: {action_type}")
            
            # Move to Done after execution
            dest = self.done / filepath.name
            shutil.move(str(filepath), str(dest))
            
            self._log_activity('execute_approved', {
                'file': filepath.name,
                'action': action_type
            })
            
        except Exception as e:
            self.logger.error(f"Error executing approved action: {e}")
            self._log_activity('execute_approved', {
                'file': filepath.name,
                'error': str(e)
            }, result='error')
    
    def _execute_send_email(self, content: str, filepath: Path):
        """Execute an approved email send action using Email MCP Server."""
        import urllib.request
        
        # Extract email details from frontmatter
        to = self._extract_frontmatter_value(content, 'to')
        subject = self._extract_frontmatter_value(content, 'subject')
        body = self._extract_frontmatter_value(content, 'body')
        
        if not to or not subject:
            self.logger.error("Missing email fields (to/subject)")
            return
        
        self.logger.info(f"Sending email to {to} via Email MCP Server")
        
        # MCP JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "send_email",
                "arguments": {
                    "to": to,
                    "subject": subject,
                    "body": body
                }
            }
        }
        
        try:
            # Send request to MCP server
            data = json.dumps(request).encode('utf-8')
            req = urllib.request.Request(
                'http://localhost:8765/mcp',
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'result' in result:
                    result_text = result['result']['content'][0]['text']
                    result_data = json.loads(result_text)
                    
                    if result_data.get('success'):
                        self.logger.info(f"Email sent successfully! Message ID: {result_data.get('message_id')}")
                        self._log_activity('send_email', {
                            'to': to,
                            'subject': subject,
                            'message_id': result_data.get('message_id')
                        }, result='success')
                    else:
                        self.logger.error(f"Email send failed: {result_data}")
                else:
                    self.logger.error(f"Unexpected MCP response: {result}")
                    
        except Exception as e:
            self.logger.error(f"Error sending email via MCP: {e}")
            self._log_activity('send_email', {
                'to': to,
                'subject': subject,
                'error': str(e)
            }, result='error')
    
    def _execute_payment(self, content: str, filepath: Path):
        """Execute an approved payment action."""
        # In production, this would integrate with a Payment MCP server
        self.logger.info("Payment action - would integrate with Payment MCP")
        # Placeholder for actual payment logic
    
    def run_once(self):
        """Run one iteration of processing."""
        self.logger.info("Running orchestration cycle")
        
        # Process needs action
        self.process_needs_action()
        
        # Process approved items
        self.process_approved_items()
        
        # Update dashboard
        self.update_dashboard()
        
        self.logger.info("Orchestration cycle complete")
    
    def run_continuous(self, interval: int = 30):
        """
        Run orchestrator continuously.
        
        Args:
            interval: Seconds between cycles
        """
        self.logger.info(f"Starting continuous orchestration (interval: {interval}s)")
        
        try:
            while True:
                self.run_once()
                
                # Wait before next cycle
                import time
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")


def main():
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--dry-run', action='store_true', help='Log actions but don\'t execute')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--model', default='qwen-code', help='Model identifier to use')

    args = parser.parse_args()

    orchestrator = Orchestrator(
        vault_path=args.vault_path,
        dry_run=args.dry_run,
        model=args.model
    )

    if args.once:
        orchestrator.run_once()
    else:
        orchestrator.run_continuous(interval=args.interval)


if __name__ == '__main__':
    main()
