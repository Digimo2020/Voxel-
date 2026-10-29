"""
Settings, Downloads & About Dialog for Voxel.
Allows configuring default voices, speeds, trigger timeouts, dock modes, themes, and auto-close options.
Features OS-adaptive download options:
- On macOS: Displays macOS .pkg and .dmg download options; Windows .exe is invisible.
- On Windows: Displays Windows .exe download option; macOS .pkg and .dmg are invisible.
All label and text colors are explicitly styled with high-contrast text for dark backgrounds on Windows and macOS.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QComboBox, QCheckBox, QDoubleSpinBox, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QCursor, QDesktopServices

from src.config import THEME, VOICES, SPEED_STEPS, VERSION, GITHUB_URL, APP_NAME, APP_TAGLINE, FONT_FAMILY, IS_MAC
from src.utils.settings import settings_db
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from src.ui.voxel_logo_widget import VoxelLogoWidget


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} — Settings & Preferences")
        self.setFixedSize(540, 530)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME["bg_window"]};
                color: #F8FAFF;
                font-family: {FONT_FAMILY};
            }}
            QLabel {{
                color: #F1F5F9;
                font-size: 13px;
            }}
            QTabWidget::pane {{
                border: 1px solid {THEME["border_window"]};
                background-color: #171B2D;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: #1F243B;
                color: #94A3B8;
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
                color: #F8FAFF;
            }}
            QGroupBox::title {{
                color: #38BDF8;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
            QComboBox, QDoubleSpinBox {{
                background-color: #242942;
                color: #F8FAFF;
                border: 1px solid {THEME["border_window"]};
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 13px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #1E2337;
                color: #FFFFFF;
                selection-background-color: #0084FF;
                selection-color: #FFFFFF;
                border: 1px solid #334155;
            }}
            QCheckBox {{
                color: #F1F5F9;
                font-size: 13px;
                spacing: 8px;
            }}
            QPushButton {{
                background-color: #242942;
                color: #FFFFFF;
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

    def _make_field_label(self, text: str) -> QLabel:
        """Helper to create high-contrast, crystal clear field labels for Windows & Mac."""
        lbl = QLabel(text, self)
        lbl.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: 600;")
        return lbl

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget(self)

        # ─── Tab 1: General Preferences ─────────────────────────────
        tab_prefs = QWidget()
        layout_prefs = QVBoxLayout(tab_prefs)
        layout_prefs.setContentsMargins(14, 14, 14, 14)
        layout_prefs.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # 1. Default Voice
        self.combo_voice = QComboBox(self)
        for v in VOICES:
            self.combo_voice.addItem(v["label"], v["id"])
        form.addRow(self._make_field_label("Default Voice:"), self.combo_voice)

        # 2. Default Speed
        self.combo_speed = QComboBox(self)
        for s in SPEED_STEPS:
            self.combo_speed.addItem(f"{s}x", s)
        form.addRow(self._make_field_label("Default Speed:"), self.combo_speed)

        # 3. Player Theme (Frosted Glass vs Dark Glass)
        self.combo_theme = QComboBox(self)
        self.combo_theme.addItem("Frosted Glass (Light Acrylic)", "light_glass")
        self.combo_theme.addItem("Dark Glass (Obsidian Glass)", "light_glass")
        form.addRow(self._make_field_label("Player Theme:"), self.combo_theme)

        # 4. Docking Position
        self.combo_dock = QComboBox(self)
        self.combo_dock.addItem("Bottom-Right Corner (Animated)", "bottom_right")
        self.combo_dock.addItem("Near Selection Cursor", "near_cursor")
        form.addRow(self._make_field_label("Player Position:"), self.combo_dock)

        # 5. Bubble Timeout
        self.spin_timeout = QDoubleSpinBox(self)
        self.spin_timeout.setRange(1.5, 12.0)
        self.spin_timeout.setSingleStep(0.5)
        self.spin_timeout.setSuffix(" sec")
        form.addRow(self._make_field_label("Trigger Timeout:"), self.spin_timeout)

        layout_prefs.addLayout(form)

        # Selection trigger checkbox
        self.chk_trigger = QCheckBox("Show floating Voxel logo badge when selecting text", self)
        layout_prefs.addWidget(self.chk_trigger)

        # Auto-Close on Finished Speaking Group
        autoclose_box = QGroupBox("Playback Completion Behavior", self)
        autoclose_layout = QVBoxLayout(autoclose_box)
        autoclose_layout.setSpacing(6)

        self.chk_autoclose = QCheckBox("Automatically close player when speech finishes", autoclose_box)
        autoclose_layout.addWidget(self.chk_autoclose)

        delay_row = QHBoxLayout()
        lbl_delay = QLabel("Fade-out duration:", autoclose_box)
        lbl_delay.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        delay_row.addWidget(lbl_delay)

        self.spin_autoclose_delay = QDoubleSpinBox(autoclose_box)
        self.spin_autoclose_delay.setRange(0.5, 5.0)
        self.spin_autoclose_delay.setSingleStep(0.5)
        self.spin_autoclose_delay.setValue(1.0)
        self.spin_autoclose_delay.setSuffix(" sec")
        self.spin_autoclose_delay.setFixedWidth(110)
        delay_row.addWidget(self.spin_autoclose_delay)
        delay_row.addStretch()
        autoclose_layout.addLayout(delay_row)

        layout_prefs.addWidget(autoclose_box)

        # macOS Accessibility Permission Box (Mac only)
        if IS_MAC:
            perm_box = QGroupBox("macOS System Permissions", self)
            perm_layout = QHBoxLayout(perm_box)
            trusted = is_accessibility_trusted(prompt=False)
            status_text = "🟢 Granted" if trusted else "⚠️ Accessibility Needed"
            self.lbl_perm = QLabel(f"Accessibility: <b>{status_text}</b>", perm_box)
            perm_layout.addWidget(self.lbl_perm)

            btn_open_perm = QPushButton("Open System Settings", perm_box)
            btn_open_perm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open_perm.clicked.connect(open_accessibility_settings)
            perm_layout.addWidget(btn_open_perm)
            layout_prefs.addWidget(perm_box)

        layout_prefs.addStretch()
        self.tabs.addTab(tab_prefs, "⚙️ Preferences")

        # ─── Tab 2: Downloads & Data (OS-Adaptive) ─────────────────────
        tab_downloads = QWidget()
        layout_down = QVBoxLayout(tab_downloads)
        layout_down.setContentsMargins(14, 14, 14, 14)
        layout_down.setSpacing(12)

        down_header = QLabel("📦 Official Download & Installation Packages", tab_downloads)
        down_header.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 700;")
        layout_down.addWidget(down_header)

        if IS_MAC:
            # macOS .pkg Option
            pkg_box = QGroupBox("🍎 macOS System-Wide Installer (.pkg)", tab_downloads)
            pkg_layout = QVBoxLayout(pkg_box)
            pkg_layout.setSpacing(8)

            lbl_pkg_desc = QLabel(
                "Standard guided installer wizard with embedded UX design previews. "
                "Installs Voxel into <code>/Applications</code> for all user accounts.",
                tab_downloads
            )
            lbl_pkg_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
            lbl_pkg_desc.setWordWrap(True)
            pkg_layout.addWidget(lbl_pkg_desc)

            pkg_row = QHBoxLayout()
            pkg_row.addWidget(QLabel("Target: <b>/Applications (System)</b>", tab_downloads))
            pkg_row.addStretch()

            btn_pkg = QPushButton("📥 Download Voxel.pkg", tab_downloads)
            btn_pkg.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_pkg.setStyleSheet("background-color: #0084FF; color: #FFFFFF; padding: 6px 14px;")
            pkg_url = f"{GITHUB_URL}/releases/latest/download/Voxel.pkg"
            btn_pkg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(pkg_url)))
            pkg_row.addWidget(btn_pkg)
            pkg_layout.addLayout(pkg_row)
            layout_down.addWidget(pkg_box)

            # macOS .dmg Option
            dmg_box = QGroupBox("💿 macOS Drag-and-Drop Disk Image (.dmg)", tab_downloads)
            dmg_layout = QVBoxLayout(dmg_box)
            dmg_layout.setSpacing(8)

            lbl_dmg_desc = QLabel(
                "Traditional Apple disk image format. Mount the DMG and drag Voxel.app directly "
                "into your Applications folder.",
                tab_downloads
            )
            lbl_dmg_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
            lbl_dmg_desc.setWordWrap(True)
            dmg_layout.addWidget(lbl_dmg_desc)

            dmg_row = QHBoxLayout()
            dmg_row.addWidget(QLabel("Target: <b>Portable / User Folder</b>", tab_downloads))
            dmg_row.addStretch()

            btn_dmg = QPushButton("📥 Download Voxel.dmg", tab_downloads)
            btn_dmg.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            dmg_url = f"{GITHUB_URL}/releases/latest/download/Voxel.dmg"
            btn_dmg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(dmg_url)))
            dmg_row.addWidget(btn_dmg)
            dmg_layout.addLayout(dmg_row)
            layout_down.addWidget(dmg_box)

        else:
            # Windows .exe Option
            win_box = QGroupBox("⊞ Windows Standalone Executable (.exe)", tab_downloads)
            win_layout = QVBoxLayout(win_box)
            win_layout.setSpacing(8)

            lbl_win_desc = QLabel(
                "Single zero-dependency portable executable. No Python installation, "
                "administrator rights, or complex setup required.",
                tab_downloads
            )
            lbl_win_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
            lbl_win_desc.setWordWrap(True)
            win_layout.addWidget(lbl_win_desc)

            win_row = QHBoxLayout()
            win_row.addWidget(QLabel("Target: <b>Windows 10 / 11</b>", tab_downloads))
            win_row.addStretch()

            btn_win = QPushButton("📥 Download Voxel.exe", tab_downloads)
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

        # ─── Tab 3: About & Version ──────────────────────────────────
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
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 800;")
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
        btn_gh.setStyleSheet("""
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
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0084FF;
                color: #FFFFFF;
                border: none;
                padding: 7px 18px;
            }
            QPushButton:hover {
                background-color: #0072FF;
            }
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

        theme_mode = settings_db.get("theme_mode", "light_glass")
        idx_th = self.combo_theme.findData(theme_mode)
        if idx_th >= 0:
            self.combo_theme.setCurrentIndex(idx_th)

        dock_mode = settings_db.get("dock_position", "bottom_right")
        idx_dk = self.combo_dock.findData(dock_mode)
        if idx_dk >= 0:
            self.combo_dock.setCurrentIndex(idx_dk)

        timeout = settings_db.get("bubble_timeout", 4.0)
        self.spin_timeout.setValue(timeout)

        enabled = settings_db.get("selection_popup_enabled", True)
        self.chk_trigger.setChecked(enabled)

        autoclose = settings_db.get("auto_close_finished", True)
        self.chk_autoclose.setChecked(autoclose)

        delay_val = settings_db.get("auto_close_delay", 1.0)
        self.spin_autoclose_delay.setValue(delay_val)

    def save_and_apply(self):
        """Saves values and emits signal."""
        settings_db.set("default_voice", self.combo_voice.currentData())
        settings_db.set("default_speed", self.combo_speed.currentData())
        settings_db.set("theme_mode", self.combo_theme.currentData())
        settings_db.set("dock_position", self.combo_dock.currentData())
        settings_db.set("bubble_timeout", self.spin_timeout.value())
        settings_db.set("selection_popup_enabled", self.chk_trigger.isChecked())
        settings_db.set("auto_close_finished", self.chk_autoclose.isChecked())
        settings_db.set("auto_close_delay", self.spin_autoclose_delay.value())

        self.settings_applied.emit()
        self.close()
