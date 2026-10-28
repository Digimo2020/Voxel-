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
from src.ui.voxel_logo_widget import VoxelLogoWidget


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

        # Embedded vector Voxel logo
        logo_dim = int(BUBBLE_SIZE * 0.76)
        self.logo = VoxelLogoWidget(size=logo_dim, animated=False, parent=self)
        offset = (BUBBLE_SIZE - logo_dim) // 2
        self.logo.move(offset, offset)
        self.logo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

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
        self.logo.start_voice_animation()
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.logo.stop_voice_animation()
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

        s = float(self.width())
        cx, cy = s / 2.0, s / 2.0

        # Outer glowing halo when hovered
        if self.is_hovered:
            glow = QRadialGradient(cx, cy, s / 2.0)
            glow.setColorAt(0.0, QColor(0, 132, 255, 90))
            glow.setColorAt(0.7, QColor(124, 58, 237, 40))
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QRectF(0, 0, s, s))

        # Frosted Glass Circle Background
        badge_pad = 2.0
        badge_rect = QRectF(badge_pad, badge_pad, s - 2 * badge_pad, s - 2 * badge_pad)

        if self.is_hovered:
            bg_color = QColor(24, 28, 45, 230)
            border_color = QColor(0, 132, 255, 180)
        else:
            bg_color = QColor(18, 21, 33, 200)
            border_color = QColor(255, 255, 255, 45)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.2))
        painter.drawEllipse(badge_rect)

        painter.end()
