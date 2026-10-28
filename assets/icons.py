"""
Vector icon generator using QPainter.
Produces crisp, resolution-independent line-art icons for frosted glass micro-UIs.
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QPointF, QRectF
import math


def create_speaker_icon(size: int = 24, color: str = "#FFFFFF", waves: int = 2) -> QIcon:
    """Creates an elegant line-art speaker icon with sound waves."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    c = QColor(color)
    stroke = max(1.2, size * 0.08)

    # 1. Speaker body & cone
    path = QPainterPath()
    x0, y0 = size * 0.18, size * 0.38
    x1, y1 = size * 0.32, size * 0.62
    x2, y2 = size * 0.52, size * 0.78
    x3, y3 = size * 0.52, size * 0.22

    path.moveTo(x0, y0)
    path.lineTo(x1, y0)
    path.lineTo(x2, y3)
    path.lineTo(x2, y2)
    path.lineTo(x1, y1)
    path.lineTo(x0, y1)
    path.closeSubpath()

    painter.setBrush(QBrush(c))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(path)

    # 2. Sound wave arcs
    pen_wave = QPen(c, stroke, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_wave)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    # First small wave arc
    arc1_w, arc1_h = size * 0.32, size * 0.44
    arc1_x = size * 0.46
    arc1_y = (size - arc1_h) / 2
    path_w1 = QPainterPath()
    path_w1.arcMoveTo(QRectF(arc1_x, arc1_y, arc1_w, arc1_h), -45)
    path_w1.arcTo(QRectF(arc1_x, arc1_y, arc1_w, arc1_h), -45, 90)
    painter.drawPath(path_w1)

    # Second larger wave arc
    if waves >= 2:
        arc2_w, arc2_h = size * 0.54, size * 0.72
        arc2_x = size * 0.44
        arc2_y = (size - arc2_h) / 2
        path_w2 = QPainterPath()
        path_w2.arcMoveTo(QRectF(arc2_x, arc2_y, arc2_w, arc2_h), -40)
        path_w2.arcTo(QRectF(arc2_x, arc2_y, arc2_w, arc2_h), -40, 80)
        painter.drawPath(path_w2)

    painter.end()
    return QIcon(pixmap)


def create_gear_icon(size: int = 20, color: str = "#94A3B8") -> QIcon:
    """Minimalist line-art settings cog/gear icon."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    c = QColor(color)
    stroke = max(1.2, size * 0.08)
    pen = QPen(c, stroke, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    cx, cy = size / 2.0, size / 2.0
    outer_r = size * 0.38
    inner_r = size * 0.18

    # Inner hole
    painter.drawEllipse(QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2))

    # Outer teeth (6 teeth)
    teeth = 6
    for i in range(teeth):
        angle = i * (2 * math.pi / teeth)
        x1 = cx + (outer_r * 0.7) * math.cos(angle)
        y1 = cy + (outer_r * 0.7) * math.sin(angle)
        x2 = cx + outer_r * math.cos(angle)
        y2 = cy + outer_r * math.sin(angle)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    # Outer circle rim
    painter.drawEllipse(QRectF(cx - outer_r * 0.75, cy - outer_r * 0.75, outer_r * 1.5, outer_r * 1.5))

    painter.end()
    return QIcon(pixmap)


def create_play_icon(size: int = 24, color: str = "#60A5FA") -> QIcon:
    """Crisp line-art play triangle."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    c = QColor(color)
    painter.setBrush(QBrush(c))
    painter.setPen(Qt.PenStyle.NoPen)

    path = QPainterPath()
    p1 = QPointF(size * 0.35, size * 0.28)
    p2 = QPointF(size * 0.35, size * 0.72)
    p3 = QPointF(size * 0.72, size * 0.50)
    path.moveTo(p1)
    path.lineTo(p2)
    path.lineTo(p3)
    path.closeSubpath()
    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_pause_icon(size: int = 24, color: str = "#60A5FA") -> QIcon:
    """Two sleek rounded pause bars."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)

    bar_w = max(2.5, size * 0.15)
    bar_h = size * 0.48
    y = (size - bar_h) / 2
    r = bar_w / 2

    # Left bar
    painter.drawRoundedRect(QRectF(size * 0.33, y, bar_w, bar_h), r, r)
    # Right bar
    painter.drawRoundedRect(QRectF(size * 0.55, y, bar_w, bar_h), r, r)

    painter.end()
    return QIcon(pixmap)


def create_stop_icon(size: int = 24, color: str = "#F87171") -> QIcon:
    """Clean rounded stop square."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)

    s = size * 0.38
    x = (size - s) / 2
    painter.drawRoundedRect(QRectF(x, x, s, s), 2.5, 2.5)

    painter.end()
    return QIcon(pixmap)


def create_close_icon(size: int = 20, color: str = "#94A3B8") -> QIcon:
    """Delicate line cross."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), max(1.5, size * 0.10))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    pad = size * 0.32
    painter.drawLine(QPointF(pad, pad), QPointF(size - pad, size - pad))
    painter.drawLine(QPointF(size - pad, pad), QPointF(pad, size - pad))

    painter.end()
    return QIcon(pixmap)


def create_app_icon(size: int = 64) -> QIcon:
    """Creates the application tray & window icon with speaker symbol."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Frosted dark circular glass background
    painter.setBrush(QBrush(QColor("#1E2235")))
    painter.setPen(QPen(QColor(255, 255, 255, 80), 1.5))
    painter.drawEllipse(QRectF(2, 2, size - 4, size - 4))
    painter.end()

    # Inner speaker
    spk = create_speaker_icon(size=int(size * 0.65), color="#60A5FA", waves=2)
    painter = QPainter(pixmap)
    offset = int(size * 0.175)
    spk.paint(painter, offset, offset, int(size * 0.65), int(size * 0.65))
    painter.end()

    return QIcon(pixmap)
