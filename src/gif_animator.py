"""
GIF Animation Engine for ASCII Art
Converts GIF frames to ASCII and plays them back
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PIL import Image, ImageSequence
import tempfile
import os
from converter import convert_image_to_ascii


class GifConverter(QObject):
    """Converts GIF to ASCII frames"""
    
    frame_converted = pyqtSignal(int, int)  # current, total
    conversion_complete = pyqtSignal(list, list)  # frames, delays
    conversion_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.frames = []
        self.delays = []
        self.is_cancelled = False
    
    def cancel(self):
        """Cancel ongoing conversion"""
        self.is_cancelled = True
    
    def convert_gif(self, gif_path, columns=120):
        """
        Convert all GIF frames to ASCII art
        
        Args:
            gif_path: Path to GIF file
            columns: ASCII width in characters
        
        Returns:
            (frames, delays) tuple
        """
        self.frames = []
        self.delays = []
        self.is_cancelled = False
        
        try:
            with Image.open(gif_path) as gif:
                # Get total frame count
                total_frames = 0
                try:
                    while True:
                        gif.seek(total_frames)
                        total_frames += 1
                except EOFError:
                    pass
                
                gif.seek(0)  # Reset to first frame
                
                # Convert each frame
                for frame_index in range(total_frames):
                    if self.is_cancelled:
                        self.conversion_error.emit("Conversion cancelled")
                        return [], []
                    
                    gif.seek(frame_index)
                    
                    # Get frame delay (in milliseconds)
                    delay = gif.info.get('duration', 100)
                    
                    # Convert frame to RGB
                    frame_rgb = gif.convert('RGB')
                    
                    # Save to temp file for ASCII conversion
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        frame_rgb.save(tmp.name, 'PNG')
                        temp_path = tmp.name
                    
                    # Convert to ASCII
                    ascii_frame = convert_image_to_ascii(temp_path, columns=columns)
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                    
                    if ascii_frame:
                        self.frames.append(ascii_frame)
                        self.delays.append(delay)
                        self.frame_converted.emit(frame_index + 1, total_frames)
                    else:
                        self.conversion_error.emit(f"Failed to convert frame {frame_index}")
                        return [], []
                
                self.conversion_complete.emit(self.frames, self.delays)
                return self.frames, self.delays
                
        except Exception as e:
            self.conversion_error.emit(f"GIF conversion error: {str(e)}")
            return [], []


class GifPlayer(QObject):
    """Plays back ASCII animation frames"""
    
    frame_changed = pyqtSignal(str, int)  # frame_text, frame_number
    playback_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.frames = []
        self.delays = []
        self.current_frame = 0
        self.is_playing = False
        self.is_looping = True
        self.playback_speed = 1.0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._next_frame)
    
    def load_animation(self, frames, delays):
        """Load animation data"""
        self.frames = frames
        self.delays = delays
        self.current_frame = 0
    
    def play(self):
        """Start playing animation"""
        if not self.frames:
            return
        
        self.is_playing = True
        self._show_current_frame()
        self._schedule_next_frame()
    
    def pause(self):
        """Pause animation"""
        self.is_playing = False
        self.timer.stop()
    
    def stop(self):
        """Stop and reset animation"""
        self.pause()
        self.current_frame = 0
        if self.frames:
            self._show_current_frame()
    
    def set_speed(self, speed):
        """
        Set playback speed multiplier
        
        Args:
            speed: 0.5 = half speed, 1.0 = normal, 2.0 = double speed
        """
        self.playback_speed = max(0.1, min(speed, 5.0))
    
    def set_looping(self, loop):
        """Enable/disable looping"""
        self.is_looping = loop
    
    def goto_frame(self, frame_number):
        """Jump to specific frame"""
        if 0 <= frame_number < len(self.frames):
            self.current_frame = frame_number
            self._show_current_frame()
    
    def _show_current_frame(self):
        """Display current frame"""
        if self.frames and 0 <= self.current_frame < len(self.frames):
            frame_text = self.frames[self.current_frame]
            self.frame_changed.emit(frame_text, self.current_frame)
    
    def _next_frame(self):
        """Advance to next frame"""
        if not self.is_playing:
            return
        
        self.current_frame += 1
        
        # Check if reached end
        if self.current_frame >= len(self.frames):
            if self.is_looping:
                self.current_frame = 0
            else:
                self.pause()
                self.playback_finished.emit()
                return
        
        self._show_current_frame()
        self._schedule_next_frame()
    
    def _schedule_next_frame(self):
        """Schedule next frame based on delay and speed"""
        if self.delays and self.current_frame < len(self.delays):
            base_delay = self.delays[self.current_frame]
            adjusted_delay = int(base_delay / self.playback_speed)
            adjusted_delay = max(10, adjusted_delay)  # Minimum 10ms
            self.timer.start(adjusted_delay)
    
    def get_frame_count(self):
        """Get total number of frames"""
        return len(self.frames)
    
    def get_current_frame_number(self):
        """Get current frame index"""
        return self.current_frame


class GifAnimationManager:
    """
    High-level manager for GIF animations
    Combines converter and player
    """
    
    def __init__(self):
        self.converter = GifConverter()
        self.player = GifPlayer()
        self.is_gif_loaded = False
    
    def load_gif(self, gif_path, columns=120):
        """Load and convert GIF file"""
        self.converter.convert_gif(gif_path, columns)
    
    def set_frames(self, frames, delays):
        """Set animation frames directly"""
        self.player.load_animation(frames, delays)
        self.is_gif_loaded = len(frames) > 0
    
    def play(self):
        """Play animation"""
        self.player.play()
    
    def pause(self):
        """Pause animation"""
        self.player.pause()
    
    def stop(self):
        """Stop animation"""
        self.player.stop()
    
    def set_speed(self, speed):
        """Set playback speed"""
        self.player.set_speed(speed)
    
    def set_looping(self, enabled):
        """Enable/disable looping"""
        self.player.set_looping(enabled)
    
    def is_playing(self):
        """Check if currently playing"""
        return self.player.is_playing
    
    def has_animation(self):
        """Check if animation is loaded"""
        return self.is_gif_loaded