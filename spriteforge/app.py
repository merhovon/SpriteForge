"""
Main application entry point for SpriteForge (PyQt6 Version)
"""

import sys
from pathlib import Path
from typing import Optional, List
import json
from collections import deque
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QMenu,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QRubberBand,
    QSlider,
    QProgressDialog,
    QDialog,
    QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QRect, QPoint, QPointF
from PyQt6.QtGui import (
    QAction,
    QKeySequence,
    QPixmap,
    QImage,
    QPainter,
    QMouseEvent,
)

from PIL import Image as PILImage

from .image_processor import ImageProcessor
from .logger import get_logger, setup_logger

# Logger initialisieren
logger = get_logger("app")


class SelectionTool(Enum):
    """Enum für verschiedene Selection-Tools."""

    RECTANGLE = "rectangle"
    POLYGON = "polygon"
    CIRCLE = "circle"


class PreviewDialog(QDialog):
    """Dialog zur Anzeige einer Live-Vorschau vor dem Speichern."""

    def __init__(
        self, parent, title: str, pil_image: PILImage.Image, info_text: str = ""
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.pil_image = pil_image
        self.save_confirmed = False
        self.init_ui(info_text)

    def init_ui(self, info_text: str):
        """Initialisiert die UI des Preview-Dialogs."""
        layout = QVBoxLayout(self)

        # Info Label
        if info_text:
            info_label = QLabel(info_text)
            info_label.setStyleSheet("color: #333; font-size: 12px; padding: 5px;")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

        # Scroll Area für Bild
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Responsive size - 70% of screen size, min 600x600, max 1200x1200
        from PyQt6.QtWidgets import QApplication

        screen = QApplication.primaryScreen().geometry()
        preview_width = max(600, min(1200, int(screen.width() * 0.7)))
        preview_height = max(600, min(1200, int(screen.height() * 0.7)))
        scroll_area.setMinimumSize(preview_width, preview_height)

        # Konvertiere PIL zu QImage
        if self.pil_image.mode == "RGB":
            qimage = QImage(
                self.pil_image.tobytes(),
                self.pil_image.width,
                self.pil_image.height,
                self.pil_image.width * 3,
                QImage.Format.Format_RGB888,
            )
        elif self.pil_image.mode == "RGBA":
            qimage = QImage(
                self.pil_image.tobytes(),
                self.pil_image.width,
                self.pil_image.height,
                self.pil_image.width * 4,
                QImage.Format.Format_RGBA8888,
            )
        else:
            # Convert to RGBA
            temp_image = self.pil_image.convert("RGBA")
            qimage = QImage(
                temp_image.tobytes(),
                temp_image.width,
                temp_image.height,
                temp_image.width * 4,
                QImage.Format.Format_RGBA8888,
            )

        # QLabel für Bildanzeige
        image_label = QLabel()
        pixmap = QPixmap.fromImage(qimage)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area.setWidget(image_label)
        layout.addWidget(scroll_area)

        # Button Layout
        button_layout = QHBoxLayout()

        # Save Button
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet(
            "background-color: #007acc; color: white; padding: 10px; font-size: 14px;"
        )
        save_btn.clicked.connect(self.on_save)
        button_layout.addWidget(save_btn)

        # Cancel Button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet(
            "background-color: #666; color: white; padding: 10px; font-size: 14px;"
        )
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_save(self):
        """Bestätigt das Speichern."""
        self.save_confirmed = True
        self.accept()


class RecentFiles:
    """Verwaltet die Liste der zuletzt geöffneten Dateien."""

    def __init__(self, max_files=10):
        self.max_files = max_files
        self.config_file = Path.home() / ".spriteforge" / "recent.json"
        self.files: List[str] = []
        self.load()

    def load(self):
        """Lädt die Recent Files Liste."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.files = data.get("recent", [])
                logger.info(f"Loaded {len(self.files)} recent files")
        except Exception as e:
            logger.error(f"Error loading recent files: {e}")
            self.files = []

    def save(self):
        """Speichert die Recent Files Liste."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({"recent": self.files}, f, indent=2)
            logger.info("Saved recent files")
        except Exception as e:
            logger.error(f"Error saving recent files: {e}")

    def add(self, file_path: str):
        """Fügt eine Datei zur Liste hinzu."""
        file_path = str(Path(file_path).resolve())

        if file_path in self.files:
            self.files.remove(file_path)

        self.files.insert(0, file_path)
        self.files = self.files[: self.max_files]

        self.save()
        logger.debug(f"Added recent file: {file_path}")

    def get_files(self) -> List[str]:
        """Gibt die Liste der existierenden Recent Files zurück."""
        existing = [f for f in self.files if Path(f).exists()]
        if len(existing) != len(self.files):
            self.files = existing
            self.save()
        return existing


class UndoRedoManager:
    """Verwaltet Undo/Redo für Selektionen."""

    def __init__(self, max_history=50):
        self.undo_stack = deque(maxlen=max_history)
        self.redo_stack = deque(maxlen=max_history)

    def push(self, selection: tuple):
        """Fügt eine Selektion zur Undo-History hinzu."""
        self.undo_stack.append(selection)
        self.redo_stack.clear()
        logger.debug(f"Pushed selection to undo stack: {selection}")

    def undo(self) -> Optional[tuple]:
        """Macht die letzte Selektion rückgängig."""
        if self.undo_stack:
            current = self.undo_stack.pop()
            self.redo_stack.append(current)
            logger.debug(f"Undo: {current}")
            return self.undo_stack[-1] if self.undo_stack else (0, 0, 0, 0)
        return None

    def redo(self) -> Optional[tuple]:
        """Stellt die letzte rückgängig gemachte Selektion wieder her."""
        if self.redo_stack:
            selection = self.redo_stack.pop()
            self.undo_stack.append(selection)
            logger.debug(f"Redo: {selection}")
            return selection
        return None

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0


