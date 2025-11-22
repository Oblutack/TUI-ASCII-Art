"""
Cyberpunk Redesign Theme - Based on Figma Design
Dark theme with neon borders and glow effects
"""

from PyQt6.QtGui import QFont, QFontDatabase

# Color Palette from Figma
class CyberpunkColors:
    """Cyberpunk color scheme"""
    
    # Backgrounds
    BG_DARK = "#0a0e1a"           # Main background
    BG_PANEL = "#12172b"          # Panel backgrounds
    BG_INPUT = "#1a1f35"          # Input fields
    
    # Neon Borders (matching Figma)
    CYAN = "#00d9ff"              # INPUT, ADJUSTMENTS
    MAGENTA = "#ff006e"           # WIDTH
    PURPLE = "#b794f6"            # STYLE
    GREEN = "#00ff88"             # ACTIONS
    BLUE_PURPLE = "#8b5cf6"       # OUTPUT
    
    # Text colors
    TEXT_PRIMARY = "#e0e0e0"      # Main text
    TEXT_SECONDARY = "#a0aec0"    # Secondary text
    TEXT_DIM = "#6b7280"          # Dimmed text
    TEXT_CYAN = "#00d9ff"         # Cyan accents
    
    # Button colors
    BTN_SAVE = "#ff006e"          # Save button
    BTN_WINDOW = "#8b5cf6"        # Window button
    BTN_HISTORY = "#3b82f6"       # History button
    BTN_QUIT = "#ef4444"          # Quit button
    
    # Slider colors
    SLIDER_CYAN = "#00d9ff"       # Cyan glow
    SLIDER_TRACK = "#1e293b"     # Track background
    
    # Special effects
    GLOW_CYAN = "rgba(0, 217, 255, 0.4)"
    GLOW_MAGENTA = "rgba(255, 0, 110, 0.4)"
    GLOW_PURPLE = "rgba(183, 148, 246, 0.4)"


