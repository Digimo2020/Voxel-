"""
Voxel brand assets — original approved logo mark.

The Voxel mark uses a rounded text/speech capsule with three text lines,
framed by an open U-shaped lower contour and a speech tail. The mark is
rendered with the approved violet-to-blue gradient, with monochrome
variants for tray/taskbar use.
"""
import math
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtCore import Qt, QPointF, QRectF


BRAND_PURPLE = "#6847FF"
BRAND_BLUE = "#168BFF"
BRAND_NAVY = "#111B2E"


def create_voxel_logo(size: int = 64, monochrome: str | None = None) -> QIcon:
    """Return the approved Voxel icon as scalable QPainter artwork.

    Args:
        size: Requested square output size in pixels.
        monochrome: Optional single colour, e.g. '#667085', for taskbar/tray use.
    """
    size = max(16, int(size))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    s = float(size)
    # Fit the mark inside a square with comfortable icon padding.
    scale = s / 100.0
    def pt(x, y):
        return QPointF(x * scale, y * scale)

    if monochrome:
        pen = QPen(QColor(monochrome), max(1.8, 7.0 * scale),
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        gradient = None
    else:
        gradient = QLinearGradient(14 * scale, 82 * scale, 78 * scale, 18 * scale)
        gradient.setColorAt(0.0, QColor(BRAND_PURPLE))
        gradient.setColorAt(0.52, QColor("#465DFF"))
        gradient.setColorAt(1.0, QColor(BRAND_BLUE))
        pen = QPen(QBrush(gradient), max(1.8, 7.0 * scale),
                   Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Main capsule: tall rounded text field, left/right sides and curved top/bottom.
    capsule = QPainterPath()
    capsule.moveTo(pt(35, 48))
    capsule.lineTo(pt(35, 29))
    capsule.cubicTo(pt(35, 18), pt(42, 12), pt(50, 12))
    capsule.cubicTo(pt(59, 12), pt(65, 18), pt(65, 29))
    capsule.lineTo(pt(65, 48))
    capsule.cubicTo(pt(65, 60), pt(59, 67), pt(50, 67))
    capsule.cubicTo(pt(41, 67), pt(35, 60), pt(35, 48))
    p.drawPath(capsule)

    # Three short rounded text lines inside the capsule.
    p.setPen(QPen(QBrush(gradient) if gradient else QColor(monochrome),
                  max(2.0, 6.2 * scale), Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    for x1, x2, y in [(43, 57, 31), (43, 57, 40), (44, 55, 49)]:
        p.drawLine(pt(x1, y), pt(x2, y))

    # Open U-shaped frame and integrated speech tail.
    p.setPen(pen)
    frame = QPainterPath()
    frame.moveTo(pt(23, 42))
    frame.cubicTo(pt(23, 58), pt(33, 72), pt(47, 75))
    frame.lineTo(pt(47, 89))
    frame.lineTo(pt(70, 69))
    frame.cubicTo(pt(79, 61), pt(82, 52), pt(82, 42))
    p.drawPath(frame)

    p.end()
    return QIcon(pixmap)


def create_voxel_app_icon(size: int = 64, background: str | None = None) -> QIcon:
    """Create the Voxel app/tray icon; transparent by default."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    if background:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(background)))
        p.drawRoundedRect(QRectF(1, 1, size - 2, size - 2), size * 0.22, size * 0.22)
    p.end()

    logo = create_voxel_logo(size=int(size * 0.9))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    logo.paint(painter, int(size * 0.05), int(size * 0.05), int(size * 0.9), int(size * 0.9))
    painter.end()
    return QIcon(pixmap)


# Backward-compatible aliases so existing UI imports don't break during rebranding.
def create_app_icon(size: int = 64) -> QIcon:
    return create_voxel_app_icon(size, background="#151C2B")


def create_speaker_icon(size: int = 24, color: str = "#FFFFFF", waves: int = 2) -> QIcon:
    """Kept for existing floating-trigger call sites; intentionally simple."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(color)
    pen = QPen(c, max(1.4, size * 0.09), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    s = float(size)
    # An understated text-to-speech glyph: capsule + three text lines, no conventional volume cone.
    capsule = QRectF(s*0.28, s*0.08, s*0.42, s*0.55)
    p.drawRoundedRect(capsule, s*0.16, s*0.16)
    for y, half in [(0.25, 0.10), (0.37, 0.10), (0.49, 0.075)]:
        p.drawLine(QPointF(s*(0.49-half), s*y), QPointF(s*(0.49+half), s*y))
    frame = QPainterPath()
    frame.moveTo(QPointF(s*0.15, s*0.43))
    frame.cubicTo(QPointF(s*0.15, s*0.68), QPointF(s*0.32, s*0.76), QPointF(s*0.46, s*0.78))
    frame.lineTo(QPointF(s*0.46, s*0.96))
    frame.lineTo(QPointF(s*0.72, s*0.74))
    frame.cubicTo(QPointF(s*0.84, s*0.64), QPointF(s*0.86, s*0.54), QPointF(s*0.86, s*0.43))
    p.drawPath(frame)
    p.end()
    return QIcon(pixmap)
