# src/widget_window.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont

class AsciiWidget(QWidget):
    """Floating ASCII art widget for Windows"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.dragging = False
        self.offset = QPoint()
        
    def init_ui(self):
        # Frameless window that stays on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Semi-transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout
        layout = QVBoxLayout()
        
        # ASCII display area
        self.ascii_display = QTextEdit()
        self.ascii_display.setReadOnly(True)
        self.ascii_display.setFont(QFont('Courier New', 8))
        self.ascii_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 46, 200);
                color: #a6e3a1;
                border: 2px solid #89b4fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.ascii_display)
        self.setLayout(layout)
        
        # Default size
        self.resize(400, 300)
        
    def set_ascii_text(self, text):
        """Update ASCII art display"""
        self.ascii_display.setText(text)
        
    def mousePressEvent(self, event):
        """Enable dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        """Handle dragging"""
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))
            
    def mouseReleaseEvent(self, event):
        """Stop dragging"""
        self.dragging = False
        
    def mouseDoubleClickEvent(self, event):
        """Double click to close"""
        self.close()