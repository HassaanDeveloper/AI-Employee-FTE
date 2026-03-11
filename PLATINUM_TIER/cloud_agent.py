#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Agent - AI Employee Cloud Component (Oracle Cloud 24/7)

Responsibilities:
- Email triage (read and categorize)
- Draft replies (draft only, no sending)
- Social media drafts (draft only, no posting)
- Write to /Cloud/Drafts/ folder
- Sync with Local via Git

Security:
- NO secrets stored (tokens, credentials stay local)
- Draft-only mode (no actual sending/posting)
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/ai-employee-cloud.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CloudAgent')


class CloudAgent:
    """Cloud Agent for AI Employee - Draft-only operations."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.cloud_drafts = self.vault_path / 'Cloud' / 'Drafts'
        self.cloud_signals = self.vault_path / 'Cloud' / 'Signals'
        self.local_approved = self.vault_path / 'Local' / 'Approved'
        
        # Ensure directories exist
        self.cloud_drafts.mkdir(parents=True, exist_ok=True)
        self.cloud_signals.mkdir(parents=True, exist_ok=True)
        
        # Cloud mode - NO sending
        self.draft_only = True
        
        logger.info(f"Cloud Agent initialized (draft-only mode)")
        logger.info(f"Vault: {self.vault_path}")
    
    def process_email(self, email_data: Dict[str, Any]) -> Path:
        """
        Process email and create draft reply.
        
        Args:
            email_data: Email data from Gmail Watcher
            
        Returns:
            Path to draft file
        """
        try:
            from_email = email_data.get('from', 'Unknown')
            subject = email_data.get('subject', 'No Subject')
            content = email_data.get('content', '')
            
            # Categorize email
            category = self._categorize_email(subject, content)
            
            # Create draft reply
            draft_content = self._create_draft_reply(email_data, category)
            
            # Save draft
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"DRAFT_EMAIL_{timestamp}_{category}.md"
            draft_path = self.cloud_drafts / filename
            
            draft_path.write_text(draft_content, encoding='utf-8')
            
            logger.info(f"Created draft reply: {draft_path.name}")
            
            # Write signal for Local Agent
            self._write_signal('email_draft', str(draft_path))
            
            return draft_path
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return None
    
    def process_social_post(self, post_data: Dict[str, Any]) -> Path:
        """
        Create social media post draft.
        
        Args:
            post_data: Post data (topic, keywords, etc.)
            
        Returns:
            Path to draft file
        """
        try:
            topic = post_data.get('topic', 'General')
            keywords = post_data.get('keywords', [])
            
            # Create draft post
            draft_content = self._create_social_draft(topic, keywords)
            
            # Save draft
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"DRAFT_SOCIAL_{timestamp}.md"
            draft_path = self.cloud_drafts / filename
            
            draft_path.write_text(draft_content, encoding='utf-8')
            
            logger.info(f"Created social media draft: {draft_path.name}")
            
            # Write signal for Local Agent
            self._write_signal('social_draft', str(draft_path))
            
            return draft_path
            
        except Exception as e:
            logger.error(f"Error creating social draft: {e}")
            return None
    
    def _categorize_email(self, subject: str, content: str) -> str:
        """Categorize email by content."""
        subject_lower = subject.lower()
        content_lower = content.lower()
        
        # Priority keywords
        if any(kw in subject_lower for kw in ['urgent', 'asap', 'emergency']):
            return 'urgent'
        elif any(kw in subject_lower for kw in ['invoice', 'payment', 'billing']):
            return 'financial'
        elif any(kw in subject_lower for kw in ['meeting', 'schedule', 'appointment']):
            return 'meeting'
        elif any(kw in subject_lower for kw in ['question', 'help', 'support']):
            return 'support'
        elif any(kw in subject_lower for kw in ['opportunity', 'proposal', 'project']):
            return 'business'
        else:
            return 'general'
    
    def _create_draft_reply(self, email_data: Dict[str, Any], category: str) -> str:
        """Create draft reply based on email category."""
        from_email = email_data.get('from', 'Unknown')
        subject = email_data.get('subject', 'No Subject')
        content = email_data.get('content', '')
        
        # Category-specific templates
        templates = {
            'urgent': f"""---
