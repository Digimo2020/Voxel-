"""
Generates every screenshot used in README.md and docs/HOW_TO_USE.md by running the REAL
Voxel windows off-screen (no display needed) and grabbing them.

Run from the repo root:   python scripts/generate_docs_images.py
Output:                   docs/images/*.png

Privacy: settings, history, startup state and the recordings folder are replaced with demo
values, so nothing from the machine that runs this ends up in the images.
"""
import os
import sys

os.environ.setdefault("QT_SCALE_FACTOR", "2")          # crisp 2x images
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
OUT = os.path.join(ROOT, "docs", "images")
os.makedirs(OUT, exist_ok=True)

from PyQt6.QtWidgets import QApplication, QScrollArea, QMenu
from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer
from PyQt6.QtGui import (QImage, QPainter, QColor, QFont, QFontMetrics, QPen, QBrush, QLinearGradient,
                         QPainterPath, QPolygonF, QPixmap)

app = QApplication(sys.argv)
SCALE = app.primaryScreen().devicePixelRatio()   # physical pixels per logical pixel

# ── Demo data (never touch the user's real data) ─────────────────────────────
from src.utils import settings as S
DEMO = {"settings_theme": "light", "default_voice": "en-US-JennyNeural", "default_speed": 1.0,
        "default_pitch": 0, "volume": 80, "bubble_transparency": 90, "bubble_size": "Large",
        "bubble_distance": 28, "bubble_corner_radius": "Medium", "bubble_appearance": "Frosted Glass",
        "smooth_fade_in": True, "prebuffer_enabled": True, "selection_popup_enabled": True,
        "auto_close_finished": True, "auto_close_delay": 1.0}
S.settings_db.get = lambda key, default=None: DEMO.get(key, default)
S.settings_db.set = lambda key, value: DEMO.__setitem__(key, value)

from src.utils import history as H
H.history_db.get_all = lambda: [
    {"timestamp": "2026-11-21 09:14", "voice": "Jenny", "speed": 1.0, "text": "x",
     "preview": "Neural voices make long articles easy to follow..."},
    {"timestamp": "2026-11-21 09:02", "voice": "Guy", "speed": 1.2, "text": "x",
     "preview": "Meeting notes: ship the new settings window on Friday."},
    {"timestamp": "2026-11-20 18:40", "voice": "Sonia", "speed": 1.0, "text": "x",
     "preview": "Chapter 3: The quiet city woke slowly that morning..."},
]

import src.ui.settings_dialog as SD
SD.is_startup_enabled = lambda: False
SD.get_recordings_dir = lambda: r"C:\Users\You\Documents\Voxel Recordings"

from src.tts_engine import TTSEngine
from src.ui.settings_dialog import SettingsDialog
from src.ui.floating_bubble import FloatingBubble
from src.ui.mini_player import MiniPlayer
from src.ui.history_dialog import HistoryDialog
from src.ui.tray_icon import AppTrayIcon as TrayIcon

PURPLE = QColor("#7C3AED")
FONT = "Segoe UI"


def pump(n=6):
    for _ in range(n):
        app.processEvents()


def offscreen(w):
    w.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    return w


def save(pix_or_img, name):
    """Saves at 2x logical size regardless of the machine's display scaling."""
    img = pix_or_img.toImage() if isinstance(pix_or_img, QPixmap) else pix_or_img
    target_w = round(img.width() * 2 / SCALE)
    if abs(target_w - img.width()) > 2:
        img = img.scaledToWidth(target_w, Qt.TransformationMode.SmoothTransformation)
    img.save(os.path.join(OUT, name), "PNG")
    print("saved", name)


# ── 1. Settings pages (light + dark) ─────────────────────────────────────────
def shoot_settings():
    d = offscreen(SettingsDialog(tts_engine=None))
    d.txt_reader.setPlainText(
        "Paste text from anywhere: a locked PDF, a web page that blocks copying, a chat message.\n\n"
        "Press Read aloud and Voxel reads it to you in the voice you picked.")
    d.show()
    names = {d.PAGE_READ: "read-text", d.PAGE_VOICE: "voice", d.PAGE_PLAYBACK: "playback",
             d.PAGE_APPEARANCE: "appearance", d.PAGE_ABOUT: "about"}
    for theme in ("light", "dark"):
        d.apply_theme(theme)
        for page, slug in names.items():
            d._go_to(page)
            d.resize(880, 640)
            pump()
            cur = d.stacked_pages.currentWidget()
            sa = cur if isinstance(cur, QScrollArea) else cur.findChild(QScrollArea)
            if sa is not None:  # grow the window so the whole page is visible
                extra = d.height() - sa.viewport().height()
                d.resize(880, min(1400, sa.widget().sizeHint().height() + extra + 4))
                pump()
            save(d.grab(), f"settings-{slug}-{theme}.png")
    d.resize(880, 640)
    d.apply_theme("light")
    d._go_to(d.PAGE_READ)
    pump()
    return d


