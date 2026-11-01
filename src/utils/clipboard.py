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
IS_WIN = sys.platform == "win32"
MODIFIER_KEY = keyboard.Key.cmd if IS_MAC else keyboard.Key.ctrl

_kb_controller = keyboard.Controller()

if IS_MAC:
    try:
        from AppKit import NSPasteboard, NSPasteboardTypeString
        _MAC_PB = NSPasteboard.generalPasteboard()
    except Exception:
        _MAC_PB = None
else:
    _MAC_PB = None


def _simulate_copy_mac() -> bool:
    """Hardware-level Cmd+C via macOS Quartz CoreGraphics Event Tap."""
    try:
        from Quartz.CoreGraphics import (
            CGEventSourceCreate, kCGEventSourceStateCombinedSessionState,
            CGEventCreateKeyboardEvent, CGEventSetFlags, CGEventPost,
            kCGSessionEventTap, kCGHIDEventTap, kCGEventFlagMaskCommand
        )
        src = CGEventSourceCreate(kCGEventSourceStateCombinedSessionState)
        down = CGEventCreateKeyboardEvent(src, 8, True)   # Keycode 8 = 'c'
        up = CGEventCreateKeyboardEvent(src, 8, False)
        CGEventSetFlags(down, kCGEventFlagMaskCommand)
        CGEventSetFlags(up, kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, down)
        time.sleep(0.015)
        CGEventPost(kCGHIDEventTap, up)
        try:
            CGEventPost(kCGSessionEventTap, down)
            time.sleep(0.015)
            CGEventPost(kCGSessionEventTap, up)
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"[Clipboard] Mac Quartz copy error: {e}")
        return False


def _simulate_copy_applescript() -> bool:
    """Native macOS System Events AppleScript copy fallback."""
    try:
        script = 'tell application "System Events" to keystroke "c" using command down'
        subprocess.run(["osascript", "-e", script], timeout=0.25, capture_output=True)
        return True
    except Exception:
        return False


def _simulate_copy_win() -> bool:
    """Native Windows keybd_event for Ctrl+C."""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        VK_CONTROL = 0x11
        VK_C = 0x43
        KEYEVENTF_KEYUP = 0x0002
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_C, 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        return True
    except Exception as e:
        print(f"[Clipboard] Win32 copy error: {e}")
        return False


def _simulate_copy_pynput():
    """Fallback cross-platform copy using pynput Controller."""
    try:
        with _kb_controller.pressed(MODIFIER_KEY):
            time.sleep(0.02)
            _kb_controller.press("c")
            time.sleep(0.03)
            _kb_controller.release("c")
            time.sleep(0.02)
        return True
    except Exception as e:
        print(f"[Clipboard] pynput copy error: {e}")
        return False


def grab_selected_text(timeout_ms: int = 480) -> str:
    """
    Simulates a copy event to capture highlighted text from the active window,
    then restores the user's previous clipboard contents.
    
    Returns the selected string, or empty string if nothing selected.
    """
    # High-speed native NSPasteboard path on macOS (no subprocess overhead, no clipboard clobbering)
    if IS_MAC and _MAC_PB is not None:
        try:
            initial_count = _MAC_PB.changeCount()
            _simulate_copy_mac()

            start_time = time.time()
            max_wait = timeout_ms / 1000.0
            new_text = ""
            tried_fallback = False

            while time.time() - start_time < max_wait:
                time.sleep(0.015)
                if _MAC_PB.changeCount() != initial_count:
                    new_text = _MAC_PB.stringForType_(NSPasteboardTypeString) or ""
                    break
                if not tried_fallback and (time.time() - start_time) > 0.15:
                    tried_fallback = True
                    _simulate_copy_applescript()
                    _simulate_copy_pynput()

            if new_text:
                cleaned = new_text.strip()
                if len(cleaned) >= 1:
                    return cleaned
            return ""
        except Exception as e:
            print(f"[Clipboard] Mac native capture error: {e}")

    # Fallback path for Windows / non-AppKit
    old_clip = ""
    try:
        old_clip = pyperclip.paste()
    except Exception:
        old_clip = ""

    sentinel = f"__VOX_SENTINEL_{time.time_ns()}__"
    try:
        pyperclip.copy(sentinel)
    except Exception:
        pass

    copied = False
    if IS_MAC:
        copied = _simulate_copy_mac()
    elif IS_WIN:
        copied = _simulate_copy_win()

    if not copied:
        _simulate_copy_pynput()

    start_time = time.time()
    new_text = ""
    max_wait = timeout_ms / 1000.0
    retried_fallback = False

    while time.time() - start_time < max_wait:
        time.sleep(0.02)
        try:
            curr = pyperclip.paste()
            if curr and curr != sentinel:
                new_text = curr
                break
        except Exception:
            pass

        if not retried_fallback and (time.time() - start_time) > (max_wait * 0.45):
            retried_fallback = True
            _simulate_copy_pynput()

    _safe_restore_clipboard(old_clip)

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
