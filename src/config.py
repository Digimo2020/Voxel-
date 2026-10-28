"""
Configuration settings for Text 2 Voice.
"""
import sys

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

# UI Settings
BUBBLE_SIZE = 38
BUBBLE_TIMEOUT_SECONDS = 4.0
MIN_SELECTED_LENGTH = 2
DRAG_THRESHOLD_PIXELS = 8

# Hotkey fallback (e.g. Ctrl+Alt+S on Windows, Cmd+Alt+S on Mac)
HOTKEY_WINDOWS = "<ctrl>+<alt>+s"
HOTKEY_MAC = "<cmd>+<alt>+s"

# Modern Dark UI Theme Palettes
THEME = {
    "bg_bubble": "#6366F1",         # Indigo accent
    "bg_bubble_hover": "#4F46E5",
    "bg_player": "#1E1E2E",         # Deep slate dark
    "border_player": "#313244",
    "text_primary": "#CDD6F4",
    "text_secondary": "#A6ADC8",
    "accent": "#89B4FA",           # Soft blue accent
    "accent_hover": "#B4BEFE",
    "button_bg": "#313244",
    "button_hover": "#45475A",
    "button_active": "#585B70",
    "stop_bg": "#F38BA8",          # Soft coral red
    "stop_hover": "#EBA0AC"
}

IS_MAC = sys.platform == "darwin"
