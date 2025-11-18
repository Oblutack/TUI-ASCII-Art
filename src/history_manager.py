"""
History Manager - Tracks conversion history and gallery
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class HistoryEntry:
    """Single history entry"""
    
    def __init__(
        self,
        timestamp: str,
        file_name: str,
        file_path: str,
        ascii_result: str,
        is_gif: bool,
        settings: Dict,
        thumbnail: Optional[str] = None,
        frames: Optional[List[str]] = None,
        delays: Optional[List[int]] = None
    ):
        self.timestamp = timestamp
        self.file_name = file_name
        self.file_path = file_path
        self.ascii_result = ascii_result
        self.is_gif = is_gif
        self.settings = settings
        self.thumbnail = thumbnail
        self.frames = frames
        self.delays = delays
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'ascii_result': self.ascii_result,
            'is_gif': self.is_gif,
            'settings': self.settings,
            'thumbnail': self.thumbnail,
            'frames': self.frames,
            'delays': self.delays
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'HistoryEntry':
        """Create from dictionary"""
        return HistoryEntry(
            timestamp=data['timestamp'],
            file_name=data['file_name'],
            file_path=data['file_path'],
            ascii_result=data['ascii_result'],
            is_gif=data['is_gif'],
            settings=data['settings'],
            thumbnail=data.get('thumbnail'),
            frames=data.get('frames'),
            delays=data.get('delays')
        )
    
    def get_preview(self, lines: int = 10) -> str:
        """Get preview of ASCII art (first N lines)"""
        lines_list = self.ascii_result.split('\n')
        return '\n'.join(lines_list[:lines])
    
    def get_display_name(self) -> str:
        """Get display name for UI"""
        dt = datetime.fromisoformat(self.timestamp)
        time_str = dt.strftime("%H:%M:%S")
        type_str = "GIF" if self.is_gif else "IMG"
        return f"[{time_str}] {type_str} - {self.file_name}"


class HistoryManager:
    """Manages conversion history"""
    
    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.history: List[HistoryEntry] = []
        self.history_file = Path.home() / '.ascii_generator_history.json'
        self.load_history()
    
    def add_entry(
        self,
        file_name: str,
        file_path: str,
        ascii_result: str,
        is_gif: bool,
        settings: Dict,
        frames: Optional[List[str]] = None,
        delays: Optional[List[int]] = None
    ):
        """Add new history entry"""
        timestamp = datetime.now().isoformat()
        
        # Create thumbnail (first few lines of ASCII)
        thumbnail = '\n'.join(ascii_result.split('\n')[:5])
        
        entry = HistoryEntry(
            timestamp=timestamp,
            file_name=file_name,
            file_path=file_path,
            ascii_result=ascii_result,
            is_gif=is_gif,
            settings=settings,
            thumbnail=thumbnail,
            frames=frames,
            delays=delays
        )
        
        # Add to beginning of list
        self.history.insert(0, entry)
        
        # Limit size
        if len(self.history) > self.max_entries:
            self.history = self.history[:self.max_entries]
        
        # Save to disk
        self.save_history()
    
    def get_all_entries(self) -> List[HistoryEntry]:
        """Get all history entries"""
        return self.history
    
    def get_entry(self, index: int) -> Optional[HistoryEntry]:
        """Get entry by index"""
        if 0 <= index < len(self.history):
            return self.history[index]
        return None
    
    def clear_history(self):
        """Clear all history"""
        self.history = []
        self.save_history()
    
    def remove_entry(self, index: int):
        """Remove specific entry"""
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self.save_history()
    
    def save_history(self):
        """Save history to file"""
        try:
            # Only save metadata, not full frames (too large)
            data = []
            for entry in self.history:
                entry_dict = entry.to_dict()
                # Don't save frames for GIFs (too large)
                if entry_dict.get('frames'):
                    entry_dict['frames'] = None
                data.append(entry_dict)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        """Load history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [HistoryEntry.from_dict(entry) for entry in data]
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
    
    def get_statistics(self) -> Dict:
        """Get history statistics"""
        total = len(self.history)
        gifs = sum(1 for e in self.history if e.is_gif)
        images = total - gifs
        
        return {
            'total': total,
            'gifs': gifs,
            'images': images
        }