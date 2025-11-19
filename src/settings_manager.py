"""
Settings Manager - User preferences and auto-save
"""

import json
from pathlib import Path
from typing import Dict, Any


class SettingsManager:
    """Manages user settings and preferences"""
    
    DEFAULT_SETTINGS = {
        # Main window settings
        'width': 120,
        'character_set': 'detailed',
        'brightness': 0,
        'contrast': 100,
        'invert': False,
        'remove_background': False,
        'aspect_ratio': 'original',  # original, square, custom
        'custom_ratio': 1.0,
        
        # Widget settings
        'widget_font_size': 9,
        'widget_color_theme': 'grape',  # grape, matrix, amber, cyan, custom
        'widget_opacity': 95,
        
        # Window geometry
        'window_width': 800,
        'window_height': 550,
        'window_x': 100,
        'window_y': 100,
    }
    
    def __init__(self):
        self.settings_file = Path.home() / '.ascii_generator_settings.json'
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults (in case new settings were added)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set setting value"""
        self.settings[key] = value
        self.save_settings()
    
    def get_all(self) -> Dict:
        """Get all settings"""
        return self.settings.copy()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()


class ColorTheme:
    """Color themes for widget"""
    
    THEMES = {
        'grape': {
            'name': 'Grape (Default)',
            'background': 'rgba(48, 41, 47, 250)',
            'text': '#9b96d6',
            'border': '#5f5aa2',
            'accent': '#7b76c2'
        },
        'matrix': {
            'name': 'Matrix Green',
            'background': 'rgba(0, 0, 0, 250)',
            'text': '#00ff00',
            'border': '#00aa00',
            'accent': '#00ff00'
        },
        'amber': {
            'name': 'Amber Terminal',
            'background': 'rgba(20, 15, 10, 250)',
            'text': '#ffb000',
            'border': '#ff8800',
            'accent': '#ffd700'
        },
        'cyan': {
            'name': 'Cyan Wave',
            'background': 'rgba(10, 15, 25, 250)',
            'text': '#00ffff',
            'border': '#0099cc',
            'accent': '#00d9ff'
        },
        'pink': {
            'name': 'Pink Neon',
            'background': 'rgba(25, 10, 20, 250)',
            'text': '#ff1493',
            'border': '#ff69b4',
            'accent': '#ff1493'
        },
        'monochrome': {
            'name': 'Monochrome',
            'background': 'rgba(20, 20, 20, 250)',
            'text': '#ffffff',
            'border': '#666666',
            'accent': '#cccccc'
        }
    }
    
    @staticmethod
    def get_theme(theme_name: str) -> Dict:
        """Get theme colors"""
        return ColorTheme.THEMES.get(theme_name, ColorTheme.THEMES['grape'])
    
    @staticmethod
    def get_all_themes():
        """Get all theme names"""
        return list(ColorTheme.THEMES.keys())
    
    @staticmethod
    def get_display_name(theme_name: str) -> str:
        """Get display name for theme"""
        theme = ColorTheme.THEMES.get(theme_name, ColorTheme.THEMES['grape'])
        return theme['name']


class AspectRatioMode:
    """Aspect ratio modes"""
    
    ORIGINAL = 'original'
    SQUARE = 'square'
    WIDESCREEN = 'widescreen'  # 16:9
    PORTRAIT = 'portrait'  # 9:16
    CUSTOM = 'custom'
    
    MODES = {
        ORIGINAL: ('Keep Original', 0),  # 0 means use original
        SQUARE: ('Square (1:1)', 1.0),
        WIDESCREEN: ('Widescreen (16:9)', 16/9),
        PORTRAIT: ('Portrait (9:16)', 9/16),
        CUSTOM: ('Custom...', 1.0)
    }
    
    @staticmethod
    def get_display_name(mode: str) -> str:
        """Get display name for mode"""
        return AspectRatioMode.MODES.get(mode, AspectRatioMode.MODES[AspectRatioMode.ORIGINAL])[0]
    
    @staticmethod
    def get_ratio(mode: str) -> float:
        """Get ratio value for mode"""
        return AspectRatioMode.MODES.get(mode, AspectRatioMode.MODES[AspectRatioMode.ORIGINAL])[1]
    
    @staticmethod
    def get_all_modes():
        """Get all mode keys"""
        return list(AspectRatioMode.MODES.keys())