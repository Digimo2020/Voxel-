"""
Floating Mic Bubble widget.
Smoothly fades in near selected text with a sleek, modern circular icon.
Clicking it launches playback and reveals the mini player.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QCursor, QMouseEvent

from src.config import BUBBLE_SIZE, BUBBLE_TIMEOUT_SECONDS, THEME
from assets.icons import create_mic_icon


class FloatingBubble(QWidget):
    """
    Subtle circular floating mic button appearing near selected text.
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

        # Pre-render mic icon
        self.mic_icon = create_mic_icon(size=int(BUBBLE_SIZE * 0.62), color="#FFFFFF")

        # Fade animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(220)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Auto-hide timer
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setInterval(int(BUBBLE_TIMEOUT_SECONDS * 1000))
        self.hide_timer.timeout.connect(self.fade_out)

    def show_at(self, text: str, cursor_x: int, cursor_y: int):
        """
        Positions the bubble near the mouse cursor (offset above or below)
        and smoothly fades it in.
        """
        self.selected_text = text

        # Position slightly above and to the right of cursor
        offset_x = 12
        offset_y = -BUBBLE_SIZE - 10

        target_x = cursor_x + offset_x
        target_y = cursor_y + offset_y

        # Screen boundary clamping
        screen = self.screen() or self.parent().screen() if self.parent() else None
        if screen:
            geo = screen.availableGeometry()
            # If too close to top edge, place below cursor
            if target_y < geo.top() + 10:
                target_y = cursor_y + 24
            # Keep within horizontal bounds
            target_x = max(geo.left() + 10, min(geo.right() - BUBBLE_SIZE - 10, target_x))
            target_y = max(geo.top() + 10, min(geo.bottom() - BUBBLE_SIZE - 10, target_y))

        self.move(int(target_x), int(target_y))

        # Start fade-in animation
        self.fade_anim.stop()
        self.setWindowOpacity(0.0)
        self.show()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

        # Start auto-hide timeout
        self.hide_timer.start()

    def fade_out(self):
        """Smoothly fades out and hides the bubble."""
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

        w = self.width()
        h = self.height()

        # Outer subtle glow / shadow border
        bg_color = QColor(THEME["bg_bubble_hover"] if self.is_hovered else THEME["bg_bubble"])
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(255, 255, 255, 60), 1.5))
        painter.drawEllipse(2, 2, w - 4, h - 4)

        # Draw center mic icon
        icon_size = int(w * 0.58)
        ix = (w - icon_size) // 2
        iy = (h - icon_size) // 2
        self.mic_icon.paint(painter, ix, iy, icon_size, icon_size)

        painter.end()

    def enterEvent(self, event):
        self.is_hovered = True
        self.hide_timer.stop()  # Keep alive while hovered
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
