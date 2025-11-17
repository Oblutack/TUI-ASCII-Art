# styles/cyberpunk_theme.py
"""
Cyberpunk Terminal UI Theme
Sharp corners, neon accents, high contrast
Inspired by TUI apps like Bagels
"""

CYBERPUNK_THEME = """
/* ============================
   GLOBAL STYLES - Dark & Sharp
   ============================ */

QMainWindow {
    background-color: #0a0e1a;
    color: #e0e0e0;
}

QWidget {
    background-color: #0a0e1a;
    color: #e0e0e0;
    font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
    font-size: 11pt;
}

/* ============================
   FRAMES - Sharp Boxed Design
   ============================ */

QFrame {
    background-color: #12172b;
    border: 2px solid #1e2742;
    border-radius: 0px;  /* Sharp corners! */
    padding: 12px;
}

QFrame#titleFrame {
    background-color: #0a0e1a;
    border: 2px solid #ff6b00;
    border-radius: 0px;
    padding: 16px;
    margin-bottom: 8px;
}

QFrame#controlPanel {
    background-color: #12172b;
    border: 2px solid #1e2742;
    border-radius: 0px;
    padding: 16px;
}

QFrame#displayPanel {
    background-color: #0a0e1a;
    border: 3px solid #00d9ff;
    border-radius: 0px;
    padding: 16px;
}

/* ============================
   BUTTONS - Neon & Sharp
   ============================ */

QPushButton {
    background-color: #1e2742;
    color: #00d9ff;
    border: 2px solid #2a3f5f;
    border-radius: 0px;  /* Sharp corners */
    padding: 12px 24px;
    font-weight: bold;
    font-size: 11pt;
    min-height: 35px;
}

QPushButton:hover {
    background-color: #2a3f5f;
    border: 2px solid #00d9ff;
    color: #00ffff;
    /* Neon glow effect */
}

QPushButton:pressed {
    background-color: #0d1525;
    border: 2px solid #0099cc;
}

QPushButton:disabled {
    background-color: #0d1525;
    color: #4a5568;
    border: 2px solid #1a1f35;
}

/* Load Button - Cyan accent */
QPushButton#loadButton {
    border: 2px solid #00d9ff;
    color: #00d9ff;
}

QPushButton#loadButton:hover {
    background-color: #00d9ff;
    color: #0a0e1a;
    border: 2px solid #00ffff;
}

/* Export Button - Green accent */
QPushButton#exportButton {
    border: 2px solid #00ff88;
    color: #00ff88;
}

QPushButton#exportButton:hover {
    background-color: #00ff88;
    color: #0a0e1a;
    border: 2px solid #00ffaa;
}

/* Quit Button - Pink/Red accent */
QPushButton#quitButton {
    border: 2px solid #ff006e;
    color: #ff006e;
}

QPushButton#quitButton:hover {
    background-color: #ff006e;
    color: #ffffff;
    border: 2px solid #ff1a8c;
}

/* ============================
   CHECKBOXES - Cyberpunk Style
   ============================ */

QCheckBox {
    color: #e0e0e0;
    spacing: 10px;
    font-size: 11pt;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #2a3f5f;
    border-radius: 0px;  /* Sharp corners */
    background-color: #0d1525;
}

QCheckBox::indicator:hover {
    border: 2px solid #00d9ff;
}

QCheckBox::indicator:checked {
    background-color: #00d9ff;
    border: 2px solid #00ffff;
    image: none;
}

QCheckBox::indicator:checked::after {
    content: "✓";
}

/* ============================
   SLIDERS - Neon Track
   ============================ */

QSlider::groove:horizontal {
    background-color: #1e2742;
    height: 10px;
    border-radius: 0px;
    border: 2px solid #2a3f5f;
}

QSlider::handle:horizontal {
    background-color: #00d9ff;
    border: 2px solid #00ffff;
    width: 24px;
    height: 24px;
    margin: -9px 0;
    border-radius: 0px;  /* Sharp square handle */
}

QSlider::handle:horizontal:hover {
    background-color: #00ffff;
    border: 2px solid #ffffff;
}

QSlider::sub-page:horizontal {
    background-color: #0099cc;
    border-radius: 0px;
}

/* ============================
   TEXT DISPLAYS - Terminal Look
   ============================ */

QTextEdit, QPlainTextEdit {
    background-color: #0a0e1a;
    color: #00ff88;
    border: 2px solid #1e2742;
    border-radius: 0px;
    padding: 16px;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 10pt;
    line-height: 1.5;
    selection-background-color: #2a3f5f;
    selection-color: #00ffff;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #00d9ff;
}

/* ============================
   LABELS - Sharp Typography
   ============================ */

QLabel {
    color: #a0aec0;
    font-size: 11pt;
    padding: 4px;
    border: none;
    background: transparent;
}

QLabel#titleLabel {
    color: #ff6b00;
    font-size: 16pt;
    font-weight: bold;
    padding: 0px;
    letter-spacing: 2px;
}

QLabel#subtitleLabel {
    color: #718096;
    font-size: 10pt;
}

QLabel#sectionLabel {
    color: #00d9ff;
    font-size: 12pt;
    font-weight: bold;
    border-bottom: 2px solid #00d9ff;
    padding-bottom: 4px;
    margin-bottom: 8px;
}

QLabel#valueLabel {
    color: #00ffff;
    font-weight: bold;
    font-size: 12pt;
}

/* ============================
   SCROLL BARS - Minimal
   ============================ */

QScrollBar:vertical {
    background-color: #0a0e1a;
    width: 12px;
    border-radius: 0px;
    border: 1px solid #1e2742;
}

QScrollBar::handle:vertical {
    background-color: #2a3f5f;
    border-radius: 0px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00d9ff;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0a0e1a;
    height: 12px;
    border-radius: 0px;
    border: 1px solid #1e2742;
}

QScrollBar::handle:horizontal {
    background-color: #2a3f5f;
    border-radius: 0px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #00d9ff;
}

/* ============================
   TOOLTIPS
   ============================ */

QToolTip {
    background-color: #12172b;
    color: #00d9ff;
    border: 2px solid #00d9ff;
    padding: 8px;
    border-radius: 0px;
    font-size: 10pt;
}

/* ============================
   LINE EDIT
   ============================ */

QLineEdit {
    background-color: #0d1525;
    color: #e0e0e0;
    border: 2px solid #2a3f5f;
    border-radius: 0px;
    padding: 10px;
    font-size: 11pt;
}

QLineEdit:focus {
    border: 2px solid #00d9ff;
}

/* ============================
   SPIN BOX
   ============================ */

QSpinBox {
    background-color: #0d1525;
    color: #e0e0e0;
    border: 2px solid #2a3f5f;
    border-radius: 0px;
    padding: 8px;
}

QSpinBox:focus {
    border: 2px solid #00d9ff;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #1e2742;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #00d9ff;
}

/* ============================
   PROGRESS BAR
   ============================ */

QProgressBar {
    background-color: #12172b;
    border: 2px solid #2a3f5f;
    border-radius: 0px;
    text-align: center;
    color: #00d9ff;
    font-weight: bold;
    height: 28px;
}

QProgressBar::chunk {
    background-color: #00d9ff;
    border-radius: 0px;
}
"""

