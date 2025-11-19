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
                             QSlider, QLabel, QFrame, QProgressBar, QDialog, QComboBox)
from PyQt6.QtGui import QFont, QColor, QTextCursor, QPalette, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QUrl
from rich.text import Text 

from converter import convert_image_to_ascii, convert_image_to_ascii_custom
from background import remove_background_from_image
from gif_animator import GifConverter, GifPlayer
from ascii_widget import FloatingAsciiWidget
from gif_exporter import GifExporter
from gif_export_dialog import GifExportDialog
from character_sets import CharacterSet, CharacterSetManager
from image_adjustments import ImageAdjustments
from history_manager import HistoryManager
from history_panel import HistoryPanel
from settings_manager import SettingsManager, AspectRatioMode
from styles.compact_theme import COMPACT_THEME, get_compact_font, CompactColors


class Worker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, file_path, columns, remove_bg, char_set=None, brightness=0, contrast=100, invert=False, aspect_ratio='original'):
        super().__init__()
        self.file_path = file_path
        self.columns = columns
        self.remove_bg = remove_bg
        self.char_set = char_set
        self.brightness = brightness
        self.contrast = contrast
        self.invert = invert
        self.aspect_ratio = aspect_ratio

    def run(self):
        try:
            from PIL import Image
            
            # Load image
            img = Image.open(self.file_path)
            
            # Remove background if requested
            if self.remove_bg:
                processed_image = remove_background_from_image(self.file_path)
                if processed_image:
                    img = processed_image
            
            # Apply aspect ratio
            if self.aspect_ratio != 'original':
                ratio = AspectRatioMode.get_ratio(self.aspect_ratio)
                if ratio > 0:
                    current_ratio = img.width / img.height
                    if abs(current_ratio - ratio) > 0.1:  # If different enough
                        if ratio > current_ratio:  # Need wider
                            new_width = int(img.height * ratio)
                            img = img.resize((new_width, img.height), Image.Resampling.LANCZOS)
                        else:  # Need taller
                            new_height = int(img.width / ratio)
                            img = img.resize((img.width, new_height), Image.Resampling.LANCZOS)
            
            # Apply adjustments
            img = ImageAdjustments.apply_all_adjustments(
                img,
                brightness=self.brightness,
                contrast=self.contrast,
                invert=self.invert
            )
            
            # Convert to ASCII
            if self.char_set:
                ascii_result = convert_image_to_ascii_custom(img, columns=self.columns, char_set=self.char_set)
            else:
                ascii_result = convert_image_to_ascii(img, columns=self.columns)

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

    def __init__(self, gif_path, columns, char_set=None, brightness=0, contrast=100, invert=False, aspect_ratio='original'):
        super().__init__()
        self.gif_path = gif_path
        self.columns = columns
        self.char_set = char_set
        self.brightness = brightness
        self.contrast = contrast
        self.invert = invert
        self.aspect_ratio = aspect_ratio
        self.converter = GifConverter()

    def run(self):
        from PIL import Image
        
        try:
            frames = []
            delays = []
            
            with Image.open(self.gif_path) as gif:
                frame_index = 0
                total_frames = 0
                
                # Count total frames
                try:
                    while True:
                        gif.seek(total_frames)
                        total_frames += 1
                except EOFError:
                    pass
                
                gif.seek(0)
                
                # Process each frame
                for frame_index in range(total_frames):
                    gif.seek(frame_index)
                    
                    # Get frame delay
                    delay = gif.info.get('duration', 100)
                    
                    # Convert frame
                    frame_img = gif.convert('RGB')
                    
                    # Apply aspect ratio
                    if self.aspect_ratio != 'original':
                        ratio = AspectRatioMode.get_ratio(self.aspect_ratio)
                        if ratio > 0:
                            current_ratio = frame_img.width / frame_img.height
                            if abs(current_ratio - ratio) > 0.1:
                                if ratio > current_ratio:
                                    new_width = int(frame_img.height * ratio)
                                    frame_img = frame_img.resize((new_width, frame_img.height), Image.Resampling.LANCZOS)
                                else:
                                    new_height = int(frame_img.width / ratio)
                                    frame_img = frame_img.resize((frame_img.width, new_height), Image.Resampling.LANCZOS)
                    
                    # Apply adjustments
                    frame_img = ImageAdjustments.apply_all_adjustments(
                        frame_img,
                        brightness=self.brightness,
                        contrast=self.contrast,
                        invert=self.invert
                    )
                    
                    # Convert to ASCII
                    if self.char_set:
                        ascii_frame = convert_image_to_ascii_custom(frame_img, self.columns, self.char_set)
                    else:
                        from converter import convert_image_to_ascii
                        import tempfile
                        
                        # Create temp file
                        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                        tmp_path = tmp.name
                        tmp.close()
                        
                        try:
                            frame_img.save(tmp_path, 'PNG')
                            ascii_frame = convert_image_to_ascii(tmp_path, columns=self.columns)
                        finally:
                            if os.path.exists(tmp_path):
                                try:
                                    os.unlink(tmp_path)
                                except:
                                    pass
                    
                    if ascii_frame:
                        frames.append(ascii_frame)
                        delays.append(delay)
                    
                    # Emit progress
                    self.progress.emit(frame_index + 1, total_frames)
            
            if frames:
                self.finished.emit(frames, delays)
            else:
                self.error.emit("Failed to convert GIF frames")
                
        except Exception as e:
            self.error.emit(f"GIF conversion error: {str(e)}")


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
        
        # Enable drag & drop
        self.setAcceptDrops(True)
        
        self.last_ascii_result = None
        self.is_gif_mode = False
        
        # GIF player
        self.gif_player = GifPlayer()
        self.gif_player.frame_changed.connect(self.display_frame)
        
        # Floating widgets (multiple support)
        self.floating_widgets = []
        
        # History manager
        self.history_manager = HistoryManager()
        self.history_panel = None
        
        # Settings manager
        self.settings_manager = SettingsManager()
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.main_layout)
        
        # Build UI
        self.create_title_bar()
        self.create_control_panel()
        self.create_adjustments_panel()  # NEW
        self.create_gif_controls()
        self.create_display_area()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
        # Threading
        self.thread = None
        self.worker = None
        self.gif_thread = None
        self.gif_worker = None
        
        # Hide GIF controls initially
        self.gif_controls_frame.hide()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # Ctrl+O - Open file
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.start_processing)
        
        # Ctrl+S - Save
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.on_export)
        
        # Ctrl+W - Open widget
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.open_widget)
        
        # Ctrl+H - Open history
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.open_history)
        
        # Space - Play/Pause (only in GIF mode)
        QShortcut(QKeySequence("Space"), self).activated.connect(self.shortcut_play_pause)
        
        # Ctrl+Q - Quit
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)

    def shortcut_play_pause(self):
        """Play/pause handler for keyboard shortcut"""
        if self.is_gif_mode:
            self.toggle_playback()

    # ========== DRAG & DROP HANDLERS ==========
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter - check if file is valid"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) >= 1:  # Accept one or more files
                file_path = urls[0].toLocalFile()
                # Check if it's an image or GIF
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
                if any(file_path.lower().endswith(ext) for ext in valid_extensions):
                    event.accept()  # Accept the event
                    # Visual feedback
                    self.setStyleSheet(COMPACT_THEME + """
                        QMainWindow {
                            border: 3px dashed #5f5aa2;
                        }
                    """)
                    return
        event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move - needed for proper drag & drop"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave - remove visual feedback"""
        self.setStyleSheet(COMPACT_THEME)
    
    def dropEvent(self, event: QDropEvent):
        """Handle file drop"""
        # Remove visual feedback
        self.setStyleSheet(COMPACT_THEME)
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                file_path = urls[0].toLocalFile()
                
                # Check if it's a GIF
                if file_path.lower().endswith('.gif'):
                    self.load_gif(file_path)
                else:
                    self.load_image(file_path)
                
                event.acceptProposedAction()
                
                # Show feedback in text area
                filename = os.path.basename(file_path)
                self.text_area.clear()
                self.text_area.insertPlainText(f"// FILE DROPPED: {filename}\n// Processing...")
    
    # ========== END DRAG & DROP ==========

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
        
        # Drag & Drop hint
        hint_label = QLabel("💡 Drag & Drop files here")
        hint_label.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt; font-style: italic;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        title_layout.addWidget(hint_label)
        
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
        charset_box = self.create_charset_box()
        right_box = self.create_actions_box()
        
        controls_layout.addWidget(left_box, stretch=1)
        controls_layout.addWidget(middle_box, stretch=2)
        controls_layout.addWidget(charset_box, stretch=2)
        controls_layout.addWidget(right_box, stretch=2)
        
        control_frame.setLayout(controls_layout)
        self.main_layout.addWidget(control_frame)
    
    def create_adjustments_panel(self):
        """Image adjustments panel (brightness, contrast, invert)"""
        adjust_frame = QFrame()
        adjust_frame.setObjectName("controlPanel")
        
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Section label
        section_label = QLabel("▸ ADJUSTMENTS")
        section_label.setObjectName("sectionLabel")
        section_label.setStyleSheet(f"color: {CompactColors.DUSTY_GRAPE}; font-weight: bold; font-size: 10pt;")
        
        # Brightness control
        bright_layout = QVBoxLayout()
        bright_layout.setSpacing(4)
        
        bright_header = QHBoxLayout()
        bright_label = QLabel("Brightness:")
        bright_label.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt;")
        
        self.brightness_value_label = QLabel("0")
        self.brightness_value_label.setStyleSheet(f"color: {CompactColors.GRAPE_LIGHT}; font-weight: bold; font-size: 9pt;")
        self.brightness_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        bright_header.addWidget(bright_label)
        bright_header.addStretch()
        bright_header.addWidget(self.brightness_value_label)
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setMinimumWidth(120)
        self.brightness_slider.valueChanged.connect(self.update_brightness_label)
        
        bright_layout.addLayout(bright_header)
        bright_layout.addWidget(self.brightness_slider)
        
        # Contrast control
        contrast_layout = QVBoxLayout()
        contrast_layout.setSpacing(4)
        
        contrast_header = QHBoxLayout()
        contrast_label = QLabel("Contrast:")
        contrast_label.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt;")
        
        self.contrast_value_label = QLabel("100%")
        self.contrast_value_label.setStyleSheet(f"color: {CompactColors.GRAPE_LIGHT}; font-weight: bold; font-size: 9pt;")
        self.contrast_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        contrast_header.addWidget(contrast_label)
        contrast_header.addStretch()
        contrast_header.addWidget(self.contrast_value_label)
        
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(25, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setMinimumWidth(120)
        self.contrast_slider.valueChanged.connect(self.update_contrast_label)
        
        contrast_layout.addLayout(contrast_header)
        contrast_layout.addWidget(self.contrast_slider)
        
        # Invert checkbox
        self.invert_checkbox = QCheckBox("INVERT")
        self.invert_checkbox.setToolTip("Invert colors (negative effect)")
        self.invert_checkbox.setStyleSheet(f"color: {CompactColors.TEXT_PRIMARY}; font-size: 10pt;")
        
        # Reset button
        reset_btn = QPushButton("↻ RESET")
        reset_btn.setMinimumHeight(28)
        reset_btn.setFixedWidth(70)
        reset_btn.setToolTip("Reset all adjustments to default")
        reset_btn.clicked.connect(self.reset_adjustments)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(65, 63, 84, 200);
                color: {CompactColors.TEXT_SECONDARY};
                border: 2px solid {CompactColors.VINTAGE_GRAPE};
                border-radius: 0px;
                padding: 4px;
                font-weight: bold;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: {CompactColors.VINTAGE_GRAPE};
                color: {CompactColors.TEXT_PRIMARY};
                border-color: {CompactColors.DUSTY_GRAPE};
            }}
        """)
        
        # Layout assembly
        layout.addWidget(section_label)
        layout.addSpacing(10)
        layout.addLayout(bright_layout)
        layout.addSpacing(10)
        layout.addLayout(contrast_layout)
        layout.addSpacing(10)
        layout.addWidget(self.invert_checkbox)
        layout.addSpacing(10)
        layout.addWidget(reset_btn)
        layout.addStretch()
        
        adjust_frame.setLayout(layout)
        self.main_layout.addWidget(adjust_frame)
    
    def update_brightness_label(self, value):
        """Update brightness label"""
        sign = "+" if value > 0 else ""
        self.brightness_value_label.setText(f"{sign}{value}")
    
    def update_contrast_label(self, value):
        """Update contrast label"""
        self.contrast_value_label.setText(f"{value}%")
    
    def reset_adjustments(self):
        """Reset all adjustments to default"""
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(100)
        self.invert_checkbox.setChecked(False)

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
        self.speed_slider.setRange(25, 400)
        self.speed_slider.setValue(100)
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
        self.load_button.setMinimumHeight(28)
        self.load_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_button.clicked.connect(self.start_processing)
        self.load_button.setToolTip("Open file (Ctrl+O)")
        
        self.bg_checkbox = QCheckBox("RM BG")
        self.bg_checkbox.setToolTip("Remove Background")
        
        layout.addWidget(label)
        layout.addWidget(self.load_button)
        layout.addWidget(self.bg_checkbox)
        
        box.setLayout(layout)
        return box

    def create_charset_box(self):
        """Character set selection"""
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
        
        label = QLabel("▸ STYLE")
        label.setObjectName("sectionLabel")
        
        # Character set combo box
        self.charset_combo = QComboBox()
        self.charset_combo.setMinimumHeight(28)
        self.charset_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(48, 41, 47, 240);
                color: {CompactColors.TEXT_PRIMARY};
                border: 2px solid {CompactColors.VINTAGE_GRAPE};
                border-radius: 0px;
                padding: 6px;
                font-size: 10pt;
            }}
            QComboBox:hover {{
                border-color: {CompactColors.DUSTY_GRAPE};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {CompactColors.DUSTY_GRAPE};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(48, 41, 47, 250);
                color: {CompactColors.TEXT_PRIMARY};
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                selection-background-color: {CompactColors.DUSTY_GRAPE};
                selection-color: white;
            }}
        """)
        
        # Add character set options
        for preset in CharacterSetManager.get_all_presets():
            display_name = CharacterSetManager.get_display_name(preset)
            self.charset_combo.addItem(display_name, preset)
            
            # Set tooltip
            idx = self.charset_combo.count() - 1
            tooltip = CharacterSetManager.get_description(preset)
            self.charset_combo.setItemData(idx, tooltip, Qt.ItemDataRole.ToolTipRole)
        
        # Preview label
        self.charset_preview = QLabel("Preview: @@@%%%###***")
        self.charset_preview.setStyleSheet(f"""
            QLabel {{
                color: {CompactColors.GRAPE_BRIGHT};
                font-family: 'Courier New', monospace;
                font-size: 8pt;
                padding: 4px;
                background-color: rgba(48, 41, 47, 200);
                border: 1px solid {CompactColors.VINTAGE_GRAPE};
            }}
        """)
        self.charset_preview.setWordWrap(True)
        
        # Connect signal
        self.charset_combo.currentIndexChanged.connect(self.update_charset_preview)
        
        layout.addWidget(label)
        layout.addWidget(self.charset_combo)
        layout.addWidget(self.charset_preview)
        
        box.setLayout(layout)
        return box
    
    def update_charset_preview(self):
        """Update character set preview"""
        preset = self.charset_combo.currentData()
        if preset:
            preview = CharacterSetManager.get_preview(preset)
            self.charset_preview.setText(f"Preview: {preview}")

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
        
        # Aspect ratio combo
        aspect_label = QLabel("Ratio:")
        aspect_label.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt;")
        
        self.aspect_combo = QComboBox()
        self.aspect_combo.setMinimumHeight(24)
        self.aspect_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(48, 41, 47, 240);
                color: {CompactColors.TEXT_PRIMARY};
                border: 2px solid {CompactColors.VINTAGE_GRAPE};
                padding: 4px;
                font-size: 9pt;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(48, 41, 47, 250);
                color: {CompactColors.TEXT_PRIMARY};
                selection-background-color: {CompactColors.DUSTY_GRAPE};
            }}
        """)
        
        for mode in AspectRatioMode.get_all_modes():
            display_name = AspectRatioMode.get_display_name(mode)
            self.aspect_combo.addItem(display_name, mode)
        
        layout.addWidget(label)
        layout.addLayout(width_header)
        layout.addWidget(self.width_slider)
        layout.addSpacing(4)
        layout.addWidget(aspect_label)
        layout.addWidget(self.aspect_combo)
        
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
        
        self.export_button = QPushButton("💾 SAVE")
        self.export_button.setObjectName("exportButton")
        self.export_button.setDisabled(True)
        self.export_button.setMinimumHeight(28)
        self.export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_button.clicked.connect(self.on_export)
        self.export_button.setToolTip("Save ASCII art (Ctrl+S)")
        
        # Widget button
        self.widget_button = QPushButton("🪟 WIDGET")
        self.widget_button.setObjectName("exportButton")
        self.widget_button.setDisabled(True)
        self.widget_button.setMinimumHeight(28)
        self.widget_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.widget_button.clicked.connect(self.open_widget)
        self.widget_button.setToolTip("Open floating widget (Ctrl+W)")
        
        # History button - NEW
        self.history_button = QPushButton("📚 HISTORY")
        self.history_button.setObjectName("exportButton")
        self.history_button.setMinimumHeight(28)
        self.history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_button.clicked.connect(self.open_history)
        self.history_button.setToolTip("View conversion history (Ctrl+H)")
        
        self.quit_button = QPushButton("✕ QUIT")
        self.quit_button.setObjectName("quitButton")
        self.quit_button.setMinimumHeight(28)
        self.quit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quit_button.clicked.connect(self.close)
        self.quit_button.setToolTip("Quit application (Ctrl+Q)")
        
        layout.addWidget(label)
        layout.addWidget(self.export_button)
        layout.addWidget(self.widget_button)
        layout.addWidget(self.history_button)
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
        self.text_area.setPlaceholderText("// READY\n// Load an image or GIF to begin\n// Or drag & drop a file here")
        
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

    def load_settings(self):
        """Load saved settings"""
        # Main controls
        self.width_slider.setValue(self.settings_manager.get('width', 120))
        
        # Character set
        char_set = self.settings_manager.get('character_set', 'detailed')
        for i in range(self.charset_combo.count()):
            if self.charset_combo.itemData(i).value == char_set:
                self.charset_combo.setCurrentIndex(i)
                break
        
        # Adjustments
        self.brightness_slider.setValue(self.settings_manager.get('brightness', 0))
        self.contrast_slider.setValue(self.settings_manager.get('contrast', 100))
        self.invert_checkbox.setChecked(self.settings_manager.get('invert', False))
        self.bg_checkbox.setChecked(self.settings_manager.get('remove_background', False))
        
        # Aspect ratio
        aspect_mode = self.settings_manager.get('aspect_ratio', 'original')
        for i in range(self.aspect_combo.count()):
            if self.aspect_combo.itemData(i) == aspect_mode:
                self.aspect_combo.setCurrentIndex(i)
                break
        
        # Window geometry
        win_width = self.settings_manager.get('window_width', 800)
        win_height = self.settings_manager.get('window_height', 550)
        win_x = self.settings_manager.get('window_x', 100)
        win_y = self.settings_manager.get('window_y', 100)
        
        self.setGeometry(win_x, win_y, win_width, win_height)
    
    def save_settings(self):
        """Save current settings"""
        # Main controls
        self.settings_manager.set('width', self.width_slider.value())
        
        # Character set
        preset = self.charset_combo.currentData()
        if preset:
            self.settings_manager.set('character_set', preset.value)
        
        # Adjustments
        self.settings_manager.set('brightness', self.brightness_slider.value())
        self.settings_manager.set('contrast', self.contrast_slider.value())
        self.settings_manager.set('invert', self.invert_checkbox.isChecked())
        self.settings_manager.set('remove_background', self.bg_checkbox.isChecked())
        
        # Aspect ratio
        aspect_mode = self.aspect_combo.currentData()
        if aspect_mode:
            self.settings_manager.set('aspect_ratio', aspect_mode)
        
        # Window geometry
        self.settings_manager.set('window_width', self.width())
        self.settings_manager.set('window_height', self.height())
        self.settings_manager.set('window_x', self.x())
        self.settings_manager.set('window_y', self.y())
    
    def closeEvent(self, event):
        """Handle window close - save settings"""
        self.save_settings()
        event.accept()
    
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
        
        # Check if GIF
        if file_path.lower().endswith('.gif'):
            self.load_gif(file_path)
        else:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Load static image"""
        self.is_gif_mode = False
        self.gif_controls_frame.hide()
        self.gif_player.pause()
        
        self.last_loaded_file = file_path  # Store for history
        
        self.load_button.setDisabled(True)
        self.export_button.setDisabled(True)
        self.text_area.clear()
        self.text_area.insertPlainText("// PROCESSING IMAGE...")

        columns = self.width_slider.value()
        remove_bg = self.bg_checkbox.isChecked()
        
        # Get character set
        preset = self.charset_combo.currentData()
        char_set = None
        if preset and preset != CharacterSet.DETAILED:
            char_set = CharacterSetManager.get_character_set(preset)
        
        # Get adjustments
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        invert = self.invert_checkbox.isChecked()
        
        # Get aspect ratio
        aspect_mode = self.aspect_combo.currentData()

        self.thread = QThread()
        self.worker = Worker(
            file_path=file_path,
            columns=columns,
            remove_bg=remove_bg,
            char_set=char_set,
            brightness=brightness,
            contrast=contrast,
            invert=invert,
            aspect_ratio=aspect_mode
        )
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
        
        self.last_loaded_file = file_path  # Store for history
        
        self.load_button.setDisabled(True)
        self.export_button.setDisabled(True)
        self.text_area.clear()
        self.text_area.insertPlainText("// CONVERTING GIF...\n// This may take a moment...")
        
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        columns = self.width_slider.value()
        
        # Get character set
        preset = self.charset_combo.currentData()
        char_set = None
        if preset and preset != CharacterSet.DETAILED:
            char_set = CharacterSetManager.get_character_set(preset)
        
        # Get adjustments
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        invert = self.invert_checkbox.isChecked()

        self.gif_thread = QThread()
        aspect_mode = self.aspect_combo.currentData()

        self.gif_worker = GifWorker(
            file_path,
            columns,
            char_set,
            brightness,
            contrast,
            invert,
            aspect_mode
        )
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
        self.widget_button.setDisabled(False)
        
        total_frames = len(frames)
        self.frame_label.setText(f"Frame: 1/{total_frames}")
        
        # Show first frame
        self.text_area.append_ansi_text(frames[0])
        
        # Add to history
        if hasattr(self, 'last_loaded_file'):
            settings = {
                'width': self.width_slider.value(),
                'char_set': self.charset_combo.currentText(),
                'brightness': self.brightness_slider.value(),
                'contrast': self.contrast_slider.value(),
                'invert': self.invert_checkbox.isChecked()
            }
            
            self.history_manager.add_entry(
                file_name=os.path.basename(self.last_loaded_file),
                file_path=self.last_loaded_file,
                ascii_result=frames[0],
                is_gif=True,
                settings=settings,
                frames=None,  # Don't save frames (too large)
                delays=delays
            )
        
        # Auto-play
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
            self.widget_button.setDisabled(False)
            
            # Add to history
            if hasattr(self, 'last_loaded_file'):
                settings = {
                    'width': self.width_slider.value(),
                    'char_set': self.charset_combo.currentText(),
                    'brightness': self.brightness_slider.value(),
                    'contrast': self.contrast_slider.value(),
                    'invert': self.invert_checkbox.isChecked(),
                    'remove_bg': self.bg_checkbox.isChecked()
                }
                
                self.history_manager.add_entry(
                    file_name=os.path.basename(self.last_loaded_file),
                    file_path=self.last_loaded_file,
                    ascii_result=ascii_result,
                    is_gif=False,
                    settings=settings
                )

    def on_export(self):
        """Export ASCII art"""
        if self.is_gif_mode:
            # GIF Export with dialog
            if not self.gif_player.frames:
                return
            
            try:
                dialog = GifExportDialog(self)
                result = dialog.exec()
                
                if result == QDialog.DialogCode.Accepted:
                    format_type, output_path = dialog.get_export_info()
                
                if not output_path:
                    return
                
                # Show progress message
                self.text_area.insertPlainText(f"\n\n// EXPORTING as {format_type.upper()}...")
                QApplication.processEvents()
                
                # Export based on format
                success = False
                if format_type == 'txt':
                    success = GifExporter.export_to_single_txt(
                        self.gif_player.frames,
                        self.gif_player.delays,
                        output_path
                    )
                elif format_type == 'html':
                    success = GifExporter.export_to_html(
                        self.gif_player.frames,
                        self.gif_player.delays,
                        output_path
                    )
                elif format_type == 'folder':
                    success = GifExporter.export_to_folder(
                        self.gif_player.frames,
                        self.gif_player.delays,
                        output_path
                    )
                
                if success:
                    self.text_area.insertPlainText(f"\n// ✓ SAVED: {output_path}")
                else:
                    self.text_area.insertPlainText(f"\n// ✗ ERROR: Export failed")
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.text_area.insertPlainText(f"\n\n// ERROR: {e}")
        else:
            # Static image export
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
    
    def open_widget(self):
        """Open NEW floating widget with current ASCII art (multiple widgets support)"""
        # Get widget settings
        font_size = self.settings_manager.get('widget_font_size', 9)
        color_theme = self.settings_manager.get('widget_color_theme', 'grape')
        
        # Create new widget instance with settings
        widget = FloatingAsciiWidget(font_size=font_size, color_theme=color_theme)
        
        # Set content based on mode
        if self.is_gif_mode and self.gif_player.frames:
            # Animated GIF
            widget.set_animation(
                self.gif_player.frames,
                self.gif_player.delays
            )
        elif self.last_ascii_result:
            # Static image
            widget.set_ascii_text(self.last_ascii_result)
        
        # Add to list
        self.floating_widgets.append(widget)
        
        # Remove from list when closed
        widget.destroyed.connect(lambda: self.on_widget_closed(widget))
        
        # Show widget
        widget.show()
        widget.raise_()
        widget.activateWindow()
    
    def on_widget_closed(self, widget):
        """Handle widget closing"""
        if widget in self.floating_widgets:
            self.floating_widgets.remove(widget)
    
    def open_history(self):
        """Open history/gallery panel"""
        if self.history_panel is None or not self.history_panel.isVisible():
            self.history_panel = HistoryPanel(self.history_manager, self)
            self.history_panel.entry_selected.connect(self.on_history_entry_selected)
        
        self.history_panel.show()
        self.history_panel.raise_()
        self.history_panel.activateWindow()
    
    def on_history_entry_selected(self, entry):
        """Handle history entry selection"""
        # Check if should open in widget
        if hasattr(entry, 'open_in_widget') and entry.open_in_widget:
            # Open in new widget
            widget = FloatingAsciiWidget()
            widget.set_ascii_text(entry.ascii_result)
            self.floating_widgets.append(widget)
            widget.destroyed.connect(lambda: self.on_widget_closed(widget))
            widget.show()
            widget.raise_()
            widget.activateWindow()
        else:
            # Load into main window
            self.text_area.append_ansi_text(entry.ascii_result)
            self.last_ascii_result = entry.ascii_result
            self.export_button.setDisabled(False)
            self.widget_button.setDisabled(False)


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