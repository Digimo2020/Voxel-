"""
Voxel brand v2: minimal waveform identity (no microphone, no gradients, no glow).

Writes:
  assets/brand/*.svg                 scalable masters (mark A, mark B, app icon, monochrome)
  docs/images/logo-options.png       side-by-side comparison sheet
  with --apply: replaces the PNG/ICO/ICNS files the app already loads
                (assets/branding/png/*, assets/icon.ico, assets/icon.icns, assets/icon_1024.png)

Run:  python scripts/generate_brand_v2.py            (preview only)
      python scripts/generate_brand_v2.py --apply A  (apply mark A or B)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRectF, QByteArray, QPointF
from PyQt6.QtGui import QImage, QPainter, QColor, QFont, QPen
from PyQt6.QtSvg import QSvgRenderer

app = QApplication.instance() or QApplication(sys.argv)

ACCENT = "#3478F6"          # design-system accent (light)
ACCENT_DARK = "#6B9FFF"     # design-system accent (dark)
INK = "#222222"
PAPER = "#FFFFFF"
FONT = "Segoe UI"           # Inter preferred when bundled

# ── Marks: bars in a 100x100 box (x, y, w, h) — all fully rounded ────────────
MARKS = {
    # A: the owner's idea, refined: three bars, centered, 1 : 2 ratio
    "A": [(20, 31, 17, 38), (41.5, 12, 17, 76), (63, 31, 17, 38)],
    # B: "V-wave": five bars hang from one top line; their ends draw a V
    "B": [(14, 24, 11, 22), (29, 24, 11, 36), (44.5, 24, 11, 52), (60, 24, 11, 36), (75, 24, 11, 22)],
}


def mark_svg(key: str, color: str, size: int = 100, pad: float = 0.0, bg: str = None, bg_radius: float = 0.0) -> str:
    bars = MARKS[key]
    s = (100 - 2 * pad) / 100.0
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}">']
    if bg:
        parts.append(f'<rect width="100" height="100" rx="{bg_radius}" fill="{bg}"/>')
    for x, y, w, h in bars:
        parts.append(f'<rect x="{pad + x * s:.2f}" y="{pad + y * s:.2f}" width="{w * s:.2f}" height="{h * s:.2f}" '
                     f'rx="{w * s / 2:.2f}" fill="{color}"/>')
    parts.append("</svg>")
    return "".join(parts)


def app_icon_svg(key: str, accent: str = ACCENT) -> str:
    # macOS-style squircle-ish rounded square, white bars, no gradient
    return mark_svg(key, "#FFFFFF", pad=16, bg=accent, bg_radius=22.5)


def bubble_svg(key: str, accent: str = ACCENT) -> str:
    # circle badge used inside the floating bubble and mini player
    bars = MARKS[key]
    s, pad = 0.62, 19
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">',
           f'<circle cx="50" cy="50" r="50" fill="{accent}"/>']
    for x, y, w, h in bars:
        out.append(f'<rect x="{pad + x * s:.2f}" y="{pad + y * s:.2f}" width="{w * s:.2f}" height="{h * s:.2f}" '
                   f'rx="{w * s / 2:.2f}" fill="#FFFFFF"/>')
    out.append("</svg>")
    return "".join(out)


def doc_bubble_svg(accent: str = ACCENT) -> str:
    # outline file-text glyph (Lucide style) in white on the same circle
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            f'<circle cx="50" cy="50" r="50" fill="{accent}"/>'
            '<g fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M57 25H38a6 6 0 0 0-6 6v38a6 6 0 0 0 6 6h24a6 6 0 0 0 6-6V36z"/>'
            '<path d="M56 25v12h12"/><path d="M41 51h18"/><path d="M41 62h18"/></g></svg>')


def render(svg: str, w: int, h: int = None) -> QImage:
    h = h or w
    img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(0)
    r = QSvgRenderer(QByteArray(svg.encode()))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    r.render(p, QRectF(0, 0, w, h))
    p.end()
    return img


def wordmark(key: str, dark: bool, width: int = 1200) -> QImage:
    """Mark + 'Voxel' wordmark (transparent background)."""
    h = int(width * 0.30)
    img = QImage(width, h, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    icon = render(app_icon_svg(key, ACCENT_DARK if dark else ACCENT), int(h * 0.82))
    p.drawImage(int(h * 0.09), int(h * 0.09), icon)
    f = QFont(FONT)
    f.setPixelSize(int(h * 0.50))
    f.setWeight(QFont.Weight.DemiBold)
    p.setFont(f)
    p.setPen(QColor("#F5F5F5" if dark else INK))
    p.drawText(QRectF(h * 1.08, 0, width - h * 1.1, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "Voxel")
    p.end()
    return img


def comparison_sheet(path: str):
    W, H = 1400, 820
    img = QImage(W, H, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(QColor("#FFFFFF"))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    def text(t, x, y, px=22, bold=False, color=INK):
        f = QFont(FONT); f.setPixelSize(px); f.setWeight(QFont.Weight.DemiBold if bold else QFont.Weight.Normal)
        p.setFont(f); p.setPen(QColor(color)); p.drawText(QPointF(x, y), t)

    titles = {"A": "A  ·  Waveform (your idea, refined)  ✓ chosen", "B": "B  ·  V-wave (bars draw a V)  · alternative"}
    for row, key in enumerate(["A", "B"]):
        y0 = 30 + row * 395
        text(titles[key], 40, y0 + 10, 26, True)
        # light panel
        p.setPen(QPen(QColor("#EAEAEA"), 2)); p.setBrush(QColor("#F7F7F7"))
        p.drawRoundedRect(QRectF(40, y0 + 30, 640, 340), 14, 14)
        p.drawImage(70, y0 + 55, render(app_icon_svg(key), 140))
        for i, s in enumerate([64, 32, 16]):
            p.drawImage(290 + i * 90, y0 + 60 + (64 - s) // 2, render(app_icon_svg(key), s))
            text(f"{s}px", 290 + i * 90, y0 + 150, 14, False, "#777777")
        p.drawImage(560, y0 + 66, render(mark_svg(key, INK), 70))
        text("mono", 572, y0 + 150, 14, False, "#777777")
        p.drawImage(60, y0 + 230, wordmark(key, False, 400))
        # dark panel
        p.setPen(QPen(QColor("#343434"), 2)); p.setBrush(QColor("#171717"))
        p.drawRoundedRect(QRectF(720, y0 + 30, 640, 340), 14, 14)
        p.drawImage(750, y0 + 55, render(app_icon_svg(key, ACCENT_DARK), 140))
        for i, s in enumerate([64, 32, 16]):
            p.drawImage(970 + i * 90, y0 + 60 + (64 - s) // 2, render(app_icon_svg(key, ACCENT_DARK), s))
        p.drawImage(1240, y0 + 66, render(mark_svg(key, "#F5F5F5"), 70))
        # bubble preview
        bub = QImage(150, 72, QImage.Format.Format_ARGB32_Premultiplied); bub.fill(0)
        bp = QPainter(bub); bp.setRenderHint(QPainter.RenderHint.Antialiasing)
        bp.setPen(QPen(QColor("#EAEAEA"), 2)); bp.setBrush(QColor("#FFFFFF"))
        bp.drawRoundedRect(QRectF(2, 2, 146, 68), 34, 34)
        bp.drawImage(14, 12, render(bubble_svg(key), 48)); bp.drawImage(88, 12, render(doc_bubble_svg(), 48))
        bp.setPen(QPen(QColor("#EAEAEA"), 2)); bp.drawLine(75, 16, 75, 56); bp.end()
        p.drawImage(1180, y0 + 250, bub)
        text("bubble", 1225, y0 + 345, 14, False, "#A3A3A3")
        p.drawImage(740, y0 + 230, wordmark(key, True, 400))
    p.end()
    img.save(path)
    print("saved", os.path.relpath(path, ROOT))


def write_masters():
    out = os.path.join(ROOT, "assets", "brand")
    os.makedirs(out, exist_ok=True)
    for key in MARKS:
        files = {
            f"voxel-mark-{key.lower()}.svg": mark_svg(key, INK),
            f"voxel-mark-{key.lower()}-white.svg": mark_svg(key, "#FFFFFF"),
            f"voxel-app-icon-{key.lower()}.svg": app_icon_svg(key),
            f"voxel-app-icon-{key.lower()}-dark.svg": app_icon_svg(key, ACCENT_DARK),
            f"voxel-bubble-{key.lower()}.svg": bubble_svg(key),
        }
        for name, svg in files.items():
            with open(os.path.join(out, name), "w", encoding="utf-8") as f:
                f.write(svg)
    with open(os.path.join(out, "voxel-bubble-doc.svg"), "w", encoding="utf-8") as f:
        f.write(doc_bubble_svg())
    print("saved assets/brand/*.svg")


def apply(key: str):
    """Overwrites the raster assets the app already loads, so every window picks up the new identity."""
    png = os.path.join(ROOT, "assets", "branding", "png")
    icon = render(app_icon_svg(key), 512)
    for name in ["app_logo.png", "app_logo_square.png", "tray_bar_logo.png", "tray_bar_logo_square.png"]:
        icon.save(os.path.join(png, name))
    bub = render(bubble_svg(key), 512)
    for name in ["selection_bubble_logo.png", "selection_bubble_logo_square.png"]:
        bub.save(os.path.join(png, name))
    doc = render(doc_bubble_svg(), 512)
    for name in ["selection_bubble_doc.png", "selection_bubble_doc_square.png"]:
        doc.save(os.path.join(png, name))
    wordmark(key, False).save(os.path.join(png, "voxel_logo_main_light.png"))
    wordmark(key, True).save(os.path.join(png, "voxel_logo_main_dark.png"))
    big = render(app_icon_svg(key), 1024)
    big.save(os.path.join(ROOT, "assets", "icon_1024.png"))

    from PIL import Image
    tmp = os.path.join(ROOT, "assets", "icon_1024.png")
    im = Image.open(tmp).convert("RGBA")
    im.save(os.path.join(ROOT, "assets", "icon.ico"), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    im.save(os.path.join(ROOT, "assets", "icon.icns"))
    print(f"applied mark {key}: branding/png/*, icon.ico, icon.icns, icon_1024.png")


if __name__ == "__main__":
    write_masters()
    os.makedirs(os.path.join(ROOT, "docs", "images"), exist_ok=True)
    comparison_sheet(os.path.join(ROOT, "docs", "images", "logo-options.png"))
    if "--apply" in sys.argv:
        apply(sys.argv[sys.argv.index("--apply") + 1].upper())
