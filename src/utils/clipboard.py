"""
Universal clipboard capture and restore utility.
Safely extracts selected text across all applications (Browser, Word, Google Docs, etc.)
and restores previous clipboard content so the user clipboard isn't lost.
"""
import sys
import time
import pyperclip
from pynput import keyboard

# Determine OS modifier key (Cmd on macOS, Ctrl on Windows/Linux)
IS_MAC = sys.platform == "darwin"
MODIFIER_KEY = keyboard.Key.cmd if IS_MAC else keyboard.Key.ctrl

_kb_controller = keyboard.Controller()


def grab_selected_text(timeout_ms: int = 150) -> str:
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

    # Unique sentinel to know if new text was copied
    sentinel = f"__T2V_SENTINEL_{time.time_ns()}__"
    try:
        pyperclip.copy(sentinel)
    except Exception:
        pass

    # 2. Simulate Ctrl+C (or Cmd+C on Mac)
    try:
        with _kb_controller.pressed(MODIFIER_KEY):
            _kb_controller.tap("c")
    except Exception as e:
        print(f"[Clipboard] Key simulation error: {e}")
        # Restore clipboard
        _safe_restore_clipboard(old_clip)
        return ""

    # 3. Poll clipboard for new text
    start_time = time.time()
    new_text = ""
    max_wait = timeout_ms / 1000.0

    while time.time() - start_time < max_wait:
        time.sleep(0.025)
        try:
            curr = pyperclip.paste()
            if curr != sentinel:
                new_text = curr
                break
        except Exception:
            continue

    # 4. Restore original clipboard text so user's clipboard history remains intact
    _safe_restore_clipboard(old_clip)

    # 5. Clean up and validate
    if new_text and new_text != sentinel:
        cleaned = new_text.strip()
        # Ensure it has some text
        if len(cleaned) >= 1:
            return cleaned

    return ""


def _safe_restore_clipboard(text: str):
    """Restores clipboard safely without throwing exceptions."""
    try:
        pyperclip.copy(text)
    except Exception:
        pass
