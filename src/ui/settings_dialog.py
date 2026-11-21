"""
Voxel Settings window (v2.0).

Clean card-based layout built from a few reusable pieces:
- Card / setting rows with a title on the left and the control on the right
- Animated ToggleSwitch for every on/off option (no raw checkboxes)
- Segmented controls for small choice sets (theme, bubble size, corners)
- "Read Text" page: paste or type any text and listen, for apps that block selection

All colors come from one palette per theme, so Light and Dark stay consistent.
Public API and settings keys are unchanged from v1.x.
"""
import os
import tempfile
from typing import Optional, List, Dict, Callable

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget, QScrollArea, QWidget,
    QLabel, QComboBox, QPushButton, QFrame, QButtonGroup, QSlider, QFileDialog,
    QPlainTextEdit, QSizePolicy, QApplication
)
from PyQt6.QtCore import QSize, Qt, QUrl, pyqtSignal, QTimer, QRectF, QPointF, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import (
    QGuiApplication, QCursor, QDesktopServices, QPainter, QColor, QBrush, QPen, QLinearGradient,
    QImage, QShortcut, QKeySequence, QFontMetrics
)

from src.config import (
    VOICES, EMOTION_MODES, DEFAULT_EMOTION_MODE, VERSION, GITHUB_URL, APP_NAME,
    FONT_FAMILY, IS_MAC, COMPANY_NAME, COMPANY_URL
)
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from src.utils.startup import is_startup_enabled, set_startup_enabled
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from src.utils.audio_recorder import get_recordings_dir, open_recordings_folder
from src.ui.equalizer_widget import VoiceEqualizerWidget
from assets.icons import create_app_icon, get_brand_logo_pixmap

LINKEDIN_URL = "https://www.linkedin.com/in/fahimdigital/"

from src.ui.design import PALETTES, FONT_STACK, resolve_theme, line_icon, THEME_PREFS


def _icon_file(name: str, color: str, draw: Callable[[QPainter], None]) -> str:
    """Renders a tiny 32px icon once into the temp folder and returns a QSS-safe path."""
    path = os.path.join(tempfile.gettempdir(), f"voxel_{name}_{color.strip('#')}.png")
    if not os.path.exists(path):
        img = QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(color), 3.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        draw(p)
        p.end()
        img.save(path, "PNG")
    return path.replace("\\", "/")


def _chevron(p: QPainter):
    p.drawPolyline([QPointF(9, 12.5), QPointF(16, 19.5), QPointF(23, 12.5)])


# ─────────────────────────────────────────────────────────────────────────────
# Reusable widgets
# ─────────────────────────────────────────────────────────────────────────────
class ToggleSwitch(QWidget):
    """Animated pill switch. API-compatible with the old ToggleSwitch."""
    toggled = pyqtSignal(bool)

    def __init__(self, checked: bool = True, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._checked = checked
        self._pos = 1.0 if checked else 0.0
        self.palette_ = PALETTES["light"]
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_anim)

    def _on_anim(self, v):
        self._pos = float(v)
        self.update()

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool, animate: bool = True):
        checked = bool(checked)
        if self._checked == checked:
            return
        self._checked = checked
        if animate and self.isVisible():
            self._anim.stop()
            self._anim.setStartValue(self._pos)
            self._anim.setEndValue(1.0 if checked else 0.0)
            self._anim.start()
        else:
            self._pos = 1.0 if checked else 0.0
            self.update()
        self.toggled.emit(checked)

    def set_theme_mode(self, mode: str):
        self.palette_ = PALETTES.get(mode, PALETTES["light"])
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self.setChecked(not self._checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        off, on = QColor(self.palette_["track_off"]), QColor(self.palette_["accent"])
        t = self._pos
        track = QColor(
            int(off.red() + (on.red() - off.red()) * t),
            int(off.green() + (on.green() - off.green()) * t),
            int(off.blue() + (on.blue() - off.blue()) * t),
        )
        if not self.isEnabled():
            track.setAlpha(110)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(QRectF(0, 0, w, h), h / 2, h / 2)
        d = h - 6
        x = 3 + (w - d - 6) * t
        p.setBrush(QColor(0, 0, 0, 30))
        p.drawEllipse(QRectF(x, 4, d, d))
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QRectF(x, 3, d, d))
        p.end()


class Segmented(QFrame):
    """Pill-style segmented control. Emits the selected value."""
    changed = pyqtSignal(object)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.setObjectName("Segmented")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(2)
        self._group = QButtonGroup(self)
        self._buttons: Dict[object, QPushButton] = {}
        for label, value in options:
            b = QPushButton(label, self)
            b.setObjectName("SegBtn")
            b.setCheckable(True)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _=False, v=value: self.changed.emit(v))
            self._group.addButton(b)
            self._buttons[value] = b
            lay.addWidget(b)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def value(self):
        for v, b in self._buttons.items():
            if b.isChecked():
                return v
        return None

    def set_value(self, value):
        b = self._buttons.get(value)
        if b:
            b.setChecked(True)


