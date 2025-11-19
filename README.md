# ASCII Art Generator

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**A powerful desktop application for converting images and GIFs into high-quality ASCII art**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation)

</div>

---

## Overview

ASCII Art Generator is a modern desktop application that transforms images and animated GIFs into ASCII art. Built with PyQt6 and advanced image processing algorithms, it provides extensive customization options and real-time conversion capabilities.

### Key Capabilities

- **High-Performance Conversion** - Multi-threaded processing for images and GIF animations
- **Advanced Customization** - Full control over character sets, colors, and image adjustments
- **Floating Widgets** - Display ASCII art on desktop with customizable themes and transparency
- **Multiple Export Formats** - TXT, HTML, and folder-based exports
- **Built-in History** - Automatic tracking and gallery view of all conversions
- **Batch Operations** - Process multiple files efficiently

---

## Features

### Core Functionality

**Image Processing**
- Support for PNG, JPG, JPEG, BMP, and GIF formats
- Adjustable width (40-300 characters)
- Brightness control (-100 to +100)
- Contrast adjustment (25% to 200%)
- Color inversion
- Background removal (powered by rembg)
- Aspect ratio presets (Original, Square, Widescreen, Portrait)

**Character Sets**
- Detailed (high-quality default)
- Simple ASCII
- Unicode blocks
- Binary (0/1)
- Dots
- Minimal (2-character)

**GIF Animation**
- Frame-by-frame conversion
- Playback controls with speed adjustment (0.25x - 4.0x)
- Loop mode
- Real-time frame counter

### Floating Widgets

**Display Features**
- Multiple simultaneous widgets
- Six color themes (Grape, Matrix, Amber, Cyan, Pink, Monochrome)
- Font size control (6pt - 16pt)
- Opacity adjustment (30% - 100%)
- Transparent mode with UI toggle
- Always-on-top positioning
- Drag and resize capabilities

**Widget Themes**
- **Grape** - Purple gradient (default)
- **Matrix** - Green on black terminal style
- **Amber** - Retro orange terminal
- **Cyan** - Modern blue aesthetic
- **Pink** - Neon pink theme
- **Monochrome** - High-contrast black and white

### Export Options

**Format Types**
- **Single Text File** - All frames with metadata and separators
- **Interactive HTML** - JavaScript-powered player with full controls
- **Frame Folder** - Individual text files with animation info

### User Interface

- Drag and drop file loading
- Comprehensive keyboard shortcuts
- Auto-save preferences
- History gallery with preview
- Real-time conversion feedback
- Responsive layout

---

## Installation

### Requirements

- Python 3.10 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/TUI-ASCII-Art.git
cd TUI-ASCII-Art

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main_window.py
```

### Dependencies

Core libraries:
```
ascii_magic==2.7.2
Pillow==12.0.0
PyQt6==6.10.0
rembg==2.0.67
opencv-python==4.11.0.86
numpy==1.26.4
onnxruntime==1.19.2
rich==14.2.0
```

---

## Usage

### Basic Workflow

1. **Load File**
   - Click LOAD button or press `Ctrl+O`
   - Drag and drop supported

2. **Adjust Settings**
   - Width: Character count for ASCII art
   - Style: Select character set
   - Adjustments: Brightness, contrast, inversion
   - Aspect Ratio: Choose display format

3. **Convert**
   - Automatic processing with progress display
   - Real-time preview

4. **Export or Display**
   - `Ctrl+S` - Save to file
   - `Ctrl+W` - Open in floating widget
   - `Ctrl+H` - View in history gallery

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save/Export |
| `Ctrl+W` | New widget |
| `Ctrl+H` | History gallery |
| `Ctrl+Q` | Quit |
| `Space` | Play/Pause (GIF mode) |

### Advanced Options

**Character Set Selection**
- Different sets produce varied aesthetics
- Blocks for retro pixel art
- Binary for Matrix-style effects
- Minimal for high contrast

**Image Adjustments**
- Brightness: Enhance light/dark areas
- Contrast: Control sharpness
- Invert: Create negative effect
- Background Removal: Isolate subjects

**Widget Management**
- Multiple widgets can run simultaneously
- Each widget maintains independent settings
- Click ASCII art to toggle UI visibility
- Drag corners to resize

---

## Configuration

### Settings Storage

Settings automatically saved to:
- Windows: `%USERPROFILE%\.ascii_generator_settings.json`
- Linux/macOS: `~/.ascii_generator_settings.json`

### Auto-saved Preferences

- Window geometry
- Conversion parameters
- Widget customization
- Theme selection
- Font preferences

### Manual Configuration

Edit settings file for advanced options:

```json
{
  "width": 120,
  "character_set": "detailed",
  "brightness": 0,
  "contrast": 100,
  "widget_font_size": 9,
  "widget_color_theme": "grape",
  "aspect_ratio": "original"
}
```

---

## Documentation

### Export Format Details

**Single Text File**
- Structured with frame markers
- Includes timing metadata
- Best for text editor viewing

**Interactive HTML**
- Self-contained player
- No server required
- Full playback controls
- Responsive design

**Frame Folder**
- Separate file per frame
- Metadata file included
- Ideal for frame-by-frame editing

### Performance Optimization

**For Large Files**
- Reduce character width (< 120)
- Close unnecessary widgets
- Process in smaller batches

**For GIF Animations**
- Limit frame count if possible
- Use lower character widths
- Monitor memory usage

---

## Troubleshooting

### Common Issues

**Application Startup Failure**
```bash
# Verify Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**GIF Conversion Errors**
- Verify file size (< 10MB recommended)
- Reduce width setting
- Check available system memory

**Background Removal Issues**
- Ensure internet connection (first run)
- Verify disk space (> 1GB)
- Try without background removal

**Widget Display Problems**
- Check screen boundaries
- Try default theme
- Restart application

---

## Contributing

### Guidelines

Contributions welcome via pull requests. Please ensure:
- Code follows project style
- Tests pass for new features
- Documentation updated
- Clear commit messages

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/TUI-ASCII-Art.git

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Check code style
flake8 src/
```

### Reporting Issues

Include in bug reports:
- Steps to reproduce
- Expected vs actual behavior
- System information
- Screenshots if applicable

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2024 ASCII Art Generator Contributors

---

## Acknowledgments

**Core Technologies**
- PyQt6 - GUI framework
- ascii-magic - ASCII conversion engine
- Pillow - Image processing
- rembg - Background removal

**Inspiration**
- Classic ASCII art tools
- Modern TUI applications
- Open source community

---

<div align="center">

**[Documentation](https://github.com/yourusername/TUI-ASCII-Art/wiki)** • **[Issues](https://github.com/yourusername/TUI-ASCII-Art/issues)** • **[Discussions](https://github.com/yourusername/TUI-ASCII-Art/discussions)**

![GitHub stars](https://img.shields.io/github/stars/yourusername/TUI-ASCII-Art?style=social)

</div>
