"""
ASCII Character Set Presets
Different character sets for various ASCII art styles
"""

from enum import Enum
from typing import Dict, List


class CharacterSet(Enum):
    """Available character set presets"""
    DETAILED = "detailed"
    SIMPLE = "simple"
    BLOCKS = "blocks"
    BINARY = "binary"
    DOTS = "dots"
    MINIMAL = "minimal"
    CUSTOM = "custom"


class CharacterSetManager:
    """Manages ASCII character sets for conversion"""
    
    # Predefined character sets (from darkest to lightest)
    SETS: Dict[CharacterSet, str] = {
        CharacterSet.DETAILED: "@%#*+=-:. ",  # Default ascii_magic
        CharacterSet.SIMPLE: "@%#*+=-:. ",
        CharacterSet.BLOCKS: "█▓▒░ ",
        CharacterSet.BINARY: "10 ",
        CharacterSet.DOTS: "●◐○ ",
        CharacterSet.MINIMAL: "█░ ",
    }
    
    # Display names for UI
    DISPLAY_NAMES: Dict[CharacterSet, str] = {
        CharacterSet.DETAILED: "Detailed (Default)",
        CharacterSet.SIMPLE: "Simple",
        CharacterSet.BLOCKS: "Blocks (Unicode)",
        CharacterSet.BINARY: "Binary (0/1)",
        CharacterSet.DOTS: "Dots",
        CharacterSet.MINIMAL: "Minimal",
        CharacterSet.CUSTOM: "Custom...",
    }
    
    # Descriptions for tooltips
    DESCRIPTIONS: Dict[CharacterSet, str] = {
        CharacterSet.DETAILED: "Full character set with high detail - @%#*+=-:. ",
        CharacterSet.SIMPLE: "Simple ASCII characters - @%#*+=-:. ",
        CharacterSet.BLOCKS: "Unicode block elements - █▓▒░",
        CharacterSet.BINARY: "Binary digits only - 1 and 0",
        CharacterSet.DOTS: "Circular dots - ●◐○",
        CharacterSet.MINIMAL: "Two characters only - █░",
        CharacterSet.CUSTOM: "Define your own character set",
    }
    
    @staticmethod
    def get_character_set(preset: CharacterSet, custom_chars: str = None) -> str:
        """
        Get character set string
        
        Args:
            preset: CharacterSet enum value
            custom_chars: Custom character string (if preset is CUSTOM)
        
        Returns:
            Character set string
        """
        if preset == CharacterSet.CUSTOM:
            if custom_chars and len(custom_chars) >= 2:
                return custom_chars
            else:
                # Fallback to simple if custom is invalid
                return CharacterSetManager.SETS[CharacterSet.SIMPLE]
        
        return CharacterSetManager.SETS.get(preset, CharacterSetManager.SETS[CharacterSet.DETAILED])
    
    @staticmethod
    def get_display_name(preset: CharacterSet) -> str:
        """Get display name for UI"""
        return CharacterSetManager.DISPLAY_NAMES.get(preset, "Unknown")
    
    @staticmethod
    def get_description(preset: CharacterSet) -> str:
        """Get description for tooltip"""
        return CharacterSetManager.DESCRIPTIONS.get(preset, "")
    
    @staticmethod
    def get_all_presets() -> List[CharacterSet]:
        """Get list of all available presets"""
        return [
            CharacterSet.DETAILED,
            CharacterSet.SIMPLE,
            CharacterSet.BLOCKS,
            CharacterSet.BINARY,
            CharacterSet.DOTS,
            CharacterSet.MINIMAL,
            CharacterSet.CUSTOM,
        ]
    
    @staticmethod
    def validate_custom_chars(chars: str) -> bool:
        """
        Validate custom character set
        
        Args:
            chars: Custom character string
        
        Returns:
            True if valid, False otherwise
        """
        if not chars or len(chars) < 2:
            return False
        
        # Check for duplicates
        if len(chars) != len(set(chars)):
            return False
        
        return True
    
    @staticmethod
    def get_preview(preset: CharacterSet, custom_chars: str = None) -> str:
        """
        Get preview of character set
        
        Args:
            preset: CharacterSet enum value
            custom_chars: Custom character string (if preset is CUSTOM)
        
        Returns:
            Preview string showing gradient
        """
        chars = CharacterSetManager.get_character_set(preset, custom_chars)
        
        # Create gradient preview (reverse for dark to light)
        preview = ""
        for i in range(len(chars)):
            preview += chars[i] * 3
        
        return preview