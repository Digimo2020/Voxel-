"""
Settings & About Dialog.
Allows users to configure voices, speeds, trigger behaviors, and docking positions.
Displays current version (v1.0.01) and clickable GitHub repository link.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QComboBox, QCheckBox, QDoubleSpinBox, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QDesktopServices

from src.config import THEME, VOICES, SPEED_STEPS, VERSION, GITHUB_URL
from src.utils.settings import settings_db


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Text 2 Voice — Settings & About")
        self.setFixedSize(500, 440)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME["bg_player"]};
                color: {THEME["text_primary"]};
            }}
            QTabWidget::pane {{
                border: 1px solid {THEME["border_player"]};
                background-color: #181926;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: #1E2030;
                color: {THEME["text_secondary"]};
                padding: 8px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: #181926;
                color: #FFFFFF;
                border-bottom: 2px solid {THEME["accent"]};
            }}
            QGroupBox {{
                border: 1px solid {THEME["border_player"]};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 14px;
                font-weight: bold;
                color: {THEME["text_primary"]};
            }}
            QComboBox, QDoubleSpinBox {{
                background-color: #24273A;
                color: {THEME["text_primary"]};
                border: 1px solid {THEME["border_player"]};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QCheckBox {{
                color: {THEME["text_primary"]};
                spacing: 8px;
            }}
            QPushButton {{
                background-color: {THEME["button_bg"]};
                color: {THEME["text_primary"]};
                border: 1px solid {THEME["border_player"]};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME["button_hover"]};
            }}
        """)

        self._init_ui()
        self.load_values()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget(self)

        # Tab 1: General Preferences
        tab_prefs = QWidget()
        layout_prefs = QVBoxLayout(tab_prefs)
        layout_prefs.setContentsMargins(14, 14, 14, 14)
        layout_prefs.setSpacing(12)

        # Form Layout
        form = QFormLayout()
        form.setSpacing(10)

        # Default Voice
        self.combo_voice = QComboBox(self)
        for v in VOICES:
            self.combo_voice.addItem(v["label"], v["id"])
        form.addRow("Default Voice:", self.combo_voice)

        # Default Speed
        self.combo_speed = QComboBox(self)
        for s in SPEED_STEPS:
            self.combo_speed.addItem(f"{s}x", s)
        form.addRow("Default Speed:", self.combo_speed)

        # Docking Position
        self.combo_dock = QComboBox(self)
        self.combo_dock.addItem("Bottom-Right Corner (Animated)", "bottom_right")
        self.combo_dock.addItem("Near Selection Cursor", "near_cursor")
        form.addRow("Player Position:", self.combo_dock)

        # Bubble Timeout
        self.spin_timeout = QDoubleSpinBox(self)
        self.spin_timeout.setRange(1.5, 12.0)
        self.spin_timeout.setSingleStep(0.5)
        self.spin_timeout.setSuffix(" sec")
        form.addRow("Trigger Timeout:", self.spin_timeout)

        layout_prefs.addLayout(form)

        # Selection trigger checkbox
        self.chk_trigger = QCheckBox("Show floating speaker trigger when selecting text", self)
        layout_prefs.addWidget(self.chk_trigger)
        layout_prefs.addStretch()

        self.tabs.addTab(tab_prefs, "⚙️ Preferences")

        # Tab 2: About & Version
        tab_about = QWidget()
        layout_about = QVBoxLayout(tab_about)
        layout_about.setContentsMargins(16, 16, 16, 16)
        layout_about.setSpacing(10)

        title_lbl = QLabel("🔊 Text 2 Voice", self)
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {THEME['accent']};")
        layout_about.addWidget(title_lbl)

        sub_lbl = QLabel("Universal Frosted Glass Text-to-Speech Engine", self)
        sub_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        sub_lbl.setStyleSheet("color: #94A3B8;")
        layout_about.addWidget(sub_lbl)

        # Version Pill Box
        ver_box = QGroupBox("Release & Version Information", self)
        ver_layout = QVBoxLayout(ver_box)
        ver_layout.setSpacing(6)

        lbl_ver = QLabel(f"Current Version: <b><font color='#60A5FA'>{VERSION}</font></b>", self)
        lbl_ver.setFont(QFont("Segoe UI", 11))
        ver_layout.addWidget(lbl_ver)

        lbl_ver_rule = QLabel(
            "Structure: <code>v&lt;Major&gt;.&lt;Minor&gt;.&lt;Patch:02d&gt;</code><br>"
            "Every 10th patch increments minor, every 10th minor increments major.", self
        )
        lbl_ver_rule.setStyleSheet("color: #94A3B8; font-size: 11px;")
        ver_layout.addWidget(lbl_ver_rule)

        layout_about.addWidget(ver_box)

        # GitHub Project Info Box
        gh_box = QGroupBox("Open Source Repository", self)
        gh_layout = QVBoxLayout(gh_box)
        gh_layout.setSpacing(8)

        lbl_author = QLabel("Created & Maintained by: <b>Digimo2020</b>", self)
        gh_layout.addWidget(lbl_author)

        btn_gh = QPushButton(f"🌐 Open GitHub: {GITHUB_URL}", self)
        btn_gh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_gh.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(96, 165, 250, 0.15);
                border: 1px solid rgba(96, 165, 250, 0.6);
                color: #93C5FD;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(96, 165, 250, 0.3);
                color: #FFFFFF;
            }}
        """)
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        gh_layout.addWidget(btn_gh)

        layout_about.addWidget(gh_box)
        layout_about.addStretch()

        self.tabs.addTab(tab_about, "ℹ️ About & Version")
        main_layout.addWidget(self.tabs)

        # Bottom buttons: Save & Cancel
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_save = QPushButton("Save & Apply", self)
        btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_save.setStyleSheet(f"background-color: {THEME['accent']}; color: #11111B;")
        btn_save.clicked.connect(self.save_and_apply)
        btn_row.addWidget(btn_save)

        btn_close = QPushButton("Close", self)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)

        main_layout.addLayout(btn_row)

    def load_values(self):
        """Loads saved settings into controls."""
        voice_id = settings_db.get("default_voice", "en-US-JennyNeural")
        idx = self.combo_voice.findData(voice_id)
        if idx >= 0:
            self.combo_voice.setCurrentIndex(idx)

        speed_val = settings_db.get("default_speed", 1.0)
        idx_sp = self.combo_speed.findData(speed_val)
        if idx_sp >= 0:
            self.combo_speed.setCurrentIndex(idx_sp)

        dock_mode = settings_db.get("dock_position", "bottom_right")
        idx_dk = self.combo_dock.findData(dock_mode)
        if idx_dk >= 0:
            self.combo_dock.setCurrentIndex(idx_dk)

        timeout = settings_db.get("bubble_timeout", 4.0)
        self.spin_timeout.setValue(timeout)

        enabled = settings_db.get("selection_popup_enabled", True)
        self.chk_trigger.setChecked(enabled)

    def save_and_apply(self):
        """Saves values and emits signal."""
        settings_db.set("default_voice", self.combo_voice.currentData())
        settings_db.set("default_speed", self.combo_speed.currentData())
        settings_db.set("dock_position", self.combo_dock.currentData())
        settings_db.set("bubble_timeout", self.spin_timeout.value())
        settings_db.set("selection_popup_enabled", self.chk_trigger.isChecked())

        self.settings_applied.emit()
        self.close()
