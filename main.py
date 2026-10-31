"""
Voxel - Text to Speech, Anywhere.
Main Application Entry Point.
Coordinates UI widgets, background selection listeners, settings, and TTS playback.
"""
import sys
import os
import traceback
import pyperclip
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt, QPoint, QTimer

# Install top-level crash guard so unhandled slot exceptions never abort the process
def _global_exception_handler(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"[Voxel Uncaught Error] {err_msg}", file=sys.stderr)

sys.excepthook = _global_exception_handler

from src.config import VERSION, VOICES, APP_NAME, APP_TAGLINE, IS_MAC, DEFAULT_EMOTION_MODE
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
from src.utils.document_reader import capture_full_document_from_active_window, extract_text_from_file


class VoxelApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationDisplayName("")
        self.app.setWindowIcon(create_app_icon(64))

        # Core Components
        self.tts = TTSEngine()
        self.bubble = FloatingBubble()
        self.player = MiniPlayer(self.tts)
        self.tray = AppTrayIcon(self.tts)
        self.history_dialog = HistoryDialog()
        self._last_selected_text = ""
        self.settings_dialog = SettingsDialog(tts_engine=self.tts)

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
        self.player.btn_speed.setText(f"{saved_speed}x ▾")

        # 3. Bubble timeout
        saved_timeout = settings_db.get("bubble_timeout", 4.0)
        self.bubble.hide_timer.setInterval(int(saved_timeout * 1000))

        # 4. Player & Bubble Theme
        saved_theme = settings_db.get("settings_theme", "light")
        player_theme = "light_glass" if saved_theme == "light" else "dark_glass"
        self.player.apply_theme(player_theme)
        if hasattr(self.bubble, "set_theme_mode"):
            self.bubble.set_theme_mode(player_theme)

        # 5. Emotion & Expressiveness
        saved_emotion = settings_db.get("emotion_mode", DEFAULT_EMOTION_MODE)
        self.tts.set_emotion_mode(saved_emotion)

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

        # 2. Bubble actions: Read Selection, Read Document, Open File, Hover Pre-buffer
        self.bubble.clicked.connect(self._on_bubble_clicked)
        self.bubble.read_document_requested.connect(self._on_read_document_requested)
        self.bubble.open_file_requested.connect(self._on_open_file_requested)
        self.bubble.settings_requested.connect(self._show_settings)
        self.bubble.about_requested.connect(self._show_about)
        self.bubble.quit_requested.connect(self.quit)
        self.bubble.hovered.connect(self._on_bubble_hovered)

        # 3. User clicked empty outside space -> Fade out bubble
        self.listener.clicked_outside.connect(self._on_clicked_outside, Qt.ConnectionType.QueuedConnection)

        # 4. Tray, Player, History, Settings & Document Controls
        self.tray.toggle_enabled_requested.connect(self._on_tray_toggle_enabled)
        self.tray.history_requested.connect(self._show_history)
        self.tray.settings_requested.connect(self._show_settings)
        self.tray.about_requested.connect(self._show_about)
        self.tray.read_clipboard_requested.connect(self._on_read_clipboard_requested)
        self.tray.read_document_requested.connect(self._on_read_document_requested)
        self.tray.open_file_requested.connect(self._on_open_file_requested)

        self.player.read_document_requested.connect(self._on_read_document_requested)
        self.player.settings_requested.connect(self._show_settings)
        self.player.recording_saved.connect(self._on_recording_saved)

        self.history_dialog.replay_requested.connect(self._replay_history)
        self.settings_dialog.settings_applied.connect(self._on_settings_applied)
        self.tray.quit_requested.connect(self.quit)

        # 5. Global Hotkeys: Document reader & Permission guidance
        self.listener.document_hotkey_triggered.connect(self._on_read_document_requested, Qt.ConnectionType.QueuedConnection)
        self.listener.permission_needed.connect(self._on_permission_needed)

        # App shutdown hook
        self.app.aboutToQuit.connect(self._cleanup)

    def _on_text_selected(self, text: str, x: int, y: int):
        """Called when text is selected in any application."""
        self._last_selected_text = text
        if settings_db.get("selection_popup_enabled", True):
            self.bubble.show_at(text, x, y)

    def _on_bubble_clicked(self, text: str):
        """Called when user clicks the floating Voxel logo to read selected text."""
        self.player.play_text(text)

    def _on_bubble_hovered(self, text: str):
        """Pre-buffers first sentence on hover for 0ms sub-second latency playback."""
        if settings_db.get("prebuffer_enabled", True):
            self.tts.prefetch(text)

    def _on_read_document_requested(self, fallback_text: str = ""):
        """
        Captures full document text from active Google Docs, Word, PDF, or Presentation window.
        Uses asynchronous singleShot to allow mouse release and window focus to return to document.
        Does NOT mistakenly downgrade to a single highlighted word when user requested full document.
        """
        active_fallback = fallback_text or getattr(self, "_last_selected_text", "")

        def _do_capture():
            try:
                doc_text = capture_full_document_from_active_window(timeout_ms=1400)
                if doc_text and len(doc_text) >= 15:
                    self.player.play_text(doc_text)
                elif doc_text and len(doc_text) >= 2:
                    self.player.play_text(doc_text)
                elif active_fallback and len(active_fallback.strip()) >= 20:
                    # Only fallback if user had previously selected a substantial block of text
                    self.player.play_text(active_fallback.strip())
                else:
                    self.tray.showMessage(
                        "Voxel Document Reader",
                        "Could not capture entire document. Please ensure Google Docs or your document window is open and active.",
                        AppTrayIcon.MessageIcon.Information,
                        3000
                    )
            except Exception as e:
                print(f"[Main] Document capture error: {e}", file=sys.stderr)
                if active_fallback:
                    self.player.play_text(active_fallback)

        # 200ms delay lets mouse release and background document window regain full focus
        QTimer.singleShot(200, _do_capture)

    def _on_open_file_requested(self):
        """Opens file picker dialog to extract and read PDF, Word, or text files directly."""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Open Document or Presentation for Narration",
            "",
            "Supported Files (*.pdf *.docx *.txt *.md *.rtf *.csv);;PDF Documents (*.pdf);;Word Documents (*.docx);;Text Files (*.txt *.md);;All Files (*)"
        )
        if file_path:
            text = extract_text_from_file(file_path)
            if text and len(text) >= 2:
                self.player.play_text(text)
            else:
                self.tray.showMessage(
                    "Voxel File Reader",
                    "Could not extract readable text from the selected file.",
                    AppTrayIcon.MessageIcon.Warning,
                    3000
                )

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
        """Displays the settings dialog on Preferences tab."""
        try:
            self.settings_dialog.load_values()
            self.settings_dialog.open_preferences()
        except Exception as e:
            print(f"[Voxel] Error showing settings dialog: {e}", file=sys.stderr)

    def _show_about(self):
        """Displays the settings dialog on About tab."""
        try:
            self.settings_dialog.open_about()
        except Exception as e:
            print(f"[Voxel] Error showing about dialog: {e}", file=sys.stderr)

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

    def _on_recording_saved(self, file_path: str):
        """Notifies user when an audio recording has been saved to the Documents folder."""
        filename = os.path.basename(file_path)
        self.tray.showMessage(
            "🎙️ Voxel Recording Saved",
            f"Saved to Documents/Voxel Recordings/{filename}",
            AppTrayIcon.MessageIcon.Information,
            4000
        )

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


_single_instance_handle = None


def acquire_single_instance_lock():
    """
    Guarantees only a single instance of Voxel runs at any time,
    preventing duplicate tray icons and background hook conflicts.
    """
    global _single_instance_handle
    if sys.platform == "win32":
        try:
            import ctypes
            mutex_name = "Voxel_SingleInstance_Mutex_Digimo"
            mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
            if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                return False
            _single_instance_handle = mutex
            return True
        except Exception as e:
            print(f"[Voxel] Mutex warning: {e}", file=sys.stderr)
            return True
    else:
        from PyQt6.QtCore import QSharedMemory
        shared_mem = QSharedMemory("Voxel_SingleInstance_Digimo")
        if not shared_mem.create(1):
            return False
        _single_instance_handle = shared_mem
        return True


if __name__ == "__main__":
    if not acquire_single_instance_lock():
        print(f"[Voxel] Another instance is already running in the system tray. Exiting duplicate.", file=sys.stderr)
        sys.exit(0)

    app_instance = VoxelApp()
    app_instance.start()
