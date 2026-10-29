"""
Configuration settings for Voxel (Text to Speech, Anywhere).
Supports cross-platform presets, macOS native design tokens, and neural voice profiles.
"""
import sys
import os
from src.utils.version import CURRENT_VERSION, GITHUB_REPO_URL

APP_NAME = "Voxel"
APP_TAGLINE = "TEXT TO SPEECH, ANYWHERE"
VERSION = CURRENT_VERSION
GITHUB_URL = GITHUB_REPO_URL
COMPANY_NAME = "Digimo"
COMPANY_URL = "https://www.digimo.pt/"
IS_MAC = sys.platform == "darwin"

# Voice Profiles (Edge-TTS Neural Voices)
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
    },
    {
        "id": "en-US-AriaNeural",
        "name": "Aria (Female)",
        "gender": "Female",
        "country": "US",
        "label": "Aria (US Female)",
        "short_label": "Aria"
    }
]

# Offline Fallback Voice IDs (macOS native 'say' or SAPI5 on Windows)
if IS_MAC:
    OFFLINE_VOICE_FEMALE = "Samantha"
    OFFLINE_VOICE_MALE = "Alex"
else:
    OFFLINE_VOICE_FEMALE = "Zira"
    OFFLINE_VOICE_MALE = "David"

# Playback Speed Presets
SPEED_STEPS = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
DEFAULT_SPEED = 1.0
DEFAULT_VOICE_INDEX = 0  # Jenny (US Female)

# UI Settings
BUBBLE_SIZE = 38                # Ergonomic 38px floating badge holding the Voxel logo
BUBBLE_TIMEOUT_SECONDS = 4.0
MIN_SELECTED_LENGTH = 2
DRAG_THRESHOLD_PIXELS = 8

# Hotkey fallback (Cmd+Alt+S on Mac, Ctrl+Alt+S on Windows)
HOTKEY_WINDOWS = "<ctrl>+<alt>+s"
HOTKEY_MAC = "<cmd>+<alt>+s"

# System font stack
FONT_FAMILY = '".AppleSystemUIFont", "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Segoe UI", sans-serif'

# Voxel Official Brand Tokens & Frosted Glass Palette
THEME = {
    # Brand Primary Gradients
    "cradle_purple": "#7C3AED",
    "cradle_indigo": "#6366F1",
    "cradle_blue": "#0084FF",
    "cradle_cyan": "#00C6FF",
    
    # Play / Active Glow
    "glow_color": "rgba(0, 132, 255, 0.40)",
    "glow_purple": "rgba(124, 58, 237, 0.35)",

    # Floating Trigger Glass Bubble
    "bubble_bg": "rgba(22, 25, 38, 0.78)",
    "bubble_border": "rgba(255, 255, 255, 0.22)",
    "bubble_hover_bg": "rgba(30, 36, 56, 0.90)",
    "bubble_hover_border": "rgba(0, 132, 255, 0.65)",

    # Mini Player Capsule (Dark Frosted Glass)
    "player_capsule_bg": "rgba(18, 21, 33, 0.88)",
    "player_capsule_border": "rgba(255, 255, 255, 0.14)",
    "player_capsule_glow": "rgba(0, 0, 0, 0.35)",

    # Mini Player Capsule (Light Frosted Glass)
    "player_capsule_light_bg": "rgba(255, 255, 255, 0.65)",
    "player_capsule_light_border": "rgba(255, 255, 255, 0.50)",

    # Segmented Inner Buttons & Pills
    "pill_bg": "rgba(255, 255, 255, 0.08)",
    "pill_border": "rgba(255, 255, 255, 0.12)",
    "pill_hover_bg": "rgba(255, 255, 255, 0.16)",
    "pill_hover_border": "rgba(255, 255, 255, 0.25)",
    "pill_pressed_bg": "rgba(255, 255, 255, 0.22)",

    # Typography
    "text_primary": "#FFFFFF",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    
    # Dialogs & Backgrounds
    "bg_window": "#131625",
    "border_window": "#252B44",
    "accent": "#0084FF",
    "accent_hover": "#38BDF8",

    # Stop button
    "stop_icon": "#94A3B8",
    "stop_bg": "rgba(255, 255, 255, 0.08)",
    "stop_border": "rgba(255, 255, 255, 0.12)",
    "stop_hover_bg": "rgba(248, 113, 113, 0.20)",
    "stop_hover_border": "rgba(248, 113, 113, 0.50)",
    "stop_hover_icon": "#F87171"
}
