import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(root_dir))

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QFileDialog, QCheckBox, 
                             QSlider, QLabel, QFrame, QProgressBar)
from PyQt6.QtGui import QFont, QColor, QTextCursor, QPalette
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread
from rich.text import Text 

from converter import convert_image_to_ascii
from background import remove_background_from_image
from gif_animator import GifConverter, GifPlayer
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


class GifWorker(QObject):
    """Worker for GIF conversion in background thread"""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(list, list)
    error = pyqtSignal(str)

    def __init__(self, gif_path, columns):
        super().__init__()
        self.gif_path = gif_path
        self.columns = columns
        self.converter = GifConverter()

    def run(self):
        self.converter.frame_converted.connect(self.progress.emit)
        self.converter.conversion_error.connect(self.error.emit)
        
        frames, delays = self.converter.convert_gif(self.gif_path, self.columns)
        
        if frames:
            self.finished.emit(frames, delays)
        else:
            self.error.emit("Failed to convert GIF")


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
                    color = QColor(CompactColors.GRAPE_BRIGHT)
                    
                    if 30 <= color_code <= 37:
                        colors = [
                            CompactColors.TEXT_DIM,
                            "#d89aa3",
                            CompactColors.GRAPE_BRIGHT,
                            "#e0c097",
                            CompactColors.DUSTY_GRAPE,
                            "#c5a3d8",
                            CompactColors.GRAPE_LIGHT,
                            CompactColors.TEXT_PRIMARY
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
        
        # Window setup
        self.setWindowTitle("ASCII GENERATOR v1.0 - with GIF Support")
        self.setGeometry(100, 100, 800, 550)
        self.setMinimumSize(700, 500)
        
        self.last_ascii_result = None
        self.is_gif_mode = False
        
        # GIF player
        self.gif_player = GifPlayer()
        self.gif_player.frame_changed.connect(self.display_frame)
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.main_layout)
        
        # Build UI
        self.create_title_bar()
        self.create_control_panel()
        self.create_gif_controls()  # NEW
        self.create_display_area()
        
        # Threading
        self.thread = None
        self.worker = None
        self.gif_thread = None
        self.gif_worker = None
        
        # Hide GIF controls initially
        self.gif_controls_frame.hide()

    def create_title_bar(self):
        """Compact title bar"""
        title_frame = QFrame()
        title_frame.setObjectName("titleFrame")
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(8, 6, 8, 6)
        title_layout.setSpacing(10)
        
        title_label = QLabel("▌ASCII GENERATOR")
        title_label.setObjectName("titleLabel")
        
        subtitle_label = QLabel("// Image & GIF Converter")
        subtitle_label.setObjectName("subtitleLabel")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        title_frame.setLayout(title_layout)
        self.main_layout.addWidget(title_frame)

    def create_control_panel(self):
        """Main control panel"""
        control_frame = QFrame()
        control_frame.setObjectName("controlPanel")
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(10, 8, 10, 8)
        
        left_box = self.create_input_box()
        middle_box = self.create_width_box()
        right_box = self.create_actions_box()
        
        controls_layout.addWidget(left_box, stretch=1)
        controls_layout.addWidget(middle_box, stretch=2)
        controls_layout.addWidget(right_box, stretch=1)
        
        control_frame.setLayout(controls_layout)
        self.main_layout.addWidget(control_frame)

    def create_gif_controls(self):
        """GIF playback controls"""
        self.gif_controls_frame = QFrame()
        self.gif_controls_frame.setObjectName("controlPanel")
        
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 6, 10, 6)
        
        # Playback buttons
        self.play_button = QPushButton("▶ PLAY")
        self.play_button.setObjectName("loadButton")
        self.play_button.setMinimumHeight(28)
        self.play_button.clicked.connect(self.toggle_playback)
        
        self.stop_button = QPushButton("■ STOP")
        self.stop_button.setMinimumHeight(28)
        self.stop_button.clicked.connect(self.stop_animation)
        
        # Speed control
        speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(25, 400)  # 0.25x to 4x
        self.speed_slider.setValue(100)  # 1.0x
        self.speed_slider.setMinimumWidth(120)
        self.speed_slider.valueChanged.connect(self.update_speed)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setObjectName("valueLabel")
        self.speed_label.setMinimumWidth(40)
        
        # Loop checkbox
        self.loop_checkbox = QCheckBox("LOOP")
        self.loop_checkbox.setChecked(True)
        self.loop_checkbox.toggled.connect(self.gif_player.set_looping)
        
        # Frame counter
        self.frame_label = QLabel("Frame: 0/0")
        self.frame_label.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY};")
        
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addSpacing(10)
        layout.addWidget(speed_label)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.speed_label)
        layout.addSpacing(10)
        layout.addWidget(self.loop_checkbox)
        layout.addStretch()
        layout.addWidget(self.frame_label)
        
        self.gif_controls_frame.setLayout(layout)
        self.main_layout.addWidget(self.gif_controls_frame)

    def create_input_box(self):
        """Input section"""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(65, 63, 84, 255);
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                padding: 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        
        label = QLabel("▸ INPUT")
        label.setObjectName("sectionLabel")
        
        self.load_button = QPushButton("LOAD")
        self.load_button.setObjectName("loadButton")
        self.load_button.setMinimumHeight(34)
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
        """Width control"""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(65, 63, 84, 255);
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                padding: 8px;
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
        self.width_slider.setMinimumHeight(22)
        self.width_slider.valueChanged.connect(self.update_width_label)
        
        layout.addWidget(label)
        layout.addLayout(width_header)
        layout.addWidget(self.width_slider)
        
        box.setLayout(layout)
        return box

    def create_actions_box(self):
        """Actions"""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(65, 63, 84, 255);
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                padding: 8px;
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
        self.export_button.setMinimumHeight(34)
        self.export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_button.clicked.connect(self.on_export)
        
        self.quit_button = QPushButton("QUIT")
        self.quit_button.setObjectName("quitButton")
        self.quit_button.setMinimumHeight(34)
        self.quit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quit_button.clicked.connect(self.close)
        
        layout.addWidget(label)
        layout.addWidget(self.export_button)
        layout.addWidget(self.quit_button)
        
        box.setLayout(layout)
        return box

    def create_display_area(self):
        """Display area"""
        display_frame = QFrame()
        display_frame.setObjectName("displayPanel")
        
        display_layout = QVBoxLayout()
        display_layout.setContentsMargins(10, 8, 10, 10)
        display_layout.setSpacing(6)
        
        output_label = QLabel("▸ OUTPUT")
        output_label.setObjectName("sectionLabel")
        
        self.text_area = CompactTextEdit()
        self.text_area.setPlaceholderText("// READY\n// Load an image or GIF to begin")
        
        # Progress bar for GIF conversion
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        
        display_layout.addWidget(output_label)
        display_layout.addWidget(self.progress_bar)
        display_layout.addWidget(self.text_area)
        
        display_frame.setLayout(display_layout)
        self.main_layout.addWidget(display_frame, stretch=1)

    def update_width_label(self, value):
        self.width_label.setText(str(value))

    def update_speed(self, value):
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.1f}x")
        self.gif_player.set_speed(speed)

    def start_processing(self):
        """Load image or GIF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "OPEN IMAGE/GIF", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp);;GIF (*.gif);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        if file_path.lower().endswith('.gif'):
            self.load_gif(file_path)
        else:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Load static image"""
        self.is_gif_mode = False
        self.gif_controls_frame.hide()
        self.gif_player.pause()
        
        self.load_button.setDisabled(True)
        self.export_button.setDisabled(True)
        self.text_area.clear()
        self.text_area.insertPlainText("// PROCESSING IMAGE...")

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

    def load_gif(self, file_path):
        """Load and convert GIF"""
        self.is_gif_mode = True
        self.gif_controls_frame.show()
        
        self.load_button.setDisabled(True)
        self.export_button.setDisabled(True)
        self.text_area.clear()
        self.text_area.insertPlainText("// CONVERTING GIF...\n// This may take a moment...")
        
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        columns = self.width_slider.value()

        self.gif_thread = QThread()
        self.gif_worker = GifWorker(file_path, columns)
        self.gif_worker.moveToThread(self.gif_thread)
        
        self.gif_thread.started.connect(self.gif_worker.run)
        self.gif_worker.progress.connect(self.update_gif_progress)
        self.gif_worker.finished.connect(self.on_gif_converted)
        self.gif_worker.error.connect(self.on_gif_error)
        self.gif_worker.finished.connect(self.gif_thread.quit)
        self.gif_worker.finished.connect(self.gif_worker.deleteLater)
        self.gif_thread.finished.connect(self.gif_thread.deleteLater)
        
        self.gif_thread.start()

    def update_gif_progress(self, current, total):
        """Update GIF conversion progress"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_bar.setFormat(f"Converting: {current}/{total} frames")

    def on_gif_converted(self, frames, delays):
        """GIF conversion complete"""
        self.progress_bar.hide()
        self.gif_player.load_animation(frames, delays)
        self.load_button.setDisabled(False)
        self.export_button.setDisabled(False)
        
        total_frames = len(frames)
        self.frame_label.setText(f"Frame: 1/{total_frames}")
        
        self.text_area.append_ansi_text(frames[0])
        
        self.gif_player.play()
        self.play_button.setText("⏸ PAUSE")

    def on_gif_error(self, error_msg):
        """GIF conversion error"""
        self.progress_bar.hide()
        self.text_area.clear()
        self.text_area.insertPlainText(f"// ERROR\n// {error_msg}")
        self.load_button.setDisabled(False)

    def display_frame(self, frame_text, frame_number):
        """Display animation frame"""
        self.text_area.append_ansi_text(frame_text)
        total = self.gif_player.get_frame_count()
        self.frame_label.setText(f"Frame: {frame_number + 1}/{total}")

    def toggle_playback(self):
        """Toggle play/pause"""
        if self.gif_player.is_playing:
            self.gif_player.pause()
            self.play_button.setText("▶ PLAY")
        else:
            self.gif_player.play()
            self.play_button.setText("⏸ PAUSE")

    def stop_animation(self):
        """Stop animation"""
        self.gif_player.stop()
        self.play_button.setText("▶ PLAY")

    def update_text_area(self, ascii_result: str):
        """Update display (for static images)"""
        self.last_ascii_result = ascii_result
        self.text_area.append_ansi_text(ascii_result)
        self.load_button.setDisabled(False)
        
        if not ascii_result.startswith("Error"):
            self.export_button.setDisabled(False)

    def on_export(self):
        """Export ASCII art"""
        if self.is_gif_mode:
            # TODO: 
            self.text_area.insertPlainText("\n\n// GIF export coming soon!")
            return
        
        if not self.last_ascii_result:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "SAVE ASCII", 
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