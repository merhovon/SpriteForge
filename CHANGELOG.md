# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
