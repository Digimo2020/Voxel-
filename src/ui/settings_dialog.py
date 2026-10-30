"""
Settings, Preferences, Downloads & About Dialog for Voxel.
Allows configuring:
- Default voice (including new expressive Copilot neural voices Ava, Andrew, Emma, Brian)
- Emotion tone & expressiveness modes (Empathetic, Warm, Cheerful, Professional)
- Playback speeds (0.5x to 2.5x)
- Sub-second instant playback pre-buffering
- Launch at system startup (Windows Registry & macOS LaunchAgents)
- Document & Presentation auto-reader options
- Themes, docking positions, and auto-close options
Features high-contrast dark obsidian glass aesthetics and OS-adaptive official download options.
"""
import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QComboBox, QCheckBox, QDoubleSpinBox, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QCursor, QDesktopServices

from src.config import (
    THEME, VOICES, EMOTION_MODES, DEFAULT_EMOTION_MODE, SPEED_STEPS,
    VERSION, GITHUB_URL, APP_NAME, APP_TAGLINE, FONT_FAMILY, IS_MAC,
    COMPANY_NAME, COMPANY_URL
)
from src.utils.settings import settings_db
from src.utils.startup import is_startup_enabled, set_startup_enabled
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from src.ui.voxel_logo_widget import VoxelLogoWidget


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} — Settings & Preferences ({VERSION})")
        self.setFixedSize(600, 680)
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
                padding: 9px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 12px;
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
                padding: 14px 12px 10px 12px;
                font-weight: 600;
                color: #F8FAFF;
            }}
            QGroupBox::title {{
                color: #38BDF8;
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                font-size: 12px;
                font-weight: 700;
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
                border-color: rgba(0, 132, 255, 0.6);
            }}
        """)

        self._init_ui()
        self.load_values()

    def _make_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text, self)
        lbl.setStyleSheet("color: #E2E8F0; font-size: 13px; font-weight: 600;")
        return lbl

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        self.tabs = QTabWidget(self)

        # ─── Tab 1: Preferences & Emotion ───────────────────────────
        tab_prefs = QWidget()
        layout_prefs = QVBoxLayout(tab_prefs)
        layout_prefs.setContentsMargins(14, 14, 14, 14)
        layout_prefs.setSpacing(10)

        # Form Group
        box_voice = QGroupBox("🎙 Voice & Emotional Prosody", tab_prefs)
        form_voice = QFormLayout(box_voice)
        form_voice.setSpacing(10)
        form_voice.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Default Voice
        self.combo_voice = QComboBox(box_voice)
        for v in VOICES:
            self.combo_voice.addItem(v["label"], v["id"])
        form_voice.addRow(self._make_field_label("Default Voice:"), self.combo_voice)

        # Emotion & Expressiveness Mode
        self.combo_emotion = QComboBox(box_voice)
        for m in EMOTION_MODES:
            self.combo_emotion.addItem(m["label"], m["id"])
        form_voice.addRow(self._make_field_label("Emotion & Tone:"), self.combo_emotion)

        # Default Speed
        self.combo_speed = QComboBox(box_voice)
        for s in SPEED_STEPS:
            self.combo_speed.addItem(f"{s}x", s)
        form_voice.addRow(self._make_field_label("Default Speed:"), self.combo_speed)

        layout_prefs.addWidget(box_voice)

        # Behavior & Startup Group
        box_system = QGroupBox("⚙️ System, Startup & Playback", tab_prefs)
        layout_system = QVBoxLayout(box_system)
        layout_system.setSpacing(8)

        # Launch at Startup
        self.chk_startup = QCheckBox("🚀 Launch Voxel automatically on system startup", box_system)
        layout_system.addWidget(self.chk_startup)

        # Pre-buffer on hover (sub-second instant playback)
        self.chk_prebuffer = QCheckBox("⚡ Instant Playback: Pre-generate first sentence on hover (0ms delay)", box_system)
        layout_system.addWidget(self.chk_prebuffer)

        # Selection trigger checkbox
        self.chk_trigger = QCheckBox("✨ Show floating Voxel dual-capsule badge when selecting text", box_system)
        layout_system.addWidget(self.chk_trigger)

        # Auto-Close on Finished Speaking
        self.chk_autoclose = QCheckBox("⏳ Automatically close player when speech finishes", box_system)
        layout_system.addWidget(self.chk_autoclose)

        delay_row = QHBoxLayout()
        lbl_delay = QLabel("Fade-out duration:", box_system)
        lbl_delay.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        delay_row.addWidget(lbl_delay)

        self.spin_autoclose_delay = QDoubleSpinBox(box_system)
        self.spin_autoclose_delay.setRange(0.5, 5.0)
        self.spin_autoclose_delay.setSingleStep(0.5)
        self.spin_autoclose_delay.setValue(1.0)
        self.spin_autoclose_delay.setSuffix(" sec")
        self.spin_autoclose_delay.setFixedWidth(110)
        delay_row.addWidget(self.spin_autoclose_delay)
        delay_row.addStretch()
        layout_system.addLayout(delay_row)

        layout_prefs.addWidget(box_system)

        # macOS Accessibility Permission Box (Mac only)
        if IS_MAC:
            perm_box = QGroupBox("macOS System Permissions", tab_prefs)
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

        # ─── Tab 2: Document & Presentation Reader ──────────────────
        tab_doc = QWidget()
        layout_doc = QVBoxLayout(tab_doc)
        layout_doc.setContentsMargins(14, 14, 14, 14)
        layout_doc.setSpacing(12)

        doc_header = QLabel("📑 Smart Document & Presentation Narration", tab_doc)
        doc_header.setStyleSheet("color: #38BDF8; font-size: 14px; font-weight: 700;")
        layout_doc.addWidget(doc_header)

        lbl_doc_info = QLabel(
            "Voxel can automatically read entire Google Docs, Microsoft Word documents, "
            "PowerPoint and Google Slides presentations, and PDF files without requiring you "
            "to manually select hundreds of lines.",
            tab_doc
        )
        lbl_doc_info.setStyleSheet("color: #E2E8F0; font-size: 12px; line-height: 1.45;")
        lbl_doc_info.setWordWrap(True)
        layout_doc.addWidget(lbl_doc_info)

        methods_box = QGroupBox("3 Ways to Read Entire Documents", tab_doc)
        methods_layout = QVBoxLayout(methods_box)
        methods_layout.setSpacing(8)

        m1 = QLabel("<b>1. Floating Trigger Capsule:</b> Click the right <b>📑 Document icon</b> on the floating badge that appears when you select text.", methods_box)
        m1.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        m1.setWordWrap(True)
        methods_layout.addWidget(m1)

        hotkey_label = "Cmd+Alt+D" if IS_MAC else "Ctrl+Alt+D"
        m2 = QLabel(f"<b>2. Global Hotkey:</b> Press <b><code>{hotkey_label}</code></b> anytime while viewing any document or presentation tab.", methods_box)
        m2.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        m2.setWordWrap(True)
        methods_layout.addWidget(m2)

        m3 = QLabel("<b>3. Mini Player & Tray Menu:</b> Click the <b>📑 Document button</b> in the player capsule or choose <i>Open File...</i> to pick any PDF/Docx.", methods_box)
        m3.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        m3.setWordWrap(True)
        methods_layout.addWidget(m3)

        layout_doc.addWidget(methods_box)

        # Instant Pipelining Note
        pipe_box = QGroupBox("⚡ Zero-Delay Continuous Pipelining", tab_doc)
        pipe_layout = QVBoxLayout(pipe_box)
        lbl_pipe = QLabel(
            "Even for 50-page documents or long slide decks, Voxel breaks the content into "
            "smart sentence chunks and starts speaking the first sentence in <b>under 300 milliseconds</b>! "
            "Subsequent sentences synthesize continuously in the background for gapless narration.",
            pipe_box
        )
        lbl_pipe.setStyleSheet("color: #94A3B8; font-size: 11px; line-height: 1.4;")
        lbl_pipe.setWordWrap(True)
        pipe_layout.addWidget(lbl_pipe)
        layout_doc.addWidget(pipe_box)

        layout_doc.addStretch()
        self.tabs.addTab(tab_doc, "📑 Document Reader")

        # ─── Tab 3: Downloads & Local Folder ────────────────────────
        tab_downloads = QWidget()
        layout_down = QVBoxLayout(tab_downloads)
        layout_down.setContentsMargins(14, 14, 14, 14)
        layout_down.setSpacing(12)

        down_header = QLabel(f"📦 Official Download & Local Packages ({VERSION})", tab_downloads)
        down_header.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 700;")
        layout_down.addWidget(down_header)

        if IS_MAC:
            pkg_box = QGroupBox(f"🍎 macOS System-Wide Installer ({VERSION})", tab_downloads)
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
            pkg_row.addWidget(QLabel(f"Target: <b>/Applications ({VERSION})</b>", tab_downloads))
            pkg_row.addStretch()

            btn_pkg = QPushButton(f"📥 Download Voxel-{VERSION}.pkg", tab_downloads)
            btn_pkg.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_pkg.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 6px 14px;")
            pkg_url = f"{GITHUB_URL}/releases/download/{VERSION}/Voxel-{VERSION}.pkg"
            btn_pkg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(pkg_url)))
            pkg_row.addWidget(btn_pkg)
            pkg_layout.addLayout(pkg_row)
            layout_down.addWidget(pkg_box)

        else:
            win_box = QGroupBox(f"⊞ Windows Standalone Executable ({VERSION})", tab_downloads)
            win_layout = QVBoxLayout(win_box)
            win_layout.setSpacing(8)

            lbl_win_desc = QLabel(
                "Single zero-dependency portable executable with embedded icon and single-instance lock. "
                "No Python installation, administrator rights, or setup required.",
                tab_downloads
            )
            lbl_win_desc.setStyleSheet("color: #94A3B8; font-size: 12px;")
            lbl_win_desc.setWordWrap(True)
            win_layout.addWidget(lbl_win_desc)

            win_row = QHBoxLayout()
            win_row.addWidget(QLabel(f"Target: <b>Windows 10 / 11 ({VERSION})</b>", tab_downloads))
            win_row.addStretch()

            btn_win = QPushButton(f"📥 Download Voxel-{VERSION}.exe", tab_downloads)
            btn_win.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_win.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 6px 14px;")
            win_url = f"{GITHUB_URL}/releases/download/{VERSION}/Voxel-{VERSION}.exe"
            btn_win.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(win_url)))
            win_row.addWidget(btn_win)
            win_layout.addLayout(win_row)

            # Local folder shortcut button
            local_row = QHBoxLayout()
            btn_open_local = QPushButton("📁 Open Local Computer 'dist' Folder", tab_downloads)
            btn_open_local.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open_local.setStyleSheet("background-color: #1E293B; color: #38BDF8; font-weight: 600; border: 1px solid #334155;")
            dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dist"))
            btn_open_local.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(dist_path)))
            local_row.addWidget(btn_open_local)
            local_row.addStretch()
            win_layout.addLayout(local_row)

            layout_down.addWidget(win_box)

        # Historical Releases Archive
        archive_box = QGroupBox("📦 Historical Versions Archive", tab_downloads)
        archive_layout = QVBoxLayout(archive_box)
        archive_layout.setSpacing(6)

        ver_list = QLabel(
            f"• <b>{VERSION} (Current)</b> — Instant document reader, emotional Copilot voices, startup toggle<br>"
            "• <b>v1.1.03</b> — Vibrant full-frame startup bar logo, maximized white mic icon<br>"
            "• <b>v1.1.02</b> — Standalone system tray mic icon maximization<br>"
            "• <b>v1.1.01</b> — 3-tier PNG icon branding for tray, app, and selection bubble<br>"
            "• <b>v1.1.00</b> — Vector SVG final logo integration<br>"
            "• <b>v1.0.09</b> — Smart App Control native MCI audio bypass<br>"
            "• <b>v1.0.06</b> — Light frosted glass tray icon & single-instance lock",
            tab_downloads
        )
        ver_list.setStyleSheet("color: #CBD5E1; font-size: 11px; line-height: 1.4;")
        archive_layout.addWidget(ver_list)

        archive_row = QHBoxLayout()
        archive_row.addStretch()
        btn_archive = QPushButton("🌐 View All Versions on GitHub Releases", tab_downloads)
        btn_archive.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_archive.setStyleSheet("background-color: #334155; color: #FFFFFF; font-size: 11px; padding: 5px 12px; border-radius: 4px;")
        btn_archive.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"{GITHUB_URL}/releases")))
        archive_row.addWidget(btn_archive)
        archive_layout.addLayout(archive_row)

        layout_down.addWidget(archive_box)
        layout_down.addStretch()
        self.tabs.addTab(tab_downloads, "📥 Downloads & Versions")

        # ─── Tab 4: About & Open Source ─────────────────────────────
        tab_about = QWidget()
        layout_about = QVBoxLayout(tab_about)
        layout_about.setContentsMargins(16, 16, 16, 16)
        layout_about.setSpacing(10)

        header_row = QHBoxLayout()
        header_logo = VoxelLogoWidget(size=46, animated=True, parent=tab_about)
        header_row.addWidget(header_logo)

        header_text = QVBoxLayout()
        title_lbl = QLabel(f"{APP_NAME}", self)
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 800;")
        header_text.addWidget(title_lbl)

        sub_lbl = QLabel(f"{APP_TAGLINE}  •  A {COMPANY_NAME} Product", self)
        sub_lbl.setStyleSheet("color: #0084FF; font-size: 11px; font-weight: 700; letter-spacing: 0.8px;")
        header_text.addWidget(sub_lbl)
        header_row.addLayout(header_text)
        header_row.addStretch()
        layout_about.addLayout(header_row)

        # Version Pill Box
        ver_box = QGroupBox("Version Information", self)
        ver_layout = QVBoxLayout(ver_box)
        ver_layout.setSpacing(4)
        lbl_ver = QLabel(f"Current Version: <b><font color='#0084FF'>{VERSION}</font></b>  <font color='#64748B'>(Base-10 Rollover)</font>", self)
        ver_layout.addWidget(lbl_ver)
        lbl_ver_rule = QLabel(
            "Structure: <code>v&lt;Major&gt;.&lt;Minor&gt;.&lt;Patch:02d&gt;</code> • "
            "Local machine operation only • No telemetry", self
        )
        lbl_ver_rule.setStyleSheet("color: #94A3B8; font-size: 11px;")
        ver_layout.addWidget(lbl_ver_rule)
        layout_about.addWidget(ver_box)

        # Digimo & Open Source Box
        digimo_box = QGroupBox("🏢 Digimo Product & Open Source Freedom", self)
        digimo_layout = QVBoxLayout(digimo_box)
        digimo_layout.setSpacing(8)

        lbl_digimo_desc = QLabel(
            f"Voxel is an open-source product from <b>{COMPANY_NAME}</b>.<br>"
            "This software is <b>completely free and open source</b> with no copyright restrictions. "
            "Anyone is welcome to experiment, build upon it, make it more modern, and contribute.",
            self
        )
        lbl_digimo_desc.setStyleSheet("color: #E2E8F0; font-size: 12px; line-height: 1.45;")
        lbl_digimo_desc.setWordWrap(True)
        digimo_layout.addWidget(lbl_digimo_desc)

        links_row = QHBoxLayout()
        btn_website = QPushButton(f"🌐 Visit Digimo ({COMPANY_URL})", self)
        btn_website.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_website.setStyleSheet("""
            QPushButton {
                background-color: #0084FF;
                color: #FFFFFF;
                font-weight: 700;
                padding: 6px 14px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0072FF;
            }
        """)
        btn_website.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(COMPANY_URL)))
        links_row.addWidget(btn_website)

        btn_gh = QPushButton("🐙 GitHub Repository", self)
        btn_gh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_gh.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 132, 255, 0.15);
                border: 1px solid rgba(0, 132, 255, 0.5);
                color: #38BDF8;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(0, 132, 255, 0.3);
                color: #FFFFFF;
            }
        """)
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        links_row.addWidget(btn_gh)
        digimo_layout.addLayout(links_row)
        layout_about.addWidget(digimo_box)

        # Disclaimer & Setup Guide Box
        disclaimer_box = QGroupBox("⚖️ Disclaimer & Setup Guide", self)
        disclaimer_layout = QVBoxLayout(disclaimer_box)
        disclaimer_layout.setSpacing(6)

        lbl_disclaimer = QLabel(
            "<b>Disclaimer:</b> Provided 'as is' for personal and experimental use. "
            "Digimo and creators assume no responsibility or liability for any use or outcome. "
            "Please read the included setup guides and documentation before configuring on your machine.",
            self
        )
        lbl_disclaimer.setStyleSheet("color: #94A3B8; font-size: 11px; line-height: 1.4;")
        lbl_disclaimer.setWordWrap(True)
        disclaimer_layout.addWidget(lbl_disclaimer)

        layout_about.addWidget(disclaimer_box)
        layout_about.addStretch()

        self.tabs.addTab(tab_about, "ℹ️ About & Legal")
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
        voice_id = settings_db.get("default_voice", "en-US-AvaNeural")
        idx = self.combo_voice.findData(voice_id)
        if idx >= 0:
            self.combo_voice.setCurrentIndex(idx)

        emotion_mode = settings_db.get("emotion_mode", DEFAULT_EMOTION_MODE)
        idx_em = self.combo_emotion.findData(emotion_mode)
        if idx_em >= 0:
            self.combo_emotion.setCurrentIndex(idx_em)

        speed_val = settings_db.get("default_speed", 1.0)
        idx_sp = self.combo_speed.findData(speed_val)
        if idx_sp >= 0:
            self.combo_speed.setCurrentIndex(idx_sp)

        # Startup on login
        self.chk_startup.setChecked(is_startup_enabled())

        # Pre-buffer on hover
        prebuffer = settings_db.get("prebuffer_enabled", True)
        self.chk_prebuffer.setChecked(prebuffer)

        # Selection trigger
        enabled = settings_db.get("selection_popup_enabled", True)
        self.chk_trigger.setChecked(enabled)

        # Auto-close
        autoclose = settings_db.get("auto_close_finished", True)
        self.chk_autoclose.setChecked(autoclose)

        delay_val = settings_db.get("auto_close_delay", 1.0)
        self.spin_autoclose_delay.setValue(delay_val)

    def save_and_apply(self):
        """Saves values, applies startup state, and emits signal."""
        settings_db.set("default_voice", self.combo_voice.currentData())
        settings_db.set("emotion_mode", self.combo_emotion.currentData())
        settings_db.set("default_speed", self.combo_speed.currentData())
        settings_db.set("prebuffer_enabled", self.chk_prebuffer.isChecked())
        settings_db.set("selection_popup_enabled", self.chk_trigger.isChecked())
        settings_db.set("auto_close_finished", self.chk_autoclose.isChecked())
        settings_db.set("auto_close_delay", self.spin_autoclose_delay.value())

        # Apply startup state
        set_startup_enabled(self.chk_startup.isChecked())

        self.settings_applied.emit()
        self.close()
