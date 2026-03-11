#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ralph Wiggum Loop - Keep Qwen Code working until tasks are complete.

This implements the "Stop Hook" pattern that:
1. Intercepts Qwen Code's exit
2. Checks if task is complete
3. Re-injects prompt if task is incomplete
4. Continues until completion or max iterations

Usage:
    python ralph_loop.py "Process all emails and create invoice for Client A"
"""

import sys
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime


class RalphWiggumLoop:
    """Ralph Wiggum Stop Hook for autonomous task completion."""
    
    def __init__(
        self,
        vault_path: str,
        prompt: str,
        max_iterations: int = 10,
        completion_signal: str = "TASK_COMPLETE"
    ):
        self.vault_path = Path(vault_path)
        self.prompt = prompt
        self.max_iterations = max_iterations
        self.completion_signal = completion_signal
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        
        self.logger = print  # Simple logging
    
    def check_task_complete(self) -> bool:
        """Check if task is complete by checking Needs_Action folder."""
        # Task is complete if Needs_Action is empty
        if not self.needs_action.exists():
            return True
        
        md_files = list(self.needs_action.glob('*.md'))
        return len(md_files) == 0
    
    def run_loop(self):
        """Run the Ralph Wiggum loop."""
        self.logger(f"\n{'='*60}")
        self.logger(f"Ralph Wiggum Loop - Autonomous Task Completion")
        self.logger(f"{'='*60}")
        self.logger(f"Task: {self.prompt}")
        self.logger(f"Max iterations: {self.max_iterations}")
        self.logger(f"Completion signal: {self.completion_signal}")
        self.logger(f"{'='*60}\n")
        
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            self.logger(f"\n[Iteration {iteration}/{self.max_iterations}]")
            self.logger(f"Checking task status...")
            
            # Check if task is complete
            if self.check_task_complete():
                self.logger(f"✓ Task complete! Needs_Action folder is empty.")
                self.logger(f"\n{'='*60}")
                self.logger(f"Ralph Wiggum Loop finished successfully!")
                self.logger(f"{'='*60}\n")
                return True
            
            self.logger(f"Task not complete. Running Qwen Code...")
            
            # Run Qwen Code with prompt
            try:
                result = self._run_qwen(self.prompt)
                
                if result == 'timeout':
                    self.logger(f"⚠ Qwen Code timed out")
                elif result == 'error':
                    self.logger(f"⚠ Qwen Code encountered an error")
                else:
                    self.logger(f"✓ Qwen Code completed iteration")
                
            except Exception as e:
                self.logger(f"✗ Error running Qwen Code: {e}")
            
            # Wait a moment for file system to update
            time.sleep(2)
        
        # Max iterations reached
        self.logger(f"\n{'='*60}")
        self.logger(f"⚠ Max iterations ({self.max_iterations}) reached")
        self.logger(f"Task may still be incomplete.")
        self.logger(f"{'='*60}\n")
        
        return False
    
    def _run_qwen(self, prompt: str) -> str:
        """Run Qwen Code with the given prompt."""
        try:
            # Build Qwen Code command
            cmd = [
                'qwen',
                '--model', 'qwen-code',
                '--append-system-prompt',
                f'''You are an AI Employee working autonomously.
                
Task: {prompt}

IMPORTANT:
1. Process all items in Needs_Action folder
2. Move completed items to Done folder
3. When task is COMPLETE, output exactly: {self.completion_signal}
4. Do not exit until task is complete or you cannot make further progress

Rules:
- Follow Company_Handbook.md
- Request approval for sensitive actions
- Log all activities
- Be persistent but know when to stop
'''
            ]
            
            # Run Qwen Code
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.vault_path),
                shell=True,
                encoding='utf-8'
            )
            
            # Wait for completion or timeout (10 minutes max per iteration)
            try:
                stdout, stderr = process.communicate(timeout=600)
                
                # Check if completion signal was output
                if self.completion_signal in stdout:
                    self.logger(f"✓ Detected completion signal!")
                    return 'completed'
                
                return 'success'
                
            except subprocess.TimeoutExpired:
                process.kill()
                return 'timeout'
                
        except FileNotFoundError:
            self.logger(f"✗ Qwen Code not found. Make sure it's installed.")
            return 'error'
        except Exception as e:
            self.logger(f"✗ Error: {e}")
            return 'error'


def main():
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Keep Qwen Code working until done',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python ralph_loop.py "Process all emails"
  python ralph_loop.py "Create invoices for all clients" --max-iterations 5
  python ralph_loop.py "Clean up inbox" --completion-signal "DONE"
        '''
    )
    
    parser.add_argument('prompt', help='Task description')
    parser.add_argument(
        '--vault',
        default='E:\\AI-Employee-FTE\\AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum iterations before giving up'
    )
    parser.add_argument(
        '--completion-signal',
        default='TASK_COMPLETE',
        help='Signal text that indicates task completion'
    )
    
    args = parser.parse_args()
    
    loop = RalphWiggumLoop(
        vault_path=args.vault,
        prompt=args.prompt,
        max_iterations=args.max_iterations,
        completion_signal=args.completion_signal
    )
    
    success = loop.run_loop()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