# ── 2. Bubble + player + tray + history ──────────────────────────────────────
def grab_bubble(style="Frosted Glass", size="Large"):
    DEMO.update(bubble_appearance=style, bubble_size=size)
    b = offscreen(FloatingBubble())
    b.apply_settings()
    b.show()
    b.setWindowOpacity(1.0)
    pump()
    pm = b.grab()
    b.close()
    return pm


def grab_player(theme="light_glass", playing=False):
    m = offscreen(MiniPlayer(TTSEngine()))
    m.apply_theme(theme)
    m.show()
    if playing:
        m._on_playback_started()
    m.setWindowOpacity(1.0)
    for _ in range(25):
        pump(1)
    pm = m.grab()
    m.close()
    return pm


def card(w, h, bg="#FFFFFF", border="#E9E6F2"):
    img = QImage(int(w * SCALE), int(h * SCALE), QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(SCALE, SCALE)
    p.setBrush(QColor(bg))
    p.setPen(QPen(QColor(border), 1))
    p.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 14, 14)
    return img, p


def label(p, text, x, y, size=12, bold=False, color="#17142B", align=Qt.AlignmentFlag.AlignLeft, w=300):
    f = QFont(FONT, 1)
    f.setPixelSize(size)
    f.setBold(bold)
    p.setFont(f)
    p.setPen(QColor(color))
    p.drawText(QRectF(x, y, w, size + 8), align | Qt.AlignmentFlag.AlignVCenter, text)


def bubble_styles_image():
    styles = ["Default", "Frosted Glass", "Transparent", "Minimal"]
    W, H = 760, 250
    img, p = card(W, H)
    label(p, "Bubble styles", 24, 16, 15, True)
    cw = (W - 48 - 3 * 12) / 4
    for i, st in enumerate(styles):
        x = 24 + i * (cw + 12)
        p.setBrush(QColor("#F4F2FA")); p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(x, 50, cw, 70), 10, 10)
        pm = grab_bubble(st, "Large")
        p.drawPixmap(QPointF(x + (cw - pm.width() / pm.devicePixelRatio()) / 2, 50 + 15), pm)
        label(p, st, x, 124, 12, True, align=Qt.AlignmentFlag.AlignHCenter, w=cw)
    label(p, "Bubble sizes", 24, 156, 15, True)
    sizes = [("Small Dot", "Small"), ("Medium", "Medium"), ("Large", "Large")]
    cw = (W - 48 - 2 * 12) / 3
    for i, (val, name) in enumerate(sizes):
        x = 24 + i * (cw + 12)
        p.setBrush(QColor("#F4F2FA")); p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(x, 188, cw, 46), 10, 10)
        pm = grab_bubble("Frosted Glass", val)
        pw, ph = pm.width() / pm.devicePixelRatio(), pm.height() / pm.devicePixelRatio()
        p.drawPixmap(QPointF(x + 14, 188 + (46 - ph) / 2), pm)
        label(p, name, x + 14 + pw + 12, 188 + 12, 12, True, w=cw)
    p.end()
    DEMO.update(bubble_appearance="Frosted Glass", bubble_size="Large")
    save(img, "bubble-styles.png")


def player_image():
    W, H = 460, 190
    img, p = card(W, H)
    label(p, "Mini player", 24, 14, 15, True)
    for i, (theme, playing, cap) in enumerate([("light_glass", True, "Playing (light)"),
                                              ("dark_glass", True, "Playing (dark)")]):
        y = 52 + i * 66
        bg = "#EEF0F7" if i == 0 else "#2A2740"
        p.setBrush(QColor(bg)); p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(24, y, W - 48, 56), 12, 12)
        pm = grab_player(theme, playing)
        p.drawPixmap(QPointF(34, y + 4), pm)
    p.end()
    save(img, "player.png")


def tray_image(tts):
    tray = TrayIcon(tts)
    menu = tray.contextMenu()
    menu.adjustSize()
    pump()
    pm = menu.grab()
    save(pm, "tray-menu.png")


