"""
Interactive Voice Equalizer Widget for Voxel.
Parametric EQ curve display matching professional audio workstations:
- Interactive draggable control nodes (HPF, 100Hz, 200Hz, 500Hz, 1kHz, 2kHz, LPF).
- Dynamic bezier frequency curve with gradient fill.
- Vocal presets: Podcast Warmth, Vocal Clarity, Bright & Airy, Flat / Natural.
- Full Light Mode and Dark Mode support.
"""
from typing import List, Dict, Optional
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QButtonGroup
)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient,
    QFont, QCursor, QMouseEvent
)

from src.utils.settings import settings_db

EQ_PRESETS: Dict[str, List[float]] = {
    "Podcast Warmth": [0.0, 3.5, 2.0, -1.0, 0.5, 1.5, 0.0],
    "Vocal Clarity": [-2.0, -1.0, 0.0, -1.5, 2.5, 4.0, 1.0],
    "Bright & Airy": [0.0, 0.5, 0.0, 0.0, 1.5, 3.5, 3.0],
    "Flat / Natural": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
}

BAND_CONFIGS = [
    {"id": "hpf", "name": "HPF", "freq": "80Hz", "default": 0.0},
    {"id": "100hz", "name": "100Hz", "freq": "100Hz", "default": 3.5},
    {"id": "200hz", "name": "200Hz", "freq": "200Hz", "default": 2.0},
    {"id": "500hz", "name": "500Hz", "freq": "500Hz", "default": -1.0},
    {"id": "1khz", "name": "1kHz", "freq": "1kHz", "default": 0.5},
    {"id": "2khz", "name": "2kHz", "freq": "2kHz", "default": 1.5},
    {"id": "lpf", "name": "LPF", "freq": "12kHz", "default": 0.0},
]


