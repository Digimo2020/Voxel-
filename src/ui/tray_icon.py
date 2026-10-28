"""
Menu Bar / System Tray Icon for Voxel.
Lives in the macOS Menu Bar (or Windows Notification Area) for quick controls and settings.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QActionGroup, QDesktopServices
from PyQt6.QtCore import pyqtSignal, QUrl

from src.config import VOICES, VERSION, GITHUB_URL, APP_NAME, APP_TAGLINE, IS_MAC
from src.tts_engine import TTSEngine
from assets.icons import create_tray_icon


class AppTrayIcon(QSystemTrayIcon):
    """
    Menu Bar / System Tray icon for quick control, settings access, and status.
    """
    toggle_enabled_requested = pyqtSignal(bool)
    history_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    read_clipboard_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.setIcon(create_tray_icon(size=32))
        self.setToolTip(f"{APP_NAME} ({VERSION}) — {APP_TAGLINE}")

        self._init_menu()

    def _init_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #131625;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0084FF;
                color: #FFFFFF;
            }
        """)

        # Header Title with Version
        title_action = menu.addAction(f"🎙 {APP_NAME} ({VERSION})")
        title_action.setEnabled(False)
        menu.addSeparator()

        # Read Clipboard Directly action
        read_clip = menu.addAction("🔊 Read Current Clipboard")
        read_clip.triggered.connect(self.read_clipboard_requested.emit)

        # Enable / Disable toggle checkbox
        self.enable_action = QAction("Enable Text Selection Trigger", menu)
        self.enable_action.setCheckable(True)
        self.enable_action.setChecked(True)
        self.enable_action.toggled.connect(self.toggle_enabled_requested.emit)
        menu.addAction(self.enable_action)

        menu.addSeparator()

        # Voice selection submenu
        voice_menu = menu.addMenu("Voices")
        voice_menu.setStyleSheet(menu.styleSheet())
        self.voice_action_group = QActionGroup(self)
        self.voice_action_group.setExclusive(True)

        for i, v in enumerate(VOICES):
            action = QAction(v["label"], voice_menu)
            action.setCheckable(True)
            if i == self.tts.current_voice_index:
                action.setChecked(True)
            action.triggered.connect(lambda checked, idx=i: self._on_voice_selected(idx))
            self.voice_action_group.addAction(action)
            voice_menu.addAction(action)

        menu.addSeparator()

        # History dialog
        history_action = menu.addAction("📜 History & Recent Clips...")
        history_action.triggered.connect(self.history_requested.emit)

        # Settings & Downloads dialog
        settings_action = menu.addAction("⚙️ Settings & Downloads...")
        settings_action.triggered.connect(self.settings_requested.emit)

        # Platform-specific direct download link (OS-adaptive)
        if IS_MAC:
            down_action = menu.addAction("📥 Download macOS Installer (.pkg)...")
            down_url = f"{GITHUB_URL}/releases/latest/download/Voxel.pkg"
        else:
            down_action = menu.addAction("📥 Download Windows App (.exe)...")
            down_url = f"{GITHUB_URL}/releases/latest/download/Voxel.exe"
        down_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(down_url)))

        menu.addSeparator()

        # Quit
        quit_action = menu.addAction("Quit Voxel")
        quit_action.triggered.connect(self.quit_requested.emit)

        self.setContextMenu(menu)

    def _on_voice_selected(self, index: int):
        self.tts.set_voice_index(index)
