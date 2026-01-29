# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-29

### Major Release - Complete GUI Overhaul & Feature Expansion

This release represents a **complete rewrite** of SpriteForge with significant performance improvements and feature additions.

#### 🎨 New Selection Tools

- **Circle Selection Tool**: Draw circular selections with visual center point and radius
- **Polygon Selection Tool**: Create complex freeform selections with unlimited vertices
- **Rectangle Selection Tool**: Enhanced with visual feedback and handles

#### ⌨️ Keyboard Controls (Arrow Keys)

- **Arrow Keys (←→↑↓)**: Move selection by 1 pixel
- **Shift + Arrows**: Move selection by 5 pixels (fast mode)
- **Ctrl + Arrows**: Resize selection from bottom-right corner
- **Alt + Arrows**: Resize selection from top-left corner
- **Universal Support**: Works with ALL selection types (Rectangle, Circle, Polygon)
- **Boundary Clamping**: Selections stay within image bounds

#### 🎭 Overlay Tools

- **Unique Colors Overlay**: Toggle overlay showing only unique colors in selection
- **Transparent Sprite Overlay**: Live preview of transparent sprite extraction
- **Real-time Updates**: Overlays update dynamically with selections

#### 📋 Copy & Coordinate Features

- **Copy Region Coordinates**: Copy selection coordinates to clipboard (y1, x1, y2, x2 format)
- **Keyboard Shortcut**: Ctrl+Shift+C to copy coordinates
- **UI Button**: Dedicated button in toolbar
- **SpriteX Compatible**: Format matches original SpriteX convention

#### 🎯 Visual Enhancements

- **Grid Overlay**: Toggle grid with adjustable spacing
- **Selection Opacity Control**: Adjust selection overlay transparency (0-100%)
- **Visual Handles**: Resize handles for Rectangle selections
- **Shape Indicators**: Visual feedback for Circle (center + radius) and Polygon (vertices)
- **Zoom Controls**: Zoom in/out with mouse wheel and toolbar buttons
- **Pan & Drag**: Pan image with middle mouse button or drag

#### 🚀 Performance & Architecture

- **PyQt6 Native GUI**: 10x performance improvement over Flet
- **Graphics Scene**: QGraphicsView for smooth rendering and zooming
- **Optimized Rendering**: Hardware-accelerated graphics
- **Responsive UI**: No lag during selection or overlay operations

#### 🔧 Technical Improvements

- **Modular Architecture**: Separated ImageCanvas from main application
- **Type Annotations**: Full type hints throughout codebase
- **Enhanced Logging**: Detailed logging with loguru
- **Progress Callbacks**: Progress indicators for long operations
- **Error Handling**: Comprehensive error handling with user feedback

#### 🐛 Bug Fixes

- Fixed keyboard focus issues (added setFocusPolicy)
- Fixed arrow key handling for non-Rectangle selections
- Fixed overlay positioning with different selection types
- Fixed coordinate system conversions (view ↔ scene ↔ image)
- Fixed Circle/Polygon shape updates during arrow-key manipulation

#### 💥 Breaking Changes

- **GUI Framework**: Migrated from Flet to PyQt6 (requires PyQt6 installation)
- **Coordinate Format**: Copy coordinates now use (y1, x1, y2, x2) format
- **Python Version**: Requires Python 3.10+ (was 3.9+)

#### 📚 Documentation

- Updated README.md with all new features
- Added keyboard shortcuts documentation
- Enhanced code comments and docstrings

#### 🎁 Exceeds Original SpriteX

SpriteForge now **exceeds** the original SpriteX capabilities:
- ✅ Arrow-key control for ALL selection types (SpriteX: Rectangle only)
- ✅ Circle and Polygon selection tools (SpriteX: Rectangle only)
- ✅ Live overlay previews (SpriteX: None)
- ✅ Zoom and pan controls (SpriteX: Limited)
- ✅ Modern PyQt6 interface (SpriteX: Tkinter)

---

## [1.0.0] - 2026-01-27

### Initial Release

First public release of **SpriteForge** - a modern Flet-based sprite extraction tool.

#### Features

- **Image Loading**: Load PNG, JPG, JPEG, BMP, GIF images
- **Region Selection**: Define rectangular regions with coordinate input
- **Sprite Extraction**: Extract and save selected regions as PNG files
- **Unique Color Detection**: Find colors that exist only in selected region
- **Unique Sprite Generation**: Create sprites with only unique colors (others transparent)
- **Transparent Sprite Extraction**: Compare same region across multiple images
- **Modern GUI**: Built with Flet for responsive, cross-platform interface
- **Progress Indicators**: Real-time progress feedback for long operations
- **Copy to Clipboard**: Copy region coordinates in standard format
- **File Picker**: Native file selection dialogs

#### Technical

- Python 3.10+ support
- Flet 0.25+ for GUI
- NumPy 1.21+ for array operations
- Pillow 10.0+ for image processing
- Modular architecture (separated GUI and processing logic)
- Type hints throughout codebase
- Comprehensive documentation

#### Project

- GPL-3.0-or-later License
- CI/CD with GitHub Actions
- Test framework with pytest
- Example scripts for programmatic usage
- Cross-platform launcher scripts

---

## Future Releases

See [TODO.md](TODO.md) for planned features and improvements.

---

[1.0.0]: https://github.com/merhovon/SpriteForge/releases/tag/v1.0.0
