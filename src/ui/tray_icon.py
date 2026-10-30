"""
Menu Bar / System Tray Icon for Voxel.
Lives in the Windows Notification Area / macOS Menu Bar.
Supports:
- Left-click opens Settings & Preferences immediately.
- Right-click reveals rich context menu including Read Document, File Picker, Voices, History, and Downloads.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QActionGroup, QDesktopServices
from PyQt6.QtCore import pyqtSignal, QUrl

from src.config import VOICES, VERSION, GITHUB_URL, APP_NAME, APP_TAGLINE, IS_MAC
from src.tts_engine import TTSEngine
from assets.icons import create_tray_icon


class AppTrayIcon(QSystemTrayIcon):
    """
    System Tray / Startup Bar icon for quick controls, document narration, and preferences.
    """
    toggle_enabled_requested = pyqtSignal(bool)
    history_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    read_clipboard_requested = pyqtSignal()
    read_document_requested = pyqtSignal()
    open_file_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.setIcon(create_tray_icon(size=32))
        self.setToolTip(f"{APP_NAME} ({VERSION}) — {APP_TAGLINE}\n• Left-Click: Open Settings\n• Right-Click: Quick Menu")

        self._init_menu()
        self.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Opens Settings dialog immediately when user left-clicks the startup tray icon."""
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.settings_requested.emit()

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

        # Read Entire Document (Google Docs / PDF / Presentation)
        hotkey_str = "Cmd+Alt+D" if IS_MAC else "Ctrl+Alt+D"
        read_doc_action = menu.addAction(f"📑 Read Entire Document ({hotkey_str})")
        read_doc_action.setToolTip("Reads all text from currently active Google Docs, Word, PDF, or Presentation")
        read_doc_action.triggered.connect(self.read_document_requested.emit)

        # Open & Read Document File
        open_file_action = menu.addAction("📂 Open & Read File (PDF / Slides / Docs)...")
        open_file_action.triggered.connect(self.open_file_requested.emit)

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

        # Settings & Preferences dialog
        settings_action = menu.addAction("⚙️ Settings & Preferences...")
        settings_action.triggered.connect(self.settings_requested.emit)

        # Platform-specific direct download link
        if IS_MAC:
            down_action = menu.addAction(f"📥 Download macOS Installer ({VERSION})...")
            down_url = f"{GITHUB_URL}/releases/download/{VERSION}/Voxel-{VERSION}.pkg"
        else:
            down_action = menu.addAction(f"📥 Download Windows App ({VERSION})...")
            down_url = f"{GITHUB_URL}/releases/download/{VERSION}/Voxel-{VERSION}.exe"
        down_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(down_url)))

        menu.addSeparator()

        # Quit
        quit_action = menu.addAction("Quit Voxel")
        quit_action.triggered.connect(self.quit_requested.emit)

        self.setContextMenu(menu)

    def _on_voice_selected(self, index: int):
        self.tts.set_voice_index(index)