# Cyberpunk color palette
class CyberpunkColors:
    """Neon cyberpunk color scheme"""
    
    # Backgrounds
    BG_DARK = "#0a0e1a"       # Darkest - main background
    BG_MEDIUM = "#12172b"     # Medium - panels
    BG_LIGHT = "#1e2742"      # Light - buttons
    
    # Borders
    BORDER_DARK = "#1a1f35"
    BORDER_MEDIUM = "#2a3f5f"
    BORDER_LIGHT = "#3d5a80"
    
    # Text
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#a0aec0"
    TEXT_TERTIARY = "#718096"
    TEXT_DIM = "#4a5568"
    
    # Neon accents
    CYAN = "#00d9ff"          # Primary accent
    CYAN_BRIGHT = "#00ffff"   # Hover/bright
    CYAN_DARK = "#0099cc"     # Pressed
    
    GREEN = "#00ff88"         # Success/export
    GREEN_BRIGHT = "#00ffaa"  # Hover
    GREEN_ASCII = "#00ff88"   # ASCII art text
    
    PINK = "#ff006e"          # Danger/quit
    PINK_BRIGHT = "#ff1a8c"   # Hover
    
    ORANGE = "#ff6b00"        # Warning/title
    ORANGE_BRIGHT = "#ff8c1a" # Hover
    
    PURPLE = "#b794f6"        # Special
    YELLOW = "#ffd600"        # Highlight


def get_cyberpunk_font():
    """Returns the best monospace font for cyberpunk aesthetic"""
    from PyQt6.QtGui import QFont, QFontDatabase
    
    # Preferred fonts for terminal look
    font_families = [
        'JetBrains Mono',
        'Fira Code', 
        'Source Code Pro',
        'Courier New',
        'Consolas',
        'Monaco'
    ]
    
    for family in font_families:
        if family in QFontDatabase.families():
            font = QFont(family, 11)
            font.setStyleHint(QFont.StyleHint.Monospace)
            return font
    
    # Fallback
    font = QFont()
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(11)
    return font