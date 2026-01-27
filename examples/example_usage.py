"""
Example script demonstrating SpriteForge usage programmatically
"""

from pathlib import Path
from spriteforge.image_processor import ImageProcessor


def main():
    """Example usage of SpriteForge programmatically"""
    
    # Example: Load an image
    image_path = "path/to/your/image.png"
    
    if not Path(image_path).exists():
        print(f"Please provide a valid image path. Current: {image_path}")
        return
    
    print("Loading image...")
    processor = ImageProcessor(image_path)
    
    width, height = processor.get_image_size()
    print(f"Image size: {width}x{height}")
    
    # Example: Define a selection region (x, y, width, height)
    selection = (100, 100, 200, 200)
    print(f"Selection: {selection}")
    
    # Example: Extract sprite
    print("\nExtracting sprite...")
    sprite_path = processor.save_sprite(selection, name="example_sprite")
    print(f"Saved sprite: {sprite_path}")
    
    # Example: Find unique colors
    print("\nFinding unique colors...")
    def progress_callback(percent):
        if int(percent) % 20 == 0:  # Print every 20%
            print(f"Progress: {int(percent)}%")
    
    unique_colors = processor.find_unique_colors(selection, progress_callback)
    print(f"Found {len(unique_colors)} unique colors")
    
    if unique_colors:
        # Save unique colors
        colors_path = processor.save_unique_colors(unique_colors, name="example_colors")
        print(f"Saved colors: {colors_path}")
        
        # Create unique sprite
        print("\nCreating unique sprite...")
        unique_sprite_path = processor.save_unique_sprite(
            selection, 
            name="example_unique",
            progress_callback=progress_callback
        )
        if unique_sprite_path:
            print(f"Saved unique sprite: {unique_sprite_path}")
    
    # Example: Extract transparent sprite (requires multiple images)
    print("\nExtracting transparent sprite...")
    print("Note: This requires multiple PNG images in the same directory")
    
    transparent_path = processor.save_transparent_sprite(
        selection,
        name="example_transparent",
        progress_callback=progress_callback
    )
    
    if transparent_path:
        print(f"Saved transparent sprite: {transparent_path}")
    else:
        print("Could not create transparent sprite (need multiple images)")
    
    print("\nDone! Check the output directory for generated files.")


if __name__ == "__main__":
    main()
