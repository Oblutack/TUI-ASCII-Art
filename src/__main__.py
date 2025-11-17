from .tui_app import AsciiApp

def main():
    """Pokreće Textual aplikaciju."""
    app = AsciiApp()
    app.run()

if __name__ == "__main__":
    main()