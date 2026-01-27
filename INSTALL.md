# Installation and Setup Guide

## Prerequisites

- Python 3.10 or higher installed on your system
- pip (Python package installer)

## Installation Options

### Option 1: Quick Install (PyPI)

Once published on PyPI, you can install with:

```bash
pip install spriteforge
```

### Option 2: Install from Source

#### Clone the Repository

```bash
git clone https://github.com/merhovon/SpriteForge.git
cd SpriteForge
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Install the Package

For production use:
```bash
pip install .
```

For development (editable mode):
```bash
pip install -e .
```

### Option 3: Virtual Environment (Recommended)

Using a virtual environment keeps your dependencies isolated:

#### Windows

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

#### macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Running the Application

After installation, you can run:

```bash
spriteforge
```

Or with a specific image:

```bash
spriteforge path/to/your/image.png
```

## Verifying Installation

Test if the installation was successful:

```bash
python -c "import spriteforge; print(spriteforge.__version__)"
```

This should print the version number (e.g., `1.0.0`).

## Troubleshooting

### Python Version Issues

Make sure you're using Python 3.10 or higher:

```bash
python --version
```

If you have multiple Python versions, use:

```bash
python3.10 -m pip install -r requirements.txt
```

### Flet Installation Issues

If Flet fails to install, try:

```bash
pip install --upgrade pip
pip install flet
```

### Permission Errors

On macOS/Linux, if you get permission errors:

```bash
pip install --user spriteforge
```

Or use a virtual environment (recommended).

### Import Errors

If you get import errors when running, make sure you've activated your virtual environment:

- Windows: `.\venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

## Updating

To update to the latest version:

```bash
pip install --upgrade spriteforge
```

Or if installed from source:

```bash
cd spriteforge
git pull
pip install --upgrade -e .
```

## Uninstalling

```bash
pip uninstall spriteforge
```

## Development Setup

For contributing to the project:

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/spriteforge.git
cd spriteforge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install in development mode with dev dependencies
pip install -e .

# Run from source
python -m spriteforge.app
```

## Platform-Specific Notes

### Windows

- Make sure Python is added to your PATH during installation
- Use PowerShell or Command Prompt
- Flet works best with Windows 10 or later

### macOS

- You may need to install Python from python.org if using the system Python
- Flet requires macOS 10.13 or later
- Grant accessibility permissions if requested

### Linux

- Install Python development headers: `sudo apt-get install python3-dev` (Debian/Ubuntu)
- Some distributions may require additional dependencies for GUI applications

## Getting Help

If you encounter issues:

1. Check the [README.md](README.md) for common solutions
2. Search existing [GitHub Issues](https://github.com/merhovon/SpriteForge/issues)
3. Create a new issue with:
   - Your Python version: `python --version`
   - Your OS and version
   - Complete error message
   - Steps to reproduce

## Next Steps

After successful installation, see the [README.md](README.md) for usage instructions and examples.
