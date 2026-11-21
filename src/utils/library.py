"""
Voxel library: things the user chooses to keep.

- saved_texts : text saved from Read Text (title, text, created, updated)
- bookmarks   : items starred from History, so they survive the 50-item history limit

History (history.json) stays the automatic log and is not changed. Recordings stay MP3 files in
the recordings folder. This file only holds what the user deliberately keeps:

    <app storage>/library.json
    {"schema": 1, "saved_texts": [...], "bookmarks": [...]}

Safe by design: atomic writes (temp file + replace), duplicate protection (same text is updated,
not added twice), and a corrupt file is moved aside to library.json.bak instead of being lost.
"""
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional

from src.utils.settings import get_app_storage_dir

SCHEMA = 1
LIBRARY_FILE = os.path.join(get_app_storage_dir(), "library.json")
MAX_ITEMS = 500


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _norm(text: str) -> str:
    return " ".join((text or "").split())


def _title_from(text: str) -> str:
    first = next((ln.strip() for ln in (text or "").splitlines() if ln.strip()), "Untitled")
    return first[:60] + ("…" if len(first) > 60 else "")


class LibraryManager:
    def __init__(self, filepath: str = LIBRARY_FILE):
        self.filepath = filepath
        self.data: Dict[str, Any] = {"schema": SCHEMA, "saved_texts": [], "bookmarks": []}
        self.load()

    # ── storage ─────────────────────────────────────────────────────────────
    def load(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.data = self._migrate(raw)
        except Exception as e:
            # keep the broken file for recovery instead of overwriting it
            try:
                os.replace(self.filepath, self.filepath + ".bak")
            except Exception:
                pass
            print(f"[Library] Could not read library, moved to .bak: {e}")

    @staticmethod
    def _migrate(raw: Any) -> Dict[str, Any]:
        """Accepts older/partial shapes and returns the current schema."""
        out = {"schema": SCHEMA, "saved_texts": [], "bookmarks": []}
        if isinstance(raw, dict):
            for key in ("saved_texts", "bookmarks"):
                items = raw.get(key, [])
                if isinstance(items, list):
                    out[key] = [i for i in items if isinstance(i, dict) and i.get("text")]
        return out

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            tmp = self.filepath + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.filepath)
        except Exception as e:
            print(f"[Library] Save error: {e}")

    # ── saved text ──────────────────────────────────────────────────────────
    def saved_texts(self) -> List[Dict[str, Any]]:
        items = self.data["saved_texts"]  # newest first; ties (same second) by most recently added
        return [i for _, i in sorted(enumerate(items), key=lambda p: (p[1].get("updated", ""), p[0]), reverse=True)]

    def save_text(self, text: str, item_id: Optional[str] = None, title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        text = (text or "").strip()
        if not text:
            return None
        items = self.data["saved_texts"]
        existing = next((i for i in items if i.get("id") == item_id), None) if item_id else None
        if existing is None:  # same text already saved -> update it instead of adding a duplicate
            existing = next((i for i in items if _norm(i.get("text")) == _norm(text)), None)
        if existing is not None:
            existing.update(text=text, title=title or _title_from(text), updated=_now())
            item = existing
        else:
            item = {"id": uuid.uuid4().hex[:12], "title": title or _title_from(text), "text": text,
                    "created": _now(), "updated": _now()}
            items.append(item)
            del items[:-MAX_ITEMS]
        self.save()
        return item

    def delete_text(self, item_id: str):
        self.data["saved_texts"] = [i for i in self.data["saved_texts"] if i.get("id") != item_id]
        self.save()

    # ── bookmarks ───────────────────────────────────────────────────────────
    def bookmarks(self) -> List[Dict[str, Any]]:
        items = self.data["bookmarks"]
        return [i for _, i in sorted(enumerate(items), key=lambda p: (p[1].get("created", ""), p[0]), reverse=True)]

    def is_bookmarked(self, text: str) -> bool:
        n = _norm(text)
        return any(_norm(b.get("text")) == n for b in self.data["bookmarks"])

    def add_bookmark(self, text: str, voice: str = "", speed: float = 1.0, read_at: str = "") -> Optional[Dict[str, Any]]:
        text = (text or "").strip()
        if not text:
            return None
        n = _norm(text)
        for b in self.data["bookmarks"]:
            if _norm(b.get("text")) == n:
                return b
        b = {"id": uuid.uuid4().hex[:12], "title": _title_from(text), "text": text, "voice": voice,
             "speed": speed, "read_at": read_at, "created": _now()}
        self.data["bookmarks"].append(b)
        del self.data["bookmarks"][:-MAX_ITEMS]
        self.save()
        return b

    def remove_bookmark(self, item_id: str = "", text: str = ""):
        n = _norm(text)
        self.data["bookmarks"] = [b for b in self.data["bookmarks"]
                                  if not ((item_id and b.get("id") == item_id) or (text and _norm(b.get("text")) == n))]
        self.save()


library_db = LibraryManager()
