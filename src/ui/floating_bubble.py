"""
Floating Voxel Logo Trigger widget.
Subtle frosted glass circular badge displaying the Voxel microphone logo.
Appears smoothly with fade-in near selected text without stealing window focus.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QCursor, QMouseEvent,
    QRadialGradient, QEnterEvent
)

from src.config import BUBBLE_SIZE, BUBBLE_TIMEOUT_SECONDS, THEME
from assets.icons import get_selection_bubble_pixmap


class FloatingBubble(QWidget):
    """
    Subtle floating Voxel logo badge appearing near selected text.
    Fades in smoothly, responds to hover with a glowing aura, and triggers playback on click.
    """
    clicked = pyqtSignal(str)  # (selected_text)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_text: str = ""
        self.is_hovered: bool = False

        # Non-activating floating tool window
        self.setWindowFlags(
            Qt.WindowType.ToolTip |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(BUBBLE_SIZE, BUBBLE_SIZE)

        # Load the official selection bubble PNG logo
        self.bubble_pixmap = get_selection_bubble_pixmap(BUBBLE_SIZE)

        # Smooth Fade In / Fade Out Animations
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(160)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Auto-hide Timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setInterval(int(BUBBLE_TIMEOUT_SECONDS * 1000))
        self.hide_timer.timeout.connect(self.fade_out)

    def show_at(self, text: str, cursor_x: int, cursor_y: int):
        """Positions the floating logo near cursor and smoothly fades in."""
        self.selected_text = text

        offset_x = 10
        offset_y = -BUBBLE_SIZE - 10

        target_x = cursor_x + offset_x
        target_y = cursor_y + offset_y

        screen = self.screen() or self.parent().screen() if self.parent() else None
        if screen:
            geo = screen.availableGeometry()
            if target_y < geo.top() + 8:
                target_y = cursor_y + 22
            target_x = max(geo.left() + 8, min(geo.right() - BUBBLE_SIZE - 8, target_x))
            target_y = max(geo.top() + 8, min(geo.bottom() - BUBBLE_SIZE - 8, target_y))

        self.move(int(target_x), int(target_y))

        self.fade_anim.stop()
        self.setWindowOpacity(0.0)
        self.show()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
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
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.hide_timer.start()
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            text = self.selected_text
            self.fade_out()
            self.clicked.emit(text)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        s = float(self.width())
        cx, cy = s / 2.0, s / 2.0

        # Ambient glow aura on hover
        if self.is_hovered:
            aura = QRadialGradient(cx, cy, s / 2.0)
            aura.setColorAt(0.0, QColor(99, 102, 241, 110))
            aura.setColorAt(0.70, QColor(0, 140, 255, 50))
            aura.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(aura))
            painter.drawEllipse(QRectF(0, 0, s, s))

        # Render the official selection bubble PNG logo
        if hasattr(self, "bubble_pixmap") and not self.bubble_pixmap.isNull():
            pad = 1.0 if self.is_hovered else 2.0
            rect = QRectF(pad, pad, s - 2 * pad, s - 2 * pad)
            painter.drawPixmap(rect.toRect(), self.bubble_pixmap)

        painter.end()
