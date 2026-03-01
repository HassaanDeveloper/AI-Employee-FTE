#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filesystem Watcher - Monitors a drop folder for new files.

When files are added to the Inbox folder, creates corresponding
action files in Needs_Action for Claude Code to process.

Uses watchdog library for efficient file system monitoring.
Install with: pip install watchdog

Usage:
    python filesystem_watcher.py /path/to/vault
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher

# Watchdog imports (optional - graceful fallback)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Watchdog not installed. Install with: pip install watchdog")
    print("Will use polling fallback mode.")


class DropFolderHandler(FileSystemEventHandler):
    """Handler for file system events in the drop folder."""
    
    def __init__(self, watcher: 'FilesystemWatcher'):
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        self.logger.info(f"New file detected: {event.src_path}")
        self.watcher.process_new_file(Path(event.src_path))
    
    def on_moved(self, event):
        """Handle file move events (files moved into drop folder)."""
        if event.is_directory:
            return
        
        self.logger.info(f"File moved into folder: {event.dest_path}")
        self.watcher.process_new_file(Path(event.dest_path))


class FilesystemWatcher(BaseWatcher):
    """Watcher for filesystem drop folder."""
    
    def __init__(
        self, 
        vault_path: str,
        check_interval: int = 30
    ):
        """
        Initialize Filesystem Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Also watch the Inbox folder directly
        self.drop_folder = self.inbox
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        self.observer = None
        self.handler = None
        
        if WATCHDOG_AVAILABLE:
            self._setup_observer()
        else:
            self.logger.info("Using polling mode (watchdog not available)")
    
    def _setup_observer(self):
        """Set up watchdog observer for real-time monitoring."""
        try:
            self.handler = DropFolderHandler(self)
            self.observer = Observer()
            self.observer.schedule(self.handler, str(self.drop_folder), recursive=False)
            self.observer.start()
            self.logger.info(f"Watching folder: {self.drop_folder}")
        except Exception as e:
            self.logger.error(f"Could not set up observer: {e}")
            self.observer = None
    
    def process_new_file(self, filepath: Path):
        """
        Process a newly detected file.
        
        Args:
            filepath: Path to the new file
        """
        if not filepath.exists():
            return
        
        # Skip hidden files and temp files
        if filepath.name.startswith('.') or filepath.suffix == '.tmp':
            self.logger.debug(f"Skipping temp/hidden file: {filepath}")
            return
        
        # Generate file ID (hash of content)
        file_id = self._generate_file_id(filepath)
        
        if file_id in self.processed_ids:
            self.logger.debug(f"File already processed: {filepath}")
            return
        
        # Create action file
        action_file = self.create_action_file({
            'path': str(filepath),
            'name': filepath.name,
            'size': filepath.stat().st_size,
            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            'file_id': file_id
        })
        
        if action_file:
            self._save_processed_id(file_id)
    
    def _generate_file_id(self, filepath: Path) -> str:
        """Generate unique ID for a file based on content hash."""
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                # Hash first 1MB for large files
                chunk = f.read(1024 * 1024)
                hasher.update(chunk)
            return hasher.hexdigest()[:16]
        except Exception as e:
            self.logger.error(f"Could not hash file: {e}")
            return f"unknown_{datetime.now().timestamp()}"
    
    def check_for_updates(self):
        """
        Check for new files in drop folder (polling mode).
        
        This is used as fallback when watchdog is not available,
        or as a secondary check.
        """
        if self.observer and self.observer.is_alive():
            # Watchdog is handling real-time monitoring
            # Still do periodic scan to catch any missed files
            pass
        
        new_files = []
        try:
            for filepath in self.drop_folder.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    file_id = self._generate_file_id(filepath)
                    if file_id not in self.processed_ids:
                        new_files.append({
                            'path': str(filepath),
                            'name': filepath.name,
                            'size': filepath.stat().st_size,
                            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                            'file_id': file_id
                        })
        except Exception as e:
            self.logger.error(f"Error scanning drop folder: {e}")
        
        return new_files
    
    def create_action_file(self, file_info: Dict[str, Any]) -> Optional[Path]:
        """
        Create action file for a dropped file.
        
        Args:
            file_info: Dict with file metadata
            
        Returns:
            Path to created file
        """
        try:
            filepath = Path(file_info['path'])
            filename = file_info['name']
            size = file_info['size']
            file_id = file_info['file_id']
            
            # Determine file type category
            file_type = self._categorize_file(filename)
            
            # Read file content if text-based
            content_preview = ""
            if self._is_text_file(filename):
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                        content_preview = f.read(1000)  # First 1000 chars
                except Exception:
                    pass
            
            content = f'''---
type: file_drop
original_name: {filename}
file_id: {file_id}
size: {size}
size_human: {self._format_size(size)}
received: {datetime.now().isoformat()}
category: {file_type}
status: pending
---

# File Dropped for Processing

**Original Name:** {filename}  
**Size:** {self._format_size(size)}  
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Category:** {file_type}

## Content Preview

```
{content_preview if content_preview else "(Binary file or could not read)"}
```

## File Location

Source: `{filepath}`

## Suggested Actions

- [ ] Review file content
- [ ] Categorize and file appropriately
- [ ] Extract any actionable items
- [ ] Move to appropriate folder after processing
- [ ] Delete original from Inbox if no longer needed

## Notes

*Add your notes here*

---
*Created by Filesystem Watcher*
'''
            
            # Create filename
            safe_name = self._sanitize_filename(filename)[:30]
            action_filename = f"FILE_{file_id}_{safe_name}.md"
            
            action_path = self._create_markdown_file(action_filename, content)
            
            return action_path
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def _categorize_file(self, filename: str) -> str:
        """Categorize file based on extension."""
        ext = Path(filename).suffix.lower()
        
        categories = {
            '.pdf': 'Document',
            '.doc': 'Document',
            '.docx': 'Document',
            '.txt': 'Document',
            '.md': 'Document',
            '.xls': 'Spreadsheet',
            '.xlsx': 'Spreadsheet',
            '.csv': 'Spreadsheet',
            '.jpg': 'Image',
            '.jpeg': 'Image',
            '.png': 'Image',
            '.gif': 'Image',
            '.mp3': 'Audio',
            '.wav': 'Audio',
            '.mp4': 'Video',
            '.mov': 'Video',
            '.zip': 'Archive',
            '.rar': 'Archive',
        }
        
        return categories.get(ext, 'Other')
    
    def _is_text_file(self, filename: str) -> bool:
        """Check if file is likely text-based."""
        text_extensions = {'.txt', '.md', '.csv', '.json', '.xml', '.html', '.log', '.py', '.js'}
        return Path(filename).suffix.lower() in text_extensions
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        invalid = '<>:"/\\|？*'
        for char in invalid:
            text = text.replace(char, '_')
        return text.strip()
    
    def stop(self):
        """Stop the observer."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("Filesystem watcher stopped")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Filesystem Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    watcher = FilesystemWatcher(
        vault_path=args.vault_path,
        check_interval=args.interval
    )
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.stop()
        print("\nFilesystem watcher stopped")


if __name__ == '__main__':
    main()
