"""
Self-contained vector icon generator using QPainter.
Produces crisp, resolution-independent icons for High-DPI screens.
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QPointF, QRectF


def create_mic_icon(size: int = 32, color: str = "#FFFFFF") -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    c = QColor(color)
    pen = QPen(c, size * 0.08)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    # Mic body (pill capsule)
    w = size * 0.32
    h = size * 0.44
    x = (size - w) / 2
    y = size * 0.14
    painter.setBrush(QBrush(c))
    painter.drawRoundedRect(QRectF(x, y, w, h), w / 2, w / 2)

    # Mic cradle (arc below body)
    arc_w = size * 0.52
    arc_h = size * 0.48
    arc_x = (size - arc_w) / 2
    arc_y = size * 0.22
    painter.setBrush(Qt.BrushStyle.NoBrush)
    path = QPainterPath()
    path.arcMoveTo(QRectF(arc_x, arc_y, arc_w, arc_h), 180)
    path.arcTo(QRectF(arc_x, arc_y, arc_w, arc_h), 180, 180)
    painter.drawPath(path)

    # Mic stand (vertical line)
    stand_top = arc_y + arc_h
    stand_bottom = size * 0.82
    painter.drawLine(QPointF(size / 2, stand_top), QPointF(size / 2, stand_bottom))

    # Mic base (horizontal line)
    base_w = size * 0.36
    painter.drawLine(QPointF((size - base_w) / 2, stand_bottom), QPointF((size + base_w) / 2, stand_bottom))

    painter.end()
    return QIcon(pixmap)


def create_play_icon(size: int = 24, color: str = "#FFFFFF") -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)

    # Triangle
    path = QPainterPath()
    p1 = QPointF(size * 0.30, size * 0.22)
    p2 = QPointF(size * 0.30, size * 0.78)
    p3 = QPointF(size * 0.78, size * 0.50)
    path.moveTo(p1)
    path.lineTo(p2)
    path.lineTo(p3)
    path.closeSubpath()
    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_pause_icon(size: int = 24, color: str = "#FFFFFF") -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)

    bar_w = size * 0.18
    bar_h = size * 0.56
    y = (size - bar_h) / 2
    r = bar_w / 3

    # Left bar
    painter.drawRoundedRect(QRectF(size * 0.26, y, bar_w, bar_h), r, r)
    # Right bar
    painter.drawRoundedRect(QRectF(size * 0.56, y, bar_w, bar_h), r, r)

    painter.end()
    return QIcon(pixmap)


def create_stop_icon(size: int = 24, color: str = "#FFFFFF") -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)

    s = size * 0.48
    x = (size - s) / 2
    painter.drawRoundedRect(QRectF(x, x, s, s), 3, 3)

    painter.end()
    return QIcon(pixmap)


def create_close_icon(size: int = 20, color: str = "#A6ADC8") -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), size * 0.12)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    pad = size * 0.28
    painter.drawLine(QPointF(pad, pad), QPointF(size - pad, size - pad))
    painter.drawLine(QPointF(size - pad, pad), QPointF(pad, size - pad))

    painter.end()
    return QIcon(pixmap)


def create_app_icon(size: int = 64) -> QIcon:
    """Creates the application tray & window icon (gradient bubble with mic)."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Circle background
    painter.setBrush(QBrush(QColor("#6366F1")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QRectF(2, 2, size - 4, size - 4))

    # Inner mic
    painter.end()

    mic = create_mic_icon(size=int(size * 0.65), color="#FFFFFF")
    painter = QPainter(pixmap)
    mic.paint(painter, int(size * 0.175), int(size * 0.175), int(size * 0.65), int(size * 0.65))
    painter.end()

    return QIcon(pixmap)