def history_image():
    h = offscreen(HistoryDialog())
    h.load_history()
    h.show()
    pump()
    save(h.grab(), "history.png")


# ── 3. Scenes: a fake article with the real bubble and player placed on it ───
def scene(step):
    W, H = 760, 430
    img = QImage(int(W * SCALE), int(H * SCALE), QImage.Format.Format_ARGB32_Premultiplied)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    p.scale(SCALE, SCALE)

    # wallpaper
    g = QLinearGradient(0, 0, W, H)
    g.setColorAt(0, QColor("#C7D2FE")); g.setColorAt(1, QColor("#E9D5FF"))
    p.fillRect(QRectF(0, 0, W, H), g)

    # window
    wx, wy, ww, wh = 40, 22, W - 80, H - 22 - 44
    p.setPen(QPen(QColor(0, 0, 0, 40), 1)); p.setBrush(QColor("#FFFFFF"))
    p.drawRoundedRect(QRectF(wx, wy, ww, wh), 10, 10)
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#F1F0F7"))
    path = QPainterPath(); path.addRoundedRect(QRectF(wx, wy, ww, 30), 10, 10)
    path.addRect(QRectF(wx, wy + 18, ww, 12)); p.drawPath(path)
    for i, c in enumerate(["#FB7185", "#FBBF24", "#34D399"]):
        p.setBrush(QColor(c)); p.drawEllipse(QPointF(wx + 18 + i * 16, wy + 15), 4.5, 4.5)
    p.setBrush(QColor("#FFFFFF")); p.drawRoundedRect(QRectF(wx + 80, wy + 7, ww - 160, 17), 8, 8)
    label(p, "reader.example.com/how-neural-voices-work", wx + 92, wy + 7, 10, False, "#6E6A86", w=ww - 180)

    # article
    label(p, "How neural voices work", wx + 36, wy + 46, 22, True, w=ww - 60)
    body = QFont(FONT, 1); body.setPixelSize(14)
    fm = QFontMetrics(body)
    lines = [("A neural network learns ", "how people really speak", " and then generates"),
             ("every sound from scratch, including pauses and emphasis.", "", ""),
             ("The result sounds natural, even for long articles.", "", "")]
    y = wy + 112
    sel_rect = None
    for before, sel, after in lines:
        p.setFont(body)
        x = wx + 36
        p.setPen(QColor("#3B3752"))
        p.drawText(QPointF(x, y + 12), before)
        x += fm.horizontalAdvance(before)
        if sel:
            sw = fm.horizontalAdvance(sel)
            sel_rect = QRectF(x - 1, y - 1, sw + 2, 20)
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#A5C8FF")); p.drawRect(sel_rect)
            p.setPen(QColor("#17142B")); p.drawText(QPointF(x, y + 12), sel)
            x += sw
            p.setPen(QColor("#3B3752")); p.drawText(QPointF(x, y + 12), after)
        y += 30
    for k in range(2):  # grey paragraph lines
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#E7E4F1"))
        p.drawRoundedRect(QRectF(wx + 36, y + 8 + k * 16, ww - 100 - k * 90, 7), 3.5, 3.5)

    # taskbar
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(255, 255, 255, 190))
    p.drawRect(QRectF(0, H - 44, W, 44))
    p.setBrush(QColor("#7C3AED"))
    for i in range(6):
        p.setBrush(QColor("#7C3AED") if i == 2 else QColor("#A9A5BC"))
        p.drawRoundedRect(QRectF(W / 2 - 80 + i * 28, H - 31, 18, 18), 5, 5)

    def badge(n, x, y):
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(PURPLE)
        p.drawEllipse(QPointF(x, y), 13, 13)
        label(p, str(n), x - 13, y - 13, 14, True, "#FFFFFF", Qt.AlignmentFlag.AlignHCenter, 26)

    def caption(text, x, y, w=230):
        f = QFont(FONT, 1); f.setPixelSize(13); f.setBold(True)
        fm2 = QFontMetrics(f); tw = fm2.horizontalAdvance(text) + 22
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#17142B"))
        p.drawRoundedRect(QRectF(x, y, tw, 28), 14, 14)
        label(p, text, x, y, 13, True, "#FFFFFF", Qt.AlignmentFlag.AlignHCenter, tw)

    def cursor(x, y):
        poly = QPolygonF([QPointF(x, y), QPointF(x, y + 17), QPointF(x + 4.5, y + 13),
                          QPointF(x + 8, y + 20), QPointF(x + 11, y + 18.5), QPointF(x + 7.5, y + 12), QPointF(x + 13, y + 12)])
        p.setPen(QPen(QColor("#FFFFFF"), 1.5)); p.setBrush(QColor("#111111")); p.drawPolygon(poly)

    bubble = grab_bubble("Frosted Glass", "Large")
    bw, bh = bubble.width() / bubble.devicePixelRatio(), bubble.height() / bubble.devicePixelRatio()
    bx = sel_rect.center().x() - bw / 2
    by = sel_rect.top() - bh - 8

    if step == 1:
        p.setPen(QPen(QColor("#2563EB"), 2)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(sel_rect.adjusted(-3, -3, 3, 3), 4, 4)
        cursor(sel_rect.right() + 4, sel_rect.center().y() + 2)
        badge(1, sel_rect.right() + 150, sel_rect.center().y() - 38)
        caption("Highlight any text", sel_rect.right() + 168, sel_rect.center().y() - 52)
    elif step == 2:
        p.drawPixmap(QPointF(bx, by), bubble)
        cursor(bx + bw * 0.25, by + bh * 0.55)
        p.setPen(QPen(QColor(124, 58, 237, 150), 2)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(bx + bw * 0.25, by + bh * 0.5), 20, 20)
        badge(2, bx + bw + 28, by + bh / 2)
        caption("Click the mic to listen", bx + bw + 46, by + bh / 2 - 14)
    else:
        player = grab_player("light_glass", True)
        pw, ph = player.width() / player.devicePixelRatio(), player.height() / player.devicePixelRatio()
        px, py = W - pw - 22, H - 44 - ph - 14
        p.drawPixmap(QPointF(px, py), player)
        badge(3, px - 20, py + ph / 2)
        caption("Voxel reads it aloud", px + 6, py - 38)
    p.end()
    return img


def how_it_works(imgs):
    cw, ch = imgs[0].width(), imgs[0].height()
    gap = 24
    out = QImage(cw * 3 + gap * 4, ch + 2 * gap, QImage.Format.Format_ARGB32_Premultiplied)
    out.fill(QColor("#FFFFFF"))
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    for i, im in enumerate(imgs):
        p.drawImage(gap + i * (cw + gap), gap, im)
    p.end()
    save(out.scaledToWidth(2200, Qt.TransformationMode.SmoothTransformation), "how-it-works.png")


def annotated_read_text(dialog):
    dialog.apply_theme("light")
    dialog._go_to(dialog.PAGE_READ)
    dialog.resize(880, 640)
    pump()
    pm = dialog.grab()
    img = pm.toImage()
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    def mark(n, x, y, text, tx, ty):
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(PURPLE)
        p.drawEllipse(QPointF(x, y), 13, 13)
        label(p, str(n), x - 13, y - 13, 14, True, "#FFFFFF", Qt.AlignmentFlag.AlignHCenter, 26)
        f = QFont(FONT, 1); f.setPixelSize(13); f.setBold(True)
        tw = QFontMetrics(f).horizontalAdvance(text) + 22
        p.setBrush(QColor("#17142B")); p.drawRoundedRect(QRectF(tx, ty, tw, 28), 14, 14)
        label(p, text, tx, ty, 13, True, "#FFFFFF", Qt.AlignmentFlag.AlignHCenter, tw)

    def where(widget):
        c = widget.mapTo(dialog, widget.rect().center())
        return c.x(), c.y()

    bx, by = where(dialog.btn_read)
    mark(3, bx - 120, by - 52, "Press Read aloud", bx - 102, by - 66)
    tx, ty = where(dialog.txt_reader)
    mark(2, tx - 160, ty + 20, "Type or paste your text", tx - 140, ty + 6)
    paste = [b for b in dialog.findChildren(type(dialog.btn_read)) if b.text().strip().endswith("Paste")]
    if paste:
        px, py = where(paste[0])
        mark(1, px, py - 52, "Paste from clipboard", px + 18, py - 66)
    p.end()
    save(QPixmap.fromImage(img), "read-text-annotated.png")


def main():
    dialog = shoot_settings()
    bubble_styles_image()
    player_image()
    tray_image(TTSEngine())
    imgs = [scene(1), scene(2), scene(3)]
    for i, im in enumerate(imgs, 1):
        save(im, f"step{i}-" + ["select", "click", "listen"][i - 1] + ".png")
    how_it_works(imgs)
    annotated_read_text(dialog)
    print("done ->", OUT)


if __name__ == "__main__":
    main()
