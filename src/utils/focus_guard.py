"""
Detects when the user is editing a single-line text box (search box, URL bar, form field),
so Voxel can stay out of the way instead of popping up while they edit.

- macOS: reads the focused element's role through the Accessibility API (the permission Voxel
  already needs). AXTextField / AXSearchField / AXComboBox / secure fields count as "typing boxes".
  Text areas and documents (AXTextArea, web content) are NOT skipped, so reading still works there.
- Windows: checks the focused native control (Edit / RichEdit / ComboBox without the multi-line
  style). Browser page fields are not visible to this check; the other safeguards still apply there.

Every call is defensive: any error means "not a text box" so Voxel keeps working.
"""
import sys

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

MAC_INPUT_ROLES = {"AXTextField", "AXSearchField", "AXComboBox"}
MAC_INPUT_SUBROLES = {"AXSearchField", "AXSecureTextField"}
WIN_EDIT_CLASSES = ("edit", "richedit", "combobox", "tedit", "thunderrt6textbox", "windowsforms10.edit")
ES_MULTILINE = 0x0004
GWL_STYLE = -16


def is_typing_in_text_box() -> bool:
    try:
        if IS_MAC:
            return _mac_focused_is_input()
        if IS_WIN:
            return _win_focused_is_input()
    except Exception:
        return False
    return False


# ── macOS ────────────────────────────────────────────────────────────────────
def _mac_focused_is_input() -> bool:
    from ApplicationServices import (  # provided by pyobjc (a pynput dependency on macOS)
        AXUIElementCreateSystemWide, AXUIElementCopyAttributeValue, AXUIElementSetMessagingTimeout,
    )
    system = AXUIElementCreateSystemWide()
    try:
        AXUIElementSetMessagingTimeout(system, 0.15)  # never hang on a busy app
    except Exception:
        pass
    err, focused = AXUIElementCopyAttributeValue(system, "AXFocusedUIElement", None)
    if err or focused is None:
        return False
    _, role = AXUIElementCopyAttributeValue(focused, "AXRole", None)
    _, subrole = AXUIElementCopyAttributeValue(focused, "AXSubrole", None)
    return str(role or "") in MAC_INPUT_ROLES or str(subrole or "") in MAC_INPUT_SUBROLES


# ── Windows ──────────────────────────────────────────────────────────────────
def _win_focused_hwnd():
    import ctypes
    import ctypes.wintypes as w

    class GUITHREADINFO(ctypes.Structure):
        _fields_ = [("cbSize", w.DWORD), ("flags", w.DWORD), ("hwndActive", w.HWND), ("hwndFocus", w.HWND),
                    ("hwndCapture", w.HWND), ("hwndMenuOwner", w.HWND), ("hwndMoveSize", w.HWND),
                    ("hwndCaret", w.HWND), ("rcCaret", w.RECT)]

    info = GUITHREADINFO()
    info.cbSize = ctypes.sizeof(info)
    if not ctypes.windll.user32.GetGUIThreadInfo(0, ctypes.byref(info)):  # 0 = foreground thread
        return None
    return info.hwndFocus


def win_hwnd_is_input(hwnd) -> bool:
    """True if hwnd is a single-line native text box."""
    if not hwnd:
        return False
    import ctypes
    user32 = ctypes.windll.user32
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    cls = buf.value.lower()
    if not any(cls.startswith(c) for c in WIN_EDIT_CLASSES):
        return False
    style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    return not (style & ES_MULTILINE)


def _win_focused_is_input() -> bool:
    return win_hwnd_is_input(_win_focused_hwnd())
