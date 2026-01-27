"""
Main application entry point and Flet GUI for SpriteForge
"""

import flet as ft
from pathlib import Path
import sys
from typing import Optional
import base64
from io import BytesIO
from PIL import Image as PILImage

from .image_processor import ImageProcessor


class SpriteForgeApp:
    """Main Flet application for sprite extraction"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "SpriteForge - Forge Your Sprites"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        # State
        self.processor: Optional[ImageProcessor] = None
        self.current_image_path: Optional[str] = None
        self.selection_start: Optional[tuple] = None
        self.selection_end: Optional[tuple] = None
        self.selection: tuple = (0, 0, 0, 0)  # x, y, width, height
        self.zoom_level = 1.0
        self.pan_offset = [0, 0]
        self.is_selecting = False
        
        # UI Components
        self.image_container: Optional[ft.Container] = None
        self.image_widget: Optional[ft.Image] = None
        self.selection_rect: Optional[ft.Container] = None
        self.progress_bar: Optional[ft.ProgressBar] = None
        self.info_panel: Optional[ft.Column] = None
        
        # Info labels
        self.info_labels = {}
        
        self.build_ui()
    
    def build_ui(self):
        """Build the main user interface"""
        
        # Progress bar (hidden by default)
        self.progress_bar = ft.ProgressBar(
            width=400,
            visible=False,
            color=ft.colors.GREEN,
            bgcolor=ft.colors.GREY_300
        )
        
        # Image viewer area
        self.image_widget = ft.Image(
            fit=ft.ImageFit.CONTAIN,
            visible=False
        )
        
        self.selection_rect = ft.Container(
            border=ft.border.all(2, ft.colors.YELLOW),
            bgcolor=ft.colors.with_opacity(0.3, ft.colors.GREEN),
            visible=False
        )
        
        # Stack for image and selection overlay
        image_stack = ft.Stack(
            controls=[
                self.image_widget,
                self.selection_rect
            ],
            expand=True
        )
        
        self.image_container = ft.Container(
            content=image_stack,
            expand=True,
            bgcolor=ft.colors.GREY_900,
            alignment=ft.alignment.center,
            on_click=self.on_image_click
        )
        
        # Info panel labels
        self.info_labels = {
            'file': self._create_info_text('File: No image loaded'),
            'dimensions': self._create_info_text('Dimensions: -'),
            'mouse_x': self._create_info_text('Mouse X: -'),
            'mouse_y': self._create_info_text('Mouse Y: -'),
            'sel_x': self._create_info_text('Selection X: -'),
            'sel_y': self._create_info_text('Selection Y: -'),
            'sel_width': self._create_info_text('Width: -'),
            'sel_height': self._create_info_text('Height: -'),
        }
        
        # Control panel (right side)
        control_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("SpriteForge", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # Load image button
                    ft.ElevatedButton(
                        "Load Image",
                        icon=ft.icons.FOLDER_OPEN,
                        on_click=self.load_image_dialog,
                        bgcolor=ft.colors.BLUE_700
                    ),
                    
                    ft.Divider(),
                    ft.Text("Selection Tools", weight=ft.FontWeight.BOLD),
                    
                    ft.ElevatedButton(
                        "Select Region",
                        icon=ft.icons.SELECT_ALL,
                        on_click=self.start_selection_mode,
                        bgcolor=ft.colors.GREEN_700
                    ),
                    
                    ft.ElevatedButton(
                        "Copy Region",
                        icon=ft.icons.COPY,
                        on_click=self.copy_region_to_clipboard,
                    ),
                    
                    ft.Divider(),
                    ft.Text("Extract Operations", weight=ft.FontWeight.BOLD),
                    
                    ft.ElevatedButton(
                        "Extract Sprite",
                        icon=ft.icons.IMAGE,
                        on_click=self.extract_sprite,
                    ),
                    
                    ft.ElevatedButton(
                        "Unique Colors",
                        icon=ft.icons.PALETTE,
                        on_click=self.extract_unique_colors,
                    ),
                    
                    ft.ElevatedButton(
                        "Unique Sprite",
                        icon=ft.icons.AUTO_FIX_HIGH,
                        on_click=self.extract_unique_sprite,
                    ),
                    
                    ft.ElevatedButton(
                        "Transparent Sprite",
                        icon=ft.icons.LAYERS,
                        on_click=self.extract_transparent_sprite,
                    ),
                    
                    ft.Divider(),
                    ft.Text("Region Info", weight=ft.FontWeight.BOLD),
                    
                    # Info display
                    ft.Column(
                        controls=[
                            self.info_labels['file'],
                            self.info_labels['dimensions'],
                            ft.Divider(height=5),
                            self.info_labels['mouse_x'],
                            self.info_labels['mouse_y'],
                            ft.Divider(height=5),
                            self.info_labels['sel_x'],
                            self.info_labels['sel_y'],
                            self.info_labels['sel_width'],
                            self.info_labels['sel_height'],
                        ],
                        spacing=5
                    ),
                    
                    ft.Container(expand=True),  # Spacer
                    self.progress_bar,
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=300,
            padding=20,
            bgcolor=ft.colors.GREY_800
        )
        
        # Main layout
        main_row = ft.Row(
            controls=[
                self.image_container,
                control_panel
            ],
            spacing=0,
            expand=True
        )
        
        self.page.add(main_row)
        
        # Check for command line argument
        if len(sys.argv) > 1:
            self.load_image(sys.argv[1])
    
    def _create_info_text(self, text: str) -> ft.Text:
        """Create an info label"""
        return ft.Text(text, size=12, color=ft.colors.WHITE70)
    
    def _update_info_label(self, key: str, value: str):
        """Update an info label"""
        if key in self.info_labels:
            self.info_labels[key].value = value
            self.info_labels[key].update()
    
    def load_image_dialog(self, e):
        """Open file picker to select an image"""
        def on_file_pick(result: ft.FilePickerResultEvent):
            if result.files:
                file_path = result.files[0].path
                self.load_image(file_path)
        
        file_picker = ft.FilePicker(on_result=on_file_pick)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg", "bmp", "gif"],
            dialog_title="Select an image"
        )
    
    def load_image(self, file_path: str):
        """Load and display an image"""
        try:
            self.current_image_path = file_path
            self.processor = ImageProcessor(file_path)
            
            # Convert PIL image to base64 for Flet
            img = self.processor.image
            if img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                self.image_widget.src_base64 = img_base64
                self.image_widget.visible = True
                
                width, height = self.processor.get_image_size()
                self._update_info_label('file', f'File: {Path(file_path).name}')
                self._update_info_label('dimensions', f'Dimensions: {width}x{height}')
                
                self.page.update()
                self.show_message(f"Loaded: {Path(file_path).name}", success=True)
        
        except Exception as ex:
            self.show_message(f"Error loading image: {ex}", success=False)
    
    def start_selection_mode(self, e):
        """Activate selection mode"""
        self.is_selecting = True
        self.selection_start = None
        self.selection_end = None
        self.selection_rect.visible = False
        self.page.update()
        self.show_message("Click and drag to select a region", success=True)
    
    def on_image_click(self, e: ft.TapEvent):
        """Handle clicks on the image"""
        if not self.processor or not self.is_selecting:
            return
        
        # For simplicity, we'll use a dialog-based selection
        # In a full implementation, you'd track mouse drag events
        self.show_selection_dialog()
    
    def show_selection_dialog(self):
        """Show dialog for manual region selection"""
        x_field = ft.TextField(label="X", value="0", width=100)
        y_field = ft.TextField(label="Y", value="0", width=100)
        width_field = ft.TextField(label="Width", value="100", width=100)
        height_field = ft.TextField(label="Height", value="100", width=100)
        
        def on_confirm(e):
            try:
                x = int(x_field.value)
                y = int(y_field.value)
                w = int(width_field.value)
                h = int(height_field.value)
                
                self.selection = (x, y, w, h)
                self._update_info_label('sel_x', f'Selection X: {x}')
                self._update_info_label('sel_y', f'Selection Y: {y}')
                self._update_info_label('sel_width', f'Width: {w}')
                self._update_info_label('sel_height', f'Height: {h}')
                
                self.selection_rect.visible = True
                self.is_selecting = False
                
                dialog.open = False
                self.page.update()
                self.show_message("Region selected!", success=True)
            except ValueError:
                self.show_message("Invalid selection values", success=False)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Define Selection Region"),
            content=ft.Column([
                ft.Text("Enter the region coordinates:"),
                ft.Row([x_field, y_field]),
                ft.Row([width_field, height_field]),
            ], tight=True, height=200),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("Confirm", on_click=on_confirm),
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def copy_region_to_clipboard(self, e):
        """Copy region coordinates to clipboard"""
        if not self.check_selection():
            return
        
        x, y, w, h = self.selection
        text = f'"REGION": ({y}, {x}, {y + h}, {x + w})'
        
        self.page.set_clipboard(text)
        self.show_message(f"Copied: {text}", success=True)
    
    def extract_sprite(self, e):
        """Extract and save the selected sprite"""
        if not self.check_ready():
            return
        
        self.show_progress(True)
        
        try:
            output_path = self.processor.save_sprite(self.selection)
            self.show_message(f"Sprite saved: {Path(output_path).name}", success=True)
        except Exception as ex:
            self.show_message(f"Error: {ex}", success=False)
        finally:
            self.show_progress(False)
    
    def extract_unique_colors(self, e):
        """Extract unique colors from selection"""
        if not self.check_ready():
            return
        
        self.show_progress(True)
        
        try:
            unique_colors = self.processor.find_unique_colors(
                self.selection,
                progress_callback=self.update_progress
            )
            
            if unique_colors:
                output_path = self.processor.save_unique_colors(unique_colors)
                self.show_message(
                    f"Found {len(unique_colors)} unique colors. Saved: {Path(output_path).name}",
                    success=True
                )
            else:
                self.show_message("No unique colors found", success=False)
        
        except Exception as ex:
            self.show_message(f"Error: {ex}", success=False)
        finally:
            self.show_progress(False)
    
    def extract_unique_sprite(self, e):
        """Extract sprite with only unique colors visible"""
        if not self.check_ready():
            return
        
        self.show_progress(True)
        
        try:
            output_path = self.processor.save_unique_sprite(
                self.selection,
                progress_callback=self.update_progress
            )
            
            if output_path:
                self.show_message(f"Unique sprite saved: {Path(output_path).name}", success=True)
            else:
                self.show_message("No unique colors found", success=False)
        
        except Exception as ex:
            self.show_message(f"Error: {ex}", success=False)
        finally:
            self.show_progress(False)
    
    def extract_transparent_sprite(self, e):
        """Extract transparent sprite from multiple images"""
        if not self.check_ready():
            return
        
        self.show_progress(True)
        
        try:
            output_path = self.processor.save_transparent_sprite(
                self.selection,
                progress_callback=self.update_progress
            )
            
            if output_path:
                self.show_message(f"Transparent sprite saved: {Path(output_path).name}", success=True)
            else:
                self.show_message("Error: Need multiple images in directory", success=False)
        
        except Exception as ex:
            self.show_message(f"Error: {ex}", success=False)
        finally:
            self.show_progress(False)
    
    def check_ready(self) -> bool:
        """Check if processor and selection are ready"""
        if not self.processor:
            self.show_message("Please load an image first", success=False)
            return False
        return self.check_selection()
    
    def check_selection(self) -> bool:
        """Check if a valid selection exists"""
        x, y, w, h = self.selection
        if w * h < 1:
            self.show_message("Please select a region first", success=False)
            return False
        return True
    
    def show_progress(self, visible: bool):
        """Show or hide progress bar"""
        self.progress_bar.visible = visible
        self.progress_bar.value = None if visible else 0
        self.page.update()
    
    def update_progress(self, percent: float):
        """Update progress bar value"""
        if self.progress_bar.visible:
            self.progress_bar.value = percent / 100.0
            self.page.update()
    
    def show_message(self, message: str, success: bool = True):
        """Show a snack bar message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.GREEN if success else ft.colors.RED_700
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        """Close a dialog"""
        dialog.open = False
        self.page.update()


def main():
    """Main entry point for SpriteForge"""
    def app_main(page: ft.Page):
        SpriteForgeApp(page)
    
    ft.app(target=app_main)


if __name__ == "__main__":
    main()
