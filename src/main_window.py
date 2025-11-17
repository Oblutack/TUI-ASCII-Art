import sys
import os
from pathlib import Path

# Fix paths
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(root_dir))

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QFileDialog, QCheckBox, 
                             QSlider, QLabel, QFrame)
from PyQt6.QtGui import QFont, QColor, QTextCursor, QPalette
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from rich.text import Text 

from converter import convert_image_to_ascii
from background import remove_background_from_image
from styles.compact_theme import COMPACT_THEME, get_compact_font, CompactColors


class Worker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, file_path, columns, remove_bg):
        super().__init__()
        self.file_path = file_path
        self.columns = columns
        self.remove_bg = remove_bg

    def run(self):
        try:
            image_source = self.file_path
            temp_file_path = "temp_processed_image.png"

            if self.remove_bg:
                processed_image = remove_background_from_image(self.file_path)
                if processed_image:
                    processed_image.save(temp_file_path, 'PNG')
                    image_source = temp_file_path
            
            ascii_result = convert_image_to_ascii(image_source, columns=self.columns)

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            if ascii_result:
                self.finished.emit(ascii_result)
            else:
                self.finished.emit("Error: Could not convert image.")
        except Exception as e:
            self.finished.emit(f"An unexpected error occurred:\n{e}")


