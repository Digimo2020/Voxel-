"""
Global Mouse and Keyboard Selection Listener for Voxel.
Detects text selection across any macOS or Windows application (browsers, editors, documents)
and notifies the UI on the main thread via Qt signals.
"""
import sys
import time
import math
import threading
from typing import Callable, Optional
from pynput import mouse, keyboard
from PyQt6.QtCore import QObject, pyqtSignal

from src.config import DRAG_THRESHOLD_PIXELS, MIN_SELECTED_LENGTH, HOTKEY_WINDOWS, HOTKEY_MAC, HOTKEY_DOC_WINDOWS, HOTKEY_DOC_MAC, IS_MAC
from src.utils.clipboard import grab_selected_text
from src.utils.mac_permissions import is_accessibility_trusted
from src.utils.focus_guard import is_typing_in_text_box
from src.utils.settings import settings_db

# Known screenshot apps, drawing overlays, and full-screen capture tools to never intercept
BLOCKED_OVERLAY_PROCESSES = {
    "flameshot", "lightshot", "snippingtool", "screensketch", "snipaste",
    "sharex", "greenshot", "screenpresso", "picpick"
}

if sys.platform == "win32":
    import ctypes
    _user32 = ctypes.windll.user32
    _kernel32 = ctypes.windll.kernel32
    _PROCESS_QUERY_LIMITED = 0x1000

    def _is_screenshot_app_active() -> bool:
        """Returns True if the active foreground window belongs to a screenshot tool."""
        try:
            hwnd = _user32.GetForegroundWindow()
            if not hwnd:
                return False
            pid = ctypes.c_ulong()
            _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if not pid.value:
                return False
            hproc = _kernel32.OpenProcess(_PROCESS_QUERY_LIMITED, False, pid.value)
            if not hproc:
                return False
            buf = ctypes.create_unicode_buffer(1024)
            size = ctypes.c_ulong(1024)
            _kernel32.QueryFullProcessImageNameW(hproc, 0, buf, ctypes.byref(size))
            _kernel32.CloseHandle(hproc)
            proc_path = buf.value.lower()
            return any(tool in proc_path for tool in BLOCKED_OVERLAY_PROCESSES)
        except Exception:
            return False
else:
    def _is_screenshot_app_active() -> bool:
        return False


