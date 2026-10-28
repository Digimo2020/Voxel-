"""
Text 2 Voice - Main Application Entry Point.
Coordinates UI widgets, background selection listeners, and TTS playback.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint

from src.tts_engine import TTSEngine
from src.selection_listener import SelectionListener
from src.ui.floating_bubble import FloatingBubble
from src.ui.mini_player import MiniPlayer
from src.ui.tray_icon import AppTrayIcon
from src.ui.history_dialog import HistoryDialog
from assets.icons import create_app_icon


class Text2VoiceApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("Text 2 Voice")
        self.app.setWindowIcon(create_app_icon(64))

        # Core Components
        self.tts = TTSEngine()
        self.bubble = FloatingBubble()
        self.player = MiniPlayer(self.tts)
        self.tray = AppTrayIcon(self.tts)
        self.history_dialog = HistoryDialog()

        # Selection Listener with collision check function
        self.listener = SelectionListener(
            is_inside_widget_fn=self.is_inside_any_widget
        )

        self._connect_signals()

    def is_inside_any_widget(self, x: int, y: int) -> bool:
        """Returns True if point (x, y) is inside the Bubble or Player window."""
        pt = QPoint(x, y)
        if self.bubble.isVisible() and self.bubble.geometry().contains(pt):
            return True
        if self.player.isVisible() and self.player.geometry().contains(pt):
            return True
        return False

    def _connect_signals(self):
        # 1. Selection detected -> Show floating mic bubble (QueuedConnection ensures thread safety)
        self.listener.text_selected.connect(self._on_text_selected, Qt.ConnectionType.QueuedConnection)

        # 2. Bubble clicked -> Launch playback & open Mini Player
        self.bubble.clicked.connect(self._on_bubble_clicked)

        # 3. User clicked empty outside space -> Fade out bubble
        self.listener.clicked_outside.connect(self._on_clicked_outside, Qt.ConnectionType.QueuedConnection)

        # 4. Tray & History controls
        self.tray.toggle_enabled_requested.connect(self.listener.set_enabled)
        self.tray.history_requested.connect(self._show_history)
        self.history_dialog.replay_requested.connect(self._replay_history)
        self.tray.quit_requested.connect(self.quit)

        # App shutdown hook
        self.app.aboutToQuit.connect(self._cleanup)

    def _on_text_selected(self, text: str, x: int, y: int):
        """Called when text is selected in any application."""
        self.bubble.show_at(text, x, y)

    def _on_bubble_clicked(self, text: str):
        """Called when user clicks the floating mic/speaker bubble."""
        self.player.play_text(text)

    def _on_clicked_outside(self):
        """Called when user clicks elsewhere on screen."""
        if self.bubble.isVisible():
            self.bubble.fade_out()

    def _show_history(self):
        """Displays the JSON history dialog."""
        self.history_dialog.load_history()
        self.history_dialog.show()
        self.history_dialog.activateWindow()

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

        # Show notification on startup
        self.tray.showMessage(
            "Text 2 Voice is Active",
            "Select any text in any app to read it aloud. Press Ctrl+Alt+S anytime!",
            AppTrayIcon.MessageIcon.Information,
            3500
        )

        sys.exit(self.app.exec())

    def quit(self):
        self._cleanup()
        self.app.quit()


if __name__ == "__main__":
    app_instance = Text2VoiceApp()
    app_instance.start()
