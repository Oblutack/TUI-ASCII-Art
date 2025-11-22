import sys
import os
from pathlib import Path

# Fix paths
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(root_dir))

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QTextEdit, QPushButton, QFileDialog, QCheckBox, 
                             QSlider, QLabel, QFrame, QProgressBar, QDialog, QComboBox)
from PyQt6.QtGui import QFont, QColor, QTextCursor, QPalette, QDragEnterEvent, QDropEvent, QShortcut, QKeySequence
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
from cyberpunk_redesign import CYBERPUNK_THEME, get_cyberpunk_font, get_cyberpunk_mono_font, CyberpunkColors

class CompactTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_cyberpunk_mono_font())
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
    def append_ansi_text(self, text):
        self.clear()
        
        
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
            
            img = Image.open(self.file_path)
            
            if self.remove_bg:
                processed_image = remove_background_from_image(self.file_path)
                if processed_image:
                    img = processed_image
            
            if self.aspect_ratio != 'original':
                ratio = AspectRatioMode.get_ratio(self.aspect_ratio)
                if ratio > 0:
                    current_ratio = img.width / img.height
                    if abs(current_ratio - ratio) > 0.1:
                        if ratio > current_ratio:
                            new_width = int(img.height * ratio)
                            img = img.resize((new_width, img.height), Image.Resampling.LANCZOS)
                        else:
                            new_height = int(img.width / ratio)
                            img = img.resize((img.width, new_height), Image.Resampling.LANCZOS)
            
            img = ImageAdjustments.apply_all_adjustments(
                img,
                brightness=self.brightness,
                contrast=self.contrast,
                invert=self.invert
            )
            
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
                total_frames = 0
                try:
                    while True:
                        gif.seek(total_frames)
                        total_frames += 1
                except EOFError:
                    pass
                
                gif.seek(0)
                
                for frame_index in range(total_frames):
                    gif.seek(frame_index)
                    delay = gif.info.get('duration', 100)
                    frame_img = gif.convert('RGB')
                    
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
                    
                    frame_img = ImageAdjustments.apply_all_adjustments(
                        frame_img,
                        brightness=self.brightness,
                        contrast=self.contrast,
                        invert=self.invert
                    )
                    
                    if self.char_set:
                        ascii_frame = convert_image_to_ascii_custom(frame_img, self.columns, self.char_set)
                    else:
                        import tempfile
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
                    
                    self.progress.emit(frame_index + 1, total_frames)
            
            if frames:
                self.finished.emit(frames, delays)
            else:
                self.error.emit("Failed to convert GIF frames")
                
        except Exception as e:
            self.error.emit(f"GIF conversion error: {str(e)}")


class CompactTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_cyberpunk_mono_font())
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
    def append_ansi_text(self, text):
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
                    color = QColor(CyberpunkColors.TEXT_PRIMARY)
                    
                    if 30 <= color_code <= 37:
                        colors = [
                            CyberpunkColors.TEXT_DIM,
                            "#d89aa3",
                            CyberpunkColors.CYAN,
                            "#e0c097",
                            CyberpunkColors.PURPLE,
                            "#c5a3d8",
                            CyberpunkColors.GREEN,
                            CyberpunkColors.TEXT_PRIMARY
                        ]
                        color = QColor(colors[color_code - 30])
                    
                    self.setTextColor(color)
                    self.insertPlainText(text_part)
                except (ValueError, IndexError):
                    self.setTextColor(QColor(CyberpunkColors.TEXT_PRIMARY))
                    self.insertPlainText(part)
            else:
                self.setTextColor(QColor(CyberpunkColors.TEXT_PRIMARY))
                self.insertPlainText(part)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Apply cyberpunk theme
        self.setStyleSheet(CYBERPUNK_THEME)
        self.setFont(get_cyberpunk_font())
        
        # Window setup
        self.setWindowTitle("ASCII GENERATOR v1.0 - with GIF Support")
        
        # Fixed window size - 1280x720
        window_width = 1280
        window_height = 720
        
        # Set size policy
        from PyQt6.QtWidgets import QSizePolicy
        size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(size_policy)
        
        # Center window on screen (initial position and size)
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        
        # Enable drag & drop
        self.setAcceptDrops(True)
        
        self.last_ascii_result = None
        self.is_gif_mode = False
        
        # GIF player
        self.gif_player = GifPlayer()
        self.gif_player.frame_changed.connect(self.display_frame)
        
        # Floating widgets
        self.floating_widgets = []
        
        # History manager
        self.history_manager = HistoryManager()
        self.history_panel = None
        
        # Settings manager
        self.settings_manager = SettingsManager()
        
        # For window dragging
        self.drag_position = None
        self.dragging = False 
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.main_layout.setContentsMargins(8, 8, 8, 8) 
        self.setLayout(self.main_layout)
        
        # Build UI
        self.create_title_bar()
        self.create_main_grid()
        self.create_adjustments_panel()
        self.create_gif_controls()
        
        # Load saved settings
        self.load_settings()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
        # Threading
        self.thread = None
        self.worker = None
        self.gif_thread = None
        self.gif_worker = None
        
        # Hide GIF controls initially
        self.gif_controls_frame.hide()
        
        # Force layout calculation before fixing size
        self.layout().activate()
        QApplication.processEvents()
        self.setFixedSize(1280, 720)
    
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.start_processing)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.on_export)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.open_widget)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.open_history)
        QShortcut(QKeySequence("Space"), self).activated.connect(self.shortcut_play_pause)
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)

    def shortcut_play_pause(self):
        if self.is_gif_mode:
            self.toggle_playback()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) >= 1:
                file_path = urls[0].toLocalFile()
                valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
                if any(file_path.lower().endswith(ext) for ext in valid_extensions):
                    event.accept()
                    return
        event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        pass
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                file_path = urls[0].toLocalFile()
                
                if file_path.lower().endswith('.gif'):
                    self.load_gif(file_path)
                else:
                    self.load_image(file_path)
                
                event.acceptProposedAction()

    def create_title_bar(self):
        """Cyberpunk title bar"""
        self.title_frame = QFrame()
        self.title_frame.setObjectName("titleFrame")
        
        # Make title bar draggable
        self.title_frame.mousePressEvent = self.title_mouse_press
        self.title_frame.mouseMoveEvent = self.title_mouse_move
        self.title_frame.setCursor(Qt.CursorShape.SizeAllCursor)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 4)
        title_layout.setSpacing(6)
        
        title_label = QLabel("ASCII GENERATOR")
        title_label.setObjectName("titleLabel")
        
        subtitle_label = QLabel("// Image & GIF Converter")
        subtitle_label.setObjectName("subtitleLabel")
        
        hint_label = QLabel("↓ Drag & Drop files here")
        hint_label.setObjectName("hintLabel")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        title_layout.addWidget(hint_label)
        
        self.title_frame.setLayout(title_layout)
        self.main_layout.addWidget(self.title_frame)
        self.title_frame.installEventFilter(self)
        
    
    def title_mouse_press(self, event):
        """Handle title bar mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()
    
    def title_mouse_move(self, event):
        """Handle title bar mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def create_main_grid(self):
        """Main grid layout - 2x2 grid on left (1/3 width), OUTPUT on right (2/3 width)"""
        main_horizontal = QHBoxLayout()
        main_horizontal.setSpacing(12)
        main_horizontal.setContentsMargins(0, 0, 0, 0)
        
        # LEFT SIDE - 2x2 Grid (INPUT, WIDTH, STYLE, ACTIONS)
        left_container = QWidget()
        left_grid = QGridLayout()
        left_grid.setSpacing(8)
        left_grid.setContentsMargins(0, 0, 0, 0)
        
        # Row 0: INPUT (col 0) | WIDTH (col 1)
        left_grid.addWidget(self.create_input_box(), 0, 0)
        left_grid.addWidget(self.create_width_box(), 0, 1)
        
        # Row 1: STYLE (col 0) | ACTIONS (col 1)
        left_grid.addWidget(self.create_style_box(), 1, 0)
        left_grid.addWidget(self.create_actions_box(), 1, 1)
        
        # Make columns equal width
        left_grid.setColumnStretch(0, 1)
        left_grid.setColumnStretch(1, 1)
        
        # Make row 0 and row 1 equal height
        left_grid.setRowStretch(0, 1)
        left_grid.setRowStretch(1, 1)
        
        left_container.setLayout(left_grid)
        
        # RIGHT SIDE - OUTPUT (2/3 width)
        right_container = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.create_output_box())
        right_container.setLayout(right_layout)
        
        # Add to main horizontal layout with stretch factors
        # Left: 1/3, Right: 2/3
        main_horizontal.addWidget(left_container, stretch=1)
        main_horizontal.addWidget(right_container, stretch=2)
        
        self.main_layout.addLayout(main_horizontal)

    def create_input_box(self):
        """INPUT box - Cyan border"""
        box = QFrame()
        box.setObjectName("inputBox")
        
        layout = QVBoxLayout()
        layout.setSpacing(4) 
        layout.setContentsMargins(8, 8, 8, 8)
        
        label = QLabel("INPUT")
        label.setObjectName("sectionLabel")
        
        # Image placeholder with icon
        placeholder_container = QFrame()
        placeholder_container.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkColors.BG_INPUT};
                border: 2px dashed {CyberpunkColors.TEXT_DIM};
                border-radius: 8px;
            }}
        """)
        placeholder_container.setMinimumHeight(50)
        placeholder_container.setMaximumHeight(70)
        
        placeholder_layout = QVBoxLayout()
        placeholder_icon = QLabel("🖼️")
        placeholder_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_icon.setStyleSheet("font-size: 16pt; border: none; background: transparent;")
        
        placeholder_text = QLabel("Drop image here")
        placeholder_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_text.setStyleSheet(f"color: {CyberpunkColors.TEXT_DIM}; font-size: 6pt; border: none; background: transparent;")
        
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(placeholder_icon)
        placeholder_layout.addWidget(placeholder_text)
        placeholder_layout.addStretch()
        placeholder_container.setLayout(placeholder_layout)
        
        self.load_button = QPushButton("LOAD")
        self.load_button.setObjectName("loadButton")
        self.load_button.setMinimumHeight(24)
        self.load_button.clicked.connect(self.start_processing)
        self.load_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.bg_checkbox = QCheckBox("Remove Background")
        
        layout.addWidget(label)
        layout.addWidget(placeholder_container)
        layout.addWidget(self.load_button)
        layout.addWidget(self.bg_checkbox)
        
        box.setLayout(layout)
        return box

    def create_width_box(self):
        """WIDTH box - Magenta border"""
        box = QFrame()
        box.setObjectName("widthBox")
        
        layout = QVBoxLayout()
        layout.setSpacing(2) 
        layout.setContentsMargins(8, 8, 8, 8)
        
        label = QLabel("WIDTH")
        label.setObjectName("sectionLabel")
        
        # Large value display - BIG NUMBER
        self.width_label = QLabel("120")
        self.width_label.setObjectName("valueLabel")
        self.width_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.width_label.setStyleSheet(f"""
            QLabel {{
                color: {CyberpunkColors.CYAN};
                font-size: 24pt;
                font-weight: 700;
                padding: 2px 0;
                background: transparent;
                border: none;
            }}
        """)
        
        chars_label = QLabel("chars")
        chars_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chars_label.setStyleSheet(f"color: {CyberpunkColors.TEXT_DIM}; font-size: 7pt; background: transparent; border: none;")
        
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(40, 300)
        self.width_slider.setValue(120)
        self.width_slider.setMinimumHeight(20)
        self.width_slider.valueChanged.connect(self.update_width_label)
        
        # Ratio section
        ratio_label = QLabel("Ratio:")
        ratio_label.setStyleSheet(f"color: {CyberpunkColors.TEXT_SECONDARY}; margin-top: 12px; background: transparent; border: none;")
        
        self.aspect_combo = QComboBox()
        self.aspect_combo.setMinimumHeight(24)
        for mode in AspectRatioMode.get_all_modes():
            self.aspect_combo.addItem(AspectRatioMode.get_display_name(mode), mode)
        
        layout.addWidget(label)
        layout.addWidget(self.width_label)
        layout.addWidget(chars_label)
        layout.addSpacing(2)
        layout.addWidget(self.width_slider)
        layout.addSpacing(4)
        layout.addWidget(ratio_label)
        layout.addWidget(self.aspect_combo)
        
        box.setLayout(layout)
        return box

    def create_style_box(self):
        """STYLE box - Purple border"""
        box = QFrame()
        box.setObjectName("styleBox")
        
        layout = QVBoxLayout()
        layout.setSpacing(4) 
        layout.setContentsMargins(8, 8, 8, 8)
        
        label = QLabel("STYLE")
        label.setObjectName("sectionLabel")
        
        self.charset_combo = QComboBox()
        self.charset_combo.setMinimumHeight(24)
        for preset in CharacterSetManager.get_all_presets():
            display_name = CharacterSetManager.get_display_name(preset)
            self.charset_combo.addItem(display_name, preset)
        
        self.charset_combo.currentIndexChanged.connect(self.update_charset_preview)
        
        # Preview area with proper styling
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet(f"color: {CyberpunkColors.TEXT_SECONDARY}; font-size: 9pt; background: transparent; border: none;")
        
        self.charset_preview = QLabel("@@@%%%###***")
        self.charset_preview.setMinimumHeight(40)
        self.charset_preview.setStyleSheet(f"""
            QLabel {{
                color: {CyberpunkColors.CYAN};
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                padding: 8px;
                background-color: {CyberpunkColors.BG_DARK};
                border: 1px solid {CyberpunkColors.TEXT_DIM};
                border-radius: 6px;
            }}
        """)
        self.charset_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.charset_preview.setWordWrap(True)
        
        layout.addWidget(label)
        layout.addWidget(self.charset_combo)
        layout.addSpacing(4)
        layout.addWidget(preview_label)
        layout.addWidget(self.charset_preview)
        
        box.setLayout(layout)
        return box

    def create_actions_box(self):
        """ACTIONS box - Green border - NO nested borders on buttons"""
        box = QFrame()
        box.setObjectName("actionsBox")
        
        layout = QVBoxLayout()
        layout.setSpacing(4) 
        layout.setContentsMargins(8, 8, 8, 8)
        
        label = QLabel("ACTIONS")
        label.setObjectName("sectionLabel")
        
        # Buttons WITHOUT objectName (no special border styling)
        self.export_button = QPushButton("💾 SAVE")
        self.export_button.setDisabled(True)
        self.export_button.setMinimumHeight(26)
        self.export_button.clicked.connect(self.on_export)
        self.export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkColors.BG_PANEL};
                color: {CyberpunkColors.TEXT_PRIMARY};
                border: 2px solid {CyberpunkColors.TEXT_DIM};
                border-radius: 6px;
                padding: 10px;
                font-weight: 600;
                font-size: 10pt;
            }}
            QPushButton:hover:!disabled {{
                border-color: {CyberpunkColors.BTN_SAVE};
                color: {CyberpunkColors.BTN_SAVE};
                background-color: rgba(255, 0, 110, 0.1);
            }}
            QPushButton:disabled {{
                color: {CyberpunkColors.TEXT_DIM};
                border-color: {CyberpunkColors.TEXT_DIM};
            }}
        """)
        
        self.widget_button = QPushButton("🪟 WINDOW")
        self.widget_button.setDisabled(True)
        self.widget_button.setMinimumHeight(26)
        self.widget_button.clicked.connect(self.open_widget)
        self.widget_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.widget_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkColors.BG_PANEL};
                color: {CyberpunkColors.TEXT_PRIMARY};
                border: 2px solid {CyberpunkColors.TEXT_DIM};
                border-radius: 6px;
                padding: 10px;
                font-weight: 600;
                font-size: 10pt;
            }}
            QPushButton:hover:!disabled {{
                border-color: {CyberpunkColors.BTN_WINDOW};
                color: {CyberpunkColors.BTN_WINDOW};
                background-color: rgba(139, 92, 246, 0.1);
            }}
            QPushButton:disabled {{
                color: {CyberpunkColors.TEXT_DIM};
                border-color: {CyberpunkColors.TEXT_DIM};
            }}
        """)
        
        self.history_button = QPushButton("📚 HISTORY")
        self.history_button.setMinimumHeight(26)
        self.history_button.clicked.connect(self.open_history)
        self.history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkColors.BG_PANEL};
                color: {CyberpunkColors.TEXT_PRIMARY};
                border: 2px solid {CyberpunkColors.TEXT_DIM};
                border-radius: 6px;
                padding: 10px;
                font-weight: 600;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                border-color: {CyberpunkColors.BTN_HISTORY};
                color: {CyberpunkColors.BTN_HISTORY};
                background-color: rgba(59, 130, 246, 0.1);
            }}
        """)
        
        self.quit_button = QPushButton("✕ QUIT")
        self.quit_button.setMinimumHeight(26)
        self.quit_button.clicked.connect(self.close)
        self.quit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {CyberpunkColors.BG_PANEL};
                color: {CyberpunkColors.TEXT_PRIMARY};
                border: 2px solid {CyberpunkColors.TEXT_DIM};
                border-radius: 6px;
                padding: 10px;
                font-weight: 600;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                border-color: {CyberpunkColors.BTN_QUIT};
                color: {CyberpunkColors.BTN_QUIT};
                background-color: rgba(239, 68, 68, 0.1);
            }}
        """)
        
        layout.addWidget(label)
        layout.addWidget(self.export_button)
        layout.addWidget(self.widget_button)
        layout.addWidget(self.history_button)
        layout.addWidget(self.quit_button)
        
        box.setLayout(layout)
        return box

    def create_output_box(self):
        """OUTPUT box - Blue/Purple border"""
        box = QFrame()
        box.setObjectName("outputBox")
        
        layout = QVBoxLayout()
        layout.setSpacing(4) 
        layout.setContentsMargins(12, 12, 12, 12)
        
        label = QLabel("OUTPUT")
        label.setObjectName("sectionLabel")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(24)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        
        # Text display
        self.text_area = CompactTextEdit()
        self.text_area.setPlaceholderText("// No output yet\nLoad an image or GIF to generate ASCII art")
        self.text_area.setMinimumHeight(150)
        
        layout.addWidget(label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.text_area)
        
        box.setLayout(layout)
        return box

    def create_adjustments_panel(self):
        """ADJUSTMENTS panel - Cyan border, wide"""
        box = QFrame()
        box.setObjectName("adjustmentsBox")
        
        layout = QHBoxLayout()
        layout.setSpacing(8) 
        layout.setContentsMargins(12, 8, 12, 8) 
        
        label = QLabel("ADJUSTMENTS")
        label.setObjectName("sectionLabel")
        
        # Invert checkbox
        self.invert_checkbox = QCheckBox("INVERT")
        
        # Reset button
        reset_btn = QPushButton("↻ RESET")
        reset_btn.setObjectName("resetButton")
        reset_btn.clicked.connect(self.reset_adjustments)
        
        # Brightness
        bright_layout = QVBoxLayout()
        bright_layout.setSpacing(4)
        
        bright_header = QHBoxLayout()
        bright_label = QLabel("Brightness:")
        self.brightness_value_label = QLabel("0")
        self.brightness_value_label.setStyleSheet(f"color: {CyberpunkColors.CYAN}; font-weight: 600;")
        bright_header.addWidget(bright_label)
        bright_header.addStretch()
        bright_header.addWidget(self.brightness_value_label)
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setMinimumWidth(90)
        self.brightness_slider.valueChanged.connect(self.update_brightness_label)
        
        bright_layout.addLayout(bright_header)
        bright_layout.addWidget(self.brightness_slider)
        
        # Contrast
        contrast_layout = QVBoxLayout()
        contrast_layout.setSpacing(4)
        
        contrast_header = QHBoxLayout()
        contrast_label = QLabel("Contrast:")

        self.contrast_value_label = QLabel("100%")
        self.contrast_value_label.setStyleSheet(f"color: {CyberpunkColors.CYAN}; font-weight: 600;")
        contrast_header.addWidget(contrast_label)
        contrast_header.addStretch()
        contrast_header.addWidget(self.contrast_value_label)
        
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(25, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setMinimumWidth(90)
        self.contrast_slider.valueChanged.connect(self.update_contrast_label)
        
        contrast_layout.addLayout(contrast_header)
        contrast_layout.addWidget(self.contrast_slider)
        
        layout.addWidget(label)
        layout.addSpacing(16)
        layout.addWidget(self.invert_checkbox)
        layout.addWidget(reset_btn)
        layout.addSpacing(24)
        layout.addLayout(bright_layout)
        layout.addSpacing(16)
        layout.addLayout(contrast_layout)
        layout.addStretch()
        
        box.setLayout(layout)
        self.main_layout.addWidget(box)

    def create_gif_controls(self):
        """GIF playback controls"""
        self.gif_controls_frame = QFrame()
        self.gif_controls_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CyberpunkColors.BG_PANEL};
                border: 2px solid {CyberpunkColors.PURPLE};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(4) 
        layout.setContentsMargins(8, 6, 8, 6) 
        
        label = QLabel("PLAYBACK")
        label.setObjectName("sectionLabel")
        
        self.play_button = QPushButton("▶ PLAY")
        self.play_button.setMinimumHeight(26)
        self.play_button.clicked.connect(self.toggle_playback)
        
        self.stop_button = QPushButton("■ STOP")
        self.stop_button.setMinimumHeight(26)
        self.stop_button.clicked.connect(self.stop_animation)
        
        speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(25, 400)
        self.speed_slider.setValue(100)
        self.speed_slider.setMinimumWidth(100)
        self.speed_slider.valueChanged.connect(self.update_speed)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setStyleSheet(f"color: {CyberpunkColors.CYAN}; font-weight: 600; min-width: 40px;")
        
        self.loop_checkbox = QCheckBox("LOOP")
        self.loop_checkbox.setChecked(True)
        self.loop_checkbox.toggled.connect(self.gif_player.set_looping)
        
        self.frame_label = QLabel("Frame: 0/0")
        self.frame_label.setStyleSheet(f"color: {CyberpunkColors.TEXT_SECONDARY};")
        
        layout.addWidget(label)
        layout.addSpacing(8)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addSpacing(16)
        layout.addWidget(speed_label)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.speed_label)
        layout.addSpacing(16)
        layout.addWidget(self.loop_checkbox)
        layout.addStretch()
        layout.addWidget(self.frame_label)
        
        self.gif_controls_frame.setLayout(layout)
        self.main_layout.addWidget(self.gif_controls_frame)

    # Update methods
    def update_width_label(self, value):
        self.width_label.setText(str(value))

    def update_brightness_label(self, value):
        sign = "+" if value > 0 else ""
        self.brightness_value_label.setText(f"{sign}{value}")

    def update_contrast_label(self, value):
        self.contrast_value_label.setText(f"{value}%")

    def update_charset_preview(self):
        preset = self.charset_combo.currentData()
        if preset:
            preview = CharacterSetManager.get_preview(preset)
            self.charset_preview.setText(preview)

    def reset_adjustments(self):
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(100)
        self.invert_checkbox.setChecked(False)

    def update_speed(self, value):
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.1f}x")
        self.gif_player.set_speed(speed)

    # Processing methods
    def start_processing(self):
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
        self.is_gif_mode = False
        self.gif_controls_frame.hide()
        self.gif_player.pause()
        
        self.last_loaded_file = file_path
        
        self.load_button.setDisabled(True)
        self.export_button.setDisabled(True)
        self.text_area.clear()
        self.text_area.insertPlainText("// PROCESSING IMAGE...")

        columns = self.width_slider.value()
        remove_bg = self.bg_checkbox.isChecked()
        
        preset = self.charset_combo.currentData()
        char_set = None
        if preset and preset != CharacterSet.DETAILED:
            char_set = CharacterSetManager.get_character_set(preset)
        
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        invert = self.invert_checkbox.isChecked()
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
        self.is_gif_mode = True
        self.gif_controls_frame.show()
        
        self.last_loaded_file = file_path
        
        self.load_button.setDisabled(True)
        self.export_button.setDisabled(True)
        self.text_area.clear()
        self.text_area.insertPlainText("// CONVERTING GIF...\n// This may take a moment...")
        
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        columns = self.width_slider.value()
        
        preset = self.charset_combo.currentData()
        char_set = None
        if preset and preset != CharacterSet.DETAILED:
            char_set = CharacterSetManager.get_character_set(preset)
        
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        invert = self.invert_checkbox.isChecked()
        aspect_mode = self.aspect_combo.currentData()

        self.gif_thread = QThread()
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
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_bar.setFormat(f"Converting: {current}/{total} frames")

    def on_gif_converted(self, frames, delays):
        self.progress_bar.hide()
        self.gif_player.load_animation(frames, delays)
        self.load_button.setDisabled(False)
        self.export_button.setDisabled(False)
        self.widget_button.setDisabled(False)
        
        total_frames = len(frames)
        self.frame_label.setText(f"Frame: 1/{total_frames}")
        
        self.text_area.append_ansi_text(frames[0])
        
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
                frames=None,
                delays=delays
            )
        
        self.gif_player.play()
        self.play_button.setText("⏸ PAUSE")

    def on_gif_error(self, error_msg):
        self.progress_bar.hide()
        self.text_area.clear()
        self.text_area.insertPlainText(f"// ERROR\n// {error_msg}")
        self.load_button.setDisabled(False)

    def display_frame(self, frame_text, frame_number):
        self.text_area.append_ansi_text(frame_text)
        total = self.gif_player.get_frame_count()
        self.frame_label.setText(f"Frame: {frame_number + 1}/{total}")

    def toggle_playback(self):
        if self.gif_player.is_playing:
            self.gif_player.pause()
            self.play_button.setText("▶ PLAY")
        else:
            self.gif_player.play()
            self.play_button.setText("⏸ PAUSE")

    def stop_animation(self):
        self.gif_player.stop()
        self.play_button.setText("▶ PLAY")

    def update_text_area(self, ascii_result: str):
        self.last_ascii_result = ascii_result
        self.text_area.append_ansi_text(ascii_result)
        self.load_button.setDisabled(False)
        
        if not ascii_result.startswith("Error"):
            self.export_button.setDisabled(False)
            self.widget_button.setDisabled(False)
            
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
        if self.is_gif_mode:
            if not self.gif_player.frames:
                return
            
            try:
                dialog = GifExportDialog(self)
                result = dialog.exec()
                
                if result == QDialog.DialogCode.Accepted:
                    format_type, output_path = dialog.get_export_info()
                    
                    if not output_path:
                        return
                    
                    self.text_area.insertPlainText(f"\n\n// EXPORTING as {format_type.upper()}...")
                    QApplication.processEvents()
                    
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
        font_size = self.settings_manager.get('widget_font_size', 9)
        color_theme = self.settings_manager.get('widget_color_theme', 'grape')
        
        widget = FloatingAsciiWidget(font_size=font_size, color_theme=color_theme)
        
        if self.is_gif_mode and self.gif_player.frames:
            widget.set_animation(
                self.gif_player.frames,
                self.gif_player.delays
            )
        elif self.last_ascii_result:
            widget.set_ascii_text(self.last_ascii_result)
        
        self.floating_widgets.append(widget)
        widget.destroyed.connect(lambda: self.on_widget_closed(widget))
        
        widget.show()
        widget.raise_()
        widget.activateWindow()

    def on_widget_closed(self, widget):
        if widget in self.floating_widgets:
            self.floating_widgets.remove(widget)

    def open_history(self):
        if self.history_panel is None or not self.history_panel.isVisible():
            self.history_panel = HistoryPanel(self.history_manager, self)
            self.history_panel.entry_selected.connect(self.on_history_entry_selected)
        
        self.history_panel.show()
        self.history_panel.raise_()
        self.history_panel.activateWindow()

    def on_history_entry_selected(self, entry):
        if hasattr(entry, 'open_in_widget') and entry.open_in_widget:
            widget = FloatingAsciiWidget()
            widget.set_ascii_text(entry.ascii_result)
            self.floating_widgets.append(widget)
            widget.destroyed.connect(lambda: self.on_widget_closed(widget))
            widget.show()
            widget.raise_()
            widget.activateWindow()
        else:
            self.text_area.append_ansi_text(entry.ascii_result)
            self.last_ascii_result = entry.ascii_result
            self.export_button.setDisabled(False)
            self.widget_button.setDisabled(False)

    def load_settings(self):
        self.width_slider.setValue(self.settings_manager.get('width', 120))
        
        char_set = self.settings_manager.get('character_set', 'detailed')
        for i in range(self.charset_combo.count()):
            if self.charset_combo.itemData(i).value == char_set:
                self.charset_combo.setCurrentIndex(i)
                break
        
        self.brightness_slider.setValue(self.settings_manager.get('brightness', 0))
        self.contrast_slider.setValue(self.settings_manager.get('contrast', 100))
        self.invert_checkbox.setChecked(self.settings_manager.get('invert', False))
        self.bg_checkbox.setChecked(self.settings_manager.get('remove_background', False))
        
        aspect_mode = self.settings_manager.get('aspect_ratio', 'original')
        for i in range(self.aspect_combo.count()):
            if self.aspect_combo.itemData(i) == aspect_mode:
                self.aspect_combo.setCurrentIndex(i)
                break
        
        win_width = self.settings_manager.get('window_width', 1280)
        win_height = self.settings_manager.get('window_height', 720)
        win_x = self.settings_manager.get('window_x', 100)
        win_y = self.settings_manager.get('window_y', 100)
        
        self.setGeometry(win_x, win_y, win_width, win_height)

    def save_settings(self):
        self.settings_manager.set('width', self.width_slider.value())
        
        preset = self.charset_combo.currentData()
        if preset:
            self.settings_manager.set('character_set', preset.value)
        
        self.settings_manager.set('brightness', self.brightness_slider.value())
        self.settings_manager.set('contrast', self.contrast_slider.value())
        self.settings_manager.set('invert', self.invert_checkbox.isChecked())
        self.settings_manager.set('remove_background', self.bg_checkbox.isChecked())
        
        aspect_mode = self.aspect_combo.currentData()
        if aspect_mode:
            self.settings_manager.set('aspect_ratio', aspect_mode)
        
        self.settings_manager.set('window_width', self.width())
        self.settings_manager.set('window_height', self.height())
        self.settings_manager.set('window_x', self.x())
        self.settings_manager.set('window_y', self.y())

    def closeEvent(self, event):
        self.save_settings()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setFont(get_cyberpunk_font())
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(CyberpunkColors.BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(CyberpunkColors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(CyberpunkColors.BG_DARK))
    palette.setColor(QPalette.ColorRole.Text, QColor(CyberpunkColors.TEXT_PRIMARY))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()