"""
Persistent Settings Manager.
Saves user preferences (default voice, speed, bubble timeout, hotkey, dock mode)
to %LOCALAPPDATA%/Text2Voice/settings.json.
"""
import os
import json
from typing import Any, Dict

SETTINGS_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Text2Voice")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "default_voice": "en-US-JennyNeural",
    "default_speed": 1.0,
    "selection_popup_enabled": True,
    "bubble_timeout": 4.0,
    "dock_position": "bottom_right",   # "bottom_right" or "near_cursor"
    "hotkey": "<ctrl>+<alt>+s",
    "version": "v1.0.01"
}


class SettingsManager:
    def __init__(self, filepath: str = SETTINGS_FILE):
        self.filepath = filepath
        self.settings: Dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        """Loads settings from JSON file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        self.settings.update(saved)
            except Exception as e:
                print(f"[SettingsManager] Load error: {e}")
        else:
            self.save()

    def save(self):
        """Saves current settings to JSON file safely."""
        try:
            folder = os.path.dirname(self.filepath)
            os.makedirs(folder, exist_ok=True)
            tmp = self.filepath + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
            if os.path.exists(self.filepath):
                os.replace(tmp, self.filepath)
            else:
                os.rename(tmp, self.filepath)
        except Exception as e:
            print(f"[SettingsManager] Save error: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()


# Global singleton instance
settings_db = SettingsManager()