class SelectionListener(QObject):
    """
    Background listener that triggers when user selects text or presses the global hotkey.
    """
    text_selected = pyqtSignal(str, int, int, int, int)  # (text, cursor_x, cursor_y, start_x, start_y)
    clicked_outside = pyqtSignal()
    permission_needed = pyqtSignal()
    document_hotkey_triggered = pyqtSignal()

    def __init__(self, is_inside_widget_fn: Optional[Callable[[int, int], bool]] = None, parent=None):
        super().__init__(parent)
        self.is_inside_widget_fn = is_inside_widget_fn
        self.is_enabled: bool = True

        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.GlobalHotKeys] = None

        # Tracking mouse states
        self._press_pos = (0, 0)
        self._press_time = 0.0
        self._last_click_time = 0.0
        self._last_click_pos = (0, 0)
        self._last_key_time = 0.0          # any key press, used to back off while the user types
        self._activity_listener: Optional[keyboard.Listener] = None
        self._ignore_keys_until = 0.0     # Voxel's own copy keystrokes are not user typing

    def start(self):
        """Starts mouse and hotkey listeners."""
        # On macOS, check if accessibility permission is granted
        if IS_MAC and not is_accessibility_trusted(prompt=False):
            print("[SelectionListener] Notice: macOS Accessibility permission not yet granted.")
            self.permission_needed.emit()

        # 1. Mouse listener
        try:
            self._mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click
            )
            self._mouse_listener.daemon = True
            self._mouse_listener.start()
        except Exception as e:
            print(f"[SelectionListener] Mouse listener start error: {e}")

        # 1b. Key activity (no key data is kept; only the time of the last press)
        try:
            self._activity_listener = keyboard.Listener(on_press=self._on_any_key)
            self._activity_listener.daemon = True
            self._activity_listener.start()
        except Exception as e:
            print(f"[SelectionListener] Key activity listener error: {e}")

        # 2. Global Hotkey listeners: Selection (Ctrl+Alt+S) & Document (Ctrl+Alt+D)
        hotkey_str = HOTKEY_MAC if IS_MAC else HOTKEY_WINDOWS
        hotkey_doc_str = HOTKEY_DOC_MAC if IS_MAC else HOTKEY_DOC_WINDOWS
        try:
            self._keyboard_listener = keyboard.GlobalHotKeys({
                hotkey_str: self._on_hotkey_triggered,
                hotkey_doc_str: self._on_doc_hotkey_triggered
            })
            self._keyboard_listener.daemon = True
            self._keyboard_listener.start()
        except Exception as e:
            print(f"[SelectionListener] Hotkey registration error: {e}")

    def stop(self):
        """Stops listeners cleanly."""
        if self._mouse_listener:
            try:
                self._mouse_listener.stop()
            except Exception:
                pass
            self._mouse_listener = None

        for attr in ("_keyboard_listener", "_activity_listener"):
            lst = getattr(self, attr, None)
            if lst:
                try:
                    lst.stop()
                except Exception:
                    pass
                setattr(self, attr, None)

    def _on_any_key(self, key, injected=False):
        # pynput 1.8+ passes injected=True for synthetic keys (our own Ctrl/Cmd+C).
        # The time window covers platforms/versions that don't report it.
        now = time.time()
        if injected or now < self._ignore_keys_until:
            return
        self._last_key_time = now

    def _copy_selection(self, **kwargs) -> str:
        """Runs the copy while ignoring the key events it generates."""
        self._ignore_keys_until = time.time() + 5.0
        try:
            return grab_selected_text(**kwargs)
        finally:
            self._ignore_keys_until = time.time() + 0.15  # late-delivered key-up events

    def set_enabled(self, enabled: bool):
        """Toggle whether selection detection is active."""
        self.is_enabled = enabled

    def _on_mouse_click(self, x, y, button, pressed):
        if not self.is_enabled:
            return

        # Only track left mouse button
        if button != mouse.Button.left:
            return

        # Ignore clicks that landed inside our own widgets
        if self.is_inside_widget_fn and self.is_inside_widget_fn(int(x), int(y)):
            return

        now = time.time()

        if pressed:
            self._press_pos = (x, y)
            self._press_time = now
        else:
            # Mouse released
            drag_dist = math.hypot(x - self._press_pos[0], y - self._press_pos[1])
            is_drag = drag_dist >= DRAG_THRESHOLD_PIXELS

            # Double-click check (within 450ms and small displacement)
            double_click_dist = math.hypot(x - self._last_click_pos[0], y - self._last_click_pos[1])
            is_double_click = (now - self._last_click_time < 0.45) and (double_click_dist < 15)

            self._last_click_time = now
            self._last_click_pos = (x, y)

            if is_drag or is_double_click:
                start_x = int(self._press_pos[0])
                start_y = int(self._press_pos[1])
                # Dispatch immediately to background worker thread so Quartz event tap never times out
                threading.Thread(
                    target=self._handle_possible_selection,
                    args=(int(x), int(y), start_x, start_y, now),
                    daemon=True
                ).start()
            else:
                # User clicked empty space or single-clicked without dragging
                self.clicked_outside.emit()

    def _user_moved_on(self, since: float) -> bool:
        """True if the user typed or clicked again after the selection ended."""
        return self._last_key_time > since or self._press_time > since

    def _handle_possible_selection(self, cursor_x: int, cursor_y: int, start_x: int = 0, start_y: int = 0,
                                   released_at: float = 0.0):
        """Waits briefly for selection to settle in target app, then grabs text.

        Stays out of the way: never runs in screenshot tools, in single-line text boxes
        (search / URL / form fields, unless the user turned that off), or once the user
        starts typing or clicks again.
        """
        released_at = released_at or time.time()
        # Never inject copy keystrokes into screenshot overlay apps (Flameshot, Lightshot, Snipping Tool)
        if _is_screenshot_app_active():
            return

        if settings_db.get("skip_text_fields", True) and is_typing_in_text_box():
            return

        time.sleep(0.12)
        if self._user_moved_on(released_at):
            return

        text = self._copy_selection(timeout_ms=320, persistent=False)
        if self._user_moved_on(released_at):
            return  # user is busy again: don't pop up over their work
        if text and len(text) >= MIN_SELECTED_LENGTH:
            if any(c.isalnum() for c in text):
                self.text_selected.emit(text, cursor_x, cursor_y, start_x, start_y)

    def _on_hotkey_triggered(self):
        """Triggered when pressing Cmd+Alt+S (or Ctrl+Alt+S)."""
        if not self.is_enabled:
            return

        def _worker():
            text = self._copy_selection(timeout_ms=250)
            if text and len(text) >= MIN_SELECTED_LENGTH:
                ctrl = mouse.Controller()
                cx, cy = ctrl.position
                self.text_selected.emit(text, int(cx), int(cy), int(cx), int(cy))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_doc_hotkey_triggered(self):
        """Triggered when pressing Cmd+Alt+D (or Ctrl+Alt+D) to read entire document."""
        if not self.is_enabled:
            return
        self.document_hotkey_triggered.emit()
