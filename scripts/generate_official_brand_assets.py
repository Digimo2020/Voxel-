#!/usr/bin/env python3
"""
generate_official_brand_assets.py
---------------------------------
Builds production-grade, anti-aliased, alpha-transparent brand assets
for macOS (.icns, .app) and Windows (.ico, .exe) from official source logos in:
- assets/Fainal/Voxel Logo (1)/
- assets/Fainal/
"""

import os
import sys
import math
import struct
import subprocess
from PyQt6.QtGui import QImage, QColor, QPainter
from PyQt6.QtCore import Qt, QRect, QByteArray, QBuffer, QIODevice

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
BRANDING_PNG = os.path.join(ASSETS_DIR, "branding", "png")
ICONSET_DIR = os.path.join(ASSETS_DIR, "icon.iconset")

os.makedirs(BRANDING_PNG, exist_ok=True)
os.makedirs(ICONSET_DIR, exist_ok=True)

def process_circle(src_path: str, dest_path: str, target_size: int = 512):
    """
    Extracts an elliptical/circular emblem from a solid background
    with smooth anti-aliased edge alpha masking and centers it in target_size x target_size.
    """
    src = QImage(src_path)
    if src.isNull():
        raise FileNotFoundError(f"Cannot load image: {src_path}")
    w, h = src.width(), src.height()

    # Find bounding box of non-white / non-black content
    # Detect background color from pixel (0, 0)
    bg = src.pixelColor(0, 0)
    is_dark_bg = (bg.red() < 30 and bg.green() < 30 and bg.blue() < 30)

    min_x, max_x, min_y, max_y = w, 0, h, 0
    for y in range(h):
        for x in range(w):
            c = src.pixelColor(x, y)
            is_bg = (c.red() < 25 and c.green() < 25 and c.blue() < 25) if is_dark_bg else (c.red() > 240 and c.green() > 240 and c.blue() > 240)
            if not is_bg:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y

    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    rx = (max_x - min_x + 1) / 2.0
    ry = (max_y - min_y + 1) / 2.0

    cropped = QImage(w, h, QImage.Format.Format_ARGB32)
    cropped.fill(Qt.GlobalColor.transparent)

    for y in range(h):
        for x in range(w):
            c = src.pixelColor(x, y)
            nx = (x - cx) / rx
            ny = (y - cy) / ry
            d = math.sqrt(nx * nx + ny * ny)
            if d <= 0.995:
                cropped.setPixelColor(x, y, c)
            elif d >= 1.008:
                cropped.setPixelColor(x, y, QColor(0, 0, 0, 0))
            else:
                t = (1.008 - d) / (1.008 - 0.995)
                alpha = int(255 * (t * t * (3 - 2 * t)))
                c.setAlpha(alpha)
                cropped.setPixelColor(x, y, c)

    bbox_img = cropped.copy(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    final_img = QImage(target_size, target_size, QImage.Format.Format_ARGB32)
    final_img.fill(Qt.GlobalColor.transparent)

    p = QPainter(final_img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    pad = int(target_size * 0.03)
    target_rect = QRect(pad, pad, target_size - 2 * pad, target_size - 2 * pad)
    scaled = bbox_img.scaled(target_rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    off_x = (target_size - scaled.width()) // 2
    off_y = (target_size - scaled.height()) // 2
    p.drawImage(off_x, off_y, scaled)
    p.end()

    final_img.save(dest_path, "PNG")
    print(f"Generated circle emblem: {dest_path} ({target_size}x{target_size})")
    return final_img

def make_transparent_wordmark(src_path: str, dest_path: str, is_dark_bg: bool = False):
    """Extracts horizontal wordmark with alpha blending."""
    src = QImage(src_path)
    if src.isNull():
        raise FileNotFoundError(f"Cannot load image: {src_path}")
    w, h = src.width(), src.height()
    out = QImage(w, h, QImage.Format.Format_ARGB32)
    out.fill(Qt.GlobalColor.transparent)

    for y in range(h):
        for x in range(w):
            c = src.pixelColor(x, y)
            if is_dark_bg:
                bright = max(c.red(), c.green(), c.blue())
                if bright <= 10:
                    out.setPixelColor(x, y, QColor(0, 0, 0, 0))
                elif bright >= 50:
                    out.setPixelColor(x, y, c)
                else:
                    alpha = int(255 * (bright - 10) / 40.0)
                    c.setAlpha(alpha)
                    out.setPixelColor(x, y, c)
            else:
                diff = 255 - min(c.red(), c.green(), c.blue())
                if diff <= 5:
                    out.setPixelColor(x, y, QColor(0, 0, 0, 0))
                elif diff >= 45:
                    out.setPixelColor(x, y, c)
                else:
                    alpha = int(255 * (diff - 5) / 40.0)
                    c.setAlpha(alpha)
                    out.setPixelColor(x, y, c)

    out.save(dest_path, "PNG")
    print(f"Generated wordmark: {dest_path}")
    return out

def create_multi_ico(master_img: QImage, out_path: str, sizes=[256, 128, 64, 48, 32, 24, 16]):
    """Packages multi-resolution PNG streams into Windows .ico."""
    png_buffers = []
    for s in sizes:
        scaled = master_img.scaled(s, s, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        scaled.save(buf, "PNG")
        buf.close()
        png_buffers.append((s, bytes(ba)))

    num_images = len(png_buffers)
    header = struct.pack("<HHH", 0, 1, num_images)
    entries = []
    offset = 6 + 16 * num_images
    data_bytes = bytearray()

    for s, raw in png_buffers:
        w_byte = 0 if s == 256 else s
        h_byte = 0 if s == 256 else s
        size_bytes = len(raw)
        entry = struct.pack("<BBBBHHII", w_byte, h_byte, 0, 0, 1, 32, size_bytes, offset)
        entries.append(entry)
        data_bytes.extend(raw)
        offset += size_bytes

    with open(out_path, "wb") as f:
        f.write(header)
        for e in entries:
            f.write(e)
        f.write(data_bytes)
    print(f"Generated Windows multi-res ICO: {out_path} ({len(sizes)} resolutions)")

def create_mac_icns(master_img: QImage, iconset_dir: str, icns_path: str):
    """Generates all standard macOS iconset sizes and compiles into .icns using iconutil."""
    icon_defs = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]

    for filename, s in icon_defs:
        scaled = master_img.scaled(s, s, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        p = os.path.join(iconset_dir, filename)
        scaled.save(p, "PNG")

    res = subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error compiling icns: {res.stderr}")
    else:
        print(f"Successfully compiled native macOS .icns: {icns_path}")

def main():
    print("=== Generating Voxel Official Brand Assets ===")

    # 1. Official App Emblem (Purple with Cyan Ring & White Mic)
    src_app = os.path.join(ASSETS_DIR, "Fainal", "Voxel Logo (1)", "apps icon (2).png")
    if not os.path.exists(src_app):
        src_app = os.path.join(ASSETS_DIR, "Fainal", "Voxel Logo for apps.png")

    app_logo_512 = process_circle(src_app, os.path.join(BRANDING_PNG, "app_logo.png"), 512)
    process_circle(src_app, os.path.join(BRANDING_PNG, "app_logo_square.png"), 512)
    process_circle(src_app, os.path.join(BRANDING_PNG, "tray_bar_logo.png"), 512)
    process_circle(src_app, os.path.join(BRANDING_PNG, "tray_bar_logo_square.png"), 512)
    process_circle(src_app, os.path.join(BRANDING_PNG, "selection_bubble_logo.png"), 512)
    process_circle(src_app, os.path.join(BRANDING_PNG, "selection_bubble_logo_square.png"), 512)

    # Master 1024x1024 for macOS
    app_logo_1024 = process_circle(src_app, os.path.join(ASSETS_DIR, "icon_1024.png"), 1024)

    # 2. Official Document Reader Emblem (Purple with White Document)
    src_doc = os.path.join(ASSETS_DIR, "Fainal", "Voxel Logo (1)", "dock icon.png")
    if not os.path.exists(src_doc):
        src_doc = os.path.join(ASSETS_DIR, "Fainal", "Voxel Logo for Doc.png")
    process_circle(src_doc, os.path.join(BRANDING_PNG, "selection_bubble_doc.png"), 512)
    process_circle(src_doc, os.path.join(BRANDING_PNG, "selection_bubble_doc_square.png"), 512)

    # 3. Horizontal Wordmarks (Light & Dark)
    src_wm_light = os.path.join(ASSETS_DIR, "Fainal", "Voxel Logo (1)", "Main logo Light.png")
    src_wm_dark = os.path.join(ASSETS_DIR, "Fainal", "Voxel Logo Main Dark.png")
    make_transparent_wordmark(src_wm_light, os.path.join(BRANDING_PNG, "voxel_logo_main_light.png"), is_dark_bg=False)
    make_transparent_wordmark(src_wm_dark, os.path.join(BRANDING_PNG, "voxel_logo_main_dark.png"), is_dark_bg=True)

    # 4. Windows .ico
    create_multi_ico(app_logo_512, os.path.join(ASSETS_DIR, "icon.ico"))

    # 5. macOS .icns
    create_mac_icns(app_logo_1024, ICONSET_DIR, os.path.join(ASSETS_DIR, "icon.icns"))

    print("=== All Brand Assets Successfully Generated! ===")

if __name__ == "__main__":
    main()
