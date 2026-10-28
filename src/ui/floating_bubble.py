"""
Floating Voxel trigger shown near selected text.
Uses the approved text/speech mark, not a conventional recording microphone or volume icon.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QCursor, QMouseEvent

from src.config import BUBBLE_SIZE, BUBBLE_TIMEOUT_SECONDS, BRAND
from assets.icons import create_voxel_logo


class FloatingBubble(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_text = ""
        self.is_hovered = False

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

        self.logo = create_voxel_logo(int(BUBBLE_SIZE * 0.86))
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(160)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setInterval(int(BUBBLE_TIMEOUT_SECONDS * 1000))
        self.hide_timer.timeout.connect(self.fade_out)

    def show_at(self, text: str, cursor_x: int, cursor_y: int):
        self.selected_text = text
        target_x = cursor_x + 10
        target_y = cursor_y - self.height() - 8
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            if target_y < geo.top() + 6:
                target_y = cursor_y + 20
            target_x = max(geo.left() + 6, min(geo.right() - self.width() - 6, target_x))
            target_y = max(geo.top() + 6, min(geo.bottom() - self.height() - 6, target_y))
        self.move(int(target_x), int(target_y))

        self.fade_anim.stop()
        self.setWindowOpacity(0.0)
        self.show()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        self.hide_timer.start()

    def fade_out(self):
        self.hide_timer.stop()
        self.fade_anim.stop()
        self.fade_anim.setStartValue(self.windowOpacity())
        self.fade_anim.setEndValue(0.0)
        try:
            self.fade_anim.finished.disconnect(self._on_fade_out_finished)
        except Exception:
            pass
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
        rect = QRectF(1.0, 1.0, self.width() - 2.0, self.height() - 2.0)
        if self.is_hovered:
            painter.setBrush(QBrush(QColor(104, 71, 255, 35)))
            painter.setPen(QPen(QColor(22, 139, 255, 170), 1.2))
        else:
            painter.setBrush(QBrush(QColor(255, 255, 255, 28)))
            painter.setPen(QPen(QColor(255, 255, 255, 95), 0.8))
        painter.drawEllipse(rect)
        self.logo.paint(painter, int(self.width()*0.07), int(self.height()*0.07),
                        int(self.width()*0.86), int(self.height()*0.86))
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
            self.hide_timer.stop()
            self.hide()
            self.clicked.emit(text)
        super().mousePressEvent(event)
