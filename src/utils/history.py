"""
JSON-based History and Storage Manager for Voxel.
Persists recent spoken text clips, timestamps, voice, and speed to:
- macOS: ~/Library/Application Support/Voxel/history.json
- Windows: %LOCALAPPDATA%/Voxel/history.json
"""
import sys
import os
import json
import time
from typing import List, Dict, Any

IS_MAC = sys.platform == "darwin"

from src.utils.settings import get_app_storage_dir

HISTORY_DIR = get_app_storage_dir()
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")
MAX_HISTORY_ENTRIES = 50


class HistoryManager:
    def __init__(self, filepath: str = HISTORY_FILE):
        self.filepath = filepath
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensures the directory and history file exist."""
        try:
            folder = os.path.dirname(self.filepath)
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            if not os.path.exists(self.filepath):
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
        except Exception as e:
            print(f"[HistoryManager] Error initializing storage: {e}")

    def add_entry(self, text: str, voice_name: str, speed: float) -> Dict[str, Any]:
        """Adds a new spoken text record to history."""
        cleaned = text.strip()
        if not cleaned:
            return {}

        entry = {
            "id": f"vox_{int(time.time() * 1000)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "text": cleaned,
            "preview": cleaned[:55] + ("..." if len(cleaned) > 55 else ""),
            "voice": voice_name,
            "speed": round(speed, 2),
            "char_count": len(cleaned)
        }

        history = self.get_all()
        # Avoid duplicate consecutive entries
        if history and history[0].get("text") == cleaned:
            return history[0]

        history.insert(0, entry)
        if len(history) > MAX_HISTORY_ENTRIES:
            history = history[:MAX_HISTORY_ENTRIES]

        self._save(history)
        return entry

    def get_all(self) -> List[Dict[str, Any]]:
        """Reads all history records."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"[HistoryManager] Read error: {e}")
            return []

    def clear(self):
        """Empties history storage."""
        self._save([])

    def _save(self, items: List[Dict[str, Any]]):
        try:
            tmp = self.filepath + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)
            if os.path.exists(self.filepath):
                os.replace(tmp, self.filepath)
            else:
                os.rename(tmp, self.filepath)
        except Exception as e:
            print(f"[HistoryManager] Write error: {e}")


# Global Singleton Instance
history_db = HistoryManager()
