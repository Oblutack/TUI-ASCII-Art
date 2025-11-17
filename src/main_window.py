import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QFileDialog, QCheckBox, 
                             QSlider, QLabel)
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from rich.text import Text 

from converter import convert_image_to_ascii
from background import remove_background_from_image


class Worker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, file_path, columns, remove_bg):
        super().__init__()
        self.file_path = file_path
        self.columns = columns
        self.remove_bg = remove_bg

    def run(self):
        """This is the work that will be done in the background."""
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


class AnsiTextEdit(QTextEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Courier New", 10))
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    def append_ansi_text(self, text):
        self.clear(); self.moveCursor(QTextCursor.MoveOperation.End)
        parts = text.split('\x1b[')
        for part in parts:
            if 'm' in part:
                try:
                    code_part, text_part = part.split('m', 1)
                    if not code_part: continue
                    color_code = int(code_part.split(';')[0])
                    color = QColor("white")
                    if 30 <= color_code <= 37:
                        colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
                        color = QColor(colors[color_code - 30])
                    self.setTextColor(color); self.insertPlainText(text_part)
                except (ValueError, IndexError):
                    self.setTextColor(QColor("white")); self.insertPlainText(part)
            else: self.setTextColor(QColor("white")); self.insertPlainText(part)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII Art Generator")
        self.setGeometry(100, 100, 1000, 700) 
        self.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc;")

        self.last_ascii_result = None

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.controls_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load Image")
        self.bg_checkbox = QCheckBox("Remove Background")
        self.width_label = QLabel("Width: 120")
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(40, 300)
        self.width_slider.setValue(120)
        self.width_slider.valueChanged.connect(self.update_width_label)
        
        self.export_button = QPushButton("Export to .txt")
        self.export_button.setDisabled(True)
        self.export_button.clicked.connect(self.on_export)
        
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.controls_layout.addWidget(self.load_button)
        self.controls_layout.addWidget(self.bg_checkbox)
        self.controls_layout.addSpacing(20)
        self.controls_layout.addWidget(self.width_label)
        self.controls_layout.addWidget(self.width_slider)
        self.controls_layout.addStretch() 
        self.controls_layout.addWidget(self.export_button)
        self.controls_layout.addWidget(self.quit_button)
        
        self.text_area = AnsiTextEdit()

        self.main_layout.addLayout(self.controls_layout)
        self.main_layout.addWidget(self.text_area)

        self.load_button.clicked.connect(self.start_processing)
        
        self.apply_styles()

        self.thread = None
        self.worker = None

    def apply_styles(self):
        button_style = """
            QPushButton { background-color: #333; border: 1px solid #555; padding: 5px 10px; }
            QPushButton:hover { background-color: #444; }
            QPushButton:disabled { color: #777; }
        """
        self.load_button.setStyleSheet(button_style)
        self.export_button.setStyleSheet(button_style)
        self.quit_button.setStyleSheet("QPushButton { background-color: #5c2b2b; border: 1px solid #8b4b4b; padding: 5px 10px; } QPushButton:hover { background-color: #7c3b3b; }")
        self.bg_checkbox.setStyleSheet("QCheckBox::indicator { width: 15px; height: 15px; } QCheckBox::indicator:unchecked { background-color: #333; border: 1px solid #555; } QCheckBox::indicator:checked { background-color: #0a7; }")
        self.width_slider.setStyleSheet("QSlider::groove:horizontal { border: 1px solid #555; height: 4px; background: #333; } QSlider::handle:horizontal { background: #0a7; border: 1px solid #0c9; width: 15px; height: 15px; margin: -6px 0; }")

    def update_width_label(self, value):
        self.width_label.setText(f"Width: {value}")

    def start_processing(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.load_button.setDisabled(True)
            self.export_button.setDisabled(True)
            self.text_area.clear()
            self.text_area.insertPlainText("Processing, please wait...")

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
        if not self.last_ascii_result: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save ASCII Art", "", "Text Files (*.txt)")
        if file_path:
            try:
                clean_text = Text.from_ansi(self.last_ascii_result).plain
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clean_text)
            except Exception as e:
                self.text_area.append_ansi_text(f"\n\nExport failed: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()