"""Voxel Preferences & About dialog."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QComboBox, QCheckBox, QDoubleSpinBox, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QDesktopServices, QPixmap

from src.config import THEME, VOICES, SPEED_STEPS, VERSION, GITHUB_URL
from src.utils.settings import settings_db
from assets.icons import create_voxel_logo


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Voxel — Settings")
        self.setFixedSize(520, 470)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"""
            QDialog {{ background: #151C2B; color: #F8FAFF; }}
            QTabWidget::pane {{ border: 1px solid #2A344A; background: #192235; border-radius: 10px; }}
            QTabBar::tab {{ background: #20283A; color: #A7B2C6; padding: 9px 16px; border-top-left-radius: 7px; border-top-right-radius: 7px; margin-right: 4px; }}
            QTabBar::tab:selected {{ background: #192235; color: #FFFFFF; border-bottom: 2px solid #168BFF; }}
            QGroupBox {{ border: 1px solid #2A344A; border-radius: 8px; margin-top: 12px; padding-top: 13px; font-weight: 600; }}
            QComboBox, QDoubleSpinBox {{ background: #20283A; color: #F8FAFF; border: 1px solid #36435C; border-radius: 6px; padding: 6px; }}
            QCheckBox {{ color: #F8FAFF; spacing: 8px; }}
            QPushButton {{ background: #20283A; color: #F8FAFF; border: 1px solid #36435C; border-radius: 7px; padding: 7px 13px; }}
            QPushButton:hover {{ background: #2B3853; }}
        """)
        self._init_ui()
        self.load_values()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        self.tabs = QTabWidget(self)

        prefs = QWidget()
        prefs_layout = QVBoxLayout(prefs)
        prefs_layout.setContentsMargins(14, 14, 14, 14)
        form = QFormLayout()
        form.setSpacing(11)

        self.combo_voice = QComboBox(self)
        for voice in VOICES:
            self.combo_voice.addItem(voice["label"], voice["id"])
        form.addRow("Default voice", self.combo_voice)

        self.combo_speed = QComboBox(self)
        for speed in SPEED_STEPS:
            self.combo_speed.addItem(f"{speed:g}×", speed)
        form.addRow("Default speed", self.combo_speed)

        self.combo_dock = QComboBox(self)
        self.combo_dock.addItem("Bottom-right", "bottom_right")
        self.combo_dock.addItem("Near selection", "near_cursor")
        form.addRow("Player position", self.combo_dock)

        self.combo_theme = QComboBox(self)
        self.combo_theme.addItem("Dark", "dark")
        self.combo_theme.addItem("Glass", "glass")
        form.addRow("Player appearance", self.combo_theme)

        self.spin_timeout = QDoubleSpinBox(self)
        self.spin_timeout.setRange(1.5, 12.0)
        self.spin_timeout.setSingleStep(0.5)
        self.spin_timeout.setSuffix(" sec")
        form.addRow("Trigger timeout", self.spin_timeout)

        prefs_layout.addLayout(form)
        self.chk_trigger = QCheckBox("Show floating Voxel trigger on text selection", self)
        prefs_layout.addWidget(self.chk_trigger)
        help_text = QLabel("Dark uses a solid charcoal surface. Glass uses a pale translucent finish. Some transparency effects depend on Windows desktop composition.", self)
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color:#A7B2C6;")
        prefs_layout.addWidget(help_text)
        prefs_layout.addStretch()
        self.tabs.addTab(prefs, "Preferences")

        about = QWidget()
        about_layout = QVBoxLayout(about)
        about_layout.setContentsMargins(18, 18, 18, 18)
        about_layout.setSpacing(10)
        logo = QLabel(self)
        logo.setPixmap(create_voxel_logo(56).pixmap(56, 56))
        about_layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignHCenter)
        name = QLabel("Voxel")
        name.setFont(QFont("Segoe UI", 19, QFont.Weight.Bold))
        name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        about_layout.addWidget(name)
        tagline = QLabel("Text to Speech, Anywhere.")
        tagline.setStyleSheet("color:#A7B2C6;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        about_layout.addWidget(tagline)
        about_layout.addSpacing(8)

        ver_box = QGroupBox("Version")
        ver_layout = QVBoxLayout(ver_box)
        ver_layout.addWidget(QLabel(f"Current version: {VERSION}"))
        about_layout.addWidget(ver_box)

        repo_box = QGroupBox("Project")
        repo_layout = QVBoxLayout(repo_box)
        repo_layout.addWidget(QLabel("Created and maintained by Digimo2020"))
        repo_link = QPushButton("Open Voxel on GitHub")
        repo_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        repo_link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        repo_layout.addWidget(repo_link)
        about_layout.addWidget(repo_box)
        about_layout.addStretch()
        self.tabs.addTab(about, "About")

        main_layout.addWidget(self.tabs)
        buttons = QHBoxLayout()
        buttons.addStretch()
        save = QPushButton("Save & Apply")
        save.setStyleSheet("background:#168BFF; color:#FFFFFF; border-color:#168BFF;")
        save.clicked.connect(self.save_and_apply)
        buttons.addWidget(save)
        close = QPushButton("Close")
        close.clicked.connect(self.close)
        buttons.addWidget(close)
        main_layout.addLayout(buttons)

    def load_values(self):
        voice_id = settings_db.get("default_voice", "en-US-JennyNeural")
        idx = self.combo_voice.findData(voice_id)
        if idx >= 0:
            self.combo_voice.setCurrentIndex(idx)

        speed = settings_db.get("default_speed", 1.0)
        idx = self.combo_speed.findData(speed)
        if idx >= 0:
            self.combo_speed.setCurrentIndex(idx)

        dock = settings_db.get("dock_position", "bottom_right")
        idx = self.combo_dock.findData(dock)
        if idx >= 0:
            self.combo_dock.setCurrentIndex(idx)

        theme = settings_db.get("player_theme", "dark")
        idx = self.combo_theme.findData(theme)
        self.combo_theme.setCurrentIndex(max(0, idx))

        self.spin_timeout.setValue(settings_db.get("bubble_timeout", 4.0))
        self.chk_trigger.setChecked(settings_db.get("selection_popup_enabled", True))

    def save_and_apply(self):
        settings_db.set("default_voice", self.combo_voice.currentData())
        settings_db.set("default_speed", self.combo_speed.currentData())
        settings_db.set("dock_position", self.combo_dock.currentData())
        settings_db.set("player_theme", self.combo_theme.currentData())
        settings_db.set("bubble_timeout", self.spin_timeout.value())
        settings_db.set("selection_popup_enabled", self.chk_trigger.isChecked())
        self.settings_applied.emit()
        self.close()
