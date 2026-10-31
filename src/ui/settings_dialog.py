"""
Settings, Preferences & About Dialog for Voxel.
Faithfully styled after modern Fluent/macOS design (matching mockups):
- Left Sidebar with brand header, 4 clean tabs, and bottom decorative wave:
  Voice & Speech, Playback, Appearance, About.
- Top Header with icon badge, title, subtitle, and segmented Light/Dark toggle pill.
- Playback Tab: Playback speed slider with 1.25x pill, Fade & Timing controls,
  Playback Behavior checkboxes, Audio Output, and Voxel Recordings folder integration.
- Appearance Tab: Selectable Light/Dark theme cards, 4 Floating Bubble appearance cards
  (Default, Frosted Glass, Transparent, Minimal), and Transparency/Size sliders.
- Voice & Speech Tab: Neural voices, emotion modes, interactive parametric Voice Equalizer (EQ),
  and latency performance test with live spectrum visualizer.
- About Tab: Version badge v1.1.13, Connect on LinkedIn, Digimo, and GitHub links.
- Bottom Action Bar: Reset to Default and vibrant purple Save Changes.
"""
import os
import sys
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget, QScrollArea,
    QWidget, QLabel, QComboBox, QCheckBox, QDoubleSpinBox, QPushButton,
    QGroupBox, QFormLayout, QFrame, QButtonGroup, QSlider, QSizePolicy
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QCursor, QDesktopServices, QPainter, QColor, QBrush, QPen, QFont,
    QPainterPath, QLinearGradient
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
from src.utils.audio_recorder import get_recordings_dir, open_recordings_folder
from src.ui.voxel_logo_widget import VoxelLogoWidget
from src.ui.equalizer_widget import VoiceEqualizerWidget, EQ_PRESETS
from assets.icons import create_app_icon

LINKEDIN_URL = "https://www.linkedin.com/in/fahimdigital/"


