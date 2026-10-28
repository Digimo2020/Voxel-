"""
Renders professional open-source preview images and banners for the GitHub repository.
Reflects the refined frosted glass aesthetic, line-art buttons, and speaker icon.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import (
    QImage, QPainter, QColor, QFont, QPen, QBrush, QLinearGradient,
    QPainterPath, QRadialGradient
)
from PyQt6.QtCore import Qt, QRectF, QPointF

app = QApplication.instance() or QApplication(sys.argv)
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def render_banner():
    width, height = 1200, 400
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(QColor("#0B0D17"))

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Ambient radial glow
    radial = QRadialGradient(QPointF(width * 0.5, height * 0.4), 600)
    radial.setColorAt(0.0, QColor(96, 165, 250, 60))
    radial.setColorAt(0.5, QColor(59, 130, 246, 20))
    radial.setColorAt(1.0, QColor(11, 13, 23, 0))
    p.setBrush(QBrush(radial))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(0, 0, width, height)

    p.setPen(QPen(QColor(255, 255, 255, 25), 1))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(QRectF(1, 1, width - 2, height - 2), 14, 14)

    # Logo circle
    logo_size = 76
    logo_x = (width - logo_size) // 2
    logo_y = 55
    grad_logo = QLinearGradient(logo_x, logo_y, logo_x + logo_size, logo_y + logo_size)
    grad_logo.setColorAt(0.0, QColor(38, 44, 68, 240))
    grad_logo.setColorAt(1.0, QColor(22, 26, 42, 230))
    p.setBrush(QBrush(grad_logo))
    p.setPen(QPen(QColor(96, 165, 250, 180), 1.5))
    p.drawEllipse(QRectF(logo_x, logo_y, logo_size, logo_size))

    # Inner Speaker icon with waves
    p.setBrush(QBrush(QColor("#60A5FA")))
    p.setPen(Qt.PenStyle.NoPen)
    spk_path = QPainterPath()
    sx0, sy0 = logo_x + 22, logo_y + 30
    sx1, sy1 = logo_x + 30, logo_y + 46
    sx2, sy2 = logo_x + 44, logo_y + 56
    sx3, sy3 = logo_x + 44, logo_y + 20
    spk_path.moveTo(sx0, sy0)
    spk_path.lineTo(sx1, sy0)
    spk_path.lineTo(sx2, sy3)
    spk_path.lineTo(sx2, sy2)
    spk_path.lineTo(sx1, sy1)
    spk_path.lineTo(sx0, sy1)
    spk_path.closeSubpath()
    p.drawPath(spk_path)

    # Waves
    p.setBrush(Qt.BrushStyle.NoBrush)
    pen_w = QPen(QColor("#60A5FA"), 2.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen_w)
    w1_rect = QRectF(logo_x + 38, logo_y + 26, 22, 24)
    pw1 = QPainterPath()
    pw1.arcMoveTo(w1_rect, -45)
    pw1.arcTo(w1_rect, -45, 90)
    p.drawPath(pw1)

    w2_rect = QRectF(logo_x + 35, logo_y + 20, 34, 36)
    pw2 = QPainterPath()
    pw2.arcMoveTo(w2_rect, -40)
    pw2.arcTo(w2_rect, -40, 80)
    p.drawPath(pw2)

    # Title: TEXT 2 VOICE
    p.setPen(QColor("#FFFFFF"))
    font_title = QFont("Segoe UI", 32, QFont.Weight.Bold)
    p.setFont(font_title)
    p.drawText(QRectF(0, 150, width, 50), Qt.AlignmentFlag.AlignCenter, "TEXT 2 VOICE")

    # Subtitle
    p.setPen(QColor("#94A3B8"))
    font_sub = QFont("Segoe UI", 15, QFont.Weight.Normal)
    p.setFont(font_sub)
    p.drawText(QRectF(0, 210, width, 30), Qt.AlignmentFlag.AlignCenter, "Universal Frosted Glass Text-to-Speech Engine for Windows & macOS")

    # Feature badges
    badges = [
        "⚡ 24px Micro Trigger",
        "🪟 Frosted Glass UI",
        "🎙️ Neural Natural Voices",
        "🎛️ Line-Art Speed Pill",
        "📜 JSON History Storage"
    ]
    badge_y = 280
    start_x = 105
    spacing = 205
    for i, b in enumerate(badges):
        bx = start_x + (i * spacing)
        p.setBrush(QBrush(QColor(22, 26, 42, 200)))
        p.setPen(QPen(QColor(255, 255, 255, 30), 1))
        p.drawRoundedRect(QRectF(bx, badge_y, 190, 38), 19, 19)

        p.setPen(QColor("#E2E8F0"))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        p.drawText(QRectF(bx, badge_y, 190, 38), Qt.AlignmentFlag.AlignCenter, b)

    p.end()
    out_path = os.path.join(OUT_DIR, "banner.png")
    img.save(out_path)
    print("Saved banner to:", out_path)


def render_ui_preview():
    width, height = 1000, 560
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(QColor("#0B0D17"))

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Simulated Application Window (Clean Editor / Browser)
    win_x, win_y, win_w, win_h = 60, 40, 880, 480
    p.setBrush(QBrush(QColor("#131622")))
    p.setPen(QPen(QColor(255, 255, 255, 18), 1))
    p.drawRoundedRect(QRectF(win_x, win_y, win_w, win_h), 14, 14)

    # Title Bar
    p.setBrush(QBrush(QColor("#1A1E2E")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(win_x, win_y, win_w, 42), 14, 14)
    p.drawRect(QRectF(win_x, win_y + 30, win_w, 12))

    p.setBrush(QBrush(QColor("#EF4444")))
    p.drawEllipse(QRectF(win_x + 16, win_y + 15, 11, 11))
    p.setBrush(QBrush(QColor("#F59E0B")))
    p.drawEllipse(QRectF(win_x + 34, win_y + 15, 11, 11))
    p.setBrush(QBrush(QColor("#10B981")))
    p.drawEllipse(QRectF(win_x + 52, win_y + 15, 11, 11))

    p.setPen(QColor("#94A3B8"))
    p.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
    p.drawText(QRectF(win_x + 76, win_y + 11, 400, 20), Qt.AlignmentFlag.AlignLeft, "Document — Works anywhere in Chrome, Word, VS Code, Google Docs")

    # Document text
    content_y = win_y + 80
    p.setPen(QColor("#CAD3F5"))
    p.setFont(QFont("Segoe UI", 13, QFont.Weight.Normal))
    p.drawText(win_x + 50, content_y, "Natural Language Processing and Speech Synthesis have advanced dramatically.")
    p.drawText(win_x + 50, content_y + 35, "Users can effortlessly highlight any paragraph or sentence across any platform.")

    # Selected text highlight
    sel_rect = QRectF(win_x + 48, content_y + 52, 595, 30)
    p.setBrush(QBrush(QColor(96, 165, 250, 45)))
    p.setPen(QPen(QColor(96, 165, 250, 90), 1))
    p.drawRoundedRect(sel_rect, 4, 4)

    p.setPen(QColor("#FFFFFF"))
    p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    p.drawText(win_x + 52, content_y + 73, "Text 2 Voice will instantly detect the selection and fade in a floating speaker.")

    p.setPen(QColor("#CAD3F5"))
    p.setFont(QFont("Segoe UI", 13, QFont.Weight.Normal))
    p.drawText(win_x + 50, content_y + 118, "Playback begins with natural human cadence, crystal-clear pronunciation, and custom speed.")

    # 1. New 24px Micro Speaker Bubble Mockup (50% smaller!)
    bubble_x = win_x + 655
    bubble_y = content_y + 53
    bubble_size = 24

    # Frosted glass circle
    grad_b = QLinearGradient(0, bubble_y, 0, bubble_y + bubble_size)
    grad_b.setColorAt(0.0, QColor(48, 56, 82, 235))
    grad_b.setColorAt(1.0, QColor(22, 26, 40, 220))
    p.setBrush(QBrush(grad_b))
    p.setPen(QPen(QColor(255, 255, 255, 80), 1.0))
    p.drawEllipse(QRectF(bubble_x, bubble_y, bubble_size, bubble_size))

    # Inner speaker icon
    p.setBrush(QBrush(QColor("#FFFFFF")))
    p.setPen(Qt.PenStyle.NoPen)
    spk_p = QPainterPath()
    bx0, by0 = bubble_x + 5, bubble_y + 9
    bx1, by1 = bubble_x + 8, bubble_y + 15
    bx2, by2 = bubble_x + 13, bubble_y + 19
    bx3, by3 = bubble_x + 13, bubble_y + 5
    spk_p.moveTo(bx0, by0)
    spk_p.lineTo(bx1, by0)
    spk_p.lineTo(bx2, by3)
    spk_p.lineTo(bx2, by2)
    spk_p.lineTo(bx1, by1)
    spk_p.lineTo(bx0, by1)
    spk_p.closeSubpath()
    p.drawPath(spk_p)

    # Wave arc
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor("#FFFFFF"), 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    w_arc = QRectF(bubble_x + 11, bubble_y + 7, 8, 10)
    pw = QPainterPath()
    pw.arcMoveTo(w_arc, -45)
    pw.arcTo(w_arc, -45, 90)
    p.drawPath(pw)

    # Pointer arrow & label
    p.setPen(QColor("#94A3B8"))
    p.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
    p.drawText(bubble_x + 32, bubble_y + 16, "← Subtle 24px Speaker Trigger (Fades in)")

    # 2. Refined Frosted Glass Mini Player Pill Mockup
    player_w, player_h = 320, 48
    player_x = (width - player_w) // 2
    player_y = content_y + 195

    # True Frosted Glass Pill
    grad_p = QLinearGradient(0, player_y, 0, player_y + player_h)
    grad_p.setColorAt(0.0, QColor(38, 44, 64, 215))
    grad_p.setColorAt(0.4, QColor(22, 25, 38, 205))
    grad_p.setColorAt(1.0, QColor(16, 18, 28, 220))
    p.setBrush(QBrush(grad_p))
    p.setPen(QPen(QColor(255, 255, 255, 48), 1.0))
    p.drawRoundedRect(QRectF(player_x, player_y, player_w, player_h), player_h / 2, player_h / 2)

    # Button 1: Play/Pause circle with line border
    btn1_x = player_x + 12
    btn1_y = player_y + 8
    btn1_r = 32
    p.setBrush(QBrush(QColor(96, 165, 250, 40)))
    p.setPen(QPen(QColor(96, 165, 250, 180), 1.2))
    p.drawEllipse(QRectF(btn1_x, btn1_y, btn1_r, btn1_r))
    # Pause bars
    p.setBrush(QBrush(QColor("#60A5FA")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(btn1_x + 10, btn1_y + 9, 3.5, 14), 1.5, 1.5)
    p.drawRoundedRect(QRectF(btn1_x + 18, btn1_y + 9, 3.5, 14), 1.5, 1.5)

    # Button 2: Stop circle with line border
    btn2_x = btn1_x + 40
    btn2_y = player_y + 10
    btn2_r = 28
    p.setBrush(QBrush(QColor(248, 113, 113, 35)))
    p.setPen(QPen(QColor(248, 113, 113, 140), 1.0))
    p.drawEllipse(QRectF(btn2_x, btn2_y, btn2_r, btn2_r))
    p.setBrush(QBrush(QColor("#F87171")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(btn2_x + 9, btn2_y + 9, 10, 10), 2, 2)

    # Separator
    p.setPen(QPen(QColor(255, 255, 255, 35), 1))
    p.drawLine(QPointF(btn2_x + 36, player_y + 15), QPointF(btn2_x + 36, player_y + 33))

    # Speed controls: [-] 1.0x [+]
    sp_x = btn2_x + 46
    p.setBrush(QBrush(QColor(255, 255, 255, 20)))
    p.setPen(QPen(QColor(255, 255, 255, 45), 1))
    p.drawEllipse(QRectF(sp_x, player_y + 12, 24, 24))
    p.setPen(QColor("#CBD5E1"))
    p.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
    p.drawText(QRectF(sp_x, player_y + 12, 24, 24), Qt.AlignmentFlag.AlignCenter, "-")

    p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
    p.drawText(QRectF(sp_x + 24, player_y + 12, 42, 24), Qt.AlignmentFlag.AlignCenter, "1.25x")

    p.setBrush(QBrush(QColor(255, 255, 255, 20)))
    p.setPen(QPen(QColor(255, 255, 255, 45), 1))
    p.drawEllipse(QRectF(sp_x + 66, player_y + 12, 24, 24))
    p.setPen(QColor("#CBD5E1"))
    p.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
    p.drawText(QRectF(sp_x + 66, player_y + 12, 24, 24), Qt.AlignmentFlag.AlignCenter, "+")

    # Separator
    p.setPen(QPen(QColor(255, 255, 255, 35), 1))
    p.drawLine(QPointF(sp_x + 98, player_y + 15), QPointF(sp_x + 98, player_y + 33))

    # Voice capsule
    vc_x = sp_x + 106
    p.setBrush(QBrush(QColor(255, 255, 255, 20)))
    p.setPen(QPen(QColor(255, 255, 255, 50), 1))
    p.drawRoundedRect(QRectF(vc_x, player_y + 11, 62, 26), 13, 13)
    p.setPen(QColor("#E2E8F0"))
    p.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
    p.drawText(QRectF(vc_x, player_y + 11, 62, 26), Qt.AlignmentFlag.AlignCenter, "Jenny")

    # Close button
    cl_x = vc_x + 70
    p.setPen(QPen(QColor("#94A3B8"), 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    p.drawLine(QPointF(cl_x + 4, player_y + 19), QPointF(cl_x + 14, player_y + 29))
    p.drawLine(QPointF(cl_x + 14, player_y + 19), QPointF(cl_x + 4, player_y + 29))

    # Annotation pointer for player
    p.setPen(QColor("#60A5FA"))
    p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
    p.drawText(QRectF(0, player_y + 64, width, 24), Qt.AlignmentFlag.AlignCenter, "Frosted Glass Pill with Simple Line-Art Round Buttons (Draggable anywhere)")

    p.end()
    out_path = os.path.join(OUT_DIR, "floating_ui_preview.png")
    img.save(out_path)
    print("Saved preview to:", out_path)


if __name__ == "__main__":
    render_banner()
    render_ui_preview()
