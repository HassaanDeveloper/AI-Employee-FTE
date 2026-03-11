#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Agent - AI Employee Local Component (Your PC)

Responsibilities:
- Review Cloud drafts
- Approve/Reject actions
- Execute final send/post actions
- Manage secrets (tokens, credentials)
- WhatsApp session (local only)
- Payments/banking (local only)

Security:
- ALL secrets stored locally
- NEVER synced to Cloud
- Final approval authority
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LocalAgent')


class LocalAgent:
    """Local Agent for AI Employee - Final approval and execution."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.cloud_drafts = self.vault_path / 'Cloud' / 'Drafts'
        self.cloud_signals = self.vault_path / 'Cloud' / 'Signals'
        self.local_approved = self.vault_path / 'Local' / 'Approved'
        self.local_pending = self.vault_path / 'Local' / 'Pending'
        self.local_secrets = self.vault_path / '.secrets'
        self.done_folder = self.vault_path / 'Done'
        
        # Ensure directories exist
        for folder in [self.local_approved, self.local_pending, self.done_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Load secrets (NEVER sync these!)
        self.secrets = self._load_secrets()
        
        logger.info(f"Local Agent initialized")
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Secrets loaded: {bool(self.secrets)}")
    
    def check_cloud_signals(self) -> list:
        """Check for new signals from Cloud Agent."""
        signals = []
        
        if not self.cloud_signals.exists():
            return signals
        
        for signal_file in self.cloud_signals.glob('SIGNAL_*.json'):
            try:
                with open(signal_file, 'r') as f:
                    signal_data = json.load(f)
                
                signals.append({
                    'file': signal_file,
                    'type': signal_data.get('type'),
                    'data': signal_data.get('data'),
                    'timestamp': signal_data.get('timestamp')
                })
            except Exception as e:
                logger.error(f"Error reading signal: {e}")
        
        return signals
    
    def process_draft(self, draft_path: Path, action: str) -> bool:
        """
        Process draft from Cloud Agent.
        
        Args:
            draft_path: Path to draft file
            action: 'approve' or 'reject'
            
        Returns:
            True if successful
        """
        if not draft_path.exists():
            logger.error(f"Draft not found: {draft_path}")
            return False
        
        if action == 'approve':
            return self._execute_draft(draft_path)
        elif action == 'reject':
            return self._reject_draft(draft_path)
        else:
            logger.error(f"Unknown action: {action}")
            return False
    
    def _execute_draft(self, draft_path: Path) -> bool:
        """Execute approved draft (send email or post to social)."""
        try:
            content = draft_path.read_text(encoding='utf-8')
            
            # Extract draft type from frontmatter
            draft_type = self._extract_frontmatter_value(content, 'type')
            
            if draft_type == 'email_draft':
                return self._send_email(draft_path, content)
            elif draft_type == 'social_draft':
                return self._post_social(draft_path, content)
            else:
                logger.error(f"Unknown draft type: {draft_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing draft: {e}")
            return False
    
    def _send_email(self, draft_path: Path, content: str) -> bool:
        """Send email using Email MCP Server."""
        try:
            # Extract email details
            to_email = self._extract_frontmatter_value(content, 'to')
            subject = self._extract_frontmatter_value(content, 'subject')
            
            # Get message body (after ## Draft Message)
            body = content.split('## Draft Message')[-1].split('---')[0].strip()
            
            logger.info(f"Sending email to: {to_email}")
            logger.info(f"Subject: {subject}")
            
            # Call Email MCP Server (port 8765)
            import urllib.request
            
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "send_email",
                    "arguments": {
                        "to": to_email,
                        "subject": subject.replace('Re: ', ''),
                        "body": body
                    }
                }
            }
            
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
                    logger.info(f"Email sent successfully!")
                    
                    # Move to Done
                    done_path = self.done_folder / draft_path.name
                    shutil.move(str(draft_path), str(done_path))
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _post_social(self, draft_path: Path, content: str) -> bool:
        """Post to social media using Facebook MCP Server."""
        try:
            # Extract post message
            message = content.split('## Draft Post')[-1].split('---')[0].strip()
            
            # Get Facebook config from secrets
            page_id = self.secrets.get('FACEBOOK_PAGE_ID', '993926910480113')
            access_token = self.secrets.get('FACEBOOK_ACCESS_TOKEN')
            
            if not access_token:
                logger.error("Facebook access token not found in secrets")
                return False
            
            logger.info(f"Posting to Facebook Page: {page_id}")
            
            # Call Facebook MCP Server (port 8771)
            import urllib.request
            
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "post_to_facebook",
                    "arguments": {
                        "message": message,
                        "link": None
                    }
                }
            }
            
            data = json.dumps(request).encode('utf-8')
            req = urllib.request.Request(
                'http://localhost:8771/mcp',
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'result' in result:
                    result_text = json.loads(result['result']['content'][0]['text'])
                    
                    if result_text.get('success'):
                        post_id = result_text.get('post_id')
                        logger.info(f"Posted to Facebook! Post ID: {post_id}")
                        
                        # Move to Done
                        done_path = self.done_folder / draft_path.name
                        shutil.move(str(draft_path), str(done_path))
                        
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error posting to Facebook: {e}")
            return False
    
    def _reject_draft(self, draft_path: Path) -> bool:
        """Reject draft and move to Rejected folder."""
        try:
            rejected_folder = self.vault_path / 'Rejected'
            rejected_folder.mkdir(parents=True, exist_ok=True)
            
            rejected_path = rejected_folder / draft_path.name
            shutil.move(str(draft_path), str(rejected_path))
            
            logger.info(f"Draft rejected: {draft_path.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting draft: {e}")
            return False
    
    def _load_secrets(self) -> Dict[str, str]:
        """Load secrets from local .secrets folder (NEVER synced)."""
        secrets = {}
        
        if not self.local_secrets.exists():
            logger.warning("Secrets folder not found")
            return secrets
        
        # Load .env file
        env_file = self.local_secrets / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        secrets[key.strip()] = value.strip()
        
        logger.info(f"Loaded {len(secrets)} secrets")
        
        return secrets
    
    def _extract_frontmatter_value(self, content: str, key: str) -> str:
        """Extract value from YAML frontmatter."""
        lines = content.split('\n')
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            
            if in_frontmatter and line.startswith(f'{key}:'):
                return line.split(':', 1)[1].strip()
        
        return ''


def main():
    """Main Local Agent loop."""
    vault_path = os.environ.get('VAULT_PATH', 'E:/AI-Employee-FTE/AI_Employee_Vault')
    
    agent = LocalAgent(vault_path)
    
    logger.info("Local Agent starting...")
    logger.info("Checking for Cloud signals...")
    
    import time
    
    while True:
        try:
            # Check for signals from Cloud
            signals = agent.check_cloud_signals()
            
            if signals:
                logger.info(f"Found {len(signals)} signal(s) from Cloud")
                
                for signal in signals:
                    logger.info(f"Processing signal: {signal['type']}")
                    
                    # In production, this would:
                    # 1. Notify user of new draft
                    # 2. Wait for user approval
                    # 3. Execute or reject based on approval
                    
                    # For now, just log and remove signal
                    signal['file'].unlink()
            else:
                logger.debug("No new signals from Cloud")
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("Local Agent stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in Local Agent loop: {e}")
            time.sleep(30)


if __name__ == '__main__':
    main()
