# styles/compact_theme.py
"""
Compact Transparent Theme with Custom Color Palette
Sharp corners, tight spacing, semi-transparent background
"""

COMPACT_THEME = """
/* ============================
   GLOBAL - Compact & Transparent
   ============================ */

QMainWindow {
    background-color: rgba(48, 41, 47, 245);  /* shadow-grey with transparency */
    color: #e0e0e0;
}

QWidget {
    background-color: transparent;
    color: #e0e0e0;
    font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
    font-size: 10pt;
}

/* ============================
   FRAMES - Compact Boxes
   ============================ */

QFrame {
    background-color: rgba(65, 63, 84, 230);  /* vintage-grape semi-transparent */
    border: 2px solid #5f5aa2;  /* dusty-grape */
    border-radius: 0px;
    padding: 8px;
}

QFrame#titleFrame {
    background-color: rgba(48, 41, 47, 240);  /* shadow-grey */
    border: 2px solid #5f5aa2;  /* dusty-grape */
    padding: 10px;
    margin-bottom: 6px;
}

QFrame#controlPanel {
    background-color: rgba(63, 64, 69, 230);  /* gunmetal semi-transparent */
    border: 2px solid #413f54;  /* vintage-grape */
    padding: 10px;
}

QFrame#displayPanel {
    background-color: rgba(48, 41, 47, 240);  /* shadow-grey */
    border: 2px solid #5f5aa2;  /* dusty-grape */
    padding: 10px;
}

/* ============================
   BUTTONS - Compact & Sharp
   ============================ */

QPushButton {
    background-color: rgba(65, 63, 84, 200);  /* vintage-grape */
    color: #5f5aa2;  /* dusty-grape */
    border: 2px solid #413f54;
    border-radius: 0px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 10pt;
    min-height: 30px;
}

QPushButton:hover {
    background-color: rgba(95, 90, 162, 240);  /* dusty-grape */
    border: 2px solid #5f5aa2;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: rgba(53, 86, 145, 200);  /* dusk-blue */
    border: 2px solid #355691;
}

QPushButton:disabled {
    background-color: rgba(48, 41, 47, 150);
    color: #666666;
    border: 2px solid #30292f;
}

/* Load Button */
QPushButton#loadButton {
    border: 2px solid #5f5aa2;
    color: #5f5aa2;
}

QPushButton#loadButton:hover {
    background-color: rgba(95, 90, 162, 220);
    color: #ffffff;
}

/* Export Button */
QPushButton#exportButton {
    border: 2px solid #355691;  /* dusk-blue */
    color: #355691;
}

QPushButton#exportButton:hover {
    background-color: rgba(53, 86, 145, 220);
    color: #ffffff;
}

/* Quit Button */
QPushButton#quitButton {
    border: 2px solid #8b5f65;
    color: #d89aa3;
}

QPushButton#quitButton:hover {
    background-color: rgba(139, 95, 101, 200);
    color: #ffffff;
}

/* ============================
   CHECKBOXES - Compact
   ============================ */

QCheckBox {
    color: #e0e0e0;
    spacing: 6px;
    font-size: 9pt;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #413f54;
    border-radius: 0px;
    background-color: rgba(48, 41, 47, 240);
}

QCheckBox::indicator:hover {
    border: 2px solid #5f5aa2;
}

QCheckBox::indicator:checked {
    background-color: #5f5aa2;
    border: 2px solid #5f5aa2;
}

/* ============================
   SLIDERS - Compact
   ============================ */

QSlider::groove:horizontal {
    background-color: rgba(65, 63, 84, 200);
    height: 6px;
    border-radius: 0px;
    border: 1px solid #413f54;
}

QSlider::handle:horizontal {
    background-color: #5f5aa2;
    border: 2px solid #5f5aa2;
    width: 18px;
    height: 18px;
    margin: -7px 0;
    border-radius: 0px;
}

QSlider::handle:horizontal:hover {
    background-color: #7b76c2;
    border: 2px solid #7b76c2;
}

QSlider::sub-page:horizontal {
    background-color: #355691;  /* dusk-blue */
    border-radius: 0px;
}

/* ============================
   TEXT DISPLAYS - Compact
   ============================ */

QTextEdit, QPlainTextEdit {
    background-color: rgba(48, 41, 47, 230);
    color: #9b96d6;  /* light dusty-grape */
    border: 2px solid #413f54;
    border-radius: 0px;
    padding: 10px;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 9pt;
    line-height: 1.3;
    selection-background-color: rgba(95, 90, 162, 150);
    selection-color: #ffffff;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #5f5aa2;
}

/* ============================
   LABELS - Compact
   ============================ */

QLabel {
    color: #b0b0b0;
    font-size: 9pt;
    padding: 2px;
    border: none;
    background: transparent;
}

QLabel#titleLabel {
    color: #5f5aa2;  /* dusty-grape */
    font-size: 13pt;
    font-weight: bold;
    letter-spacing: 1px;
}

QLabel#subtitleLabel {
    color: #808080;
    font-size: 8pt;
}

QLabel#sectionLabel {
    color: #5f5aa2;
    font-size: 10pt;
    font-weight: bold;
    border-bottom: 1px solid #5f5aa2;
    padding-bottom: 3px;
    margin-bottom: 6px;
}

QLabel#valueLabel {
    color: #7b76c2;
    font-weight: bold;
    font-size: 11pt;
}

/* ============================
   SCROLL BARS - Minimal
   ============================ */

QScrollBar:vertical {
    background-color: rgba(48, 41, 47, 240);
    width: 10px;
    border-radius: 0px;
    border: 1px solid #413f54;
}

QScrollBar::handle:vertical {
    background-color: #413f54;
    border-radius: 0px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5f5aa2;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: rgba(48, 41, 47, 240);
    height: 10px;
    border-radius: 0px;
    border: 1px solid #413f54;
}

QScrollBar::handle:horizontal {
    background-color: #413f54;
    border-radius: 0px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5f5aa2;
}

/* ============================
   TOOLTIPS
   ============================ */

QToolTip {
    background-color: rgba(65, 63, 84, 240);
    color: #e0e0e0;
    border: 2px solid #5f5aa2;
    padding: 6px;
    border-radius: 0px;
    font-size: 9pt;
}

/* ============================
   LINE EDIT
   ============================ */

QLineEdit {
    background-color: rgba(48, 41, 47, 240);
    color: #e0e0e0;
    border: 2px solid #413f54;
    border-radius: 0px;
    padding: 6px;
    font-size: 10pt;
}

QLineEdit:focus {
    border: 2px solid #5f5aa2;
}

/* ============================
   PROGRESS BAR
   ============================ */

QProgressBar {
    background-color: rgba(65, 63, 84, 200);
    border: 2px solid #413f54;
    border-radius: 0px;
    text-align: center;
    color: #e0e0e0;
    font-weight: bold;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #5f5aa2;
    border-radius: 0px;
}
"""

