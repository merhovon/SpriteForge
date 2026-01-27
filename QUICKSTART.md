# Quick Start Guide

Get up and running with **SpriteForge** in 5 minutes!

## 📋 Prerequisites

- Python 3.10 or higher installed
- Basic familiarity with command line/terminal

Check your Python version:
```bash
python --version
# or
python3 --version
```

## 🚀 Installation (3 steps)

### Step 1: Get the Code

```bash
# Clone the repository
git clone https://github.com/merhovon/SpriteForge.git
cd SpriteForge
```

### Step 2: Install Dependencies

#### Option A: Quick Install
```bash
pip install -r requirements.txt
pip install -e .
```

#### Option B: With Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Step 3: Run!

```bash
spriteforge
```

Or with a quick start script:

**Windows:** Double-click `run.bat` or:
```
run.bat
```

**macOS/Linux:**
```bash
chmod +x run.sh
./run.sh
```

## 🎯 First Use

### 1. Load an Image

Two ways:
- **A)** Click "Load Image" button in the GUI
- **B)** Start with image: `spriteforge path/to/image.png`

### 2. Select a Region

- Click "Select Region" button
- Enter coordinates in the dialog:
  - **X**: Starting X coordinate (pixels from left)
  - **Y**: Starting Y coordinate (pixels from top)
  - **Width**: Region width in pixels
  - **Height**: Region height in pixels
- Click "Confirm"

**Example:** To select a 100×100 region starting at position (50, 50):
```
X: 50
Y: 50
Width: 100
Height: 100
```

### 3. Extract!

Choose an operation:

- **Extract Sprite** → Saves the selected region as PNG
- **Unique Colors** → Finds colors only in this region
- **Unique Sprite** → Creates sprite with only unique colors
- **Transparent Sprite** → Compares with other images (needs multiple PNGs)

Output files are saved in the same folder as your image with timestamps.

## 💡 Common Tasks

### Task: Extract a Character Sprite

```bash
1. Open your game screenshot
2. Select Region: x=100, y=150, width=64, height=64
3. Click "Extract Sprite"
4. Find output: sprite_YYYYMMDDHHMMSS.png
```

### Task: Find Unique UI Element

```bash
1. Open your UI screenshot
2. Select Region around the element
3. Click "Unique Colors"
4. Check how many colors are unique
5. Click "Unique Sprite" to see visualization
```

### Task: Extract Animation Frame

```bash
1. Place all animation frames in one folder
2. Open first frame: spriteforge frame_001.png
3. Select Region where sprite moves
4. Click "Transparent Sprite"
5. Gets sprite by comparing all frames
```

## 📝 Output Files

All files saved with timestamp in same directory:

| File | What It Is |
|------|------------|
| `sprite_20260127123045.png` | Exact copy of selected region |
| `unique_20260127123045.png` | 1-pixel tall strip of unique colors |
| `highlight_20260127123045.png` | Sprite with only unique colors visible (others transparent) |
| `extracted_20260127123045.png` | Transparent sprite from multiple image comparison |

## ⌨️ Tips & Tricks

### Finding Coordinates

1. Use any image viewer/editor to find pixel coordinates
2. Or use trial and error with small selections
3. The info panel shows selection details in real-time

### Copy Region Format

Click "Copy Region" to get coordinates in this format:
```
"REGION": (y, x, y+height, x+width)
```
Useful for scripts and saving presets.

### Batch Processing

For multiple files, use the programmatic approach:

```python
# See examples/example_usage.py
from spriteforge.image_processor import ImageProcessor

for image in images:
    processor = ImageProcessor(image)
    processor.save_sprite(selection)
```

## ❓ Troubleshooting

### "spriteforge: command not found"

Make sure you installed with `pip install -e .`

Or run directly:
```bash
python -m spriteforge.app
```

### "No module named 'flet'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "Please select a region first"

You need to:
1. Load an image first
2. Click "Select Region"
3. Enter coordinates and confirm

### Progress bar stuck

Some operations take time with large images. Wait for it to complete.

### No unique colors found

This means all colors in your selection also appear elsewhere in the image.
Try:
- Selecting a more specific region
- Using a different image

## 📚 Learn More

- **Full Documentation**: [README.md](README.md)
- **Installation Guide**: [INSTALL.md](INSTALL.md)
- **Examples**: [examples/](examples/)
- **API Usage**: [examples/example_usage.py](examples/example_usage.py)

## 🆘 Get Help

- **Issues**: [GitHub Issues](https://github.com/merhovon/SpriteForge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/merhovon/SpriteForge/discussions)

## ✨ Next Steps

1. Try extracting sprites from your images
2. Explore the [examples/](examples/) directory
3. Check out [MIGRATION.md](MIGRATION.md) if coming from old version
4. Consider [contributing](CONTRIBUTING.md)!

---

**Happy sprite extracting! 🎮🎨**
