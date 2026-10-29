"""
Voxel - Text to Speech, Anywhere.
Main Application Entry Point.
Coordinates UI widgets, background selection listeners, settings, and TTS playback.
"""
import sys
import os
import traceback
import pyperclip
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QPoint

# Install top-level crash guard so unhandled slot exceptions never abort the process
def _global_exception_handler(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"[Voxel Uncaught Error] {err_msg}", file=sys.stderr)

sys.excepthook = _global_exception_handler

from src.config import VERSION, VOICES, APP_NAME, APP_TAGLINE, IS_MAC
from src.tts_engine import TTSEngine
from src.selection_listener import SelectionListener
from src.ui.floating_bubble import FloatingBubble
from src.ui.mini_player import MiniPlayer
from src.ui.tray_icon import AppTrayIcon
from src.ui.history_dialog import HistoryDialog
from src.ui.settings_dialog import SettingsDialog
from src.utils.settings import settings_db
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from assets.icons import create_app_icon


class VoxelApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationDisplayName(f"{APP_NAME} — {APP_TAGLINE}")
        self.app.setWindowIcon(create_app_icon(64))

        # Core Components
        self.tts = TTSEngine()
        self.bubble = FloatingBubble()
        self.player = MiniPlayer(self.tts)
        self.tray = AppTrayIcon(self.tts)
        self.history_dialog = HistoryDialog()
        self.settings_dialog = SettingsDialog()

        # Apply saved settings to TTS & Bubble
        self._apply_initial_settings()

        # Selection Listener with collision check function
        self.listener = SelectionListener(
            is_inside_widget_fn=self.is_inside_any_widget
        )

        self._connect_signals()

    def _apply_initial_settings(self):
        """Loads and applies saved user settings."""
        # 1. Voice
        saved_voice = settings_db.get("default_voice", "en-US-JennyNeural")
        for i, v in enumerate(VOICES):
            if v["id"] == saved_voice:
                self.tts.set_voice_index(i)
                break
        self.player.update_voice_label()

        # 2. Speed
        saved_speed = settings_db.get("default_speed", 1.0)
        self.tts.set_speed(saved_speed)
        self.player.lbl_speed.setText(f"{saved_speed}x")

        # 3. Bubble timeout
        saved_timeout = settings_db.get("bubble_timeout", 4.0)
        self.bubble.hide_timer.setInterval(int(saved_timeout * 1000))

        # 4. Player Theme
        saved_theme = settings_db.get("theme_mode", "dark_glass")
        self.player.apply_theme(saved_theme)

    def is_inside_any_widget(self, x: int, y: int) -> bool:
        """Returns True if point (x, y) is inside the Bubble, Player, or Settings window."""
        pt = QPoint(x, y)
        if self.bubble.isVisible() and self.bubble.geometry().contains(pt):
            return True
        if self.player.isVisible() and self.player.geometry().contains(pt):
            return True
        if self.settings_dialog.isVisible() and self.settings_dialog.geometry().contains(pt):
            return True
        if self.history_dialog.isVisible() and self.history_dialog.geometry().contains(pt):
            return True
        return False

    def _connect_signals(self):
        # 1. Selection detected -> Show floating Voxel logo
        self.listener.text_selected.connect(self._on_text_selected, Qt.ConnectionType.QueuedConnection)

        # 2. Bubble clicked -> Launch playback & open Mini Player
        self.bubble.clicked.connect(self._on_bubble_clicked)

        # 3. User clicked empty outside space -> Fade out bubble
        self.listener.clicked_outside.connect(self._on_clicked_outside, Qt.ConnectionType.QueuedConnection)

        # 4. Tray, History, Settings & Direct Clipboard controls
        self.tray.toggle_enabled_requested.connect(self._on_tray_toggle_enabled)
        self.tray.history_requested.connect(self._show_history)
        self.tray.settings_requested.connect(self._show_settings)
        self.tray.read_clipboard_requested.connect(self._on_read_clipboard_requested)
        self.player.settings_requested.connect(self._show_settings)
        self.history_dialog.replay_requested.connect(self._replay_history)
        self.settings_dialog.settings_applied.connect(self._on_settings_applied)
        self.tray.quit_requested.connect(self.quit)

        # 5. Permission guidance on macOS
        self.listener.permission_needed.connect(self._on_permission_needed)

        # App shutdown hook
        self.app.aboutToQuit.connect(self._cleanup)

    def _on_text_selected(self, text: str, x: int, y: int):
        """Called when text is selected in any application."""
        if settings_db.get("selection_popup_enabled", True):
            self.bubble.show_at(text, x, y)

    def _on_bubble_clicked(self, text: str):
        """Called when user clicks the floating Voxel logo."""
        self.player.play_text(text)

    def _on_clicked_outside(self):
        """Called when user clicks elsewhere on screen."""
        if self.bubble.isVisible():
            self.bubble.fade_out()

    def _on_read_clipboard_requested(self):
        """Reads current system clipboard aloud directly."""
        try:
            text = pyperclip.paste().strip()
            if text:
                self.player.play_text(text)
        except Exception as e:
            print(f"[Main] Clipboard read error: {e}")

    def _on_permission_needed(self):
        """Informs user if macOS Accessibility permission is required for global hooks."""
        if IS_MAC:
            self.tray.showMessage(
                "Voxel: Accessibility Permission",
                "To detect selected text across your apps, please grant Accessibility in System Settings.",
                AppTrayIcon.MessageIcon.Warning,
                6000
            )

    def _show_history(self):
        """Displays the JSON history dialog."""
        try:
            self.history_dialog.load_history()
            self.history_dialog.show()
            self.history_dialog.activateWindow()
        except Exception as e:
            print(f"[Voxel] Error showing history dialog: {e}", file=sys.stderr)

    def _show_settings(self):
        """Displays the settings dialog with about & version info."""
        try:
            self.settings_dialog.load_values()
            self.settings_dialog.show()
            self.settings_dialog.activateWindow()
        except Exception as e:
            print(f"[Voxel] Error showing settings dialog: {e}", file=sys.stderr)

    def _on_settings_applied(self):
        """Applies updated settings across the app."""
        self._apply_initial_settings()
        enabled = settings_db.get("selection_popup_enabled", True)
        self.listener.set_enabled(enabled)
        self.tray.enable_action.setChecked(enabled)

    def _on_tray_toggle_enabled(self, enabled: bool):
        settings_db.set("selection_popup_enabled", enabled)
        self.listener.set_enabled(enabled)

    def _replay_history(self, text: str):
        """Replays selected history item."""
        self.player.play_text(text)

    def _cleanup(self):
        """Clean up threads and temp files on exit."""
        self.listener.stop()
        self.tts.stop()

    def start(self):
        """Starts listeners and enters Qt event loop."""
        self.tray.show()
        self.listener.start()

        hotkey_desc = "Cmd+Alt+S" if IS_MAC else "Ctrl+Alt+S"
        self.tray.showMessage(
            f"{APP_NAME} ({VERSION}) is Active",
            f"Select text in any app to read it aloud. Press {hotkey_desc} anytime!",
            AppTrayIcon.MessageIcon.Information,
            3500
        )

        sys.exit(self.app.exec())

    def quit(self):
        self._cleanup()
        self.app.quit()


if __name__ == "__main__":
    app_instance = VoxelApp()
    app_instance.start()
