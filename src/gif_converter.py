# src/gif_converter.py

from PIL import Image, ImageSequence
import ascii_magic
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
import tempfile
import os

class GifToAsciiConverter(QObject):
    frame_ready = pyqtSignal(str, int)  # (ascii_frame, frame_number)
    conversion_complete = pyqtSignal(list, list)  # (frames, delays)
    
    def __init__(self):
        super().__init__()
        self.frames = []
        self.delays = []
        
    def convert_gif(self, gif_path, width=80, mode='detailed'):
        """Convert GIF to list of ASCII frames"""
        try:
            img = Image.open(gif_path)
            
            frame_count = 0
            for frame in ImageSequence.Iterator(img):
                # Convert frame to ASCII
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    frame.convert('RGB').save(tmp.name)
                    
                    ascii_art = ascii_magic.from_image_file(
                        tmp.name,
                        columns=width,
                        mode=ascii_magic.Modes.ASCII
                    )
                    
                    self.frames.append(str(ascii_art))
                    
                    # Get frame delay (in milliseconds)
                    delay = frame.info.get('duration', 100)
                    self.delays.append(delay)
                    
                    self.frame_ready.emit(str(ascii_art), frame_count)
                    frame_count += 1
                    
                    os.unlink(tmp.name)
            
            self.conversion_complete.emit(self.frames, self.delays)
            return self.frames, self.delays
            
        except Exception as e:
            print(f"Error converting GIF: {e}")
            return [], []

class AsciiAnimationPlayer(QObject):
    """Play ASCII animation frames"""
    
    def __init__(self):
        super().__init__()
        self.frames = []
        self.delays = []
        self.current_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.is_playing = False
        
    def load_animation(self, frames, delays):
        self.frames = frames
        self.delays = delays
        self.current_frame = 0
        
    def play(self):
        if not self.frames:
            return
        self.is_playing = True
        self._schedule_next_frame()
        
    def pause(self):
        self.is_playing = False
        self.timer.stop()
        
    def stop(self):
        self.pause()
        self.current_frame = 0
        
    def next_frame(self):
        if not self.is_playing:
            return
            
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self._schedule_next_frame()
        
    def _schedule_next_frame(self):
        if self.delays and self.current_frame < len(self.delays):
            delay = self.delays[self.current_frame]
            self.timer.start(delay)
        
    def get_current_frame(self):
        if self.frames and self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return ""