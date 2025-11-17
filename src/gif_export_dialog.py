"""
GIF Export Dialog
UI for selecting export format for animated ASCII art
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QRadioButton, QButtonGroup, QFrame, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from styles.compact_theme import CompactColors, get_compact_font
import os


class GifExportDialog(QDialog):
    """Dialog for choosing GIF export format"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_format = None
        self.output_path = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Export GIF Animation")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setFont(get_compact_font())
        
        # Apply styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CompactColors.SHADOW_GREY};
            }}
            QLabel {{
                color: {CompactColors.TEXT_PRIMARY};
            }}
            QRadioButton {{
                color: {CompactColors.TEXT_PRIMARY};
                font-size: 10pt;
                spacing: 8px;
                padding: 8px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {CompactColors.VINTAGE_GRAPE};
                border-radius: 9px;
                background-color: {CompactColors.SHADOW_GREY};
            }}
            QRadioButton::indicator:checked {{
                background-color: {CompactColors.DUSTY_GRAPE};
                border-color: {CompactColors.GRAPE_LIGHT};
            }}
            QRadioButton::indicator:hover {{
                border-color: {CompactColors.DUSTY_GRAPE};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("▌ SELECT EXPORT FORMAT")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {CompactColors.DUSTY_GRAPE};
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Choose how you want to export your animated ASCII art:")
        desc_label.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 10pt; padding: 5px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Options frame
        options_frame = QFrame()
        options_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(65, 63, 84, 230);
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                border-radius: 0px;
                padding: 15px;
            }}
        """)
        options_layout = QVBoxLayout()
        options_layout.setSpacing(15)
        
        # Radio button group
        self.format_group = QButtonGroup()
        
        # Option 1: Single TXT
        self.txt_radio = QRadioButton("📄 Single Text File")
        self.txt_radio.setChecked(True)
        txt_desc = QLabel("   All frames in one .txt file with separators\n   Best for: Viewing entire animation as text")
        txt_desc.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt; margin-left: 30px;")
        
        # Option 2: HTML
        self.html_radio = QRadioButton("🌐 Interactive HTML")
        html_desc = QLabel("   Playable HTML file with JavaScript controls\n   Best for: Sharing online, interactive viewing")
        html_desc.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt; margin-left: 30px;")
        
        # Option 3: Folder
        self.folder_radio = QRadioButton("📁 Folder of Frames")
        folder_desc = QLabel("   Each frame as separate .txt file in a folder\n   Best for: Frame-by-frame editing, analysis")
        folder_desc.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt; margin-left: 30px;")
        
        # Add to button group
        self.format_group.addButton(self.txt_radio, 1)
        self.format_group.addButton(self.html_radio, 2)
        self.format_group.addButton(self.folder_radio, 3)
        
        # Add to layout
        options_layout.addWidget(self.txt_radio)
        options_layout.addWidget(txt_desc)
        options_layout.addSpacing(10)
        
        options_layout.addWidget(self.html_radio)
        options_layout.addWidget(html_desc)
        options_layout.addSpacing(10)
        
        options_layout.addWidget(self.folder_radio)
        options_layout.addWidget(folder_desc)
        
        options_frame.setLayout(options_layout)
        layout.addWidget(options_frame)
        
        layout.addSpacing(10)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        cancel_btn = QPushButton("✕ CANCEL")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setStyleSheet(f"""
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
                border-color: #d89aa3;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        export_btn = QPushButton("💾 EXPORT")
        export_btn.setMinimumHeight(35)
        export_btn.setStyleSheet(f"""
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
                border-color: white;
            }}
        """)
        export_btn.clicked.connect(self.on_export)
        export_btn.setDefault(True)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(export_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def on_export(self):
        """Handle export button click"""
        # Determine selected format
        if self.txt_radio.isChecked():
            self.selected_format = 'txt'
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save ASCII Animation",
                "ascii_animation.txt",
                "Text Files (*.txt)"
            )
            if file_path:
                self.output_path = file_path
                self.accept()
        
        elif self.html_radio.isChecked():
            self.selected_format = 'html'
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save ASCII Animation",
                "ascii_animation.html",
                "HTML Files (*.html)"
            )
            if file_path:
                self.output_path = file_path
                self.accept()
        
        elif self.folder_radio.isChecked():
            self.selected_format = 'folder'
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "Select Folder for Frames",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            if folder_path:
                # Create subfolder for this export
                base_name = "ascii_frames"
                counter = 1
                output_folder = os.path.join(folder_path, base_name)
                
                # Find unique folder name
                while os.path.exists(output_folder):
                    output_folder = os.path.join(folder_path, f"{base_name}_{counter}")
                    counter += 1
                
                self.output_path = output_folder
                self.accept()
    
    def get_export_info(self):
        """Return selected format and output path"""
        return self.selected_format, self.output_path