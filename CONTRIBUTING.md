# Contributing to SpriteForge

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Bugs

If you find a bug:

1. Check if the bug has already been reported in [Issues](https://github.com/merhovon/SpriteForge/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Detailed description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Your environment (OS, Python version, etc.)

### Suggesting Features

Feature requests are welcome! Please:

1. Check existing feature requests in Issues
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach (optional)

### Pull Requests

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/merhovon/SpriteForge.git
   cd SpriteForge
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Make your changes**
   - Write clear, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

5. **Test your changes**
   ```bash
   # Run the application
   python -m spriteforge.app
   
   # Test with sample images
   python -m spriteforge.app test_image.png
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```
   
   Good commit messages:
   - "Add drag-and-drop file upload feature"
   - "Fix selection coordinates calculation bug"
   - "Update README with new installation instructions"

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of changes
   - Reference any related issues

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use descriptive variable and function names
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Type Hints

Use type hints for function parameters and return values:

```python
def process_image(image_path: str, selection: Tuple[int, int, int, int]) -> Optional[PILImage.Image]:
    ...
```

### Documentation

- Add docstrings to all functions and classes
- Use Google-style docstrings:

```python
def find_unique_colors(selection: Tuple[int, int, int, int]) -> List[List[int]]:
    """
    Find colors unique to the selected region.
    
    Args:
        selection: Tuple of (x, y, width, height)
    
    Returns:
        List of RGB color values unique to selection
    
    Raises:
        ValueError: If selection is invalid
    """
```

### Testing

Currently, the project uses manual testing. Automated tests are welcome contributions!

Planned test areas:
- Image processing functions
- Selection validation
- File I/O operations
- GUI components

### Project Structure

```
spriteforge/
├── __init__.py          # Package initialization
├── app.py               # Main Flet GUI application
└── image_processor.py   # Core image processing logic
```

When adding new features:
- Put UI code in `app.py`
- Put image processing in `image_processor.py`
- Create new modules for substantial features

## Feature Ideas

Looking for something to work on? Here are some ideas:

### Easy
- [ ] Add keyboard shortcuts
- [ ] Improve error messages
- [ ] Add file drag-and-drop support
- [ ] Recent files menu
- [ ] Better progress feedback

### Medium
- [ ] Interactive mouse-based selection
- [ ] Zoom and pan controls
- [ ] Preset selection sizes
- [ ] Batch processing mode
- [ ] Export settings persistence

### Advanced
- [ ] Sprite sheet generation
- [ ] Animation preview
- [ ] Plugin system
- [ ] Command-line interface
- [ ] Color histogram visualization

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions on GitHub
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Git commit history

Thank you for contributing! 🎉
