"""
Universal clipboard capture and restore utility for Voxel.
Safely extracts selected text across all applications on macOS and Windows,
then restores previous clipboard contents so user clipboard history isn't overwritten.
"""
import sys
import os
import time
import subprocess
import pyperclip
from pynput import keyboard

IS_MAC = sys.platform == "darwin"
MODIFIER_KEY = keyboard.Key.cmd if IS_MAC else keyboard.Key.ctrl

_kb_controller = keyboard.Controller()


def grab_selected_text(timeout_ms: int = 180) -> str:
    """
    Simulates a copy event to capture highlighted text from the active window,
    then restores the user's previous clipboard contents.
    
    Returns the selected string, or empty string if nothing selected.
    """
    # 1. Backup old clipboard text
    old_clip = ""
    try:
        old_clip = pyperclip.paste()
    except Exception:
        old_clip = ""

    # Unique sentinel to verify if new text arrived
    sentinel = f"__VOX_SENTINEL_{time.time_ns()}__"
    try:
        pyperclip.copy(sentinel)
    except Exception:
        pass

    # 2. Simulate Copy (Cmd+C on macOS, Ctrl+C on Windows)
    copied = False
    try:
        with _kb_controller.pressed(MODIFIER_KEY):
            time.sleep(0.015)
            _kb_controller.press("c")
            time.sleep(0.015)
            _kb_controller.release("c")
            time.sleep(0.015)
        copied = True
    except Exception as e:
        print(f"[Clipboard] Key controller error: {e}")

    # Fallback to AppleScript keystroke on macOS if needed
    if not copied and IS_MAC:
        try:
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to keystroke "c" using {command down}'],
                timeout=0.3,
                capture_output=True
            )
        except Exception:
            pass

    # 3. Poll clipboard for new text
    start_time = time.time()
    new_text = ""
    max_wait = timeout_ms / 1000.0

    while time.time() - start_time < max_wait:
        time.sleep(0.02)
        try:
            curr = pyperclip.paste()
            if curr != sentinel:
                new_text = curr
                break
        except Exception:
            continue

    # 4. Restore original clipboard text
    _safe_restore_clipboard(old_clip)

    # 5. Clean up and validate
    if new_text and new_text != sentinel:
        cleaned = new_text.strip()
        if len(cleaned) >= 1:
            return cleaned

    return ""


def _safe_restore_clipboard(text: str):
    """Restores clipboard safely without throwing exceptions."""
    try:
        pyperclip.copy(text)
    except Exception:
        pass
