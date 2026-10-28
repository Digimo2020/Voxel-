"""
Voxel theme primitives for a compact floating TTS player.
Both dark and glass styles use the approved purple-to-blue brand accents.
"""
from PyQt6.QtGui import QColor

VOXEL_COLORS = {
    "purple": "#6847FF",
    "blue": "#168BFF",
    "navy": "#111B2E",
    "dark_surface": "#151C2B",
    "dark_surface_alt": "#20283A",
    "dark_text": "#F8FAFF",
    "dark_muted": "#9AA6BC",
    "light_surface": "#F8FAFF",
    "light_text": "#111B2E",
    "light_muted": "#667085",
    "border_light": "rgba(255,255,255,0.18)",
    "glass_edge": "rgba(255,255,255,0.54)",
}


def player_styles(mode: str = "dark") -> dict[str, str]:
    """Return stylesheet tokens for dark or glass player appearance."""
    if mode.lower() == "glass":
        return {
            "surface": "rgba(232, 240, 255, 0.76)",
            "surface_alt": "rgba(255, 255, 255, 0.50)",
            "border": "rgba(255, 255, 255, 0.86)",
            "text": "#18243A",
            "muted": "#596982",
            "separator": "rgba(80, 105, 150, 0.22)",
            "button": "rgba(255, 255, 255, 0.58)",
            "button_hover": "rgba(255, 255, 255, 0.84)",
            "accent": VOXEL_COLORS["blue"],
            "stop": "#D95565",
        }
    return {
        "surface": "#151C2B",
        "surface_alt": "#20283A",
        "border": "rgba(255, 255, 255, 0.12)",
        "text": "#F8FAFF",
        "muted": "#A7B2C6",
        "separator": "rgba(255, 255, 255, 0.14)",
        "button": "rgba(255, 255, 255, 0.07)",
        "button_hover": "rgba(255, 255, 255, 0.14)",
        "accent": VOXEL_COLORS["blue"],
        "stop": "#F87171",
    }
