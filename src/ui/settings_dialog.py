"""
Settings, Preferences & About Dialog for Voxel.
Redesigned with modern, professional sidebar navigation matching Image 5:
- Left Sidebar with brand header, Voxel logo, and navigation tabs:
  Preferences, Voice & Speech, Playback, General, Appearance, About.
- Top Header with dynamic title, subtitle, and segmented Light/Dark toggle capsule.
- Embedded interactive Voice Equalizer (EQ) with vocal presets and parametric graph.
- Voice Performance & Latency live test with reactive spectrum visualizer.
- Clean About section with version badge, Connect on LinkedIn, Digimo, and GitHub links.
- Bottom Action Bar with Reset to Default, Close, and Save Changes.
"""
import os
import sys
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget, QScrollArea,
    QWidget, QLabel, QComboBox, QCheckBox, QDoubleSpinBox, QPushButton,
    QGroupBox, QFormLayout, QFrame, QButtonGroup
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QTimer, QRectF
from PyQt6.QtGui import (
    QCursor, QDesktopServices, QPainter, QColor, QBrush, QPen, QFont
)

from src.config import (
    VOICES, EMOTION_MODES, DEFAULT_EMOTION_MODE, SPEED_STEPS,
    VERSION, GITHUB_URL, APP_NAME, APP_TAGLINE, FONT_FAMILY, IS_MAC,
    COMPANY_NAME, COMPANY_URL
)
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from src.utils.startup import is_startup_enabled, set_startup_enabled
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from src.ui.voxel_logo_widget import VoxelLogoWidget
from src.ui.equalizer_widget import VoiceEqualizerWidget, EQ_PRESETS
from assets.icons import create_app_icon

LINKEDIN_URL = "https://www.linkedin.com/in/fahimdigital/"


