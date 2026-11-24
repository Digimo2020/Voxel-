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
    read_selection_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
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

        sel_key = "Cmd+Opt+S" if IS_MAC else "Ctrl+Alt+S"
        doc_key = "Cmd+Opt+D" if IS_MAC else "Ctrl+Alt+D"
        a = menu.addAction(ic("play"), f"Read selected text\t{sel_key}")
        a.triggered.connect(self.read_selection_requested.emit)
        a = menu.addAction(ic("file-text"), f"Read whole document\t{doc_key}")
        a.triggered.connect(lambda: self.read_document_requested.emit(""))
        a = menu.addAction(ic("clipboard"), "Read copied text")
        a.triggered.connect(self.read_clipboard_requested.emit)
        self.pause_action = menu.addAction(ic("pause"), "Pause")
        self.pause_action.triggered.connect(self.pause_requested.emit)
        self.stop_action = menu.addAction(ic("square"), "Stop")
        self.stop_action.triggered.connect(self.stop_requested.emit)
        menu.addSeparator()

        self.enable_action = menu.addAction("Bubble on selection")
        self.enable_action.setCheckable(True)
        try:
            from src.utils.settings import settings_db
            self.enable_action.setChecked(bool(settings_db.get("selection_popup_enabled", True)))
        except Exception:
            self.enable_action.setChecked(True)
        self.enable_action.toggled.connect(self.toggle_enabled_requested.emit)
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

        menu.aboutToShow.connect(self._refresh_playback_actions)
        self._menu = menu
        self.setContextMenu(menu)

    def _refresh_playback_actions(self):
        """Show Pause/Resume and Stop only while Voxel is reading."""
        speaking = bool(getattr(self.tts, "is_speaking", False))
        paused = bool(getattr(self.tts, "is_paused", False))
        self.pause_action.setVisible(speaking)
        self.stop_action.setVisible(speaking)
        self.pause_action.setText("Resume" if paused else "Pause")
