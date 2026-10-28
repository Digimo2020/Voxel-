"""
Global Mouse and Keyboard Selection Listener.
Detects text selection across any application (browsers, editors, Google Docs, etc.)
and notifies the UI on the main thread via Qt signals.
"""
import time
import math
from typing import Callable, Optional
from pynput import mouse, keyboard
from PyQt6.QtCore import QObject, pyqtSignal

from src.config import DRAG_THRESHOLD_PIXELS, MIN_SELECTED_LENGTH, HOTKEY_WINDOWS, HOTKEY_MAC, IS_MAC
from src.utils.clipboard import grab_selected_text


class SelectionListener(QObject):
    """
    Background listener that triggers when the user selects text in any app.
    """
    text_selected = pyqtSignal(str, int, int)  # (text, cursor_x, cursor_y)
    clicked_outside = pyqtSignal()

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

    def start(self):
        """Starts mouse and hotkey listeners."""
        # 1. Mouse listener
        self._mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click
        )
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

        # 2. Global Hotkey listener (Ctrl+Alt+S or Cmd+Alt+S)
        hotkey_str = HOTKEY_MAC if IS_MAC else HOTKEY_WINDOWS
        try:
            self._keyboard_listener = keyboard.GlobalHotKeys({
                hotkey_str: self._on_hotkey_triggered
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

        if self._keyboard_listener:
            try:
                self._keyboard_listener.stop()
            except Exception:
                pass
            self._keyboard_listener = None

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

            # Double-click check (within 350ms and small displacement)
            double_click_dist = math.hypot(x - self._last_click_pos[0], y - self._last_click_pos[1])
            is_double_click = (now - self._last_click_time < 0.38) and (double_click_dist < 10)

            self._last_click_time = now
            self._last_click_pos = (x, y)

            if is_drag or is_double_click:
                self._handle_possible_selection(int(x), int(y))
            else:
                # User clicked empty space or single-clicked without dragging
                self.clicked_outside.emit()

    def _handle_possible_selection(self, cursor_x: int, cursor_y: int):
        """Waits briefly for selection to settle, then grabs text."""
        # Brief pause to let active application register selection highlight
        time.sleep(0.08)

        text = grab_selected_text(timeout_ms=160)
        if text and len(text) >= MIN_SELECTED_LENGTH:
            # Check that it contains at least one alphanumeric character
            if any(c.isalnum() for c in text):
                self.text_selected.emit(text, cursor_x, cursor_y)

    def _on_hotkey_triggered(self):
        """Triggered when pressing Ctrl+Alt+S (or Cmd+Alt+S)."""
        if not self.is_enabled:
            return

        text = grab_selected_text(timeout_ms=160)
        if text and len(text) >= MIN_SELECTED_LENGTH:
            # Get current mouse position
            ctrl = mouse.Controller()
            cx, cy = ctrl.position
            self.text_selected.emit(text, int(cx), int(cy))
