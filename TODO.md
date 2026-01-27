# TODO - Future Enhancements

This document tracks planned features and improvements for SpriteForge.

## 🎯 High Priority

### Interactive Selection
- [ ] Mouse drag-and-drop selection on image
- [ ] Visual selection rectangle overlay
- [ ] Draggable corner handles for resizing
- [ ] Click-and-drag to move selection

### Keyboard Shortcuts
- [ ] Arrow keys to move selection (1px)
- [ ] Shift + arrows to move faster (5px)
- [ ] Ctrl + arrows to resize from bottom-right
- [ ] Alt + arrows to resize from top-left
- [ ] Ctrl+C to copy region
- [ ] Ctrl+O to open file
- [ ] Ctrl+S to save current operation

### Zoom & Pan Controls
- [ ] Zoom in/out with mouse wheel
- [ ] Zoom slider in UI
- [ ] Pan image with middle-mouse drag
- [ ] Fit to window button
- [ ] 1:1 (100%) zoom button
- [ ] Zoom indicator showing current level

## 📊 Medium Priority

### User Experience
- [ ] Remember last used directory
- [ ] Recent files menu
- [ ] Preset selection sizes (common sprite sizes)
- [ ] Selection size presets (16x16, 32x32, 64x64, etc.)
- [ ] Undo/Redo for selection changes
- [ ] Settings/preferences dialog
- [ ] Dark/light theme toggle

### Visualization
- [ ] Grid overlay for pixel-perfect editing
- [ ] Pixel grid appears at high zoom levels
- [ ] Real-time preview overlays
- [ ] Highlight unique colors in preview
- [ ] Color histogram display
- [ ] Minimap for large images

### Batch Processing
- [ ] Process multiple images with same selection
- [ ] Batch extract sprites from image sequence
- [ ] Progress bar for batch operations
- [ ] Export batch settings as JSON/YAML
- [ ] Command-line batch mode

## 🔧 Technical Improvements

### Testing
- [ ] Unit tests for ImageProcessor methods
- [ ] Integration tests for GUI operations
- [ ] Test fixtures with sample images
- [ ] CI/CD runs tests automatically
- [ ] Code coverage reporting
- [ ] Performance benchmarks

### Performance
- [ ] Optimize unique color detection for large images
- [ ] Multi-threading for long operations
- [ ] Image caching for faster switching
- [ ] Lazy loading for large images
- [ ] Progress callbacks with ETA
- [ ] Memory optimization for batch processing

### Code Quality
- [ ] Type hints everywhere
- [ ] Docstrings for all public methods
- [ ] Linting with flake8/pylint
- [ ] Format code with black
- [ ] Sort imports with isort
- [ ] Pre-commit hooks

## 🎨 Features

### Export Options
- [ ] Export sprite sheet from multiple selections
- [ ] Export as animated GIF
- [ ] Export metadata (JSON with coordinates)
- [ ] Custom output filename templates
- [ ] Export to different formats (webp, tiff, etc.)

### Advanced Selection
- [ ] Multiple selections on same image
- [ ] Copy/paste selections between images
- [ ] Save/load selection presets
- [ ] Selection history
- [ ] Non-rectangular selections (polygon, circle)
- [ ] Magic wand selection (by color)

### Image Operations
- [ ] Crop image to selection
- [ ] Rotate image
- [ ] Flip horizontal/vertical
- [ ] Adjust brightness/contrast
- [ ] Apply filters (blur, sharpen, etc.)

### Integration
- [ ] Plugin system for custom operations
- [ ] Python API documentation
- [ ] REST API server mode (optional)
- [ ] Watch folder for automatic processing
- [ ] Integration with sprite packing tools

## 📱 Platform-Specific

### Windows
- [ ] Installer (MSI or EXE)
- [ ] Context menu integration (right-click image)
- [ ] File association (.png opens in SpriteForge)

### macOS
- [ ] .app bundle
- [ ] DMG installer
- [ ] Touch Bar support

### Linux
- [ ] .deb package
- [ ] .rpm package
- [ ] AppImage
- [ ] Flatpak

## 📚 Documentation

### User Documentation
- [ ] Video tutorials (YouTube)
- [ ] Interactive tutorial in app
- [ ] FAQ page
- [ ] Troubleshooting guide
- [ ] Use case examples
- [ ] Tips and tricks page

### Developer Documentation
- [ ] API reference (auto-generated from docstrings)
- [ ] Architecture documentation
- [ ] Plugin development guide
- [ ] Contributing guide expansion
- [ ] Code walkthrough tutorial

### Website
- [ ] GitHub Pages site
- [ ] Online demo (if possible)
- [ ] Gallery of example outputs
- [ ] Blog posts about features

## 🌟 Nice to Have

### Fun Features
- [ ] Animation preview for sprite sequences
- [ ] Sprite sheet generator
- [ ] Sprite comparison tool
- [ ] Color palette extractor
- [ ] Generate sprite from text/icon
- [ ] AI-powered background removal
- [ ] Style transfer for sprites

### Accessibility
- [ ] Screen reader support
- [ ] High contrast mode
- [ ] Keyboard-only navigation
- [ ] Adjustable UI scaling
- [ ] Configurable keyboard shortcuts

### Localization
- [ ] Multi-language support
- [ ] Translation system
- [ ] German translation
- [ ] Spanish translation
- [ ] French translation
- [ ] Japanese translation (for game dev)

## 🐛 Known Issues

### To Fix
- [ ] Large images (>4K) can be slow
- [ ] Progress bar doesn't show for quick operations
- [ ] Selection dialog could be more intuitive
- [ ] No way to cancel long-running operations
- [ ] Error messages could be more helpful

### To Investigate
- [ ] Memory usage with many images
- [ ] Flet compatibility with different Python versions
- [ ] Cross-platform file path handling
- [ ] Unicode filename support

## 📝 Documentation Updates Needed

- [ ] Update README with new features as added
- [ ] Add screenshots to documentation
- [ ] Record video tutorials
- [ ] Update MIGRATION.md with new features
- [ ] Update CHANGELOG.md for each release

## 🔐 Security

- [ ] Security audit of dependencies
- [ ] Input validation for all user inputs
- [ ] Safe file handling (prevent path traversal)
- [ ] Dependency vulnerability scanning
- [ ] Regular security updates

---

## How to Contribute

Pick any item from this list and:

1. Comment on related issue (or create one)
2. Fork the repository
3. Create a feature branch
4. Implement the feature
5. Add tests
6. Update documentation
7. Submit pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Priority Labels

- 🔥 **Critical** - Needed for core functionality
- ⭐ **High** - Highly requested or important
- 📊 **Medium** - Nice to have, improves UX
- 💡 **Low** - Future enhancement
- 🎨 **Polish** - Visual/UX improvements

---

Last updated: January 27, 2026
