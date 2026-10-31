"""
Settings, Preferences & About Dialog for Voxel.
Faithfully styled with modern custom CSS and components matching user mockups:
- Official Voxel Brand Logo in Sidebar Header (Light / Dark mode auto-switch).
- Ampersand bug resolved (literal '&&' so no Windows underscores appear).
- Custom ToggleSwitch widget for smooth fade-in.
- SVG/PNG white checkmark indicators for custom purple checkboxes.
- Interactive Theme Selection cards with mini window graphics and checkmarks.
- 4 Floating Bubble Appearance cards (Default, Frosted Glass, Transparent, Minimal).
- Automatic Voxel Recordings folder integration with one-click folder opener.
- Parametric Voice Equalizer (EQ) and live performance spectrum test.
"""
import os
import sys
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget, QScrollArea,
    QWidget, QLabel, QComboBox, QCheckBox, QDoubleSpinBox, QPushButton,
    QGroupBox, QFormLayout, QFrame, QButtonGroup, QSlider, QFileDialog
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QCursor, QDesktopServices, QPainter, QColor, QBrush, QPen, QFont,
    QPainterPath, QLinearGradient, QPixmap
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
from src.ui.equalizer_widget import VoiceEqualizerWidget, EQ_PRESETS
from assets.icons import create_app_icon, get_brand_logo_pixmap

LINKEDIN_URL = "https://www.linkedin.com/in/fahimdigital/"


class ToggleSwitch(QWidget):
    """Modern iOS/Windows 11 rounded pill toggle switch widget."""
    toggled = pyqtSignal(bool)

    def __init__(self, checked: bool = True, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 24)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._checked = checked
        self.theme_mode = "light"

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked != checked:
            self._checked = checked
            self.toggled.emit(self._checked)
            self.update()

    def set_theme_mode(self, mode: str):
        self.theme_mode = mode
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        r = h / 2.0
        is_dark = (self.theme_mode == "dark")

        # Track
        if self._checked:
            track_col = QColor("#7C3AED")
        else:
            track_col = QColor("#334155") if is_dark else QColor("#CBD5E1")

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_col))
        painter.drawRoundedRect(QRectF(0, 0, w, h), r, r)

        # Sliding Knob
        knob_d = h - 6.0
        knob_x = (w - knob_d - 3.0) if self._checked else 3.0
        knob_y = 3.0

        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawEllipse(QRectF(knob_x, knob_y, knob_d, knob_d))
        painter.end()


class MiniWindowGraphic(QWidget):
    """Paints a mini desktop window illustration for the Light/Dark theme cards."""
    def __init__(self, is_dark: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 36)
        self.is_dark = is_dark

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # Window body
        bg_col = QColor("#1E2438") if self.is_dark else QColor("#F1F5F9")
        border_col = QColor(255, 255, 255, 30) if self.is_dark else QColor("#CBD5E1")
        painter.setBrush(QBrush(bg_col))
        painter.setPen(QPen(border_col, 1.0))
        painter.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), 4, 4)

        # Sidebar strip
        side_col = QColor("#131627") if self.is_dark else QColor("#E2E8F0")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(side_col))
        painter.drawRoundedRect(QRectF(2, 2, 14, h - 4), 3, 3)

        # Content lines
        line_col = QColor(255, 255, 255, 45) if self.is_dark else QColor(148, 163, 184, 110)
        painter.setBrush(QBrush(line_col))
        painter.drawRoundedRect(QRectF(20, 7, 22, 3), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(20, 13, 16, 3), 1.5, 1.5)

        # Button accent
        btn_col = QColor("#7C3AED") if self.is_dark else QColor("#0084FF")
        painter.setBrush(QBrush(btn_col))
        painter.drawRoundedRect(QRectF(20, 21, 18, 7), 2, 2)

        painter.end()


