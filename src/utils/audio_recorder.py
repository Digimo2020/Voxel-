"""
Voxel Audio Recording Utility.
Manages automatic recording of text-to-speech audio streams into the
user's Documents/Voxel Recordings folder.
"""
import os
import sys
import time
import re
from pathlib import Path
from typing import List, Optional
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from src.utils.settings import settings_db


def get_recordings_dir() -> str:
    """Returns the absolute path to the Voxel Recordings folder in Documents."""
    custom_dir = settings_db.get("recordings_folder", "")
    if custom_dir and os.path.isdir(custom_dir):
        return custom_dir

    # Standard user Documents folder
    docs = os.path.join(os.path.expanduser("~"), "Documents")
    if not os.path.exists(docs):
        # Fallback to home if Documents doesn't exist
        docs = os.path.expanduser("~")

    target_dir = os.path.join(docs, "Voxel Recordings")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def open_recordings_folder():
    """Opens the Voxel Recordings folder in Windows Explorer / macOS Finder."""
    folder = get_recordings_dir()
    if sys.platform == "win32":
        try:
            os.startfile(folder)
            return
        except Exception:
            pass
    QDesktopServices.openUrl(QUrl.fromLocalFile(folder))


def open_recording_file(file_path: str):
    """Opens the recorded audio file with the system default media player."""
    if os.path.exists(file_path):
        if sys.platform == "win32":
            try:
                os.startfile(file_path)
                return
            except Exception:
                pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))


def generate_recording_filename(text_hint: str = "") -> str:
    """Generates a clean timestamped filename for a recording."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    clean_hint = ""
    if text_hint:
        words = re.sub(r"[^\w\s-]", "", text_hint).strip().split()
        if words:
            clean_hint = "_".join(words[:4])
            if len(clean_hint) > 30:
                clean_hint = clean_hint[:30]

    if clean_hint:
        return f"Voxel_{clean_hint}_{timestamp}.mp3"
    return f"Voxel_Recording_{timestamp}.mp3"


def save_recording_from_chunks(chunk_paths: List[str], text_hint: str = "") -> Optional[str]:
    """
    Concatenates synthesized MP3 chunks and saves the final file to the
    Documents/Voxel Recordings folder.
    Returns the absolute path to the saved file or None if failed.
    """
    valid_chunks = [p for p in chunk_paths if p and os.path.exists(p) and os.path.getsize(p) > 0]
    if not valid_chunks:
        return None

    out_dir = get_recordings_dir()
    filename = generate_recording_filename(text_hint)
    dest_path = os.path.join(out_dir, filename)

    try:
        with open(dest_path, "wb") as out_f:
            for c_path in valid_chunks:
                with open(c_path, "rb") as in_f:
                    out_f.write(in_f.read())

        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            return dest_path
    except Exception as e:
        print(f"[Audio Recorder] Failed to save recording: {e}", file=sys.stderr)

    return None
