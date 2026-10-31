"""
Menu Bar / System Tray Icon for Voxel.
Lives in the Windows Notification Area / macOS Menu Bar.
Provides:
- Double-click to open Preferences.
- Clean, wider, focused right-click context menu with Preferences, About, and Quit.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal

from src.config import VERSION, APP_NAME, APP_TAGLINE
from src.tts_engine import TTSEngine
from assets.icons import create_tray_icon


class AppTrayIcon(QSystemTrayIcon):
    """
    Streamlined System Tray icon for quick access to Preferences, About, and App Controls.
    """
    settings_requested = pyqtSignal()
    about_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    # Retained for signal compatibility
    toggle_enabled_requested = pyqtSignal(bool)
    history_requested = pyqtSignal()
    read_clipboard_requested = pyqtSignal()
    read_document_requested = pyqtSignal(str)
    open_file_requested = pyqtSignal()

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.setIcon(create_tray_icon(size=32))
        self.setToolTip(f"{APP_NAME} ({VERSION}) — {APP_TAGLINE}\n• Double-Click: Open Preferences\n• Right-Click: Menu")

        self._init_menu()
        self.activated.connect(self._on_tray_activated)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Opens Preferences dialog strictly on double-click."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.settings_requested.emit()

    def _init_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #171A29;
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 10px;
                padding: 6px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                min-width: 220px;
                padding: 8px 16px;
                border-radius: 6px;
                margin: 2px 2px;
                font-weight: 500;
            }
            QMenu::item:selected {
                background-color: #0084FF;
                color: #FFFFFF;
                font-weight: 600;
            }
            QMenu::item:disabled {
                color: #60A5FA;
                font-weight: 700;
                font-size: 13px;
                padding: 8px 16px 6px 16px;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(255, 255, 255, 0.10);
                margin: 5px 8px;
            }
        """)

        # Header Title with Version (Disabled, styled header)
        title_action = menu.addAction(f"🎙  {APP_NAME}  ({VERSION})")
        title_action.setEnabled(False)

        menu.addSeparator()

        # Preferences
        settings_action = menu.addAction("⚙️  Preferences...")
        settings_action.triggered.connect(self.settings_requested.emit)

        # About Voxel
        about_action = menu.addAction("ℹ️  About Voxel...")
        about_action.triggered.connect(self.about_requested.emit)

        menu.addSeparator()

        # Quit
        quit_action = menu.addAction("Quit Voxel")
        quit_action.triggered.connect(self.quit_requested.emit)

        self.setContextMenu(menu)
