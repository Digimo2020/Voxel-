"""
Settings, Preferences, Downloads & About Dialog for Voxel.
Allows configuring:
- Dual Theme Views: Light Frosted Glass & Dark Obsidian Glass
- Voice profiles & 4 Emotional Prosody styles
- Live Performance & Voice Test button
- Launch at system startup (Windows Registry & macOS LaunchAgents)
- Document & Presentation auto-reader options
- Creator & Architecture credits (Fahim - LinkedIn: https://www.linkedin.com/in/fahimdigital/)
- Digimo open source freedom and OS-adaptive download options
"""
import os
import sys
from typing import Optional
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
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from src.utils.startup import is_startup_enabled, set_startup_enabled
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from src.ui.voxel_logo_widget import VoxelLogoWidget

LINKEDIN_URL = "https://www.linkedin.com/in/fahimdigital/"


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()

    def __init__(self, tts_engine: Optional[TTSEngine] = None, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.current_theme = settings_db.get("settings_theme", "dark")
        self.setWindowTitle(f"{APP_NAME} — Settings & Preferences ({VERSION})")
        self.setFixedSize(620, 710)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self._labels_to_theme = []
        self._init_ui()
        self.apply_theme(self.current_theme)
        self.load_values()

    def _get_dark_stylesheet(self) -> str:
        return f"""
            QDialog {{
                background-color: #131625;
                color: #F8FAFF;
                font-family: {FONT_FAMILY};
            }}
            QLabel {{
                color: #F1F5F9;
                font-size: 13px;
            }}
            QTabWidget::pane {{
                border: 1px solid #252B44;
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
                border-bottom: 2px solid #0084FF;
            }}
            QGroupBox {{
                border: 1px solid #252B44;
                border-radius: 8px;
                margin-top: 10px;
                padding: 14px 12px 10px 12px;
                font-weight: 600;
                color: #F8FAFF;
                background-color: transparent;
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
                border: 1px solid #334155;
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
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #313859;
                border-color: rgba(0, 132, 255, 0.6);
            }}
        """

    def _get_light_stylesheet(self) -> str:
        return f"""
            QDialog {{
                background-color: #F1F5F9;
                color: #0F172A;
                font-family: {FONT_FAMILY};
            }}
            QLabel {{
                color: #0F172A;
                font-size: 13px;
            }}
            QTabWidget::pane {{
                border: 1px solid #CBD5E1;
                background-color: #FFFFFF;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: #E2E8F0;
                color: #475569;
                padding: 9px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                background-color: #FFFFFF;
                color: #0F172A;
                border-bottom: 2px solid #0084FF;
            }}
            QGroupBox {{
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                margin-top: 10px;
                padding: 14px 12px 10px 12px;
                font-weight: 600;
                color: #0F172A;
                background-color: #FFFFFF;
            }}
            QGroupBox::title {{
                color: #0284C7;
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                font-size: 12px;
                font-weight: 700;
            }}
            QComboBox, QDoubleSpinBox {{
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 13px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                color: #0F172A;
                selection-background-color: #0084FF;
                selection-color: #FFFFFF;
                border: 1px solid #CBD5E1;
            }}
            QCheckBox {{
                color: #0F172A;
                font-size: 13px;
                spacing: 8px;
            }}
            QPushButton {{
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #E2E8F0;
                border-color: #0084FF;
            }}
        """

    def apply_theme(self, theme: str):
        """Switches between Dark Obsidian Glass and Light Frosted Acrylic."""
        self.current_theme = theme
        settings_db.set("settings_theme", theme)

        if theme == "light":
            self.setStyleSheet(self._get_light_stylesheet())
            self.btn_theme_toggle.setText("🌙 Dark Mode")
            self.btn_theme_toggle.setStyleSheet("background-color: #1E293B; color: #F8FAFC; font-weight: 600; border-radius: 12px; padding: 4px 12px;")
            sub_col = "#475569"
        else:
            self.setStyleSheet(self._get_dark_stylesheet())
            self.btn_theme_toggle.setText("☀️ Light Mode")
            self.btn_theme_toggle.setStyleSheet("background-color: rgba(255, 255, 255, 0.12); color: #F8FAFC; font-weight: 600; border-radius: 12px; padding: 4px 12px;")
            sub_col = "#94A3B8"

        for lbl in self._labels_to_theme:
            lbl.setStyleSheet(f"color: {sub_col}; font-size: 12px; line-height: 1.4;")

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)

    def _make_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text, self)
        lbl.setStyleSheet("font-size: 13px; font-weight: 600;")
        return lbl

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)

        # Header bar with Brand & Theme Switch
        top_bar = QHBoxLayout()
        header_title = QLabel(f"⚙️ {APP_NAME} Preferences", self)
        header_title.setStyleSheet("font-size: 16px; font-weight: 800;")
        top_bar.addWidget(header_title)

        top_bar.addStretch()

        self.btn_theme_toggle = QPushButton("☀️ Light Mode", self)
        self.btn_theme_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.btn_theme_toggle)

        main_layout.addLayout(top_bar)

        self.tabs = QTabWidget(self)

        # ─── Tab 1: Preferences & Performance ─────────────────────────
        tab_prefs = QWidget()
        layout_prefs = QVBoxLayout(tab_prefs)
        layout_prefs.setContentsMargins(14, 14, 14, 14)
        layout_prefs.setSpacing(10)

        # 1. Voice & Emotion Form
        box_voice = QGroupBox("🎙 Voice & Emotional Prosody", tab_prefs)
        form_voice = QFormLayout(box_voice)
        form_voice.setSpacing(10)
        form_voice.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.combo_voice = QComboBox(box_voice)
        for v in VOICES:
            self.combo_voice.addItem(v["label"], v["id"])
        form_voice.addRow(self._make_field_label("Default Voice:"), self.combo_voice)

        self.combo_emotion = QComboBox(box_voice)
        for m in EMOTION_MODES:
            self.combo_emotion.addItem(m["label"], m["id"])
        form_voice.addRow(self._make_field_label("Emotion & Tone:"), self.combo_emotion)

        self.combo_speed = QComboBox(box_voice)
        for s in SPEED_STEPS:
            self.combo_speed.addItem(f"{s}x", s)
        form_voice.addRow(self._make_field_label("Default Speed:"), self.combo_speed)

        layout_prefs.addWidget(box_voice)

        # 2. Performance & Live Voice Test Box
        box_test = QGroupBox("⚡ Audio Performance & Live Voice Test", tab_prefs)
        layout_test = QVBoxLayout(box_test)
        layout_test.setSpacing(8)

        lbl_test_desc = QLabel("Test speech synthesis speed, neural voice emotion, and latency in real time:", box_test)
        self._labels_to_theme.append(lbl_test_desc)
        layout_test.addWidget(lbl_test_desc)

        test_row = QHBoxLayout()
        self.btn_test_perf = QPushButton("▶ Test Voice & Latency Performance", box_test)
        self.btn_test_perf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_test_perf.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 7px 16px; border: none; border-radius: 5px;")
        self.btn_test_perf.clicked.connect(self._run_performance_test)
        test_row.addWidget(self.btn_test_perf)

        self.lbl_test_status = QLabel("Ready to test live audio", box_test)
        self.lbl_test_status.setStyleSheet("color: #0284C7; font-weight: 600; font-size: 12px;")
        test_row.addWidget(self.lbl_test_status)
        test_row.addStretch()
        layout_test.addLayout(test_row)

        layout_prefs.addWidget(box_test)

        # 3. System & Startup Options
        box_system = QGroupBox("⚙️ System, Startup & Playback", tab_prefs)
        layout_system = QVBoxLayout(box_system)
        layout_system.setSpacing(8)

        self.chk_startup = QCheckBox("🚀 Launch Voxel automatically when Windows starts", box_system)
        layout_system.addWidget(self.chk_startup)

        self.chk_prebuffer = QCheckBox("⚡ Instant Playback: Pre-generate first sentence on hover (0ms delay)", box_system)
        layout_system.addWidget(self.chk_prebuffer)

        self.chk_trigger = QCheckBox("✨ Show floating Voxel dual-capsule badge when selecting text", box_system)
        layout_system.addWidget(self.chk_trigger)

        self.chk_autoclose = QCheckBox("⏳ Automatically close player when speech finishes", box_system)
        layout_system.addWidget(self.chk_autoclose)

        delay_row = QHBoxLayout()
        lbl_delay = QLabel("Fade-out duration:", box_system)
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

        # macOS Accessibility
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

        # ─── Tab 2: Document & Presentation Reader ────────────────────
        tab_doc = QWidget()
        layout_doc = QVBoxLayout(tab_doc)
        layout_doc.setContentsMargins(14, 14, 14, 14)
        layout_doc.setSpacing(12)

        doc_header = QLabel("📑 Smart Document & Presentation Narration", tab_doc)
        doc_header.setStyleSheet("color: #0284C7; font-size: 14px; font-weight: 700;")
        layout_doc.addWidget(doc_header)

        lbl_doc_info = QLabel(
            "Voxel can automatically read entire Google Docs, Microsoft Word documents, "
            "PowerPoint and Google Slides presentations, and PDF files. "
            "Even if a document has hundreds of pages, narration begins in under 300ms.",
            tab_doc
        )
        self._labels_to_theme.append(lbl_doc_info)
        lbl_doc_info.setWordWrap(True)
        layout_doc.addWidget(lbl_doc_info)

        methods_box = QGroupBox("3 Ways to Read Entire Documents", tab_doc)
        methods_layout = QVBoxLayout(methods_box)
        methods_layout.setSpacing(8)

        m1 = QLabel("<b>1. Floating Trigger Capsule:</b> Click the right <b>📑 Document icon</b> on the floating badge near your selection.", methods_box)
        m1.setWordWrap(True)
        methods_layout.addWidget(m1)

        hotkey_label = "Cmd+Alt+D" if IS_MAC else "Ctrl+Alt+D"
        m2 = QLabel(f"<b>2. Global Hotkey:</b> Press <b><code>{hotkey_label}</code></b> anytime while viewing any document or presentation tab.", methods_box)
        m2.setWordWrap(True)
        methods_layout.addWidget(m2)

        m3 = QLabel("<b>3. Mini Player & Tray Menu:</b> Click the <b>📑 Document button</b> in the player capsule or choose <i>Open File...</i> to pick any PDF/Docx.", methods_box)
        m3.setWordWrap(True)
        methods_layout.addWidget(m3)

        layout_doc.addWidget(methods_box)

        pipe_box = QGroupBox("⚡ Zero-Delay Continuous Pipelining", tab_doc)
        pipe_layout = QVBoxLayout(pipe_box)
        lbl_pipe = QLabel(
            "Even for 50-page documents or long slide decks, Voxel breaks the content into "
            "smart sentence chunks and starts speaking the first sentence in <b>under 300 milliseconds</b>! "
            "Subsequent sentences synthesize continuously in the background for seamless narration.",
            pipe_box
        )
        lbl_pipe.setWordWrap(True)
        self._labels_to_theme.append(lbl_pipe)
        pipe_layout.addWidget(lbl_pipe)
        layout_doc.addWidget(pipe_box)

        layout_doc.addStretch()
        self.tabs.addTab(tab_doc, "📑 Document Reader")

        # ─── Tab 3: Downloads & Local Files ───────────────────────────
        tab_downloads = QWidget()
        layout_down = QVBoxLayout(tab_downloads)
        layout_down.setContentsMargins(14, 14, 14, 14)
        layout_down.setSpacing(12)

        down_header = QLabel(f"📦 Official Download & Local Packages ({VERSION})", tab_downloads)
        down_header.setStyleSheet("font-size: 14px; font-weight: 700;")
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
            lbl_pkg_desc.setWordWrap(True)
            self._labels_to_theme.append(lbl_pkg_desc)
            pkg_layout.addWidget(lbl_pkg_desc)

            pkg_row = QHBoxLayout()
            pkg_row.addWidget(QLabel(f"Target: <b>/Applications ({VERSION})</b>", tab_downloads))
            pkg_row.addStretch()

            btn_pkg = QPushButton(f"📥 Download Voxel-{VERSION}.pkg", tab_downloads)
            btn_pkg.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_pkg.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 6px 14px; border: none; border-radius: 5px;")
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
            lbl_win_desc.setWordWrap(True)
            self._labels_to_theme.append(lbl_win_desc)
            win_layout.addWidget(lbl_win_desc)

            win_row = QHBoxLayout()
            win_row.addWidget(QLabel(f"Target: <b>Windows 10 / 11 ({VERSION})</b>", tab_downloads))
            win_row.addStretch()

            btn_win = QPushButton(f"📥 Download Voxel-{VERSION}.exe", tab_downloads)
            btn_win.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_win.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 6px 14px; border: none; border-radius: 5px;")
            win_url = f"{GITHUB_URL}/releases/download/{VERSION}/Voxel-{VERSION}.exe"
            btn_win.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(win_url)))
            win_row.addWidget(btn_win)
            win_layout.addLayout(win_row)

            local_row = QHBoxLayout()
            btn_open_local = QPushButton("📁 Open Local Computer 'dist' Folder", tab_downloads)
            btn_open_local.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open_local.setStyleSheet("background-color: #0284C7; color: #FFFFFF; font-weight: 600; padding: 6px 14px; border: none; border-radius: 5px;")
            dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dist"))
            btn_open_local.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(dist_path)))
            local_row.addWidget(btn_open_local)
            local_row.addStretch()
            win_layout.addLayout(local_row)

            layout_down.addWidget(win_box)

        archive_box = QGroupBox("📦 Historical Versions Archive", tab_downloads)
        archive_layout = QVBoxLayout(archive_box)
        archive_layout.setSpacing(6)

        ver_list = QLabel(
            f"• <b>{VERSION} (Current)</b> — Light/Dark Settings, Live Test button, Fahim Architecture credits<br>"
            "• <b>v1.1.04</b> — Smart Document Reader, Emotional Copilot voices, Sub-second pipelining<br>"
            "• <b>v1.1.03</b> — Vibrant full-frame startup bar logo with maximized white mic<br>"
            "• <b>v1.1.02</b> — Standalone system tray mic icon maximization<br>"
            "• <b>v1.1.01</b> — 3-tier PNG icon branding for tray, app, and selection bubble<br>"
            "• <b>v1.1.00</b> — Vector SVG final logo integration<br>"
            "• <b>v1.0.09</b> — Smart App Control native MCI audio bypass<br>"
            "• <b>v1.0.06</b> — Light frosted glass tray icon & single-instance lock",
            tab_downloads
        )
        self._labels_to_theme.append(ver_list)
        archive_layout.addWidget(ver_list)

        archive_row = QHBoxLayout()
        archive_row.addStretch()
        btn_archive = QPushButton("🌐 View All Versions on GitHub Releases", tab_downloads)
        btn_archive.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_archive.setStyleSheet("padding: 5px 12px; border-radius: 4px; font-size: 11px;")
        btn_archive.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"{GITHUB_URL}/releases")))
        archive_row.addWidget(btn_archive)
        archive_layout.addLayout(archive_row)

        layout_down.addWidget(archive_box)
        layout_down.addStretch()
        self.tabs.addTab(tab_downloads, "📥 Downloads & Versions")

        # ─── Tab 4: About, Creator & Open Source ──────────────────────
        tab_about = QWidget()
        layout_about = QVBoxLayout(tab_about)
        layout_about.setContentsMargins(16, 16, 16, 16)
        layout_about.setSpacing(10)

        header_row = QHBoxLayout()
        header_logo = VoxelLogoWidget(size=46, animated=True, parent=tab_about)
        header_row.addWidget(header_logo)

        header_text = QVBoxLayout()
        title_lbl = QLabel(f"{APP_NAME}", self)
        title_lbl.setStyleSheet("font-size: 20px; font-weight: 800;")
        header_text.addWidget(title_lbl)

        sub_lbl = QLabel(f"{APP_TAGLINE}  •  A {COMPANY_NAME} Product", self)
        sub_lbl.setStyleSheet("color: #0084FF; font-size: 11px; font-weight: 700; letter-spacing: 0.8px;")
        header_text.addWidget(sub_lbl)
        header_row.addLayout(header_text)
        header_row.addStretch()
        layout_about.addLayout(header_row)

        # 1. Creator, Architecture & Design Concept Box (Fahim)
        creator_box = QGroupBox("💡 Creator, System Architecture & Design Concept", tab_about)
        creator_layout = QVBoxLayout(creator_box)
        creator_layout.setSpacing(8)

        creator_header = QLabel("<b>Fahim</b> — System Architecture, UX/UI Design & Product Concept", creator_box)
        creator_header.setStyleSheet("color: #0284C7; font-size: 13px; font-weight: 700;")
        creator_layout.addWidget(creator_header)

        creator_desc = QLabel(
            "Voxel was conceived, structurally architected, and designed by <b>Fahim</b> "
            f"as an official open-source product from <b>{COMPANY_NAME}</b> (<a href='{COMPANY_URL}' style='color:#0084FF;'>{COMPANY_URL}</a>).<br>"
            "Crafted to provide free, high-performance, and emotional text-to-speech anywhere on local machines without telemetry or restrictions.",
            creator_box
        )
        creator_desc.setWordWrap(True)
        self._labels_to_theme.append(creator_desc)
        creator_layout.addWidget(creator_desc)

        links_row = QHBoxLayout()
        btn_linkedin = QPushButton("🔗 Connect with Fahim on LinkedIn", creator_box)
        btn_linkedin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_linkedin.setStyleSheet("background-color: #0A66C2; color: #FFFFFF; font-weight: 700; padding: 7px 16px; border: none; border-radius: 5px;")
        btn_linkedin.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(LINKEDIN_URL)))
        links_row.addWidget(btn_linkedin)

        btn_website = QPushButton(f"🌐 Visit Digimo ({COMPANY_URL})", creator_box)
        btn_website.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_website.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 7px 16px; border: none; border-radius: 5px;")
        btn_website.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(COMPANY_URL)))
        links_row.addWidget(btn_website)

        btn_gh = QPushButton("🐙 GitHub Repository", creator_box)
        btn_gh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_gh.setStyleSheet("padding: 7px 14px; border-radius: 5px; font-weight: 600;")
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        links_row.addWidget(btn_gh)
        creator_layout.addLayout(links_row)

        layout_about.addWidget(creator_box)

        # 2. Open Source Freedom Box
        digimo_box = QGroupBox("🏢 Digimo Product & Open Source Freedom", tab_about)
        digimo_layout = QVBoxLayout(digimo_box)
        digimo_layout.setSpacing(6)

        lbl_digimo_desc = QLabel(
            "This software is <b>100% free and open source</b> with no copyright restrictions. "
            "Anyone is welcome to experiment, build upon it, make it more modern, and contribute.",
            self
        )
        lbl_digimo_desc.setWordWrap(True)
        self._labels_to_theme.append(lbl_digimo_desc)
        digimo_layout.addWidget(lbl_digimo_desc)
        layout_about.addWidget(digimo_box)

        # 3. Disclaimer Box
        disclaimer_box = QGroupBox("⚖️ Disclaimer & Setup Guide", tab_about)
        disclaimer_layout = QVBoxLayout(disclaimer_box)
        disclaimer_layout.setSpacing(6)

        lbl_disclaimer = QLabel(
            "<b>Disclaimer:</b> Provided 'as is' for personal and experimental use. "
            "Digimo, Fahim, and creators assume no responsibility or liability for any use or outcome. "
            "Please read the included setup guides before configuring on your machine.",
            self
        )
        lbl_disclaimer.setWordWrap(True)
        self._labels_to_theme.append(lbl_disclaimer)
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
        btn_save.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; border: none; padding: 7px 18px; border-radius: 5px;")
        btn_save.clicked.connect(self.save_and_apply)
        btn_row.addWidget(btn_save)

        btn_close = QPushButton("Close", self)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)

        main_layout.addLayout(btn_row)

    def _run_performance_test(self):
        """Runs a live speech test with the currently selected voice, speed, and emotion."""
        if not self.tts:
            self.lbl_test_status.setText("Audio engine not attached.")
            return

        if self.tts.is_speaking:
            self.tts.stop()
            self.btn_test_perf.setText("▶ Test Voice & Latency Performance")
            self.lbl_test_status.setText("Test stopped.")
            return

        # Temporarily apply selected voice and parameters
        voice_id = self.combo_voice.currentData()
        for i, v in enumerate(VOICES):
            if v["id"] == voice_id:
                self.tts.set_voice_index(i)
                break
        self.tts.set_speed(self.combo_speed.currentData())
        self.tts.set_emotion_mode(self.combo_emotion.currentData())

        self.btn_test_perf.setText("⏹ Stop Test")
        self.lbl_test_status.setText("⚡ Synthesizing live test phrase...")

        test_phrase = (
            "Hello! This is a live performance test of Voxel with your selected voice, "
            "playback speed, and emotional tone. Audio synthesis is fast, clear, and running at peak performance."
        )

        def _on_test_done():
            try:
                self.tts.playback_finished.disconnect(_on_test_done)
            except Exception:
                pass
            self.btn_test_perf.setText("▶ Test Voice & Latency Performance")
            self.lbl_test_status.setText("✓ Test completed successfully!")

        self.tts.playback_finished.connect(_on_test_done)
        self.tts.speak(test_phrase)

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

        self.chk_startup.setChecked(is_startup_enabled())

        prebuffer = settings_db.get("prebuffer_enabled", True)
        self.chk_prebuffer.setChecked(prebuffer)

        enabled = settings_db.get("selection_popup_enabled", True)
        self.chk_trigger.setChecked(enabled)

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
        settings_db.set("settings_theme", self.current_theme)

        set_startup_enabled(self.chk_startup.isChecked())

        self.settings_applied.emit()
        self.close()
