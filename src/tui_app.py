from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import ScrollableContainer
from rich.text import Text

from .converter import convert_image_to_ascii

import os
from PIL import Image, ImageDraw


class AsciiApp(App):
    """Textual aplikacija za prikazivanje ASCII arta."""

    TITLE = "TUI-ASCII-Art Generator"
    SUB_TITLE = "Pretvorite slike u umjetnost!"

    def compose(self) -> ComposeResult:
        """Definiše izgled (layout) aplikacije."""
        yield Header()
        yield ScrollableContainer(Static(id="ascii_display"))
        yield Footer()

    def on_mount(self) -> None:
    
        display = self.query_one("#ascii_display", Static)

       
        test_image_path = "test_image.png"
        if not os.path.exists(test_image_path):
            img = Image.new('RGB', (200, 150), color = 'red')
            d = ImageDraw.Draw(img)
            d.rectangle([40, 30, 160, 120], fill='yellow', outline='blue', width=5)
            d.text((55, 65), "ASCII Test!", fill='black')
            img.save(test_image_path)
        

        ascii_art_string = convert_image_to_ascii(test_image_path)

        rich_text = Text.from_ansi(ascii_art_string)

        display.update(rich_text)