"""
JSON-based History and Storage Manager.
Persists recent spoken text clips, timestamps, voice, and speed to a local JSON file.
"""
import os
import json
import time
from typing import List, Dict, Any

HISTORY_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Text2Voice")
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
            "id": f"t2v_{int(time.time() * 1000)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "text": cleaned,
            "preview": cleaned[:45] + ("..." if len(cleaned) > 45 else ""),
            "voice": voice_name,
            "speed": round(speed, 2),
            "char_count": len(cleaned)
        }

        history = self.get_all()
        # Avoid duplicate consecutive entries
        if history and history[0].get("text") == cleaned:
            return history[0]

        history.insert(0, entry)
        history = history[:MAX_HISTORY_ENTRIES]
        self._save(history)
        return entry

    def get_all(self) -> List[Dict[str, Any]]:
        """Retrieves all history entries."""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[HistoryManager] Read error: {e}")
        return []

    def clear(self):
        """Clears all history."""
        self._save([])

    def _save(self, data: List[Dict[str, Any]]):
        """Writes data back to the JSON file safely."""
        try:
            tmp = self.filepath + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if os.path.exists(self.filepath):
                os.replace(tmp, self.filepath)
            else:
                os.rename(tmp, self.filepath)
        except Exception as e:
            print(f"[HistoryManager] Save error: {e}")


# Global singleton instance
history_db = HistoryManager()
