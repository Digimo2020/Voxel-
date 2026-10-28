"""
Renders professional open-source preview images and banners for the GitHub repository.
Uses PyQt6 QPainter for high-resolution, anti-aliased visual output.
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
    img.fill(QColor("#0F111A"))

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Background ambient radial glow
    radial = QRadialGradient(QPointF(width * 0.5, height * 0.4), 600)
    radial.setColorAt(0.0, QColor(99, 102, 241, 70))
    radial.setColorAt(0.5, QColor(139, 92, 246, 25))
    radial.setColorAt(1.0, QColor(15, 17, 26, 0))
    p.setBrush(QBrush(radial))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(0, 0, width, height)

    # Subtle border
    p.setPen(QPen(QColor(255, 255, 255, 20), 1))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(QRectF(1, 1, width - 2, height - 2), 12, 12)

    # Logo circle
    logo_size = 80
    logo_x = (width - logo_size) // 2
    logo_y = 55
    grad_logo = QLinearGradient(logo_x, logo_y, logo_x + logo_size, logo_y + logo_size)
    grad_logo.setColorAt(0.0, QColor("#6366F1"))
    grad_logo.setColorAt(1.0, QColor("#8B5CF6"))
    p.setBrush(QBrush(grad_logo))
    p.setPen(QPen(QColor(255, 255, 255, 100), 2))
    p.drawEllipse(QRectF(logo_x, logo_y, logo_size, logo_size))

    # Inner Mic icon in logo
    p.setBrush(QBrush(QColor("#FFFFFF")))
    p.setPen(Qt.PenStyle.NoPen)
    # Mic capsule
    mc_w, mc_h = 24, 34
    mc_x = logo_x + (logo_size - mc_w) / 2
    mc_y = logo_y + 16
    p.drawRoundedRect(QRectF(mc_x, mc_y, mc_w, mc_h), 12, 12)
    # Cradle
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor("#FFFFFF"), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    arc_rect = QRectF(logo_x + 20, logo_y + 24, 40, 36)
    path = QPainterPath()
    path.arcMoveTo(arc_rect, 180)
    path.arcTo(arc_rect, 180, 180)
    p.drawPath(path)
    # Stand
    p.drawLine(QPointF(logo_x + 40, logo_y + 60), QPointF(logo_x + 40, logo_y + 67))
    p.drawLine(QPointF(logo_x + 28, logo_y + 67), QPointF(logo_x + 52, logo_y + 67))

    # Title: TEXT 2 VOICE
    p.setPen(QColor("#FFFFFF"))
    font_title = QFont("Segoe UI", 32, QFont.Weight.Bold)
    p.setFont(font_title)
    p.drawText(QRectF(0, 155, width, 50), Qt.AlignmentFlag.AlignCenter, "TEXT 2 VOICE")

    # Subtitle / Tagline
    p.setPen(QColor("#A6ADC8"))
    font_sub = QFont("Segoe UI", 15, QFont.Weight.Normal)
    p.setFont(font_sub)
    p.drawText(QRectF(0, 215, width, 30), Qt.AlignmentFlag.AlignCenter, "Universal Floating Text-to-Speech Engine for Windows & macOS")

    # Feature badges
    badges = [
        "⚡ Universal Selection",
        "🎙️ Natural Neural Voices",
        "🎛️ Speed Controls (0.5x-2.0x)",
        "📜 JSON History Storage",
        "📦 100% Standalone .EXE"
    ]
    badge_y = 285
    start_x = 105
    spacing = 205
    for i, b in enumerate(badges):
        bx = start_x + (i * spacing)
        # Badge pill
        p.setBrush(QBrush(QColor(30, 32, 48, 220)))
        p.setPen(QPen(QColor(99, 102, 241, 120), 1.2))
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
    img.fill(QColor("#11131F"))

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Desktop Application Window Mockup (Chrome / Editor window)
    win_x, win_y, win_w, win_h = 60, 40, 880, 480
    p.setBrush(QBrush(QColor("#181926")))
    p.setPen(QPen(QColor(255, 255, 255, 20), 1))
    p.drawRoundedRect(QRectF(win_x, win_y, win_w, win_h), 12, 12)

    # Window Title Bar
    p.setBrush(QBrush(QColor("#1E2030")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(win_x, win_y, win_w, 42), 12, 12)
    p.drawRect(QRectF(win_x, win_y + 30, win_w, 12))

    # Window Dots (Close, Min, Max)
    p.setBrush(QBrush(QColor("#ED8796")))
    p.drawEllipse(QRectF(win_x + 16, win_y + 15, 12, 12))
    p.setBrush(QBrush(QColor("#EED49F")))
    p.drawEllipse(QRectF(win_x + 36, win_y + 15, 12, 12))
    p.setBrush(QBrush(QColor("#A6DA95")))
    p.drawEllipse(QRectF(win_x + 56, win_y + 15, 12, 12))

    # Window title text
    p.setPen(QColor("#939AB7"))
    p.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
    p.drawText(QRectF(win_x + 80, win_y + 11, 400, 20), Qt.AlignmentFlag.AlignLeft, "Document.txt — Any Windows Application / Browser / Google Docs")

    # Document content text
    content_y = win_y + 80
    p.setPen(QColor("#CAD3F5"))
    p.setFont(QFont("Segoe UI", 13, QFont.Weight.Normal))
    p.drawText(win_x + 50, content_y, "Natural Language Processing and Speech Synthesis have advanced dramatically.")
    p.drawText(win_x + 50, content_y + 35, "Users can effortlessly select any paragraph or sentence across any platform.")

    # Highlighting selected text
    sel_rect = QRectF(win_x + 48, content_y + 52, 590, 32)
    p.setBrush(QBrush(QColor(99, 102, 241, 90)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(sel_rect, 4, 4)

    p.setPen(QColor("#FFFFFF"))
    p.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    p.drawText(win_x + 52, content_y + 74, "Text 2 Voice will instantly detect the selection and fade in a floating mic.")

    p.setPen(QColor("#CAD3F5"))
    p.setFont(QFont("Segoe UI", 13, QFont.Weight.Normal))
    p.drawText(win_x + 50, content_y + 120, "Playback begins with natural human cadence, crystal-clear pronunciation, and custom speed.")

    # 1. Floating Mic Bubble Mockup
    bubble_x = win_x + 655
    bubble_y = content_y + 44
    bubble_size = 44

    # Glow effect
    p.setBrush(QBrush(QColor(99, 102, 241, 60)))
    p.drawEllipse(QRectF(bubble_x - 4, bubble_y - 4, bubble_size + 8, bubble_size + 8))

    p.setBrush(QBrush(QColor("#6366F1")))
    p.setPen(QPen(QColor(255, 255, 255, 120), 2))
    p.drawEllipse(QRectF(bubble_x, bubble_y, bubble_size, bubble_size))

    # Mic inside bubble
    p.setBrush(QBrush(QColor("#FFFFFF")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(bubble_x + 14, bubble_y + 9, 16, 20), 8, 8)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor("#FFFFFF"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    b_arc = QRectF(bubble_x + 10, bubble_y + 14, 24, 20)
    p_b = QPainterPath()
    p_b.arcMoveTo(b_arc, 180)
    p_b.arcTo(b_arc, 180, 180)
    p.drawPath(p_b)
    p.drawLine(QPointF(bubble_x + 22, bubble_y + 34), QPointF(bubble_x + 22, bubble_y + 38))

    # Tooltip / label pointing to bubble
    p.setPen(QColor("#A6ADC8"))
    p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    p.drawText(bubble_x - 30, bubble_y - 12, "Fades in smoothly ↗")

    # 2. Floating Mini Player Pill Mockup
    player_w, player_h = 390, 60
    player_x = (width - player_w) // 2
    player_y = content_y + 190

    # Shadow
    p.setBrush(QBrush(QColor(0, 0, 0, 160)))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(player_x + 3, player_y + 6, player_w, player_h), 30, 30)

    # Pill background
    p.setBrush(QBrush(QColor("#1E1E2E")))
    p.setPen(QPen(QColor("#313244"), 2))
    p.drawRoundedRect(QRectF(player_x, player_y, player_w, player_h), 30, 30)

    # Play/Pause button
    btn_r = 40
    btn_x = player_x + 12
    btn_y = player_y + (player_h - btn_r) // 2
    p.setBrush(QBrush(QColor("#89B4FA")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(btn_x, btn_y, btn_r, btn_r))

    # Pause icon bars
    p.setBrush(QBrush(QColor("#1E1E2E")))
    p.drawRoundedRect(QRectF(btn_x + 13, btn_y + 12, 5, 16), 2, 2)
    p.drawRoundedRect(QRectF(btn_x + 22, btn_y + 12, 5, 16), 2, 2)

    # Stop button
    stop_x = btn_x + 48
    stop_y = player_y + 14
    p.setBrush(QBrush(QColor("#313244")))
    p.drawRoundedRect(QRectF(stop_x, stop_y, 32, 32), 16, 16)
    p.setBrush(QBrush(QColor("#F38BA8")))
    p.drawRoundedRect(QRectF(stop_x + 9, stop_y + 9, 14, 14), 2, 2)

    # Separator 1
    p.setPen(QPen(QColor("#45475A"), 1.5))
    p.drawLine(QPointF(stop_x + 42, player_y + 16), QPointF(stop_x + 42, player_y + 44))

    # Speed Controls [-] 1.0x [+]
    sp_x = stop_x + 54
    p.setBrush(QBrush(QColor("#313244")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(sp_x, player_y + 16, 28, 28), 14, 14)
    p.setPen(QColor("#CDD6F4"))
    p.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    p.drawText(QRectF(sp_x, player_y + 16, 28, 28), Qt.AlignmentFlag.AlignCenter, "-")

    p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    p.drawText(QRectF(sp_x + 28, player_y + 16, 50, 28), Qt.AlignmentFlag.AlignCenter, "1.25x")

    p.drawRoundedRect(QRectF(sp_x + 78, player_y + 16, 28, 28), 14, 14)
    p.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    p.drawText(QRectF(sp_x + 78, player_y + 16, 28, 28), Qt.AlignmentFlag.AlignCenter, "+")

    # Separator 2
    p.setPen(QPen(QColor("#45475A"), 1.5))
    p.drawLine(QPointF(sp_x + 116, player_y + 16), QPointF(sp_x + 116, player_y + 44))

    # Voice button
    vc_x = sp_x + 126
    p.setBrush(QBrush(QColor("#313244")))
    p.setPen(QPen(QColor("#89B4FA"), 1))
    p.drawRoundedRect(QRectF(vc_x, player_y + 15, 86, 30), 15, 15)
    p.setPen(QColor("#CDD6F4"))
    p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    p.drawText(QRectF(vc_x, player_y + 15, 86, 30), Qt.AlignmentFlag.AlignCenter, "Jenny (F)")

    # Close button
    cl_x = vc_x + 94
    p.setPen(QColor("#A6ADC8"))
    p.setFont(QFont("Segoe UI", 11, QFont.Weight.Normal))
    p.drawText(QRectF(cl_x, player_y + 15, 26, 30), Qt.AlignmentFlag.AlignCenter, "✕")

    # Annotation pointer for player
    p.setPen(QColor("#89B4FA"))
    p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
    p.drawText(QRectF(0, player_y + 70, width, 24), Qt.AlignmentFlag.AlignCenter, "Floating Mini Player Pill (Draggable anywhere on screen)")

    p.end()
    out_path = os.path.join(OUT_DIR, "floating_ui_preview.png")
    img.save(out_path)
    print("Saved preview to:", out_path)


def render_architecture():
    width, height = 1000, 380
    img = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(QColor("#0F111A"))

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Title
    p.setPen(QColor("#FFFFFF"))
    p.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    p.drawText(QRectF(0, 24, width, 30), Qt.AlignmentFlag.AlignCenter, "Text 2 Voice System Architecture & Workflow")

    # Flowchart boxes
    steps = [
        {"num": "1", "title": "Global Hook", "sub": "pynput listener\nMouse drag / Hotkey", "color": "#6366F1"},
        {"num": "2", "title": "Safe Clipboard", "sub": "Silent Ctrl+C copy\nRestores user clipboard", "color": "#3B82F6"},
        {"num": "3", "title": "Floating Micro-UI", "sub": "PyQt6 translucent\nMic bubble & Mini Player", "color": "#06B6D4"},
        {"num": "4", "title": "Neural TTS Engine", "sub": "Edge-TTS Neural\nOffline SAPI5 Fallback", "color": "#10B981"},
        {"num": "5", "title": "JSON Storage", "sub": "history.json database\nReplay & favorites", "color": "#F59E0B"}
    ]

    box_w, box_h = 160, 150
    start_x = 45
    spacing = 190
    box_y = 95

    for i, s in enumerate(steps):
        bx = start_x + (i * spacing)

        # Card
        p.setBrush(QBrush(QColor("#181926")))
        p.setPen(QPen(QColor(s["color"]), 1.8))
        p.drawRoundedRect(QRectF(bx, box_y, box_w, box_h), 12, 12)

        # Header tag
        p.setBrush(QBrush(QColor(s["color"])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(bx + 12, box_y + 12, 28, 28), 14, 14)
        p.setPen(QColor("#FFFFFF"))
        p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        p.drawText(QRectF(bx + 12, box_y + 12, 28, 28), Qt.AlignmentFlag.AlignCenter, s["num"])

        # Title
        p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        p.drawText(QRectF(bx + 48, box_y + 16, box_w - 55, 24), Qt.AlignmentFlag.AlignLeft, s["title"])

        # Divider
        p.setPen(QPen(QColor("#313244"), 1))
        p.drawLine(QPointF(bx + 12, box_y + 52), QPointF(bx + box_w - 12, box_y + 52))

        # Description
        p.setPen(QColor("#CAD3F5"))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Normal))
        p.drawText(QRectF(bx + 12, box_y + 64, box_w - 24, 72), Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, s["sub"])

        # Draw connecting arrows between boxes
        if i < len(steps) - 1:
            ax = bx + box_w + 5
            ay = box_y + (box_h // 2)
            p.setPen(QPen(QColor("#89B4FA"), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(QPointF(ax, ay), QPointF(ax + 18, ay))
            p.drawLine(QPointF(ax + 12, ay - 5), QPointF(ax + 18, ay))
            p.drawLine(QPointF(ax + 12, ay + 5), QPointF(ax + 18, ay))

    # Bottom notes
    p.setPen(QColor("#939AB7"))
    p.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
    p.drawText(QRectF(0, 290, width, 50), Qt.AlignmentFlag.AlignCenter,
               "100% Asynchronous & Thread-Safe: Synthesis and audio never block the GUI event loop.\nCross-platform architecture engineered for instant porting to macOS.")

    p.end()
    out_path = os.path.join(OUT_DIR, "architecture.png")
    img.save(out_path)
    print("Saved architecture to:", out_path)


if __name__ == "__main__":
    render_banner()
    render_ui_preview()
    render_architecture()
