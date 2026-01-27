# Examples

This directory contains example scripts and usage patterns for SpriteForge.

## Files

### example_usage.py

Demonstrates programmatic usage of the ImageProcessor class:

```python
from spriteforge.image_processor import ImageProcessor

# Load image
processor = ImageProcessor("image.png")

# Define selection
selection = (x, y, width, height)

# Extract sprites
processor.save_sprite(selection)
processor.save_unique_colors(selection)
processor.save_unique_sprite(selection)
processor.save_transparent_sprite(selection)
```

## Running Examples

### From Command Line

```bash
# Make sure SpriteForge is installed
pip install -e .

# Run the example (edit the image path first!)
python examples/example_usage.py
```

### Modify for Your Use

1. Edit `example_usage.py`
2. Change `image_path` to your image file
3. Adjust `selection` coordinates to your region of interest
4. Run the script

## Use Cases

### Batch Processing

Process multiple images with the same selection:

```python
from pathlib import Path
from spriteforge.image_processor import ImageProcessor

image_dir = Path("frames")
selection = (100, 100, 200, 200)

for image_path in image_dir.glob("*.png"):
    processor = ImageProcessor(str(image_path))
    processor.save_sprite(selection, name=f"sprite_{image_path.stem}")
```

### Finding Unique Elements

Identify UI elements or objects by their unique colors:

```python
processor = ImageProcessor("screenshot.png")
selection = (x, y, w, h)  # Region of interest

unique_colors = processor.find_unique_colors(selection)
print(f"Found {len(unique_colors)} unique colors")

if unique_colors:
    # Save visualization
    processor.save_unique_sprite(selection, name="ui_element")
```

### Extracting Animated Sprites

Extract sprites from animation frames:

```python
# Place all animation frames in the same directory
# Use the same selection region across all frames

processor = ImageProcessor("frame_001.png")
selection = (sprite_x, sprite_y, sprite_width, sprite_height)

# This will compare all PNGs in the directory
# and extract only the changing pixels
processor.save_transparent_sprite(selection, name="animated_sprite")
```

## Tips

1. **Selection Coordinates**: Use the GUI first to find correct coordinates
2. **Progress Callbacks**: Add callbacks for long operations:
   ```python
   def progress(percent):
       print(f"\rProgress: {percent:.1f}%", end="")
   
   processor.find_unique_colors(selection, progress_callback=progress)
   ```

3. **Error Handling**: Wrap operations in try-except:
   ```python
   try:
       output = processor.save_sprite(selection)
       print(f"Success: {output}")
   except Exception as e:
       print(f"Error: {e}")
   ```

## More Examples

Check the main [README.md](../README.md) for GUI usage and installation instructions.