class CompactTextEdit(QTextEdit):
    """Compact text display with ANSI support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_compact_font())
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
    def append_ansi_text(self, text):
        """Parse ANSI with custom colors"""
        self.clear()
        self.moveCursor(QTextCursor.MoveOperation.End)
        parts = text.split('\x1b[')
        
        for part in parts:
            if 'm' in part:
                try:
                    code_part, text_part = part.split('m', 1)
                    if not code_part:
                        continue
                    
                    color_code = int(code_part.split(';')[0])
                    color = QColor(CompactColors.GRAPE_BRIGHT)  # Default
                    
                    if 30 <= color_code <= 37:
                        colors = [
                            CompactColors.TEXT_DIM,
                            "#d89aa3",  # red
                            CompactColors.GRAPE_BRIGHT,  # green
                            "#e0c097",  # yellow
                            CompactColors.DUSTY_GRAPE,  # blue
                            "#c5a3d8",  # magenta
                            CompactColors.GRAPE_LIGHT,  # cyan
                            CompactColors.TEXT_PRIMARY  # white
                        ]
                        color = QColor(colors[color_code - 30])
                    
                    self.setTextColor(color)
                    self.insertPlainText(text_part)
                except (ValueError, IndexError):
                    self.setTextColor(QColor(CompactColors.GRAPE_BRIGHT))
                    self.insertPlainText(part)
            else:
                self.setTextColor(QColor(CompactColors.GRAPE_BRIGHT))
                self.insertPlainText(part)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Apply theme
        self.setStyleSheet(COMPACT_THEME)
        self.setFont(get_compact_font())
        
        self.setWindowTitle("ASCII GENERATOR")
        
        # Compact window size (50% smaller)
        self.setGeometry(100, 100, 700, 450)
        self.setMinimumSize(600, 400)
        
        self.last_ascii_result = None
        self.dragging = False
        self.offset = None
        
        # Tight spacing layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.main_layout)
        
        # Build compact UI
        self.create_title_bar()
        self.create_control_panel()
        self.create_display_area()
        
        # Threading
        self.thread = None
        self.worker = None

    def create_title_bar(self):
        """Compact title bar with drag support"""
        title_frame = QFrame()
        title_frame.setObjectName("titleFrame")
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(8, 6, 8, 6)
        title_layout.setSpacing(10)
        
        title_label = QLabel("▌ASCII GENERATOR")
        title_label.setObjectName("titleLabel")
        
        subtitle_label = QLabel("v1.0")
        subtitle_label.setObjectName("subtitleLabel")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        title_frame.setLayout(title_layout)
        self.main_layout.addWidget(title_frame)

    def create_control_panel(self):
        """Super compact control panel"""
        control_frame = QFrame()
        control_frame.setObjectName("controlPanel")
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(10, 8, 10, 8)
        
        # Left box - compact
        left_box = self.create_input_box()
        
        # Middle box - compact
        middle_box = self.create_width_box()
        
        # Right box - compact
        right_box = self.create_actions_box()
        
        controls_layout.addWidget(left_box, stretch=1)
        controls_layout.addWidget(middle_box, stretch=2)
        controls_layout.addWidget(right_box, stretch=1)
        
        control_frame.setLayout(controls_layout)
        self.main_layout.addWidget(control_frame)

    def create_input_box(self):
        """Compact input section"""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {CompactColors.VINTAGE_ALPHA};
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                padding: 6px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        
        label = QLabel("▸ INPUT")
        label.setObjectName("sectionLabel")
        
        self.load_button = QPushButton("LOAD")
        self.load_button.setObjectName("loadButton")
        self.load_button.setMinimumHeight(32)
        self.load_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_button.clicked.connect(self.start_processing)
        
        self.bg_checkbox = QCheckBox("RM BG")
        self.bg_checkbox.setToolTip("Remove Background")
        
        layout.addWidget(label)
        layout.addWidget(self.load_button)
        layout.addWidget(self.bg_checkbox)
        
        box.setLayout(layout)
        return box

    def create_width_box(self):
        """Compact width control"""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {CompactColors.VINTAGE_ALPHA};
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                padding: 6px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        
        label = QLabel("▸ WIDTH")
        label.setObjectName("sectionLabel")
        
        width_header = QHBoxLayout()
        width_text = QLabel("Chars:")
        
        self.width_label = QLabel("120")
        self.width_label.setObjectName("valueLabel")
        self.width_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        width_header.addWidget(width_text)
        width_header.addStretch()
        width_header.addWidget(self.width_label)
        
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(40, 300)
        self.width_slider.setValue(120)
        self.width_slider.setMinimumHeight(20)
        self.width_slider.valueChanged.connect(self.update_width_label)
        
        layout.addWidget(label)
        layout.addLayout(width_header)
        layout.addWidget(self.width_slider)
        
        box.setLayout(layout)
        return box

    def create_actions_box(self):
        """Compact actions"""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {CompactColors.VINTAGE_ALPHA};
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                padding: 6px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        
        label = QLabel("▸ ACTIONS")
        label.setObjectName("sectionLabel")
        
        self.export_button = QPushButton("SAVE")
        self.export_button.setObjectName("exportButton")
        self.export_button.setDisabled(True)
        self.export_button.setMinimumHeight(32)
        self.export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_button.clicked.connect(self.on_export)
        
        self.quit_button = QPushButton("QUIT")
        self.quit_button.setObjectName("quitButton")
        self.quit_button.setMinimumHeight(32)
        self.quit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quit_button.clicked.connect(self.close)
        
        layout.addWidget(label)
        layout.addWidget(self.export_button)
        layout.addWidget(self.quit_button)
        
        box.setLayout(layout)
        return box

    def create_display_area(self):
        """Compact display"""
        display_frame = QFrame()
        display_frame.setObjectName("displayPanel")
        
        display_layout = QVBoxLayout()
        display_layout.setContentsMargins(10, 8, 10, 10)
        display_layout.setSpacing(6)
        
        output_label = QLabel("▸ OUTPUT")
        output_label.setObjectName("sectionLabel")
        
        self.text_area = CompactTextEdit()
        self.text_area.setPlaceholderText("// READY")
        
        display_layout.addWidget(output_label)
        display_layout.addWidget(self.text_area)
        
        display_frame.setLayout(display_layout)
        self.main_layout.addWidget(display_frame, stretch=1)

    def update_width_label(self, value):
        self.width_label.setText(str(value))

    def start_processing(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "OPEN", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.load_button.setDisabled(True)
            self.export_button.setDisabled(True)
            self.text_area.clear()
            self.text_area.insertPlainText("// PROCESSING...")

            columns = self.width_slider.value()
            remove_bg = self.bg_checkbox.isChecked()

            self.thread = QThread()
            self.worker = Worker(file_path=file_path, columns=columns, remove_bg=remove_bg)
            self.worker.moveToThread(self.thread)
            
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.update_text_area)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            self.thread.start()

    def update_text_area(self, ascii_result: str):
        self.last_ascii_result = ascii_result
        self.text_area.append_ansi_text(ascii_result)
        self.load_button.setDisabled(False)
        
        if not ascii_result.startswith("Error"):
            self.export_button.setDisabled(False)

    def on_export(self):
        if not self.last_ascii_result:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "SAVE", 
            "ascii.txt", 
            "Text (*.txt)"
        )
        
        if file_path:
            try:
                clean_text = Text.from_ansi(self.last_ascii_result).plain
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clean_text)
                
                self.text_area.insertPlainText(f"\n\n// SAVED: {file_path}")
            except Exception as e:
                self.text_area.insertPlainText(f"\n\n// ERROR: {e}")

    # Drag window support (frameless)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and self.offset:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        self.dragging = False


def main():
    app = QApplication(sys.argv)
    app.setFont(get_compact_font())
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(CompactColors.SHADOW_GREY))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(CompactColors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(CompactColors.SHADOW_GREY))
    palette.setColor(QPalette.ColorRole.Text, QColor(CompactColors.GRAPE_BRIGHT))
    palette.setColor(QPalette.ColorRole.Button, QColor(CompactColors.VINTAGE_GRAPE))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(CompactColors.DUSTY_GRAPE))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()