"""
Persistent Settings Manager for Voxel.
Saves user preferences (default voice, speed, bubble timeout, hotkey, dock mode, theme)
to standard application data locations:
- macOS: ~/Library/Application Support/Voxel/settings.json
- Windows: %LOCALAPPDATA%/Voxel/settings.json
- Linux: ~/.config/Voxel/settings.json
"""
import sys
import os
import json
from typing import Any, Dict

IS_MAC = sys.platform == "darwin"

def get_app_storage_dir() -> str:
    """Finds an accessible storage directory across platforms and sandboxes."""
    import tempfile
    candidates = []
    if IS_MAC:
        candidates.append(os.path.expanduser("~/Library/Application Support/Voxel"))
    elif os.name == "nt":
        candidates.append(os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Voxel"))
    else:
        candidates.append(os.path.expanduser("~/.config/Voxel"))

    candidates.append(os.path.expanduser("~/.voxel"))
    candidates.append(os.path.join(os.path.expanduser("~"), ".voxel_data"))
    candidates.append(os.path.join(tempfile.gettempdir(), ".voxel_data"))

    for c in candidates:
        try:
            os.makedirs(c, exist_ok=True)
            test_file = os.path.join(c, ".write_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return c
        except Exception:
            continue

    fallback = os.path.join(tempfile.gettempdir(), ".voxel_data")
    try:
        os.makedirs(fallback, exist_ok=True)
    except Exception:
        pass
    return fallback


SETTINGS_DIR = get_app_storage_dir()
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "default_voice": "en-US-JennyNeural",
    "default_speed": 1.0,
    "selection_popup_enabled": True,
    "bubble_timeout": 4.0,
    "dock_position": "bottom_right",   # "bottom_right" or "near_cursor"
    "hotkey": "<cmd>+<alt>+s" if IS_MAC else "<ctrl>+<alt>+s",
    "theme_mode": "dark_glass",       # "dark_glass" or "light_glass"
    "auto_close_finished": True,      # Auto-close player after speech completes
    "auto_close_delay": 1.0,          # Fade-out duration in seconds
    "version": "v1.0.02"
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


# Global Singleton Instance
settings_db = SettingsManager()