class ParametricEQGraph(QWidget):
    """Interactive canvas rendering the parametric EQ frequency curve."""
    band_changed = pyqtSignal(int, float)  # (band_index, gain_db)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(150)
        self.setMinimumWidth(360)
        self.setMouseTracking(True)

        self.gains: List[float] = [b["default"] for b in BAND_CONFIGS]
        self.drag_band: Optional[int] = None
        self.hover_band: Optional[int] = None
        self.theme_mode: str = "light"

    def set_theme_mode(self, mode: str):
        self.theme_mode = mode
        self.update()

    def set_gains(self, gains: List[float]):
        self.gains = [max(-12.0, min(12.0, float(g))) for g in gains]
        self.update()

    def get_gains(self) -> List[float]:
        return list(self.gains)

    def _db_to_y(self, db: float, h: float, padding: float = 22.0) -> float:
        """Maps gain dB [-12, +12] to Y coordinate."""
        usable_h = h - (padding * 2.0)
        # +12 dB is top (padding), -12 dB is bottom (h - padding)
        norm = (db - (-12.0)) / 24.0  # 0.0 at -12dB, 1.0 at +12dB
        return (h - padding) - (norm * usable_h)

    def _y_to_db(self, y: float, h: float, padding: float = 22.0) -> float:
        """Maps Y coordinate back to gain dB [-12, +12]."""
        usable_h = h - (padding * 2.0)
        clamped_y = max(padding, min(h - padding, y))
        norm = ((h - padding) - clamped_y) / usable_h
        return (norm * 24.0) - 12.0

    def _band_x(self, idx: int, w: float, padding: float = 34.0) -> float:
        """Maps band index to X coordinate."""
        usable_w = w - (padding * 2.0)
        step = usable_w / max(1, len(self.gains) - 1)
        return padding + (idx * step)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            w, h = float(self.width()), float(self.height())
            for i in range(len(self.gains)):
                bx = self._band_x(i, w)
                by = self._db_to_y(self.gains[i], h)
                dist = math.hypot(pos.x() - bx, pos.y() - by)
                if dist <= 14.0:
                    self.drag_band = i
                    self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                    break
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double click resets the clicked band to 0 dB."""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            w, h = float(self.width()), float(self.height())
            for i in range(len(self.gains)):
                bx = self._band_x(i, w)
                by = self._db_to_y(self.gains[i], h)
                if math.hypot(pos.x() - bx, pos.y() - by) <= 14.0:
                    self.gains[i] = 0.0
                    self.band_changed.emit(i, 0.0)
                    self.update()
                    break
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        w, h = float(self.width()), float(self.height())

        if self.drag_band is not None:
            new_db = round(self._y_to_db(pos.y(), h), 1)
            self.gains[self.drag_band] = new_db
            self.band_changed.emit(self.drag_band, new_db)
            self.update()
            return

        # Check hover
        old_hover = self.hover_band
        self.hover_band = None
        for i in range(len(self.gains)):
            bx = self._band_x(i, w)
            by = self._db_to_y(self.gains[i], h)
            if math.hypot(pos.x() - bx, pos.y() - by) <= 14.0:
                self.hover_band = i
                self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
                break

        if self.hover_band is None:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        if old_hover != self.hover_band:
            self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.drag_band is not None:
            self.drag_band = None
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor if self.hover_band is not None else Qt.CursorShape.ArrowCursor))
            self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())
        is_dark = (self.theme_mode == "dark")

        # 1. Background Rounded Panel
        bg_col = QColor("#131627") if is_dark else QColor("#F8FAFC")
        border_col = QColor(255, 255, 255, 24) if is_dark else QColor(226, 232, 240, 255)
        painter.setBrush(QBrush(bg_col))
        painter.setPen(QPen(border_col, 1.0))
        painter.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), 8.0, 8.0)

        # 2. Horizontal Grid Lines (+12, +6, 0, -6, -12 dB)
        grid_col = QColor(255, 255, 255, 16) if is_dark else QColor(148, 163, 184, 55)
        zero_col = QColor(255, 255, 255, 45) if is_dark else QColor(148, 163, 184, 130)
        label_col = QColor("#94A3B8") if is_dark else QColor("#64748B")

        font = QFont(self.font().family(), 8)
        painter.setFont(font)

        for db in [12.0, 6.0, 0.0, -6.0, -12.0]:
            gy = self._db_to_y(db, h)
            if db == 0.0:
                pen = QPen(zero_col, 1.0, Qt.PenStyle.DashLine)
            else:
                pen = QPen(grid_col, 0.8, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(int(28.0), int(gy), int(w - 12.0), int(gy))

            # dB label
            painter.setPen(QPen(label_col))
            sign = "+" if db > 0 else ""
            painter.drawText(QRectF(4.0, gy - 7.0, 22.0, 14.0), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{sign}{int(db)}")

        # 3. Vertical Grid Lines & Frequency Labels
        num_bands = len(self.gains)
        pts: List[QPointF] = []
        for i in range(num_bands):
            bx = self._band_x(i, w)
            by = self._db_to_y(self.gains[i], h)
            pts.append(QPointF(bx, by))

            # Vertical grid line
            painter.setPen(QPen(grid_col, 0.8, Qt.PenStyle.SolidLine))
            painter.drawLine(int(bx), 16, int(bx), int(h - 22))

            # Band Frequency label at bottom
            painter.setPen(QPen(label_col))
            lbl = BAND_CONFIGS[i]["name"]
            painter.drawText(QRectF(bx - 20.0, h - 20.0, 40.0, 16.0), Qt.AlignmentFlag.AlignCenter, lbl)

        # 4. Interpolate Curve using Catmull-Rom or cubic Bezier
        curve_path = QPainterPath()
        if pts:
            curve_path.moveTo(pts[0].x(), pts[0].y())
            for i in range(len(pts) - 1):
                p0 = pts[i - 1] if i > 0 else pts[i]
                p1 = pts[i]
                p2 = pts[i + 1]
                p3 = pts[i + 2] if i + 2 < len(pts) else p2

                # Smooth control points
                c1 = QPointF(p1.x() + (p2.x() - p0.x()) / 5.0, p1.y() + (p2.y() - p0.y()) / 5.0)
                c2 = QPointF(p2.x() - (p3.x() - p1.x()) / 5.0, p2.y() - (p3.y() - p1.y()) / 5.0)
                curve_path.cubicTo(c1, c2, p2)

        # 5. Gradient Fill below Curve
        fill_path = QPainterPath(curve_path)
        fill_path.lineTo(pts[-1].x(), h - 22.0)
        fill_path.lineTo(pts[0].x(), h - 22.0)
        fill_path.closeSubpath()

        grad = QLinearGradient(0, 16, 0, h - 22)
        if is_dark:
            grad.setColorAt(0.0, QColor(124, 58, 237, 75))
            grad.setColorAt(0.5, QColor(0, 132, 255, 45))
            grad.setColorAt(1.0, QColor(0, 132, 255, 5))
        else:
            grad.setColorAt(0.0, QColor(124, 58, 237, 55))
            grad.setColorAt(0.5, QColor(0, 132, 255, 30))
            grad.setColorAt(1.0, QColor(0, 132, 255, 5))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawPath(fill_path)

        # 6. Draw Curve Line
        curve_pen = QPen(QColor("#7C3AED") if is_dark else QColor("#6366F1"), 2.2)
        curve_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(curve_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(curve_path)

        # 7. Draw Band Control Nodes
        for i, pt in enumerate(pts):
            is_hovered = (i == self.hover_band or i == self.drag_band)
            node_r = 6.5 if is_hovered else 4.5

            # Outer glow
            if is_hovered:
                glow_col = QColor(124, 58, 237, 90)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(glow_col))
                painter.drawEllipse(pt, node_r + 4.0, node_r + 4.0)

            # Node body
            body_col = QColor("#0084FF") if is_hovered else QColor("#7C3AED")
            painter.setPen(QPen(QColor("#FFFFFF"), 1.6))
            painter.setBrush(QBrush(body_col))
            painter.drawEllipse(pt, node_r, node_r)

            # Gain badge if hovered/dragged
            if is_hovered:
                val = self.gains[i]
                sign = "+" if val > 0 else ""
                badge_text = f"{sign}{val:.1f} dB"
                painter.setFont(QFont(self.font().family(), 8, QFont.Weight.Bold))
                painter.setPen(QPen(QColor("#FFFFFF") if is_dark else QColor("#0F172A")))
                by_off = -14.0 if pt.y() > 32.0 else 18.0
                painter.drawText(QRectF(pt.x() - 30.0, pt.y() + by_off - 8.0, 60.0, 16.0), Qt.AlignmentFlag.AlignCenter, badge_text)

        painter.end()


class VoiceEqualizerWidget(QWidget):
    """
    Complete Voice Equalizer card containing preset pill selector and parametric curve canvas.
    """
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_mode = "light"
        self._init_ui()
        self._load_saved_eq()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Preset Button Group
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(6)

        self.btn_group = QButtonGroup(self)
        self.preset_buttons: Dict[str, QPushButton] = {}

        for preset_name in EQ_PRESETS.keys():
            btn = QPushButton(preset_name)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, name=preset_name: self.apply_preset(name))
            self.btn_group.addButton(btn)
            preset_layout.addWidget(btn)
            self.preset_buttons[preset_name] = btn

        preset_layout.addStretch()
        layout.addLayout(preset_layout)

        # Parametric Graph Canvas
        self.graph = ParametricEQGraph(self)
        self.graph.band_changed.connect(self._on_band_changed)
        layout.addWidget(self.graph)

    def set_theme_mode(self, mode: str):
        self.theme_mode = mode
        self.graph.set_theme_mode(mode)
        is_dark = (mode == "dark")

        btn_style = f"""
            QPushButton {{
                background-color: {'#1E2338' if is_dark else '#F1F5F9'};
                color: {'#94A3B8' if is_dark else '#475569'};
                border: 1px solid {'#2A324B' if is_dark else '#CBD5E1'};
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {'#262D47' if is_dark else '#E2E8F0'};
                color: {'#FFFFFF' if is_dark else '#0F172A'};
            }}
            QPushButton:checked {{
                background-color: #7C3AED;
                color: #FFFFFF;
                border: 1px solid #7C3AED;
                font-weight: 600;
            }}
        """
        for btn in self.preset_buttons.values():
            btn.setStyleSheet(btn_style)

    def _load_saved_eq(self):
        saved_preset = settings_db.get("eq_preset", "Podcast Warmth")
        saved_gains = settings_db.get("eq_gains", EQ_PRESETS.get(saved_preset, EQ_PRESETS["Podcast Warmth"]))
        self.graph.set_gains(saved_gains)

        if saved_preset in self.preset_buttons:
            self.preset_buttons[saved_preset].setChecked(True)
        else:
            if "Podcast Warmth" in self.preset_buttons:
                self.preset_buttons["Podcast Warmth"].setChecked(True)

    def apply_preset(self, name: str):
        if name in EQ_PRESETS:
            gains = EQ_PRESETS[name]
            self.graph.set_gains(gains)
            settings_db.set("eq_preset", name)
            settings_db.set("eq_gains", gains)
            if name in self.preset_buttons:
                self.preset_buttons[name].setChecked(True)
            self.settings_changed.emit()

    def _on_band_changed(self, band_idx: int, gain_db: float):
        gains = self.graph.get_gains()
        # Find if matches existing preset
        matched = False
        for pname, pvals in EQ_PRESETS.items():
            if all(abs(g - p) < 0.1 for g, p in zip(gains, pvals)):
                settings_db.set("eq_preset", pname)
                if pname in self.preset_buttons:
                    self.preset_buttons[pname].setChecked(True)
                matched = True
                break
        if not matched:
            settings_db.set("eq_preset", "Custom")
            self.btn_group.setExclusive(False)
            for btn in self.preset_buttons.values():
                btn.setChecked(False)
            self.btn_group.setExclusive(True)

        settings_db.set("eq_gains", gains)
        self.settings_changed.emit()