class ImageCanvas(QGraphicsView):
    """Custom QGraphicsView für Image Display mit Zoom/Pan und Selection."""

    # Signals
    selectionChanged = pyqtSignal(tuple)  # (x, y, width, height)
    mouseMoved = pyqtSignal(int, int)  # (x, y) in image coordinates

    def __init__(self, parent=None):
        super().__init__(parent)

        # Scene setup
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Pixmap Item
        self.pixmap_item: Optional[QGraphicsPixmapItem] = None

        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)  # Start in selection mode
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Scroll bar policies
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Size policy - expand to fill available space
        from PyQt6.QtWidgets import QSizePolicy

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)

        # Background
        self.setStyleSheet("background-color: #2b2b2b; border: none;")

        # Zoom settings
        self.zoom_factor = 1.15
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.current_zoom = 1.0

        # Selection state
        self.selection_mode = True  # True = selection, False = pan
        self.current_tool = SelectionTool.RECTANGLE  # Active tool
        self.rubber_band: Optional[QRubberBand] = None
        self.selection_start: Optional[QPoint] = None
        self.current_selection: Optional[tuple[int, int, int, int]] = None
        self.current_selection_tool: Optional[SelectionTool] = (
            None  # Which tool created current selection
        )

        # Polygon tool state
        self.polygon_points: List[QPoint] = []  # View coordinates
        self.polygon_preview_active = False
        self.polygon_cursor_pos: Optional[QPoint] = None  # Current cursor position
        self.finalized_polygon_points: List[
            QPoint
        ] = []  # Finalized polygon for display

        # Circle tool state
        self.circle_center: Optional[QPoint] = None  # View coordinates
        self.circle_radius_point: Optional[QPoint] = None  # View coordinates
        self.finalized_circle_center: Optional[QPoint] = None  # Finalized circle center
        self.finalized_circle_radius: float = 0.0  # Finalized circle radius

        # Grid settings
        self.grid_visible = False
        self.grid_size = 32  # pixels

        # Overlay
        self.overlay_item: Optional[QGraphicsPixmapItem] = None

        # History flag (used by undo/redo)
        self._is_applying_history = False

        # Enable mouse tracking
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.snap_to_grid_enabled = True  # Snap polygon points to grid

        # Enable keyboard focus for arrow key handling
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Selection manipulation state
        self.handle_size = 8  # Handle size in pixels
        self.active_handle: Optional[str] = None  # Which handle is being dragged
        self.is_moving_selection = False  # Is selection being moved
        self.move_start_pos: Optional[QPoint] = None  # Start position for move

        logger.info("ImageCanvas initialized")

    def set_image(self, image: QImage):
        """Setzt ein neues Bild im Canvas."""
        # Clear existing items
        self.scene.clear()

        # Create pixmap from image
        pixmap = QPixmap.fromImage(image)

        # Add to scene
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)

        # Set scene rect to pixmap bounds
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        # Fit in view
        self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.current_zoom = 1.0

        logger.info(f"Image set: {pixmap.width()}x{pixmap.height()}")

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        if self.pixmap_item is None:
            return

        # Get scroll direction
        delta = event.angleDelta().y()

        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        """Zoom in."""
        if self.current_zoom < self.max_zoom:
            self.scale(self.zoom_factor, self.zoom_factor)
            self.current_zoom *= self.zoom_factor
            logger.debug(f"Zoomed in: {self.current_zoom:.2f}x")

    def zoom_out(self):
        """Zoom out."""
        if self.current_zoom > self.min_zoom:
            factor = 1.0 / self.zoom_factor
            self.scale(factor, factor)
            self.current_zoom *= factor
            logger.debug(f"Zoomed out: {self.current_zoom:.2f}x")

    def zoom_reset(self):
        """Reset zoom to 1:1."""
        if self.pixmap_item:
            self.resetTransform()
            self.current_zoom = 1.0
            logger.debug("Zoom reset to 1:1")

    def zoom_fit(self):
        """Fit image in view."""
        if self.pixmap_item:
            self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
            self.current_zoom = 1.0
            logger.debug("Zoom fit to window")

    def get_zoom_level(self) -> float:
        """Returns current zoom level."""
        return self.current_zoom

    def set_selection_mode(self, enabled: bool):
        """Toggle between selection and pan mode."""
        self.selection_mode = enabled
        if not enabled:
            # Pan mode
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self._cancel_current_operation()
        else:
            # Selection mode
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def set_tool(self, tool: SelectionTool):
        """Wechselt das aktive Selection-Tool."""
        if self.current_tool != tool:
            self._cancel_current_operation()
            self.current_tool = tool
            logger.info(f"Selection tool changed to: {tool.value}")

    def _cancel_current_operation(self):
        """Bricht die aktuelle Selection-Operation ab."""
        # Rectangle: Hide rubber band
        if self.rubber_band:
            self.rubber_band.hide()
        self.selection_start = None

        # Polygon: Clear points
        self.polygon_points.clear()
        self.polygon_preview_active = False

        # Circle: Clear state
        self.circle_center = None
        self.circle_radius_point = None

        # Trigger repaint
        self.viewport().update()

    def get_selection(self) -> Optional[tuple[int, int, int, int]]:
        """Returns current selection (x, y, w, h) in image coordinates."""
        return self.current_selection

    def clear_selection(self):
        """Clears current selection."""
        if self.rubber_band:
            self.rubber_band.hide()
        self.current_selection = None
        self.current_selection_tool = None
        self.finalized_circle_center = None
        self.finalized_circle_radius = 0.0
        self.finalized_polygon_points.clear()
        self.active_handle = None
        self.is_moving_selection = False
        self.move_start_pos = None
        self.selectionChanged.emit(())

    def apply_selection(self, selection: tuple):
        """Apply a selection programmatically (for undo/redo).

        Args:
            selection: (x, y, width, height) in image coordinates
        """
        if not selection or selection == (0, 0, 0, 0):
            self.clear_selection()
            return

        x, y, w, h = selection

        # Set internal state
        self.current_selection = selection

        # Update rubber band visual
        if not self.rubber_band:
            self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self.viewport())

        # Convert image coords to view coords
        view_rect = self._image_coords_to_view_rect(selection)
        if view_rect:
            self.rubber_band.setGeometry(view_rect)
            self.rubber_band.show()

        # Force redraw
        self.viewport().update()
        logger.debug(f"Applied selection: {selection}")

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for selection."""
        # Ensure canvas has focus for keyboard events (Ctrl+Arrow, Alt+Arrow)
        self.setFocus()

        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            if not self.pixmap_item:
                return

            if self.current_tool == SelectionTool.RECTANGLE:
                self._handle_rectangle_press(event)
            elif self.current_tool == SelectionTool.POLYGON:
                self._handle_polygon_click(event)
            elif self.current_tool == SelectionTool.CIRCLE:
                self._handle_circle_press(event)
        else:
            # Let base class handle (for pan mode)
            super().mousePressEvent(event)

    def _handle_rectangle_press(self, event: QMouseEvent):
        """Handle mouse press for rectangle tool."""
        # Check if clicking on existing selection handle or inside selection
        if self.current_selection and self.current_tool == SelectionTool.RECTANGLE:
            handle = self._get_handle_at_pos(event.pos())
            if handle:
                # Start resize operation
                self.active_handle = handle
                self.move_start_pos = event.pos()
                return

            # Check if clicking inside selection
            if self._is_point_in_selection(event.pos()):
                # Start move operation
                self.is_moving_selection = True
                self.move_start_pos = event.pos()
                return

        # Start new selection
        self.selection_start = event.pos()

        # Create or reset rubber band
        if not self.rubber_band:
            self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self.viewport())

        self.rubber_band.setGeometry(QRect(self.selection_start, self.selection_start))
        self.rubber_band.show()

    def _get_handle_at_pos(self, pos: QPoint) -> Optional[str]:
        """Check if position is on a selection handle."""
        if not self.current_selection:
            return None

        # Convert selection to view coordinates
        sel_rect = self._selection_to_view_rect()
        if not sel_rect:
            return None

        x, y, w, h = sel_rect.x(), sel_rect.y(), sel_rect.width(), sel_rect.height()
        hs = self.handle_size

        # Check all 8 handles
        handles = {
            "top-left": QRect(x - hs // 2, y - hs // 2, hs, hs),
            "top": QRect(x + w // 2 - hs // 2, y - hs // 2, hs, hs),
            "top-right": QRect(x + w - hs // 2, y - hs // 2, hs, hs),
            "right": QRect(x + w - hs // 2, y + h // 2 - hs // 2, hs, hs),
            "bottom-right": QRect(x + w - hs // 2, y + h - hs // 2, hs, hs),
            "bottom": QRect(x + w // 2 - hs // 2, y + h - hs // 2, hs, hs),
            "bottom-left": QRect(x - hs // 2, y + h - hs // 2, hs, hs),
            "left": QRect(x - hs // 2, y + h // 2 - hs // 2, hs, hs),
        }

        for name, rect in handles.items():
            if rect.contains(pos):
                return name

        return None

    def _is_point_in_selection(self, pos: QPoint) -> bool:
        """Check if point is inside current selection."""
        if not self.current_selection:
            return False

        sel_rect = self._selection_to_view_rect()
        if not sel_rect:
            return False

        return sel_rect.contains(pos)

    def _selection_to_view_rect(self) -> Optional[QRect]:
        """Convert image selection coordinates to view rectangle."""
        if not self.current_selection or not self.pixmap_item:
            return None

        x, y, w, h = self.current_selection

        # Convert image coords to scene coords
        scene_top_left = QPointF(x, y)
        scene_bottom_right = QPointF(x + w, y + h)

        # Convert scene coords to view coords
        view_top_left = self.mapFromScene(scene_top_left)
        view_bottom_right = self.mapFromScene(scene_bottom_right)

        return QRect(view_top_left, view_bottom_right).normalized()

    def _handle_polygon_click(self, event: QMouseEvent):
        """Handle click for polygon tool (AnyLabeling-style)."""
        # Add point to polygon
        point = event.pos()

        # Snap to grid if enabled
        if self.snap_to_grid_enabled:
            point = self._snap_to_grid(point)

        self.polygon_points.append(point)
        self.polygon_preview_active = True

        logger.debug(f"Polygon point added: {len(self.polygon_points)}")

        # Trigger repaint to show preview
        self.viewport().update()

    def _handle_circle_press(self, event: QMouseEvent):
        """Handle mouse press for circle tool."""
        if self.circle_center is None:
            # First click: set center
            self.circle_center = event.pos()
            logger.debug("Circle center set")
        else:
            # Second click: set radius point (will be handled in release)
            self.circle_radius_point = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for selection."""
        # Emit mouse position in image coordinates
        if self.pixmap_item:
            scene_pos = self.mapToScene(event.pos())
            img_x = int(scene_pos.x())
            img_y = int(scene_pos.y())

            # Clamp to image bounds
            img_w = int(self.pixmap_item.boundingRect().width())
            img_h = int(self.pixmap_item.boundingRect().height())

            if 0 <= img_x < img_w and 0 <= img_y < img_h:
                self.mouseMoved.emit(img_x, img_y)

        if self.selection_mode:
            if self.current_tool == SelectionTool.RECTANGLE:
                # Handle resize operation
                if self.active_handle and self.move_start_pos:
                    self._resize_selection(event.pos())
                    return

                # Handle move operation
                if self.is_moving_selection and self.move_start_pos:
                    self._move_selection(event.pos())
                    return

                # Regular rubber band drawing
                if self.selection_start and self.rubber_band:
                    # Update rubber band geometry
                    rect = QRect(self.selection_start, event.pos()).normalized()
                    self.rubber_band.setGeometry(rect)
            elif self.current_tool == SelectionTool.POLYGON:
                # Update preview for polygon (live edge from last point to cursor)
                if self.polygon_preview_active:
                    self.polygon_cursor_pos = event.pos()  # Store cursor position
                    self.viewport().update()
            elif self.current_tool == SelectionTool.CIRCLE:
                # Update circle radius during drag
                if self.circle_center is not None:
                    self.circle_radius_point = event.pos()
                    self.viewport().update()
        else:
            # Let base class handle
            super().mouseMoveEvent(event)

    def _move_selection(self, current_pos: QPoint):
        """Move selection by mouse drag."""
        if not self.current_selection or not self.move_start_pos:
            return

        # Calculate delta in view coordinates
        delta = current_pos - self.move_start_pos

        # Convert delta to scene coordinates
        scene_delta = self.mapToScene(delta) - self.mapToScene(QPoint(0, 0))

        x, y, w, h = self.current_selection

        # Update selection position
        new_x = int(x + scene_delta.x())
        new_y = int(y + scene_delta.y())

        # Clamp to image bounds
        if self.pixmap_item:
            img_w = int(self.pixmap_item.boundingRect().width())
            img_h = int(self.pixmap_item.boundingRect().height())

            new_x = max(0, min(new_x, img_w - w))
            new_y = max(0, min(new_y, img_h - h))

        self.current_selection = (new_x, new_y, w, h)
        self.move_start_pos = current_pos

        # Trigger repaint
        self.viewport().update()

    def _resize_selection(self, current_pos: QPoint):
        """Resize selection by dragging handle."""
        if (
            not self.current_selection
            or not self.active_handle
            or not self.move_start_pos
        ):
            return

        # Get current selection
        x, y, w, h = self.current_selection

        # Convert positions to scene coordinates
        scene_current = self.mapToScene(current_pos)
        scene_start = self.mapToScene(self.move_start_pos)
        delta_x = scene_current.x() - scene_start.x()
        delta_y = scene_current.y() - scene_start.y()

        # Update selection based on handle
        if "left" in self.active_handle:
            new_x = int(x + delta_x)
            new_w = int(w - delta_x)
            if new_w > 0:
                x, w = new_x, new_w
        if "right" in self.active_handle:
            w = int(max(1, w + delta_x))
        if "top" in self.active_handle:
            new_y = int(y + delta_y)
            new_h = int(h - delta_y)
            if new_h > 0:
                y, h = new_y, new_h
        if "bottom" in self.active_handle:
            h = int(max(1, h + delta_y))

        # Clamp to image bounds
        if self.pixmap_item:
            img_w = int(self.pixmap_item.boundingRect().width())
            img_h = int(self.pixmap_item.boundingRect().height())

            x = max(0, min(x, img_w - 1))
            y = max(0, min(y, img_h - 1))
            w = max(1, min(w, img_w - x))
            h = max(1, min(h, img_h - y))

        self.current_selection = (x, y, w, h)
        self.move_start_pos = current_pos

        # Trigger repaint
        self.viewport().update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release for selection."""
        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            # Finalize move/resize operations
            if self.active_handle or self.is_moving_selection:
                # Emit updated selection
                if self.current_selection:
                    self.selectionChanged.emit(self.current_selection)

                # Reset state
                self.active_handle = None
                self.is_moving_selection = False
                self.move_start_pos = None
                return

            if self.current_tool == SelectionTool.RECTANGLE:
                self._finalize_rectangle_selection(event)
            elif self.current_tool == SelectionTool.CIRCLE:
                self._finalize_circle_selection()
            # Polygon is finalized via Enter key, not mouse release
        else:
            # Let base class handle
            super().mouseReleaseEvent(event)
            # Let base class handle
            super().mouseReleaseEvent(event)

    def _finalize_rectangle_selection(self, event: QMouseEvent):
        """Finalize rectangle selection."""
        if self.selection_start and self.rubber_band and self.pixmap_item:
            # Get selection rectangle in view coordinates
            view_rect = QRect(self.selection_start, event.pos()).normalized()

            # Convert to image coordinates
            selection = self._view_rect_to_image_coords(view_rect)

            if selection:
                self.current_selection = selection
                self.current_selection_tool = SelectionTool.RECTANGLE
                self.selectionChanged.emit(self.current_selection)
                logger.info(f"Rectangle selection: {selection}")

            # Hide rubber band
            self.rubber_band.hide()

        self.selection_start = None

    def _finalize_circle_selection(self):
        """Finalize circle selection (two-point mode)."""
        if self.circle_center and self.circle_radius_point and self.pixmap_item:
            # Calculate bounding rectangle for circle
            from math import sqrt

            # Calculate radius in view coordinates
            dx = self.circle_radius_point.x() - self.circle_center.x()
            dy = self.circle_radius_point.y() - self.circle_center.y()
            radius = sqrt(dx * dx + dy * dy)

            # Create bounding rectangle
            top_left = QPoint(
                int(self.circle_center.x() - radius),
                int(self.circle_center.y() - radius),
            )
            bottom_right = QPoint(
                int(self.circle_center.x() + radius),
                int(self.circle_center.y() + radius),
            )

            view_rect = QRect(top_left, bottom_right).normalized()

            # Convert to image coordinates
            selection = self._view_rect_to_image_coords(view_rect)

            if selection:
                self.current_selection = selection
                self.current_selection_tool = SelectionTool.CIRCLE
                # Store finalized circle data for drawing
                self.finalized_circle_center = QPoint(self.circle_center)
                self.finalized_circle_radius = radius
                self.selectionChanged.emit(self.current_selection)
                logger.info(f"Circle selection: {selection}")

            # Reset circle preview state
            self.circle_center = None
            self.circle_radius_point = None
            self.viewport().update()

    def _finalize_polygon_selection(self):
        """Finalize polygon selection (called on Enter key)."""
        if len(self.polygon_points) < 3:
            logger.warning("Polygon needs at least 3 points")
            return

        if not self.pixmap_item:
            return

        # Calculate bounding box from polygon points
        min_x = min(p.x() for p in self.polygon_points)
        max_x = max(p.x() for p in self.polygon_points)
        min_y = min(p.y() for p in self.polygon_points)
        max_y = max(p.y() for p in self.polygon_points)

        view_rect = QRect(QPoint(min_x, min_y), QPoint(max_x, max_y)).normalized()

        # Convert to image coordinates
        selection = self._view_rect_to_image_coords(view_rect)

        if selection:
            self.current_selection = selection
            self.current_selection_tool = SelectionTool.POLYGON
            # Store finalized polygon data for drawing
            self.finalized_polygon_points = [QPoint(p) for p in self.polygon_points]
            self.selectionChanged.emit(self.current_selection)
            logger.info(
                f"Polygon selection ({len(self.polygon_points)} points): {selection}"
            )

        # Clear polygon preview state
        self.polygon_points.clear()
        self.polygon_preview_active = False
        self.viewport().update()

    def _view_rect_to_image_coords(
        self, view_rect: QRect
    ) -> Optional[tuple[int, int, int, int]]:
        """Convert view rectangle to image coordinates."""
        if not self.pixmap_item:
            return None

        # Convert to scene coordinates
        scene_top_left = self.mapToScene(view_rect.topLeft())
        scene_bottom_right = self.mapToScene(view_rect.bottomRight())

        # Get pixmap item position and size
        pixmap_rect = self.pixmap_item.boundingRect()

        # Convert scene coordinates to image coordinates
        img_x = int(max(0, scene_top_left.x() - pixmap_rect.x()))
        img_y = int(max(0, scene_top_left.y() - pixmap_rect.y()))
        img_x2 = int(min(pixmap_rect.width(), scene_bottom_right.x() - pixmap_rect.x()))
        img_y2 = int(
            min(pixmap_rect.height(), scene_bottom_right.y() - pixmap_rect.y())
        )

        # Calculate width and height
        width = img_x2 - img_x
        height = img_y2 - img_y

        # Only return if selection has valid size
        if width > 0 and height > 0:
            return (img_x, img_y, width, height)

        return None

    def _image_coords_to_view_rect(self, selection: tuple) -> Optional[QRect]:
        """Convert image coordinates to view rectangle.

        Args:
            selection: (x, y, width, height) in image coordinates

        Returns:
            QRect in view coordinates or None if pixmap not loaded
        """
        if not self.pixmap_item:
            return None

        x, y, w, h = selection
        pixmap_rect = self.pixmap_item.boundingRect()

        # Scene coordinates
        scene_x = pixmap_rect.x() + x
        scene_y = pixmap_rect.y() + y
        scene_x2 = scene_x + w
        scene_y2 = scene_y + h

        # Convert to view coordinates
        view_top_left = self.mapFromScene(QPointF(scene_x, scene_y))
        view_bottom_right = self.mapFromScene(QPointF(scene_x2, scene_y2))

        return QRect(view_top_left, view_bottom_right).normalized()

    def keyPressEvent(self, event):
        """Handle keyboard events."""
        if event.key() == Qt.Key.Key_Escape:
            # Clear/cancel current operation
            self.clear_selection()
            self._cancel_current_operation()
            event.accept()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Complete polygon selection
            if (
                self.current_tool == SelectionTool.POLYGON
                and len(self.polygon_points) >= 3
            ):
                self._finalize_polygon_selection()
                event.accept()
            else:
                super().keyPressEvent(event)
        elif self.current_selection:
            # Arrow keys for move/resize (works for all selection types)
            handled = self._handle_arrow_keys(event)
            if handled:
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            # Let base class handle
            super().keyPressEvent(event)

    def _handle_arrow_keys(self, event) -> bool:
        """Handle arrow key shortcuts for move/resize selection."""
        if not self.current_selection:
            return False

        old_x, old_y, old_w, old_h = self.current_selection
        x, y, w, h = old_x, old_y, old_w, old_h
        modifiers = event.modifiers()

        # Movement delta (1px or 5px with Shift)
        delta = 5 if modifiers & Qt.KeyboardModifier.ShiftModifier else 1

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl + Arrow: Resize from bottom-right
            if event.key() == Qt.Key.Key_Left:
                w = max(1, w - delta)
            elif event.key() == Qt.Key.Key_Right:
                w += delta
            elif event.key() == Qt.Key.Key_Up:
                h = max(1, h - delta)
            elif event.key() == Qt.Key.Key_Down:
                h += delta
            else:
                return False
        elif modifiers & Qt.KeyboardModifier.AltModifier:
            # Alt + Arrow: Resize from top-left
            if event.key() == Qt.Key.Key_Left:
                x -= delta
                w += delta
            elif event.key() == Qt.Key.Key_Right:
                x += delta
                w = max(1, w - delta)
            elif event.key() == Qt.Key.Key_Up:
                y -= delta
                h += delta
            elif event.key() == Qt.Key.Key_Down:
                y += delta
                h = max(1, h - delta)
            else:
                return False
        else:
            # Arrow: Move selection
            if event.key() == Qt.Key.Key_Left:
                x -= delta
            elif event.key() == Qt.Key.Key_Right:
                x += delta
            elif event.key() == Qt.Key.Key_Up:
                y -= delta
            elif event.key() == Qt.Key.Key_Down:
                y += delta
            else:
                return False

        # Clamp to image bounds
        if self.pixmap_item:
            img_w = int(self.pixmap_item.boundingRect().width())
            img_h = int(self.pixmap_item.boundingRect().height())

            x = max(0, min(x, img_w - w))
            y = max(0, min(y, img_h - h))
            w = max(1, min(w, img_w - x))
            h = max(1, min(h, img_h - y))

        # Update selection
        self.current_selection = (x, y, w, h)

        # Update finalized shape data for Circle/Polygon selections
        self._update_finalized_shapes(old_x, old_y, old_w, old_h, x, y, w, h)

        self.selectionChanged.emit(self.current_selection)
        self.viewport().update()

        return True

    def _update_finalized_shapes(
        self, old_x, old_y, old_w, old_h, new_x, new_y, new_w, new_h
    ):
        """Update finalized shape data when selection is moved/resized via keyboard."""
        if self.current_selection_tool == SelectionTool.CIRCLE:
            # Update circle center and radius
            if self.finalized_circle_center and self.finalized_circle_radius > 0:
                # Convert to scene coordinates for calculation
                old_center_x = old_x + old_w / 2
                old_center_y = old_y + old_h / 2
                new_center_x = new_x + new_w / 2
                new_center_y = new_y + new_h / 2

                # Calculate scale factors
                scale_x = new_w / old_w if old_w > 0 else 1.0
                scale_y = new_h / old_h if old_h > 0 else 1.0
                scale = (scale_x + scale_y) / 2  # Average scale

                # Convert image delta to view delta
                if self.pixmap_item:
                    scene_old_center = QPointF(old_center_x, old_center_y)
                    scene_new_center = QPointF(new_center_x, new_center_y)
                    view_old_center = self.mapFromScene(scene_old_center)
                    view_new_center = self.mapFromScene(scene_new_center)

                    view_delta_x = view_new_center.x() - view_old_center.x()
                    view_delta_y = view_new_center.y() - view_old_center.y()

                    self.finalized_circle_center = QPoint(
                        int(self.finalized_circle_center.x() + view_delta_x),
                        int(self.finalized_circle_center.y() + view_delta_y),
                    )
                    self.finalized_circle_radius *= scale

        elif self.current_selection_tool == SelectionTool.POLYGON:
            # Update polygon points
            if self.finalized_polygon_points:
                # Convert to view coordinates for transformation
                if self.pixmap_item:
                    new_points = []
                    for point in self.finalized_polygon_points:
                        # Convert from view to scene to image coords
                        scene_point = self.mapToScene(point)
                        img_x = int(scene_point.x())
                        img_y = int(scene_point.y())

                        # Calculate relative position in old bounding box
                        rel_x = (img_x - old_x) / old_w if old_w > 0 else 0.5
                        rel_y = (img_y - old_y) / old_h if old_h > 0 else 0.5

                        # Apply to new bounding box
                        new_img_x = new_x + rel_x * new_w
                        new_img_y = new_y + rel_y * new_h

                        # Convert back to view coordinates
                        new_scene_point = QPointF(new_img_x, new_img_y)
                        new_view_point = self.mapFromScene(new_scene_point)
                        new_points.append(QPoint(new_view_point.toPoint()))

                    self.finalized_polygon_points = new_points

    def set_grid_visible(self, visible: bool):
        """Toggle grid visibility."""
        self.grid_visible = visible
        self.viewport().update()  # Trigger repaint
        logger.debug(f"Grid visibility: {visible}")

    def set_grid_size(self, size: int):
        """Set grid cell size."""
        self.grid_size = max(8, min(128, size))  # Clamp between 8-128
        if self.grid_visible:
            self.viewport().update()
        logger.debug(f"Grid size: {self.grid_size}")

    def set_overlay(self, overlay_image: PILImage.Image, selection: tuple):
        """Set overlay image to display on canvas."""
        x, y, w, h = selection

        # Convert PIL Image to QImage
        if overlay_image.mode == "RGBA":
            qimage = QImage(
                overlay_image.tobytes(),
                overlay_image.width,
                overlay_image.height,
                overlay_image.width * 4,
                QImage.Format.Format_RGBA8888,
            )
        else:
            # Convert to RGBA
            temp_image = overlay_image.convert("RGBA")
            qimage = QImage(
                temp_image.tobytes(),
                temp_image.width,
                temp_image.height,
                temp_image.width * 4,
                QImage.Format.Format_RGBA8888,
            )

        # Remove existing overlay if present
        if hasattr(self, "overlay_item") and self.overlay_item:
            self.scene.removeItem(self.overlay_item)

        # Create overlay pixmap item
        pixmap = QPixmap.fromImage(qimage)
        self.overlay_item = QGraphicsPixmapItem(pixmap)
        self.overlay_item.setPos(x, y)
        self.overlay_item.setZValue(5)  # Above selection but below handles
        self.scene.addItem(self.overlay_item)

        logger.debug(f"Overlay set at ({x}, {y}) with size {w}x{h}")

    def clear_overlay(self):
        """Remove overlay from canvas."""
        if hasattr(self, "overlay_item") and self.overlay_item:
            self.scene.removeItem(self.overlay_item)
            self.overlay_item = None
            logger.debug("Overlay cleared")

    def _snap_to_grid(self, point: QPoint) -> QPoint:
        """
        Snap a point to the nearest grid intersection.

        Args:
            point: Point in view coordinates

        Returns:
            Snapped point in view coordinates
        """
        # Convert to scene coordinates
        scene_point = self.mapToScene(point)

        # Snap to grid
        snapped_x = round(scene_point.x() / self.grid_size) * self.grid_size
        snapped_y = round(scene_point.y() / self.grid_size) * self.grid_size

        # Convert back to view coordinates
        snapped_scene = self.mapFromScene(QPointF(snapped_x, snapped_y))

        return snapped_scene

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """Draw grid overlay, tool previews, and selection handles on top of scene."""
        super().drawForeground(painter, rect)

        # Draw grid
        if self.grid_visible and self.pixmap_item:
            self._draw_grid(painter, rect)

        # Draw tool previews in viewport coordinates
        painter.save()
        painter.resetTransform()  # Switch to viewport coordinates

        # Draw polygon preview
        if self.current_tool == SelectionTool.POLYGON and self.polygon_preview_active:
            self._draw_polygon_preview(painter)

        # Draw circle preview
        if self.current_tool == SelectionTool.CIRCLE and self.circle_center:
            self._draw_circle_preview(painter)

        # Draw finalized selections based on tool used
        if self.current_selection and (
            self.rubber_band is None or not self.rubber_band.isVisible()
        ):
            if self.current_selection_tool == SelectionTool.RECTANGLE:
                self._draw_selection_handles(painter)
            elif self.current_selection_tool == SelectionTool.CIRCLE:
                self._draw_finalized_circle(painter)
            elif self.current_selection_tool == SelectionTool.POLYGON:
                self._draw_finalized_polygon(painter)

        painter.restore()

    def _draw_grid(self, painter: QPainter, rect: QRectF):
        """Draw grid overlay."""
        # Safety check
        if self.grid_size <= 0:
            return

        # Set pen for grid lines
        pen = painter.pen()
        pen.setColor(Qt.GlobalColor.white)
        pen.setWidth(0)  # Cosmetic pen (always 1 pixel)
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)

        # Get scene bounds
        scene_rect = self.sceneRect()

        # Safety check for valid scene rect
        if scene_rect.width() <= 0 or scene_rect.height() <= 0:
            return

        # Draw vertical lines
        x = 0
        max_iterations = 10000  # Prevent infinite loops
        iteration_count = 0
        while x <= scene_rect.width() and iteration_count < max_iterations:
            painter.drawLine(
                int(x), int(scene_rect.top()), int(x), int(scene_rect.bottom())
            )
            x += self.grid_size
            iteration_count += 1

        # Draw horizontal lines
        y = 0
        iteration_count = 0
        while y <= scene_rect.height() and iteration_count < max_iterations:
            painter.drawLine(
                int(scene_rect.left()), int(y), int(scene_rect.right()), int(y)
            )
            y += self.grid_size
            iteration_count += 1

    def _draw_polygon_preview(self, painter: QPainter):
        """Draw polygon preview with lines and vertices."""
        if len(self.polygon_points) < 1:
            return

        from PyQt6.QtGui import QPen, QBrush, QColor

        # Draw edges
        pen = QPen(QColor(0, 122, 204), 2)  # Blue lines
        painter.setPen(pen)

        for i in range(len(self.polygon_points) - 1):
            painter.drawLine(self.polygon_points[i], self.polygon_points[i + 1])

        # Draw live edge from last point to cursor
        if self.polygon_cursor_pos and len(self.polygon_points) > 0:
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.polygon_points[-1], self.polygon_cursor_pos)

            # Also draw potential closing line if we have enough points
            if len(self.polygon_points) >= 2:
                painter.drawLine(self.polygon_cursor_pos, self.polygon_points[0])

        # Draw closing line if we have enough points (preview)
        elif len(self.polygon_points) >= 3:
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(self.polygon_points[-1], self.polygon_points[0])

        # Draw vertices
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        brush = QBrush(QColor(0, 122, 204))
        painter.setBrush(brush)

        for point in self.polygon_points:
            painter.drawEllipse(point, 4, 4)

    def _draw_circle_preview(self, painter: QPainter):
        """Draw circle preview."""
        from PyQt6.QtGui import QPen, QColor
        from math import sqrt

        # Draw center point
        pen = QPen(QColor(0, 122, 204), 2)
        painter.setPen(pen)

        brush = painter.brush()
        brush.setStyle(Qt.BrushStyle.NoBrush)
        painter.setBrush(brush)

        # Draw center marker
        painter.drawEllipse(self.circle_center, 4, 4)

        # Draw circle if radius point is set
        if self.circle_radius_point:
            dx = self.circle_radius_point.x() - self.circle_center.x()
            dy = self.circle_radius_point.y() - self.circle_center.y()
            radius = int(sqrt(dx * dx + dy * dy))

            painter.drawEllipse(self.circle_center, radius, radius)

    def _draw_finalized_circle(self, painter: QPainter):
        """Draw finalized circle selection."""
        if not self.finalized_circle_center or self.finalized_circle_radius <= 0:
            return

        from PyQt6.QtGui import QPen, QColor

        # Draw circle outline
        pen = QPen(QColor(0, 122, 204), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        brush = painter.brush()
        brush.setStyle(Qt.BrushStyle.NoBrush)
        painter.setBrush(brush)

        radius = int(self.finalized_circle_radius)
        painter.drawEllipse(self.finalized_circle_center, radius, radius)

        # Draw center point
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawEllipse(self.finalized_circle_center, 3, 3)

    def _draw_finalized_polygon(self, painter: QPainter):
        """Draw finalized polygon selection."""
        if len(self.finalized_polygon_points) < 3:
            return

        from PyQt6.QtGui import QPen, QBrush, QColor

        # Draw polygon edges
        pen = QPen(QColor(0, 122, 204), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        # Draw all edges
        for i in range(len(self.finalized_polygon_points)):
            start = self.finalized_polygon_points[i]
            end = self.finalized_polygon_points[
                (i + 1) % len(self.finalized_polygon_points)
            ]
            painter.drawLine(start, end)

        # Draw vertices
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        brush = QBrush(QColor(0, 122, 204))
        painter.setBrush(brush)

        for point in self.finalized_polygon_points:
            painter.drawEllipse(point, 3, 3)

    def _draw_selection_handles(self, painter: QPainter):
        """Draw resize handles on selection corners and edges."""
        from PyQt6.QtGui import QPen, QBrush, QColor

        sel_rect = self._selection_to_view_rect()
        if not sel_rect:
            return

        x, y, w, h = sel_rect.x(), sel_rect.y(), sel_rect.width(), sel_rect.height()
        hs = self.handle_size

        # Handle positions
        handles = [
            (x - hs // 2, y - hs // 2),  # top-left
            (x + w // 2 - hs // 2, y - hs // 2),  # top
            (x + w - hs // 2, y - hs // 2),  # top-right
            (x + w - hs // 2, y + h // 2 - hs // 2),  # right
            (x + w - hs // 2, y + h - hs // 2),  # bottom-right
            (x + w // 2 - hs // 2, y + h - hs // 2),  # bottom
            (x - hs // 2, y + h - hs // 2),  # bottom-left
            (x - hs // 2, y + h // 2 - hs // 2),  # left
        ]

        # Draw selection outline
        pen = QPen(QColor(0, 122, 204), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(sel_rect)

        # Draw handles
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setWidth(1)
        painter.setPen(pen)
        brush = QBrush(QColor(255, 255, 255))
        painter.setBrush(brush)

        for hx, hy in handles:
            painter.drawRect(hx, hy, hs, hs)


class SpriteForgeWindow(QMainWindow):
    """Main Window für SpriteForge Application (PyQt6)"""

    # Custom Signals
    imageLoaded = pyqtSignal(str)  # file_path

    def __init__(self):
        super().__init__()
        logger.info("Initializing SpriteForgeWindow (PyQt6)")

        # State
        self.processor: Optional[ImageProcessor] = None
        self.current_image_path: Optional[str] = None
        self.selection: tuple = (0, 0, 0, 0)  # x, y, width, height
        self.zoom_level = 1.0
        self.grid_visible = False
        self.is_selection_mode = True  # Selection vs Pan mode

        # Managers
        self.recent_files = RecentFiles()
        self.undo_manager = UndoRedoManager()

        # Canvas
        self.canvas: Optional[ImageCanvas] = None

        # Overlay state
        self.unique_colors_overlay_active = False
        self.transparent_sprite_overlay_active = False
        self.unique_colors_overlay_image: Optional[PILImage.Image] = None
        self.transparent_sprite_overlay_image: Optional[PILImage.Image] = None

        # UI Actions (store for enable/disable)
        self.zoom_in_action: Optional[QAction] = None
        self.zoom_out_action: Optional[QAction] = None
        self.zoom_reset_action: Optional[QAction] = None
        self.zoom_fit_action: Optional[QAction] = None
        self.grid_action: Optional[QAction] = None
        self.copy_coords_action: Optional[QAction] = None

        # Setup UI
        self.init_ui()

        logger.info("SpriteForgeWindow initialized")

    def init_ui(self):
        """Initialisiert die UI-Komponenten."""
        self.setWindowTitle("SpriteForge - Forge Your Sprites")
        self.setGeometry(100, 100, 1400, 900)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left side: Image Canvas (QGraphicsView)
        self.canvas = ImageCanvas(self)
        # Connect canvas signals
        self.canvas.selectionChanged.connect(self.on_selection_changed)
        self.canvas.mouseMoved.connect(self.on_canvas_mouse_moved)
        # Set size policy to expand
        from PyQt6.QtWidgets import QSizePolicy

        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.canvas)

        # Right side: Control Panel with Scroll Area
        control_panel_container = QWidget()
        control_panel_container.setMinimumWidth(370)
        control_panel_container.setMaximumWidth(370)
        control_panel_container.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        control_container_layout = QVBoxLayout(control_panel_container)
        control_container_layout.setContentsMargins(0, 0, 0, 0)
        control_container_layout.setSpacing(0)

        # Scroll Area für Control Panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(
            "QScrollArea { border: none; background-color: #1e1e1e; }"
            "QScrollBar:vertical { background: #2d2d2d; width: 12px; border-radius: 6px; }"
            "QScrollBar::handle:vertical { background: #555; border-radius: 6px; min-height: 20px; }"
            "QScrollBar::handle:vertical:hover { background: #666; }"
        )

        control_panel = QWidget()
        control_panel.setStyleSheet(
            "background-color: #1e1e1e; border-left: 1px solid #555;"
        )
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(8)

        # Global button style
        button_style = (
            "QPushButton {"
            "  background-color: #2d2d2d;"
            "  color: white;"
            "  border: 1px solid #555;"
            "  border-radius: 4px;"
            "  padding: 8px 12px;"
            "  font-size: 13px;"
            "  min-height: 32px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #3d3d3d;"
            "  border: 1px solid #007acc;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #1a1a1a;"
            "}"
            "QPushButton:disabled {"
            "  background-color: #1a1a1a;"
            "  color: #666;"
            "  border: 1px solid #333;"
            "}"
        )

        # Title
        title_label = QLabel("SpriteForge")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #007acc; padding: 5px 0;"
        )
        control_layout.addWidget(title_label)

        # Separator
        separator1 = QLabel()
        separator1.setFixedHeight(1)
        separator1.setStyleSheet("background-color: #555;")
        control_layout.addWidget(separator1)
        control_layout.addSpacing(5)

        # Selection Controls
        selection_label = QLabel("Selection:")
        selection_label.setStyleSheet(
            "color: #fff; font-size: 14px; font-weight: bold; padding: 5px 0;"
        )
        control_layout.addWidget(selection_label)

        # Mode Toggle
        self.mode_btn = QPushButton("Mode: Selection")
        self.mode_btn.clicked.connect(self.toggle_mode)
        self.mode_btn.setStyleSheet(
            button_style
            + "QPushButton { background-color: #007acc; font-weight: bold; }"
        )
        self.mode_btn.setMinimumHeight(36)
        control_layout.addWidget(self.mode_btn)

        # Selection Tools
        tools_label = QLabel("Selection Tool:")
        tools_label.setStyleSheet(
            "color: #fff; font-size: 13px; font-weight: bold; padding: 5px 0; margin-top: 5px;"
        )
        control_layout.addWidget(tools_label)

        # Tool Buttons
        tool_button_layout = QHBoxLayout()
        tool_button_layout.setSpacing(5)

        tool_button_style = (
            "QPushButton {"
            "  background-color: #2d2d2d;"
            "  color: white;"
            "  border: 2px solid #555;"
            "  border-radius: 4px;"
            "  font-size: 20px;"
            "  min-width: 45px;"
            "  min-height: 45px;"
            "}"
            "QPushButton:hover { background-color: #3d3d3d; border-color: #007acc; }"
            "QPushButton:pressed { background-color: #1a1a1a; }"
        )

        self.rect_tool_btn = QPushButton("□")
        self.rect_tool_btn.setToolTip("Rectangle Selection")
        self.rect_tool_btn.clicked.connect(
            lambda: self.on_tool_changed(SelectionTool.RECTANGLE)
        )
        self.rect_tool_btn.setStyleSheet(
            tool_button_style
            + "QPushButton { background-color: #007acc; border-color: #007acc; }"
        )
        tool_button_layout.addWidget(self.rect_tool_btn)

        self.polygon_tool_btn = QPushButton("⬡")
        self.polygon_tool_btn.setToolTip(
            "Polygon Selection (Click points, Enter to complete)"
        )
        self.polygon_tool_btn.clicked.connect(
            lambda: self.on_tool_changed(SelectionTool.POLYGON)
        )
        self.polygon_tool_btn.setStyleSheet(tool_button_style)
        tool_button_layout.addWidget(self.polygon_tool_btn)

        self.circle_tool_btn = QPushButton("○")
        self.circle_tool_btn.setToolTip("Circle Selection (Two-point: center + radius)")
        self.circle_tool_btn.clicked.connect(
            lambda: self.on_tool_changed(SelectionTool.CIRCLE)
        )
        self.circle_tool_btn.setStyleSheet(tool_button_style)
        tool_button_layout.addWidget(self.circle_tool_btn)

        control_layout.addLayout(tool_button_layout)

        # Tool help text
        self.tool_help_label = QLabel("Rectangle: Click and drag")
        self.tool_help_label.setStyleSheet(
            "color: #888; font-size: 11px; padding: 3px 0;"
        )
        self.tool_help_label.setWordWrap(True)
        control_layout.addWidget(self.tool_help_label)

        control_layout.addSpacing(8)

        # Clear Selection
        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.clicked.connect(self.on_clear_selection)
        self.clear_selection_btn.setEnabled(False)
        self.clear_selection_btn.setStyleSheet(button_style)
        control_layout.addWidget(self.clear_selection_btn)

        # Copy Region Coordinates
        self.copy_coords_btn = QPushButton("📋 Copy Coordinates")
        self.copy_coords_btn.clicked.connect(self.copy_region_coordinates)
        self.copy_coords_btn.setEnabled(False)
        self.copy_coords_btn.setToolTip(
            "Copy region coordinates to clipboard (y1, x1, y2, x2)"
        )
        self.copy_coords_btn.setStyleSheet(button_style)
        control_layout.addWidget(self.copy_coords_btn)

        # Undo/Redo
        undo_redo_layout = QHBoxLayout()
        undo_redo_layout.setSpacing(5)
        self.undo_btn = QPushButton("↶ Undo")
        self.undo_btn.clicked.connect(self.on_undo)
        self.undo_btn.setEnabled(False)
        self.undo_btn.setStyleSheet(button_style)
        undo_redo_layout.addWidget(self.undo_btn)

        self.redo_btn = QPushButton("↷ Redo")
        self.redo_btn.clicked.connect(self.on_redo)
        self.redo_btn.setEnabled(False)
        self.redo_btn.setStyleSheet(button_style)
        undo_redo_layout.addWidget(self.redo_btn)
        control_layout.addLayout(undo_redo_layout)

        control_layout.addSpacing(10)

        # Separator
        separator2 = QLabel()
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background-color: #555;")
        control_layout.addWidget(separator2)
        control_layout.addSpacing(5)

        # Zoom Controls
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet(
            "color: #fff; font-size: 14px; font-weight: bold; padding: 5px 0;"
        )
        control_layout.addWidget(zoom_label)

        zoom_buttons_layout = QHBoxLayout()
        zoom_buttons_layout.setSpacing(5)

        zoom_in_btn = QPushButton("＋ Zoom In")
        zoom_in_btn.clicked.connect(self.on_zoom_in)
        zoom_in_btn.setStyleSheet(button_style)
        zoom_buttons_layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("－ Zoom Out")
        zoom_out_btn.clicked.connect(self.on_zoom_out)
        zoom_out_btn.setStyleSheet(button_style)
        zoom_buttons_layout.addWidget(zoom_out_btn)
        control_layout.addLayout(zoom_buttons_layout)

        # Zoom Slider
        slider_layout = QHBoxLayout()
        slider_layout.setSpacing(5)
        slider_label = QLabel("Level:")
        slider_label.setStyleSheet("color: #ccc; font-size: 11px;")
        slider_label.setMinimumWidth(40)
        slider_layout.addWidget(slider_label)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)  # 10% = 0.1x
        self.zoom_slider.setMaximum(1000)  # 1000% = 10x
        self.zoom_slider.setValue(100)  # 100% = 1.0x
        self.zoom_slider.setStyleSheet(
            "QSlider::groove:horizontal { background: #2d2d2d; height: 6px; border-radius: 3px; }"
            "QSlider::handle:horizontal { background: #007acc; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }"
            "QSlider::handle:horizontal:hover { background: #1a8ad6; }"
        )
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        slider_layout.addWidget(self.zoom_slider)
        control_layout.addLayout(slider_layout)

        zoom_buttons_layout2 = QHBoxLayout()
        zoom_buttons_layout2.setSpacing(5)

        zoom_reset_btn = QPushButton("1:1 (100%)")
        zoom_reset_btn.clicked.connect(self.on_zoom_reset)
        zoom_reset_btn.setStyleSheet(button_style)
        zoom_buttons_layout2.addWidget(zoom_reset_btn)

        zoom_fit_btn = QPushButton("↕ Fit Window")
        zoom_fit_btn.clicked.connect(self.on_zoom_fit)
        zoom_fit_btn.setStyleSheet(button_style)
        zoom_buttons_layout2.addWidget(zoom_fit_btn)
        control_layout.addLayout(zoom_buttons_layout2)

        self.zoom_label_display = QLabel("Zoom: 100%")
        self.zoom_label_display.setStyleSheet(
            "color: #888; font-size: 11px; padding: 3px 0;"
        )
        control_layout.addWidget(self.zoom_label_display)

        control_layout.addSpacing(10)

        # Separator
        separator3 = QLabel()
        separator3.setFixedHeight(1)
        separator3.setStyleSheet("background-color: #555;")
        control_layout.addWidget(separator3)
        control_layout.addSpacing(5)

        # Region Info Panel
        region_info_label = QLabel("Region Info:")
        region_info_label.setStyleSheet(
            "color: #fff; font-size: 14px; font-weight: bold; padding: 5px 0;"
        )
        control_layout.addWidget(region_info_label)

        region_info_widget = QWidget()
        region_info_widget.setStyleSheet(
            "background-color: #2d2d2d; padding: 10px; border-radius: 4px; border: 1px solid #555;"
        )
        region_info_layout = QVBoxLayout(region_info_widget)
        region_info_layout.setSpacing(4)
        region_info_layout.setContentsMargins(8, 8, 8, 8)

        self.region_x_label = QLabel("x: -")
        self.region_x_label.setStyleSheet(
            "color: #ccc; font-size: 12px; font-family: monospace;"
        )
        region_info_layout.addWidget(self.region_x_label)

        self.region_y_label = QLabel("y: -")
        self.region_y_label.setStyleSheet(
            "color: #ccc; font-size: 12px; font-family: monospace;"
        )
        region_info_layout.addWidget(self.region_y_label)

        self.region_sel_x_label = QLabel("sel x: -")
        self.region_sel_x_label.setStyleSheet(
            "color: #ccc; font-size: 12px; font-family: monospace;"
        )
        region_info_layout.addWidget(self.region_sel_x_label)

        self.region_sel_y_label = QLabel("sel y: -")
        self.region_sel_y_label.setStyleSheet(
            "color: #ccc; font-size: 12px; font-family: monospace;"
        )
        region_info_layout.addWidget(self.region_sel_y_label)

        self.region_sel_width_label = QLabel("sel width: -")
        self.region_sel_width_label.setStyleSheet(
            "color: #ccc; font-size: 12px; font-family: monospace;"
        )
        region_info_layout.addWidget(self.region_sel_width_label)

        self.region_sel_height_label = QLabel("sel height: -")
        self.region_sel_height_label.setStyleSheet(
            "color: #ccc; font-size: 12px; font-family: monospace;"
        )
        region_info_layout.addWidget(self.region_sel_height_label)

        control_layout.addWidget(region_info_widget)

        control_layout.addSpacing(10)

        # Separator
        separator4 = QLabel()
        separator4.setFixedHeight(1)
        separator4.setStyleSheet("background-color: #555;")
        control_layout.addWidget(separator4)
        control_layout.addSpacing(5)

        # File Operations
        file_ops_label = QLabel("File Operations:")
        file_ops_label.setStyleSheet(
            "color: #fff; font-size: 14px; font-weight: bold; padding: 5px 0;"
        )
        control_layout.addWidget(file_ops_label)

        load_btn = QPushButton("📁 Load Image")
        load_btn.clicked.connect(self.open_file_dialog)
        load_btn.setStyleSheet(
            button_style
            + "QPushButton { background-color: #0a5a0a; font-weight: bold; }"
        )
        load_btn.setMinimumHeight(40)
        control_layout.addWidget(load_btn)

        self.export_btn = QPushButton("💾 Export Sprite")
        self.export_btn.clicked.connect(self.export_sprite)
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet(button_style)
        control_layout.addWidget(self.export_btn)

        control_layout.addSpacing(10)

        # SpriteX Advanced Export Features
        export_advanced_label = QLabel("Advanced Export:")
        export_advanced_label.setStyleSheet(
            "color: #fff; font-size: 13px; font-weight: bold; padding: 5px 0;"
        )
        control_layout.addWidget(export_advanced_label)

        self.unique_colors_btn = QPushButton("🎨 Extract Unique Colors")
        self.unique_colors_btn.clicked.connect(self.extract_unique_colors)
        self.unique_colors_btn.setEnabled(False)
        self.unique_colors_btn.setToolTip("Find colors only in selection (n×1 image)")
        self.unique_colors_btn.setStyleSheet(button_style)
        control_layout.addWidget(self.unique_colors_btn)

        self.unique_sprite_btn = QPushButton("✨ Extract Unique Sprite")
        self.unique_sprite_btn.clicked.connect(self.extract_unique_sprite)
        self.unique_sprite_btn.setEnabled(False)
        self.unique_sprite_btn.setToolTip("Sprite with only unique colors visible")
        self.unique_sprite_btn.setStyleSheet(button_style)
        control_layout.addWidget(self.unique_sprite_btn)

        self.transparent_sprite_btn = QPushButton("🎬 Extract from Sequence")
        self.transparent_sprite_btn.clicked.connect(self.extract_transparent_sprite)
        self.transparent_sprite_btn.setEnabled(False)
        self.transparent_sprite_btn.setToolTip(
            "Compare all images in folder (differing pixels → transparent)"
        )
        self.transparent_sprite_btn.setStyleSheet(button_style)
        control_layout.addWidget(self.transparent_sprite_btn)

        control_layout.addSpacing(10)

        # Overlay Panel
        overlay_label = QLabel("Overlay:")
        overlay_label.setStyleSheet(
            "color: #fff; font-size: 13px; font-weight: bold; padding: 5px 0;"
        )
        control_layout.addWidget(overlay_label)

        overlay_widget = QWidget()
        overlay_widget.setStyleSheet(
            "background-color: #2d2d2d; padding: 8px; border-radius: 4px; border: 1px solid #555;"
        )
        overlay_layout = QVBoxLayout(overlay_widget)
        overlay_layout.setSpacing(6)
        overlay_layout.setContentsMargins(8, 8, 8, 8)

        self.overlay_unique_colors_btn = QPushButton("🎨 Unique Colors")
        self.overlay_unique_colors_btn.setCheckable(True)
        self.overlay_unique_colors_btn.clicked.connect(
            self.toggle_unique_colors_overlay
        )
        self.overlay_unique_colors_btn.setEnabled(False)
        self.overlay_unique_colors_btn.setStyleSheet(
            "QPushButton { background-color: #2d5016; color: white; padding: 8px; font-size: 12px; border-radius: 4px; min-height: 32px; }"
            "QPushButton:hover { background-color: #3d6026; }"
            "QPushButton:checked { background-color: #3d8c1f; font-weight: bold; }"
            "QPushButton:disabled { background-color: #1a1a1a; color: #666; }"
        )
        overlay_layout.addWidget(self.overlay_unique_colors_btn)

        self.overlay_transparent_sprite_btn = QPushButton("🎬 Transparent Sprite")
        self.overlay_transparent_sprite_btn.setCheckable(True)
        self.overlay_transparent_sprite_btn.clicked.connect(
            self.toggle_transparent_sprite_overlay
        )
        self.overlay_transparent_sprite_btn.setEnabled(False)
        self.overlay_transparent_sprite_btn.setStyleSheet(
            "QPushButton { background-color: #4a4a4a; color: white; padding: 8px; font-size: 12px; border-radius: 4px; min-height: 32px; }"
            "QPushButton:hover { background-color: #5a5a5a; }"
            "QPushButton:checked { background-color: #6a6a6a; font-weight: bold; }"
            "QPushButton:disabled { background-color: #1a1a1a; color: #666; }"
        )
        overlay_layout.addWidget(self.overlay_transparent_sprite_btn)

        control_layout.addWidget(overlay_widget)

        control_layout.addSpacing(10)

        # Separator
        separator5 = QLabel()
        separator5.setFixedHeight(1)
        separator5.setStyleSheet("background-color: #555;")
        control_layout.addWidget(separator5)
        control_layout.addSpacing(5)

        # Image Operations
        image_ops_label = QLabel("Image Operations:")
        image_ops_label.setStyleSheet(
            "color: #fff; font-size: 13px; font-weight: bold; padding: 5px 0;"
        )
        control_layout.addWidget(image_ops_label)

        self.crop_btn = QPushButton("✂ Crop to Selection")
        self.crop_btn.clicked.connect(self.crop_to_selection)
        self.crop_btn.setEnabled(False)
        self.crop_btn.setToolTip("Crop image to selection (DESTRUCTIVE)")
        self.crop_btn.setStyleSheet(button_style)
        control_layout.addWidget(self.crop_btn)

        control_layout.addStretch()

        # Separator
        separator_bottom = QLabel()
        separator_bottom.setFixedHeight(1)
        separator_bottom.setStyleSheet("background-color: #555;")
        control_layout.addWidget(separator_bottom)
        control_layout.addSpacing(5)

        # Info Labels
        self.info_label = QLabel("No image loaded")
        self.info_label.setStyleSheet(
            "color: #ccc; font-size: 12px; padding: 5px; background-color: #2d2d2d; border-radius: 4px;"
        )
        self.info_label.setWordWrap(True)
        control_layout.addWidget(self.info_label)

        # Set control panel into scroll area
        scroll_area.setWidget(control_panel)
        control_container_layout.addWidget(scroll_area)

        # Add control panel container to main layout
        main_layout.addWidget(control_panel_container)

        # Create Menu Bar
        self.create_menu_bar()

        # Create Status Bar
        statusbar = self.statusBar()
        statusbar.setStyleSheet(
            "QStatusBar { background-color: #2d2d2d; color: #ccc; font-size: 12px; padding: 4px; border-top: 1px solid #555; }"
        )
        statusbar.showMessage("Ready")
        logger.info("UI initialized")

    def create_menu_bar(self):
        """Erstellt die Menu Bar."""
        menubar = self.menuBar()
        menubar.setStyleSheet(
            "QMenuBar { background-color: #2d2d2d; color: #fff; font-size: 13px; padding: 4px; }"
            "QMenuBar::item { background-color: transparent; padding: 6px 12px; }"
            "QMenuBar::item:selected { background-color: #007acc; }"
            "QMenu { background-color: #2d2d2d; color: #fff; border: 1px solid #555; }"
            "QMenu::item { padding: 8px 30px 8px 20px; }"
            "QMenu::item:selected { background-color: #007acc; }"
            "QMenu::separator { height: 1px; background-color: #555; margin: 4px 0; }"
        )

        # File Menu
        file_menu = menubar.addMenu("&File")

        # Open Action
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open an image file")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        # Recent Files Submenu
        self.recent_menu = QMenu("Recent Files", self)
        file_menu.addMenu(self.recent_menu)
        self.update_recent_menu()

        file_menu.addSeparator()

        # Export Action
        self.export_action = QAction("&Export Sprite...", self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.setStatusTip("Export selected region as sprite")
        self.export_action.triggered.connect(self.export_sprite)
        self.export_action.setEnabled(False)
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()

        # Exit Action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu (Undo/Redo - Phase 3)
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setEnabled(False)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setEnabled(False)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Copy Action
        self.copy_action = QAction("&Copy Selection", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.setStatusTip("Copy selected region to clipboard")
        self.copy_action.triggered.connect(self.copy_selection)
        self.copy_action.setEnabled(False)
        edit_menu.addAction(self.copy_action)

        # Copy Region Coordinates Action
        self.copy_coords_action = QAction("Copy Region &Coordinates", self)
        self.copy_coords_action.setShortcut("Ctrl+Shift+C")
        self.copy_coords_action.setStatusTip(
            "Copy region coordinates to clipboard (y1, x1, y2, x2)"
        )
        self.copy_coords_action.triggered.connect(self.copy_region_coordinates)
        self.copy_coords_action.setEnabled(False)
        edit_menu.addAction(self.copy_coords_action)

        # Save Action
        self.save_action = QAction("&Save Selection...", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Save selected region")
        self.save_action.triggered.connect(self.save_selection)
        self.save_action.setEnabled(False)
        edit_menu.addAction(self.save_action)

        # View Menu (Zoom/Grid - Phase 2)
        view_menu = menubar.addMenu("&View")

        self.zoom_in_action = QAction("Zoom &In", self)
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.triggered.connect(self.on_zoom_in)
        self.zoom_in_action.setEnabled(False)
        view_menu.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction("Zoom &Out", self)
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.triggered.connect(self.on_zoom_out)
        self.zoom_out_action.setEnabled(False)
        view_menu.addAction(self.zoom_out_action)

        self.zoom_reset_action = QAction("Zoom &Reset (1:1)", self)
        self.zoom_reset_action.setShortcut("Ctrl+0")
        self.zoom_reset_action.triggered.connect(self.on_zoom_reset)
        self.zoom_reset_action.setEnabled(False)
        view_menu.addAction(self.zoom_reset_action)

        self.zoom_fit_action = QAction("&Fit to Window", self)
        self.zoom_fit_action.setShortcut("Ctrl+9")
        self.zoom_fit_action.triggered.connect(self.on_zoom_fit)
        self.zoom_fit_action.setEnabled(False)
        view_menu.addAction(self.zoom_fit_action)

        view_menu.addSeparator()

        self.grid_action = QAction("Toggle &Grid", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setShortcut("Ctrl+G")
        self.grid_action.toggled.connect(self.toggle_grid)
        self.grid_action.setEnabled(False)
        view_menu.addAction(self.grid_action)

        logger.info("Menu bar created")

    def update_recent_menu(self):
        """Aktualisiert das Recent Files Menu."""
        self.recent_menu.clear()

        recent_files = self.recent_files.get_files()
        if recent_files:
            for file_path in recent_files:
                action = QAction(Path(file_path).name, self)
                action.setStatusTip(file_path)
                action.triggered.connect(
                    lambda checked, path=file_path: self.load_image(path)
                )
                self.recent_menu.addAction(action)
        else:
            no_recent_action = QAction("No recent files", self)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)

    def open_file_dialog(self):
        """Öffnet File Dialog zum Laden eines Bildes."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
        )

        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path: str):
        """Lädt ein Bild."""
        try:
            logger.info(f"Loading image: {file_path}")

            # Create ImageProcessor
            self.processor = ImageProcessor(file_path)
            self.current_image_path = file_path

            # Get PIL Image and convert to QImage
            pil_image = self.processor.image

            # Convert PIL Image to QImage
            if pil_image.mode == "RGB":
                qimage = QImage(
                    pil_image.tobytes(),
                    pil_image.width,
                    pil_image.height,
                    pil_image.width * 3,
                    QImage.Format.Format_RGB888,
                )
            elif pil_image.mode == "RGBA":
                qimage = QImage(
                    pil_image.tobytes(),
                    pil_image.width,
                    pil_image.height,
                    pil_image.width * 4,
                    QImage.Format.Format_RGBA8888,
                )
            else:
                # Convert to RGBA
                pil_image = pil_image.convert("RGBA")
                qimage = QImage(
                    pil_image.tobytes(),
                    pil_image.width,
                    pil_image.height,
                    pil_image.width * 4,
                    QImage.Format.Format_RGBA8888,
                )

            # Set image in canvas
            self.canvas.set_image(qimage)

            # Enable zoom actions
            self.zoom_in_action.setEnabled(True)
            self.zoom_out_action.setEnabled(True)
            self.zoom_reset_action.setEnabled(True)
            self.zoom_fit_action.setEnabled(True)
            self.grid_action.setEnabled(True)

            # Add to recent files
            self.recent_files.add(file_path)
            self.update_recent_menu()

            # Update UI
            width, height = self.processor.get_image_size()
            self.info_label.setText(
                f"Image: {Path(file_path).name}\nSize: {width}x{height}px"
            )

            # Update zoom display
            self.update_zoom_display()

            # Emit signal
            self.imageLoaded.emit(file_path)

            # Status message
            self.statusBar().showMessage(f"Loaded: {Path(file_path).name}", 3000)

            logger.info("Image loaded successfully")

        except Exception as e:
            logger.error(f"Error loading image: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load image:\n{str(e)}")

    def on_zoom_in(self):
        """Zoom in handler."""
        if self.canvas:
            self.canvas.zoom_in()
            self.update_zoom_display()

    def on_zoom_out(self):
        """Zoom out handler."""
        if self.canvas:
            self.canvas.zoom_out()
            self.update_zoom_display()

    def on_zoom_reset(self):
        """Zoom reset handler."""
        if self.canvas:
            self.canvas.zoom_reset()
            self.update_zoom_display()

    def on_zoom_fit(self):
        """Zoom fit handler."""
        if self.canvas:
            self.canvas.zoom_fit()
            self.update_zoom_display()

    def update_zoom_display(self):
        """Updates zoom level display."""
        if self.canvas:
            zoom = self.canvas.get_zoom_level()
            self.zoom_label_display.setText(f"Zoom: {zoom * 100:.0f}%")

            # Update slider without triggering signal
            if hasattr(self, "zoom_slider"):
                self.zoom_slider.blockSignals(True)
                self.zoom_slider.setValue(int(zoom * 100))
                self.zoom_slider.blockSignals(False)

    def on_zoom_slider_changed(self, value: int):
        """Handle zoom slider value change."""
        if not self.canvas or not self.canvas.pixmap_item:
            return

        target_zoom = value / 100.0  # Convert percentage to factor
        current_zoom = self.canvas.get_zoom_level()

        if abs(target_zoom - current_zoom) < 0.01:
            return

        # Calculate scale factor
        scale_factor = target_zoom / current_zoom

        # Apply scaling
        self.canvas.scale(scale_factor, scale_factor)
        self.canvas.current_zoom = target_zoom

        # Update display
        self.zoom_label_display.setText(f"Zoom: {target_zoom * 100:.0f}%")

    def toggle_mode(self):
        """Toggle between selection and pan mode."""
        self.is_selection_mode = not self.is_selection_mode
        self.canvas.set_selection_mode(self.is_selection_mode)

        if self.is_selection_mode:
            self.mode_btn.setText("Mode: Selection")
            self.statusBar().showMessage("Selection mode active", 2000)
        else:
            self.mode_btn.setText("Mode: Pan")
            self.statusBar().showMessage("Pan mode active", 2000)

    def toggle_grid(self, checked: bool):
        """Toggle grid overlay."""
        if self.canvas:
            self.canvas.set_grid_visible(checked)
            self.grid_visible = checked

            if checked:
                self.statusBar().showMessage(
                    f"Grid enabled ({self.canvas.grid_size}px)", 2000
                )
            else:
                self.statusBar().showMessage("Grid disabled", 2000)

    def on_tool_changed(self, tool: SelectionTool):
        """Handle tool selection change."""
        if self.canvas:
            self.canvas.set_tool(tool)

            # Update button styles
            active_style = "background-color: #007acc; color: white; font-size: 16px; padding: 8px;"
            inactive_style = (
                "background-color: #333; color: white; font-size: 16px; padding: 8px;"
            )

            self.rect_tool_btn.setStyleSheet(
                active_style if tool == SelectionTool.RECTANGLE else inactive_style
            )
            self.polygon_tool_btn.setStyleSheet(
                active_style if tool == SelectionTool.POLYGON else inactive_style
            )
            self.circle_tool_btn.setStyleSheet(
                active_style if tool == SelectionTool.CIRCLE else inactive_style
            )

            # Update help text
            if tool == SelectionTool.RECTANGLE:
                self.tool_help_label.setText("Rectangle: Click and drag")
            elif tool == SelectionTool.POLYGON:
                self.tool_help_label.setText(
                    "Polygon: Click points, Enter to complete, ESC to cancel"
                )
            elif tool == SelectionTool.CIRCLE:
                self.tool_help_label.setText(
                    "Circle: Click center, then click/drag radius point"
                )

            self.statusBar().showMessage(
                f"Tool changed to: {tool.value.capitalize()}", 2000
            )
            logger.info(f"Tool changed to: {tool.value}")

    def on_selection_changed(self, selection: tuple):
        """Handle selection changes from canvas."""
        if selection:
            x, y, w, h = selection
            # Store current selection
            self.selection = selection

            # Add to undo history (skip if applying from history)
            if not self.canvas._is_applying_history:
                self.undo_manager.push(selection)

            # Update UI
            self.info_label.setText(
                f"{self.info_label.text()}\nSelection: {w}x{h}px at ({x}, {y})"
            )

            # Enable buttons
            self.clear_selection_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            self.export_action.setEnabled(True)
            self.copy_action.setEnabled(True)
            self.copy_coords_btn.setEnabled(True)
            if self.copy_coords_action:
                self.copy_coords_action.setEnabled(True)
            self.save_action.setEnabled(True)
            self.unique_colors_btn.setEnabled(True)
            self.unique_sprite_btn.setEnabled(True)
            self.transparent_sprite_btn.setEnabled(True)
            self.crop_btn.setEnabled(True)
            self.undo_btn.setEnabled(self.undo_manager.can_undo())
            self.redo_btn.setEnabled(False)

            # Enable overlay buttons if image is loaded
            self.overlay_unique_colors_btn.setEnabled(True)
            self.overlay_transparent_sprite_btn.setEnabled(True)

            # Update region info
            self.region_sel_x_label.setText(f"sel x: {x}")
            self.region_sel_y_label.setText(f"sel y: {y}")
            self.region_sel_width_label.setText(f"sel width: {w}")
            self.region_sel_height_label.setText(f"sel height: {h}")

            self.statusBar().showMessage(f"Selected: {w}x{h}px at ({x}, {y})", 3000)
        else:
            # Selection cleared
            self.selection = (0, 0, 0, 0)
            self.clear_selection_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            self.export_action.setEnabled(False)
            self.copy_action.setEnabled(False)
            self.copy_coords_btn.setEnabled(False)
            if self.copy_coords_action:
                self.copy_coords_action.setEnabled(False)
            self.save_action.setEnabled(False)
            self.unique_colors_btn.setEnabled(False)
            self.unique_sprite_btn.setEnabled(False)
            self.transparent_sprite_btn.setEnabled(False)
            self.crop_btn.setEnabled(False)

            # Clear region info selection details
            self.region_sel_x_label.setText("sel x: -")
            self.region_sel_y_label.setText("sel y: -")
            self.region_sel_width_label.setText("sel width: -")
            self.region_sel_height_label.setText("sel height: -")

    def on_canvas_mouse_moved(self, x: int, y: int):
        """Handle mouse movement on canvas."""
        # Update region info with current mouse position
        self.region_x_label.setText(f"x: {x}")
        self.region_y_label.setText(f"y: {y}")

    def toggle_unique_colors_overlay(self, checked: bool):
        """Toggle unique colors overlay on canvas."""
        if checked:
            if (
                not self.processor
                or not self.selection
                or self.selection == (0, 0, 0, 0)
            ):
                QMessageBox.warning(
                    self, "No Selection", "Please select a region first."
                )
                self.overlay_unique_colors_btn.setChecked(False)
                return

            # Create unique colors overlay
            try:
                progress = QProgressDialog(
                    "Creating unique colors overlay...", "Cancel", 0, 100, self
                )
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(500)

                def update_progress(percent):
                    progress.setValue(int(percent))
                    QApplication.processEvents()
                    if progress.wasCanceled():
                        raise InterruptedError("Operation cancelled by user")

                unique_sprite = self.processor.create_unique_sprite(
                    self.selection, progress_callback=update_progress
                )

                progress.close()

                if unique_sprite:
                    self.unique_colors_overlay_image = unique_sprite
                    self.unique_colors_overlay_active = True
                    self.canvas.set_overlay(unique_sprite, self.selection)
                    self.statusBar().showMessage("Unique colors overlay active", 2000)
                else:
                    QMessageBox.information(
                        self, "No Unique Colors", "No unique colors found in selection."
                    )
                    self.overlay_unique_colors_btn.setChecked(False)
            except InterruptedError:
                self.overlay_unique_colors_btn.setChecked(False)
                self.statusBar().showMessage("Cancelled", 2000)
            except Exception as e:
                logger.error(f"Overlay creation failed: {e}", exc_info=True)
                QMessageBox.critical(
                    self, "Error", f"Failed to create overlay:\\n{str(e)}"
                )
                self.overlay_unique_colors_btn.setChecked(False)
        else:
            # Remove overlay
            self.unique_colors_overlay_active = False
            self.unique_colors_overlay_image = None
            self.canvas.clear_overlay()
            self.statusBar().showMessage("Unique colors overlay removed", 2000)

    def toggle_transparent_sprite_overlay(self, checked: bool):
        """Toggle transparent sprite overlay on canvas."""
        if checked:
            if (
                not self.processor
                or not self.selection
                or self.selection == (0, 0, 0, 0)
            ):
                QMessageBox.warning(
                    self, "No Selection", "Please select a region first."
                )
                self.overlay_transparent_sprite_btn.setChecked(False)
                return

            # Check for multiple images
            directory = Path(self.processor.image_path).parent
            png_files = list(directory.glob("*.png"))

            if len(png_files) < 2:
                QMessageBox.warning(
                    self,
                    "Not Enough Images",
                    f"Found only {len(png_files)} PNG image(s).\\nThis overlay requires at least 2 images.",
                )
                self.overlay_transparent_sprite_btn.setChecked(False)
                return

            # Create transparent sprite overlay
            try:
                progress = QProgressDialog(
                    f"Creating transparent sprite overlay from {len(png_files)} images...",
                    "Cancel",
                    0,
                    100,
                    self,
                )
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)

                def update_progress(percent):
                    progress.setValue(int(percent))
                    QApplication.processEvents()
                    if progress.wasCanceled():
                        raise InterruptedError("Operation cancelled by user")

                transparent_sprite = self.processor.extract_transparent_sprite(
                    self.selection, progress_callback=update_progress
                )

                progress.close()

                if transparent_sprite:
                    self.transparent_sprite_overlay_image = transparent_sprite
                    self.transparent_sprite_overlay_active = True
                    self.canvas.set_overlay(transparent_sprite, self.selection)
                    self.statusBar().showMessage(
                        f"Transparent sprite overlay active ({len(png_files)} images)",
                        2000,
                    )

                    # Update button style
                    self.overlay_transparent_sprite_btn.setStyleSheet(
                        "background-color: #6a6a6a; color: white; padding: 5px; font-size: 11px; font-weight: bold;"
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "Could not create transparent sprite."
                    )
                    self.overlay_transparent_sprite_btn.setChecked(False)
            except InterruptedError:
                self.overlay_transparent_sprite_btn.setChecked(False)
                self.statusBar().showMessage("Cancelled", 2000)
            except Exception as e:
                logger.error(f"Overlay creation failed: {e}", exc_info=True)
                QMessageBox.critical(
                    self, "Error", f"Failed to create overlay:\\n{str(e)}"
                )
                self.overlay_transparent_sprite_btn.setChecked(False)
        else:
            # Remove overlay
            self.transparent_sprite_overlay_active = False
            self.transparent_sprite_overlay_image = None
            self.canvas.clear_overlay()
            self.statusBar().showMessage("Transparent sprite overlay removed", 2000)

    def on_clear_selection(self):
        """Clear current selection."""
        if self.canvas:
            self.canvas.clear_selection()
            self.statusBar().showMessage("Selection cleared", 2000)

    def on_undo(self):
        """Undo last selection."""
        selection = self.undo_manager.undo()
        if selection:
            # Apply selection to canvas visually
            self.canvas._is_applying_history = True
            self.canvas.apply_selection(selection)
            self.canvas._is_applying_history = False

            # Update internal state
            self.selection = selection
            x, y, w, h = selection
            self.statusBar().showMessage(f"Undo: {w}x{h}px at ({x}, {y})", 2000)

            # Update UI
            self.info_label.setText(
                f"{self.info_label.text().split('Selection')[0]}Selection: {w}x{h}px at ({x}, {y})"
            )

        self.undo_btn.setEnabled(self.undo_manager.can_undo())
        self.redo_btn.setEnabled(self.undo_manager.can_redo())

    def on_redo(self):
        """Redo last undone selection."""
        selection = self.undo_manager.redo()
        if selection:
            # Apply selection to canvas visually
            self.canvas._is_applying_history = True
            self.canvas.apply_selection(selection)
            self.canvas._is_applying_history = False

            # Update internal state
            self.selection = selection
            x, y, w, h = selection
            self.statusBar().showMessage(f"Redo: {w}x{h}px at ({x}, {y})", 2000)

            # Update UI
            self.info_label.setText(
                f"{self.info_label.text().split('Selection')[0]}Selection: {w}x{h}px at ({x}, {y})"
            )

        self.undo_btn.setEnabled(self.undo_manager.can_undo())
        self.redo_btn.setEnabled(self.undo_manager.can_redo())

    def export_sprite(self):
        """Export selected region as sprite."""
        if not self.processor or not self.selection or self.selection == (0, 0, 0, 0):
            QMessageBox.warning(
                self, "No Selection", "Please select a region to export."
            )
            return

        x, y, w, h = self.selection
        if w == 0 or h == 0:
            QMessageBox.warning(
                self, "Invalid Selection", "Selection has zero width or height."
            )
            return

        # Get save file path
        default_name = f"sprite_{w}x{h}.png"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Sprite",
            default_name,
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*.*)",
        )

        if not file_path:
            return  # User cancelled

        try:
            logger.info(f"Exporting sprite: {self.selection} to {file_path}")

            # Get sprite image from processor
            sprite_image = self.processor.get_selection_image(self.selection)

            if sprite_image:
                # Determine format from file extension
                save_format = None
                if file_path.lower().endswith((".jpg", ".jpeg")):
                    save_format = "JPEG"
                    # Convert RGBA to RGB for JPEG
                    if sprite_image.mode == "RGBA":
                        # Create white background
                        rgb_image = PILImage.new(
                            "RGB", sprite_image.size, (255, 255, 255)
                        )
                        rgb_image.paste(
                            sprite_image,
                            mask=sprite_image.split()[3]
                            if len(sprite_image.split()) > 3
                            else None,
                        )
                        sprite_image = rgb_image
                elif file_path.lower().endswith(".png"):
                    save_format = "PNG"

                # Save the sprite
                sprite_image.save(file_path, format=save_format)

                self.statusBar().showMessage(
                    f"Sprite exported: {Path(file_path).name}", 5000
                )

                QMessageBox.information(
                    self,
                    "Export Success",
                    f"Sprite exported successfully to:\n{file_path}",
                )

                logger.info(f"Sprite exported successfully: {file_path}")
            else:
                raise Exception("Failed to get selection image")

        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export sprite:\n{str(e)}"
            )

    def copy_selection(self):
        """Copy selected region to clipboard."""
        if not self.processor or not self.selection or self.selection == (0, 0, 0, 0):
            self.statusBar().showMessage("No selection to copy", 2000)
            return

        try:
            # Get sprite image from processor
            sprite_image = self.processor.get_selection_image(self.selection)

            if sprite_image:
                # Convert PIL Image to QImage
                if sprite_image.mode == "RGB":
                    qimage = QImage(
                        sprite_image.tobytes(),
                        sprite_image.width,
                        sprite_image.height,
                        sprite_image.width * 3,
                        QImage.Format.Format_RGB888,
                    )
                elif sprite_image.mode == "RGBA":
                    qimage = QImage(
                        sprite_image.tobytes(),
                        sprite_image.width,
                        sprite_image.height,
                        sprite_image.width * 4,
                        QImage.Format.Format_RGBA8888,
                    )
                else:
                    sprite_image = sprite_image.convert("RGBA")
                    qimage = QImage(
                        sprite_image.tobytes(),
                        sprite_image.width,
                        sprite_image.height,
                        sprite_image.width * 4,
                        QImage.Format.Format_RGBA8888,
                    )

                # Copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setImage(qimage)

                self.statusBar().showMessage(
                    f"Selection copied to clipboard ({self.selection[2]}x{self.selection[3]}px)",
                    3000,
                )
                logger.info("Selection copied to clipboard")
            else:
                raise Exception("Failed to get selection image")

        except Exception as e:
            logger.error(f"Copy failed: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Copy Failed", f"Failed to copy selection:\n{str(e)}"
            )

    def copy_region_coordinates(self):
        """Copy region coordinates to clipboard in (y1, x1, y2, x2) format."""
        if not self.selection or self.selection == (0, 0, 0, 0):
            self.statusBar().showMessage("No selection to copy", 2000)
            return

        try:
            x, y, w, h = self.selection
            # Calculate coordinates: (y1, x1, y2, x2)
            y1 = y
            x1 = x
            y2 = y + h
            x2 = x + w

            # Format as in original SpriteX
            coords_text = f"({y1}, {x1}, {y2}, {x2})"

            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(coords_text)

            self.statusBar().showMessage(
                f"Coordinates copied: {coords_text}",
                3000,
            )
            logger.info(f"Region coordinates copied to clipboard: {coords_text}")

        except Exception as e:
            logger.error(f"Copy coordinates failed: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Copy Failed", f"Failed to copy coordinates:\n{str(e)}"
            )

    def save_selection(self):
        """Save selected region (similar to export but with Ctrl+S)."""
        # Just call export_sprite for now
        self.export_sprite()

    def extract_unique_colors(self):
        """Extract unique colors from selection (SpriteX feature)."""
        if not self.processor or not self.selection or self.selection == (0, 0, 0, 0):
            QMessageBox.warning(self, "No Selection", "Please select a region first.")
            return

        try:
            # Create progress dialog
            progress = QProgressDialog(
                "Finding unique colors...", "Cancel", 0, 100, self
            )
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(500)

            # Define progress callback
            def update_progress(percent):
                progress.setValue(int(percent))
                QApplication.processEvents()
                if progress.wasCanceled():
                    raise InterruptedError("Operation cancelled by user")

            logger.info(f"Extracting unique colors from selection: {self.selection}")

            # Find unique colors
            unique_colors = self.processor.find_unique_colors(
                self.selection, progress_callback=update_progress
            )

            progress.close()

            if not unique_colors:
                QMessageBox.information(
                    self,
                    "No Unique Colors",
                    "No unique colors found in selection.\nAll colors also appear outside the selection.",
                )
                return

            # Create unique colors image (n x 1)
            colors_image = self.processor.create_unique_colors_image(unique_colors)

            # Show preview dialog
            info_text = f"Found {len(unique_colors)} unique colors (n×1 px bar)"
            preview = PreviewDialog(
                self, "Unique Colors Preview", colors_image, info_text
            )

            result = preview.exec()

            if result == QDialog.DialogCode.Accepted and preview.save_confirmed:
                # User confirmed save
                output_path = self.processor.save_unique_colors(unique_colors, "unique")

                self.statusBar().showMessage(
                    f"Unique colors extracted: {len(unique_colors)} colors", 5000
                )

                QMessageBox.information(
                    self,
                    "Unique Colors Extracted",
                    f"Found {len(unique_colors)} unique colors.\n\nSaved to:\n{output_path}",
                )

                logger.info(
                    f"Extracted {len(unique_colors)} unique colors to {output_path}"
                )
            else:
                self.statusBar().showMessage("Cancelled", 2000)

        except InterruptedError:
            logger.info("Unique colors extraction cancelled by user")
            self.statusBar().showMessage("Operation cancelled", 2000)
        except Exception as e:
            logger.error(f"Unique colors extraction failed: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Extraction Failed",
                f"Failed to extract unique colors:\n{str(e)}",
            )

    def extract_unique_sprite(self):
        """Extract sprite with only unique colors (SpriteX feature)."""
        if not self.processor or not self.selection or self.selection == (0, 0, 0, 0):
            QMessageBox.warning(self, "No Selection", "Please select a region first.")
            return

        try:
            # Create progress dialog
            progress = QProgressDialog(
                "Creating unique sprite...", "Cancel", 0, 100, self
            )
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(500)

            # Define progress callback
            def update_progress(percent):
                progress.setValue(int(percent))
                QApplication.processEvents()
                if progress.wasCanceled():
                    raise InterruptedError("Operation cancelled by user")

            logger.info(f"Creating unique sprite from selection: {self.selection}")

            # Create unique sprite
            unique_sprite = self.processor.create_unique_sprite(
                self.selection, progress_callback=update_progress
            )

            progress.close()

            if not unique_sprite:
                QMessageBox.information(
                    self,
                    "No Unique Colors",
                    "No unique colors found in selection.\nCannot create unique sprite.",
                )
                return

            # Show preview dialog
            info_text = (
                "Sprite with transparent background (only unique colors visible)"
            )
            preview = PreviewDialog(
                self, "Unique Sprite Preview", unique_sprite, info_text
            )

            result = preview.exec()

            if result == QDialog.DialogCode.Accepted and preview.save_confirmed:
                # User confirmed save
                default_name = f"highlight_{self.selection[2]}x{self.selection[3]}.png"
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Unique Sprite",
                    default_name,
                    "PNG Images (*.png)",
                )

                if file_path:
                    unique_sprite.save(file_path, format="PNG")

                    self.statusBar().showMessage("Unique sprite extracted", 5000)

                    QMessageBox.information(
                        self,
                        "Unique Sprite Created",
                        f"Unique sprite saved with transparent background.\n\nSaved to:\n{file_path}",
                    )

                    logger.info(f"Unique sprite saved to {file_path}")
                else:
                    self.statusBar().showMessage("Cancelled", 2000)
            else:
                self.statusBar().showMessage("Cancelled", 2000)

        except InterruptedError:
            logger.info("Unique sprite extraction cancelled by user")
            self.statusBar().showMessage("Operation cancelled", 2000)
        except Exception as e:
            logger.error(f"Unique sprite extraction failed: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Extraction Failed",
                f"Failed to extract unique sprite:\n{str(e)}",
            )

    def extract_transparent_sprite(self):
        """Extract sprite from multiple images (SpriteX feature)."""
        if not self.processor or not self.selection or self.selection == (0, 0, 0, 0):
            QMessageBox.warning(self, "No Selection", "Please select a region first.")
            return

        try:
            # Count PNG files in directory
            directory = Path(self.processor.image_path).parent
            png_files = list(directory.glob("*.png"))
            num_files = len(png_files)

            if num_files < 2:
                QMessageBox.warning(
                    self,
                    "Not Enough Images",
                    f"Found only {num_files} PNG image(s) in folder.\n\nThis feature requires at least 2 images in the same folder.",
                )
                return

            # Confirm with user
            reply = QMessageBox.question(
                self,
                "Extract from Sequence",
                f"Found {num_files} PNG images in folder.\n\nThis will compare the same region across all images.\nPixels that differ will become transparent.\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Create progress dialog
            progress = QProgressDialog(
                f"Processing {num_files} images...", "Cancel", 0, 100, self
            )
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)

            # Define progress callback
            def update_progress(percent):
                progress.setValue(int(percent))
                QApplication.processEvents()
                if progress.wasCanceled():
                    raise InterruptedError("Operation cancelled by user")

            logger.info(
                f"Extracting transparent sprite from {num_files} images: {self.selection}"
            )

            # Extract transparent sprite
            transparent_sprite = self.processor.extract_transparent_sprite(
                self.selection, progress_callback=update_progress
            )

            progress.close()

            if not transparent_sprite:
                QMessageBox.warning(
                    self,
                    "Extraction Failed",
                    "Could not extract transparent sprite.\nMake sure all images have the same dimensions.",
                )
                return

            # Show preview dialog
            info_text = (
                f"Processed {num_files} images. Differing pixels are transparent."
            )
            preview = PreviewDialog(
                self, "Transparent Sprite Preview", transparent_sprite, info_text
            )

            result = preview.exec()

            if result == QDialog.DialogCode.Accepted and preview.save_confirmed:
                # User confirmed save
                default_name = f"extracted_{self.selection[2]}x{self.selection[3]}.png"
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Transparent Sprite",
                    default_name,
                    "PNG Images (*.png)",
                )

                if file_path:
                    transparent_sprite.save(file_path, format="PNG")

                    self.statusBar().showMessage(
                        f"Transparent sprite extracted from {num_files} images", 5000
                    )

                    QMessageBox.information(
                        self,
                        "Transparent Sprite Created",
                        f"Processed {num_files} images.\n\nDiffering pixels are now transparent.\n\nSaved to:\n{file_path}",
                    )

                    logger.info(
                        f"Transparent sprite saved to {file_path} ({num_files} images processed)"
                    )
                else:
                    self.statusBar().showMessage("Cancelled", 2000)
            else:
                self.statusBar().showMessage("Cancelled", 2000)

        except InterruptedError:
            logger.info("Transparent sprite extraction cancelled by user")
            self.statusBar().showMessage("Operation cancelled", 2000)
        except Exception as e:
            logger.error(f"Transparent sprite extraction failed: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Extraction Failed",
                f"Failed to extract transparent sprite:\n{str(e)}",
            )

    def crop_to_selection(self):
        """Crop image to current selection (DESTRUCTIVE)."""
        if not self.processor or not self.selection or self.selection == (0, 0, 0, 0):
            QMessageBox.warning(self, "No Selection", "Please select a region first.")
            return

        x, y, w, h = self.selection

        # Confirm with user (destructive operation!)
        reply = QMessageBox.question(
            self,
            "Crop Image",
            f"This will permanently crop the image to the selected region ({w}x{h}px).\n\nOriginal image size: {self.processor.get_image_size()[0]}x{self.processor.get_image_size()[1]}px\n\nThis cannot be undone. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            logger.info(f"Cropping image to selection: {self.selection}")

            # Crop in processor
            self.processor.crop_to_selection(self.selection)

            # Reload image in canvas
            new_size = self.processor.get_image_size()
            logger.info(f"Image cropped to {new_size[0]}x{new_size[1]}px")

            # Convert PIL Image to QImage
            pil_image = self.processor.image
            if pil_image.mode == "RGB":
                qimage = QImage(
                    pil_image.tobytes(),
                    pil_image.width,
                    pil_image.height,
                    pil_image.width * 3,
                    QImage.Format.Format_RGB888,
                )
            elif pil_image.mode == "RGBA":
                qimage = QImage(
                    pil_image.tobytes(),
                    pil_image.width,
                    pil_image.height,
                    pil_image.width * 4,
                    QImage.Format.Format_RGBA8888,
                )
            else:
                pil_image = pil_image.convert("RGBA")
                qimage = QImage(
                    pil_image.tobytes(),
                    pil_image.width,
                    pil_image.height,
                    pil_image.width * 4,
                    QImage.Format.Format_RGBA8888,
                )

            # Update canvas
            self.canvas.set_image(qimage)
            self.canvas.clear_selection()

            # Update info
            self.info_label.setText(
                f"Image: {new_size[0]}x{new_size[1]}px\nPath: {self.processor.image_path.name}"
            )

            self.statusBar().showMessage(
                f"Image cropped to {new_size[0]}x{new_size[1]}px", 5000
            )

            QMessageBox.information(
                self,
                "Crop Successful",
                f"Image cropped to {new_size[0]}x{new_size[1]}px.\n\nNote: This change is only in memory.\nUse File > Export to save.",
            )

        except Exception as e:
            logger.error(f"Crop failed: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Crop Failed", f"Failed to crop image:\n{str(e)}"
            )

    def show_message(self, message: str, success: bool = True):
        """Zeigt eine Statusmeldung."""
        if success:
            self.statusBar().showMessage(message, 3000)
        else:
            QMessageBox.warning(self, "Warning", message)

    def closeEvent(self, event):
        """Überschreibt Close Event."""
        logger.info("Application closing")
        event.accept()


def main():
    """Application Entry Point."""
    # Setup Logger
    setup_logger()
    logger.info("Starting SpriteForge Application (PyQt6)")

    # Create Application
    app = QApplication(sys.argv)
    app.setApplicationName("SpriteForge")
    app.setOrganizationName("merhovon")

    # Set Dark Theme
    app.setStyle("Fusion")

    # Create and show main window
    window = SpriteForgeWindow()
    window.showMaximized()  # Start in fullscreen/maximized mode

    logger.info("Application started")

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
