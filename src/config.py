"""
Configuration settings for Text 2 Voice.
"""
import sys
from src.utils.version import CURRENT_VERSION, GITHUB_REPO_URL

VERSION = CURRENT_VERSION
GITHUB_URL = GITHUB_REPO_URL

# Voice Profiles
VOICES = [
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny (Female)",
        "gender": "Female",
        "country": "US",
        "label": "Jenny (US Female)",
        "short_label": "Jenny"
    },
    {
        "id": "en-US-GuyNeural",
        "name": "Guy (Male)",
        "gender": "Male",
        "country": "US",
        "label": "Guy (US Male)",
        "short_label": "Guy"
    },
    {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia (Female)",
        "gender": "Female",
        "country": "UK",
        "label": "Sonia (UK Female)",
        "short_label": "Sonia"
    }
]

# Offline Fallback Voice IDs (SAPI5 on Windows, NSSpeech on Mac)
OFFLINE_VOICE_FEMALE = "Zira"
OFFLINE_VOICE_MALE = "David"

# Playback Speed Presets
SPEED_STEPS = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
DEFAULT_SPEED = 1.0
DEFAULT_VOICE_INDEX = 0  # Jenny (US Female)

# UI Settings - Refined Minimalist Glass Aesthetic
BUBBLE_SIZE = 30                # Slightly bigger (30px) for easier clicking, pure transparent glass
BUBBLE_TIMEOUT_SECONDS = 4.0
MIN_SELECTED_LENGTH = 2
DRAG_THRESHOLD_PIXELS = 8

# Hotkey fallback (e.g. Ctrl+Alt+S on Windows, Cmd+Alt+S on Mac)
HOTKEY_WINDOWS = "<ctrl>+<alt>+s"
HOTKEY_MAC = "<cmd>+<alt>+s"

# Refined Frosted Glass Palettes
THEME = {
    # Transparent Glass Bubble Trigger (No dark black background!)
    "bubble_bg": "rgba(255, 255, 255, 0.12)",
    "bubble_border": "rgba(255, 255, 255, 0.35)",
    "bubble_hover_bg": "rgba(96, 165, 250, 0.25)",
    "bubble_hover_border": "rgba(96, 165, 250, 0.75)",

    # Frosted Glass Mini Player Backgrounds
    "glass_bg": "rgba(22, 25, 38, 0.82)",
    "glass_border": "rgba(255, 255, 255, 0.18)",
    "glass_border_subtle": "rgba(255, 255, 255, 0.10)",
    
    # Text
    "text_primary": "#E2E8F0",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    
    # Dialogs & Panels
    "bg_player": "#161926",
    "border_player": "#2A3048",
    "button_bg": "#22273B",
    "button_hover": "#313854",
    "button_active": "#3E4668",
    "accent": "#60A5FA",
    "accent_hover": "#93C5FD",

    # Line Art Accent Buttons
    "accent_line": "#60A5FA",
    "accent_bg": "rgba(96, 165, 250, 0.15)",
    "accent_hover_bg": "rgba(96, 165, 250, 0.28)",
    
    # Neutral Circle Buttons
    "btn_glass": "rgba(255, 255, 255, 0.06)",
    "btn_glass_border": "rgba(255, 255, 255, 0.16)",
    "btn_glass_hover": "rgba(255, 255, 255, 0.14)",
    "btn_glass_active": "rgba(255, 255, 255, 0.22)",
    
    # Stop / Danger
    "stop_line": "#F87171",
    "stop_bg": "rgba(248, 113, 113, 0.15)",
    "stop_hover_bg": "rgba(248, 113, 113, 0.28)"
}

IS_MAC = sys.platform == "darwin"
