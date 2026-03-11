#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO Briefing Generator - Generate weekly business intelligence reports.

Analyzes completed tasks, revenue, bottlenecks, and provides
proactive suggestions for the "Monday Morning CEO Briefing".

Usage:
    python ceo_briefing.py /path/to/vault
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict


class CEOBriefingGenerator:
    """Generate CEO Briefing reports."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        self.accounting_folder = self.vault_path / 'Accounting'
        self.briefings_folder = self.vault_path / 'Briefings'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.business_goals = self.vault_path / 'Business_Goals.md'
        
        self.briefings_folder.mkdir(parents=True, exist_ok=True)
    
    def generate_briefing(self, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          preview: bool = False) -> Path:
        """
        Generate CEO Briefing for date range.
        
        Args:
            start_date: Start of period (default: 7 days ago)
            end_date: End of period (default: today)
            preview: If True, print to stdout without saving
            
        Returns:
            Path to generated briefing file
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # Collect data
        completed_tasks = self._get_completed_tasks(start_date, end_date)
        revenue = self._calculate_revenue(start_date, end_date)
        bottlenecks = self._identify_bottlenecks(start_date, end_date)
        suggestions = self._generate_suggestions()
        
        # Generate content
        content = self._create_briefing_content(
            start_date=start_date,
            end_date=end_date,
            completed_tasks=completed_tasks,
            revenue=revenue,
            bottlenecks=bottlenecks,
            suggestions=suggestions
        )
        
        if preview:
            print(content)
            return None
        
        # Save briefing
        filename = f"{end_date.strftime('%Y-%m-%d')}_CEO_Briefing.md"
        filepath = self.briefings_folder / filename
        filepath.write_text(content, encoding='utf-8')
        
        # Update dashboard
        self._update_dashboard(filepath)
        
        return filepath
    
    def _get_completed_tasks(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get tasks completed in date range."""
        tasks = []
        
        if not self.done_folder.exists():
            return tasks
        
        for filepath in self.done_folder.iterdir():
            if filepath.suffix != '.md':
                continue
            
            try:
                content = filepath.read_text(encoding='utf-8')
                
                # Try to extract date from content or file modified time
                file_date = datetime.fromtimestamp(filepath.stat().st_mtime)
                
                if start_date <= file_date <= end_date:
                    # Extract task info
                    task_type = 'unknown'
                    for line in content.split('\n')[:20]:
                        if line.startswith('type:'):
                            task_type = line.split(':')[1].strip()
                            break
                    
                    tasks.append({
                        'file': filepath.name,
                        'type': task_type,
                        'completed_at': file_date.isoformat()
                    })
            except Exception as e:
                continue
        
        return tasks
    
    def _calculate_revenue(self, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate revenue for period."""
        revenue = {
            'this_week': 0.0,
            'mtd': 0.0,
            'transactions': []
        }
        
        # Check activity logs for transaction data
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if self.logs_folder.exists():
            for log_file in self.logs_folder.glob('*_activity.json'):
                try:
                    with open(log_file, 'r') as f:
                        data = json.load(f)
                    
                    for activity in data.get('activities', []):
                        if activity.get('action_type') == 'transaction':
                            details = activity.get('details', {})
                            amount = details.get('amount', 0)
                            timestamp = datetime.fromisoformat(activity.get('timestamp', ''))
                            
                            if start_date <= timestamp <= end_date:
                                revenue['this_week'] += amount
                                revenue['transactions'].append({
                                    'amount': amount,
                                    'date': timestamp.isoformat(),
                                    'description': details.get('description', '')
                                })
                            
                            if month_start <= timestamp <= today:
                                revenue['mtd'] += amount
                                
                except Exception as e:
                    continue
        
        return revenue
    
    def _identify_bottlenecks(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Identify tasks that took longer than expected."""
        bottlenecks = []
        
        # Check plans folder for delayed tasks
        plans_folder = self.vault_path / 'Plans'
        if not plans_folder.exists():
            return bottlenecks
        
        for filepath in plans_folder.iterdir():
            if filepath.suffix != '.md':
                continue
            
            try:
                content = filepath.read_text(encoding='utf-8')
                created = None
                completed = None
                
                for line in content.split('\n')[:20]:
                    if line.startswith('created:'):
                        created = datetime.fromisoformat(line.split(':')[1].strip())
                
                # Check if moved to Done
                done_file = self.done_folder / filepath.name
                if done_file.exists():
                    completed = datetime.fromtimestamp(done_file.stat().st_mtime)
                
                if created and completed:
                    duration = (completed - created).days
                    if duration > 3:  # More than 3 days
                        bottlenecks.append({
                            'task': filepath.name,
                            'duration_days': duration,
                            'created': created.strftime('%Y-%m-%d'),
                            'completed': completed.strftime('%Y-%m-%d')
                        })
                        
            except Exception as e:
                continue
        
        return bottlenecks
    
    def _generate_suggestions(self) -> List[Dict]:
        """Generate proactive suggestions."""
        suggestions = []
        
        # Check for subscription optimization
        subscriptions = self._analyze_subscriptions()
        if subscriptions:
            suggestions.append({
                'category': 'Cost Optimization',
                'items': subscriptions
            })
        
        # Check upcoming deadlines
        deadlines = self._get_upcoming_deadlines()
        if deadlines:
            suggestions.append({
                'category': 'Upcoming Deadlines',
                'items': deadlines
            })
        
        return suggestions
    
    def _analyze_subscriptions(self) -> List[Dict]:
        """Analyze subscriptions for optimization."""
        # This would integrate with accounting data
        # For now, return placeholder
        return []
    
    def _get_upcoming_deadlines(self) -> List[Dict]:
        """Get upcoming deadlines from Business_Goals.md."""
        deadlines = []
        
        if not self.business_goals.exists():
            return deadlines
        
        content = self.business_goals.read_text(encoding='utf-8')
        
        # Simple parsing for deadlines section
        in_deadlines = False
        for line in content.split('\n'):
            if 'Quarterly Deadlines' in line or 'Deadlines' in line:
                in_deadlines = True
                continue
            if in_deadlines and line.startswith('|'):
                parts = line.split('|')
                if len(parts) >= 3:
                    deadlines.append({
                        'deadline': parts[1].strip(),
                        'date': parts[2].strip()
                    })
            elif in_deadlines and line.startswith('#'):
                break
        
        return deadlines
    
    def _create_briefing_content(self,
                                  start_date: datetime,
                                  end_date: datetime,
                                  completed_tasks: List[Dict],
                                  revenue: Dict,
                                  bottlenecks: List[Dict],
                                  suggestions: List[Dict]) -> str:
        """Create briefing markdown content."""
        
        # Executive summary
        summary = self._generate_executive_summary(completed_tasks, revenue, bottlenecks)
        
        content = f'''---
generated: {datetime.now().isoformat()}
period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
---

# Monday Morning CEO Briefing

**Period:** {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}

## Executive Summary

{summary}

## Revenue

- **This Week:** ${revenue['this_week']:,.2f}
- **MTD:** ${revenue['mtd']:,.2f}
- **Transactions:** {len(revenue['transactions'])}

## Completed Tasks

Total: {len(completed_tasks)} tasks

'''
        
        # Add completed tasks
        for task in completed_tasks[:10]:  # Show last 10
            content += f"- [x] {task['file']} ({task['type']})\n"
        
        if len(completed_tasks) > 10:
            content += f"\n*...and {len(completed_tasks) - 10} more*\n"
        
        # Add bottlenecks
        content += "\n## Bottlenecks\n\n"
        if bottlenecks:
            content += "| Task | Duration | Created | Completed |\n"
            content += "|------|----------|---------|-----------|\n"
            for b in bottlenecks:
                content += f"| {b['task'][:30]} | {b['duration_days']} days | {b['created']} | {b['completed']} |\n"
        else:
            content += "*No bottlenecks identified*\n"
        
        # Add suggestions
        content += "\n## Proactive Suggestions\n"
        if suggestions:
            for suggestion in suggestions:
                content += f"\n### {suggestion['category']}\n"
                for item in suggestion['items']:
                    if isinstance(item, dict):
                        content += f"- **{item.get('deadline', item.get('name', 'Item'))}**: {item.get('date', item.get('details', ''))}\n"
                    else:
                        content += f"- {item}\n"
        else:
            content += "\n*No suggestions at this time*\n"
        
        content += "\n---\n*Generated by AI Employee v0.1 (Silver Tier)*\n"
        
        return content
    
    def _generate_executive_summary(self, 
                                     completed_tasks: List[Dict],
                                     revenue: Dict,
                                     bottlenecks: List[Dict]) -> str:
        """Generate executive summary."""
        parts = []
        
        if revenue['this_week'] > 0:
            parts.append(f"Revenue of ${revenue['this_week']:,.2f} this week")
        
        if len(completed_tasks) > 5:
            parts.append(f"{len(completed_tasks)} tasks completed")
        elif len(completed_tasks) > 0:
            parts.append(f"{len(completed_tasks)} tasks completed")
        else:
            parts.append("No tasks completed")
        
        if bottlenecks:
            parts.append(f"{len(bottlenecks)} bottleneck(s) identified")
        
        if parts:
            return ". ".join(parts[:3]) + "."
        return "Quiet week with no significant activity."
    
    def _update_dashboard(self, briefing_path: Path):
        """Update Dashboard.md with latest briefing."""
        if not self.dashboard.exists():
            return
        
        content = self.dashboard.read_text(encoding='utf-8')
        
        # Add briefing link to recent activity
        briefing_link = f"- [{briefing_path.stem}]({briefing_path.relative_to(self.vault_path)})"
        
        # Insert after "## Recent Activity"
        if '## Recent Activity' in content:
            parts = content.split('## Recent Activity')
            content = parts[0] + '## Recent Activity\n\n' + briefing_link + '\n' + parts[1]
        
        self.dashboard.write_text(content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='CEO Briefing Generator')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--preview', action='store_true', help='Preview without saving')
    
    args = parser.parse_args()
    
    generator = CEOBriefingGenerator(args.vault_path)
    
    start_date = datetime.strptime(args.start, '%Y-%m-%d') if args.start else None
    end_date = datetime.strptime(args.end, '%Y-%m-%d') if args.end else None
    
    filepath = generator.generate_briefing(
        start_date=start_date,
        end_date=end_date,
        preview=args.preview
    )
    
    if filepath and not args.preview:
        print(f"Briefing generated: {filepath}")


if __name__ == '__main__':
    main()
