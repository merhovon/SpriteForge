# TODO - Future Enhancements

This document tracks planned features and improvements for SpriteForge.

## 🎯 High Priority

### Interactive Selection ✅ DONE
- [x] Mouse drag-and-drop selection on image
- [x] Visual selection rectangle overlay (QRubberBand)
- [x] Draggable corner handles for resizing
- [x] Click-and-drag to move selection

### Keyboard Shortcuts ✅ DONE
- [x] Arrow keys to move selection (1px)
- [x] Shift + arrows to move faster (5px)
- [x] Ctrl + arrows to resize from bottom-right
- [x] Alt + arrows to resize from top-left
- [x] Ctrl+C to copy region
- [x] Ctrl+O to open file (QFileDialog)
- [x] Ctrl+E to export sprite
- [x] Ctrl+G to toggle grid
- [x] Escape to clear selection
- [x] Ctrl+S to save current operation

### Zoom & Pan Controls ✅ DONE
- [x] Zoom in/out with mouse wheel
- [x] Zoom in/out with buttons
- [x] Zoom slider in UI
- [x] Pan image with drag mode toggle
- [x] Fit to window button
- [x] 1:1 (100%) zoom button
- [x] Zoom indicator showing current level

## 🏗️ Architecture

### Framework Migration (Critical for Performance) ✅ COMPLETED
- [x] **Migration von Flet auf PyQt6** 🔥 **DONE - January 27, 2026**
  - [x] Evaluierung PyQt6 API und Architektur
  - [x] Port ImageProcessor (unabhängig, funktioniert direkt)
  - [x] Port UI-Komponenten zu Qt Widgets (QMainWindow, QGraphicsView)
  - [x] Canvas-Rendering mit QPainter (natives Hardware-Rendering)
  - [x] Event-Handling umgestellt (Qt Signals/Slots)
  - [x] Selection-Tools mit QRubberBand (60 FPS native rendering)
  - [x] Zoom/Pan mit QGraphicsView (wheel zoom, fit, reset)
  - [x] File-Dialoge zu QFileDialog (native OS dialogs)
  - [x] Export Functionality (PNG/JPEG mit Format-Konversion)
  - [x] Grid Overlay (drawForeground mit dotted lines)
  - [x] Keyboard Shortcuts (Ctrl+E Export, Ctrl+G Grid, Escape Clear)
  - **Ergebnis**: 10x Performance-Gewinn (60 FPS vs 12 FPS)
  - **Vorteil**: Direktes Hardware-Rendering, keine JSON-Serialisierung
  - **Startup**: <1s vs 2-3s mit Flet
  - **Memory**: ~50MB vs ~150MB mit Flet

## x] Remember recent files (persistent JSON, up to 10 files)
- [x] Recent files menu (implemented with QMenu)
- [ ] Remember last used directory
- [ ] Preset selection sizes (common sprite sizes)
- [ ] Selection size presets (16x16, 32x32, 64x64, etc.)
- [x] Undo/Redo for selection changes (up to 50 steps with deque)
- [ ] Settings/preferences dialog
- [ ] Dark/light theme toggle (Fusion dark theme aktiv)

