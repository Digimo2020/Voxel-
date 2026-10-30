"""
Cross-Platform Startup Manager for Voxel.
Enables or disables launching Voxel automatically on Windows startup
(via HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run)
or macOS login (via ~/Library/LaunchAgents).
"""
import os
import sys

IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
APP_NAME = "Voxel"


def _get_target_launch_command() -> str:
    """Returns the executable command line for startup launch."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    else:
        # Running from source
        main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "main.py"))
        return f'"{sys.executable}" "{main_py}"'


def is_startup_enabled() -> bool:
    """Checks whether Voxel is registered to run on user startup."""
    if IS_WIN:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, APP_NAME)
                return bool(val)
        except Exception:
            return False
    elif IS_MAC:
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.digimo.voxel.plist")
        return os.path.exists(plist_path)
    return False


def set_startup_enabled(enabled: bool) -> bool:
    """Enables or disables Voxel startup on login."""
    if IS_WIN:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                if enabled:
                    cmd = _get_target_launch_command()
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, APP_NAME)
                    except FileNotFoundError:
                        pass
            return True
        except Exception as e:
            print(f"[Startup] Windows registry update error: {e}")
            return False
    elif IS_MAC:
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.digimo.voxel.plist")
        if enabled:
            try:
                cmd = _get_target_launch_command().replace('"', "")
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.digimo.voxel</string>
    <key>ProgramArguments</key>
    <array>
        <string>{cmd}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
                os.makedirs(os.path.dirname(plist_path), exist_ok=True)
                with open(plist_path, "w", encoding="utf-8") as f:
                    f.write(plist_content)
                return True
            except Exception as e:
                print(f"[Startup] macOS LaunchAgent write error: {e}")
                return False
        else:
            if os.path.exists(plist_path):
                try:
                    os.remove(plist_path)
                    return True
                except Exception as e:
                    print(f"[Startup] macOS LaunchAgent removal error: {e}")
                    return False
            return True
    return False
