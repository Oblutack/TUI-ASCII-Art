# src/ascii_widget.py
"""
Floating ASCII Art Widget
Always-on-top, draggable, resizable window for displaying ASCII art
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QSlider, QFrame)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QFont, QColor, QTextCursor
from styles.compact_theme import get_compact_font, CompactColors


class FloatingAsciiWidget(QWidget):
    """
    Floating widget for displaying ASCII art
    Features: Always on top, draggable, semi-transparent
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Window flags for floating behavior
        self.setWindowFlags(
            Qt.WindowType.Tool |  # Tool window (no taskbar entry)
            Qt.WindowType.FramelessWindowHint |  # No title bar
            Qt.WindowType.WindowStaysOnTopHint  # Always on top
        )
        
        # Semi-transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # For dragging
        self.dragging = False
        self.drag_position = QPoint()
        
        # For resizing
        self.resizing = False
        self.resize_start_pos = QPoint()
        self.resize_start_size = self.size()
        
        # UI visibility state
        self.ui_visible = True
        
        # Animation state
        self.is_animated = False
        self.animation_frames = []
        self.animation_delays = []
        self.current_frame = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._next_animation_frame)
        
        # Setup UI
        self.init_ui()
        
        # Default size
        self.resize(500, 400)
    
    def init_ui(self):
        """Initialize widget UI"""
        # Main container with styling
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(48, 41, 47, 240);
                border: 3px solid {CompactColors.DUSTY_GRAPE};
                border-radius: 0px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setLayout(layout)
        
        # Title bar
        self.title_bar = self.create_title_bar()
        layout.addWidget(self.title_bar)
        
        # ASCII display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(get_compact_font())
        self.text_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(48, 41, 47, 250);
                color: {CompactColors.GRAPE_BRIGHT};
                border: none;
                padding: 10px;
                font-size: 9pt;
            }}
        """)
        layout.addWidget(self.text_display, stretch=1)
        
        # Control bar (for animations)
        self.control_bar = self.create_control_bar()
        layout.addWidget(self.control_bar)
        self.control_bar.hide()  # Hidden by default
        
        # Resize handle
        self.resize_handle = self.create_resize_handle()
        layout.addWidget(self.resize_handle)
        
        # Set container as main widget
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
    
    def create_title_bar(self):
        """Create draggable title bar"""
        title_bar = QFrame()
        title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(65, 63, 84, 255);
                border-bottom: 2px solid {CompactColors.DUSTY_GRAPE};
                padding: 6px;
            }}
        """)
        title_bar.setFixedHeight(35)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel("▌ASCII WIDGET")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {CompactColors.DUSTY_GRAPE};
                font-weight: bold;
                font-size: 10pt;
            }}
        """)
        
        layout.addWidget(title_label)
        layout.addStretch()
        
        # Opacity slider
        opacity_label = QLabel("👁")
        opacity_label.setToolTip("Opacity")
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(95)
        self.opacity_slider.setMaximumWidth(80)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        self.opacity_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background-color: rgba(48, 41, 47, 200);
                height: 4px;
                border-radius: 0px;
            }}
            QSlider::handle:horizontal {{
                background-color: {CompactColors.DUSTY_GRAPE};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 0px;
            }}
        """)
        
        layout.addWidget(opacity_label)
        layout.addWidget(self.opacity_slider)
        
        layout.addSpacing(8)
        
        # Hide/Show UI button - MORE VISIBLE
        self.hide_ui_btn = QPushButton("⬜ HIDE")
        self.hide_ui_btn.setFixedHeight(24)
        self.hide_ui_btn.setMinimumWidth(60)
        self.hide_ui_btn.setToolTip("Hide UI (Click widget to restore)")
        self.hide_ui_btn.clicked.connect(self.toggle_ui_visibility)
        self.hide_ui_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CompactColors.DUSTY_GRAPE};
                color: white;
                border: 2px solid {CompactColors.GRAPE_LIGHT};
                font-weight: bold;
                font-size: 9pt;
                padding: 2px 8px;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: {CompactColors.GRAPE_LIGHT};
                border-color: white;
            }}
        """)
        
        layout.addWidget(self.hide_ui_btn)
        layout.addSpacing(8)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(139, 95, 101, 200);
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(216, 154, 163, 255);
            }}
        """)
        
        layout.addWidget(close_btn)
        
        title_bar.setLayout(layout)
        return title_bar
    
    def create_control_bar(self):
        """Create animation control bar"""
        control_bar = QFrame()
        control_bar.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(63, 64, 69, 255);
                border-top: 2px solid {CompactColors.DUSTY_GRAPE};
                padding: 4px;
            }}
        """)
        control_bar.setFixedHeight(40)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Play/Pause button
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(28, 28)
        self.play_pause_btn.clicked.connect(self.toggle_animation)
        self.play_pause_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(95, 90, 162, 200);
                color: white;
                border: 2px solid {CompactColors.DUSTY_GRAPE};
                font-weight: bold;
                border-radius: 0px;
            }}
        """)
        
        # Frame label
        self.frame_label = QLabel("0/0")
        self.frame_label.setStyleSheet(f"color: {CompactColors.TEXT_SECONDARY}; font-size: 9pt;")
        
        # Speed control
        speed_label = QLabel("⚡")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(25, 300)
        self.speed_slider.setValue(100)
        self.speed_slider.setMaximumWidth(100)
        self.speed_slider.valueChanged.connect(self.update_animation_speed)
        
        layout.addWidget(self.play_pause_btn)
        layout.addWidget(self.frame_label)
        layout.addSpacing(10)
        layout.addWidget(speed_label)
        layout.addWidget(self.speed_slider)
        layout.addStretch()
        
        control_bar.setLayout(layout)
        return control_bar
    
    def create_resize_handle(self):
        """Create resize handle indicator"""
        handle = QLabel("⋰")
        handle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        handle.setFixedHeight(20)
        handle.setStyleSheet(f"""
            QLabel {{
                color: {CompactColors.TEXT_DIM};
                font-size: 16pt;
                padding-right: 4px;
                background-color: transparent;
            }}
        """)
        handle.setCursor(Qt.CursorShape.SizeFDiagCursor)
        return handle
    
    def set_ascii_text(self, text):
        """Set static ASCII art text"""
        self.is_animated = False
        self.animation_timer.stop()
        self.control_bar.hide()
        self._display_text(text)
    
    def set_animation(self, frames, delays):
        """Set animated ASCII art"""
        self.is_animated = True
        self.animation_frames = frames
        self.animation_delays = delays
        self.current_frame = 0
        self.control_bar.show()
        
        if frames:
            self._display_text(frames[0])
            self.frame_label.setText(f"1/{len(frames)}")
    
    def _display_text(self, text):
        """Display text with ANSI color support"""
        self.text_display.clear()
        self.text_display.moveCursor(QTextCursor.MoveOperation.End)
        
        # Parse ANSI codes
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
                    
                    self.text_display.setTextColor(color)
                    self.text_display.insertPlainText(text_part)
                except:
                    self.text_display.setTextColor(QColor(CompactColors.GRAPE_BRIGHT))
                    self.text_display.insertPlainText(part)
            else:
                self.text_display.setTextColor(QColor(CompactColors.GRAPE_BRIGHT))
                self.text_display.insertPlainText(part)
    
    def toggle_animation(self):
        """Toggle animation play/pause"""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.play_pause_btn.setText("▶")
        else:
            self._play_animation()
            self.play_pause_btn.setText("⏸")
    
    def _play_animation(self):
        """Start animation playback"""
        if not self.animation_frames:
            return
        self._schedule_next_frame()
    
    def _next_animation_frame(self):
        """Show next animation frame"""
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        self._display_text(self.animation_frames[self.current_frame])
        self.frame_label.setText(f"{self.current_frame + 1}/{len(self.animation_frames)}")
        self._schedule_next_frame()
    
    def _schedule_next_frame(self):
        """Schedule next frame based on delay and speed"""
        if self.current_frame < len(self.animation_delays):
            base_delay = self.animation_delays[self.current_frame]
            speed = self.speed_slider.value() / 100.0
            adjusted_delay = int(base_delay / speed)
            adjusted_delay = max(10, adjusted_delay)
            self.animation_timer.start(adjusted_delay)
    
    def update_animation_speed(self, value):
        """Update animation speed"""
        # Speed will be applied on next frame
        pass
    
    def update_opacity(self, value):
        """Update window opacity"""
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
    
    def toggle_ui_visibility(self):
        """Toggle visibility of UI elements (title bar, controls)"""
        self.ui_visible = not self.ui_visible
        
        if self.ui_visible:
            # Show UI - restore background
            self.title_bar.show()
            if self.is_animated:
                self.control_bar.show()
            self.resize_handle.show()
            self.hide_ui_btn.setText("⬜ HIDE")
            self.hide_ui_btn.setToolTip("Hide UI")
            
            # Restore background for main container
            self.findChild(QFrame).setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(48, 41, 47, 240);
                    border: 3px solid {CompactColors.DUSTY_GRAPE};
                    border-radius: 0px;
                }}
            """)
            
            # Restore text display background
            self.text_display.setStyleSheet(f"""
                QTextEdit {{
                    background-color: rgba(48, 41, 47, 250);
                    color: {CompactColors.GRAPE_BRIGHT};
                    border: none;
                    padding: 10px;
                    font-size: 9pt;
                }}
            """)
        else:
            # Hide UI - make transparent
            self.title_bar.hide()
            self.control_bar.hide()
            self.resize_handle.hide()
            
            # Make main container transparent
            self.findChild(QFrame).setStyleSheet(f"""
                QFrame {{
                    background-color: transparent;
                    border: none;
                    border-radius: 0px;
                }}
            """)
            
            # Make text display fully transparent
            self.text_display.setStyleSheet(f"""
                QTextEdit {{
                    background-color: transparent;
                    color: {CompactColors.GRAPE_BRIGHT};
                    border: none;
                    padding: 10px;
                    font-size: 9pt;
                }}
            """)
    
    # Mouse events for dragging
    def mousePressEvent(self, event):
        """Handle mouse press for dragging, resizing, and UI toggle"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking near bottom-right corner (resize)
            corner_size = 20
            if (self.ui_visible and 
                event.pos().x() > self.width() - corner_size and 
                event.pos().y() > self.height() - corner_size):
                self.resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_size = self.size()
            # Check if UI is hidden and clicking on text area (show UI)
            elif not self.ui_visible:
                self.toggle_ui_visibility()
            else:
                # Normal drag
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging and resizing"""
        if self.dragging:
            # Move window
            self.move(event.globalPosition().toPoint() - self.drag_position)
        elif self.resizing:
            # Resize window
            delta = event.globalPosition().toPoint() - self.resize_start_pos
            new_width = max(300, self.resize_start_size.width() + delta.x())
            new_height = max(200, self.resize_start_size.height() + delta.y())
            self.resize(new_width, new_height)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
    
    def mouseDoubleClickEvent(self, event):
        """Double click to toggle size"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Toggle between small and large
            if self.width() < 600:
                self.resize(800, 600)
            else:
                self.resize(400, 300)