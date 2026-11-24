"""
Remembers which app window the user was working in, so tray actions ("Read selected text",
"Read whole document") can send the copy shortcut to THAT window.

Why: on Windows, right-clicking the tray icon makes the taskbar the active window, so a copy
shortcut sent from the tray menu would go to the taskbar and copy nothing. Voxel samples the
foreground window a few times per second (ignoring the taskbar and its own windows) and puts
it back in front just before copying.

On macOS the menu bar does not take focus from the front app, so nothing is needed there.
"""
import os
import sys

IS_WIN = sys.platform == "win32"

_SHELL_CLASSES = {
    "shell_traywnd", "shell_secondarytraywnd", "notifyiconoverflowwindow",
    "toplevelwindowforoverflowxamlisland", "windows.ui.core.corewindow", "progman", "workerw",
    "xamlexplorerhostislandwindow", "#32768",  # popup menus
}

_last_hwnd = 0


def _class_name(hwnd) -> str:
    import ctypes
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.GetClassNameW(hwnd, buf, 256)
    return buf.value.lower()


def _is_own_process(hwnd) -> bool:
    import ctypes
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value == os.getpid()


def remember():
    """Call regularly: stores the current foreground window if it is a normal app window."""
    global _last_hwnd
    if not IS_WIN:
        return
    try:
        import ctypes
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd and not _is_own_process(hwnd) and _class_name(hwnd) not in _SHELL_CLASSES:
            _last_hwnd = hwnd
    except Exception:
        pass


def last_window() -> int:
    return _last_hwnd


def restore() -> bool:
    """Brings the remembered window back to the front. Returns True if it is in front now."""
    if not IS_WIN or not _last_hwnd:
        return not IS_WIN
    try:
        import ctypes
        user32 = ctypes.windll.user32
        if not user32.IsWindow(_last_hwnd):
            return False
        if user32.GetForegroundWindow() == _last_hwnd:
            return True
        if user32.IsIconic(_last_hwnd):
            user32.ShowWindow(_last_hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(_last_hwnd)
        return user32.GetForegroundWindow() == _last_hwnd
    except Exception:
        return False
