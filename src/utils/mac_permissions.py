"""
macOS Accessibility Permissions Utility.
Checks if Voxel is trusted for Accessibility (required for global mouse & keyboard hooks)
and provides helpers to guide users to System Settings.
"""
import sys
import os
import subprocess
import ctypes
from typing import Tuple

IS_MAC = sys.platform == "darwin"


def is_accessibility_trusted(prompt: bool = False) -> bool:
    """
    Checks if the process has Accessibility permissions on macOS.
    If prompt=True and permissions are missing, automatically launches System Settings.
    """
    if not IS_MAC:
        return True

    try:
        hiservices = ctypes.cdll.LoadLibrary(
            "/System/Library/Frameworks/ApplicationServices.framework/Frameworks/HIServices.framework/HIServices"
        )
        hiservices.AXIsProcessTrusted.restype = ctypes.c_bool
        trusted = bool(hiservices.AXIsProcessTrusted())
        if not trusted:
            try:
                hiservices.AXIsProcessTrustedWithOptions.restype = ctypes.c_bool
                hiservices.AXIsProcessTrustedWithOptions.argtypes = [ctypes.c_void_p]
                trusted = bool(hiservices.AXIsProcessTrustedWithOptions(None))
            except Exception:
                pass

        if not trusted and prompt:
            open_accessibility_settings()
        return trusted
    except Exception as e:
        print(f"[MacPermissions] Check error: {e}")
        return False


def open_accessibility_settings():
    """Opens macOS System Settings directly to Privacy & Security -> Accessibility."""
    if not IS_MAC:
        return
    try:
        # Ventura / Sonoma / Sequoia URL scheme
        subprocess.run(
            ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"],
            check=False
        )
    except Exception as e:
        print(f"[MacPermissions] Failed to open settings: {e}")


def restart_voxel_app():
    """Restarts Voxel so new macOS system permissions take effect immediately."""
    if not IS_MAC:
        return
    try:
        import sys
        from PyQt6.QtWidgets import QApplication
        if "/Applications/Voxel.app" in sys.executable or hasattr(sys, "_MEIPASS"):
            subprocess.Popen(["open", "-n", "/Applications/Voxel.app"])
        else:
            subprocess.Popen([sys.executable, "main.py"])
        app = QApplication.instance()
        if app:
            app.quit()
        else:
            sys.exit(0)
    except Exception as e:
        print(f"[MacPermissions] Restart error: {e}")
