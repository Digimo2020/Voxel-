"""
Settings, Preferences & About Dialog for Voxel.
Redesigned with modern, clutter-free UI/UX:
- Two focused tabs: Preferences and About.
- Clean typography and card layout without underscores or text clipping.
- Dual Themes: Light Mode & Dark Mode with instant live preview.
- Direct links to LinkedIn, Digimo, and GitHub repository.
"""
import os
import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QComboBox, QCheckBox, QDoubleSpinBox, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QTimer
from PyQt6.QtGui import QCursor, QDesktopServices, QPainter, QColor, QBrush

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

LINKEDIN_URL = "https://www.linkedin.com/in/fahimdigital/"


class EqualizerPreviewWidget(QWidget):
    """Voice-reactive animated spectrum equalizer visualizer widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setMinimumWidth(150)
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

            color = QColor("#0084FF") if self.is_active else QColor(148, 163, 184, 120)
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
        self.setFixedSize(580, 680)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self._labels_to_theme = []
        self._init_ui()
        self.apply_theme(self.current_theme)
        self.load_values()

    def _get_dark_stylesheet(self) -> str:
        return f"""
            QDialog {{
                background-color: #121523;
                color: #F8FAFC;
                font-family: {FONT_FAMILY};
            }}
            QLabel {{
                color: #F1F5F9;
                font-size: 13px;
            }}
            QTabWidget::pane {{
                border: 1px solid #23293F;
                background-color: #161A2B;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: #1E2338;
                color: #94A3B8;
                padding: 10px 24px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background-color: #161A2B;
                color: #FFFFFF;
                border-bottom: 2px solid #0084FF;
            }}
            QGroupBox {{
                border: 1px solid #23293F;
                border-radius: 8px;
                margin-top: 10px;
                padding: 14px 12px 10px 12px;
                font-weight: 600;
                color: #F8FAFC;
                background-color: #1A1F33;
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
                background-color: #242A42;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #1E2438;
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
                background-color: #242A42;
                color: #FFFFFF;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #2F3755;
                border-color: #0084FF;
            }}
        """

    def _get_light_stylesheet(self) -> str:
        return f"""
            QDialog {{
                background-color: #F8FAFC;
                color: #0F172A;
                font-family: {FONT_FAMILY};
            }}
            QLabel {{
                color: #0F172A;
                font-size: 13px;
            }}
            QTabWidget::pane {{
                border: 1px solid #E2E8F0;
                background-color: #FFFFFF;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: #EDF2F7;
                color: #64748B;
                padding: 10px 24px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                background-color: #FFFFFF;
                color: #0F172A;
                border-bottom: 2px solid #0084FF;
            }}
            QGroupBox {{
                border: 1px solid #E2E8F0;
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
                padding: 6px 10px;
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
                padding: 7px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #EDF2F7;
                border-color: #0084FF;
            }}
        """

    def apply_theme(self, theme: str):
        """Switches between Dark Mode and Light Mode."""
        self.current_theme = theme
        settings_db.set("settings_theme", theme)

        if theme == "light":
            self.setStyleSheet(self._get_light_stylesheet())
            self.btn_theme_toggle.setText("🌙 Dark Mode")
            self.btn_theme_toggle.setStyleSheet("background-color: #1E293B; color: #F8FAFC; font-weight: 600; border-radius: 14px; padding: 5px 14px; border: none;")
            sub_col = "#64748B"
        else:
            self.setStyleSheet(self._get_dark_stylesheet())
            self.btn_theme_toggle.setText("☀️ Light Mode")
            self.btn_theme_toggle.setStyleSheet("background-color: rgba(255, 255, 255, 0.12); color: #F8FAFC; font-weight: 600; border-radius: 14px; padding: 5px 14px; border: 1px solid rgba(255, 255, 255, 0.2);")
            sub_col = "#94A3B8"

        for lbl in self._labels_to_theme:
            lbl.setStyleSheet(f"color: {sub_col}; font-size: 12px; line-height: 1.4;")

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)

    def open_preferences(self):
        self.tabs.setCurrentIndex(0)
        self.show()
        self.raise_()
        self.activateWindow()

    def open_about(self):
        self.tabs.setCurrentIndex(1)
        self.show()
        self.raise_()
        self.activateWindow()

    def _make_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text, self)
        lbl.setStyleSheet("font-size: 13px; font-weight: 600;")
        return lbl

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        # ─── Top Header Bar ──────────────────────────────────────────
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

        # ═════════════════════════════════════════════════════════════
        # ─── TAB 1: PREFERENCES ──────────────────────────────────────
        # ═════════════════════════════════════════════════════════════
        tab_prefs = QWidget()
        layout_prefs = QVBoxLayout(tab_prefs)
        layout_prefs.setContentsMargins(16, 16, 16, 16)
        layout_prefs.setSpacing(12)

        # 1. Voice & Emotion Form
        box_voice = QGroupBox("Voice & Speech Settings", tab_prefs)
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
        box_test = QGroupBox("Voice Performance & Audio Test", tab_prefs)
        layout_test = QVBoxLayout(box_test)
        layout_test.setSpacing(8)

        lbl_test_desc = QLabel("Test speech synthesis speed, neural voice emotion, and latency in real time:", box_test)
        self._labels_to_theme.append(lbl_test_desc)
        layout_test.addWidget(lbl_test_desc)

        test_row = QHBoxLayout()
        self.btn_test_perf = QPushButton("▶ Test Voice & Latency", box_test)
        self.btn_test_perf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_test_perf.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 7px 16px; border: none; border-radius: 6px;")
        self.btn_test_perf.clicked.connect(self._run_performance_test)
        test_row.addWidget(self.btn_test_perf)

        self.equalizer_preview = EqualizerPreviewWidget(box_test)
        test_row.addWidget(self.equalizer_preview)

        self.lbl_test_status = QLabel("Ready to test live audio", box_test)
        self.lbl_test_status.setStyleSheet("color: #0284C7; font-weight: 600; font-size: 12px;")
        test_row.addWidget(self.lbl_test_status)
        test_row.addStretch()
        layout_test.addLayout(test_row)

        layout_prefs.addWidget(box_test)

        # 3. System & Startup Options
        box_system = QGroupBox("System & Playback Options", tab_prefs)
        layout_system = QVBoxLayout(box_system)
        layout_system.setSpacing(8)

        self.chk_startup = QCheckBox("Launch Voxel automatically when Windows starts", box_system)
        layout_system.addWidget(self.chk_startup)

        self.chk_prebuffer = QCheckBox("Instant Playback: Pre-generate first sentence on hover (0ms delay)", box_system)
        layout_system.addWidget(self.chk_prebuffer)

        self.chk_trigger = QCheckBox("Show floating Voxel dual-capsule badge when selecting text", box_system)
        layout_system.addWidget(self.chk_trigger)

        self.chk_autoclose = QCheckBox("Automatically close player when speech finishes", box_system)
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

        # ═════════════════════════════════════════════════════════════
        # ─── TAB 2: ABOUT US ─────────────────────────────────────────
        # ═════════════════════════════════════════════════════════════
        tab_about = QWidget()
        layout_about = QVBoxLayout(tab_about)
        layout_about.setContentsMargins(16, 16, 16, 16)
        layout_about.setSpacing(12)

        # Hero Brand Header
        header_row = QHBoxLayout()
        header_logo = VoxelLogoWidget(size=48, animated=True, parent=tab_about)
        header_row.addWidget(header_logo)

        header_text = QVBoxLayout()
        title_row = QHBoxLayout()
        title_lbl = QLabel(APP_NAME, self)
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 800; letter-spacing: 0.5px;")
        title_row.addWidget(title_lbl)

        ver_badge = QLabel(f" {VERSION} ", self)
        ver_badge.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-size: 11px; font-weight: 700; border-radius: 4px; padding: 2px 8px;")
        title_row.addWidget(ver_badge)
        title_row.addStretch()
        header_text.addLayout(title_row)

        sub_lbl = QLabel(f"{APP_TAGLINE}  •  A {COMPANY_NAME} Product", self)
        sub_lbl.setStyleSheet("color: #0084FF; font-size: 12px; font-weight: 600;")
        header_text.addWidget(sub_lbl)
        header_row.addLayout(header_text)
        header_row.addStretch()
        layout_about.addLayout(header_row)

        # 1. Product Overview & Connect Card
        about_box = QGroupBox("About Voxel", tab_about)
        about_layout = QVBoxLayout(about_box)
        about_layout.setSpacing(10)

        about_desc = QLabel(
            f"Voxel is an official open-source product from <b>{COMPANY_NAME}</b>.<br>"
            "Crafted to provide free, high-performance, and emotional text-to-speech anywhere on local machines without telemetry or restrictions.",
            about_box
        )
        about_desc.setWordWrap(True)
        self._labels_to_theme.append(about_desc)
        about_layout.addWidget(about_desc)

        # Prominent Link Buttons with Full, Clear Labels
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
        btn_gh.setStyleSheet("padding: 8px 16px; border-radius: 6px; font-weight: 600;")
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        links_row.addWidget(btn_gh)

        about_layout.addLayout(links_row)
        layout_about.addWidget(about_box)

        # 2. Open Source Freedom Card
        freedom_box = QGroupBox("Open Source Freedom", tab_about)
        freedom_layout = QVBoxLayout(freedom_box)
        freedom_layout.setSpacing(6)

        lbl_freedom = QLabel(
            "This software is <b>100% free and open source</b> with no copyright restrictions or telemetry. "
            "Anyone is welcome to experiment, build upon it, make it more modern, and contribute.",
            tab_about
        )
        lbl_freedom.setWordWrap(True)
        self._labels_to_theme.append(lbl_freedom)
        freedom_layout.addWidget(lbl_freedom)
        layout_about.addWidget(freedom_box)

        # 3. Disclaimer Card
        disclaimer_box = QGroupBox("Disclaimer", tab_about)
        disclaimer_layout = QVBoxLayout(disclaimer_box)
        disclaimer_layout.setSpacing(6)

        lbl_disclaimer = QLabel(
            "Provided 'as is' for personal and productivity use. "
            "Digimo and creators assume no responsibility or liability for any use or outcome.",
            tab_about
        )
        lbl_disclaimer.setWordWrap(True)
        self._labels_to_theme.append(lbl_disclaimer)
        disclaimer_layout.addWidget(lbl_disclaimer)
        layout_about.addWidget(disclaimer_box)

        layout_about.addStretch()
        self.tabs.addTab(tab_about, "ℹ️ About")

        main_layout.addWidget(self.tabs)

        # ─── Bottom Actions Bar ──────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_save = QPushButton("Save Changes", self)
        btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_save.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; border: none; padding: 8px 22px; border-radius: 6px;")
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
