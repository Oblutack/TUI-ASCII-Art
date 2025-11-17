# styles/terminal_theme.py
"""
Complete Terminal UI aesthetic theme for ASCII Art Generator
Inspired by retro terminals and modern TUI apps like Posting
"""

TERMINAL_THEME = """
/* ============================
   GLOBAL STYLES
   ============================ */

QMainWindow {
    background-color: #0d1117;
    color: #c9d1d9;
}

QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
    font-size: 10pt;
}

/* ============================
   BUTTONS
   ============================ */

QPushButton {
    background-color: #21262d;
    color: #58a6ff;
    border: 2px solid #30363d;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 11pt;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #58a6ff;
    color: #79c0ff;
}

QPushButton:pressed {
    background-color: #161b22;
    border-color: #1f6feb;
    color: #58a6ff;
}

QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}

/* Special button - Quit */
QPushButton#quitButton {
    background-color: #1a1d23;
    border-color: #f85149;
    color: #f85149;
}

QPushButton#quitButton:hover {
    background-color: #2d1517;
    border-color: #ff7b72;
    color: #ff7b72;
}

/* Special button - Export */
QPushButton#exportButton {
    background-color: #1a1d23;
    border-color: #3fb950;
    color: #3fb950;
}

QPushButton#exportButton:hover {
    background-color: #1b2b1f;
    border-color: #56d364;
    color: #56d364;
}

/* ============================
   CHECKBOXES
   ============================ */

QCheckBox {
    color: #c9d1d9;
    spacing: 8px;
    font-size: 10pt;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #30363d;
    border-radius: 4px;
    background-color: #0d1117;
}

QCheckBox::indicator:hover {
    border-color: #58a6ff;
}

QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #58a6ff;
    image: url(none);
}

QCheckBox::indicator:checked:hover {
    background-color: #58a6ff;
}

/* ============================
   SLIDERS
   ============================ */

QSlider::groove:horizontal {
    background-color: #21262d;
    height: 8px;
    border-radius: 4px;
    border: 1px solid #30363d;
}

QSlider::handle:horizontal {
    background-color: #58a6ff;
    border: 2px solid #1f6feb;
    width: 20px;
    height: 20px;
    margin: -7px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background-color: #79c0ff;
    border-color: #58a6ff;
}

QSlider::sub-page:horizontal {
    background-color: #1f6feb;
    border-radius: 4px;
}

/* ============================
   TEXT DISPLAYS
   ============================ */

QTextEdit, QPlainTextEdit {
    background-color: #0d1117;
    color: #7ee787;
    border: 2px solid #30363d;
    border-radius: 8px;
    padding: 12px;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 9pt;
    line-height: 1.4;
    selection-background-color: #1f6feb;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #58a6ff;
}

/* ============================
   LABELS
   ============================ */

QLabel {
    color: #8b949e;
    font-size: 10pt;
    padding: 2px;
}

QLabel#titleLabel {
    color: #58a6ff;
    font-size: 14pt;
    font-weight: bold;
    padding: 8px;
}

QLabel#valueLabel {
    color: #79c0ff;
    font-weight: bold;
    font-size: 11pt;
}

/* ============================
   SCROLL BARS
   ============================ */

QScrollBar:vertical {
    background-color: #0d1117;
    width: 14px;
    border-radius: 7px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 7px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0d1117;
    height: 14px;
    border-radius: 7px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 7px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #484f58;
}

/* ============================
   FRAMES & CONTAINERS
   ============================ */

QFrame {
    background-color: #161b22;
    border: 2px solid #30363d;
    border-radius: 8px;
    padding: 8px;
}

QFrame#controlPanel {
    background-color: #0d1117;
    border: 2px solid #21262d;
    border-radius: 10px;
    padding: 12px;
}

QFrame#displayPanel {
    background-color: #0d1117;
    border: 2px solid #30363d;
    border-radius: 10px;
}

/* ============================
   TOOLTIPS
   ============================ */

QToolTip {
    background-color: #161b22;
    color: #c9d1d9;
    border: 2px solid #30363d;
    padding: 6px;
    border-radius: 4px;
    font-size: 9pt;
}

/* ============================
   STATUS BAR
   ============================ */

QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 2px solid #21262d;
    font-size: 9pt;
    padding: 4px;
}

QStatusBar::item {
    border: none;
}

/* ============================
   MENU BAR (if used)
   ============================ */

QMenuBar {
    background-color: #0d1117;
    color: #c9d1d9;
    border-bottom: 2px solid #21262d;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

QMenu {
    background-color: #161b22;
    border: 2px solid #30363d;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

/* ============================
   PROGRESS BAR
   ============================ */

QProgressBar {
    background-color: #161b22;
    border: 2px solid #30363d;
    border-radius: 6px;
    text-align: center;
    color: #c9d1d9;
    font-weight: bold;
    height: 24px;
}

QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 4px;
}

/* ============================
   LINE EDIT (Input fields)
   ============================ */

QLineEdit {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 2px solid #30363d;
    border-radius: 6px;
    padding: 8px;
    font-size: 10pt;
}

QLineEdit:focus {
    border-color: #58a6ff;
}

/* ============================
   SPIN BOX
   ============================ */

QSpinBox {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 2px solid #30363d;
    border-radius: 6px;
    padding: 6px;
}

QSpinBox:focus {
    border-color: #58a6ff;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #21262d;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #30363d;
}
"""

# Color palette for programmatic access
class TerminalColors:
    """Terminal color palette - GitHub Dark theme inspired"""
    
    # Backgrounds
    BG_PRIMARY = "#0d1117"
    BG_SECONDARY = "#161b22"
    BG_TERTIARY = "#21262d"
    
    # Borders
    BORDER_PRIMARY = "#30363d"
    BORDER_SECONDARY = "#21262d"
    BORDER_ACTIVE = "#58a6ff"
    
    # Text
    TEXT_PRIMARY = "#c9d1d9"
    TEXT_SECONDARY = "#8b949e"
    TEXT_TERTIARY = "#484f58"
    
    # Accent colors
    BLUE = "#58a6ff"
    BLUE_LIGHT = "#79c0ff"
    BLUE_DARK = "#1f6feb"
    
    GREEN = "#3fb950"
    GREEN_LIGHT = "#56d364"
    GREEN_ASCII = "#7ee787"
    
    RED = "#f85149"
    RED_LIGHT = "#ff7b72"
    
    ORANGE = "#d29922"
    PURPLE = "#bc8cff"
    CYAN = "#76e3ea"
    YELLOW = "#f0883e"


def get_custom_font():
    """Returns the best available monospace font"""
    from PyQt6.QtGui import QFont, QFontDatabase
    
    # Try to load custom font if available
    font_families = ['JetBrains Mono', 'Fira Code', 'Courier New', 'Consolas', 'Monaco']
    
    for family in font_families:
        if family in QFontDatabase.families():
            return QFont(family, 10)
    
    # Fallback to system monospace
    font = QFont()
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(10)
    return font