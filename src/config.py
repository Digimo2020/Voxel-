"""Configuration for Voxel."""
import sys
from src.utils.version import CURRENT_VERSION, GITHUB_REPO_URL

VERSION = CURRENT_VERSION
GITHUB_URL = GITHUB_REPO_URL

VOICES = [
    {"id":"en-US-JennyNeural","name":"Jenny (Female)","gender":"Female","country":"US","label":"Jenny (US Female)","short_label":"Jenny"},
    {"id":"en-US-GuyNeural","name":"Guy (Male)","gender":"Male","country":"US","label":"Guy (US Male)","short_label":"Guy"},
    {"id":"en-GB-SoniaNeural","name":"Sonia (Female)","gender":"Female","country":"UK","label":"Sonia (UK Female)","short_label":"Sonia"},
]

OFFLINE_VOICE_FEMALE = "Zira"
OFFLINE_VOICE_MALE = "David"
SPEED_STEPS = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
DEFAULT_SPEED = 1.0
DEFAULT_VOICE_INDEX = 0

BUBBLE_SIZE = 30
BUBBLE_TIMEOUT_SECONDS = 4.0
MIN_SELECTED_LENGTH = 2
DRAG_THRESHOLD_PIXELS = 8
HOTKEY_WINDOWS = "<ctrl>+<alt>+s"
HOTKEY_MAC = "<cmd>+<alt>+s"

# Brand values: keep aligned with assets/branding/voxel-logo.svg.
BRAND = {
    "purple": "#6847FF",
    "blue": "#168BFF",
    "navy": "#111B2E",
}
THEME = {
    "bubble_bg": "rgba(255, 255, 255, 0.12)",
    "bubble_border": "rgba(255, 255, 255, 0.35)",
    "bubble_hover_bg": "rgba(104, 71, 255, 0.20)",
    "bubble_hover_border": "rgba(22, 139, 255, 0.78)",
    "glass_bg": "rgba(235, 241, 255, 0.78)",
    "glass_border": "rgba(255, 255, 255, 0.72)",
    "glass_border_subtle": "rgba(255, 255, 255, 0.30)",
    "text_primary": "#F8FAFF",
    "text_secondary": "#A7B2C6",
    "text_muted": "#667085",
    "bg_player": "#151C2B",
    "border_player": "#2A344A",
    "button_bg": "#20283A",
    "button_hover": "#2B3853",
    "button_active": "#3C4E75",
    "accent": "#168BFF",
    "accent_hover": "#6847FF",
    "accent_line": "#168BFF",
    "accent_bg": "rgba(22, 139, 255, 0.15)",
    "accent_hover_bg": "rgba(104, 71, 255, 0.22)",
    "btn_glass": "rgba(255, 255, 255, 0.08)",
    "btn_glass_border": "rgba(255, 255, 255, 0.18)",
    "btn_glass_hover": "rgba(255, 255, 255, 0.16)",
    "btn_glass_active": "rgba(255, 255, 255, 0.24)",
    "stop_line": "#F87171",
    "stop_bg": "rgba(248, 113, 113, 0.15)",
    "stop_hover_bg": "rgba(248, 113, 113, 0.28)",
}
IS_MAC = sys.platform == "darwin"