class Card(QFrame):
    """Rounded surface with an optional title and stacked rows separated by dividers."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(18, 14, 18, 14)
        self._lay.setSpacing(0)
        self._rows = 0
        if title:
            t = QLabel(title, self)
            t.setObjectName("CardTitle")
            self._lay.addWidget(t)
            self._lay.addSpacing(6)

    def add(self, widget: QWidget, divider: bool = True):
        if self._rows and divider:
            d = QFrame(self)
            d.setObjectName("Divider")
            d.setFixedHeight(1)
            self._lay.addWidget(d)
        self._lay.addWidget(widget)
        self._rows += 1
        return widget


def setting_row(title: str, control: Optional[QWidget] = None, hint: str = "", stretch_control: bool = False) -> QWidget:
    """A single settings line: title (+ optional hint) on the left, control on the right."""
    row = QWidget()
    row.setObjectName("Row")
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 10, 0, 10)
    lay.setSpacing(16)
    text_col = QVBoxLayout()
    text_col.setSpacing(1)
    lt = QLabel(title)
    lt.setObjectName("RowTitle")
    text_col.addWidget(lt)
    if hint:
        lh = QLabel(hint)
        lh.setObjectName("RowHint")
        lh.setWordWrap(True)
        text_col.addWidget(lh)
    lay.addLayout(text_col, 1)
    if control is not None:
        if stretch_control:
            lay.addWidget(control, 2)
        else:
            lay.addWidget(control, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    row.title_label = lt
    return row


class SliderRow(QWidget):
    """Title on the left, slider and a value pill on the right."""

    def __init__(self, title: str, lo: int, hi: int, value: int, fmt: Callable[[int], str], hint: str = ""):
        super().__init__()
        self.fmt = fmt
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 10, 0, 10)
        lay.setSpacing(14)
        col = QVBoxLayout()
        col.setSpacing(1)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("RowTitle")
        col.addWidget(self.title_label)
        if hint:
            h = QLabel(hint)
            h.setObjectName("RowHint")
            col.addWidget(h)
        lay.addLayout(col, 1)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(lo, hi)
        self.slider.setMinimumWidth(200)
        self.slider.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lay.addWidget(self.slider, 2)
        self.pill = QLabel()
        self.pill.setObjectName("Pill")
        self.pill.setFixedWidth(62)
        self.pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.pill)
        self.slider.valueChanged.connect(lambda v: self.pill.setText(self.fmt(v)))
        self.slider.setValue(value)
        self.pill.setText(self.fmt(value))


class BubbleStyleGraphic(QWidget):
    """Mini preview of the floating bubble for each style preset."""

    def __init__(self, style_name: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(62, 26)
        self.style_name = style_name
        self.is_dark = False

    def set_dark(self, is_dark: bool):
        self.is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        r = h / 2.0
        rect = QRectF(1, 1, w - 2, h - 2)
        if self.style_name == "Default":
            p.setPen(QPen(QColor("#94A3B8"), 1.2))
            p.setBrush(QColor("#1E293B") if self.is_dark else QColor("#FFFFFF"))
        elif self.style_name == "Frosted Glass":
            p.setPen(QPen(QColor("#6B9FFF") if self.is_dark else QColor("#3478F6"), 1.5))
            p.setBrush(QColor(37, 37, 37, 235) if self.is_dark else QColor(255, 255, 255, 235))
        elif self.style_name == "Transparent":
            p.setPen(QPen(QColor("#94A3B8"), 1.2, Qt.PenStyle.DashLine))
            p.setBrush(QColor(0, 0, 0, 40) if self.is_dark else QColor(255, 255, 255, 40))
        else:  # Minimal
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#2A2A2A") if self.is_dark else QColor("#EFEFEF"))
        p.drawRoundedRect(rect, r, r)
        p.setPen(QPen(QColor(255, 255, 255, 40) if self.is_dark else QColor("#CBD5E1"), 1.0))
        p.drawLine(int(w / 2), 5, int(w / 2), int(h - 5))
        c = QColor("#6B9FFF") if self.is_dark else QColor("#3478F6")
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(c)
        for dx, bh in ((-4, 6), (0, 11), (4, 6)):
            p.drawRoundedRect(QRectF(w * 0.25 + dx - 1.25, h * 0.5 - bh / 2, 2.5, bh), 1.25, 1.25)
        p.setPen(QPen(c, 1.2)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(QRectF(w * 0.75 - 4, h * 0.5 - 5, 8, 10), 1.5, 1.5)
        p.end()


class Tile(QFrame):
    """Selectable card tile (used for bubble styles)."""
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Tile")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setProperty("selected", False)

    def set_selected(self, selected: bool):
        self.setProperty("selected", bool(selected))
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class EqualizerPreviewWidget(QWidget):
    """Small animated voice spectrum; lively while speaking, calm when idle."""

    def __init__(self, width: int = 150, bars: int = 14, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, 26)
        self.is_active = False
        self.num_bars = bars
        self._levels = [0.12] * bars
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def set_active(self, active: bool):
        self.is_active = active

    def _tick(self):
        import math
        if not self.isVisible():
            return
        self._phase += 0.065
        t = self._phase
        n = self.num_bars
        for i in range(n):
            env = math.sin((i / float(n - 1)) * math.pi)
            if self.is_active:
                raw = 0.45 + 0.35 * math.sin(t * 3.8 + i * 0.42) * math.cos(t * 2.1 - i * 0.28) + 0.2 * math.sin(t * 5.4 + i * 0.65)
                target = max(0.12, min(0.98, 0.15 + raw * env * 0.82))
            else:
                target = max(0.08, 0.12 + math.sin(t * 1.2 + i * 0.3) * 0.05 * env)
            self._levels[i] += (target - self._levels[i]) * 0.18
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        n, bw = self.num_bars, 5.0
        gap = (w - n * bw) / max(1, n - 1)
        p.setPen(Qt.PenStyle.NoPen)
        for i, lvl in enumerate(self._levels):
            bh = max(4.0, h * lvl)
            if self.is_active:
                r = i / float(n - 1)
                p.setBrush(QColor(int(139 * (1 - r) + 6 * r), int(92 * (1 - r) + 182 * r), int(246 * (1 - r) + 212 * r), 240))
            else:
                p.setBrush(QColor(148, 163, 184, 90))
            p.drawRoundedRect(QRectF(i * (bw + gap), (h - bh) / 2, bw, bh), 2.5, 2.5)
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Settings dialog
# ─────────────────────────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()
    test_bubble_requested = pyqtSignal()
    read_text_requested = pyqtSignal(str)

    PAGE_READ, PAGE_VOICE, PAGE_PLAYBACK, PAGE_APPEARANCE, PAGE_ABOUT, PAGE_PERMISSIONS = range(6)

    def __init__(self, tts_engine: Optional[TTSEngine] = None, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.theme_pref = settings_db.get("settings_theme", "light")
        if self.theme_pref not in THEME_PREFS:
            self.theme_pref = "light"
        self.current_theme = resolve_theme(self.theme_pref)
        self.current_bubble_style: str = "Frosted Glass"
        self.current_corner_radius: str = "Medium"
        self.nav_buttons: List[QPushButton] = []
        self.bubble_tiles: Dict[str, Tile] = {}
        self.bubble_graphics: List[BubbleStyleGraphic] = []
        self.switches: List[ToggleSwitch] = []
        self._test_running = False

        self.setWindowTitle(f"{APP_NAME} — Settings")
        self.setWindowIcon(create_app_icon(64))
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(840, 600)
        self.resize(880, 640)

        self._init_ui()
        if self.tts:
            self.tts.playback_started.connect(self._on_tts_started)
            self.tts.playback_finished.connect(self._on_tts_finished)
            if hasattr(self.tts, "playback_error"):
                self.tts.playback_error.connect(lambda _msg: self._on_tts_finished())
        self.apply_theme(self.theme_pref)
        try:  # follow the OS when "System" is chosen
            QGuiApplication.styleHints().colorSchemeChanged.connect(
                lambda _s: self.apply_theme("system") if self.theme_pref == "system" else None)
        except Exception:
            pass
        self.load_values()
        self._go_to(self.PAGE_READ)

    # ── Layout ──────────────────────────────────────────────────────────────
    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar_widget = QFrame(self)
        self.sidebar_widget.setObjectName("Sidebar")
        self.sidebar_widget.setFixedWidth(200)
        side = QVBoxLayout(self.sidebar_widget)
        side.setContentsMargins(14, 22, 14, 16)
        side.setSpacing(4)

        self.lbl_sidebar_logo = QLabel(self.sidebar_widget)
        self.lbl_sidebar_logo.setFixedHeight(52)
        self.lbl_sidebar_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side.addWidget(self.lbl_sidebar_logo)
        side.addSpacing(18)

        self.pages_meta = [
            (self.PAGE_READ, "Read Text", "Read Text", "Paste any text and listen."),
            (self.PAGE_VOICE, "Voice", "Voice", "Pick a voice and tune how it sounds."),
            (self.PAGE_PLAYBACK, "Playback", "Playback", "When and how Voxel plays."),
            (self.PAGE_APPEARANCE, "Appearance", "Appearance", "Theme and floating bubble."),
            (self.PAGE_ABOUT, "About", "About", "Version, links and license."),
        ]
        if IS_MAC:
            self.pages_meta.append((self.PAGE_PERMISSIONS, "Accessibility", "Accessibility", "Let Voxel read selected text."))

        self._nav_icons = {self.PAGE_READ: "file-text", self.PAGE_VOICE: "audio-lines", self.PAGE_PLAYBACK: "play",
                           self.PAGE_APPEARANCE: "palette", self.PAGE_ABOUT: "info", self.PAGE_PERMISSIONS: "accessibility"}
        self.btn_group_nav = QButtonGroup(self)
        self._nav_by_page: Dict[int, QPushButton] = {}
        for page, label, _t, _s in self.pages_meta:
            b = QPushButton(label, self.sidebar_widget)
            b.setObjectName("NavBtn")
            b.setCheckable(True)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _=False, p=page: self._go_to(p))
            self.btn_group_nav.addButton(b)
            self.nav_buttons.append(b)
            self._nav_by_page[page] = b
            side.addWidget(b)
        side.addStretch()

        self.seg_theme = Segmented([("Light", "light"), ("Dark", "dark"), ("System", "system")], self.sidebar_widget)
        self.seg_theme.changed.connect(self.apply_theme)
        side.addWidget(self.seg_theme, 0, Qt.AlignmentFlag.AlignHCenter)
        side.addSpacing(8)
        lbl_ver = QLabel(f"{APP_NAME} {VERSION}", self.sidebar_widget)
        lbl_ver.setObjectName("Faint")
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side.addWidget(lbl_ver)
        root.addWidget(self.sidebar_widget)

        # Main column
        main = QWidget(self)
        main.setObjectName("Main")
        col = QVBoxLayout(main)
        col.setContentsMargins(28, 24, 28, 18)
        col.setSpacing(14)

        self.lbl_header_title = QLabel("", main)
        self.lbl_header_title.setObjectName("PageTitle")
        self.lbl_header_subtitle = QLabel("", main)
        self.lbl_header_subtitle.setObjectName("PageSub")
        head = QVBoxLayout()
        head.setSpacing(2)
        head.addWidget(self.lbl_header_title)
        head.addWidget(self.lbl_header_subtitle)
        col.addLayout(head)

        self.stacked_pages = QStackedWidget(main)
        self.stacked_pages.addWidget(self._create_read_page())        # 0
        self.stacked_pages.addWidget(self._create_voice_page())       # 1
        self.stacked_pages.addWidget(self._create_playback_page())    # 2
        self.stacked_pages.addWidget(self._create_appearance_page())  # 3
        self.stacked_pages.addWidget(self._create_about_page())       # 4
        if IS_MAC:
            self.stacked_pages.addWidget(self._create_permissions_page())  # 5
        col.addWidget(self.stacked_pages, 1)

        # Bottom action bar (only on settings pages)
        self.action_bar = QWidget(main)
        bar = QHBoxLayout(self.action_bar)
        bar.setContentsMargins(0, 0, 0, 0)
        self.btn_reset_defaults = QPushButton("Reset to defaults", self.action_bar)
        self.btn_reset_defaults.setObjectName("BtnGhost")
        self.btn_reset_defaults.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_reset_defaults.clicked.connect(self.reset_to_defaults)
        bar.addWidget(self.btn_reset_defaults)
        bar.addStretch()
        self.btn_save_changes = QPushButton("Save changes", self.action_bar)
        self.btn_save_changes.setObjectName("BtnPrimary")
        self.btn_save_changes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_save_changes.clicked.connect(self.save_and_apply)
        bar.addWidget(self.btn_save_changes)
        col.addWidget(self.action_bar)
        root.addWidget(main, 1)

    @staticmethod
    def _scroll(content_builder: Callable[[QVBoxLayout], None]) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("ScrollContent")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(0, 0, 10, 6)
        lay.setSpacing(14)
        content_builder(lay)
        lay.addStretch()
        scroll.setWidget(content)
        scroll.viewport().setAutoFillBackground(False)
        return scroll

    def _switch(self) -> ToggleSwitch:
        s = ToggleSwitch(True)
        self.switches.append(s)
        return s

    # ── Page: Read Text ─────────────────────────────────────────────────────
    def _create_read_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self.txt_reader = QPlainTextEdit(page)
        self.txt_reader.setObjectName("Reader")
        self.txt_reader.setPlaceholderText(
            "Paste or type text here…\n\nUseful when an app or website won't let Voxel read the selection."
        )
        self.txt_reader.textChanged.connect(self._update_reader_count)
        lay.addWidget(self.txt_reader, 1)

        bar = QFrame(page)
        bar.setObjectName("Bar")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10, 8, 10, 8)
        bl.setSpacing(8)

        btn_paste = self.btn_paste = QPushButton(" Paste", bar)
        btn_paste.setObjectName("BtnSoft")
        btn_paste.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_paste.clicked.connect(self._paste_into_reader)
        bl.addWidget(btn_paste)

        btn_clear = QPushButton("Clear", bar)
        btn_clear.setObjectName("BtnGhost")
        btn_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_clear.clicked.connect(self.txt_reader.clear)
        bl.addWidget(btn_clear)

        self.lbl_reader_count = QLabel("", bar)
        self.lbl_reader_count.setObjectName("RowHint")
        bl.addSpacing(6)
        bl.addWidget(self.lbl_reader_count)
        bl.addStretch()

        self.reader_viz = EqualizerPreviewWidget(110, 12, bar)
        bl.addWidget(self.reader_viz)

        self.btn_read = QPushButton(" Read aloud", bar)
        self.btn_read.setObjectName("BtnPrimary")
        self.btn_read.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_read.setToolTip("Ctrl+Enter")
        self.btn_read.clicked.connect(self._toggle_read)
        bl.addWidget(self.btn_read)
        lay.addWidget(bar)

        QShortcut(QKeySequence("Ctrl+Return"), self.txt_reader, activated=self._toggle_read)
        QShortcut(QKeySequence("Ctrl+Enter"), self.txt_reader, activated=self._toggle_read)
        self._update_reader_count()
        return page

    def _paste_into_reader(self):
        text = QApplication.clipboard().text()
        if text:
            self.txt_reader.setPlainText(text.strip())
            self.txt_reader.setFocus()

    def _update_reader_count(self):
        words = len(self.txt_reader.toPlainText().split())
        if not words:
            self.lbl_reader_count.setText("No text yet")
            return
        speed = max(0.5, self.slider_speed.value() / 100.0) if hasattr(self, "slider_speed") else 1.0
        mins = words / (150.0 * speed)
        dur = "< 1 min" if mins < 1 else f"~{round(mins)} min"
        self.lbl_reader_count.setText(f"{words:,} words · {dur}")

    def _toggle_read(self):
        if self.tts and self.tts.is_speaking:
            self.tts.stop()
            self._on_tts_finished()
            return
        text = self.txt_reader.toPlainText().strip()
        if not text:
            self.txt_reader.setFocus()
            return
        self._apply_voice_choice()
        if self.receivers(self.read_text_requested) > 0:
            self.read_text_requested.emit(text)
        elif self.tts:
            self.tts.speak(text)
        self._set_reading_ui(True)

    def _set_reading_ui(self, active: bool):
        self.btn_read.setText(" Stop" if active else " Read aloud")
        if hasattr(self, "_icon_play"):
            self.btn_read.setIcon(self._icon_stop if active else self._icon_play)
        self.reader_viz.set_active(active)

    # ── Page: Voice ─────────────────────────────────────────────────────────
    def _create_voice_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        def build(l: QVBoxLayout):
            c = Card("Voice")
            self.combo_voice = QComboBox()
            for v in VOICES:
                self.combo_voice.addItem(v["label"], v["id"])
            self.combo_voice.setFixedWidth(330)
            c.add(setting_row("Voice", self.combo_voice))
            self.combo_emotion = QComboBox()
            for m in EMOTION_MODES:
                short, _, detail = m["label"].partition(" (")
                self.combo_emotion.addItem(short, m["id"])
                if detail:
                    self.combo_emotion.setItemData(self.combo_emotion.count() - 1, detail.rstrip(")"), Qt.ItemDataRole.ToolTipRole)
            self.combo_emotion.setFixedWidth(330)
            c.add(setting_row("Tone", self.combo_emotion))
            l.addWidget(c)

            c = Card("Tuning")
            self.row_speed = SliderRow("Speed", 50, 200, 100, lambda v: f"{v / 100:.2f}×")
            self.slider_speed = self.row_speed.slider
            self.lbl_speed_val = self.row_speed.pill
            self.slider_speed.valueChanged.connect(self._on_speed_slider_changed)
            c.add(self.row_speed)
            self.row_pitch = SliderRow("Pitch", -50, 50, 0, lambda v: f"{v:+d} Hz" if v else "0 Hz")
            self.slider_pitch = self.row_pitch.slider
            self.lbl_pitch_val = self.row_pitch.pill
            self.slider_pitch.valueChanged.connect(self._on_pitch_slider_changed)
            c.add(self.row_pitch)
            l.addWidget(c)

            c = Card("Equalizer")
            self.equalizer_widget = VoiceEqualizerWidget()
            c.add(self.equalizer_widget)
            l.addWidget(c)

        lay.addWidget(self._scroll(build), 1)

        self.frame_test_voice = QFrame(page)
        self.frame_test_voice.setObjectName("Bar")
        tb = QHBoxLayout(self.frame_test_voice)
        tb.setContentsMargins(10, 8, 14, 8)
        tb.setSpacing(12)
        self.btn_test_perf = QPushButton(" Test voice", self.frame_test_voice)
        self.btn_test_perf.setObjectName("BtnSoft")
        self.btn_test_perf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_test_perf.clicked.connect(self._run_performance_test)
        tb.addWidget(self.btn_test_perf)
        self.equalizer_preview = EqualizerPreviewWidget(150, 16, self.frame_test_voice)
        tb.addWidget(self.equalizer_preview)
        self.lbl_test_status = QLabel("", self.frame_test_voice)
        self.lbl_test_status.setObjectName("RowHint")
        tb.addWidget(self.lbl_test_status)
        tb.addStretch()
        lay.addWidget(self.frame_test_voice)
        return page

    # ── Page: Playback ──────────────────────────────────────────────────────
    def _create_playback_page(self) -> QWidget:
        def build(l: QVBoxLayout):
            c = Card("Behavior")
            self.chk_startup = self._switch()
            c.add(setting_row("Start at login" if IS_MAC else "Start with Windows", self.chk_startup))
            self.chk_trigger = self._switch()
            c.add(setting_row("Show bubble on selection", self.chk_trigger, "Floating button appears when you highlight text"))
            self.chk_prebuffer = self._switch()
            c.add(setting_row("Instant start", self.chk_prebuffer, "Prepare audio when you hover the bubble"))
            self.switch_fade_in = self._switch()
            c.add(setting_row("Smooth fade-in", self.switch_fade_in))
            self.chk_autoclose = self._switch()
            c.add(setting_row("Close player when done", self.chk_autoclose))
            self.row_close_delay = SliderRow("Close delay", 20, 300, 100, lambda v: f"{v / 100:.1f} s")
            self.slider_fade_out = self.row_close_delay.slider
            self.lbl_fade_out_val = self.row_close_delay.pill
            c.add(self.row_close_delay)
            self.chk_autoclose.toggled.connect(self.row_close_delay.setEnabled)
            l.addWidget(c)

            c = Card("Output")
            self.combo_device = QComboBox()
            self.combo_device.addItem("System default", "default")
            self.combo_device.setFixedWidth(330)
            c.add(setting_row("Device", self.combo_device))
            self.row_volume = SliderRow("Volume", 0, 100, 80, lambda v: f"{v}%")
            self.slider_volume = self.row_volume.slider
            self.lbl_vol_val = self.row_volume.pill
            self.slider_volume.valueChanged.connect(self._on_volume_slider_changed)
            c.add(self.row_volume)

            rec_dir = str(get_recordings_dir())
            btn_open = QPushButton("Open folder")
            btn_open.setObjectName("BtnSoft")
            btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open.clicked.connect(open_recordings_folder)
            rec_row = setting_row("Recordings", btn_open, " ")
            hint = rec_row.findChild(QLabel, "RowHint")
            if hint:
                hint.setWordWrap(False)
                hint.setText(QFontMetrics(hint.font()).elidedText(rec_dir, Qt.TextElideMode.ElideMiddle, 330))
                hint.setToolTip(rec_dir)
            c.add(rec_row)
            l.addWidget(c)

        return self._scroll(build)

    # ── Page: Appearance ────────────────────────────────────────────────────
    def _create_appearance_page(self) -> QWidget:
        def build(l: QVBoxLayout):
            c = Card("Bubble style")
            tiles = QWidget()
            tl = QHBoxLayout(tiles)
            tl.setContentsMargins(0, 8, 0, 8)
            tl.setSpacing(10)
            for name in ["Default", "Frosted Glass", "Transparent", "Minimal"]:
                t = Tile()
                v = QVBoxLayout(t)
                v.setContentsMargins(8, 12, 8, 10)
                v.setSpacing(8)
                g = BubbleStyleGraphic(name, t)
                self.bubble_graphics.append(g)
                v.addWidget(g, 0, Qt.AlignmentFlag.AlignHCenter)
                lbl = QLabel(name, t)
                lbl.setObjectName("TileLabel")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                v.addWidget(lbl)
                t.clicked.connect(lambda n=name: self._select_bubble_style(n))
                self.bubble_tiles[name] = t
                tl.addWidget(t)
            c.add(tiles, divider=False)
            l.addWidget(c)

            c = Card("Bubble")
            self.seg_bubble_size = Segmented([("Small", "Small Dot"), ("Medium", "Medium"), ("Large", "Large")])
            c.add(setting_row("Size", self.seg_bubble_size))
            self.seg_corner = Segmented([("Square", "Square"), ("Medium", "Medium"), ("Round", "Round")])
            self.seg_corner.changed.connect(self._select_corner_radius)
            c.add(setting_row("Corners", self.seg_corner))
            self.row_opacity = SliderRow("Opacity", 30, 100, 90, lambda v: f"{v}%")
            self.slider_transparency = self.row_opacity.slider
            self.lbl_trans_val = self.row_opacity.pill
            c.add(self.row_opacity)
            self.row_distance = SliderRow("Distance from text", 15, 75, 28, lambda v: f"{v} px")
            self.slider_distance = self.row_distance.slider
            self.lbl_dist_val = self.row_distance.pill
            c.add(self.row_distance)
            l.addWidget(c)

            c = Card("Logo")
            w = QWidget()
            wl = QHBoxLayout(w)
            wl.setContentsMargins(0, 8, 0, 8)
            wl.setSpacing(10)
            self.frame_logo_preview = QFrame()
            self.frame_logo_preview.setObjectName("LogoBox")
            self.frame_logo_preview.setFixedSize(150, 56)
            pl = QVBoxLayout(self.frame_logo_preview)
            pl.setContentsMargins(8, 6, 8, 6)
            self.lbl_logo_preview = QLabel()
            self.lbl_logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pl.addWidget(self.lbl_logo_preview)
            wl.addWidget(self.frame_logo_preview)
            hint = QLabel("PNG or SVG, square,\n512 × 512 recommended")
            hint.setObjectName("RowHint")
            wl.addWidget(hint, 1)
            self.btn_change_logo = QPushButton("Change")
            self.btn_change_logo.setObjectName("BtnSoft")
            self.btn_change_logo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.btn_change_logo.clicked.connect(self._on_change_logo)
            wl.addWidget(self.btn_change_logo)
            self.btn_restore_logo = QPushButton("Reset")
            self.btn_restore_logo.setObjectName("BtnGhost")
            self.btn_restore_logo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.btn_restore_logo.clicked.connect(self._on_restore_default_logo)
            wl.addWidget(self.btn_restore_logo)
            c.add(w, divider=False)
            l.addWidget(c)

        return self._scroll(build)

    # ── Page: About ─────────────────────────────────────────────────────────
    def _create_about_page(self) -> QWidget:
        def build(l: QVBoxLayout):
            c = Card()
            hero = QWidget()
            hl = QVBoxLayout(hero)
            hl.setContentsMargins(0, 18, 0, 18)
            hl.setSpacing(10)
            self.lbl_about_logo = QLabel()
            self.lbl_about_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hl.addWidget(self.lbl_about_logo)
            ver = QLabel(f"Version {VERSION}")
            ver.setObjectName("Pill")
            ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ver.setFixedWidth(120)
            hl.addWidget(ver, 0, Qt.AlignmentFlag.AlignHCenter)
            desc = QLabel(f"Select text anywhere and hear it.\nFree and open source, made by {COMPANY_NAME}.")
            desc.setObjectName("PageSub")
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hl.addWidget(desc)
            links = QHBoxLayout()
            links.setSpacing(8)
            links.addStretch()
            for label, url in [("GitHub", GITHUB_URL), (COMPANY_NAME, COMPANY_URL), ("LinkedIn", LINKEDIN_URL)]:
                b = QPushButton(label)
                b.setObjectName("BtnSoft")
                b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                b.clicked.connect(lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u)))
                links.addWidget(b)
            links.addStretch()
            hl.addSpacing(4)
            hl.addLayout(links)
            c.add(hero, divider=False)
            l.addWidget(c)

            foot = QLabel("MIT License · No telemetry · Provided as is, without warranty.")
            foot.setObjectName("Faint")
            foot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.addWidget(foot)

        return self._scroll(build)

    # ── Page: Permissions (macOS) ───────────────────────────────────────────
    def _create_permissions_page(self) -> QWidget:
        def build(l: QVBoxLayout):
            c = Card("Accessibility")
            self.lbl_perm_page_status = QLabel()
            self.lbl_perm_page_status.setObjectName("RowTitle")
            btn_refresh = QPushButton("Refresh")
            btn_refresh.setObjectName("BtnGhost")
            btn_refresh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_refresh.clicked.connect(self._refresh_perm_page_status)
            row = setting_row("Status", btn_refresh)
            row.layout().insertWidget(1, self.lbl_perm_page_status)
            c.add(row)
            btn_open = QPushButton("Open settings")
            btn_open.setObjectName("BtnSoft")
            btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open.clicked.connect(open_accessibility_settings)
            c.add(setting_row("Allow Voxel", btn_open, "Privacy & Security → Accessibility → turn Voxel on"))
            from src.utils.mac_permissions import restart_voxel_app
            btn_restart = QPushButton("Restart")
            btn_restart.setObjectName("BtnSoft")
            btn_restart.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_restart.clicked.connect(restart_voxel_app)
            c.add(setting_row("Restart Voxel", btn_restart, "Needed once after granting access"))
            btn_test = QPushButton("Test")
            btn_test.setObjectName("BtnSoft")
            btn_test.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_test.clicked.connect(lambda: self.test_bubble_requested.emit())
            c.add(setting_row("Test the bubble", btn_test))
            l.addWidget(c)
            self._refresh_perm_page_status()

        return self._scroll(build)

    def _refresh_perm_page_status(self):
        if not hasattr(self, "lbl_perm_page_status"):
            return
        pal = PALETTES[self.current_theme]
        if is_accessibility_trusted(prompt=False):
            self.lbl_perm_page_status.setText(f"<span style='color:{pal['ok']}'>● Active</span>")
        else:
            self.lbl_perm_page_status.setText(f"<span style='color:{pal['warn']}'>● Not allowed yet</span>")

    # ── Handlers ────────────────────────────────────────────────────────────
    def _on_speed_slider_changed(self, val: int):
        if self.tts:
            self.tts.set_speed(round(val / 100.0, 2))
        self._update_reader_count()

    def _on_pitch_slider_changed(self, val: int):
        if self.tts and hasattr(self.tts, "set_pitch"):
            self.tts.set_pitch(val)

    def _on_volume_slider_changed(self, val: int):
        if self.tts and hasattr(self.tts, "set_volume"):
            self.tts.set_volume(val / 100.0)

    def _on_fade_out_slider_changed(self, val: int):
        """Kept for backwards compatibility; the pill updates itself."""

    def _select_bubble_style(self, style_name: str):
        if style_name not in self.bubble_tiles:
            style_name = "Frosted Glass"
        self.current_bubble_style = style_name
        for name, tile in self.bubble_tiles.items():
            tile.set_selected(name == style_name)

    def _select_corner_radius(self, corner_name: str):
        if corner_name not in ("Square", "Medium", "Round"):
            corner_name = "Medium"
        self.current_corner_radius = corner_name
        self.seg_corner.set_value(corner_name)

    def _on_change_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose logo", "", "Images (*.png *.jpg *.jpeg *.svg *.ico)"
        )
        if path and os.path.exists(path):
            settings_db.set("custom_logo_path", path)
            self._update_all_logos()

    def _on_restore_default_logo(self):
        if "custom_logo_path" in settings_db:
            settings_db.remove("custom_logo_path")
        self._update_all_logos()

    def _update_sidebar_logo(self):
        pix = get_brand_logo_pixmap(is_dark=(self.current_theme == "dark"), target_width=150)
        if not pix.isNull():
            self.lbl_sidebar_logo.setPixmap(pix)

    def _update_all_logos(self):
        self._update_sidebar_logo()
        is_dark = self.current_theme == "dark"
        if hasattr(self, "lbl_logo_preview"):
            pix = get_brand_logo_pixmap(is_dark=is_dark, target_width=120)
            if not pix.isNull():
                self.lbl_logo_preview.setPixmap(pix)
        if hasattr(self, "lbl_about_logo"):
            pix = get_brand_logo_pixmap(is_dark=is_dark, target_width=220)
            if not pix.isNull():
                self.lbl_about_logo.setPixmap(pix)

    def _go_to(self, page: int):
        meta = next((m for m in self.pages_meta if m[0] == page), self.pages_meta[0])
        self.stacked_pages.setCurrentIndex(meta[0])
        self._nav_by_page[meta[0]].setChecked(True)
        self.lbl_header_title.setText(meta[2])
        self.lbl_header_subtitle.setText(meta[3])
        self.action_bar.setVisible(meta[0] in (self.PAGE_VOICE, self.PAGE_PLAYBACK, self.PAGE_APPEARANCE))
        if meta[0] == self.PAGE_PERMISSIONS:
            self._refresh_perm_page_status()

    def _on_nav_clicked(self, page_idx: int, *_args):
        """Backwards-compatible alias."""
        self._go_to(page_idx)

    def _show_page(self, page: int):
        self._go_to(page)
        self.show()
        self.raise_()
        self.activateWindow()

    def open_preferences(self):
        self._show_page(self.PAGE_VOICE)

    def open_about(self):
        self._show_page(self.PAGE_ABOUT)

    def open_reader(self, text: str = ""):
        if text:
            self.txt_reader.setPlainText(text)
        self._show_page(self.PAGE_READ)
        self.txt_reader.setFocus()

    # ── TTS state ───────────────────────────────────────────────────────────
    def _apply_voice_choice(self):
        if not self.tts:
            return
        voice_id = self.combo_voice.currentData()
        for i, v in enumerate(VOICES):
            if v["id"] == voice_id:
                self.tts.set_voice_index(i)
                break
        self.tts.set_emotion_mode(self.combo_emotion.currentData())

    def _on_tts_started(self):
        if self._test_running:
            self.lbl_test_status.setText("Playing…")

    def _on_tts_finished(self):
        self._test_running = False
        self.btn_test_perf.setText(" Test voice")
        if hasattr(self, "_icon_play_soft"):
            self.btn_test_perf.setIcon(self._icon_play_soft)
        self.lbl_test_status.setText("")
        self.equalizer_preview.set_active(False)
        self._set_reading_ui(False)

    def _run_performance_test(self):
        if not self.tts:
            self.lbl_test_status.setText("Audio engine not available")
            return
        if self.tts.is_speaking:
            self.tts.stop()
            self._on_tts_finished()
            return
        self._apply_voice_choice()
        self._test_running = True
        self.btn_test_perf.setText(" Stop")
        if hasattr(self, "_icon_stop_soft"):
            self.btn_test_perf.setIcon(self._icon_stop_soft)
        self.lbl_test_status.setText("Preparing…")
        self.equalizer_preview.set_active(True)
        self.tts.speak("Hi, I'm Voxel. This is how I sound with your current settings.")

    # ── Theme ───────────────────────────────────────────────────────────────
    def _stylesheet(self, pal: dict) -> str:
        chevron = _icon_file("chevron", pal["muted"], _chevron)
        return f"""
        QDialog {{ background: {pal['bg']}; font-family: {FONT_STACK}; }}
        QWidget#Main, QWidget#ScrollContent {{ background: transparent; }}
        QScrollArea {{ background: transparent; border: none; }}
        QLabel {{ background: transparent; color: {pal['text']}; font-size: 13px; }}
        QToolTip {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']}; padding: 4px 8px; }}

        QFrame#Sidebar {{ background: {pal['sidebar']}; border-right: 1px solid {pal['border']}; }}
        QPushButton#NavBtn {{
            background: transparent; color: {pal['muted']}; border: none; border-radius: 10px;
            padding: 9px 12px; text-align: left; font-size: 13px; font-weight: 500;
        }}
        QPushButton#NavBtn:hover {{ background: {pal['surface2']}; color: {pal['text']}; }}
        QPushButton#NavBtn:checked {{ background: {pal['accent_soft']}; color: {pal['accent_text']}; }}

        QLabel#PageTitle {{ font-size: 22px; font-weight: 600; }}
        QLabel#PageSub {{ font-size: 13px; color: {pal['muted']}; }}
        QLabel#Faint {{ font-size: 11px; color: {pal['faint']}; }}

        QFrame#Card {{ background: {pal['surface']}; border: 1px solid {pal['border']}; border-radius: 12px; }}
        QLabel#CardTitle {{ font-size: 12px; font-weight: 600; color: {pal['muted']}; }}
        QFrame#Divider {{ background: {pal['border']}; border: none; }}
        QLabel#RowTitle {{ font-size: 13px; font-weight: 500; }}
        QLabel#RowHint {{ font-size: 11px; color: {pal['muted']}; }}
        QLabel#Pill {{
            background: {pal['accent_soft']}; color: {pal['accent_text']};
            border-radius: 8px; padding: 3px 6px; font-size: 12px; font-weight: 700;
        }}
        QFrame#Bar {{ background: {pal['surface']}; border: 1px solid {pal['border']}; border-radius: 12px; }}

        QFrame#Segmented {{ background: {pal['surface2']}; border: 1px solid {pal['border']}; border-radius: 10px; }}
        QPushButton#SegBtn {{
            background: transparent; color: {pal['muted']}; border: none; border-radius: 8px;
            padding: 5px 10px; font-size: 12px; font-weight: 500; min-width: 40px;
        }}
        QPushButton#SegBtn:hover {{ color: {pal['text']}; }}
        QPushButton#SegBtn:checked {{ background: {pal['surface']}; color: {pal['accent_text']}; border: 1px solid {pal['border']}; }}

        QFrame#Tile {{ background: {pal['surface2']}; border: 1.5px solid transparent; border-radius: 12px; }}
        QFrame#Tile:hover {{ border-color: {pal['border']}; }}
        QFrame#Tile[selected="true"] {{ background: {pal['accent_soft']}; border-color: {pal['accent']}; }}
        QLabel#TileLabel {{ font-size: 12px; font-weight: 600; }}
        QFrame#LogoBox {{ background: {pal['surface2']}; border: 1px solid {pal['border']}; border-radius: 10px; }}

        QPlainTextEdit#Reader {{
            background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
            border-radius: 12px; padding: 14px; font-size: 14px;
            selection-background-color: {pal['accent']}; selection-color: #FFFFFF;
        }}
        QPlainTextEdit#Reader:focus {{ border: 1.5px solid {pal['accent']}; }}

        QComboBox {{
            background: {pal['surface2']}; color: {pal['text']}; border: 1px solid {pal['border']};
            border-radius: 9px; padding: 6px 32px 6px 12px; font-size: 13px; min-height: 20px;
        }}
        QComboBox:hover {{ border-color: {pal['accent']}; }}
        QComboBox::drop-down {{ border: none; width: 28px; }}
        QComboBox::down-arrow {{ image: url("{chevron}"); width: 12px; height: 12px; }}
        QComboBox QAbstractItemView {{
            background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
            border-radius: 8px; padding: 4px; outline: none;
            selection-background-color: {pal['accent_soft']}; selection-color: {pal['accent_text']};
        }}

        QSlider::groove:horizontal {{ height: 4px; background: {pal['track_off']}; border-radius: 2px; }}
        QSlider::sub-page:horizontal {{ background: {pal['accent']}; border-radius: 2px; }}
        QSlider::handle:horizontal {{
            background: #FFFFFF; border: 2px solid {pal['accent']};
            width: 14px; height: 14px; margin: -7px 0; border-radius: 9px;
        }}
        QSlider::handle:horizontal:hover {{ background: {pal['accent_soft']}; }}
        QSlider::sub-page:horizontal:disabled {{ background: {pal['track_off']}; }}
        QSlider::handle:horizontal:disabled {{ border-color: {pal['track_off']}; }}

        QPushButton {{
            background: {pal['surface2']}; color: {pal['text']}; border: 1px solid {pal['border']};
            border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 500;
        }}
        QPushButton#BtnPrimary {{
            background: {pal['accent']}; color: #FFFFFF; border: none; padding: 9px 22px; font-weight: 600;
        }}
        QPushButton#BtnPrimary:hover {{ background: {pal['accent_hover']}; }}
        QPushButton#BtnSoft {{ background: {pal['accent_soft']}; color: {pal['accent_text']}; border: none; }}
        QPushButton#BtnSoft:hover {{ background: {pal['accent']}; color: #FFFFFF; }}
        QPushButton#BtnGhost {{ background: transparent; color: {pal['muted']}; border: 1px solid {pal['border']}; }}
        QPushButton#BtnGhost:hover {{ color: {pal['text']}; border-color: {pal['muted']}; }}

        QScrollBar:vertical {{ background: transparent; width: 6px; margin: 0; border: none; }}
        QScrollBar::handle:vertical {{ background: {pal['track_off']}; min-height: 30px; border-radius: 3px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        """

    def apply_theme(self, pref: str):
        """pref is the saved choice ('light' | 'dark' | 'system'); the drawn theme is resolved from it."""
        if pref not in THEME_PREFS:
            pref = "light"
        self.theme_pref = pref
        theme = resolve_theme(pref)
        self.current_theme = theme
        settings_db.set("settings_theme", pref)
        pal = PALETTES[theme]
        self.setStyleSheet(self._stylesheet(pal))
        self.seg_theme.set_value(pref)
        for page, btn in self._nav_by_page.items():
            btn.setIcon(line_icon(self._nav_icons.get(page, "info"), pal["muted"], pal["accent_text"], 18))
            btn.setIconSize(QSize(18, 18))
        self.btn_paste.setIcon(line_icon("clipboard", pal["accent_text"], size=16))
        self._icon_play = line_icon("play", "#FFFFFF", size=14)
        self._icon_stop = line_icon("square", "#FFFFFF", size=14)
        self._icon_play_soft = line_icon("play", pal["accent_text"], size=14)
        self._icon_stop_soft = line_icon("square", pal["accent_text"], size=14)
        self._set_reading_ui(bool(self.tts and self.tts.is_speaking and not self._test_running))
        self.btn_test_perf.setIcon(self._icon_stop_soft if self._test_running else self._icon_play_soft)
        for s in self.switches:
            s.set_theme_mode(theme)
        for g in self.bubble_graphics:
            g.set_dark(theme == "dark")
        if hasattr(self, "equalizer_widget"):
            self.equalizer_widget.set_theme_mode(theme)
        self._update_all_logos()
        self._refresh_perm_page_status()

    # ── Load / save ─────────────────────────────────────────────────────────
    def reset_to_defaults(self):
        idx = self.combo_voice.findData("en-US-JennyNeural")
        if idx >= 0:
            self.combo_voice.setCurrentIndex(idx)
        idx = self.combo_emotion.findData(DEFAULT_EMOTION_MODE)
        if idx >= 0:
            self.combo_emotion.setCurrentIndex(idx)
        self.slider_speed.setValue(100)
        self.slider_pitch.setValue(0)
        self.slider_fade_out.setValue(100)
        self.switch_fade_in.setChecked(True)
        self.chk_startup.setChecked(False)
        self.chk_prebuffer.setChecked(True)
        self.chk_trigger.setChecked(True)
        self.chk_autoclose.setChecked(True)
        self.slider_volume.setValue(80)
        self.slider_transparency.setValue(90)
        self.seg_bubble_size.set_value("Large")
        self.slider_distance.setValue(28)
        self.equalizer_widget.apply_preset("Podcast Warmth")
        self._select_bubble_style("Frosted Glass")
        self._select_corner_radius("Medium")
        self._on_restore_default_logo()

    def load_values(self):
        idx = self.combo_voice.findData(settings_db.get("default_voice", "en-US-JennyNeural"))
        if idx >= 0:
            self.combo_voice.setCurrentIndex(idx)
        idx = self.combo_emotion.findData(settings_db.get("emotion_mode", DEFAULT_EMOTION_MODE))
        if idx >= 0:
            self.combo_emotion.setCurrentIndex(idx)
        self.slider_speed.setValue(int(round(float(settings_db.get("default_speed", 1.0)) * 100)))
        self.slider_pitch.setValue(int(settings_db.get("default_pitch", 0)))

        self.chk_startup.setChecked(is_startup_enabled(), animate=False)
        self.chk_prebuffer.setChecked(settings_db.get("prebuffer_enabled", True), animate=False)
        self.chk_trigger.setChecked(settings_db.get("selection_popup_enabled", True), animate=False)
        self.chk_autoclose.setChecked(settings_db.get("auto_close_finished", True), animate=False)
        self.switch_fade_in.setChecked(settings_db.get("smooth_fade_in", True), animate=False)
        self.row_close_delay.setEnabled(self.chk_autoclose.isChecked())

        delay = float(settings_db.get("auto_close_delay", 1.0))
        self.slider_fade_out.setValue(max(20, min(300, int(round(delay * 100)))))
        self.slider_volume.setValue(int(settings_db.get("volume", 80)))
        self.slider_transparency.setValue(int(settings_db.get("bubble_transparency", 90)))

        size = str(settings_db.get("bubble_size", "Large")).lower()
        self.seg_bubble_size.set_value("Small Dot" if "small" in size else "Medium" if "medium" in size else "Large")
        self.slider_distance.setValue(int(settings_db.get("bubble_distance", 28)))
        self._select_corner_radius(settings_db.get("bubble_corner_radius", "Medium"))
        self._select_bubble_style(settings_db.get("bubble_appearance", "Frosted Glass"))
        self._update_all_logos()

    def save_and_apply(self):
        settings_db.set("default_voice", self.combo_voice.currentData())
        settings_db.set("emotion_mode", self.combo_emotion.currentData())
        settings_db.set("default_speed", round(self.slider_speed.value() / 100.0, 2))
        settings_db.set("default_pitch", self.slider_pitch.value())
        if self.tts and hasattr(self.tts, "set_pitch"):
            self.tts.set_pitch(self.slider_pitch.value())
        settings_db.set("prebuffer_enabled", self.chk_prebuffer.isChecked())
        settings_db.set("selection_popup_enabled", self.chk_trigger.isChecked())
        settings_db.set("auto_close_finished", self.chk_autoclose.isChecked())
        settings_db.set("auto_close_delay", round(self.slider_fade_out.value() / 100.0, 2))
        settings_db.set("volume", self.slider_volume.value())
        if self.tts and hasattr(self.tts, "set_volume"):
            self.tts.set_volume(self.slider_volume.value() / 100.0)
        settings_db.set("bubble_transparency", self.slider_transparency.value())
        settings_db.set("bubble_size", self.seg_bubble_size.value() or "Large")
        settings_db.set("bubble_distance", self.slider_distance.value())
        settings_db.set("bubble_corner_radius", self.current_corner_radius)
        settings_db.set("bubble_appearance", self.current_bubble_style)
        settings_db.set("smooth_fade_in", self.switch_fade_in.isChecked())
        settings_db.set("settings_theme", self.theme_pref)
        set_startup_enabled(self.chk_startup.isChecked())
        self.settings_applied.emit()
        self.close()
