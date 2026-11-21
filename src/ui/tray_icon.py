"""
Menu Bar / System Tray Icon for Voxel.
Lives in the Windows Notification Area / macOS Menu Bar.
Provides:
- Double-click to open Preferences.
- Clean, wider, focused right-click context menu with Preferences, About, and Quit.
"""
import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal

from src.config import VERSION, APP_NAME, APP_TAGLINE, IS_MAC
from src.tts_engine import TTSEngine
from assets.icons import create_tray_icon


class AppTrayIcon(QSystemTrayIcon):
    """
    Streamlined System Tray icon for quick access to Preferences, About, and App Controls.
    """
    settings_requested = pyqtSignal()
    about_requested = pyqtSignal()
    permissions_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    # Retained for signal compatibility
    toggle_enabled_requested = pyqtSignal(bool)
    history_requested = pyqtSignal()
    read_clipboard_requested = pyqtSignal()
    reader_requested = pyqtSignal()
    open_requested = pyqtSignal()
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
            self.open_requested.emit()

    def _init_menu(self):
        menu = QMenu()
        from src.ui.design import PALETTES, FONT_STACK, line_icon
        pal = PALETTES["light"]
        menu.setStyleSheet(f"""
            QMenu {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
                     border-radius: 10px; padding: 5px; font-family: {FONT_STACK}; font-size: 13px; }}
            QMenu::item {{ min-width: 200px; padding: 7px 14px; border-radius: 6px; margin: 1px 2px; }}
            QMenu::item:selected {{ background: {pal['accent_soft']}; color: {pal['accent_text']}; }}
            QMenu::item:disabled {{ color: {pal['faint']}; font-size: 12px; }}
            QMenu::separator {{ height: 1px; background: {pal['border']}; margin: 4px 8px; }}
        """)
        ic = lambda name: line_icon(name, pal["muted"], size=16)

        title_action = menu.addAction(f"{APP_NAME}  {VERSION}")
        title_action.setEnabled(False)
        menu.addSeparator()

        open_action = menu.addAction(ic("headphones"), "Open Voxel")
        open_action.triggered.connect(self.open_requested.emit)
        reader_action = menu.addAction(ic("file-text"), "Read Text...")
        reader_action.triggered.connect(self.reader_requested.emit)
        history_action = menu.addAction(ic("history"), "History")
        history_action.triggered.connect(self.history_requested.emit)
        settings_action = menu.addAction(ic("settings-2"), "Settings")
        settings_action.triggered.connect(self.settings_requested.emit)
        if IS_MAC:
            perm_action = menu.addAction(ic("accessibility"), "Accessibility...")
            perm_action.triggered.connect(self.permissions_requested.emit)
        about_action = menu.addAction(ic("info"), "About Voxel")
        about_action.triggered.connect(self.about_requested.emit)

        menu.addSeparator()
        quit_action = menu.addAction("Quit Voxel")
        quit_action.triggered.connect(self.quit_requested.emit)

        self.setContextMenu(menu)
