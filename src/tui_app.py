import logging
logging.basicConfig(
    filename='debug_log.txt',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


from textual.widgets import Button, Checkbox, Static, Header, Footer, Slider
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual import on, work
from textual.timer import Timer
from rich.text import Text
from typing import Optional, List, Tuple
import tkinter as tk
from tkinter import filedialog
from textual.message import Message
import os

from .converter import convert_image_to_ascii, convert_gif_to_ascii_frames
from .background import remove_background_from_image


class StatusUpdate(Message):
    def __init__(self, text: str) -> None: super().__init__(); self.text = text
class ResultUpdate(Message):
    def __init__(self, result: Optional[str]) -> None: super().__init__(); self.result = result
class AnimationResultUpdate(Message):
    def __init__(self, frames: List[Tuple[str, float]]) -> None: super().__init__(); self.frames = frames

class AsciiApp(App):
    TITLE = "TUI-ASCII-Art Generator"
    CSS_PATH = "style.css"
    
 
    animation_frames: List[Tuple[str, float]] = []
    current_frame_index: int = 0
    animation_timer: Optional[Timer] = None
   
    last_ascii_result: Optional[str] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="app-container"):
            with Horizontal(id="controls-container"):
                yield Button("Load File...", id="load-file-button", variant="primary")
                yield Checkbox("Remove Background", id="bg-checkbox")
                yield Button("Export to .txt", id="export-button", variant="success")
            
            yield Static("Width (Columns):", classes="label")
            yield Slider(min=40, max=200, value=120, id="width-slider")

            yield Static("Select a file to begin.", id="status-label")
            with ScrollableContainer(id="display-container"):
                yield Static(id="ascii_display")
            yield Button("Quit", id="quit-button", variant="error")
        yield Footer()
    
    def on_result_update(self, message: ResultUpdate) -> None:
        if self.animation_timer: self.animation_timer.stop()
            
        display = self.query_one("#ascii_display", Static)
        status_label = self.query_one("#status-label", Static)
        if message.result:
           
            self.last_ascii_result = message.result
            rich_text = Text.from_ansi(message.result)
            display.update(rich_text)
            status_label.update("Done!")
        else:
            self.last_ascii_result = None
            display.update("[bold red]Error! Check debug_log.txt[/bold red]")
            status_label.update("Failed.")
    
    def on_animation_result_update(self, message: AnimationResultUpdate) -> None:
        if self.animation_timer: self.animation_timer.stop()
        self.last_ascii_result = None 
        self.animation_frames = message.frames
        self.current_frame_index = 0
        if self.animation_frames:
            self.play_next_frame()
            self.query_one("#status-label", Static).update("Playing animation...")
        else:
            self.on_result_update(ResultUpdate(None))

    def play_next_frame(self) -> None:
        if not self.animation_frames: return
        if self.current_frame_index >= len(self.animation_frames): self.current_frame_index = 0
        frame_content, duration = self.animation_frames[self.current_frame_index]
        display = self.query_one("#ascii_display", Static)
        display.update(Text.from_ansi(frame_content))
        self.current_frame_index += 1
        self.animation_timer = self.set_timer(duration, self.play_next_frame)

    def _open_file_dialog(self) -> Optional[str]:
        root = tk.Tk(); root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select a Picture or GIF",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg"), ("Animation Files", "*.gif")]
        )
        root.destroy()
        return file_path if file_path else None

    @work(exclusive=True, thread=True)
    def process_file(self, file_path: str, remove_bg: bool, columns: int) -> None:
        try:
            self.post_message(StatusUpdate(f"Processing..."))
            is_gif = file_path.lower().endswith('.gif')
            if is_gif:
                if remove_bg: self.post_message(StatusUpdate("Note: BG removal is skipped for GIFs."))
                frames = convert_gif_to_ascii_frames(file_path, columns=columns)
                self.post_message(AnimationResultUpdate(frames))
            else:
                image_source = file_path
                temp_file_path = "temp_processed_image.png"
                if remove_bg:
                    self.post_message(StatusUpdate("Removing background..."))
                    processed_image = remove_background_from_image(file_path)
                    if processed_image:
                        processed_image.save(temp_file_path, 'PNG')
                        image_source = temp_file_path
                ascii_art_string = convert_image_to_ascii(image_source, columns=columns)
                self.post_message(ResultUpdate(ascii_art_string))
                if os.path.exists(temp_file_path): os.remove(temp_file_path)
        except Exception as e:
            logging.exception(f"CRITICAL ERROR in background thread: {e}")
            self.post_message(ResultUpdate(None))

    @on(Button.Pressed, "#load-file-button")
    def on_load_file(self) -> None:
        width_slider = self.query_one("#width-slider", Slider)
        columns = int(width_slider.value)
        
        should_remove_bg = self.query_one("#bg-checkbox", Checkbox).value
        file_path = self._open_file_dialog()
        if file_path:
            self.process_file(file_path, should_remove_bg, columns)

    @on(Button.Pressed, "#export-button")
    def on_export(self) -> None:
        if not self.last_ascii_result:
            self.query_one("#status-label", Static).update("[bold red]Nothing to export![/bold red]")
            return

        root = tk.Tk(); root.withdraw()
        file_path = filedialog.asksaveasfilename(
            title="Save ASCII Art",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )
        root.destroy()
        
        if file_path:
            try:
                clean_text = Text.from_ansi(self.last_ascii_result).plain
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clean_text)
                self.query_one("#status-label", Static).update(f"Successfully exported to {file_path.split('/')[-1]}")
            except Exception as e:
                self.query_one("#status-label", Static).update(f"[bold red]Export failed: {e}[/bold red]")

    @on(Button.Pressed, "#quit-button")
    def on_quit_button(self) -> None:
        self.exit()