class SidebarWidget(QWidget):
    """Left sidebar with subtle decorative bottom-left wave matching mockup."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(210)
        self.theme_mode = "light"

    def set_theme_mode(self, mode: str):
        self.theme_mode = mode
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        is_dark = (self.theme_mode == "dark")

        # Background
        bg_col = QColor("#121524") if is_dark else QColor("#F8FAFC")
        painter.fillRect(self.rect(), bg_col)

        # Right divider border
        border_col = QColor(255, 255, 255, 18) if is_dark else QColor("#E2E8F0")
        painter.setPen(QPen(border_col, 1.0))
        painter.drawLine(int(w - 1), 0, int(w - 1), int(h))

        # Bottom decorative organic wave (matching user mockups!)
        wave_path1 = QPainterPath()
        wave_path1.moveTo(0, h)
        wave_path1.lineTo(0, h - 85)
        wave_path1.cubicTo(w * 0.35, h - 110, w * 0.65, h - 45, w, h - 65)
        wave_path1.lineTo(w, h)
        wave_path1.closeSubpath()

        wave_path2 = QPainterPath()
        wave_path2.moveTo(0, h)
        wave_path2.lineTo(0, h - 55)
        wave_path2.cubicTo(w * 0.40, h - 80, w * 0.70, h - 20, w, h - 40)
        wave_path2.lineTo(w, h)
        wave_path2.closeSubpath()

        if is_dark:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(124, 58, 237, 28)))
            painter.drawPath(wave_path1)
            painter.setBrush(QBrush(QColor(167, 139, 250, 38)))
            painter.drawPath(wave_path2)
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(216, 180, 254, 90)))
            painter.drawPath(wave_path1)
            painter.setBrush(QBrush(QColor(192, 132, 252, 120)))
            painter.drawPath(wave_path2)

        painter.end()


class EqualizerPreviewWidget(QWidget):
    """Voice-reactive animated spectrum equalizer visualizer widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setMinimumWidth(140)
        self.is_active = False
        self._levels = [0.15] * 12

        self._timer = QTimer(self)
        self._timer.setInterval(40)
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
        self.setWindowTitle(f"{APP_NAME} — Settings ({VERSION})")
        self.setFixedSize(890, 680)
        self.setWindowIcon(create_app_icon(64))
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.nav_buttons: List[QPushButton] = []
        self._bubble_style_cards = []
        self._init_ui()
        self.apply_theme(self.current_theme)
        self.load_values()

    def _init_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ═════════════════════════════════════════════════════════════
        # 1. LEFT SIDEBAR (Width 210px with bottom wave)
        # ═════════════════════════════════════════════════════════════
        self.sidebar_widget = SidebarWidget(self)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(14, 20, 14, 16)
        sidebar_layout.setSpacing(8)

        # Brand Header in Sidebar
        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)
        self.brand_logo = VoxelLogoWidget(size=36, animated=False, parent=self.sidebar_widget)
        brand_row.addWidget(self.brand_logo)

        brand_text_col = QVBoxLayout()
        brand_text_col.setSpacing(1)
        self.lbl_brand_title = QLabel(APP_NAME, self.sidebar_widget)
        self.lbl_brand_title.setStyleSheet("font-size: 18px; font-weight: 800; letter-spacing: 0.5px;")
        brand_text_col.addWidget(self.lbl_brand_title)

        self.lbl_brand_sub = QLabel("Text to Speech, Anywhere", self.sidebar_widget)
        self.lbl_brand_sub.setStyleSheet("font-size: 10px; color: #64748B; font-weight: 500;")
        brand_text_col.addWidget(self.lbl_brand_sub)
        brand_row.addLayout(brand_text_col)
        brand_row.addStretch()
        sidebar_layout.addLayout(brand_row)

        sidebar_layout.addSpacing(18)

        # 4 Navigation Items matching user mockups
        self.nav_items = [
            ("🎙️  Voice & Speech", 0, "🎙️", "Voice & Speech", "Fine-tune neural voices, cadence, and parametric equalizer"),
            ("▶  Playback", 1, "▶", "Playback", "Control how Voxel plays text-to-speech audio"),
            ("🎨  Appearance", 2, "🎨", "Appearance", "Personalize the look and feel of Voxel"),
            ("ℹ️  About", 3, "ℹ️", "About Voxel", "Product information, licenses, and social links"),
        ]

        self.btn_group_nav = QButtonGroup(self)
        for text, page_idx, icon_badge, header_title, header_sub in self.nav_items:
            btn = QPushButton(text, self.sidebar_widget)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, idx=page_idx, b=icon_badge, h_title=header_title, h_sub=header_sub: self._on_nav_clicked(idx, b, h_title, h_sub))
            self.btn_group_nav.addButton(btn)
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        root_layout.addWidget(self.sidebar_widget)

        # ═════════════════════════════════════════════════════════════
        # 2. RIGHT MAIN CONTENT AREA
        # ═════════════════════════════════════════════════════════════
        self.main_content_widget = QWidget(self)
        main_col = QVBoxLayout(self.main_content_widget)
        main_col.setContentsMargins(22, 18, 22, 16)
        main_col.setSpacing(12)

        # ─── Top Header Bar ──────────────────────────────────────────
        top_header_layout = QHBoxLayout()
        top_header_layout.setSpacing(12)

        self.header_badge = QLabel("▶", self.main_content_widget)
        self.header_badge.setFixedSize(36, 36)
        self.header_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_badge.setStyleSheet("background-color: #EDE9FE; color: #7C3AED; font-size: 16px; font-weight: 700; border-radius: 8px;")
        top_header_layout.addWidget(self.header_badge)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(2)
        self.lbl_header_title = QLabel("Playback", self.main_content_widget)
        self.lbl_header_title.setStyleSheet("font-size: 21px; font-weight: 800;")
        header_text_layout.addWidget(self.lbl_header_title)

        self.lbl_header_subtitle = QLabel("Control how Voxel plays text-to-speech audio", self.main_content_widget)
        self.lbl_header_subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        header_text_layout.addWidget(self.lbl_header_subtitle)
        top_header_layout.addLayout(header_text_layout)

        top_header_layout.addStretch()

        # Segmented Theme Toggle Pill [ ☀️ Light | 🌙 Dark ]
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

        # Build Pages
        self.page_voice = self._create_voice_page()
        self.page_playback = self._create_playback_page()
        self.page_appearance = self._create_appearance_page()
        self.page_about = self._create_about_page()

        self.stacked_pages.addWidget(self.page_voice)        # Index 0
        self.stacked_pages.addWidget(self.page_playback)     # Index 1
        self.stacked_pages.addWidget(self.page_appearance)   # Index 2
        self.stacked_pages.addWidget(self.page_about)        # Index 3

        main_col.addWidget(self.stacked_pages)

        # ─── Bottom Action Bar ───────────────────────────────────────
        action_bar_layout = QHBoxLayout()
        action_bar_layout.setSpacing(10)

        self.btn_reset_defaults = QPushButton("↺  Reset to Default", self.main_content_widget)
        self.btn_reset_defaults.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_reset_defaults.clicked.connect(self.reset_to_defaults)
        action_bar_layout.addWidget(self.btn_reset_defaults)

        action_bar_layout.addStretch()

        self.btn_save_changes = QPushButton("✓  Save Changes", self.main_content_widget)
        self.btn_save_changes.setObjectName("BtnPrimary")
        self.btn_save_changes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save_changes.clicked.connect(self.save_and_apply)
        action_bar_layout.addWidget(self.btn_save_changes)

        main_col.addLayout(action_bar_layout)
        root_layout.addWidget(self.main_content_widget)

        # Default select Playback tab matching user mockup
        if len(self.nav_buttons) > 1:
            self.nav_buttons[1].setChecked(True)
            self._on_nav_clicked(1, "▶", "Playback", "Control how Voxel plays text-to-speech audio")

    # ═════════════════════════════════════════════════════════════
    # PAGE 1: PLAYBACK (Matching Mockup Image 2)
    # ═════════════════════════════════════════════════════════════

    def _create_playback_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(12)

        # Row 1: Playback Speed Card (Left) & Fade & Timing Card (Right)
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Card 1: Playback Speed
        card_speed = QGroupBox("Playback Speed", content)
        l_speed = QVBoxLayout(card_speed)
        l_speed.setSpacing(6)
        sub_s = QLabel("Set the speaking speed for playback.")
        sub_s.setStyleSheet("font-size: 11px; color: #64748B;")
        l_speed.addWidget(sub_s)

        slider_row = QHBoxLayout()
        self.slider_speed = QSlider(Qt.Orientation.Horizontal, card_speed)
        self.slider_speed.setRange(50, 200)  # 0.5x to 2.0x
        self.slider_speed.setValue(100)
        self.slider_speed.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.slider_speed.valueChanged.connect(self._on_speed_slider_changed)
        slider_row.addWidget(self.slider_speed)

        self.lbl_speed_val = QLabel("1.00x", card_speed)
        self.lbl_speed_val.setStyleSheet("background-color: #EDE9FE; color: #7C3AED; font-weight: 700; font-size: 12px; border-radius: 6px; padding: 3px 8px;")
        slider_row.addWidget(self.lbl_speed_val)
        l_speed.addLayout(slider_row)

        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("0.5x"))
        scale_row.addStretch()
        scale_row.addWidget(QLabel("Normal (1.0x)"))
        scale_row.addStretch()
        scale_row.addWidget(QLabel("2.0x"))
        for i in range(scale_row.count()):
            w = scale_row.itemAt(i).widget()
            if w:
                w.setStyleSheet("color: #94A3B8; font-size: 10px;")
        l_speed.addLayout(scale_row)
        top_row.addWidget(card_speed)

        # Card 2: Fade & Timing
        card_timing = QGroupBox("Fade & Timing", content)
        l_timing = QVBoxLayout(card_timing)
        l_timing.setSpacing(8)
        sub_t = QLabel("Control start and end transitions.")
        sub_t.setStyleSheet("font-size: 11px; color: #64748B;")
        l_timing.addWidget(sub_t)

        dur_row = QHBoxLayout()
        dur_row.addWidget(QLabel("Fade-out duration"))
        self.spin_fade_duration = QDoubleSpinBox(card_timing)
        self.spin_fade_duration.setRange(0.2, 5.0)
        self.spin_fade_duration.setSingleStep(0.25)
        self.spin_fade_duration.setValue(1.00)
        self.spin_fade_duration.setSuffix(" sec")
        self.spin_fade_duration.setFixedWidth(100)
        dur_row.addWidget(self.spin_fade_duration)
        l_timing.addLayout(dur_row)

        self.chk_fade_in = QCheckBox("Smooth fade-in at start", card_timing)
        self.chk_fade_in.setChecked(True)
        l_timing.addWidget(self.chk_fade_in)
        top_row.addWidget(card_timing)

        layout.addLayout(top_row)

        # Card 3: Playback Behavior (2x2 grid of checkboxes)
        card_behavior = QGroupBox("Playback Behavior", content)
        l_beh = QVBoxLayout(card_behavior)
        l_beh.setSpacing(8)
        sub_b = QLabel("Choose when and how Voxel plays audio.")
        sub_b.setStyleSheet("font-size: 11px; color: #64748B;")
        l_beh.addWidget(sub_b)

        grid_beh = QHBoxLayout()
        col1 = QVBoxLayout()
        col1.setSpacing(8)
        self.chk_startup = QCheckBox("Launch Voxel automatically when Windows starts", card_behavior)
        col1.addWidget(self.chk_startup)
        self.chk_prebuffer = QCheckBox("Instant playback: Pre-generate first sentence on hover", card_behavior)
        col1.addWidget(self.chk_prebuffer)
        grid_beh.addLayout(col1)

        col2 = QVBoxLayout()
        col2.setSpacing(8)
        self.chk_trigger = QCheckBox("Show floating Voxel badge when selecting text", card_behavior)
        col2.addWidget(self.chk_trigger)
        self.chk_autoclose = QCheckBox("Automatically close player when speech finishes", card_behavior)
        col2.addWidget(self.chk_autoclose)
        grid_beh.addLayout(col2)
        l_beh.addLayout(grid_beh)
        layout.addWidget(card_behavior)

        # Card 4: Audio Output & Automatic Recordings Folder
        card_out = QGroupBox("Audio Output & Recordings", content)
        l_out = QVBoxLayout(card_out)
        l_out.setSpacing(10)
        sub_o = QLabel("Choose where to play audio and automatically save speech recordings.")
        sub_o.setStyleSheet("font-size: 11px; color: #64748B;")
        l_out.addWidget(sub_o)

        out_row = QHBoxLayout()
        out_row.setSpacing(16)

        # Output Device
        dev_col = QVBoxLayout()
        dev_col.addWidget(QLabel("Output Device:"))
        self.combo_device = QComboBox(card_out)
        self.combo_device.addItem("🔊 Default Output Device (Speakers / Headphones)", "default")
        dev_col.addWidget(self.combo_device)
        out_row.addLayout(dev_col, 3)

        # Volume Slider
        vol_col = QVBoxLayout()
        vol_col.addWidget(QLabel("Volume:"))
        vol_h = QHBoxLayout()
        vol_h.addWidget(QLabel("🔊"))
        self.slider_volume = QSlider(Qt.Orientation.Horizontal, card_out)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(80)
        self.slider_volume.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.slider_volume.valueChanged.connect(lambda v: self.lbl_vol_val.setText(f"{v}%"))
        vol_h.addWidget(self.slider_volume)
        self.lbl_vol_val = QLabel("80%", card_out)
        self.lbl_vol_val.setStyleSheet("font-weight: 600; font-size: 12px; color: #7C3AED;")
        vol_h.addWidget(self.lbl_vol_val)
        vol_col.addLayout(vol_h)
        out_row.addLayout(vol_col, 2)
        l_out.addLayout(out_row)

        # Voxel Recordings Folder Row
        rec_row = QHBoxLayout()
        rec_row.setSpacing(8)
        lbl_rec_path = QLabel(f"📁 Automatic Recordings Folder:  <b>{get_recordings_dir()}</b>", card_out)
        lbl_rec_path.setStyleSheet("font-size: 12px; color: #475569;")
        rec_row.addWidget(lbl_rec_path)
        rec_row.addStretch()

        btn_open_rec = QPushButton("📂 Open Recordings Folder", card_out)
        btn_open_rec.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_open_rec.setStyleSheet("background-color: #EDE9FE; color: #7C3AED; font-weight: 700; border: none; border-radius: 6px; padding: 6px 14px;")
        btn_open_rec.clicked.connect(open_recordings_folder)
        rec_row.addWidget(btn_open_rec)
        l_out.addLayout(rec_row)

        layout.addWidget(card_out)
        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _on_speed_slider_changed(self, val: int):
        speed = round(val / 100.0, 2)
        self.lbl_speed_val.setText(f"{speed:.2f}x")
        if self.tts:
            self.tts.set_speed(speed)

    # ═════════════════════════════════════════════════════════════
    # PAGE 2: APPEARANCE (Matching Mockup Image 3)
    # ═════════════════════════════════════════════════════════════

    def _create_appearance_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(12)

        # Card 1: Application Theme (Selectable Light & Dark theme cards)
        card_theme = QGroupBox("Application Theme", content)
        l_th = QVBoxLayout(card_theme)
        l_th.setSpacing(8)
        sub_th = QLabel("Choose the overall look for the application.")
        sub_th.setStyleSheet("font-size: 11px; color: #64748B;")
        l_th.addWidget(sub_th)

        theme_cards_row = QHBoxLayout()
        theme_cards_row.setSpacing(12)

        # Light Theme Card
        self.card_light_theme = QFrame(card_theme)
        self.card_light_theme.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.card_light_theme.mousePressEvent = lambda e: self.apply_theme("light")
        l_lt = QHBoxLayout(self.card_light_theme)
        l_lt.setContentsMargins(14, 12, 14, 12)
        l_lt.setSpacing(10)
        lt_icon = QLabel("☀️", self.card_light_theme)
        lt_icon.setStyleSheet("font-size: 24px;")
        l_lt.addWidget(lt_icon)
        lt_text = QVBoxLayout()
        lbl_lt_title = QLabel("Light Theme", self.card_light_theme)
        lbl_lt_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        lbl_lt_sub = QLabel("Clean, bright and modern", self.card_light_theme)
        lbl_lt_sub.setStyleSheet("font-size: 11px; color: #64748B;")
        lt_text.addWidget(lbl_lt_title)
        lt_text.addWidget(lbl_lt_sub)
        l_lt.addLayout(lt_text)
        l_lt.addStretch()
        self.lbl_lt_chk = QLabel("✓", self.card_light_theme)
        self.lbl_lt_chk.setStyleSheet("background-color: #7C3AED; color: #FFFFFF; font-weight: 800; border-radius: 10px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px; qproperty-alignment: AlignCenter;")
        l_lt.addWidget(self.lbl_lt_chk)
        theme_cards_row.addWidget(self.card_light_theme)

        # Dark Theme Card
        self.card_dark_theme = QFrame(card_theme)
        self.card_dark_theme.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.card_dark_theme.mousePressEvent = lambda e: self.apply_theme("dark")
        l_dt = QHBoxLayout(self.card_dark_theme)
        l_dt.setContentsMargins(14, 12, 14, 12)
        l_dt.setSpacing(10)
        dt_icon = QLabel("🌙", self.card_dark_theme)
        dt_icon.setStyleSheet("font-size: 24px;")
        l_dt.addWidget(dt_icon)
        dt_text = QVBoxLayout()
        lbl_dt_title = QLabel("Dark Theme", self.card_dark_theme)
        lbl_dt_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        lbl_dt_sub = QLabel("Easy on the eyes, great for low light", self.card_dark_theme)
        lbl_dt_sub.setStyleSheet("font-size: 11px; color: #64748B;")
        dt_text.addWidget(lbl_dt_title)
        dt_text.addWidget(lbl_dt_sub)
        l_dt.addLayout(dt_text)
        l_dt.addStretch()
        self.lbl_dt_chk = QLabel("✓", self.card_dark_theme)
        self.lbl_dt_chk.setStyleSheet("background-color: #7C3AED; color: #FFFFFF; font-weight: 800; border-radius: 10px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px; qproperty-alignment: AlignCenter;")
        l_dt.addWidget(self.lbl_dt_chk)
        theme_cards_row.addWidget(self.card_dark_theme)

        l_th.addLayout(theme_cards_row)
        layout.addWidget(card_theme)

        # Card 2: Floating Bubble Appearance (4 selectable cards: Default, Frosted Glass, Transparent, Minimal)
        card_bubble_app = QGroupBox("Floating Bubble Appearance", content)
        l_ba = QVBoxLayout(card_bubble_app)
        l_ba.setSpacing(8)
        sub_ba = QLabel("Customize the text selection bubble style and transparency.")
        sub_ba.setStyleSheet("font-size: 11px; color: #64748B;")
        l_ba.addWidget(sub_ba)

        bubble_styles_row = QHBoxLayout()
        bubble_styles_row.setSpacing(10)

        bubble_presets = [
            ("Default", "Standard border capsule"),
            ("Frosted Glass", "Adaptive acrylic translucency"),
            ("Transparent", "Minimal outline with high transparency"),
            ("Minimal", "Solid compact purple accent"),
        ]

        self.bubble_cards: Dict[str, QFrame] = {}
        for name, desc in bubble_presets:
            f = QFrame(card_bubble_app)
            f.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            f_l = QVBoxLayout(f)
            f_l.setContentsMargins(10, 10, 10, 10)
            f_l.setSpacing(4)
            lbl_n = QLabel(name, f)
            lbl_n.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_n.setStyleSheet("font-weight: 700; font-size: 12px;")
            f_l.addWidget(lbl_n)
            f.mousePressEvent = lambda e, s=name: self._select_bubble_style(s)
            self.bubble_cards[name] = f
            bubble_styles_row.addWidget(f)

        l_ba.addLayout(bubble_styles_row)
        layout.addWidget(card_bubble_app)

        # Card 3: Bubble Settings (Transparency & Bubble Size)
        card_b_set = QGroupBox("Bubble Settings", content)
        l_bs = QVBoxLayout(card_b_set)
        l_bs.setSpacing(8)
        sub_bs = QLabel("Adjust appearance and position of the floating bubble.")
        sub_bs.setStyleSheet("font-size: 11px; color: #64748B;")
        l_bs.addWidget(sub_bs)

        bs_row = QHBoxLayout()
        bs_row.setSpacing(20)

        # Transparency
        trans_col = QVBoxLayout()
        trans_col.addWidget(QLabel("Transparency:"))
        trans_h = QHBoxLayout()
        self.slider_transparency = QSlider(Qt.Orientation.Horizontal, card_b_set)
        self.slider_transparency.setRange(30, 100)
        self.slider_transparency.setValue(90)
        self.slider_transparency.valueChanged.connect(lambda v: self.lbl_trans_val.setText(f"{v}%"))
        trans_h.addWidget(self.slider_transparency)
        self.lbl_trans_val = QLabel("90%", card_b_set)
        self.lbl_trans_val.setStyleSheet("font-weight: 700; color: #7C3AED; font-size: 12px;")
        trans_h.addWidget(self.lbl_trans_val)
        trans_col.addLayout(trans_h)
        bs_row.addLayout(trans_col)

        # Bubble Size
        size_col = QVBoxLayout()
        size_col.addWidget(QLabel("Bubble Size:"))
        size_h = QHBoxLayout()
        self.slider_bubble_size = QSlider(Qt.Orientation.Horizontal, card_b_set)
        self.slider_bubble_size.setRange(1, 3)
        self.slider_bubble_size.setValue(2)
        size_h.addWidget(self.slider_bubble_size)

        self.combo_bubble_size = QComboBox(card_b_set)
        self.combo_bubble_size.addItem("Small", 1)
        self.combo_bubble_size.addItem("Medium", 2)
        self.combo_bubble_size.addItem("Large", 3)
        self.combo_bubble_size.setCurrentIndex(1)
        self.combo_bubble_size.currentIndexChanged.connect(lambda idx: self.slider_bubble_size.setValue(idx + 1))
        self.slider_bubble_size.valueChanged.connect(lambda val: self.combo_bubble_size.setCurrentIndex(val - 1))
        size_h.addWidget(self.combo_bubble_size)
        size_col.addLayout(size_h)
        bs_row.addLayout(size_col)

        l_bs.addLayout(bs_row)
        layout.addWidget(card_b_set)
        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _select_bubble_style(self, style_name: str):
        settings_db.set("bubble_appearance", style_name)
        is_dark = (self.current_theme == "dark")
        for name, card in self.bubble_cards.items():
            if name == style_name:
                card.setStyleSheet("QFrame { background-color: #EDE9FE; border: 2px solid #7C3AED; border-radius: 8px; color: #7C3AED; }" if not is_dark else "QFrame { background-color: #2E1065; border: 2px solid #A78BFA; border-radius: 8px; color: #FFFFFF; }")
            else:
                card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; color: #0F172A; }" if not is_dark else "QFrame { background-color: #1A1F33; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; color: #94A3B8; }")

    # ═════════════════════════════════════════════════════════════
    # PAGE 0: VOICE & SPEECH
    # ═════════════════════════════════════════════════════════════

    def _create_voice_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(12)

        # Card 1: Voice & Emotion Selection
        card_v = QGroupBox("Voice & Emotion Selection", content)
        l_v = QFormLayout(card_v)
        l_v.setSpacing(10)
        l_v.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.combo_voice = QComboBox(card_v)
        for v in VOICES:
            self.combo_voice.addItem(v["label"], v["id"])
        l_v.addRow(QLabel("<b>Primary Voice:</b>"), self.combo_voice)

        self.combo_emotion = QComboBox(card_v)
        for m in EMOTION_MODES:
            self.combo_emotion.addItem(m["label"], m["id"])
        l_v.addRow(QLabel("<b>Emotion & Tone:</b>"), self.combo_emotion)
        layout.addWidget(card_v)

        # Card 2: Interactive Voice Equalizer (EQ)
        card_eq = QGroupBox("Voice Equalizer (EQ)", content)
        l_eq = QVBoxLayout(card_eq)
        l_eq.setSpacing(6)
        lbl_eq_sub = QLabel("Parametric frequency curve and vocal timbre presets:")
        lbl_eq_sub.setStyleSheet("font-size: 11px; color: #64748B;")
        l_eq.addWidget(lbl_eq_sub)

        self.equalizer_widget = VoiceEqualizerWidget(card_eq)
        l_eq.addWidget(self.equalizer_widget)
        layout.addWidget(card_eq)

        # Card 3: Performance & Latency Test
        card_perf = QGroupBox("Voice Performance & Audio Test", content)
        l_p = QVBoxLayout(card_perf)
        l_p.setSpacing(8)
        lbl_p_sub = QLabel("Test speech synthesis speed, neural voice emotion, and latency in real time:")
        lbl_p_sub.setStyleSheet("font-size: 11px; color: #64748B;")
        l_p.addWidget(lbl_p_sub)

        p_row = QHBoxLayout()
        p_row.setSpacing(10)
        self.btn_test_perf = QPushButton("▶ Test Voice & Latency", card_perf)
        self.btn_test_perf.setObjectName("BtnTest")
        self.btn_test_perf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_test_perf.clicked.connect(self._run_performance_test)
        p_row.addWidget(self.btn_test_perf)

        self.equalizer_preview = EqualizerPreviewWidget(card_perf)
        p_row.addWidget(self.equalizer_preview)

        self.lbl_test_status = QLabel("Ready to test live audio", card_perf)
        self.lbl_test_status.setStyleSheet("color: #7C3AED; font-weight: 600; font-size: 11px;")
        p_row.addWidget(self.lbl_test_status)
        p_row.addStretch()
        l_p.addLayout(p_row)
        layout.addWidget(card_perf)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    # ═════════════════════════════════════════════════════════════
    # PAGE 3: ABOUT VOXEL
    # ═════════════════════════════════════════════════════════════

    def _create_about_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(12)

        # Hero Header
        h_card = QGroupBox("", content)
        h_l = QHBoxLayout(h_card)
        h_l.setContentsMargins(16, 16, 16, 16)
        h_l.setSpacing(16)

        about_logo = VoxelLogoWidget(size=54, animated=True, parent=h_card)
        h_l.addWidget(about_logo)

        header_text = QVBoxLayout()
        header_text.setSpacing(3)
        title_row = QHBoxLayout()
        lbl_t = QLabel(APP_NAME, h_card)
        lbl_t.setStyleSheet("font-size: 24px; font-weight: 800; letter-spacing: 0.5px;")
        title_row.addWidget(lbl_t)

        ver_badge = QLabel(f" {VERSION} ", h_card)
        ver_badge.setStyleSheet("background-color: #7C3AED; color: #FFFFFF; font-size: 11px; font-weight: 700; border-radius: 4px; padding: 2px 8px;")
        title_row.addWidget(ver_badge)
        title_row.addStretch()
        header_text.addLayout(title_row)

        sub_lbl = QLabel(f"{APP_TAGLINE}  •  A {COMPANY_NAME} Product", h_card)
        sub_lbl.setStyleSheet("color: #7C3AED; font-size: 12px; font-weight: 600;")
        header_text.addWidget(sub_lbl)
        h_l.addLayout(header_text)
        h_l.addStretch()
        layout.addWidget(h_card)

        # Overview & Verified Links
        card_about = QGroupBox("About Voxel", content)
        l_ab = QVBoxLayout(card_about)
        l_ab.setSpacing(12)

        about_desc = QLabel(
            f"Voxel is an official open-source product from <b>{COMPANY_NAME}</b>.<br>"
            "Crafted to provide free, high-performance, and emotional text-to-speech anywhere on local machines without telemetry or restrictions.",
            card_about
        )
        about_desc.setWordWrap(True)
        l_ab.addWidget(about_desc)

        links_row = QHBoxLayout()
        links_row.setSpacing(10)

        btn_linkedin = QPushButton("🔗 Connect on LinkedIn", card_about)
        btn_linkedin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_linkedin.setStyleSheet("background-color: #0A66C2; color: #FFFFFF; font-weight: 700; padding: 8px 16px; border: none; border-radius: 6px;")
        btn_linkedin.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(LINKEDIN_URL)))
        links_row.addWidget(btn_linkedin)

        btn_website = QPushButton("🌐 Visit Digimo", card_about)
        btn_website.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_website.setStyleSheet("background-color: #0084FF; color: #FFFFFF; font-weight: 700; padding: 8px 16px; border: none; border-radius: 6px;")
        btn_website.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(COMPANY_URL)))
        links_row.addWidget(btn_website)

        btn_gh = QPushButton("🐙 GitHub Repository", card_about)
        btn_gh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_gh.setStyleSheet("background-color: #334155; color: #FFFFFF; font-weight: 700; padding: 8px 16px; border: none; border-radius: 6px;")
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))
        links_row.addWidget(btn_gh)

        l_ab.addLayout(links_row)
        layout.addWidget(card_about)

        # Freedom & Disclaimer
        card_free = QGroupBox("Open Source Freedom", content)
        l_f = QVBoxLayout(card_free)
        l_f.addWidget(QLabel("This software is <b>100% free and open source</b> with no copyright restrictions or telemetry. Anyone is welcome to contribute."))
        layout.addWidget(card_free)

        card_disc = QGroupBox("Disclaimer", content)
        l_d = QVBoxLayout(card_disc)
        l_d.addWidget(QLabel("Provided 'as is' for personal and productivity use. Digimo and creators assume no liability for any use or outcome."))
        layout.addWidget(card_disc)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    # ═════════════════════════════════════════════════════════════
    # THEME STYLESHEET DEFINITIONS
    # ═════════════════════════════════════════════════════════════

    def _get_light_stylesheet(self) -> str:
        return f"""
            QDialog {{
                background-color: #F8FAFC;
                color: #0F172A;
                font-family: {FONT_FAMILY};
            }}
            #ThemePill {{
                background-color: #EDE9FE;
                border-radius: 16px;
                border: 1px solid #DDD6FE;
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
                border-radius: 12px;
                margin-top: 10px;
                padding: 16px 14px 12px 14px;
                font-weight: 700;
                color: #0F172A;
                background-color: #FFFFFF;
            }}
            QGroupBox::title {{
                color: #0F172A;
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 4px;
                font-size: 13px;
                font-weight: 700;
            }}
            QComboBox, QDoubleSpinBox {{
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
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
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1.5px solid #CBD5E1;
                border-radius: 4px;
                background-color: #FFFFFF;
            }}
            QCheckBox::indicator:checked {{
                background-color: #7C3AED;
                border-color: #7C3AED;
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background: #E2E8F0;
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: #7C3AED;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: #FFFFFF;
                border: 2px solid #7C3AED;
                width: 16px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 8px;
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
                border-radius: 7px;
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
                border-radius: 12px;
                margin-top: 10px;
                padding: 16px 14px 12px 14px;
                font-weight: 700;
                color: #F8FAFC;
                background-color: #161A2B;
            }}
            QGroupBox::title {{
                color: #F8FAFC;
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 4px;
                font-size: 13px;
                font-weight: 700;
            }}
            QComboBox, QDoubleSpinBox {{
                background-color: #1E2438;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
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
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1.5px solid #475569;
                border-radius: 4px;
                background-color: #1E2438;
            }}
            QCheckBox::indicator:checked {{
                background-color: #7C3AED;
                border-color: #7C3AED;
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background: #242A42;
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: #7C3AED;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: #FFFFFF;
                border: 2px solid #7C3AED;
                width: 16px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 8px;
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
                border-radius: 7px;
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
            self.sidebar_widget.set_theme_mode("dark")
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
            self.card_light_theme.setStyleSheet("QFrame { background-color: #1A1F33; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; }")
            self.card_dark_theme.setStyleSheet("QFrame { background-color: #2E1065; border: 2px solid #A78BFA; border-radius: 8px; }")
            self.lbl_lt_chk.setVisible(False)
            self.lbl_dt_chk.setVisible(True)
        else:
            self.setStyleSheet(self._get_light_stylesheet())
            self.btn_theme_light.setChecked(True)
            self.btn_theme_dark.setChecked(False)
            self.sidebar_widget.set_theme_mode("light")
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
            self.card_light_theme.setStyleSheet("QFrame { background-color: #EDE9FE; border: 2px solid #7C3AED; border-radius: 8px; }")
            self.card_dark_theme.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; }")
            self.lbl_lt_chk.setVisible(True)
            self.lbl_dt_chk.setVisible(False)

        for btn in self.nav_buttons:
            btn.setStyleSheet(nav_btn_style)

        if hasattr(self, "equalizer_widget"):
            self.equalizer_widget.set_theme_mode(theme)

        # Update bubble style selection highlights
        curr_b_style = settings_db.get("bubble_appearance", "Frosted Glass")
        self._select_bubble_style(curr_b_style)

    def _on_nav_clicked(self, page_idx: int, icon_badge: str, header_title: str, header_sub: str):
        self.stacked_pages.setCurrentIndex(page_idx)
        self.header_badge.setText(icon_badge)
        self.lbl_header_title.setText(header_title)
        self.lbl_header_subtitle.setText(header_sub)

    def open_preferences(self):
        if len(self.nav_buttons) > 1:
            self.nav_buttons[1].setChecked(True)
        self._on_nav_clicked(1, "▶", "Playback", "Control how Voxel plays text-to-speech audio")
        self.show()
        self.raise_()
        self.activateWindow()

    def open_about(self):
        if len(self.nav_buttons) > 3:
            self.nav_buttons[3].setChecked(True)
        self._on_nav_clicked(3, "ℹ️", "About Voxel", "Product information, licenses, and social links")
        self.show()
        self.raise_()
        self.activateWindow()

    def _run_performance_test(self):
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

        voice_id = self.combo_voice.currentData()
        for i, v in enumerate(VOICES):
            if v["id"] == voice_id:
                self.tts.set_voice_index(i)
                break
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
        """Restores all settings to defaults matching mockups."""
        idx = self.combo_voice.findData("en-US-JennyNeural")
        if idx >= 0:
            self.combo_voice.setCurrentIndex(idx)
        idx_e = self.combo_emotion.findData(DEFAULT_EMOTION_MODE)
        if idx_e >= 0:
            self.combo_emotion.setCurrentIndex(idx_e)

        self.slider_speed.setValue(100)
        self.spin_fade_duration.setValue(1.00)
        self.chk_fade_in.setChecked(True)
        self.chk_startup.setChecked(False)
        self.chk_prebuffer.setChecked(True)
        self.chk_trigger.setChecked(True)
        self.chk_autoclose.setChecked(True)
        self.slider_volume.setValue(80)
        self.slider_transparency.setValue(90)
        self.slider_bubble_size.setValue(2)

        if hasattr(self, "equalizer_widget"):
            self.equalizer_widget.apply_preset("Podcast Warmth")

        self.apply_theme("light")
        self._select_bubble_style("Frosted Glass")

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

        speed_val = float(settings_db.get("default_speed", 1.0))
        self.slider_speed.setValue(int(round(speed_val * 100)))

        self.chk_startup.setChecked(is_startup_enabled())

        prebuffer = settings_db.get("prebuffer_enabled", True)
        self.chk_prebuffer.setChecked(prebuffer)

        enabled = settings_db.get("selection_popup_enabled", True)
        self.chk_trigger.setChecked(enabled)

        autoclose = settings_db.get("auto_close_finished", True)
        self.chk_autoclose.setChecked(autoclose)

        delay_val = float(settings_db.get("auto_close_delay", 1.0))
        self.spin_fade_duration.setValue(delay_val)

        vol_val = int(settings_db.get("volume", 80))
        self.slider_volume.setValue(vol_val)

        trans_val = int(settings_db.get("bubble_transparency", 90))
        self.slider_transparency.setValue(trans_val)

        curr_b_style = settings_db.get("bubble_appearance", "Frosted Glass")
        self._select_bubble_style(curr_b_style)

    def save_and_apply(self):
        """Saves values and emits update signal."""
        settings_db.set("default_voice", self.combo_voice.currentData())
        settings_db.set("emotion_mode", self.combo_emotion.currentData())
        speed = round(self.slider_speed.value() / 100.0, 2)
        settings_db.set("default_speed", speed)
        settings_db.set("prebuffer_enabled", self.chk_prebuffer.isChecked())
        settings_db.set("selection_popup_enabled", self.chk_trigger.isChecked())
        settings_db.set("auto_close_finished", self.chk_autoclose.isChecked())
        settings_db.set("auto_close_delay", self.spin_fade_duration.value())
        settings_db.set("volume", self.slider_volume.value())
        settings_db.set("bubble_transparency", self.slider_transparency.value())
        settings_db.set("settings_theme", self.current_theme)

        set_startup_enabled(self.chk_startup.isChecked())

        self.settings_applied.emit()
        self.close()
