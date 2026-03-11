#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduled Tasks Manager - Create and manage scheduled tasks for AI Employee.

Supports Windows Task Scheduler and cron (Linux/Mac).

Usage:
    python scheduled_tasks.py install --vault C:\path\to\vault
    python scheduled_tasks.py list
    python scheduled_tasks.py remove --all
"""

import sys
import argparse
import subprocess
import platform
from pathlib import Path
from datetime import datetime


class ScheduledTasksManager:
    """Manage scheduled tasks for AI Employee."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.scripts_dir = Path(__file__).parent
        self.is_windows = platform.system() == 'Windows'
    
    def install_all(self):
        """Install all scheduled tasks."""
        print(f"Installing AI Employee scheduled tasks...")
        print(f"Vault: {self.vault_path}")
        print(f"Platform: {'Windows' if self.is_windows else 'Linux/Mac'}")
        print()
        
        if self.is_windows:
            self._install_windows_tasks()
        else:
            self._install_cron_tasks()
    
    def _install_windows_tasks(self):
        """Install Windows Task Scheduler tasks."""
        python_exe = sys.executable
        vault = str(self.vault_path)
        
        tasks = [
            {
                'name': 'AI_Employee_Daily_Briefing',
                'cmd': f'{python_exe} "{self.scripts_dir}\\ceo_briefing.py" {vault}',
                'schedule': 'DAILY',
                'time': '08:00',
                'description': 'Generate daily CEO briefing'
            },
            {
                'name': 'AI_Employee_Weekly_Audit',
                'cmd': f'{python_exe} "{self.scripts_dir}\\weekly_audit.py" {vault}',
                'schedule': 'WEEKLY',
                'day': 'MON',
                'time': '09:00',
                'description': 'Weekly business audit'
            },
            {
                'name': 'AI_Employee_Health_Check',
                'cmd': f'{python_exe} "{self.scripts_dir}\\health_check.py" {vault}',
                'schedule': 'HOURLY',
                'description': 'Check orchestrator health'
            }
        ]
        
        for task in tasks:
            print(f"Creating task: {task['name']}")
            
            # Build schtasks command
            cmd = f'schtasks /Create /TN "{task["name"]}" /TR "{task["cmd"]}" /SC {task["schedule"]}'
            
            if 'time' in task:
                cmd += f' /ST {task["time"]}'
            if 'day' in task:
                cmd += f' /D {task["day"]}'
            
            cmd += ' /RL HIGHEST /F'
            
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✓ Created: {task['name']}")
                else:
                    print(f"  ✗ Failed: {task['name']}")
                    print(f"    Error: {result.stderr}")
            except Exception as e:
                print(f"  ✗ Error: {task['name']} - {e}")
        
        print()
        print("Installation complete!")
        print("Run 'schtasks /Query /TN \"AI_Employee*\"' to verify.")
    
    def _install_cron_tasks(self):
        """Install cron jobs."""
        python_exe = sys.executable
        vault = str(self.vault_path)
        
        cron_entries = [
            f'# AI Employee Daily Briefing - 8 AM daily',
            f'0 8 * * * {python_exe} {self.scripts_dir}/ceo_briefing.py {vault}',
            f'',
            f'# AI Employee Weekly Audit - Monday 9 AM',
            f'0 9 * * 1 {python_exe} {self.scripts_dir}/weekly_audit.py {vault}',
            f'',
            f'# AI Employee Health Check - Every hour',
            f'0 * * * * {python_exe} {self.scripts_dir}/health_check.py {vault}'
        ]
        
        cron_content = '\n'.join(cron_entries)
        
        print("Cron job entries to add:")
        print("-" * 50)
        print(cron_content)
        print("-" * 50)
        print()
        print("To install, run:")
        print(f'  (crontab -l 2>/dev/null; echo "{cron_content}") | crontab -')
        print()
        print("Or manually run 'crontab -e' and add the entries above.")
    
    def list_tasks(self):
        """List all AI Employee scheduled tasks."""
        print("AI Employee Scheduled Tasks:")
        print("=" * 50)
        
        if self.is_windows:
            try:
                result = subprocess.run(
                    'schtasks /Query /TN "AI_Employee*" /FO TABLE',
                    shell=True, capture_output=True, text=True
                )
                print(result.stdout)
            except Exception as e:
                print(f"Error: {e}")
        else:
            try:
                result = subprocess.run(
                    'crontab -l 2>/dev/null | grep -i "ai_employee"',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    print(result.stdout)
                else:
                    print("No AI Employee cron jobs found.")
            except Exception as e:
                print(f"Error: {e}")
    
    def remove_all(self):
        """Remove all AI Employee scheduled tasks."""
        print("Removing AI Employee scheduled tasks...")
        
        if self.is_windows:
            tasks = ['AI_Employee_Daily_Briefing', 'AI_Employee_Weekly_Audit', 'AI_Employee_Health_Check']
            for task in tasks:
                cmd = f'schtasks /Delete /TN "{task}" /F'
                subprocess.run(cmd, shell=True)
                print(f"  Removed: {task}")
        else:
            print("To remove cron jobs, run 'crontab -e' and delete AI Employee entries.")


def main():
    parser = argparse.ArgumentParser(description='Scheduled Tasks Manager')
    parser.add_argument('action', choices=['install', 'list', 'remove'], help='Action to perform')
    parser.add_argument('--vault', default='.', help='Path to vault')
    parser.add_argument('--all', action='store_true', help='Remove all tasks')
    
    args = parser.parse_args()
    
    manager = ScheduledTasksManager(args.vault)
    
    if args.action == 'install':
        manager.install_all()
    elif args.action == 'list':
        manager.list_tasks()
    elif args.action == 'remove':
        manager.remove_all()


if __name__ == '__main__':
    main()
