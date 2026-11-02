"""
Floating Voxel Dual-Action Trigger Capsule widget.
Appears near selected text in Google Docs, PDFs, Word, Presentations, or browsers.
Features:
- Left Action: Voxel Logo badge to read selected text immediately.
- Right Action: Document icon (📑) to automatically read the entire document / presentation.
- Right-click glass context menu for quick controls, open file, and settings.
- Hover pre-fetching for instant 0ms latency playback.
"""
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QCursor, QMouseEvent,
    QRadialGradient, QLinearGradient, QAction, QEnterEvent, QGuiApplication
)

from src.config import BUBBLE_TIMEOUT_SECONDS, THEME, FONT_FAMILY
from src.utils.settings import settings_db
from assets.icons import get_selection_bubble_pixmap, get_selection_bubble_doc_pixmap

CAPSULE_WIDTH = 78
CAPSULE_HEIGHT = 38
DIVIDER_X = 39


class FloatingBubble(QWidget):
    """
    Ergonomic frosted glass floating dual-action capsule.
    Provides instant one-click reading of either the selected text or the full document/presentation.
    """
    clicked = pyqtSignal(str)              # (selected_text)
    read_document_requested = pyqtSignal(str)  # Read entire document / presentation
    open_file_requested = pyqtSignal()      # Open local document file
    settings_requested = pyqtSignal()       # Open settings dialog
    about_requested = pyqtSignal()          # Open about dialog
    quit_requested = pyqtSignal()           # Quit Voxel
    hovered = pyqtSignal(str)               # Pre-fetch notification

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_text: str = ""
        self.is_hovered: bool = False
        self.hover_side: str = ""  # 'left' (selection) or 'right' (document)
        self.theme_mode: str = "light_glass"  # Default light glass

        self.capsule_width: int = CAPSULE_WIDTH
        self.capsule_height: int = CAPSULE_HEIGHT
        self.divider_x: int = DIVIDER_X
        self.icon_size: int = 26
        self.corner_radius_mode: str = "Medium"
        self.bubble_style: str = "Frosted Glass"
        self.target_opacity: float = 0.90

        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Smooth Fade In / Fade Out Animations
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(160)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Auto-hide Timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setInterval(int(BUBBLE_TIMEOUT_SECONDS * 1000))
        self.hide_timer.timeout.connect(self.fade_out)

        self.apply_settings()

    def apply_settings(self):
        """Loads and applies all appearance, size, corner radius, distance padding and transparency settings."""
        size_str = str(settings_db.get("bubble_size", "Large")).lower()
        if "small" in size_str or size_str == "1" or "dot" in size_str:
            self.size_mode = "small"
            self.capsule_width = 28
            self.capsule_height = 28
            self.divider_x = 0
            self.icon_size = 18
        elif "medium" in size_str or size_str == "2":
            self.size_mode = "medium"
            self.capsule_width = 62
            self.capsule_height = 32
            self.divider_x = 31
            self.icon_size = 22
        else:  # Large / default (standard dual capsule)
            self.size_mode = "large"
            self.capsule_width = 82
            self.capsule_height = 40
            self.divider_x = 41
            self.icon_size = 26

        self.setFixedSize(self.capsule_width, self.capsule_height)
        self.bubble_pixmap = get_selection_bubble_pixmap(self.icon_size)
        self.doc_pixmap = get_selection_bubble_doc_pixmap(self.icon_size)
        self.distance_padding = int(settings_db.get("bubble_distance", 28))

        self.corner_radius_mode = str(settings_db.get("bubble_corner_radius", "Medium"))
        self.bubble_style = str(settings_db.get("bubble_appearance", "Frosted Glass"))
        trans_val = int(settings_db.get("bubble_transparency", 90))
        self.target_opacity = max(0.2, min(1.0, trans_val / 100.0))
        self.update()

    def set_theme_mode(self, mode: str):
        """Sets light_glass or dark_glass theme for the floating bubble."""
        self.theme_mode = mode
        self.update()

    def show_at(self, text: str, cursor_x: int, cursor_y: int, start_x: int = None, start_y: int = None):
        """Positions the floating capsule near cursor and fades in with generous distance padding."""
        self.apply_settings()
        self.selected_text = text
        self.hover_side = ""

        pad = getattr(self, "distance_padding", 28)

        # Smart multi-line detection: if selection spans multiple lines,
        # place above the top line near left margin rather than inside the text.
        if start_y is not None and abs(start_y - cursor_y) > 15:
            top_y = min(start_y, cursor_y)
            bottom_y = max(start_y, cursor_y)
            target_y = top_y - self.capsule_height - pad
            target_x = min(start_x, cursor_x) + 10
        else:
            top_y = cursor_y
            bottom_y = cursor_y
            target_y = cursor_y - self.capsule_height - pad
            target_x = cursor_x + 14

        screen = QGuiApplication.screenAt(QPoint(cursor_x, cursor_y)) or QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            if target_y < geo.top() + 8:
                target_y = bottom_y + pad + 8
            target_x = max(geo.left() + 8, min(geo.right() - self.capsule_width - 8, target_x))
            target_y = max(geo.top() + 8, min(geo.bottom() - self.capsule_height - 8, target_y))

        self.move(int(target_x), int(target_y))

        self.fade_anim.stop()
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(self.target_opacity)
        self.fade_anim.start()

        self.hide_timer.start()

    def fade_out(self):
        """Smoothly fades out and hides."""
        self.hide_timer.stop()
        self.fade_anim.stop()
        self.fade_anim.setStartValue(self.windowOpacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self._on_fade_out_finished)
        self.fade_anim.start()

    def _on_fade_out_finished(self):
        try:
            self.fade_anim.finished.disconnect(self._on_fade_out_finished)
        except Exception:
            pass
        self.hide()

    def enterEvent(self, event: QEnterEvent):
        self.is_hovered = True
        self.hide_timer.stop()  # Keep open while user hovers
        if self.selected_text:
            self.hovered.emit(self.selected_text)
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.hover_side = ""
        self.hide_timer.start()
        self.update()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if getattr(self, "size_mode", "large") == "small":
            if self.hover_side != "center":
                self.hover_side = "center"
                self.setToolTip("Read Selected Text (Left Click) • Document Reader & Options (Right Click)")
                self.update()
            super().mouseMoveEvent(event)
            return

        pos_x = event.position().x()
        new_side = "left" if pos_x < self.divider_x else "right"
        if new_side != self.hover_side:
            self.hover_side = new_side
            if new_side == "left":
                self.setToolTip("Read Selected Text (Left Click)")
            else:
                self.setToolTip("Read Entire Document / Presentation / PDF (Click)")
            self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            fallback = self.selected_text
            self.fade_out()
            if getattr(self, "size_mode", "large") == "small":
                self.clicked.emit(fallback)
            else:
                pos_x = event.position().x()
                if pos_x < self.divider_x:
                    self.clicked.emit(fallback)
                else:
                    self.read_document_requested.emit(fallback)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def _show_context_menu(self, global_pos: QPoint):
        self.hide_timer.stop()
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #171A29;
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 10px;
                padding: 6px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                min-width: 200px;
                padding: 8px 16px;
                border-radius: 6px;
                margin: 2px 2px;
                font-weight: 500;
            }
            QMenu::item:selected {
                background-color: #7C3AED;
                color: #FFFFFF;
                font-weight: 600;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(255, 255, 255, 0.10);
                margin: 4px 8px;
            }
        """)

        act_settings = menu.addAction("⚙️  Preferences...")
        act_settings.triggered.connect(lambda: (self.fade_out(), self.settings_requested.emit()))

        act_about = menu.addAction("ℹ️  About Voxel...")
        act_about.triggered.connect(lambda: (self.fade_out(), self.about_requested.emit()))

        menu.addSeparator()

        act_quit = menu.addAction("Quit Voxel")
        act_quit.triggered.connect(lambda: (self.fade_out(), self.quit_requested.emit()))

        menu.exec(global_pos)
        self.hide_timer.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = float(self.width())
        h = float(self.height())

        # Determine dynamic corner radius based on settings
        if getattr(self, "size_mode", "large") == "small":
            r = h / 2.0  # Perfect circle dot
        else:
            c_mode = getattr(self, "corner_radius_mode", "Medium")
            if c_mode == "Square":
                r = 4.0
            elif c_mode == "Round":
                r = h / 2.0
            else:  # Medium
                r = 10.0

        # 1. Outer ambient glow on hover
        if self.is_hovered:
            glow = QRadialGradient(w / 2.0, h / 2.0, w / 1.6)
            glow.setColorAt(0.0, QColor(0, 132, 255, 90))
            glow.setColorAt(0.7, QColor(124, 58, 237, 45))
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow))
            painter.drawRoundedRect(QRectF(0, 0, w, h), r, r)

        # 2. Dynamic Capsule Background & Style
        capsule_rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)
        is_light = (self.theme_mode == "light_glass")
        b_style = getattr(self, "bubble_style", "Frosted Glass")

        if b_style == "Transparent":
            bg_col = QColor(255, 255, 255, 90 if is_light else 60)
            painter.setBrush(QBrush(bg_col))
            dash_col = QColor(0, 132, 255, 220) if self.is_hovered else (QColor(148, 163, 184, 180) if is_light else QColor(255, 255, 255, 75))
            painter.setPen(QPen(dash_col, 1.2, Qt.PenStyle.DashLine))
            painter.drawRoundedRect(capsule_rect, r, r)
        elif b_style == "Minimal":
            bg_col = QColor(248, 250, 252, 240) if is_light else QColor(15, 23, 42, 240)
            painter.setBrush(QBrush(bg_col))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(capsule_rect, r, r)
        elif b_style == "Default":
            bg_col = QColor(255, 255, 255, 250) if is_light else QColor(30, 41, 59, 250)
            border_col = QColor(0, 132, 255, 220) if self.is_hovered else (QColor(203, 213, 225, 240) if is_light else QColor(71, 85, 105, 240))
            painter.setBrush(QBrush(bg_col))
            painter.setPen(QPen(border_col, 1.2))
            painter.drawRoundedRect(capsule_rect, r, r)
        else:
            # Frosted Glass (Default)
            grad = QLinearGradient(0, 0, 0, h)
            if is_light:
                if self.is_hovered:
                    grad.setColorAt(0.0, QColor(255, 255, 255, 255))
                    grad.setColorAt(1.0, QColor(240, 246, 255, 255))
                else:
                    grad.setColorAt(0.0, QColor(255, 255, 255, 255))
                    grad.setColorAt(1.0, QColor(244, 247, 253, 255))
                border_col = QColor(0, 132, 255, 220) if self.is_hovered else QColor(148, 163, 184, 180)
            else:
                if self.is_hovered:
                    grad.setColorAt(0.0, QColor(36, 42, 65, 235))
                    grad.setColorAt(1.0, QColor(20, 24, 38, 245))
                else:
                    grad.setColorAt(0.0, QColor(26, 31, 48, 220))
                    grad.setColorAt(1.0, QColor(14, 17, 28, 235))
                border_col = QColor(0, 132, 255, 170) if self.is_hovered else QColor(255, 255, 255, 55)

            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(border_col, 1.2))
            painter.drawRoundedRect(capsule_rect, r, r)

            # Top Specular Glass Reflection Sheen
            sheen_rect = QRectF(r / 2.0, 2.0, max(2.0, w - r), h * 0.42)
            sheen = QLinearGradient(0, 2.0, 0, h * 0.45)
            sheen.setColorAt(0.0, QColor(255, 255, 255, 90 if is_light else 75))
            sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(sheen))
            painter.drawRoundedRect(sheen_rect, 3.0, 3.0)

        # If Small Dot, render centered logo and finish (no divider, no doc button)
        if getattr(self, "size_mode", "large") == "small":
            icon_sz = getattr(self, "icon_size", 18)
            if hasattr(self, "bubble_pixmap") and not self.bubble_pixmap.isNull():
                lx = (w - icon_sz) / 2.0
                ly = (h - icon_sz) / 2.0
                painter.drawPixmap(int(lx), int(ly), icon_sz, icon_sz, self.bubble_pixmap)
            painter.end()
            return

        # 3. Subtle Vertical Divider separating Selection vs Document actions
        div_col = QColor(148, 163, 184, 80) if is_light else QColor(255, 255, 255, 45)
        painter.setPen(QPen(div_col, 1.0))
        painter.drawLine(int(self.divider_x), 6, int(self.divider_x), int(h - 6))

        # 4. Left Highlight on Hover (Read Selection)
        if self.is_hovered and self.hover_side == "left":
            left_rect = QRectF(2.0, 2.0, self.divider_x - 3.0, h - 4.0)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 132, 255, 30 if is_light else 40)))
            painter.drawRoundedRect(left_rect, r, r)

        # 5. Right Highlight on Hover (Read Document)
        elif self.is_hovered and self.hover_side == "right":
            right_rect = QRectF(self.divider_x + 1.0, 2.0, w - self.divider_x - 3.0, h - 4.0)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(124, 58, 237, 35 if is_light else 50)))
            painter.drawRoundedRect(right_rect, r, r)

        # 6. Render Voxel Mic Logo on Left
        icon_sz = getattr(self, "icon_size", 26)
        if hasattr(self, "bubble_pixmap") and not self.bubble_pixmap.isNull():
            lx = (self.divider_x - icon_sz) / 2.0
            ly = (h - icon_sz) / 2.0
            painter.drawPixmap(int(lx), int(ly), icon_sz, icon_sz, self.bubble_pixmap)

        # 7. Render Official Circular Document Icon on Right
        if hasattr(self, "doc_pixmap") and not self.doc_pixmap.isNull():
            rx = self.divider_x + ((w - self.divider_x) - icon_sz) / 2.0
            ry = (h - icon_sz) / 2.0
            painter.drawPixmap(int(rx), int(ry), icon_sz, icon_sz, self.doc_pixmap)
        else:
            rx = self.divider_x + (w - self.divider_x) / 2.0
            ry = h / 2.0
            doc_color = QColor("#0284C7") if (self.is_hovered and self.hover_side == "right") else (QColor("#334155") if is_light else QColor("#E2E8F0"))
            dw, dh = 13.0, 16.0
            dx = rx - dw / 2.0
            dy = ry - dh / 2.0
            painter.setPen(QPen(doc_color, 1.4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(dx, dy, dw, dh), 2.0, 2.0)
            painter.drawLine(int(dx + 3), int(dy + 5), int(dx + dw - 3), int(dy + 5))
            painter.drawLine(int(dx + 3), int(dy + 8), int(dx + dw - 3), int(dy + 8))
            painter.drawLine(int(dx + 3), int(dy + 11), int(dx + dw - 5), int(dy + 11))

        painter.end()
