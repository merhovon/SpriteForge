# SpriteForge

**Forge your sprites with precision** - A modern tool for extracting sprites from images, finding unique colors, and creating transparent sprites. Perfect for AI/ML projects and game development.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-GPL--3.0--or--later-green)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52)

## 🎯 Features

- **Region Selection**: Select rectangular regions from images for extraction
- **Sprite Extraction**: Extract and save selected regions as separate sprite images
- **Unique Color Detection**: Find colors that exist only in the selected region (not in the rest of the image)
- **Unique Sprite Generation**: Create sprites showing only unique colors (others transparent)
- **Transparent Sprite Extraction**: Compare the same region across multiple images to extract only changing elements
- **Native GUI**: Built with PyQt6 for high-performance, native desktop interface
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Installation

### From PyPI (when published)

```bash
pip install spriteforge
```

### From Source

```bash
git clone https://github.com/merhovon/SpriteForge.git
cd SpriteForge
pip install -e .
```

### Requirements

- Python 3.10 or higher
- numpy >= 1.21.0
- PyQt6 >= 6.6.0
- pillow >= 10.0.0
- loguru >= 0.7.0

Install dependencies:

```bash
pip install -r requirements.txt
```

## 📖 Usage

### Launch the Application

```bash
spriteforge
```

Or with an image file:

```bash
spriteforge path/to/image.png
```

### Basic Workflow

1. **Load Image**: Click "Load Image" button or pass file path as argument
2. **Select Region**: Click "Select Region" and define coordinates (X, Y, Width, Height)
3. **Extract**: Choose from various extraction operations:
   - **Extract Sprite**: Save the selected region as a PNG
   - **Unique Colors**: Extract colors unique to the selection
   - **Unique Sprite**: Create transparent sprite with only unique colors
   - **Transparent Sprite**: Compare across multiple images (requires multiple images in same folder)

### Features Explained

#### Region Selection

Select a rectangular area from your image by specifying X, Y coordinates and dimensions. The selection info panel shows current coordinates and size.

#### Sprite Extraction

Saves the selected region as a separate PNG file with timestamp in the same directory as the source image.

#### Unique Color Detection

Analyzes the selected region and identifies colors that appear only in that region but nowhere else in the image. Useful for:
- Finding distinct objects in screenshots
- Identifying UI elements by color
- Training data preparation for ML models

#### Transparent Sprite Extraction

Compares the same region across all PNG images in the directory. Pixels that differ between images become transparent, while static pixels remain opaque. Perfect for:
- Extracting animated sprites from video frames
- Removing static backgrounds
- Isolating moving objects

## 🎮 Use Cases

### AI/ML Training Data

Create training datasets by extracting consistent regions from multiple images:

```bash
# Extract sprites from frame sequences
spriteforge frame_001.png
# Select region, then use "Extract Sprite" for each frame
```

### Game Development

Extract sprites and sprite sheets from game screenshots or animations.

### Image Analysis

Identify and isolate unique visual elements for computer vision applications.

## 🛠️ Development

### Project Structure

```
spriteforge/
├── spriteforge/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Main Flet application
│   └── image_processor.py   # Core image processing logic
├── requirements.txt         # Dependencies
├── setup.py                 # Setup configuration
├── pyproject.toml          # Modern Python project config
├── README.md               # This file
├── LICENSE                 # GPL-3.0-or-later License
└── CHANGELOG.md            # Version history
```

### Running from Source

```bash
python -m spriteforge.app
```

### Building Distribution

```bash
python -m build
```

## 📝 Output Files

All extracted images are saved in the same directory as the source image with timestamps:

- `sprite_YYYYMMDDHHMMSS.png` - Extracted sprite
- `unique_YYYYMMDDHHMMSS.png` - Unique colors (1D strip)
- `highlight_YYYYMMDDHHMMSS.png` - Unique sprite with transparency
- `extracted_YYYYMMDDHHMMSS.png` - Transparent sprite from multiple images

## 🎨 GUI Overview

The application features a clean, modern interface:

- **Left Panel**: Image viewer with selection overlay
- **Right Panel**: Controls and tools
  - Load Image
  - Selection Tools
  - Extract Operations
  - Region Info Display
  - Progress Indicator

## 📜 License

This project is licensed under the **GNU General Public License v3.0 or later** (GPL-3.0-or-later).

This means:
- ✅ You can use, modify, and distribute this software
- ✅ You must share your modifications under the same GPL license
- ✅ You must include the original copyright and license notices
- ✅ Changes must be documented
- ❌ You cannot use it in closed-source/proprietary software

See the [LICENSE](LICENSE) file for full details, or visit https://www.gnu.org/licenses/gpl-3.0.html

## 💡 Inspiration

This tool was inspired by the concept of sprite extraction. SpriteForge is built from the ground up using modern technologies (PyQt6, Python 3.10+) with a focus on performance and user experience. Migrated from Flet to PyQt6 for 10x performance improvement.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 🔮 Future Enhancements

- [ ] Interactive region selection with mouse drag
- [ ] Zoom and pan controls for image viewer
- [ ] Batch processing mode
- [ ] Export sprite sheets
- [ ] Undo/Redo functionality
- [ ] Recent files menu

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/merhovon/SpriteForge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/merhovon/SpriteForge/discussions)

---

Made with ❤️ using PyQt6 and Python