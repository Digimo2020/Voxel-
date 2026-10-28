"""
Voxel Vector Icon Generator.
Produces resolution-independent icons and symbols using QPainter for Retina/HiDPI screens.
"""
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QPen, QBrush,
    QPainterPath, QLinearGradient, QRadialGradient
)
from PyQt6.QtCore import Qt, QPointF, QRectF
import math


def create_voxel_icon_pixmap(size: int = 64) -> QPixmap:
    """Renders the standalone Voxel microphone icon onto a QPixmap."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    cx = size / 2.0
    cy = size * 0.48
    scale = size / 100.0

    # Cradle
    cradle_stroke = max(1.8, 8.2 * scale)
    grad_cradle = QLinearGradient(cx - 35 * scale, cy + 35 * scale, cx + 35 * scale, cy - 35 * scale)
    grad_cradle.setColorAt(0.0, QColor("#7C3AED"))
    grad_cradle.setColorAt(0.4, QColor("#6366F1"))
    grad_cradle.setColorAt(1.0, QColor("#0084FF"))

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

    # Microphone capsule
    mic_w = 34 * scale
    mic_h = 45 * scale
    mic_x = cx - mic_w / 2.0
    mic_y = cy - mic_h / 2.0 - 5 * scale
    mic_r = mic_w / 2.0

    grad_mic = QLinearGradient(mic_x, mic_y + mic_h, mic_x + mic_w, mic_y)
    grad_mic.setColorAt(0.0, QColor("#0072FF"))
    grad_mic.setColorAt(1.0, QColor("#00C6FF"))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(grad_mic))
    painter.drawRoundedRect(QRectF(mic_x, mic_y, mic_w, mic_h), mic_r, mic_r)

    # 3 lines
    line_thickness = max(1.6, 3.8 * scale)
    line_pen = QPen(QColor("#FFFFFF"), line_thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(line_pen)

    hw_top = 7.0 * scale
    hw_mid = 10.0 * scale
    hw_bot = 8.0 * scale

    y_top = cy - 10 * scale
    y_mid = cy - 4 * scale
    y_bot = cy + 2 * scale

    painter.drawLine(QPointF(cx - hw_top, y_top), QPointF(cx + hw_top, y_top))
    painter.drawLine(QPointF(cx - hw_mid, y_mid), QPointF(cx + hw_mid, y_mid))
    painter.drawLine(QPointF(cx - hw_bot, y_bot), QPointF(cx + hw_bot, y_bot))

    painter.end()
    return pix


def create_app_icon(size: int = 64) -> QIcon:
    """App Icon with frosted squircle and Voxel microphone."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Rounded squircle background
    r = size * 0.22
    painter.setBrush(QBrush(QColor("#131625")))
    painter.setPen(QPen(QColor(255, 255, 255, 45), 1.2))
    painter.drawRoundedRect(QRectF(2, 2, size - 4, size - 4), r, r)
    painter.end()

    # Draw logo centered
    logo_pix = create_voxel_icon_pixmap(int(size * 0.72))
    painter = QPainter(pix)
    offset = int(size * 0.14)
    painter.drawPixmap(offset, offset, logo_pix)
    painter.end()

    return QIcon(pix)


def create_tray_icon(size: int = 32) -> QIcon:
    """Menu bar / tray icon."""
    pix = create_voxel_icon_pixmap(size)
    return QIcon(pix)


def create_play_icon(size: int = 24, color: str = "#FFFFFF") -> QIcon:
    """Play triangle."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)

    path = QPainterPath()
    left = size * 0.34
    top = size * 0.24
    right = size * 0.74
    mid_y = size * 0.50
    bottom = size * 0.76

    path.moveTo(left, top)
    path.lineTo(right, mid_y)
    path.lineTo(left, bottom)
    path.closeSubpath()

    painter.drawPath(path)
    painter.end()
    return QIcon(pix)


def create_pause_icon(size: int = 24, color: str = "#FFFFFF") -> QIcon:
    """Pause double bars."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)

    bar_w = max(2.5, size * 0.15)
    bar_h = size * 0.50
    gap = size * 0.16
    cx = size / 2.0
    cy = (size - bar_h) / 2.0

    r = bar_w / 2.0
    painter.drawRoundedRect(QRectF(cx - gap - bar_w, cy, bar_w, bar_h), r, r)
    painter.drawRoundedRect(QRectF(cx + gap, cy, bar_w, bar_h), r, r)

    painter.end()
    return QIcon(pix)


def create_stop_icon(size: int = 24, color: str = "#94A3B8") -> QIcon:
    """Clean rounded stop square."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QBrush(QColor(color)))
    painter.setPen(Qt.PenStyle.NoPen)

    s = size * 0.38
    x = (size - s) / 2.0
    painter.drawRoundedRect(QRectF(x, x, s, s), 3.0, 3.0)

    painter.end()
    return QIcon(pix)


def create_minus_icon(size: int = 18, color: str = "#CBD5E1") -> QIcon:
    """Minus line for speed pill."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    pad = size * 0.28
    painter.drawLine(QPointF(pad, size / 2.0), QPointF(size - pad, size / 2.0))
    painter.end()
    return QIcon(pix)


def create_plus_icon(size: int = 18, color: str = "#CBD5E1") -> QIcon:
    """Plus sign for speed pill."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    pad = size * 0.28
    mid = size / 2.0
    painter.drawLine(QPointF(pad, mid), QPointF(size - pad, mid))
    painter.drawLine(QPointF(mid, pad), QPointF(mid, size - pad))
    painter.end()
    return QIcon(pix)


def create_chevron_down_icon(size: int = 16, color: str = "#94A3B8") -> QIcon:
    """Chevron down arrow for voice dropdown."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    path = QPainterPath()
    left = size * 0.25
    mid_x = size * 0.50
    right = size * 0.75
    top = size * 0.38
    bottom = size * 0.62

    path.moveTo(left, top)
    path.lineTo(mid_x, bottom)
    path.lineTo(right, top)

    painter.drawPath(path)
    painter.end()
    return QIcon(pix)


def create_gear_icon(size: int = 20, color: str = "#94A3B8") -> QIcon:
    """Line-art settings cog."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    cx, cy = size / 2.0, size / 2.0
    r_in = size * 0.18
    r_out = size * 0.36
    teeth = 8

    path = QPainterPath()
    for i in range(teeth * 2):
        angle = i * math.pi / teeth
        r = r_out if i % 2 == 0 else r_in * 1.35
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    painter.drawPath(path)
    painter.drawEllipse(QPointF(cx, cy), r_in * 0.85, r_in * 0.85)

    painter.end()
    return QIcon(pix)


def create_close_icon(size: int = 20, color: str = "#94A3B8") -> QIcon:
    """Delicate line cross."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    pad = size * 0.32
    painter.drawLine(QPointF(pad, pad), QPointF(size - pad, size - pad))
    painter.drawLine(QPointF(size - pad, pad), QPointF(pad, size - pad))

    painter.end()
    return QIcon(pix)
