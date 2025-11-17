import logging
logging.basicConfig(
    filename='debug_log.txt',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from textual.app import App, ComposeResult
from textual.widgets import Button, Checkbox, Static, Header, Footer
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual import on
from rich.text import Text
from typing import Optional
import tkinter as tk
from tkinter import filedialog
import threading
from textual.message import Message
import os 

from .converter import convert_image_to_ascii
from .background import remove_background_from_image

class StatusUpdate(Message):
    def __init__(self, text: str) -> None: super().__init__(); self.text = text
class ResultUpdate(Message):
    def __init__(self, result: Optional[str]) -> None: super().__init__(); self.result = result

class AsciiApp(App):
    TITLE = "TUI-ASCII-Art Generator"
    CSS_PATH = "style.css"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="app-container"):
            with Horizontal(id="controls-container"):
                yield Button("Učitaj datoteku...", id="load-file-button", variant="primary")
                yield Checkbox("Ukloni pozadinu", id="bg-checkbox")
            yield Static("Odaberite datoteku za početak.", id="status-label")
            with ScrollableContainer(id="display-container"):
                yield Static(id="ascii_display")
            yield Button("Izlaz", id="quit-button", variant="error")
        yield Footer()
    
    def on_status_update(self, message: StatusUpdate) -> None:
        self.query_one("#status-label", Static).update(message.text)
    
    def on_result_update(self, message: ResultUpdate) -> None:
        display = self.query_one("#ascii_display", Static)
        status_label = self.query_one("#status-label", Static)
        if message.result:
            rich_text = Text.from_ansi(message.result)
            display.update(rich_text)
            status_label.update("Završeno!")
        else:
            display.update("[bold red]Greška! Provjerite debug_log.txt[/bold red]")
            status_label.update("Neuspješno.")

    def _open_file_dialog(self) -> Optional[str]:
        root = tk.Tk(); root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Odaberite sliku", filetypes=[("Slike", "*.png *.jpg *.jpeg")]
        )
        root.destroy()
        return file_path if file_path else None

    @on(Button.Pressed, "#load-file-button")
    def on_load_file(self) -> None:
        should_remove_bg_value = self.query_one("#bg-checkbox", Checkbox).value
        def background_task(remove_bg: bool):
            try:
                file_path = self._open_file_dialog()
                if not file_path: return
                
                self.post_message(StatusUpdate(f"Obrađujem..."))
                
                image_source = file_path
                temp_file_path = "temp_processed_image.png"

                if remove_bg:
                    self.post_message(StatusUpdate("Uklanjam pozadinu..."))
                    processed_image = remove_background_from_image(file_path)
                    if processed_image:
                        
                        processed_image.save(temp_file_path, 'PNG')
                        image_source = temp_file_path 
                
                self.post_message(StatusUpdate("Pretvaram u ASCII art..."))
                ascii_art_string = convert_image_to_ascii(image_source)
                
                self.post_message(ResultUpdate(ascii_art_string))

                
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            except Exception as e:
                logging.exception(f"KATASTROFALNA GREŠKA U POZADINSKOM THREADU: {e}")
                self.post_message(ResultUpdate(None))

        thread = threading.Thread(target=background_task, args=(should_remove_bg_value,))
        thread.start()

    @on(Button.Pressed, "#quit-button")
    def on_quit_button(self) -> None: self.exit()