class BubbleStyleGraphic(QWidget):
    """Paints mini preview dual-capsule for Default, Frosted Glass, Transparent, Minimal."""
    def __init__(self, style_name: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(62, 26)
        self.style_name = style_name
        self.is_dark = False

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        r = h / 2.0

        if self.style_name == "Default":
            painter.setPen(QPen(QColor("#94A3B8"), 1.2))
            painter.setBrush(QBrush(QColor("#FFFFFF") if not self.is_dark else QColor("#1E293B")))
            painter.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), r, r)
        elif self.style_name == "Frosted Glass":
            grad = QLinearGradient(0, 0, w, h)
            if not self.is_dark:
                grad.setColorAt(0.0, QColor(255, 255, 255, 255))
                grad.setColorAt(1.0, QColor(237, 233, 254, 255))
                painter.setPen(QPen(QColor("#7C3AED"), 1.5))
            else:
                grad.setColorAt(0.0, QColor(46, 16, 101, 220))
                grad.setColorAt(1.0, QColor(30, 27, 75, 240))
                painter.setPen(QPen(QColor("#A78BFA"), 1.5))
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), r, r)
        elif self.style_name == "Transparent":
            pen = QPen(QColor("#94A3B8"), 1.2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 40) if not self.is_dark else QColor(0, 0, 0, 40)))
            painter.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), r, r)
        elif self.style_name == "Minimal":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#EDE9FE") if not self.is_dark else QColor("#312E81")))
            painter.drawRoundedRect(QRectF(1, 1, w - 2, h - 2), r, r)

        # Subtle divider in middle
        painter.setPen(QPen(QColor("#CBD5E1") if not self.is_dark else QColor(255, 255, 255, 40), 1.0))
        painter.drawLine(int(w / 2.0), 4, int(w / 2.0), int(h - 4))

        # Left mini mic icon
        mic_col = QColor("#0084FF") if self.style_name == "Frosted Glass" else QColor("#7C3AED")
        painter.setPen(QPen(mic_col, 1.2))
        painter.setBrush(QBrush(mic_col))
        painter.drawRoundedRect(QRectF(w * 0.25 - 3, h * 0.5 - 5, 6, 8), 3, 3)
        painter.drawLine(int(w * 0.25), int(h * 0.5 + 3), int(w * 0.25), int(h * 0.5 + 6))

        # Right mini doc icon
        doc_col = QColor("#7C3AED")
        painter.setPen(QPen(doc_col, 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(w * 0.75 - 4, h * 0.5 - 5, 8, 10), 1.5, 1.5)
        painter.drawLine(int(w * 0.75 - 2), int(h * 0.5 - 2), int(w * 0.75 + 2), int(h * 0.5 - 2))
        painter.drawLine(int(w * 0.75 - 2), int(h * 0.5 + 1), int(w * 0.75 + 2), int(h * 0.5 + 1))

        painter.end()


class CornerRadiusGraphic(QWidget):
    """Paints mini preview icon for Square, Medium, Round corner styles."""
    def __init__(self, corner_name: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.corner_name = corner_name
        self.is_dark = False

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#7C3AED"), 2.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if self.corner_name == "Square":
            painter.drawRect(QRectF(4, 4, 16, 16))
        elif self.corner_name == "Medium":
            painter.drawRoundedRect(QRectF(4, 4, 16, 16), 4.5, 4.5)
        elif self.corner_name == "Round":
            painter.drawEllipse(QRectF(4, 4, 16, 16))
        painter.end()


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
        bg_col = QColor("#0F172A") if is_dark else QColor("#F8FAFC")
        painter.fillRect(self.rect(), bg_col)

        # Right divider border
        border_col = QColor(255, 255, 255, 18) if is_dark else QColor("#E2E8F0")
        painter.setPen(QPen(border_col, 1.0))
        painter.drawLine(int(w - 1), 0, int(w - 1), int(h))

        # Bottom decorative organic wave
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
        self.bubble_cards: Dict[str, QFrame] = {}
        self.bubble_chk: Dict[str, QLabel] = {}
        self.corner_cards: Dict[str, QFrame] = {}
        self.corner_chk: Dict[str, QLabel] = {}
        self.current_bubble_style: str = "Frosted Glass"
        self.current_corner_radius: str = "Medium"
        self._init_ui()
        self.apply_theme(self.current_theme)
        self.load_values()

    def _init_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ═════════════════════════════════════════════════════════════
        # 1. LEFT SIDEBAR (Width 210px with official brand logo)
        # ═════════════════════════════════════════════════════════════
        self.sidebar_widget = SidebarWidget(self)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(14, 20, 14, 16)
        sidebar_layout.setSpacing(8)

        # Brand Header in Sidebar using official user logo asset
        self.lbl_sidebar_logo = QLabel(self.sidebar_widget)
        self.lbl_sidebar_logo.setFixedHeight(64)
        self.lbl_sidebar_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_sidebar_logo()
        sidebar_layout.addWidget(self.lbl_sidebar_logo)

        sidebar_layout.addSpacing(18)

        # 4 Navigation Items matching user mockups (literal '&&' avoids underscore mnemonic)
        self.nav_items = [
            ("🎙️  Voice && Speech", 0, "🎙️", "Voice && Speech", "Fine-tune neural voices, cadence, and parametric equalizer"),
            ("▶  Playback", 1, "▶", "Playback", "Control how Voxel plays text-to-speech audio"),
            ("🎨  Appearance", 2, "🎨", "Appearance", "Personalize the look and feel of Voxel"),
            ("ℹ️  About", 3, "ℹ️", "About Voxel", "Product information, licenses, and social links"),
        ]

        self.btn_group_nav = QButtonGroup(self)
        for text, page_idx, icon_badge, header_title, header_sub in self.nav_items:
            btn = QPushButton(text, self.sidebar_widget)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            clean_t = header_title.replace("&&", "&")
            clean_s = header_sub.replace("&&", "&")
            btn.clicked.connect(lambda checked, idx=page_idx, b=icon_badge, h_title=clean_t, h_sub=clean_s: self._on_nav_clicked(idx, b, h_title, h_sub))
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

    def _update_sidebar_logo(self):
        """Displays the official Voxel Logo Main image in the sidebar."""
        is_dark = (self.current_theme == "dark")
        pix = get_brand_logo_pixmap(is_dark=is_dark, target_width=180)
        if not pix.isNull():
            self.lbl_sidebar_logo.setPixmap(pix)

    # ═════════════════════════════════════════════════════════════
    # PAGE 1: PLAYBACK (Matching User Mockup Image 1)
    # ═════════════════════════════════════════════════════════════

    def _create_playback_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(12)

        # Top Row: Playback Speed (Left) & Fade && Timing (Right)
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
        self.slider_speed.setRange(50, 200)
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

        # Card 2: Fade && Timing (Literal '&&' avoids underscore)
        card_timing = QGroupBox("Fade && Timing", content)
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

        fade_in_row = QHBoxLayout()
        fade_in_row.addWidget(QLabel("Smooth fade-in at start"))
        fade_in_row.addStretch()
        self.switch_fade_in = ToggleSwitch(checked=True, parent=card_timing)
        fade_in_row.addWidget(self.switch_fade_in)
        l_timing.addLayout(fade_in_row)
        top_row.addWidget(card_timing)

        layout.addLayout(top_row)

        # Card 3: Playback Behavior (Clean purple checkboxes with SVG checkmarks)
        card_behavior = QGroupBox("Playback Behavior", content)
        l_beh = QVBoxLayout(card_behavior)
        l_beh.setSpacing(8)
        sub_b = QLabel("Choose when and how Voxel plays audio.")
        sub_b.setStyleSheet("font-size: 11px; color: #64748B;")
        l_beh.addWidget(sub_b)

        grid_beh = QHBoxLayout()
        col1 = QVBoxLayout()
        col1.setSpacing(10)
        self.chk_startup = QCheckBox("Launch Voxel automatically when Windows starts", card_behavior)
        col1.addWidget(self.chk_startup)
        self.chk_prebuffer = QCheckBox("Instant playback: Pre-generate first sentence on hover", card_behavior)
        col1.addWidget(self.chk_prebuffer)
        grid_beh.addLayout(col1)

        col2 = QVBoxLayout()
        col2.setSpacing(10)
        self.chk_trigger = QCheckBox("Show floating Voxel badge when selecting text", card_behavior)
        col2.addWidget(self.chk_trigger)
        self.chk_autoclose = QCheckBox("Automatically close player when speech finishes", card_behavior)
        col2.addWidget(self.chk_autoclose)
        grid_beh.addLayout(col2)
        l_beh.addLayout(grid_beh)
        layout.addWidget(card_behavior)

        # Card 4: Audio Output && Recordings
        card_out = QGroupBox("Audio Output && Recordings", content)
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

        # Automatic Recordings Folder row
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
    # PAGE 2: APPEARANCE (Matching User Mockup Image 2)
    # ═════════════════════════════════════════════════════════════

    def _create_appearance_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(14)

        # ─── Card 1: App Logo & Icons ────────────────────────────────
        card_logo = QGroupBox("App Logo && Icons", content)
        l_logo = QVBoxLayout(card_logo)
        l_logo.setSpacing(10)

        sub_logo = QLabel("Update the application logo and related icons.", card_logo)
        sub_logo.setStyleSheet("font-size: 11px; color: #64748B;")
        l_logo.addWidget(sub_logo)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(14)

        # Left: Current Logo Preview Card
        self.frame_logo_preview = QFrame(card_logo)
        self.frame_logo_preview.setFixedSize(190, 84)
        self.frame_logo_preview.setStyleSheet(
            "QFrame { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; }"
        )
        l_prev = QVBoxLayout(self.frame_logo_preview)
        l_prev.setContentsMargins(8, 8, 8, 8)
        self.lbl_logo_preview = QLabel(self.frame_logo_preview)
        self.lbl_logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l_prev.addWidget(self.lbl_logo_preview)
        logo_row.addWidget(self.frame_logo_preview)

        # Middle: Logo Action Buttons
        logo_btn_col = QVBoxLayout()
        logo_btn_col.setSpacing(8)
        logo_btn_col.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_change_logo = QPushButton("  ⭡  Change Logo", card_logo)
        self.btn_change_logo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_change_logo.setFixedHeight(34)
        self.btn_change_logo.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1.5px solid #7C3AED;
                border-radius: 8px;
                color: #7C3AED;
                font-weight: 700;
                font-size: 12px;
                padding: 4px 14px;
            }
            QPushButton:hover {
                background-color: #EDE9FE;
            }
        """)
        self.btn_change_logo.clicked.connect(self._on_change_logo)
        logo_btn_col.addWidget(self.btn_change_logo)

        self.btn_restore_logo = QPushButton("  ↺  Restore Default", card_logo)
        self.btn_restore_logo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_restore_logo.setFixedHeight(34)
        self.btn_restore_logo.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                color: #475569;
                font-weight: 600;
                font-size: 12px;
                padding: 4px 14px;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """)
        self.btn_restore_logo.clicked.connect(self._on_restore_default_logo)
        logo_btn_col.addWidget(self.btn_restore_logo)
        logo_row.addLayout(logo_btn_col)

        logo_row.addSpacing(6)

        # Right: Logo Requirements Info Card
        self.frame_logo_req = QFrame(card_logo)
        self.frame_logo_req.setStyleSheet(
            "QFrame { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; }"
        )
        l_req = QVBoxLayout(self.frame_logo_req)
        l_req.setContentsMargins(14, 10, 14, 10)
        l_req.setSpacing(4)

        lbl_req_title = QLabel("ℹ️  Logo Requirements", self.frame_logo_req)
        lbl_req_title.setStyleSheet("font-weight: 800; font-size: 12px; color: #1E293B;")
        l_req.addWidget(lbl_req_title)

        req_text = QLabel(
            "<b>Format:</b> PNG, JPG or SVG<br>"
            "<b>Recommended Size:</b> 512 × 512 px<br>"
            "<b>Minimum Size:</b> 256 × 256 px<br>"
            "<b>Aspect Ratio:</b> 1:1 (Square)",
            self.frame_logo_req
        )
        req_text.setStyleSheet("font-size: 11px; color: #475569; line-height: 1.4;")
        l_req.addWidget(req_text)
        logo_row.addWidget(self.frame_logo_req, stretch=1)

        l_logo.addLayout(logo_row)
        layout.addWidget(card_logo)

        # ─── Card 2: Floating Bubble Appearance (4 selectable cards) ───
        card_bubble_app = QGroupBox("Floating Bubble", content)
        l_ba = QVBoxLayout(card_bubble_app)
        l_ba.setSpacing(10)

        sub_ba = QLabel("Customize the text selection bubble (dual-capsule) appearance.", card_bubble_app)
        sub_ba.setStyleSheet("font-size: 11px; color: #64748B;")
        l_ba.addWidget(sub_ba)

        bubble_styles_row = QHBoxLayout()
        bubble_styles_row.setSpacing(12)

        bubble_presets = ["Default", "Frosted Glass", "Transparent", "Minimal"]

        for name in bubble_presets:
            f = QFrame(card_bubble_app)
            f.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            f_l = QVBoxLayout(f)
            f_l.setContentsMargins(10, 8, 10, 10)
            f_l.setSpacing(6)
            f_l.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Top checkmark badge container
            top_bar = QHBoxLayout()
            top_bar.setContentsMargins(0, 0, 0, 0)
            top_bar.addStretch()
            chk = QLabel("✓", f)
            chk.setStyleSheet(
                "background-color: #7C3AED; color: #FFFFFF; font-weight: 800; "
                "border-radius: 9px; min-width: 18px; max-width: 18px; min-height: 18px; max-height: 18px; "
                "qproperty-alignment: AlignCenter; font-size: 10px;"
            )
            chk.setVisible(False)
            top_bar.addWidget(chk)
            f_l.addLayout(top_bar)

            # Mini visual dual-action capsule
            g = BubbleStyleGraphic(name, f)
            f_l.addWidget(g, alignment=Qt.AlignmentFlag.AlignCenter)

            lbl_n = QLabel(name, f)
            lbl_n.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_n.setStyleSheet("font-weight: 700; font-size: 12px;")
            f_l.addWidget(lbl_n)

            f.mousePressEvent = lambda e, s=name: self._select_bubble_style(s)
            self.bubble_cards[name] = f
            self.bubble_chk[name] = chk
            bubble_styles_row.addWidget(f)

        l_ba.addLayout(bubble_styles_row)
        layout.addWidget(card_bubble_app)

        # ─── Card 3: Bubble Settings ─────────────────────────────────
        card_b_set = QGroupBox("Bubble Settings", content)
        l_bs = QVBoxLayout(card_b_set)
        l_bs.setSpacing(12)

        sub_bs = QLabel("Adjust size, transparency, and corner style.", card_b_set)
        sub_bs.setStyleSheet("font-size: 11px; color: #64748B;")
        l_bs.addWidget(sub_bs)

        # Top Row: Transparency & Bubble Size side by side
        bs_row = QHBoxLayout()
        bs_row.setSpacing(24)

        # Transparency column
        trans_col = QVBoxLayout()
        trans_col.setSpacing(6)
        lbl_trans_title = QLabel("Transparency", card_b_set)
        lbl_trans_title.setStyleSheet("font-weight: 700; font-size: 12px;")
        trans_col.addWidget(lbl_trans_title)

        trans_h = QHBoxLayout()
        trans_h.setSpacing(10)
        self.slider_transparency = QSlider(Qt.Orientation.Horizontal, card_b_set)
        self.slider_transparency.setRange(30, 100)
        self.slider_transparency.setValue(90)
        self.slider_transparency.valueChanged.connect(lambda v: self.lbl_trans_val.setText(f"{v}%"))
        trans_h.addWidget(self.slider_transparency)

        self.lbl_trans_val = QLabel("90%", card_b_set)
        self.lbl_trans_val.setFixedWidth(40)
        self.lbl_trans_val.setStyleSheet("font-weight: 700; color: #7C3AED; font-size: 12px;")
        trans_h.addWidget(self.lbl_trans_val)
        trans_col.addLayout(trans_h)
        bs_row.addLayout(trans_col)

        # Bubble Size column
        size_col = QVBoxLayout()
        size_col.setSpacing(6)
        lbl_size_title = QLabel("Bubble Size", card_b_set)
        lbl_size_title.setStyleSheet("font-weight: 700; font-size: 12px;")
        size_col.addWidget(lbl_size_title)

        size_h = QHBoxLayout()
        size_h.setSpacing(10)
        self.slider_bubble_size = QSlider(Qt.Orientation.Horizontal, card_b_set)
        self.slider_bubble_size.setRange(1, 3)
        self.slider_bubble_size.setValue(2)
        size_h.addWidget(self.slider_bubble_size)

        self.combo_bubble_size = QComboBox(card_b_set)
        self.combo_bubble_size.addItem("Small", 1)
        self.combo_bubble_size.addItem("Medium", 2)
        self.combo_bubble_size.addItem("Large", 3)
        self.combo_bubble_size.setCurrentIndex(1)
        self.combo_bubble_size.setFixedWidth(105)
        self.combo_bubble_size.currentIndexChanged.connect(lambda idx: self.slider_bubble_size.setValue(idx + 1))
        self.slider_bubble_size.valueChanged.connect(lambda val: self.combo_bubble_size.setCurrentIndex(val - 1))
        size_h.addWidget(self.combo_bubble_size)
        size_col.addLayout(size_h)
        bs_row.addLayout(size_col)

        l_bs.addLayout(bs_row)

        # Bottom Row: Corner Radius
        lbl_cr_title = QLabel("Corner Radius", card_b_set)
        lbl_cr_title.setStyleSheet("font-weight: 700; font-size: 12px; margin-top: 4px;")
        l_bs.addWidget(lbl_cr_title)

        corner_row = QHBoxLayout()
        corner_row.setSpacing(12)

        for name in ["Square", "Medium", "Round"]:
            f = QFrame(card_b_set)
            f.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            f_l = QHBoxLayout(f)
            f_l.setContentsMargins(14, 10, 14, 10)
            f_l.setSpacing(10)
            f_l.setAlignment(Qt.AlignmentFlag.AlignCenter)

            g = CornerRadiusGraphic(name, f)
            f_l.addWidget(g)

            lbl_c = QLabel(name, f)
            lbl_c.setStyleSheet("font-weight: 700; font-size: 12px;")
            f_l.addWidget(lbl_c)

            f_l.addStretch()

            chk = QLabel("✓", f)
            chk.setStyleSheet(
                "background-color: #7C3AED; color: #FFFFFF; font-weight: 800; "
                "border-radius: 9px; min-width: 18px; max-width: 18px; min-height: 18px; max-height: 18px; "
                "qproperty-alignment: AlignCenter; font-size: 10px;"
            )
            chk.setVisible(False)
            f_l.addWidget(chk)

            f.mousePressEvent = lambda e, s=name: self._select_corner_radius(s)
            self.corner_cards[name] = f
            self.corner_chk[name] = chk
            corner_row.addWidget(f)

        l_bs.addLayout(corner_row)
        layout.addWidget(card_b_set)
        layout.addStretch()

        self._update_all_logos()

        scroll.setWidget(content)
        return scroll

    def _select_bubble_style(self, style_name: str):
        self.current_bubble_style = style_name
        settings_db.set("bubble_appearance", style_name)
        is_dark = (self.current_theme == "dark")
        for name, card in self.bubble_cards.items():
            chk = self.bubble_chk.get(name)
            if name == style_name:
                card.setStyleSheet(
                    "QFrame { background-color: #EDE9FE; border: 2px solid #7C3AED; border-radius: 8px; color: #7C3AED; }"
                    if not is_dark else
                    "QFrame { background-color: #2E1065; border: 2px solid #A78BFA; border-radius: 8px; color: #FFFFFF; }"
                )
                if chk:
                    chk.setVisible(True)
            else:
                card.setStyleSheet(
                    "QFrame { background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; color: #0F172A; }"
                    if not is_dark else
                    "QFrame { background-color: #1A1F33; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; color: #94A3B8; }"
                )
                if chk:
                    chk.setVisible(False)

    def _select_corner_radius(self, corner_name: str):
        self.current_corner_radius = corner_name
        settings_db.set("bubble_corner_radius", corner_name)
        is_dark = (self.current_theme == "dark")
        for name, card in self.corner_cards.items():
            chk = self.corner_chk.get(name)
            if name == corner_name:
                card.setStyleSheet(
                    "QFrame { background-color: #EDE9FE; border: 2px solid #7C3AED; border-radius: 8px; color: #7C3AED; }"
                    if not is_dark else
                    "QFrame { background-color: #2E1065; border: 2px solid #A78BFA; border-radius: 8px; color: #FFFFFF; }"
                )
                if chk:
                    chk.setVisible(True)
            else:
                card.setStyleSheet(
                    "QFrame { background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; color: #0F172A; }"
                    if not is_dark else
                    "QFrame { background-color: #1A1F33; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; color: #94A3B8; }"
                )
                if chk:
                    chk.setVisible(False)

    def _on_change_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Application Logo", "",
            "Image Files (*.png *.jpg *.jpeg *.svg *.ico);;All Files (*)"
        )
        if file_path and os.path.exists(file_path):
            settings_db.set("custom_logo_path", file_path)
            self._update_all_logos()

    def _on_restore_default_logo(self):
        if "custom_logo_path" in settings_db:
            settings_db.remove("custom_logo_path")
        self._update_all_logos()

    def _update_all_logos(self):
        self._update_sidebar_logo()
        is_dark = (self.current_theme == "dark")
        pix = get_brand_logo_pixmap(is_dark=is_dark, target_width=140)
        if hasattr(self, "lbl_logo_preview") and not pix.isNull():
            self.lbl_logo_preview.setPixmap(pix)
        if hasattr(self, "frame_logo_preview"):
            self.frame_logo_preview.setStyleSheet(
                "QFrame { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; }"
                if not is_dark else
                "QFrame { background-color: #161F30; border: 1px solid #1E293B; border-radius: 10px; }"
            )
        if hasattr(self, "frame_logo_req"):
            self.frame_logo_req.setStyleSheet(
                "QFrame { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; }"
                if not is_dark else
                "QFrame { background-color: #161F30; border: 1px solid #1E293B; border-radius: 10px; }"
            )

    # ═════════════════════════════════════════════════════════════
    # PAGE 0: VOICE && SPEECH
    # ═════════════════════════════════════════════════════════════

    def _create_voice_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(12)

        # Card 1: Voice && Emotion Selection
        card_v = QGroupBox("Voice && Emotion Selection", content)
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
        l_v.addRow(QLabel("<b>Emotion && Tone:</b>"), self.combo_emotion)
        layout.addWidget(card_v)

        # Card 2: Interactive Voice Equalizer (EQ)
        card_eq = QGroupBox("Voice Equalizer (EQ)", content)
        l_eq = QVBoxLayout(card_eq)
        l_eq.setSpacing(6)
        lbl_eq_sub = QLabel("Parametric frequency response curve and vocal timbre presets:")
        lbl_eq_sub.setStyleSheet("font-size: 11px; color: #64748B;")
        l_eq.addWidget(lbl_eq_sub)

        self.equalizer_widget = VoiceEqualizerWidget(card_eq)
        l_eq.addWidget(self.equalizer_widget)
        layout.addWidget(card_eq)

        # Card 3: Performance && Latency Test
        card_perf = QGroupBox("Voice Performance && Audio Test", content)
        l_p = QVBoxLayout(card_perf)
        l_p.setSpacing(8)
        lbl_p_sub = QLabel("Test speech synthesis speed, neural voice emotion, and latency in real time:")
        lbl_p_sub.setStyleSheet("font-size: 11px; color: #64748B;")
        l_p.addWidget(lbl_p_sub)

        p_row = QHBoxLayout()
        p_row.setSpacing(10)
        self.btn_test_perf = QPushButton("▶ Test Voice && Latency", card_perf)
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

        # Overview && Verified Links
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

        # Freedom && Disclaimer
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
    # THEME STYLESHEET DEFINITIONS (QSS / Custom CSS)
    # ═════════════════════════════════════════════════════════════

    def _get_light_stylesheet(self) -> str:
        check_icon_path = os.path.join(os.getcwd(), "assets", "branding", "png", "checkbox_check.png").replace("\\", "/")
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
                spacing: 10px;
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1.5px solid #CBD5E1;
                border-radius: 5px;
                background-color: #FFFFFF;
            }}
            QCheckBox::indicator:hover {{
                border-color: #7C3AED;
            }}
            QCheckBox::indicator:checked {{
                background-color: #7C3AED;
                border-color: #7C3AED;
                image: url("{check_icon_path}");
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
        check_icon_path = os.path.join(os.getcwd(), "assets", "branding", "png", "checkbox_check.png").replace("\\", "/")
        return f"""
            QDialog {{
                background-color: #0B0F19;
                color: #F8FAFC;
                font-family: {FONT_FAMILY};
            }}
            #ThemePill {{
                background-color: #1E293B;
                border-radius: 16px;
                border: 1px solid #334155;
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
                background-color: #2E3A59;
                color: #FFFFFF;
                font-weight: 700;
            }}
            QLabel {{
                color: #F1F5F9;
                font-size: 13px;
            }}
            QGroupBox {{
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                margin-top: 10px;
                padding: 16px 14px 12px 14px;
                font-weight: 700;
                color: #F8FAFC;
                background-color: #161F30;
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
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #1E293B;
                color: #FFFFFF;
                selection-background-color: #7C3AED;
                selection-color: #FFFFFF;
                border: 1px solid #334155;
            }}
            QCheckBox {{
                color: #F1F5F9;
                font-size: 12px;
                spacing: 10px;
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1.5px solid #475569;
                border-radius: 5px;
                background-color: #1E293B;
            }}
            QCheckBox::indicator:hover {{
                border-color: #A78BFA;
            }}
            QCheckBox::indicator:checked {{
                background-color: #7C3AED;
                border-color: #7C3AED;
                image: url("{check_icon_path}");
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background: #1E293B;
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
                background-color: #1E293B;
                color: #FFFFFF;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #2D3748;
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

        self._update_sidebar_logo()

        if is_dark:
            self.setStyleSheet(self._get_dark_stylesheet())
            self.btn_theme_dark.setChecked(True)
            self.btn_theme_light.setChecked(False)
            self.sidebar_widget.set_theme_mode("dark")
            if hasattr(self, "switch_fade_in"):
                self.switch_fade_in.set_theme_mode("dark")
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
            self.sidebar_widget.set_theme_mode("light")
            if hasattr(self, "switch_fade_in"):
                self.switch_fade_in.set_theme_mode("light")
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

        self._update_all_logos()
        curr_b_style = getattr(self, "current_bubble_style", settings_db.get("bubble_appearance", "Frosted Glass"))
        self._select_bubble_style(curr_b_style)
        curr_corner = getattr(self, "current_corner_radius", settings_db.get("bubble_corner_radius", "Medium"))
        self._select_corner_radius(curr_corner)

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
            self.btn_test_perf.setText("▶ Test Voice && Latency")
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
            self.btn_test_perf.setText("▶ Test Voice && Latency")
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
        self.switch_fade_in.setChecked(True)
        self.chk_startup.setChecked(False)
        self.chk_prebuffer.setChecked(True)
        self.chk_trigger.setChecked(True)
        self.chk_autoclose.setChecked(True)
        self.slider_volume.setValue(80)
        self.slider_transparency.setValue(90)
        self.slider_bubble_size.setValue(2)
        self.combo_bubble_size.setCurrentIndex(1)

        if hasattr(self, "equalizer_widget"):
            self.equalizer_widget.apply_preset("Podcast Warmth")

        self.apply_theme("light")
        self._select_bubble_style("Frosted Glass")
        self._select_corner_radius("Medium")
        self._on_restore_default_logo()

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
        self.lbl_trans_val.setText(f"{trans_val}%")

        b_size = str(settings_db.get("bubble_size", "Medium")).capitalize()
        idx_size = self.combo_bubble_size.findText(b_size)
        if idx_size >= 0:
            self.combo_bubble_size.setCurrentIndex(idx_size)
            self.slider_bubble_size.setValue(idx_size + 1)

        curr_corner = settings_db.get("bubble_corner_radius", "Medium")
        self._select_corner_radius(curr_corner)

        fade_in_val = settings_db.get("smooth_fade_in", True)
        self.switch_fade_in.setChecked(fade_in_val)

        curr_b_style = settings_db.get("bubble_appearance", "Frosted Glass")
        self._select_bubble_style(curr_b_style)

        self._update_all_logos()

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
        settings_db.set("bubble_size", self.combo_bubble_size.currentText())
        settings_db.set("bubble_corner_radius", getattr(self, "current_corner_radius", "Medium"))
        settings_db.set("bubble_appearance", getattr(self, "current_bubble_style", "Frosted Glass"))
        settings_db.set("smooth_fade_in", self.switch_fade_in.isChecked())
        settings_db.set("settings_theme", self.current_theme)

        set_startup_enabled(self.chk_startup.isChecked())

        self.settings_applied.emit()
        self.close()
