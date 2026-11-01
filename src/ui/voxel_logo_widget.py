"""
Voxel Logo Vector Widget with Voice-Reactive Animations.
Renders the Voxel microphone and speech-bubble cradle with smooth anti-aliased vector paths.
Features dynamic voice animation:
- The 3 horizontal voice lines animate like an audio equalizer waveform when speaking.
- A subtle pulsating radial glow radiates from behind the microphone.
"""
import math
import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QPainterPath,
    QLinearGradient, QRadialGradient, QPixmap
)

from src.config import THEME
from assets.icons import get_selection_bubble_pixmap


class VoxelLogoWidget(QWidget):
    """
    High-DPI Vector widget rendering the Voxel logo with voice animations.
    """
    def __init__(self, size: int = 34, animated: bool = False, parent=None):
        super().__init__(parent)
        self.logo_size = size
        self.setFixedSize(size, size)

        # Animation states
        self.is_animating = False
        self._anim_phase = 0.0
        self._glow_intensity = 0.0
        self._line_scales = [1.0, 1.0, 1.0]

        # Timer for voice wave animation (40 FPS)
        self._timer = QTimer(self)
        self._timer.setInterval(25)
        self._timer.timeout.connect(self._on_anim_frame)

        if animated:
            self.start_voice_animation()

    def set_size(self, size: int):
        self.logo_size = size
        self.setFixedSize(size, size)
        self.update()

    def start_voice_animation(self):
        """Starts real-time voice reactive wave & glow animation."""
        if not self.is_animating:
            self.is_animating = True
            self._timer.start()

    def stop_voice_animation(self):
        """Stops animation and settles the 3 lines back to default."""
        self.is_animating = False
        self._timer.stop()
        self._line_scales = [1.0, 1.0, 1.0]
        self._glow_intensity = 0.0
        self.update()

    def _on_anim_frame(self):
        if not self.is_animating:
            return

        self._anim_phase += 0.16
        # Sine wave modulation for the 3 horizontal voice lines
        s1 = 0.65 + 0.35 * math.sin(self._anim_phase * 1.8)
        s2 = 0.70 + 0.30 * math.sin(self._anim_phase * 2.2 + 1.2)
        s3 = 0.60 + 0.40 * math.sin(self._anim_phase * 1.5 + 2.4)
        self._line_scales = [s1, s2, s3]

        # Gentle breathing glow
        self._glow_intensity = 0.35 + 0.30 * math.sin(self._anim_phase * 1.2)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = self.width()
        h = self.height()
        size = min(w, h)
        cx = w / 2.0
        cy = h * 0.48

        # 1. Idle display: render official authentic brand emblem
        if not self.is_animating:
            pixmap = get_selection_bubble_pixmap(int(size))
            if pixmap and not pixmap.isNull():
                target_x = int((w - pixmap.width()) / 2)
                target_y = int((h - pixmap.height()) / 2)
                painter.drawPixmap(target_x, target_y, pixmap)
                painter.end()
                return

        # 2. Voice-Reactive Animated State
        # Radial Glow behind mic when animating
        if self._glow_intensity > 0.05:
            glow_rad = size * 0.50
            glow = QRadialGradient(cx, cy, glow_rad)
            alpha = int(180 * self._glow_intensity)
            glow.setColorAt(0.0, QColor(0, 240, 255, alpha))      # Electric Cyan
            glow.setColorAt(0.55, QColor(116, 65, 249, int(alpha * 0.6)))  # Brand Purple
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QPointF(cx, cy), glow_rad, glow_rad)

        # Dimension scales
        scale = size / 100.0
        cradle_stroke = max(2.0, 8.2 * scale)

        # Outer Cradle & Speech Bubble Tail (Official Brand Purple #7441F9 to Indigo)
        grad_cradle = QLinearGradient(cx - 35 * scale, cy + 35 * scale, cx + 35 * scale, cy - 35 * scale)
        grad_cradle.setColorAt(0.0, QColor("#7441F9"))  # Brand Purple
        grad_cradle.setColorAt(0.5, QColor("#8B5CF6"))  # Accent Purple
        grad_cradle.setColorAt(1.0, QColor("#00E5FF"))  # Electric Cyan Accent

        pen_cradle = QPen(
            QBrush(grad_cradle),
            cradle_stroke,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        )
        painter.setPen(pen_cradle)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        cradle_path = QPainterPath()
        cradle_path.moveTo(cx - 26 * scale, cy - 10 * scale)
        cradle_path.cubicTo(
            cx - 26 * scale, cy + 18 * scale,
            cx - 18 * scale, cy + 28 * scale,
            cx - 10 * scale, cy + 32 * scale
        )
        cradle_path.lineTo(cx - 15 * scale, cy + 44 * scale)
        cradle_path.lineTo(cx - 2 * scale, cy + 33 * scale)
        cradle_path.cubicTo(
            cx + 16 * scale, cy + 33 * scale,
            cx + 26 * scale, cy + 20 * scale,
            cx + 26 * scale, cy - 10 * scale
        )
        painter.drawPath(cradle_path)

        # Inner Microphone Capsule (Rich Brand Gradient)
        mic_w = 34 * scale
        mic_h = 45 * scale
        mic_x = cx - mic_w / 2.0
        mic_y = cy - mic_h / 2.0 - 5 * scale
        mic_r = mic_w / 2.0

        grad_mic = QLinearGradient(mic_x, mic_y + mic_h, mic_x + mic_w, mic_y)
        grad_mic.setColorAt(0.0, QColor("#5B21B6"))
        grad_mic.setColorAt(1.0, QColor("#7C3AED"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad_mic))
        painter.drawRoundedRect(QRectF(mic_x, mic_y, mic_w, mic_h), mic_r, mic_r)

        # Glass Specular Dome on Mic Capsule
        spec_w = mic_w * 0.70
        spec_h = mic_h * 0.36
        spec_x = cx - spec_w / 2.0
        spec_y = mic_y + 2.0 * scale
        spec_grad = QLinearGradient(spec_x, spec_y, spec_x, spec_y + spec_h)
        spec_grad.setColorAt(0.0, QColor(255, 255, 255, 160))
        spec_grad.setColorAt(0.65, QColor(255, 255, 255, 40))
        spec_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(spec_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(spec_x, spec_y, spec_w, spec_h), spec_w / 2.0, spec_w / 2.0)

        # Three Voice Lines Inside the Microphone (Voice-Reactive Equalizer)
        line_thickness = max(1.8, 3.8 * scale)
        line_pen = QPen(QColor("#FFFFFF"), line_thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(line_pen)

        hw_top = 7.0 * scale * self._line_scales[0]
        hw_mid = 10.0 * scale * self._line_scales[1]
        hw_bot = 8.0 * scale * self._line_scales[2]

        y_top = cy - 10 * scale
        y_mid = cy - 4 * scale
        y_bot = cy + 2 * scale

        painter.drawLine(QPointF(cx - hw_top, y_top), QPointF(cx + hw_top, y_top))
        painter.drawLine(QPointF(cx - hw_mid, y_mid), QPointF(cx + hw_mid, y_mid))
        painter.drawLine(QPointF(cx - hw_bot, y_bot), QPointF(cx + hw_bot, y_bot))

        painter.end()