class EqualizerPreviewWidget(QWidget):
    """Voice-reactive animated spectrum equalizer visualizer widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setMinimumWidth(140)
        self.is_active = False
        self._levels = [0.15] * 12

        self._timer = QTimer(self)
        self._timer.setInterval(40)  # ~25 FPS
        self._timer.timeout.connect(self._update_bars)
        self._timer.start()

    def set_active(self, active: bool):
        self.is_active = active
        self.update()

    def _update_bars(self):
        import random
        if self.is_active:
            for i in range(12):
                self._levels[i] = random.uniform(0.25, 0.95)
        else:
            for i in range(12):
                self._levels[i] = max(0.12, self._levels[i] * 0.85)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        num_bars = len(self._levels)
        bar_w = 4.0
        gap = (w - (num_bars * bar_w)) / max(1, num_bars - 1)

        for i, lvl in enumerate(self._levels):
            x = i * (bar_w + gap)
            bar_h = max(3.0, h * lvl)
            y = (h - bar_h) / 2.0

            color = QColor("#7C3AED") if self.is_active else QColor(148, 163, 184, 90)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(int(x), int(y), int(bar_w), int(bar_h), 2, 2)

        painter.end()


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()

    def __init__(self, tts_engine: Optional[TTSEngine] = None, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.current_theme = settings_db.get("settings_theme", "light")
        self.setWindowTitle(f"{APP_NAME} — Preferences ({VERSION})")
        self.setFixedSize(860, 680)
        self.setWindowIcon(create_app_icon(64))
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.nav_buttons: List[QPushButton] = []
        self._init_ui()
        self.apply_theme(self.current_theme)
        self.load_values()

    def _init_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ═════════════════════════════════════════════════════════════
        # 1. LEFT SIDEBAR (Width 220px)
        # ═════════════════════════════════════════════════════════════
        self.sidebar_widget = QWidget(self)
        self.sidebar_widget.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(16, 20, 16, 16)
        sidebar_layout.setSpacing(8)

        # Brand Header in Sidebar
        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)
        self.brand_logo = VoxelLogoWidget(size=36, animated=False, parent=self.sidebar_widget)
        brand_row.addWidget(self.brand_logo)

        brand_text_col = QVBoxLayout()
        brand_text_col.setSpacing(1)
        self.lbl_brand_title = QLabel(APP_NAME, self.sidebar_widget)
        self.lbl_brand_title.setStyleSheet("font-size: 17px; font-weight: 800; letter-spacing: 0.5px;")
        brand_text_col.addWidget(self.lbl_brand_title)

        self.lbl_brand_sub = QLabel("Text to Speech, Anywhere", self.sidebar_widget)
        self.lbl_brand_sub.setStyleSheet("font-size: 10px; color: #64748B; font-weight: 500;")
        brand_text_col.addWidget(self.lbl_brand_sub)
        brand_row.addLayout(brand_text_col)
        brand_row.addStretch()
        sidebar_layout.addLayout(brand_row)

        sidebar_layout.addSpacing(16)

        # Navigation Items
        self.nav_items = [
            ("⚙️  Preferences", 0, "Preferences", "Configure how Voxel works for you"),
            ("🎙️  Voice & Speech", 1, "Voice & Speech", "Select neural voices, tone, and equalizer curves"),
            ("⚡  Playback", 2, "Playback Options", "Customize instant hover triggers and auto-close behaviors"),
            ("🎛️  General", 3, "General Settings", "System startup, permissions, and background execution"),
            ("🎨  Appearance", 4, "Appearance", "Personalize themes, bubble styles, and visual accents"),
            ("ℹ️  About", 5, "About Voxel", "Product information, licenses, and social links"),
        ]

        self.btn_group_nav = QButtonGroup(self)
        for text, page_idx, header_title, header_sub in self.nav_items:
            btn = QPushButton(text, self.sidebar_widget)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, idx=page_idx, h_title=header_title, h_sub=header_sub: self._on_nav_clicked(idx, h_title, h_sub))
            self.btn_group_nav.addButton(btn)
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Sidebar Footer
        self.lbl_sidebar_footer = QLabel(f"Voxel {VERSION} · Open Source", self.sidebar_widget)
        self.lbl_sidebar_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sidebar_footer.setStyleSheet("font-size: 11px; color: #94A3B8; padding: 6px;")
        sidebar_layout.addWidget(self.lbl_sidebar_footer)

        root_layout.addWidget(self.sidebar_widget)

        # ═════════════════════════════════════════════════════════════
        # 2. RIGHT MAIN CONTENT AREA
        # ═════════════════════════════════════════════════════════════
        self.main_content_widget = QWidget(self)
        main_col = QVBoxLayout(self.main_content_widget)
        main_col.setContentsMargins(24, 20, 24, 16)
        main_col.setSpacing(14)

        # ─── Top Header Bar ──────────────────────────────────────────
        top_header_layout = QHBoxLayout()
        top_header_layout.setSpacing(12)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(2)
        self.lbl_header_title = QLabel("Preferences", self.main_content_widget)
        self.lbl_header_title.setStyleSheet("font-size: 20px; font-weight: 800;")
        header_text_layout.addWidget(self.lbl_header_title)

        self.lbl_header_subtitle = QLabel("Configure how Voxel works for you", self.main_content_widget)
        self.lbl_header_subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        header_text_layout.addWidget(self.lbl_header_subtitle)
        top_header_layout.addLayout(header_text_layout)

        top_header_layout.addStretch()

        # Segmented Theme Toggle Pill
        self.theme_segmented_widget = QWidget(self.main_content_widget)
        self.theme_segmented_widget.setObjectName("ThemePill")
        pill_layout = QHBoxLayout(self.theme_segmented_widget)
        pill_layout.setContentsMargins(3, 3, 3, 3)
        pill_layout.setSpacing(2)

        self.btn_theme_light = QPushButton("☀️ Light", self.theme_segmented_widget)
        self.btn_theme_light.setCheckable(True)
        self.btn_theme_light.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_theme_light.clicked.connect(lambda: self.apply_theme("light"))
        pill_layout.addWidget(self.btn_theme_light)

        self.btn_theme_dark = QPushButton("🌙 Dark", self.theme_segmented_widget)
        self.btn_theme_dark.setCheckable(True)
        self.btn_theme_dark.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_theme_dark.clicked.connect(lambda: self.apply_theme("dark"))
        pill_layout.addWidget(self.btn_theme_dark)

        top_header_layout.addWidget(self.theme_segmented_widget)
        main_col.addLayout(top_header_layout)

        # ─── Stacked Pages ───────────────────────────────────────────
        self.stacked_pages = QStackedWidget(self.main_content_widget)

        # Build reusable card widgets
        self.card_voice = self._create_card_voice()
        self.card_eq = self._create_card_eq()
        self.card_perf = self._create_card_performance()
        self.card_playback = self._create_card_playback()
        self.card_appearance = self._create_card_appearance()
        self.card_general = self._create_card_general()
        self.card_about = self._create_card_about()

        # Page 0: All Preferences (Scrollable full view)
        scroll_prefs = QScrollArea(self.stacked_pages)
        scroll_prefs.setWidgetResizable(True)
        scroll_prefs.setFrameShape(QFrame.Shape.NoFrame)
        scroll_prefs_content = QWidget()
        scroll_prefs_layout = QVBoxLayout(scroll_prefs_content)
        scroll_prefs_layout.setContentsMargins(0, 0, 8, 0)
        scroll_prefs_layout.setSpacing(14)
        scroll_prefs_layout.addWidget(self.card_voice)
        scroll_prefs_layout.addWidget(self.card_eq)
        scroll_prefs_layout.addWidget(self.card_perf)
        scroll_prefs_layout.addWidget(self.card_playback)
        scroll_prefs_layout.addStretch()
        scroll_prefs.setWidget(scroll_prefs_content)
        self.stacked_pages.addWidget(scroll_prefs)

        # Page 1: Voice & Speech
        self.stacked_pages.addWidget(self._create_voice_page())

        # Page 2: Playback
        self.stacked_pages.addWidget(self._create_playback_page())

        # Page 3: General
        self.stacked_pages.addWidget(self.card_general)

        # Page 4: Appearance
        self.stacked_pages.addWidget(self.card_appearance)

        # Page 5: About
        self.stacked_pages.addWidget(self.card_about)

        main_col.addWidget(self.stacked_pages)

        # ─── Bottom Action Bar ───────────────────────────────────────
        action_bar_layout = QHBoxLayout()
        action_bar_layout.setSpacing(10)

        self.btn_reset_defaults = QPushButton("Reset to Default", self.main_content_widget)
        self.btn_reset_defaults.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_reset_defaults.clicked.connect(self.reset_to_defaults)
        action_bar_layout.addWidget(self.btn_reset_defaults)

        action_bar_layout.addStretch()

        self.btn_close = QPushButton("Close", self.main_content_widget)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.clicked.connect(self.close)
        action_bar_layout.addWidget(self.btn_close)

        self.btn_save_changes = QPushButton("Save Changes", self.main_content_widget)
        self.btn_save_changes.setObjectName("BtnPrimary")
        self.btn_save_changes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save_changes.clicked.connect(self.save_and_apply)
        action_bar_layout.addWidget(self.btn_save_changes)

        main_col.addLayout(action_bar_layout)
        root_layout.addWidget(self.main_content_widget)

        # Set default active navigation button
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

    # ═════════════════════════════════════════════════════════════
    # CARD BUILDERS
    # ═════════════════════════════════════════════════════════════

    def _create_card_voice(self) -> QWidget:
        card = QGroupBox("Voice & Speech Settings", self)
        layout = QFormLayout(card)
        layout.setSpacing(10)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.combo_voice = QComboBox(card)
        for v in VOICES:
            self.combo_voice.addItem(v["label"], v["id"])
        lbl_v = QLabel("Primary Voice:")
        lbl_v.setStyleSheet("font-weight: 600;")
        layout.addRow(lbl_v, self.combo_voice)

        self.combo_emotion = QComboBox(card)
        for m in EMOTION_MODES:
            self.combo_emotion.addItem(m["label"], m["id"])
        lbl_e = QLabel("Emotion & Tone:")
        lbl_e.setStyleSheet("font-weight: 600;")
        layout.addRow(lbl_e, self.combo_emotion)

        self.combo_speed = QComboBox(card)
        for s in SPEED_STEPS:
            self.combo_speed.addItem(f"{s}x", s)
        lbl_s = QLabel("Speaking Speed:")
        lbl_s.setStyleSheet("font-weight: 600;")
        layout.addRow(lbl_s, self.combo_speed)

        return card

    def _create_card_eq(self) -> QWidget:
        card = QGroupBox("Voice Equalizer (EQ)", self)
        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        lbl_desc = QLabel("Interactive parametric audio response curve & tone presets:")
        lbl_desc.setStyleSheet("font-size: 11px; color: #64748B;")
        layout.addWidget(lbl_desc)

        self.equalizer_widget = VoiceEqualizerWidget(card)
        layout.addWidget(self.equalizer_widget)
        return card

    def _create_card_performance(self) -> QWidget:
        card = QGroupBox("Voice Performance & Latency Test", self)
        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        lbl_desc = QLabel("Test speech synthesis speed, neural voice emotion, and latency in real time:")
        lbl_desc.setStyleSheet("font-size: 11px; color: #64748B;")
        layout.addWidget(lbl_desc)

        test_row = QHBoxLayout()
        test_row.setSpacing(10)

        self.btn_test_perf = QPushButton("▶ Test Voice & Latency", card)
        self.btn_test_perf.setObjectName("BtnTest")
        self.btn_test_perf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_test_perf.clicked.connect(self._run_performance_test)
        test_row.addWidget(self.btn_test_perf)

        self.equalizer_preview = EqualizerPreviewWidget(card)
        test_row.addWidget(self.equalizer_preview)

        self.lbl_test_status = QLabel("Ready to test live audio", card)
        self.lbl_test_status.setStyleSheet("color: #7C3AED; font-weight: 600; font-size: 11px;")
        test_row.addWidget(self.lbl_test_status)
        test_row.addStretch()
        layout.addLayout(test_row)
        return card

    def _create_card_playback(self) -> QWidget:
        card = QGroupBox("Playback & Trigger Options", self)
        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        self.chk_startup = QCheckBox("Launch Voxel automatically when Windows starts", card)
        layout.addWidget(self.chk_startup)

        self.chk_prebuffer = QCheckBox("Instant Playback: Pre-generate first sentence on hover (0ms delay)", card)
        layout.addWidget(self.chk_prebuffer)

        self.chk_trigger = QCheckBox("Show floating Voxel dual-capsule badge when selecting text", card)
        layout.addWidget(self.chk_trigger)

        self.chk_autoclose = QCheckBox("Automatically close player when speech finishes", card)
        layout.addWidget(self.chk_autoclose)

        delay_row = QHBoxLayout()
        lbl_delay = QLabel("Fade-out duration:", card)
        lbl_delay.setStyleSheet("font-weight: 500;")
        delay_row.addWidget(lbl_delay)

        self.spin_autoclose_delay = QDoubleSpinBox(card)
        self.spin_autoclose_delay.setRange(0.5, 5.0)
        self.spin_autoclose_delay.setSingleStep(0.5)
        self.spin_autoclose_delay.setValue(1.0)
        self.spin_autoclose_delay.setSuffix(" sec")
        self.spin_autoclose_delay.setFixedWidth(110)
        delay_row.addWidget(self.spin_autoclose_delay)
        delay_row.addStretch()
        layout.addLayout(delay_row)

        return card

    def _create_card_appearance(self) -> QWidget:
        card = QGroupBox("Appearance & Styling", self)
        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        lbl_desc = QLabel("Customize theme mode, floating capsule style, and transparency:")
        lbl_desc.setStyleSheet("font-size: 11px; color: #64748B;")
        layout.addWidget(lbl_desc)

        theme_row = QHBoxLayout()
        lbl_t = QLabel("Active Application Theme:")
        lbl_t.setStyleSheet("font-weight: 600;")
        theme_row.addWidget(lbl_t)

        self.combo_app_theme = QComboBox(card)
        self.combo_app_theme.addItem("☀️ Light Theme", "light")
        self.combo_app_theme.addItem("🌙 Dark Theme", "dark")
        self.combo_app_theme.currentIndexChanged.connect(lambda: self.apply_theme(self.combo_app_theme.currentData()))
        theme_row.addWidget(self.combo_app_theme)
        theme_row.addStretch()
        layout.addLayout(theme_row)

        bubble_row = QHBoxLayout()
        lbl_b = QLabel("Floating Bubble Appearance:")
        lbl_b.setStyleSheet("font-weight: 600;")
        bubble_row.addWidget(lbl_b)

        self.combo_bubble_theme = QComboBox(card)
        self.combo_bubble_theme.addItem("✨ Frosted Glass (Adaptive)", "adaptive")
        self.combo_bubble_theme.addItem("💎 Solid Vibrant Acrylic", "solid")
        bubble_row.addWidget(self.combo_bubble_theme)
        bubble_row.addStretch()
        layout.addLayout(bubble_row)

        layout.addStretch()
        return card

    def _create_card_general(self) -> QWidget:
        card = QGroupBox("General & System Settings", self)
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        lbl_gen = QLabel("System startup, shortcuts, and background worker coordination:")
        lbl_gen.setStyleSheet("font-size: 11px; color: #64748B;")
        layout.addWidget(lbl_gen)

        lbl_sc = QLabel("<b>Global Shortcut:</b> Double-click selected text icon or press tray icon to trigger reading.")
        lbl_sc.setWordWrap(True)
        layout.addWidget(lbl_sc)

        if IS_MAC:
            perm_box = QGroupBox("macOS System Permissions", card)
            perm_layout = QHBoxLayout(perm_box)
            trusted = is_accessibility_trusted(prompt=False)
            status_text = "🟢 Granted" if trusted else "⚠️ Accessibility Needed"
            lbl_perm = QLabel(f"Accessibility: <b>{status_text}</b>", perm_box)
            perm_layout.addWidget(lbl_perm)

            btn_open_perm = QPushButton("Open System Settings", perm_box)
            btn_open_perm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open_perm.clicked.connect(open_accessibility_settings)
            perm_layout.addWidget(btn_open_perm)
            layout.addWidget(perm_box)

        layout.addStretch()
        return card

    def _create_card_about(self) -> QWidget:
        about_widget = QWidget(self)
        layout_about = QVBoxLayout(about_widget)
        layout_about.setContentsMargins(0, 0, 0, 0)
        layout_about.setSpacing(14)

        # Hero Brand Header
        header_card = QGroupBox("", about_widget)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(16, 16, 16, 16)
        header_layout.setSpacing(16)

        about_logo = VoxelLogoWidget(size=54, animated=True, parent=header_card)
        header_layout.addWidget(about_logo)

        header_text = QVBoxLayout()
        header_text.setSpacing(3)
        title_row = QHBoxLayout()
        lbl_t = QLabel(APP_NAME, header_card)
        lbl_t.setStyleSheet("font-size: 24px; font-weight: 800; letter-spacing: 0.5px;")
        title_row.addWidget(lbl_t)

        ver_badge = QLabel(f" {VERSION} ", header_card)
        ver_badge.setStyleSheet("background-color: #7C3AED; color: #FFFFFF; font-size: 11px; font-weight: 700; border-radius: 4px; padding: 2px 8px;")
        title_row.addWidget(ver_badge)
        title_row.addStretch()
        header_text.addLayout(title_row)

        sub_lbl = QLabel(f"{APP_TAGLINE}  •  A {COMPANY_NAME} Product", header_card)
        sub_lbl.setStyleSheet("color: #7C3AED; font-size: 12px; font-weight: 600;")
        header_text.addWidget(sub_lbl)
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        layout_about.addWidget(header_card)

        # 1. Product Overview & Connect Card
        about_box = QGroupBox("About Voxel", about_widget)
        about_layout = QVBoxLayout(about_box)
        about_layout.setSpacing(12)

        about_desc = QLabel(
            f"Voxel is an official open-source product from <b>{COMPANY_NAME}</b>.<br>"
            "Crafted to provide free, high-performance, and emotional text-to-speech anywhere on local machines without telemetry or restrictions.",
            about_box
        )
        about_desc.setWordWrap(True)
        about_layout.addWidget(about_desc)

        # Links Row with "Connect on LinkedIn", "Visit Digimo", "GitHub Repository"
        links_row = QHBoxLayout()
        links_row.setSpacing(10)

        btn_linkedin = QPushButton("🔗 Connect on LinkedIn", about_box)
        btn_linkedin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_linkedin.setStyleSheet("background-color: #0A66C2; color: #FFFFFF; font-weight: 700; padding: 8px 16px; border: none; border-radius: 6px;")
        btn_linkedin.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(LINKEDIN_URL)))
        links_row.addWidget(btn_linkedin)

        btn_website = QPushButton("🌐 Visit Digimo", about_box)
        btn_website.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_website.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 8px 16px; border: none; border-radius: 6px;")
        btn_website.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(COMPANY_URL)))
        links_row.addWidget(btn_website)

        btn_gh = QPushButton("🐙 GitHub Repository", about_box)
        btn_gh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_gh.setStyleSheet("background-color: #334155; color: #FFFFFF; font-weight: 700; padding: 8px 16px; border: none; border-radius: 6px;")
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        links_row.addWidget(btn_gh)

        about_layout.addLayout(links_row)
        layout_about.addWidget(about_box)

        # 2. Open Source Freedom Card
        freedom_box = QGroupBox("Open Source Freedom", about_widget)
        freedom_layout = QVBoxLayout(freedom_box)
        freedom_layout.setSpacing(6)
        lbl_freedom = QLabel(
            "This software is <b>100% free and open source</b> with no copyright restrictions or telemetry. "
            "Anyone is welcome to experiment, build upon it, make it more modern, and contribute.",
            about_widget
        )
        lbl_freedom.setWordWrap(True)
        freedom_layout.addWidget(lbl_freedom)
        layout_about.addWidget(freedom_box)

        # 3. Disclaimer Card
        disclaimer_box = QGroupBox("Disclaimer", about_widget)
        disclaimer_layout = QVBoxLayout(disclaimer_box)
        disclaimer_layout.setSpacing(6)
        lbl_disclaimer = QLabel(
            "Provided 'as is' for personal and productivity use. "
            "Digimo and creators assume no responsibility or liability for any use or outcome.",
            about_widget
        )
        lbl_disclaimer.setWordWrap(True)
        disclaimer_layout.addWidget(lbl_disclaimer)
        layout_about.addWidget(disclaimer_box)

        layout_about.addStretch()
        return about_widget

    def _create_voice_page(self) -> QWidget:
        """Stand-alone Voice & Speech page."""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(12)
        lbl = QLabel("Fine-tune neural voices, speaking cadence, and audio equalizer:")
        lbl.setStyleSheet("font-size: 12px; color: #64748B;")
        l.addWidget(lbl)
        l.addWidget(self.card_voice)
        l.addWidget(self.card_eq)
        l.addWidget(self.card_perf)
        l.addStretch()
        return w

    def _create_playback_page(self) -> QWidget:
        """Stand-alone Playback page."""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(12)
        lbl = QLabel("Customize instant hover pre-buffering, bubble triggers, and fade-out:")
        lbl.setStyleSheet("font-size: 12px; color: #64748B;")
        l.addWidget(lbl)
        l.addWidget(self.card_playback)
        l.addStretch()
        return w

    # ═════════════════════════════════════════════════════════════
    # THEME STYLESHEETS
    # ═════════════════════════════════════════════════════════════

    def _get_light_stylesheet(self) -> str:
        return f"""
            QDialog {{
                background-color: #F8FAFC;
                color: #0F172A;
                font-family: {FONT_FAMILY};
            }}
            #ThemePill {{
                background-color: #E2E8F0;
                border-radius: 16px;
                border: 1px solid #CBD5E1;
            }}
            #ThemePill QPushButton {{
                background-color: transparent;
                color: #64748B;
                border: none;
                border-radius: 13px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            #ThemePill QPushButton:checked {{
                background-color: #FFFFFF;
                color: #0F172A;
                font-weight: 700;
            }}
            QLabel {{
                color: #0F172A;
                font-size: 13px;
            }}
            QGroupBox {{
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                margin-top: 10px;
                padding: 16px 14px 12px 14px;
                font-weight: 600;
                color: #0F172A;
                background-color: #FFFFFF;
            }}
            QGroupBox::title {{
                color: #7C3AED;
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 4px;
                font-size: 12px;
                font-weight: 700;
            }}
            QComboBox, QDoubleSpinBox {{
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                color: #0F172A;
                selection-background-color: #7C3AED;
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
                padding: 7px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #EDF2F7;
                border-color: #7C3AED;
            }}
            #BtnPrimary {{
                background-color: #7C3AED;
                color: #FFFFFF;
                border: none;
                font-weight: 700;
                padding: 8px 24px;
            }}
            #BtnPrimary:hover {{
                background-color: #6D28D9;
            }}
            #BtnTest {{
                background-color: #7C3AED;
                color: #FFFFFF;
                border: none;
                font-weight: 700;
                padding: 7px 16px;
            }}
            #BtnTest:hover {{
                background-color: #6D28D9;
            }}
        """

    def _get_dark_stylesheet(self) -> str:
        return f"""
            QDialog {{
                background-color: #0F121E;
                color: #F8FAFC;
                font-family: {FONT_FAMILY};
            }}
            #ThemePill {{
                background-color: #1A1F33;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }}
            #ThemePill QPushButton {{
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 13px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            #ThemePill QPushButton:checked {{
                background-color: #2D3757;
                color: #FFFFFF;
                font-weight: 700;
            }}
            QLabel {{
                color: #F1F5F9;
                font-size: 13px;
            }}
            QGroupBox {{
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 10px;
                margin-top: 10px;
                padding: 16px 14px 12px 14px;
                font-weight: 600;
                color: #F8FAFC;
                background-color: #161A2B;
            }}
            QGroupBox::title {{
                color: #A78BFA;
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 4px;
                font-size: 12px;
                font-weight: 700;
            }}
            QComboBox, QDoubleSpinBox {{
                background-color: #1E2438;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #1E2438;
                color: #FFFFFF;
                selection-background-color: #7C3AED;
                selection-color: #FFFFFF;
                border: 1px solid #334155;
            }}
            QCheckBox {{
                color: #F1F5F9;
                font-size: 13px;
                spacing: 8px;
            }}
            QPushButton {{
                background-color: #242A42;
                color: #FFFFFF;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #2F3755;
                border-color: #7C3AED;
            }}
            #BtnPrimary {{
                background-color: #7C3AED;
                color: #FFFFFF;
                border: none;
                font-weight: 700;
                padding: 8px 24px;
            }}
            #BtnPrimary:hover {{
                background-color: #6D28D9;
            }}
            #BtnTest {{
                background-color: #7C3AED;
                color: #FFFFFF;
                border: none;
                font-weight: 700;
                padding: 7px 16px;
            }}
            #BtnTest:hover {{
                background-color: #6D28D9;
            }}
        """

    def apply_theme(self, theme: str):
        """Switches between Dark Mode and Light Mode."""
        self.current_theme = theme
        settings_db.set("settings_theme", theme)
        is_dark = (theme == "dark")

        if is_dark:
            self.setStyleSheet(self._get_dark_stylesheet())
            self.btn_theme_dark.setChecked(True)
            self.btn_theme_light.setChecked(False)
            self.sidebar_widget.setStyleSheet("background-color: #131726; border-right: 1px solid rgba(255, 255, 255, 0.08);")
            nav_btn_style = """
                QPushButton {
                    background-color: transparent;
                    color: #94A3B8;
                    border: none;
                    border-radius: 8px;
                    padding: 9px 14px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.06);
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background-color: #7C3AED;
                    color: #FFFFFF;
                    font-weight: 700;
                }
            """
        else:
            self.setStyleSheet(self._get_light_stylesheet())
            self.btn_theme_light.setChecked(True)
            self.btn_theme_dark.setChecked(False)
            self.sidebar_widget.setStyleSheet("background-color: #F1F5F9; border-right: 1px solid #E2E8F0;")
            nav_btn_style = """
                QPushButton {
                    background-color: transparent;
                    color: #475569;
                    border: none;
                    border-radius: 8px;
                    padding: 9px 14px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                    color: #0F172A;
                }
                QPushButton:checked {
                    background-color: #7C3AED;
                    color: #FFFFFF;
                    font-weight: 700;
                }
            """

        for btn in self.nav_buttons:
            btn.setStyleSheet(nav_btn_style)

        if hasattr(self, "equalizer_widget"):
            self.equalizer_widget.set_theme_mode(theme)

    def _on_nav_clicked(self, page_idx: int, header_title: str, header_sub: str):
        self.stacked_pages.setCurrentIndex(page_idx)
        self.lbl_header_title.setText(header_title)
        self.lbl_header_subtitle.setText(header_sub)

    def open_preferences(self):
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
        self._on_nav_clicked(0, "Preferences", "Configure how Voxel works for you")
        self.show()
        self.raise_()
        self.activateWindow()

    def open_about(self):
        if len(self.nav_buttons) > 5:
            self.nav_buttons[5].setChecked(True)
        self._on_nav_clicked(5, "About Voxel", "Product information, licenses, and social links")
        self.show()
        self.raise_()
        self.activateWindow()

    def _run_performance_test(self):
        """Runs a live speech test with the currently selected voice, speed, and emotion."""
        if not self.tts:
            self.lbl_test_status.setText("Audio engine not attached.")
            return

        if self.tts.is_speaking:
            self.tts.stop()
            self.btn_test_perf.setText("▶ Test Voice & Latency")
            self.lbl_test_status.setText("Test stopped.")
            if hasattr(self, "equalizer_preview"):
                self.equalizer_preview.set_active(False)
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
        self.lbl_test_status.setText("⚡ Synthesizing live audio...")
        if hasattr(self, "equalizer_preview"):
            self.equalizer_preview.set_active(True)

        test_phrase = (
            "Hello! This is a live performance test of Voxel with your selected voice, "
            "playback speed, and emotional tone. Audio synthesis is fast, clear, and running at peak performance."
        )

        def _on_test_done():
            try:
                self.tts.playback_finished.disconnect(_on_test_done)
            except Exception:
                pass
            self.btn_test_perf.setText("▶ Test Voice & Latency")
            self.lbl_test_status.setText("✓ Test completed successfully!")
            if hasattr(self, "equalizer_preview"):
                self.equalizer_preview.set_active(False)

        self.tts.playback_finished.connect(_on_test_done)
        self.tts.speak(test_phrase)

    def reset_to_defaults(self):
        """Restores all settings to factory defaults."""
        idx = self.combo_voice.findData("en-US-JennyNeural")
        if idx >= 0:
            self.combo_voice.setCurrentIndex(idx)
        idx_e = self.combo_emotion.findData(DEFAULT_EMOTION_MODE)
        if idx_e >= 0:
            self.combo_emotion.setCurrentIndex(idx_e)
        idx_s = self.combo_speed.findData(1.0)
        if idx_s >= 0:
            self.combo_speed.setCurrentIndex(idx_s)

        self.chk_startup.setChecked(False)
        self.chk_prebuffer.setChecked(True)
        self.chk_trigger.setChecked(True)
        self.chk_autoclose.setChecked(True)
        self.spin_autoclose_delay.setValue(1.0)

        if hasattr(self, "equalizer_widget"):
            self.equalizer_widget.apply_preset("Podcast Warmth")

    def load_values(self):
        """Loads saved settings into controls."""
        voice_id = settings_db.get("default_voice", "en-US-JennyNeural")
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
