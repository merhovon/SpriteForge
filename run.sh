#!/bin/bash
# Unix/macOS shell script to run SpriteForge
# Usage: ./run.sh [optional_image_path]

echo "Starting SpriteForge..."
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "Error: Python $python_version found, but 3.10+ required"
    exit 1
fi

# Check if spriteforge is installed
if ! python3 -c "import spriteforge" &> /dev/null; then
    echo "SpriteForge not installed. Installing..."
    pip3 install -e .
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install SpriteForge"
        echo "Try running: pip3 install -r requirements.txt"
        exit 1
    fi
fi

# Run spriteforge
if [ -z "$1" ]; then
    python3 -m spriteforge.app
else
    python3 -m spriteforge.app "$1"
fi

if [ $? -ne 0 ]; then
    echo
    echo "Error occurred while running SpriteForge"
    exit 1
fi
