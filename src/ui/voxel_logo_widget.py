"""
Voxel logo widget (brand v2): three rounded bars on a solid accent circle.

While speaking, the bars move like a live waveform. No glow, no gradients.
Public API is unchanged: VoxelLogoWidget(size, animated), set_size, start/stop_voice_animation.
"""
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor

ACCENT = QColor("#3478F6")

# Same geometry as brand mark A (scripts/generate_brand_v2.py), in a 100x100 box.
_BARS = [(20, 31, 17, 38), (41.5, 12, 17, 76), (63, 31, 17, 38)]


class VoxelLogoWidget(QWidget):
    def __init__(self, size: int = 34, animated: bool = False, parent=None, badge: bool = True):
        """badge=True: white bars on a blue circle. badge=False: bars only (outline-style mark)."""
        super().__init__(parent)
        self.badge = badge
        self.bar_color = QColor("#8A8A8A")
        self.bar_active_color = ACCENT
        self.logo_size = size
        self.setFixedSize(size, size)
        self.is_animating = False
        self._anim_phase = 0.0
        self._line_scales = [1.0, 1.0, 1.0]
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._on_anim_frame)
        if animated:
            self.start_voice_animation()

    def set_bar_colors(self, idle: str, active: str):
        self.bar_color, self.bar_active_color = QColor(idle), QColor(active)
        self.update()

    def set_size(self, size: int):
        self.logo_size = size
        self.setFixedSize(size, size)
        self.update()

    def start_voice_animation(self):
        if not self.is_animating:
            self.is_animating = True
            self._timer.start()

    def stop_voice_animation(self):
        self.is_animating = False
        self._timer.stop()
        self._line_scales = [1.0, 1.0, 1.0]
        self.update()

    def _on_anim_frame(self):
        if not self.is_animating:
            return
        self._anim_phase += 0.16
        t = self._anim_phase
        # outer bars move more than the centre bar; restrained, speech-like motion
        self._line_scales = [
            0.55 + 0.45 * abs(math.sin(t * 1.7)),
            0.75 + 0.25 * abs(math.sin(t * 1.3 + 1.1)),
            0.55 + 0.45 * abs(math.sin(t * 2.1 + 2.3)),
        ]
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        size = float(min(self.width(), self.height()))
        ox = (self.width() - size) / 2.0
        oy = (self.height() - size) / 2.0

        p.setPen(Qt.PenStyle.NoPen)
        if self.badge:
            p.setBrush(ACCENT)
            p.drawEllipse(QRectF(ox, oy, size, size))
            s = size / 100.0 * 0.62          # bars inside the circle (same scale as the bubble icon)
            pad = size * 0.19
            p.setBrush(QColor("#FFFFFF"))
        else:
            s = size / 100.0                 # bars fill the box
            pad = 0.0
            p.setBrush(self.bar_active_color if self.is_animating else self.bar_color)
        for (x, y, w, h), k in zip(_BARS, self._line_scales):
            bh = h * k
            cy = y + h / 2.0                      # keep each bar centred while it scales
            rect = QRectF(ox + pad + x * s, oy + pad + (cy - bh / 2.0) * s, w * s, bh * s)
            p.drawRoundedRect(rect, w * s / 2.0, w * s / 2.0)
        p.end()