CYBERPUNK_THEME = f"""
/* ============================
   MAIN WINDOW - Dark Cyberpunk
   ============================ */

QMainWindow {{
    background-color: {CyberpunkColors.BG_DARK};
    color: {CyberpunkColors.TEXT_PRIMARY};
}}

QWidget {{
    background-color: {CyberpunkColors.BG_DARK};
    color: {CyberpunkColors.TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
    font-size: 10pt;
}}

/* ============================
   FRAMES - Neon Borders
   ============================ */

QFrame {{
    background-color: {CyberpunkColors.BG_PANEL};
    border: 2px solid {CyberpunkColors.CYAN};
    border-radius: 8px;
    padding: 12px;
    min-width: 0px;
    min-height: 0px;
}}

QFrame#titleFrame {{
    background-color: {CyberpunkColors.BG_DARK};
    border: none;
    border-bottom: 1px solid {CyberpunkColors.TEXT_DIM};
    border-radius: 0px;
    padding: 16px;
}}

QFrame#inputBox {{
    border: 2px solid {CyberpunkColors.CYAN};
    background-color: {CyberpunkColors.BG_PANEL};
}}

QFrame#widthBox {{
    border: 2px solid {CyberpunkColors.MAGENTA};
    background-color: {CyberpunkColors.BG_PANEL};
}}

QFrame#styleBox {{
    border: 2px solid {CyberpunkColors.PURPLE};
    background-color: {CyberpunkColors.BG_PANEL};
}}

QFrame#actionsBox {{
    border: 2px solid {CyberpunkColors.GREEN};
    background-color: {CyberpunkColors.BG_PANEL};
}}

QFrame#adjustmentsBox {{
    border: 2px solid {CyberpunkColors.CYAN};
    background-color: {CyberpunkColors.BG_PANEL};
}}

QFrame#outputBox {{
    border: 2px solid {CyberpunkColors.BLUE_PURPLE};
    background-color: {CyberpunkColors.BG_PANEL};
}}

/* ============================
   LABELS - Section Headers
   ============================ */

QLabel {{
    color: {CyberpunkColors.TEXT_PRIMARY};
    background: transparent;
    border: none;
}}

QLabel#titleLabel {{
    color: {CyberpunkColors.CYAN};
    font-size: 14pt;
    font-weight: 600;
    letter-spacing: 1px;
}}

QLabel#subtitleLabel {{
    color: {CyberpunkColors.TEXT_SECONDARY};
    font-size: 9pt;
}}

QLabel#sectionLabel {{
    color: {CyberpunkColors.TEXT_CYAN};
    font-size: 9pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 0px;
    border: none;
}}

QLabel#valueLabel {{
    color: {CyberpunkColors.CYAN};
    font-size: 18pt;
    font-weight: 700;
}}

QLabel#hintLabel {{
    color: {CyberpunkColors.TEXT_DIM};
    font-size: 9pt;
    font-style: italic;
}}

/* ============================
   BUTTONS - Modern Cyber Style
   ============================ */

QPushButton {{
    background-color: {CyberpunkColors.BG_PANEL};
    color: {CyberpunkColors.TEXT_PRIMARY};
    border: 2px solid {CyberpunkColors.TEXT_DIM};
    border-radius: 6px;
    padding: 10px 16px;
    font-weight: 600;
    font-size: 10pt;
    min-height: 36px;
}}

QPushButton:hover {{
    border-color: {CyberpunkColors.CYAN};
    background-color: rgba(0, 217, 255, 0.1);
}}

QPushButton:pressed {{
    background-color: rgba(0, 217, 255, 0.2);
}}

QPushButton:disabled {{
    background-color: {CyberpunkColors.BG_INPUT};
    color: {CyberpunkColors.TEXT_DIM};
    border-color: {CyberpunkColors.TEXT_DIM};
}}

/* Load Button */
QPushButton#loadButton {{
    background-color: {CyberpunkColors.BG_PANEL};
    border: 2px solid {CyberpunkColors.CYAN};
    color: {CyberpunkColors.CYAN};
}}

QPushButton#loadButton:hover {{
    background-color: rgba(0, 217, 255, 0.15);
    border-color: {CyberpunkColors.CYAN};
}}

/* Save Button */
QPushButton#saveButton {{
    background-color: {CyberpunkColors.BG_PANEL};
    border: 2px solid {CyberpunkColors.BTN_SAVE};
    color: {CyberpunkColors.BTN_SAVE};
}}

QPushButton#saveButton:hover {{
    background-color: rgba(255, 0, 110, 0.15);
}}

/* Window Button */
QPushButton#windowButton {{
    background-color: {CyberpunkColors.BG_PANEL};
    border: 2px solid {CyberpunkColors.BTN_WINDOW};
    color: {CyberpunkColors.BTN_WINDOW};
}}

QPushButton#windowButton:hover {{
    background-color: rgba(139, 92, 246, 0.15);
}}

/* History Button */
QPushButton#historyButton {{
    background-color: {CyberpunkColors.BG_PANEL};
    border: 2px solid {CyberpunkColors.BTN_HISTORY};
    color: {CyberpunkColors.BTN_HISTORY};
}}

QPushButton#historyButton:hover {{
    background-color: rgba(59, 130, 246, 0.15);
}}

/* Quit Button */
QPushButton#quitButton {{
    background-color: {CyberpunkColors.BG_PANEL};
    border: 2px solid {CyberpunkColors.BTN_QUIT};
    color: {CyberpunkColors.BTN_QUIT};
}}

QPushButton#quitButton:hover {{
    background-color: rgba(239, 68, 68, 0.15);
}}

/* Reset Button */
QPushButton#resetButton {{
    background-color: transparent;
    border: 1px solid {CyberpunkColors.TEXT_DIM};
    color: {CyberpunkColors.TEXT_SECONDARY};
    padding: 6px 12px;
    min-height: 28px;
}}

QPushButton#resetButton:hover {{
    border-color: {CyberpunkColors.CYAN};
    color: {CyberpunkColors.CYAN};
}}

/* ============================
   CHECKBOXES - Cyber Style
   ============================ */

QCheckBox {{
    color: {CyberpunkColors.TEXT_PRIMARY};
    spacing: 8px;
    font-size: 10pt;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {CyberpunkColors.TEXT_DIM};
    border-radius: 4px;
    background-color: {CyberpunkColors.BG_INPUT};
}}

QCheckBox::indicator:hover {{
    border-color: {CyberpunkColors.CYAN};
}}

QCheckBox::indicator:checked {{
    background-color: {CyberpunkColors.CYAN};
    border-color: {CyberpunkColors.CYAN};
}}

/* ============================
   SLIDERS - Neon Glow
   ============================ */

QSlider::groove:horizontal {{
    background-color: {CyberpunkColors.SLIDER_TRACK};
    height: 6px;
    border-radius: 3px;
    border: 1px solid {CyberpunkColors.TEXT_DIM};
}}

QSlider::handle:horizontal {{
    background-color: {CyberpunkColors.CYAN};
    border: 2px solid {CyberpunkColors.CYAN};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background-color: #00ffff;
    border-color: #00ffff;
    box-shadow: 0 0 12px {CyberpunkColors.GLOW_CYAN};
}}

QSlider::sub-page:horizontal {{
    background-color: {CyberpunkColors.CYAN};
    border-radius: 3px;
}}

/* ============================
   COMBOBOX - Dropdown Style
   ============================ */

QComboBox {{
    background-color: {CyberpunkColors.BG_INPUT};
    color: {CyberpunkColors.TEXT_PRIMARY};
    border: 2px solid {CyberpunkColors.TEXT_DIM};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 10pt;
    min-height: 32px;
}}

QComboBox:hover {{
    border-color: {CyberpunkColors.CYAN};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {CyberpunkColors.TEXT_SECONDARY};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {CyberpunkColors.BG_PANEL};
    color: {CyberpunkColors.TEXT_PRIMARY};
    border: 2px solid {CyberpunkColors.CYAN};
    border-radius: 6px;
    selection-background-color: rgba(0, 217, 255, 0.2);
    selection-color: {CyberpunkColors.CYAN};
    padding: 4px;
}}

/* ============================
   TEXT EDIT - Output Display
   ============================ */

QTextEdit {{
    background-color: {CyberpunkColors.BG_DARK};
    color: {CyberpunkColors.TEXT_PRIMARY};
    border: none;
    border-radius: 6px;
    padding: 16px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    line-height: 1.4;
    selection-background-color: rgba(0, 217, 255, 0.3);
}}

QTextEdit:focus {{
    border: 2px solid {CyberpunkColors.BLUE_PURPLE};
}}

/* ============================
   PROGRESS BAR - Neon Style
   ============================ */

QProgressBar {{
    background-color: {CyberpunkColors.BG_INPUT};
    border: 2px solid {CyberpunkColors.CYAN};
    border-radius: 6px;
    text-align: center;
    color: {CyberpunkColors.TEXT_PRIMARY};
    font-weight: 600;
    height: 24px;
}}

QProgressBar::chunk {{
    background-color: {CyberpunkColors.CYAN};
    border-radius: 4px;
}}

/* ============================
   SCROLLBAR - Minimal Dark
   ============================ */

QScrollBar:vertical {{
    background-color: {CyberpunkColors.BG_DARK};
    width: 10px;
    border-radius: 5px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {CyberpunkColors.TEXT_DIM};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {CyberpunkColors.CYAN};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {CyberpunkColors.BG_DARK};
    height: 10px;
    border-radius: 5px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: {CyberpunkColors.TEXT_DIM};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {CyberpunkColors.CYAN};
}}

/* ============================
   TOOLTIPS
   ============================ */

QToolTip {{
    background-color: {CyberpunkColors.BG_PANEL};
    color: {CyberpunkColors.TEXT_PRIMARY};
    border: 2px solid {CyberpunkColors.CYAN};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 9pt;
}}
"""


def get_cyberpunk_font():
    """Returns modern font for cyberpunk theme"""
    font_families = [
        'Inter',
        'Segoe UI',
        'Roboto',
        'Arial'
    ]
    
    for family in font_families:
        if family in QFontDatabase.families():
            font = QFont(family, 10)
            font.setStyleHint(QFont.StyleHint.SansSerif)
            return font
    
    font = QFont()
    font.setStyleHint(QFont.StyleHint.SansSerif)
    font.setPointSize(10)
    return font


def get_cyberpunk_mono_font():
    """Returns monospace font for code/output"""
    font_families = [
        'Consolas',
        'Courier New',
        'Monaco',
        'Monospace'
    ]
    
    for family in font_families:
        if family in QFontDatabase.families():
            font = QFont(family, 9)
            font.setStyleHint(QFont.StyleHint.Monospace)
            return font
    
    font = QFont()
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(9)
    return font