# Custom color palette
class CompactColors:
    """Your custom color scheme"""
    
    # Base colors from palette
    SHADOW_GREY = "#30292f"
    VINTAGE_GRAPE = "#413f54"
    DUSTY_GRAPE = "#5f5aa2"
    DUSK_BLUE = "#355691"
    GUNMETAL = "#3f4045"
    
    # Derived colors for UI
    TEXT_PRIMARY = "#e0e0e0"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_DIM = "#808080"
    
    # Accent variations
    GRAPE_LIGHT = "#7b76c2"
    GRAPE_BRIGHT = "#9b96d6"
    
    # Alpha versions for transparency
    SHADOW_ALPHA = "rgba(48, 41, 47, 245)"      
    VINTAGE_ALPHA = "rgba(65, 63, 84, 230)"     
    DUSTY_ALPHA = "rgba(95, 90, 162, 240)"      
    GUNMETAL_ALPHA = "rgba(63, 64, 69, 230)" 


def get_compact_font():
    """Returns compact monospace font"""
    from PyQt6.QtGui import QFont, QFontDatabase
    
    font_families = [
        'JetBrains Mono',
        'Fira Code', 
        'Consolas',
        'Courier New',
        'Monaco'
    ]
    
    for family in font_families:
        if family in QFontDatabase.families():
            font = QFont(family, 10)
            font.setStyleHint(QFont.StyleHint.Monospace)
            return font
    
    font = QFont()
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(10)
    return font
