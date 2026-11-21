"""
Voxel design system (v2): one place for colours, fonts, outline icons and theme resolution.

Colours follow the hybrid "Notion simplicity + Apple quality" brief: flat surfaces, thin borders,
no gradients, one blue accent. Icons are Lucide outline icons (ISC licence, https://lucide.dev),
drawn at 24x24 with a 2px stroke and tinted at runtime.
"""
from PyQt6.QtCore import Qt, QByteArray, QRectF
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QGuiApplication
from PyQt6.QtSvg import QSvgRenderer

FONT_STACK = '"Inter", "Segoe UI Variable Text", "Segoe UI", "SF Pro Text", ".AppleSystemUIFont", "Helvetica Neue", sans-serif'

PALETTES = {
    "light": {
        "bg": "#FFFFFF", "sidebar": "#F7F7F7", "surface": "#FFFFFF", "surface2": "#F7F7F7",
        "border": "#EAEAEA", "text": "#222222", "muted": "#777777", "faint": "#A3A3A3",
        "accent": "#3478F6", "accent_hover": "#2A66D9", "accent_soft": "#EAF1FE",
        "accent_text": "#2A66D9", "track_off": "#DCDCDC", "ok": "#1F9D55", "warn": "#C77700",
    },
    "dark": {
        "bg": "#171717", "sidebar": "#202020", "surface": "#252525", "surface2": "#202020",
        "border": "#343434", "text": "#F5F5F5", "muted": "#A3A3A3", "faint": "#6E6E6E",
        "accent": "#6B9FFF", "accent_hover": "#8BB4FF", "accent_soft": "#1E2A40",
        "accent_text": "#8BB4FF", "track_off": "#3C3C3C", "ok": "#4ADE80", "warn": "#FBBF24",
    },
}

THEME_PREFS = ("light", "dark", "system")


def system_is_dark() -> bool:
    try:
        return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except Exception:
        return False


def resolve_theme(pref: str) -> str:
    """Maps a saved preference ('light' | 'dark' | 'system') to the theme to draw."""
    if pref == "system":
        return "dark" if system_is_dark() else "light"
    return "dark" if pref == "dark" else "light"


# Lucide outline icons (ISC licence). Only the shapes, colour is applied at render time.
_ICONS = {
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "audio-lines": '<path d="M2 10v3"/><path d="M6 6v11"/><path d="M10 3v18"/><path d="M14 8v7"/><path d="M18 5v13"/><path d="M22 10v3"/>',
    "play": '<polygon points="6 3 20 12 6 21 6 3"/>',
    "square": '<rect width="14" height="14" x="5" y="5" rx="2"/>',
    "palette": '<circle cx="13.5" cy="6.5" r=".5" fill="C"/><circle cx="17.5" cy="10.5" r=".5" fill="C"/><circle cx="8.5" cy="7.5" r=".5" fill="C"/><circle cx="6.5" cy="12.5" r=".5" fill="C"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "accessibility": '<circle cx="16" cy="4" r="1"/><path d="m18 19 1-7-6 1"/><path d="m5 8 3-3 5.5 3-2.36 3.5"/><path d="M4.24 14.5a5 5 0 0 0 6.88 6"/><path d="M13.76 17.5a5 5 0 0 0-6.88-6"/>',
    "clipboard": '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "monitor": '<rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/>',
    "folder-open": '<path d="m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2"/>',
    "pause": '<rect x="14" y="4" width="4" height="16" rx="1"/><rect x="6" y="4" width="4" height="16" rx="1"/>',
    "ellipsis": '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>',
    "settings-2": '<path d="M20 7h-9"/><path d="M14 17H5"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/>',
    "circle-dot": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="1"/>',
    "headphones": '<path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/>',
    "folder": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
    "copy": '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    "trash-2": '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/>',
    "panel-left": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "external-link": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "rotate-ccw": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
}


def icon_svg(name: str, color: str) -> str:
    body = _ICONS[name].replace('fill="C"', f'fill="{color}"')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')


def icon_pixmap(name: str, color: str, size: int = 18, dpr: float = 2.0) -> QPixmap:
    px = int(size * dpr)
    pm = QPixmap(px, px)
    pm.fill(Qt.GlobalColor.transparent)
    r = QSvgRenderer(QByteArray(icon_svg(name, color).encode()))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    r.render(p, QRectF(0, 0, px, px))
    p.end()
    pm.setDevicePixelRatio(dpr)
    return pm


def line_icon(name: str, color: str, checked_color: str = None, size: int = 18) -> QIcon:
    """Outline icon; optional second colour for the checked/active state (nav buttons)."""
    icon = QIcon()
    icon.addPixmap(icon_pixmap(name, color, size), QIcon.Mode.Normal, QIcon.State.Off)
    icon.addPixmap(icon_pixmap(name, checked_color or color, size), QIcon.Mode.Normal, QIcon.State.On)
    return icon
