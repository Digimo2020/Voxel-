"""
System tray icon & context menu for Voxel.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QActionGroup, QDesktopServices
from PyQt6.QtCore import pyqtSignal, QUrl

from src.config import VOICES, VERSION, GITHUB_URL
from src.tts_engine import TTSEngine
from assets.icons import create_app_icon


class AppTrayIcon(QSystemTrayIcon):
    toggle_enabled_requested = pyqtSignal(bool)
    history_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.setIcon(create_app_icon(size=32))
        self.setToolTip(f"Voxel ({VERSION}) — Text to Speech")
        self._init_menu()

    def _init_menu(self):
        menu = QMenu()
        title_action = menu.addAction(f"Voxel ({VERSION})")
        title_action.setEnabled(False)
        menu.addSeparator()

        self.enable_action = QAction("Enable Selection Popup", menu)
        self.enable_action.setCheckable(True)
        self.enable_action.setChecked(True)
        self.enable_action.toggled.connect(self.toggle_enabled_requested.emit)
        menu.addAction(self.enable_action)
        menu.addSeparator()

        voice_menu = menu.addMenu("Voices")
        self.voice_action_group = QActionGroup(self)
        self.voice_action_group.setExclusive(True)
        for i, voice in enumerate(VOICES):
            action = QAction(voice["label"], voice_menu)
            action.setCheckable(True)
            action.setChecked(i == self.tts.current_voice_index)
            action.triggered.connect(lambda checked, idx=i: self._on_voice_selected(idx))
            self.voice_action_group.addAction(action)
            voice_menu.addAction(action)

        test_action = menu.addAction("Test Current Voice")
        test_action.triggered.connect(self._test_voice)

        history_action = menu.addAction("View History")
        history_action.triggered.connect(self.history_requested.emit)

        settings_action = menu.addAction("Settings…")
        settings_action.triggered.connect(self.settings_requested.emit)

        menu.addSeparator()
        repo_action = menu.addAction("Voxel on GitHub")
        repo_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))

        shortcut_info = menu.addAction("Shortcut: Ctrl+Alt+S")
        shortcut_info.setEnabled(False)
        menu.addSeparator()

        quit_action = menu.addAction("Exit Voxel")
        quit_action.triggered.connect(self.quit_requested.emit)
        self.setContextMenu(menu)

    def _on_voice_selected(self, index: int):
        self.tts.set_voice_index(index)

    def _test_voice(self):
        self.tts.speak(f"Hello! This is {self.tts.current_voice['name']}. Voxel text to speech is ready.")
