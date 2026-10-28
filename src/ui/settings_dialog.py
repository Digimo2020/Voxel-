"""
Settings, Downloads & About Dialog for Voxel.
Allows configuring default voices, speeds, trigger timeouts, dock modes, and theme styles.
Features OS-adaptive download options:
- On macOS: Displays macOS .pkg and .dmg download options; Windows .exe is invisible.
- On Windows: Displays Windows .exe download option; macOS .pkg and .dmg are invisible.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QComboBox, QCheckBox, QDoubleSpinBox, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QDesktopServices

from src.config import THEME, VOICES, SPEED_STEPS, VERSION, GITHUB_URL, APP_NAME, APP_TAGLINE, FONT_FAMILY, IS_MAC
from src.utils.settings import settings_db
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from src.ui.voxel_logo_widget import VoxelLogoWidget


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} — Settings & Downloads")
        self.setFixedSize(540, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME["bg_window"]};
                color: {THEME["text_primary"]};
                font-family: {FONT_FAMILY};
            }}
            QTabWidget::pane {{
                border: 1px solid {THEME["border_window"]};
                background-color: #171B2D;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: #1F243B;
                color: {THEME["text_secondary"]};
                padding: 8px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: #171B2D;
                color: #FFFFFF;
                border-bottom: 2px solid {THEME["accent"]};
            }}
            QGroupBox {{
                border: 1px solid {THEME["border_window"]};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 14px;
                font-weight: 600;
                color: {THEME["text_primary"]};
            }}
            QComboBox, QDoubleSpinBox {{
                background-color: #242942;
                color: {THEME["text_primary"]};
                border: 1px solid {THEME["border_window"]};
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QCheckBox {{
                color: {THEME["text_primary"]};
                spacing: 8px;
            }}
            QPushButton {{
                background-color: #242942;
                color: {THEME["text_primary"]};
                border: 1px solid {THEME["border_window"]};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #313859;
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
        self.chk_trigger = QCheckBox("Show floating Voxel logo when selecting text", self)
        layout_prefs.addWidget(self.chk_trigger)

        # macOS Accessibility Permission Box
        if IS_MAC:
            perm_box = QGroupBox("macOS System Permissions", self)
            perm_layout = QHBoxLayout(perm_box)
            trusted = is_accessibility_trusted(prompt=False)
            status_text = "🟢 Granted" if trusted else "⚠️ Accessibility Permission Needed"
            self.lbl_perm = QLabel(f"Accessibility: <b>{status_text}</b>", perm_box)
            perm_layout.addWidget(self.lbl_perm)

            btn_open_perm = QPushButton("Open System Settings", perm_box)
            btn_open_perm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open_perm.clicked.connect(open_accessibility_settings)
            perm_layout.addWidget(btn_open_perm)
            layout_prefs.addWidget(perm_box)

        layout_prefs.addStretch()
        self.tabs.addTab(tab_prefs, "⚙️ Preferences")

        # Tab 2: Downloads & Data (OS-Adaptive & Platform-Filtered)
        tab_downloads = QWidget()
        layout_down = QVBoxLayout(tab_downloads)
        layout_down.setContentsMargins(14, 14, 14, 14)
        layout_down.setSpacing(12)

        down_header = QLabel("📦 Official Download & Installation Packages", tab_downloads)
        down_header.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 700;")
        layout_down.addWidget(down_header)

        # Platform Filtered Options:
        # On macOS, show .pkg and .dmg; hide Windows .exe completely.
        # On Windows, show .exe; hide macOS .pkg and .dmg completely.
        if IS_MAC:
            mac_box = QGroupBox("macOS Installation Packages (Universal)", tab_downloads)
            mac_layout = QVBoxLayout(mac_box)
            mac_layout.setSpacing(10)

            # Option A: System-wide .pkg installer (Applications folder, for everyone)
            pkg_row = QHBoxLayout()
            pkg_info = QVBoxLayout()
            pkg_title = QLabel("<b>Voxel.pkg (System-wide Installer)</b>", mac_box)
            pkg_desc = QLabel("Installs into <b>/Applications</b> for all users. Includes embedded UX design assets.", mac_box)
            pkg_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
            pkg_info.addWidget(pkg_title)
            pkg_info.addWidget(pkg_desc)
            pkg_row.addLayout(pkg_info)

            btn_pkg = QPushButton("📥 Download .pkg", mac_box)
            btn_pkg.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_pkg.setStyleSheet("background-color: #0084FF; color: #FFFFFF; padding: 6px 14px;")
            pkg_url = f"{GITHUB_URL}/releases/latest/download/Voxel.pkg"
            btn_pkg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(pkg_url)))
            pkg_row.addWidget(btn_pkg)
            mac_layout.addLayout(pkg_row)

            # Option B: .dmg disk image
            dmg_row = QHBoxLayout()
            dmg_info = QVBoxLayout()
            dmg_title = QLabel("<b>Voxel.dmg (Disk Image)</b>", mac_box)
            dmg_desc = QLabel("Standard drag-and-drop installer disk image.", mac_box)
            dmg_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
            dmg_info.addWidget(dmg_title)
            dmg_info.addWidget(dmg_desc)
            dmg_row.addLayout(dmg_info)

            btn_dmg = QPushButton("📥 Download .dmg", mac_box)
            btn_dmg.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_dmg.setStyleSheet("background-color: #242942; color: #FFFFFF; padding: 6px 14px;")
            dmg_url = f"{GITHUB_URL}/releases/latest/download/Voxel.dmg"
            btn_dmg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(dmg_url)))
            dmg_row.addWidget(btn_dmg)
            mac_layout.addLayout(dmg_row)

            layout_down.addWidget(mac_box)

            # Note explaining that Windows download option is filtered/invisible
            lbl_filter = QLabel("ℹ️ <i>Windows options are hidden because you are on macOS.</i>", tab_downloads)
            lbl_filter.setStyleSheet("color: #64748B; font-size: 11px;")
            layout_down.addWidget(lbl_filter)
        else:
            win_box = QGroupBox("Windows Installation Packages", tab_downloads)
            win_layout = QVBoxLayout(win_box)
            win_layout.setSpacing(10)

            win_row = QHBoxLayout()
            win_info = QVBoxLayout()
            win_title = QLabel("<b>Voxel.exe (Standalone Executable)</b>", win_box)
            win_desc = QLabel("Zero-dependency executable for Windows 10/11.", win_box)
            win_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
            win_info.addWidget(win_title)
            win_info.addWidget(win_desc)
            win_row.addLayout(win_info)

            btn_win = QPushButton("📥 Download .exe", win_box)
            btn_win.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_win.setStyleSheet("background-color: #0084FF; color: #FFFFFF; padding: 6px 14px;")
            win_url = f"{GITHUB_URL}/releases/latest/download/Voxel.exe"
            btn_win.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(win_url)))
            win_row.addWidget(btn_win)
            win_layout.addLayout(win_row)

            layout_down.addWidget(win_box)

            lbl_filter = QLabel("ℹ️ <i>macOS packages are hidden because you are on Windows.</i>", tab_downloads)
            lbl_filter.setStyleSheet("color: #64748B; font-size: 11px;")
            layout_down.addWidget(lbl_filter)

        layout_down.addStretch()
        self.tabs.addTab(tab_downloads, "📥 Downloads")

        # Tab 3: About & Version
        tab_about = QWidget()
        layout_about = QVBoxLayout(tab_about)
        layout_about.setContentsMargins(16, 16, 16, 16)
        layout_about.setSpacing(10)

        # Header with Logo & Brand
        header_row = QHBoxLayout()
        header_logo = VoxelLogoWidget(size=44, animated=True, parent=tab_about)
        header_row.addWidget(header_logo)

        header_text = QVBoxLayout()
        title_lbl = QLabel(f"{APP_NAME}", self)
        title_lbl.setStyleSheet(f"color: #FFFFFF; font-size: 20px; font-weight: 800;")
        header_text.addWidget(title_lbl)

        sub_lbl = QLabel(f"{APP_TAGLINE}", self)
        sub_lbl.setStyleSheet("color: #0084FF; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        header_text.addWidget(sub_lbl)
        header_row.addLayout(header_text)
        header_row.addStretch()
        layout_about.addLayout(header_row)

        # Version Pill Box
        ver_box = QGroupBox("Version Information", self)
        ver_layout = QVBoxLayout(ver_box)
        ver_layout.setSpacing(6)

        lbl_ver = QLabel(f"Current Version: <b><font color='#0084FF'>{VERSION}</font></b>", self)
        ver_layout.addWidget(lbl_ver)

        lbl_ver_rule = QLabel(
            "Structure: <code>v&lt;Major&gt;.&lt;Minor&gt;.&lt;Patch:02d&gt;</code><br>"
            "Base-10 rollover scheme: increments patch, minor on 10th, major on 100th.", self
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

        btn_gh = QPushButton(f"🌐 GitHub: {GITHUB_URL}", self)
        btn_gh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_gh.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 132, 255, 0.15);
                border: 1px solid rgba(0, 132, 255, 0.5);
                color: #38BDF8;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 132, 255, 0.3);
                color: #FFFFFF;
            }}
        """)
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        gh_layout.addWidget(btn_gh)

        layout_about.addWidget(gh_box)
        layout_about.addStretch()

        self.tabs.addTab(tab_about, "ℹ️ About Voxel")
        main_layout.addWidget(self.tabs)

        # Bottom buttons: Save & Cancel
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_save = QPushButton("Save & Apply", self)
        btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: #0084FF;
                color: #FFFFFF;
                border: none;
                padding: 7px 18px;
            }}
            QPushButton:hover {{
                background-color: #0072FF;
            }}
        """)
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