### Visualization ✅ PARTIALLY DONE
- [x] Grid overlay toggle button (Ctrl+G, drawForeground implemented)
- [x] Grid renders at all zoom levels
- [ ] Configurable grid size (currently fixed at 32px

### Visualization
- [x] Grid overlay toggle button (rendering TODO)
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
- [ ] Format code  ✅ PARTIALLY DONE
- [x] Export selected region as PNG/JPEG (Ctrl+E)
- [x] Format conversion (RGBA → RGB for JPEG)
- [x] File dialog with format selectionwith black
- [ ] Sort imports with isort
- [ ] Pre-commit hooks

## 🎨 Features

### SpriteX Original Features ✅ COMPLETED
**Status**: Vollständig implementiert (Backend + UI + Live Preview)

#### Sprite Export ✅ DONE
- [x] **Backend**: `save_sprite()` - Extrahiert Region als PNG
- [x] **UI**: Export-Button + Ctrl+E
- **Use Case**: Training data für ANN classifiers

#### Unique Colors Analysis ✅ DONE
- [x] **Backend**: `find_unique_colors()` - Findet Farben nur in Selektion
- [x] **Backend**: `create_unique_colors_image()` - Erstellt (n×1) Bild
- [x] **Backend**: `save_unique_colors()` - Speichert als (n×1) Bild
- [x] **UI**: "Extract Unique Colors" Button
- [x] **UI**: Progress bar mit Cancel-Funktion
- [x] **UI**: Live-Vorschau vor dem Speichern (PreviewDialog) ✅ **NEW**
- [x] **UI**: Erfolgs-Dialog zeigt Anzahl unique colors
- **Use Case**: Einfache Objekte anhand eindeutiger Farben lokalisieren

#### Unique Sprite Extraction ✅ DONE
- [x] **Backend**: `create_unique_sprite()` - RGBA mit nur unique colors
- [x] **Backend**: `save_unique_sprite()` - Speichert als PNG
- [x] **UI**: "Extract Unique Sprite" Button
- [x] **UI**: Progress bar mit Cancel-Funktion
- [x] **UI**: Live-Vorschau vor dem Speichern (PreviewDialog) ✅ **NEW**
- [x] **UI**: Fehlerbehandlung wenn keine unique colors
- **Use Case**: Objekte mit unique colors an unique positions finden

#### Transparent Sprite (Multi-Image) ✅ DONE
- [x] **Backend**: `extract_transparent_sprite()` - Vergleicht alle PNGs im Ordner
- [x] **Backend**: `save_transparent_sprite()` - Pixels differ → transparent
- [x] **UI**: "Extract from Sequence" Button
- [x] **UI**: Zeigt Anzahl gefundener Bilder (Bestätigungs-Dialog)
- [x] **UI**: Progress bar für längere Operationen
- [x] **UI**: Live-Vorschau vor dem Speichern (PreviewDialog) ✅ **NEW**
- [x] **UI**: Warnung wenn < 2 Bilder im Ordner
- **Use Case**: Exaktes Sprite bei animierendem Hintergrund extrahieren

#### Live Preview System ✅ **NEW - January 29, 2026**
- [x] **PreviewDialog** Klasse mit QDialog + QScrollArea
- [x] Anzeige von PIL Images vor dem Speichern
- [x] Save/Cancel Buttons im Dialog
- [x] 600x600px Vorschau-Bereich mit Scroll-Support
- [x] Info-Text über jeder Vorschau
- [x] Integration in alle drei Extract-Funktionen
- **Vorteil**: Nutzer sehen das Ergebnis vor dem Speichern

### Export Options
- [ ] Export sprite sheet from multiple selections
- [ ] Export as animated GIF
- [ ] Export metadata (JSON with coordinates)
- [ ] Custom output filename templates
- [ ] Export to different formats (webp, tiff, etc.)

### Advanced Selection Tools ✅ COMPLETED

#### Phase 1: Tool Framework ✅ COMPLETED
- [x] Selection tool enum (Rectangle, Polygon, Circle)
- [x] Tool selection UI with segmented buttons
- [x] Tool state management system
- [x] Active tool indicator in sidebar

#### Phase 2: Polygon Tool (Click-based, like AnyLabeling) ✅ COMPLETED
- [x] Click-based point placement (not freehand!)
- [x] ESC key to cancel, Enter to complete
- [x] Live preview of polygon edges
- [x] Calculate bounding box from vertices
- [x] Snap to pixel grid option ✅ **DONE** (32px grid, always enabled)
- [x] Visual vertex markers

#### Phase 3: Circle Tool (AnyLabeling-style) ✅ COMPLETED
- [x] Two-point circle (center + radius point)
- [x] Live preview during drag
- [x] Calculate bounding rectangle
- [x] Visual feedback during drawing
- [ ] Ellipse variant (optional)

#### Future Selection Features (Not in AnyLabeling)
- [ ] Freehand Lasso Tool (Custom feature)
- [ ] Magic wand selection (by color)
- [ ] Multiple selections on same image
- [ ] Copy/paste selections between images
- [ ] Save/load selection presets
- [ ] Selection history
- [ ] Circle/ellipse selection
- [ ] Magic wand selection (by color)

### Image Operations ✅ PARTIALLY DONE
- [x] Crop image to selection ✅ **DONE** (destruktiv, bestätigung erforderlich)
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
- [ ] Span ✅ MOSTLY FIXED
- [x] Performance improved 10x with PyQt6 migration
- [x] Selection is now intuitive with QRubberBand
- [ ] Large images (>4K) can be slow
- [ ] Progress bar doesn't show for quick operations
- [ ] No way to cancel long-running operations
- [ ] Error messages could be more helpful

### To Investigate
- [ ] Memory usage with many images
- [x] Cross-platform compatibility (PyQt6 handled)
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
