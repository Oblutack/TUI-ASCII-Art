"""
History Panel - Gallery view of conversion history
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QListWidgetItem, QTextEdit,
                             QFrame, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from styles.compact_theme import CompactColors, get_compact_font
from history_manager import HistoryManager, HistoryEntry


class HistoryPanel(QDialog):
    """Dialog showing conversion history gallery"""
    
    entry_selected = pyqtSignal(object)  # Emits HistoryEntry
    
    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.init_ui()
        self.load_history_items()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("ASCII Art History & Gallery")
        self.setModal(False)
        self.setMinimumSize(900, 600)
        self.setFont(get_compact_font())
        
        # Styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CompactColors.SHADOW_GREY};
            }}
            QLabel {{
                color: {CompactColors.TEXT_PRIMARY};
            }}
            QListWidget {{
                background-color: rgba(48, 41, 47, 230);
                color: {CompactColors.TEXT_PRIMARY};
                border: 2px solid {CompactColors.VINTAGE_GRAPE};
                border-radius: 0px;
                padding: 5px;
                font-size: 9pt;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {CompactColors.VINTAGE_GRAPE};
            }}
            QListWidget::item:selected {{
                background-color: {CompactColors.DUSTY_GRAPE};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: rgba(95, 90, 162, 150);
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("▌ HISTORY & GALLERY")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {CompactColors.DUSTY_GRAPE};
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        
        # Statistics
        stats = self.history_manager.get_statistics()
        stats_label = QLabel(f"Total: {stats['total']} | Images: {stats['images']} | GIFs: {stats['gifs']}")
        stats_label.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt; padding: 5px;")
        
        layout.addWidget(title_label)
        layout.addWidget(stats_label)
        
        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: History list
        list_frame = QFrame()
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        list_label = QLabel("▸ RECENT CONVERSIONS")
        list_label.setStyleSheet(f"color: {CompactColors.DUSTY_GRAPE}; font-weight: bold; font-size: 10pt; padding: 5px;")
        
        self.history_list = QListWidget()
        self.history_list.setMinimumWidth(300)
        self.history_list.currentRowChanged.connect(self.on_selection_changed)
        
        list_layout.addWidget(list_label)
        list_layout.addWidget(self.history_list)
        list_frame.setLayout(list_layout)
        
        # Right: Preview and details
        preview_frame = QFrame()
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_label = QLabel("▸ PREVIEW")
        preview_label.setStyleSheet(f"color: {CompactColors.DUSTY_GRAPE}; font-weight: bold; font-size: 10pt; padding: 5px;")
        
        # Details
        self.details_label = QLabel("Select an item to preview")
        self.details_label.setStyleSheet(f"""
            QLabel {{
                color: {CompactColors.TEXT_SECONDARY};
                font-size: 9pt;
                padding: 10px;
                background-color: rgba(65, 63, 84, 200);
                border: 2px solid {CompactColors.VINTAGE_GRAPE};
            }}
        """)
        self.details_label.setWordWrap(True)
        
        # Preview
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(get_compact_font())
        self.preview_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(48, 41, 47, 230);
                color: {CompactColors.GRAPE_BRIGHT};
                border: 2px solid {CompactColors.VINTAGE_GRAPE};
                padding: 10px;
                font-size: 8pt;
            }}
        """)
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.details_label)
        preview_layout.addWidget(self.preview_text)
        preview_frame.setLayout(preview_layout)
        
        splitter.addWidget(list_frame)
        splitter.addWidget(preview_frame)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.load_btn = QPushButton("📂 LOAD SELECTED")
        self.load_btn.setMinimumHeight(35)
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.on_load_selected)
        self.load_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CompactColors.DUSTY_GRAPE};
                color: white;
                border: 2px solid {CompactColors.GRAPE_LIGHT};
                border-radius: 0px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {CompactColors.GRAPE_LIGHT};
            }}
            QPushButton:disabled {{
                background-color: rgba(65, 63, 84, 150);
                color: {CompactColors.TEXT_DIM};
                border-color: {CompactColors.VINTAGE_GRAPE};
            }}
        """)
        
        self.widget_btn = QPushButton("🪟 OPEN IN WIDGET")
        self.widget_btn.setMinimumHeight(35)
        self.widget_btn.setEnabled(False)
        self.widget_btn.clicked.connect(self.on_open_widget)
        self.widget_btn.setStyleSheet(self.load_btn.styleSheet())
        
        clear_btn = QPushButton("🗑 CLEAR HISTORY")
        clear_btn.setMinimumHeight(35)
        clear_btn.clicked.connect(self.on_clear_history)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(139, 95, 101, 200);
                color: white;
                border: 2px solid #8b5f65;
                border-radius: 0px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: rgba(216, 154, 163, 255);
            }}
        """)
        
        close_btn = QPushButton("✕ CLOSE")
        close_btn.setMinimumHeight(35)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(65, 63, 84, 200);
                color: {CompactColors.TEXT_PRIMARY};
                border: 2px solid {CompactColors.VINTAGE_GRAPE};
                border-radius: 0px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {CompactColors.VINTAGE_GRAPE};
            }}
        """)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.widget_btn)
        button_layout.addStretch()
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_history_items(self):
        """Load history items into list"""
        self.history_list.clear()
        entries = self.history_manager.get_all_entries()
        
        for entry in entries:
            item = QListWidgetItem(entry.get_display_name())
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)
    
    def on_selection_changed(self, index):
        """Handle selection change"""
        if index >= 0:
            item = self.history_list.item(index)
            entry: HistoryEntry = item.data(Qt.ItemDataRole.UserRole)
            
            # Update details
            details = f"""
File: {entry.file_name}
Type: {'GIF Animation' if entry.is_gif else 'Static Image'}
Time: {entry.timestamp.split('T')[1].split('.')[0]}
Settings: Width={entry.settings.get('width', 'N/A')}, 
          Style={entry.settings.get('char_set', 'Default')}, 
          Brightness={entry.settings.get('brightness', 0)}, 
          Contrast={entry.settings.get('contrast', 100)}%
            """.strip()
            self.details_label.setText(details)
            
            # Update preview
            preview = entry.get_preview(20)
            self.preview_text.setPlainText(preview + "\n\n... (truncated)")
            
            # Enable buttons
            self.load_btn.setEnabled(True)
            self.widget_btn.setEnabled(True)
        else:
            self.details_label.setText("Select an item to preview")
            self.preview_text.clear()
            self.load_btn.setEnabled(False)
            self.widget_btn.setEnabled(False)
    
    def on_load_selected(self):
        """Load selected entry"""
        current_row = self.history_list.currentRow()
        if current_row >= 0:
            item = self.history_list.item(current_row)
            entry: HistoryEntry = item.data(Qt.ItemDataRole.UserRole)
            self.entry_selected.emit(entry)
    
    def on_open_widget(self):
        """Open selected entry in widget"""
        current_row = self.history_list.currentRow()
        if current_row >= 0:
            item = self.history_list.item(current_row)
            entry: HistoryEntry = item.data(Qt.ItemDataRole.UserRole)
            # Emit with special flag for widget
            entry.open_in_widget = True
            self.entry_selected.emit(entry)
    
    def on_clear_history(self):
        """Clear all history"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history_manager.clear_history()
            self.load_history_items()
            self.details_label.setText("History cleared")
            self.preview_text.clear()