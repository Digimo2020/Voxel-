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
