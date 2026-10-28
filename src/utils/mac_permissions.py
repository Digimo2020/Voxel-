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
    If prompt=True, macOS will display the system prompt asking the user for permission.
    """
    if not IS_MAC:
        return True

    try:
        # Load HIServices from ApplicationServices framework
        hiservices = ctypes.cdll.LoadLibrary(
            "/System/Library/Frameworks/ApplicationServices.framework/Frameworks/HIServices.framework/HIServices"
        )
        if prompt:
            # AXIsProcessTrustedWithOptions with kAXTrustedCheckOptionPrompt = True
            kAXTrustedCheckOptionPrompt = ctypes.c_void_p.in_dll(
                hiservices, "kAXTrustedCheckOptionPrompt"
            )
            # Create CFDictionary with {kAXTrustedCheckOptionPrompt: kCFBooleanTrue}
            # Or simpler: invoke AXIsProcessTrustedWithOptions
            corefoundation = ctypes.cdll.LoadLibrary(
                "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
            )
            kCFBooleanTrue = ctypes.c_void_p.in_dll(corefoundation, "kCFBooleanTrue")

            cf_dict_create = corefoundation.CFDictionaryCreate
            cf_dict_create.restype = ctypes.c_void_p
            cf_dict_create.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_void_p),
                ctypes.POINTER(ctypes.c_void_p),
                ctypes.c_long,
                ctypes.c_void_p,
                ctypes.c_void_p,
            ]

            keys = (ctypes.c_void_p * 1)(kAXTrustedCheckOptionPrompt)
            values = (ctypes.c_void_p * 1)(kCFBooleanTrue)
            options = cf_dict_create(None, keys, values, 1, None, None)

            trusted = hiservices.AXIsProcessTrustedWithOptions(options)
            return bool(trusted)
        else:
            return bool(hiservices.AXIsProcessTrusted())
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
