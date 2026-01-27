"""
Image processing core functionality for sprite extraction
"""

import io
import time
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image as PILImage, ImageChops, ImageDraw


class ImageProcessor:
    """Handles all image processing operations for sprite extraction"""
    
    def __init__(self, image_path: str):
        self.image_path = Path(image_path)
        self.image: Optional[PILImage.Image] = None
        self.load_image()
    
    def load_image(self):
        """Load the image from file path"""
        if self.image_path.exists():
            self.image = PILImage.open(self.image_path)
    
    def get_image_size(self) -> Tuple[int, int]:
        """Get image dimensions (width, height)"""
        if self.image:
            return self.image.size
        return (0, 0)
    
    def get_selection_image(self, selection: Tuple[int, int, int, int]) -> PILImage.Image:
        """
        Extract a rectangular region from the image
        
        Args:
            selection: (x, y, width, height)
        
        Returns:
            PIL Image of the selected region
        """
        if not self.image:
            return None
        
        x, y, width, height = selection
        crop_box = (x, y, x + width, y + height)
        return self.image.crop(crop_box)
    
    def save_sprite(self, selection: Tuple[int, int, int, int], name: str = "sprite") -> str:
        """
        Save selected region as sprite image
        
        Args:
            selection: (x, y, width, height)
            name: output filename prefix
        
        Returns:
            Path to saved file
        """
        sprite = self.get_selection_image(selection)
        if sprite:
            output_path = self._get_output_path(name)
            sprite.save(output_path)
            return str(output_path)
        return ""
    
    def find_unique_colors(self, selection: Tuple[int, int, int, int], 
                          progress_callback=None) -> List[List[int]]:
        """
        Find colors that are unique to the selected region
        
        Args:
            selection: (x, y, width, height)
            progress_callback: Optional callback(percent) for progress updates
        
        Returns:
            List of RGB color values unique to selection
        """
        if not self.image:
            return []
        
        if progress_callback:
            progress_callback(5)
        
        # Get sprite region
        sprite = self.get_selection_image(selection).convert("RGB")
        
        if progress_callback:
            progress_callback(10)
        
        # Create image with selection blacked out
        image_copy = self.image.copy().convert("RGB")
        draw = ImageDraw.Draw(image_copy)
        x, y, width, height = selection
        draw.rectangle((x, y, x + width, y + height), fill=0)
        del draw
        
        if progress_callback:
            progress_callback(30)
        
        # Get unique colors from rest of image
        rest_pixels = np.unique(np.asarray(image_copy.getdata()), axis=0).tolist()
        
        if progress_callback:
            progress_callback(50)
        
        # Get unique colors from sprite
        sprite_pixels = np.unique(np.asarray(sprite.getdata()), axis=0).tolist()
        
        if progress_callback:
            progress_callback(70)
        
        # Find colors only in sprite
        unique_colors = [item for item in sprite_pixels if item not in rest_pixels]
        
        if progress_callback:
            progress_callback(90)
        
        if unique_colors:
            unique_colors.sort(reverse=True)
        
        if progress_callback:
            progress_callback(100)
        
        return unique_colors
    
    def save_unique_colors(self, unique_colors: List[List[int]], name: str = "unique") -> str:
        """
        Save unique colors as a 1D strip image
        
        Args:
            unique_colors: List of RGB colors
            name: output filename prefix
        
        Returns:
            Path to saved file
        """
        if not unique_colors:
            return ""
        
        unique_array = np.array([unique_colors])
        image = PILImage.fromarray(unique_array.astype('uint8'), "RGB")
        output_path = self._get_output_path(name)
        image.save(output_path)
        return str(output_path)
    
    def create_unique_sprite(self, selection: Tuple[int, int, int, int],
                            progress_callback=None) -> Optional[PILImage.Image]:
        """
        Create sprite showing only unique colors (others transparent)
        
        Args:
            selection: (x, y, width, height)
            progress_callback: Optional callback(percent) for progress updates
        
        Returns:
            PIL Image with RGBA mode (transparent where not unique)
        """
        if progress_callback:
            progress_callback(10)
        
        sprite_array = np.array(self.get_selection_image(selection)).tolist()
        
        if progress_callback:
            progress_callback(20)
        
        unique_colors = self.find_unique_colors(selection)
        
        if not unique_colors:
            if progress_callback:
                progress_callback(100)
            return None
        
        result = []
        total_rows = len(sprite_array)
        for idx, rows in enumerate(sprite_array):
            row = []
            for pixel in rows:
                # For RGB images, pixel is [R, G, B]
                # For RGBA, it's [R, G, B, A]
                rgb_pixel = pixel[:3] if len(pixel) >= 3 else pixel
                
                if rgb_pixel in unique_colors:
                    row.append([rgb_pixel[0], rgb_pixel[1], rgb_pixel[2], 255])
                else:
                    row.append([0, 0, 0, 0])
            result.append(row)
            
            if progress_callback and idx % 10 == 0:
                progress = 20 + int((idx / total_rows) * 70)
                progress_callback(progress)
        
        result_array = np.array(result, dtype='uint8')
        result_image = PILImage.fromarray(result_array, "RGBA")
        
        if progress_callback:
            progress_callback(100)
        
        return result_image
    
    def save_unique_sprite(self, selection: Tuple[int, int, int, int],
                          name: str = "highlight",
                          progress_callback=None) -> str:
        """
        Save sprite with only unique colors visible
        
        Args:
            selection: (x, y, width, height)
            name: output filename prefix
            progress_callback: Optional callback(percent) for progress updates
        
        Returns:
            Path to saved file or empty string
        """
        unique_sprite = self.create_unique_sprite(selection, progress_callback)
        if unique_sprite:
            output_path = self._get_output_path(name)
            unique_sprite.save(output_path)
            return str(output_path)
        return ""
    
    def extract_transparent_sprite(self, selection: Tuple[int, int, int, int],
                                   progress_callback=None) -> Optional[PILImage.Image]:
        """
        Extract sprite by comparing same region across all images in directory
        Pixels that differ become transparent
        
        Args:
            selection: (x, y, width, height)
            progress_callback: Optional callback(percent) for progress updates
        
        Returns:
            PIL Image with RGBA mode
        """
        point_table = [0] + [255] * 255
        
        def diff_image(a, b):
            """Compare two images and make differing pixels transparent"""
            diff = ImageChops.difference(a, b)
            diff = diff.convert('L')
            diff = diff.point(point_table)
            diff = ImageChops.invert(diff)
            new = diff.convert('RGB')
            new.paste(b, mask=diff)
            return new
        
        if progress_callback:
            progress_callback(1)
        
        # Find all PNG images in the same directory
        directory = self.image_path.parent
        png_files = list(directory.glob("*.png"))
        
        if len(png_files) < 2:
            return None
        
        sections = []
        for idx, file_path in enumerate(png_files):
            try:
                image = PILImage.open(file_path)
                section = self.get_selection_image(selection)
                if section:
                    sections.append(section.convert('RGB'))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
            
            if progress_callback:
                progress = 1 + int((idx / len(png_files)) * 40)
                progress_callback(progress)
        
        if not sections:
            return None
        
        # Start with first section
        result = sections.pop(0)
        
        # Compare with all other sections
        for idx, section in enumerate(sections):
            result = diff_image(result, section)
            
            if progress_callback:
                progress = 41 + int((idx / len(sections)) * 59)
                progress_callback(progress)
        
        if progress_callback:
            progress_callback(100)
        
        return result
    
    def save_transparent_sprite(self, selection: Tuple[int, int, int, int],
                               name: str = "extracted",
                               progress_callback=None) -> str:
        """
        Save transparent sprite extracted from multiple images
        
        Args:
            selection: (x, y, width, height)
            name: output filename prefix
            progress_callback: Optional callback(percent) for progress updates
        
        Returns:
            Path to saved file or empty string
        """
        transparent = self.extract_transparent_sprite(selection, progress_callback)
        if transparent:
            output_path = self._get_output_path(name)
            transparent.save(output_path)
            return str(output_path)
        return ""
    
    def _get_output_path(self, name: str) -> Path:
        """Generate unique output filename with timestamp"""
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        filename = f"{name}_{timestamp}.png"
        return self.image_path.parent / filename
    
    def get_region_info(self, x: int, y: int) -> dict:
        """
        Get information about a pixel at given coordinates
        
        Args:
            x, y: Pixel coordinates
        
        Returns:
            Dictionary with pixel color information
        """
        if not self.image:
            return {}
        
        # Ensure coordinates are within bounds
        width, height = self.image.size
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        
        try:
            pixel = self.image.getpixel((x, y))
            return {
                'x': x,
                'y': y,
                'color': pixel
            }
        except:
            return {'x': x, 'y': y, 'color': None}
