"""
Floating Speaker Bubble widget.
A tiny, elegant frosted glass circular button with a minimalist speaker icon.
Smoothly fades in near selected text without obstructing the user.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QCursor, QMouseEvent, QLinearGradient
)

from src.config import BUBBLE_SIZE, BUBBLE_TIMEOUT_SECONDS, THEME
from assets.icons import create_speaker_icon


class FloatingBubble(QWidget):
    """
    Subtle 24px floating frosted glass speaker trigger appearing near selected text.
    """
    clicked = pyqtSignal(str, QPoint)  # (selected_text, bubble_center_pos)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_text: str = ""
        self.is_hovered: bool = False

        # Frameless, stays on top, tool-tip type (doesn't steal focus)
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

        # Pre-render speaker icon sized for tiny 24px bubble
        icon_dim = int(BUBBLE_SIZE * 0.62)  # ~15px
        self.speaker_icon = create_speaker_icon(size=icon_dim, color="#FFFFFF", waves=2)

        # Fade animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(160)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Auto-hide timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setInterval(int(BUBBLE_TIMEOUT_SECONDS * 1000))
        self.hide_timer.timeout.connect(self.fade_out)

    def show_at(self, text: str, cursor_x: int, cursor_y: int):
        """
        Positions the bubble near the mouse cursor and smoothly fades in.
        """
        self.selected_text = text

        offset_x = 8
        offset_y = -BUBBLE_SIZE - 6

        target_x = cursor_x + offset_x
        target_y = cursor_y + offset_y

        screen = self.screen() or self.parent().screen() if self.parent() else None
        if screen:
            geo = screen.availableGeometry()
            if target_y < geo.top() + 6:
                target_y = cursor_y + 18
            target_x = max(geo.left() + 6, min(geo.right() - BUBBLE_SIZE - 6, target_x))
            target_y = max(geo.top() + 6, min(geo.bottom() - BUBBLE_SIZE - 6, target_y))

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)

        # Translucent Frosted Glass Effect with subtle lighting gradient
        grad = QLinearGradient(0, 0, 0, h)
        if self.is_hovered:
            grad.setColorAt(0.0, QColor(60, 68, 100, 245))
            grad.setColorAt(1.0, QColor(32, 38, 58, 235))
            border_pen = QPen(QColor(96, 165, 250, 220), 1.0)
        else:
            grad.setColorAt(0.0, QColor(42, 48, 72, 230))
            grad.setColorAt(1.0, QColor(20, 24, 38, 215))
            border_pen = QPen(QColor(255, 255, 255, 75), 1.0)

        painter.setBrush(QBrush(grad))
        painter.setPen(border_pen)
        painter.drawEllipse(rect)

        # Draw centered speaker icon
        icon_dim = int(w * 0.62)
        ix = int((w - icon_dim) / 2)
        iy = int((h - icon_dim) / 2)
        self.speaker_icon.paint(painter, ix, iy, icon_dim, icon_dim)

        painter.end()

    def enterEvent(self, event):
        self.is_hovered = True
        self.hide_timer.stop()
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
            center = self.mapToGlobal(QPoint(self.width() // 2, self.height() // 2))
            self.hide_timer.stop()
            self.hide()
            self.clicked.emit(text, center)
        super().mousePressEvent(event)
