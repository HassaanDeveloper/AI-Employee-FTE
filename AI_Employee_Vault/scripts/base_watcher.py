#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all watcher scripts.

All watchers follow this pattern:
1. Check for new items periodically
2. Create action files in Needs_Action folder
3. Log all activity
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """Abstract base class for all watcher implementations."""
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs_dir = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logger
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        # Load previously processed IDs from log
        self._load_processed_ids()
    
    def _load_processed_ids(self):
        """Load processed IDs from the last log file to avoid reprocessing."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}_processed.json'
        
        if log_file.exists():
            import json
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get('processed_ids', []))
                    self.logger.info(f"Loaded {len(self.processed_ids)} previously processed IDs")
            except Exception as e:
                self.logger.warning(f"Could not load processed IDs: {e}")
    
    def _save_processed_id(self, item_id: str):
        """Save a processed ID to the log file."""
        import json
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}_processed.json'
        
        self.processed_ids.add(item_id)
        
        try:
            # Load existing IDs
            if log_file.exists():
                with open(log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {'processed_ids': []}
            
            data['processed_ids'] = list(self.processed_ids)
            
            with open(log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save processed ID: {e}")
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items to process.
        
        Returns:
            List of new items (format depends on watcher type)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file in Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to created file, or None if failed
        """
        pass
    
    def _create_markdown_file(self, filename: str, content: str) -> Path:
        """Helper to create a markdown file in Needs_Action."""
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created action file: {filepath}")
        return filepath
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        
        This method runs indefinitely until interrupted (Ctrl+C).
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        
        try:
            while True:
                try:
                    # Check for new items
                    items = self.check_for_updates()
                    
                    if items:
                        self.logger.info(f"Found {len(items)} new item(s)")
                        for item in items:
                            try:
                                self.create_action_file(item)
                            except Exception as e:
                                self.logger.error(f"Error creating action file: {e}")
                    else:
                        self.logger.debug("No new items")
                    
                except Exception as e:
                    self.logger.error(f"Error in check loop: {e}")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f"{self.__class__.__name__} stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            raise


if __name__ == '__main__':
    # This is an abstract class - cannot be instantiated directly
    print("BaseWatcher is an abstract class. Extend it to create a specific watcher.")
