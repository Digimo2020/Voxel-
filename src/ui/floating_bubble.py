"""
Floating Voxel Logo Trigger widget.
Subtle frosted glass circular badge displaying the Voxel microphone logo.
Appears smoothly with fade-in near selected text without stealing window focus.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QCursor, QMouseEvent,
    QRadialGradient, QLinearGradient, QEnterEvent
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
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            s = float(self.width())
            cx, cy = s / 2.0, s / 2.0

            # Ambient bluish glass aura / shadow
            aura = QRadialGradient(cx, cy, s / 2.0)
            alpha_aura = 75 if self.is_hovered else 40
            aura.setColorAt(0.0, QColor(0, 140, 255, alpha_aura))
            aura.setColorAt(0.65, QColor(99, 102, 241, int(alpha_aura * 0.45)))
            aura.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(aura))
            painter.drawEllipse(QRectF(0, 0, s, s))

            # Frosted Bluish Glass Circle Background
            badge_pad = 2.0
            badge_rect = QRectF(badge_pad, badge_pad, s - 2 * badge_pad, s - 2 * badge_pad)

            # Translucent bluish acrylic gradient
            bg_grad = QRadialGradient(cx, cy * 0.72, s * 0.70)
            if self.is_hovered:
                bg_grad.setColorAt(0.0, QColor(0, 160, 255, 235))   # Electric cyan-blue highlight
                bg_grad.setColorAt(0.45, QColor(16, 68, 155, 220))  # Sapphire glass
                bg_grad.setColorAt(0.85, QColor(10, 32, 85, 205))   # Deep azure
                bg_grad.setColorAt(1.0, QColor(8, 22, 60, 195))     # Vignette edge
                border_grad = QLinearGradient(badge_rect.topLeft(), badge_rect.bottomLeft())
                border_grad.setColorAt(0.0, QColor(220, 245, 255, 240))
                border_grad.setColorAt(0.45, QColor(56, 189, 248, 210))
                border_grad.setColorAt(1.0, QColor(139, 92, 246, 190))
                border_pen = QPen(QBrush(border_grad), 1.5)
            else:
                bg_grad.setColorAt(0.0, QColor(30, 125, 245, 195))  # Smooth bluish glass tone
                bg_grad.setColorAt(0.40, QColor(14, 52, 125, 180))  # Frosted glass depth
                bg_grad.setColorAt(0.80, QColor(8, 28, 75, 175))    # Translucent deep blue
                bg_grad.setColorAt(1.0, QColor(6, 18, 50, 165))     # Soft boundary
                border_grad = QLinearGradient(badge_rect.topLeft(), badge_rect.bottomLeft())
                border_grad.setColorAt(0.0, QColor(190, 230, 255, 190))
                border_grad.setColorAt(0.45, QColor(56, 189, 248, 140))
                border_grad.setColorAt(1.0, QColor(129, 140, 248, 110))
                border_pen = QPen(QBrush(border_grad), 1.3)

            painter.setBrush(QBrush(bg_grad))
            painter.setPen(border_pen)
            painter.drawEllipse(badge_rect)

            # Specular Glass Gloss Arc / Highlight on upper dome
            gloss_w = (s - 2 * badge_pad) * 0.76
            gloss_h = (s - 2 * badge_pad) * 0.40
            gloss_rect = QRectF(cx - gloss_w / 2.0, badge_pad + 2.5, gloss_w, gloss_h)
            gloss_grad = QLinearGradient(gloss_rect.topLeft(), gloss_rect.bottomLeft())
            gloss_alpha = 130 if self.is_hovered else 85
            gloss_grad.setColorAt(0.0, QColor(255, 255, 255, gloss_alpha))
            gloss_grad.setColorAt(0.65, QColor(180, 230, 255, int(gloss_alpha * 0.35)))
            gloss_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(gloss_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(gloss_rect)
        finally:
            painter.end()