type: email_draft
category: urgent
from: {from_email}
subject: Re: {subject}
created: {datetime.now().isoformat()}
status: draft
priority: high
action_required: local_approval
---

# Draft Reply: URGENT

**To:** {from_email}  
**Subject:** Re: {subject}  
**Priority:** HIGH

## Draft Message

Dear Sender,

Thank you for your urgent message. I have received your request and will respond as soon as possible.

Best regards,  
AI Employee

---
**Note:** This is a DRAFT. Local approval required before sending.
**Action:** Move to Local/Approved/ to send.
""",
            
            'financial': f"""---
type: email_draft
category: financial
from: {from_email}
subject: Re: {subject}
created: {datetime.now().isoformat()}
status: draft
priority: normal
action_required: local_approval
---

# Draft Reply: FINANCIAL

**To:** {from_email}  
**Subject:** Re: {subject}

## Draft Message

Dear Sender,

Thank you for your message regarding financial matters.

I have received your request and will review it shortly.

Best regards,  
AI Employee

---
**Note:** This is a DRAFT. Local approval required before sending.
**Action:** Move to Local/Approved/ to send.
""",
            
            'general': f"""---
type: email_draft
category: general
from: {from_email}
subject: Re: {subject}
created: {datetime.now().isoformat()}
status: draft
priority: normal
action_required: local_approval
---

# Draft Reply

**To:** {from_email}  
**Subject:** Re: {subject}

## Draft Message

Dear Sender,

Thank you for your email.

I have received your message and will respond soon.

Best regards,  
AI Employee

---
**Note:** This is a DRAFT. Local approval required before sending.
**Action:** Move to Local/Approved/ to send.
"""
        }
        
        return templates.get(category, templates['general'])
    
    def _create_social_draft(self, topic: str, keywords: List[str]) -> str:
        """Create social media post draft."""
        hashtags = ' '.join([f'#{kw}' for kw in keywords[:5]])
        
        return f"""---
type: social_draft
platform: facebook
topic: {topic}
created: {datetime.now().isoformat()}
status: draft
action_required: local_approval
hashtags: {hashtags}
---

# Social Media Draft

**Platform:** Facebook Page  
**Topic:** {topic}

## Draft Post

🚀 Exciting update from our team!

{topic}

Stay tuned for more updates!

{hashtags}

---
**Note:** This is a DRAFT. Local approval required before posting.
**Action:** Move to Local/Approved/ to post.
"""
    
    def _write_signal(self, signal_type: str, data: str):
        """Write signal file for Local Agent."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        signal_file = self.cloud_signals / f"SIGNAL_{signal_type}_{timestamp}.json"
        
        signal_data = {
            'type': signal_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        with open(signal_file, 'w') as f:
            json.dump(signal_data, f, indent=2)
        
        logger.debug(f"Signal written: {signal_file.name}")


def main():
    """Main Cloud Agent loop."""
    vault_path = os.environ.get('VAULT_PATH', '/home/opc/ai-employee/AI_Employee_Vault')
    
    agent = CloudAgent(vault_path)
    
    logger.info("Cloud Agent starting...")
    
    # In production, this would have watchers for:
    # - Gmail (draft mode)
    # - Social media scheduling (draft mode)
    # - Signal file monitoring
    
    # For now, just log that it's running
    logger.info("Cloud Agent running in draft-only mode")
    logger.info("Waiting for emails and social media requests...")
    
    # Keep running
    import time
    while True:
        try:
            # Process any pending items
            # (In production, this would check Gmail API, etc.)
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Cloud Agent stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in Cloud Agent loop: {e}")
            time.sleep(60)


if __name__ == '__main__':
    main()
