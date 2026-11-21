"""
Voxel main window (design v2).

WORKSPACE:   Listen · Read Text · Resources · History
PREFERENCES: Settings (General, Voice, Playback, Appearance, Accessibility, About)

- Collapsible sidebar; the last opened page and sidebar state are remembered.
- Settings apply immediately (debounced); no Save button. Reset to defaults is kept.
- Advanced controls live in fold-away sections.
- Every existing settings key is preserved, so saved preferences carry over.

The class keeps its historical name (SettingsDialog) and public API so main.py keeps working.
"""
import os
import tempfile
import time
from typing import Optional, List, Dict, Callable

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget, QScrollArea, QWidget, QLabel, QComboBox,
    QPushButton, QFrame, QButtonGroup, QSlider, QFileDialog, QPlainTextEdit, QSizePolicy,
    QApplication, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import QSize, Qt, QUrl, pyqtSignal, QTimer, QRectF, QPointF, QVariantAnimation, QEasingCurve
from PyQt6.QtGui import (
    QGuiApplication, QCursor, QDesktopServices, QPainter, QColor, QPen, QImage, QShortcut, QKeySequence,
    QFontMetrics
)

from src.config import VOICES, EMOTION_MODES, DEFAULT_EMOTION_MODE, VERSION, GITHUB_URL, APP_NAME, IS_MAC, COMPANY_NAME, COMPANY_URL
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from src.utils.startup import is_startup_enabled, set_startup_enabled
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from src.utils.audio_recorder import get_recordings_dir, open_recordings_folder
from src.utils.history import history_db
from src.utils.library import library_db
from src.ui.equalizer_widget import VoiceEqualizerWidget
from src.ui.design import PALETTES, FONT_STACK, resolve_theme, line_icon, THEME_PREFS
from assets.icons import create_app_icon, get_brand_logo_pixmap

LINKEDIN_URL = "https://www.linkedin.com/in/fahimdigital/"


def _icon_file(name: str, color: str, draw: Callable[[QPainter], None]) -> str:
    path = os.path.join(tempfile.gettempdir(), f"voxel_{name}_{color.strip('#')}.png")
    if not os.path.exists(path):
        img = QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(color), 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
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
    """Animated pill switch."""
    toggled = pyqtSignal(bool)

    def __init__(self, checked: bool = True, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._checked = checked
        self._pos = 1.0 if checked else 0.0
        self.palette_ = PALETTES["light"]
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(150)
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

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.setChecked(not self._checked)
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        off, on = QColor(self.palette_["track_off"]), QColor(self.palette_["accent"])
        t = self._pos
        track = QColor(int(off.red() + (on.red() - off.red()) * t), int(off.green() + (on.green() - off.green()) * t),
                       int(off.blue() + (on.blue() - off.blue()) * t))
        if not self.isEnabled():
            track.setAlpha(110)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(QRectF(0, 0, w, h), h / 2, h / 2)
        if self.hasFocus():
            p.setPen(QPen(on, 1.5)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(0.75, 0.75, w - 1.5, h - 1.5), h / 2, h / 2)
            p.setPen(Qt.PenStyle.NoPen)
        d = h - 6
        x = 3 + (w - d - 6) * t
        p.setBrush(QColor(0, 0, 0, 25))
        p.drawEllipse(QRectF(x, 3.6, d, d))
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QRectF(x, 3, d, d))
        p.end()


class Segmented(QFrame):
    """Pill-style segmented control."""
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
        else:  # value not offered (e.g. a legacy option): show nothing selected
            self._group.setExclusive(False)
            for btn in self._buttons.values():
                btn.setChecked(False)
            self._group.setExclusive(True)


class Card(QFrame):
    """Rounded surface with an optional title; rows are separated by thin dividers."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(18, 14, 18, 12)
        self._lay.setSpacing(0)
        self._rows = 0
        if title:
            t = QLabel(title, self)
            t.setObjectName("CardTitle")
            self._lay.addWidget(t)
            self._lay.addSpacing(4)

    def add(self, widget: QWidget, divider: bool = True):
        if self._rows and divider:
            d = QFrame(self)
            d.setObjectName("Divider")
            d.setFixedHeight(1)
            self._lay.addWidget(d)
        self._lay.addWidget(widget)
        self._rows += 1
        return widget


class Collapsible(QWidget):
    """'More options' / 'Advanced' section that folds away."""

    def __init__(self, title: str = "Advanced", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(0)
        self.header = QPushButton(title, self)
        self.header.setObjectName("Fold")
        self.header.setCheckable(True)
        self.header.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.header.toggled.connect(self._toggle)
        lay.addWidget(self.header, 0, Qt.AlignmentFlag.AlignLeft)
        self.body = QWidget(self)
        self.body_lay = QVBoxLayout(self.body)
        self.body_lay.setContentsMargins(0, 0, 0, 0)
        self.body_lay.setSpacing(0)
        self.body.setVisible(False)
        lay.addWidget(self.body)
        self._icons = (None, None)

    def set_icons(self, closed, opened):
        self._icons = (closed, opened)
        self.header.setIcon(opened if self.header.isChecked() else closed)

    def _toggle(self, on: bool):
        self.body.setVisible(on)
        if self._icons[0] is not None:
            self.header.setIcon(self._icons[1] if on else self._icons[0])

    def add(self, widget: QWidget):
        if self.body_lay.count():
            d = QFrame(self.body)
            d.setObjectName("Divider")
            d.setFixedHeight(1)
            self.body_lay.addWidget(d)
        self.body_lay.addWidget(widget)
        return widget


def setting_row(title: str, control: Optional[QWidget] = None, hint: str = "", stretch_control: bool = False) -> QWidget:
    row = QWidget()
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 10, 0, 10)
    lay.setSpacing(16)
    col = QVBoxLayout()
    col.setSpacing(1)
    lt = QLabel(title)
    lt.setObjectName("RowTitle")
    col.addWidget(lt)
    if hint:
        lh = QLabel(hint)
        lh.setObjectName("RowHint")
        lh.setWordWrap(True)
        col.addWidget(lh)
    lay.addLayout(col, 1)
    if control is not None:
        if stretch_control:
            lay.addWidget(control, 2)
        else:
            lay.addWidget(control, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    row.title_label = lt
    return row


class SliderRow(QWidget):
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
        self.slider.setMinimumWidth(120)
        self.slider.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.slider.setAccessibleName(title)
        lay.addWidget(self.slider, 2)
        self.pill = QLabel()
        self.pill.setObjectName("Pill")
        self.pill.setFixedWidth(60)
        self.pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.pill)
        self.slider.valueChanged.connect(lambda v: self.pill.setText(self.fmt(v)))
        self.slider.setValue(value)
        self.pill.setText(self.fmt(value))


class EqualizerPreviewWidget(QWidget):
    """Small animated spectrum; lively while speaking, calm when idle."""

    def __init__(self, width: int = 150, bars: int = 14, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, 24)
        self.is_active = False
        self.num_bars = bars
        self._levels = [0.12] * bars
        self._phase = 0.0
        self.color = QColor("#3478F6")
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
        t, n = self._phase, self.num_bars
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
        n, bw = self.num_bars, 4.0
        gap = (w - n * bw) / max(1, n - 1)
        p.setPen(Qt.PenStyle.NoPen)
        c = QColor(self.color)
        if not self.is_active:
            c = QColor(150, 150, 150, 90)
        p.setBrush(c)
        for i, lvl in enumerate(self._levels):
            bh = max(4.0, h * lvl)
            p.drawRoundedRect(QRectF(i * (bw + gap), (h - bh) / 2, bw, bh), 2, 2)
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Main window
# ─────────────────────────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()
    test_bubble_requested = pyqtSignal()
    read_text_requested = pyqtSignal(str)

    PAGE_LISTEN, PAGE_READ, PAGE_RESOURCES, PAGE_HISTORY, PAGE_SETTINGS = range(5)
    PAGE_KEYS = {0: "listen", 1: "read", 2: "resources", 3: "history", 4: "settings"}

    def __init__(self, tts_engine: Optional[TTSEngine] = None, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.theme_pref = settings_db.get("settings_theme", "light")
        if self.theme_pref not in THEME_PREFS:
            self.theme_pref = "light"
        self.current_theme = resolve_theme(self.theme_pref)
        self.current_bubble_style = "Frosted Glass"
        self.current_corner_radius = "Medium"
        self.nav_buttons: List[QPushButton] = []
        self.switches: List[ToggleSwitch] = []
        self._folds: List[Collapsible] = []
        self._test_running = False
        self._loading = False
        self._editing_text_id: Optional[str] = None   # saved-text item open in Read Text
        self._collapsed = bool(settings_db.get("ui_sidebar_collapsed", False))

        self._apply_timer = QTimer(self)
        self._apply_timer.setSingleShot(True)
        self._apply_timer.setInterval(350)
        self._apply_timer.timeout.connect(self._apply_now)

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(create_app_icon(64))
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(720, 480)  # fits 1080p screens at 200% scaling
        self.resize(920, 660)

        self._init_ui()
        if self.tts:
            self.tts.playback_started.connect(self._on_tts_started)
            self.tts.playback_finished.connect(self._on_tts_finished)
            self.tts.playback_paused.connect(lambda: self._set_status("Paused"))
            self.tts.playback_resumed.connect(lambda: self._set_status("Reading"))
            self.tts.chunk_progress.connect(self._on_chunk_progress)
            if hasattr(self.tts, "playback_error"):
                self.tts.playback_error.connect(lambda _m: self._on_tts_finished())
        self.apply_theme(self.theme_pref)
        try:
            QGuiApplication.styleHints().colorSchemeChanged.connect(
                lambda _s: self.apply_theme("system") if self.theme_pref == "system" else None)
        except Exception:
            pass
        self.load_values()
        self._set_sidebar_collapsed(self._collapsed)
        last = settings_db.get("ui_last_page", "listen")
        self._go_to(next((k for k, v in self.PAGE_KEYS.items() if v == last), self.PAGE_LISTEN), remember=False)

    # ── Shell ───────────────────────────────────────────────────────────────
    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar_widget = QFrame(self)
        self.sidebar_widget.setObjectName("Sidebar")
        side = QVBoxLayout(self.sidebar_widget)
        side.setContentsMargins(12, 16, 12, 14)
        side.setSpacing(2)

        top = QHBoxLayout()
        top.setContentsMargins(4, 0, 0, 0)
        self.lbl_sidebar_logo = QLabel(self.sidebar_widget)
        self.lbl_sidebar_logo.setFixedHeight(36)
        top.addWidget(self.lbl_sidebar_logo)
        top.addStretch()
        self.btn_collapse = QPushButton(self.sidebar_widget)
        self.btn_collapse.setObjectName("IconBtn")
        self.btn_collapse.setFixedSize(30, 30)
        self.btn_collapse.setIconSize(QSize(18, 18))
        self.btn_collapse.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_collapse.setToolTip("Collapse sidebar")
        self.btn_collapse.clicked.connect(lambda: self._set_sidebar_collapsed(not self._collapsed, remember=True))
        top.addWidget(self.btn_collapse)
        side.addLayout(top)
        side.addSpacing(16)

        self.pages_meta = [
            (self.PAGE_LISTEN, "Listen", "headphones", "Listen", "Select text anywhere, then click the wave."),
            (self.PAGE_READ, "Read Text", "file-text", "Read Text", "Paste any text and listen."),
            (self.PAGE_RESOURCES, "Resources", "folder", "Resources", "Saved text, bookmarks and recordings."),
            (self.PAGE_HISTORY, "History", "history", "History", "Everything Voxel has read for you."),
            (self.PAGE_SETTINGS, "Settings", "settings-2", "Settings", "Changes are saved automatically."),
        ]
        self._section_labels = []
        self.btn_group_nav = QButtonGroup(self)
        self._nav_by_page: Dict[int, QPushButton] = {}
        for page, label, icon, _t, _s in self.pages_meta:
            if page == self.PAGE_LISTEN:
                self._add_section_label(side, "WORKSPACE")
            if page == self.PAGE_SETTINGS:
                side.addSpacing(14)
                self._add_section_label(side, "PREFERENCES")
            b = QPushButton(label, self.sidebar_widget)
            b.setObjectName("NavBtn")
            b.setCheckable(True)
            b.setIconSize(QSize(18, 18))
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setToolTip(label)
            b.setAccessibleName(label)
            b.clicked.connect(lambda _=False, p=page: self._go_to(p))
            b._label = label
            self.btn_group_nav.addButton(b)
            self.nav_buttons.append(b)
            self._nav_by_page[page] = b
            side.addWidget(b)
        side.addStretch()
        self.lbl_ver = QLabel(f"{VERSION}", self.sidebar_widget)
        self.lbl_ver.setObjectName("Faint")
        self.lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side.addWidget(self.lbl_ver)
        root.addWidget(self.sidebar_widget)

        main = QWidget(self)
        main.setObjectName("Main")
        col = QVBoxLayout(main)
        col.setContentsMargins(32, 26, 32, 22)
        col.setSpacing(16)
        head = QVBoxLayout()
        head.setSpacing(3)
        self.lbl_header_title = QLabel("", main)
        self.lbl_header_title.setObjectName("PageTitle")
        self.lbl_header_subtitle = QLabel("", main)
        self.lbl_header_subtitle.setObjectName("PageSub")
        head.addWidget(self.lbl_header_title)
        head.addWidget(self.lbl_header_subtitle)
        col.addLayout(head)

        self.stacked_pages = QStackedWidget(main)
        self.stacked_pages.addWidget(self._create_listen_page())
        self.stacked_pages.addWidget(self._create_read_page())
        self.stacked_pages.addWidget(self._create_resources_page())
        self.stacked_pages.addWidget(self._create_history_page())
        self.stacked_pages.addWidget(self._create_settings_page())
        col.addWidget(self.stacked_pages, 1)
        root.addWidget(main, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        narrow = self.width() < 900
        want = True if narrow else bool(settings_db.get("ui_sidebar_collapsed", False))
        if want != self._collapsed:
            self._set_sidebar_collapsed(want)

    def _add_section_label(self, layout, text):
        l = QLabel(text, self.sidebar_widget)
        l.setObjectName("Section")
        layout.addWidget(l)
        layout.addSpacing(2)
        self._section_labels.append(l)

    def _set_sidebar_collapsed(self, collapsed: bool, remember: bool = False):
        self._collapsed = collapsed
        self.sidebar_widget.setFixedWidth(64 if collapsed else 212)
        for b in self.nav_buttons:
            b.setText("" if collapsed else b._label)
        for l in self._section_labels:
            l.setVisible(not collapsed)
        self.lbl_ver.setVisible(not collapsed)
        self.btn_collapse.setToolTip("Expand sidebar" if collapsed else "Collapse sidebar")
        self._update_sidebar_logo()
        if remember:
            settings_db.set("ui_sidebar_collapsed", collapsed)

    @staticmethod
    def _scroll(builder: Callable[[QVBoxLayout], None]) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("ScrollContent")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(0, 0, 10, 6)
        lay.setSpacing(14)
        builder(lay)
        lay.addStretch()
        scroll.setWidget(content)
        scroll.viewport().setAutoFillBackground(False)
        return scroll

    def _switch(self) -> ToggleSwitch:
        s = ToggleSwitch(True)
        s.toggled.connect(self._schedule_apply)
        self.switches.append(s)
        return s

    def _btn(self, text: str, kind: str = "BtnSoft") -> QPushButton:
        b = QPushButton(text)
        b.setObjectName(kind)
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return b

    def _fold(self, title: str) -> Collapsible:
        f = Collapsible(title)
        self._folds.append(f)
        return f

    # ── Listen ──────────────────────────────────────────────────────────────
    def _create_listen_page(self) -> QWidget:
        def build(l: QVBoxLayout):
            c = Card()
            hero = QWidget()
            hl = QHBoxLayout(hero)
            hl.setContentsMargins(0, 10, 0, 10)
            hl.setSpacing(16)
            self.lbl_listen_mark = QLabel()
            self.lbl_listen_mark.setPixmap(create_app_icon(56).pixmap(56, 56))
            hl.addWidget(self.lbl_listen_mark)
            tc = QVBoxLayout()
            tc.setSpacing(4)
            t1 = QLabel("Select text, click the wave, listen.")
            t1.setObjectName("HeroTitle")
            t2 = QLabel("Works in any app: browser, Word, PDF. Use Read Text when an app blocks selection.")
            t2.setObjectName("RowHint")
            t2.setWordWrap(True)
            tc.addWidget(t1)
            tc.addWidget(t2)
            hl.addLayout(tc, 1)
            c.add(hero, divider=False)
            self.sw_listen_selection = ToggleSwitch(True)
            self.switches.append(self.sw_listen_selection)
            c.add(setting_row("Read selected text", self.sw_listen_selection, "Show the floating bubble when you highlight text"))
            l.addWidget(c)

            c = Card("Now playing")
            np = QWidget()
            nl = QVBoxLayout(np)
            nl.setContentsMargins(0, 6, 0, 8)
            nl.setSpacing(6)
            self.lbl_listen_status = QLabel("Nothing playing")
            self.lbl_listen_status.setObjectName("Status")
            nl.addWidget(self.lbl_listen_status)
            self.lbl_listen_preview = QLabel("")
            self.lbl_listen_preview.setObjectName("RowHint")
            self.lbl_listen_preview.setWordWrap(True)
            nl.addWidget(self.lbl_listen_preview)
            br = QHBoxLayout()
            br.setSpacing(8)
            self.btn_listen_pause = self._btn(" Pause")
            self.btn_listen_pause.clicked.connect(self._toggle_pause)
            self.btn_listen_stop = self._btn(" Stop", "BtnGhost")
            self.btn_listen_stop.clicked.connect(self._stop_all)
            self.btn_listen_replay = self._btn(" Play again")
            self.btn_listen_replay.clicked.connect(self._replay_last)
            for b in (self.btn_listen_pause, self.btn_listen_stop, self.btn_listen_replay):
                br.addWidget(b)
            br.addStretch()
            nl.addLayout(br)
            c.add(np, divider=False)
            l.addWidget(c)

            c = Card("Shortcuts")
            mod = "⌘ ⌥" if IS_MAC else "Ctrl Alt"
            for label, key in [("Read selected text", f"{mod} S"), ("Read the whole document", f"{mod} D"),
                               ("Read pasted text", f"{'⌘' if IS_MAC else 'Ctrl'} Enter")]:
                k = QLabel(key)
                k.setObjectName("Kbd")
                c.add(setting_row(label, k))
            l.addWidget(c)
        return self._scroll(build)

    # ── Read Text ───────────────────────────────────────────────────────────
    def _create_read_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        self.txt_reader = QPlainTextEdit(page)
        self.txt_reader.setObjectName("Reader")
        self.txt_reader.setPlaceholderText("Paste or type text here…")
        self.txt_reader.textChanged.connect(self._update_reader_count)
        lay.addWidget(self.txt_reader, 1)

        bar = QFrame(page)
        bar.setObjectName("Bar")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10, 8, 10, 8)
        bl.setSpacing(8)
        self.btn_paste = self._btn(" Paste")
        self.btn_paste.clicked.connect(self._paste_into_reader)
        bl.addWidget(self.btn_paste)
        self.btn_clear = self._btn(" Clear", "BtnGhost")
        self.btn_clear.clicked.connect(self._clear_reader)
        bl.addWidget(self.btn_clear)
        self.btn_save_text = self._btn(" Save", "BtnGhost")
        self.btn_save_text.setToolTip("Keep this text in Resources")
        self.btn_save_text.clicked.connect(self._save_reader_text)
        bl.addWidget(self.btn_save_text)
        bl.addStretch()
        info = QHBoxLayout()
        info.setContentsMargins(4, 0, 4, 0)
        self.lbl_reader_count = QLabel("")
        self.lbl_reader_count.setObjectName("RowHint")
        info.addWidget(self.lbl_reader_count)
        info.addStretch()
        self.lbl_reader_status = QLabel("")
        self.lbl_reader_status.setObjectName("RowHint")
        info.addWidget(self.lbl_reader_status)
        self.reader_viz = EqualizerPreviewWidget(90, 11, page)
        info.addWidget(self.reader_viz)
        lay.addLayout(info)
        self.btn_reader_pause = self._btn(" Pause")
        self.btn_reader_pause.clicked.connect(self._toggle_pause)
        bl.addWidget(self.btn_reader_pause)
        self.btn_read = self._btn(" Read aloud", "BtnPrimary")
        self.btn_read.setToolTip("Ctrl+Enter")
        self.btn_read.clicked.connect(self._toggle_read)
        bl.addWidget(self.btn_read)
        lay.addWidget(bar)

        QShortcut(QKeySequence("Ctrl+Return"), self.txt_reader, activated=self._toggle_read)
        QShortcut(QKeySequence("Ctrl+Enter"), self.txt_reader, activated=self._toggle_read)
        self._update_reader_count()
        return page

    def _clear_reader(self):
        self.txt_reader.clear()
        self._editing_text_id = None

    def _save_reader_text(self):
        item = library_db.save_text(self.txt_reader.toPlainText(), item_id=self._editing_text_id)
        if item:
            self._editing_text_id = item["id"]
            self.lbl_reader_status.setText("Saved to Resources")
            QTimer.singleShot(2500, lambda: self.lbl_reader_status.setText("")
                              if self.lbl_reader_status.text() == "Saved to Resources" else None)

    def _paste_into_reader(self):
        text = QApplication.clipboard().text()
        if text:
            self.txt_reader.setPlainText(text.strip())
            self._editing_text_id = None   # pasted text is a new item, not an edit
            self.txt_reader.setFocus()

    def _update_reader_count(self):
        words = len(self.txt_reader.toPlainText().split())
        if not words:
            self.lbl_reader_count.setText("No text yet")
            return
        speed = max(0.5, self.slider_speed.value() / 100.0) if hasattr(self, "slider_speed") else 1.0
        mins = words / (150.0 * speed)
        self.lbl_reader_count.setText(f"{words:,} words · {'< 1 min' if mins < 1 else f'~{round(mins)} min'}")

    def _toggle_read(self):
        if self.tts and self.tts.is_speaking:
            self._stop_all()
            return
        text = self.txt_reader.toPlainText().strip()
        if not text:
            self.txt_reader.setFocus()
            return
        self._apply_voice_choice()
        self._speak(text)

    def _speak(self, text: str):
        if self.receivers(self.read_text_requested) > 0:
            self.read_text_requested.emit(text)
        elif self.tts:
            self.tts.speak(text)
        self._set_status("Preparing…")
        self._set_reading_ui(True)

    def _toggle_pause(self):
        if not (self.tts and self.tts.is_speaking):
            return
        if self.tts.is_paused:
            self.tts.resume()
        else:
            self.tts.pause()
        self._refresh_pause_buttons()

    def _stop_all(self):
        if self.tts:
            self.tts.stop()
        self._on_tts_finished()

    def _replay_last(self):
        text = getattr(self.tts, "current_text", "") if self.tts else ""
        if text:
            self._speak(text)

    def _set_reading_ui(self, active: bool):
        self.btn_read.setText(" Stop" if active else " Read aloud")
        if hasattr(self, "_icon_play"):
            self.btn_read.setIcon(self._icon_stop if active else self._icon_play)
        self.reader_viz.set_active(active)
        self._refresh_pause_buttons()

    def _refresh_pause_buttons(self):
        speaking = bool(self.tts and self.tts.is_speaking)
        paused = bool(speaking and self.tts.is_paused)
        for b in (self.btn_reader_pause, self.btn_listen_pause):
            b.setEnabled(speaking)
            b.setText(" Resume" if paused else " Pause")
            if hasattr(self, "_icon_pause_soft"):
                b.setIcon(self._icon_play_soft if paused else self._icon_pause_soft)
        self.btn_listen_stop.setEnabled(speaking)
        self.btn_listen_replay.setVisible(not speaking and bool(getattr(self.tts, "current_text", "") if self.tts else ""))

    def _set_status(self, text: str):
        self.lbl_reader_status.setText(text)
        self.lbl_listen_status.setText(text if text else "Nothing playing")
        self._refresh_pause_buttons()

    # ── Resources ───────────────────────────────────────────────────────────
    def _create_resources_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        self.seg_resources = Segmented([("Saved text", "texts"), ("Bookmarks", "bookmarks"), ("Recordings", "recordings")])
        self.seg_resources.changed.connect(self._show_resource_tab)
        lay.addWidget(self.seg_resources, 0, Qt.AlignmentFlag.AlignLeft)
        self.res_stack = QStackedWidget()
        lay.addWidget(self.res_stack, 1)

        def tab(empty_text: str):
            w = QWidget()
            v = QVBoxLayout(w)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(10)
            lst = QListWidget()
            lst.setObjectName("List")
            lst.setWordWrap(True)
            v.addWidget(lst, 1)
            empty = QLabel(empty_text)
            empty.setObjectName("RowHint")
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(empty, 1)
            row = QHBoxLayout()
            row.setSpacing(8)
            v.addLayout(row)
            self.res_stack.addWidget(w)
            return lst, empty, row

        # Saved text
        self.list_texts, self.lbl_texts_empty, row = tab("No saved text yet. In Read Text, press Save to keep a text here.")
        self.list_texts.itemDoubleClicked.connect(lambda _i: self._open_saved_text())
        self.btn_text_open = self._btn(" Open in Read Text")
        self.btn_text_open.clicked.connect(self._open_saved_text)
        self.btn_text_read = self._btn(" Read aloud", "BtnGhost")
        self.btn_text_read.clicked.connect(lambda: self._speak_item(self.list_texts))
        self.btn_text_delete = self._btn(" Delete", "BtnGhost")
        self.btn_text_delete.clicked.connect(self._delete_saved_text)
        row.addWidget(self.btn_text_open); row.addWidget(self.btn_text_read); row.addStretch(); row.addWidget(self.btn_text_delete)

        # Bookmarks
        self.list_bookmarks, self.lbl_bookmarks_empty, row = tab("No bookmarks yet. In History, press Bookmark to keep an item for good.")
        self.list_bookmarks.itemDoubleClicked.connect(lambda _i: self._speak_item(self.list_bookmarks))
        self.btn_bm_read = self._btn(" Read aloud")
        self.btn_bm_read.clicked.connect(lambda: self._speak_item(self.list_bookmarks))
        self.btn_bm_copy = self._btn(" Copy text", "BtnGhost")
        self.btn_bm_copy.clicked.connect(lambda: self._copy_item(self.list_bookmarks))
        self.btn_bm_remove = self._btn(" Remove", "BtnGhost")
        self.btn_bm_remove.clicked.connect(self._remove_bookmark)
        row.addWidget(self.btn_bm_read); row.addWidget(self.btn_bm_copy); row.addStretch(); row.addWidget(self.btn_bm_remove)

        # Recordings (MP3 files in the recordings folder)
        self.list_recordings, self.lbl_rec_empty, row = tab("No recordings yet. In the mini player choose More → Record to MP3.")
        self.list_recordings.itemDoubleClicked.connect(self._play_recording)
        self.btn_rec_play = self._btn(" Play")
        self.btn_rec_play.clicked.connect(lambda: self._play_recording(self.list_recordings.currentItem()))
        self.btn_rec_open = self._btn(" Open folder", "BtnGhost")
        self.btn_rec_open.clicked.connect(open_recordings_folder)
        row.addWidget(self.btn_rec_play); row.addStretch(); row.addWidget(self.btn_rec_open)

        self.seg_resources.set_value(settings_db.get("ui_resources_tab", "texts") or "texts")
        self.res_stack.setCurrentIndex(["texts", "bookmarks", "recordings"].index(self.seg_resources.value() or "texts"))
        return page

    def _show_resource_tab(self, key: str):
        keys = ["texts", "bookmarks", "recordings"]
        self.res_stack.setCurrentIndex(keys.index(key) if key in keys else 0)
        settings_db.set("ui_resources_tab", key)
        self._load_resources()

    def _load_resources(self):
        self._fill(self.list_texts, self.lbl_texts_empty, library_db.saved_texts(),
                   lambda i: f"{i.get('title', 'Untitled')}\n{len(i.get('text', '').split()):,} words · saved {i.get('updated', '')}",
                   (self.btn_text_open, self.btn_text_read, self.btn_text_delete))
        self._fill(self.list_bookmarks, self.lbl_bookmarks_empty, library_db.bookmarks(),
                   lambda i: f"{i.get('title', '')}\n{i.get('voice', '')} · {i.get('speed', 1.0)}× · {i.get('read_at') or i.get('created', '')}",
                   (self.btn_bm_read, self.btn_bm_copy, self.btn_bm_remove))
        self._load_recordings()

    @staticmethod
    def _fill(lst: QListWidget, empty: QLabel, items, fmt, buttons):
        lst.clear()
        for i in items:
            it = QListWidgetItem(fmt(i))
            it.setData(Qt.ItemDataRole.UserRole, i)
            lst.addItem(it)
        has = lst.count() > 0
        lst.setVisible(has)
        empty.setVisible(not has)
        for b in buttons:
            b.setVisible(has)
        if has:
            lst.setCurrentRow(0)

    @staticmethod
    def _item(lst: QListWidget):
        it = lst.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else None

    def _speak_item(self, lst: QListWidget):
        item = self._item(lst)
        if item and item.get("text"):
            self._apply_voice_choice()
            self._speak(item["text"])

    def _copy_item(self, lst: QListWidget):
        item = self._item(lst)
        if item:
            QApplication.clipboard().setText(item.get("text", ""))

    def _open_saved_text(self):
        item = self._item(self.list_texts)
        if item:
            self.txt_reader.setPlainText(item.get("text", ""))
            self._editing_text_id = item.get("id")
            self._go_to(self.PAGE_READ)
            self.txt_reader.setFocus()

    def _delete_saved_text(self):
        item = self._item(self.list_texts)
        if not item:
            return
        ok = QMessageBox.question(self, "Delete saved text", f"Delete “{item.get('title', '')}”?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                  QMessageBox.StandardButton.No)
        if ok == QMessageBox.StandardButton.Yes:
            library_db.delete_text(item.get("id"))
            if self._editing_text_id == item.get("id"):
                self._editing_text_id = None
            self._load_resources()

    def _remove_bookmark(self):
        item = self._item(self.list_bookmarks)
        if item:
            library_db.remove_bookmark(item_id=item.get("id"))
            self._load_resources()

    def _load_recordings(self):
        self.list_recordings.clear()
        folder = str(get_recordings_dir())
        files = []
        try:
            for n in os.listdir(folder):
                if n.lower().endswith((".mp3", ".wav", ".m4a")):
                    fp = os.path.join(folder, n)
                    files.append((os.path.getmtime(fp), fp))
        except Exception:
            pass
        for mtime, fp in sorted(files, reverse=True):
            size_kb = os.path.getsize(fp) / 1024.0
            meta = time.strftime("%d %b %Y, %H:%M", time.localtime(mtime))
            size = f"{size_kb / 1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
            it = QListWidgetItem(f"{os.path.basename(fp)}\n{meta} · {size}")
            it.setData(Qt.ItemDataRole.UserRole, fp)
            self.list_recordings.addItem(it)
        has = self.list_recordings.count() > 0
        self.list_recordings.setVisible(has)
        self.lbl_rec_empty.setVisible(not has)
        self.btn_rec_play.setVisible(has)
        if has:
            self.list_recordings.setCurrentRow(0)

    def _play_recording(self, item):
        if item:
            QDesktopServices.openUrl(QUrl.fromLocalFile(item.data(Qt.ItemDataRole.UserRole)))

    # ── History ─────────────────────────────────────────────────────────────
    def _create_history_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        self.list_history = QListWidget()
        self.list_history.setObjectName("List")
        self.list_history.setWordWrap(True)
        self.list_history.itemDoubleClicked.connect(lambda _i: self._history_replay())
        lay.addWidget(self.list_history, 1)
        self.lbl_hist_empty = QLabel("Nothing read yet. Select text anywhere and click the wave.")
        self.lbl_hist_empty.setObjectName("RowHint")
        self.lbl_hist_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.lbl_hist_empty, 1)
        row = QHBoxLayout()
        row.setSpacing(8)
        self.btn_hist_replay = self._btn(" Replay")
        self.btn_hist_replay.clicked.connect(self._history_replay)
        self.btn_hist_copy = self._btn(" Copy text", "BtnGhost")
        self.btn_hist_copy.clicked.connect(self._history_copy)
        self.btn_hist_bookmark = self._btn(" Bookmark", "BtnGhost")
        self.btn_hist_bookmark.setToolTip("Keep this item in Resources, even after History removes it")
        self.btn_hist_bookmark.clicked.connect(self._history_toggle_bookmark)
        self.list_history.currentItemChanged.connect(lambda *_: self._refresh_bookmark_button())
        self.btn_hist_clear = self._btn(" Clear history", "BtnGhost")
        self.btn_hist_clear.clicked.connect(self._history_clear)
        row.addWidget(self.btn_hist_replay)
        row.addWidget(self.btn_hist_copy)
        row.addWidget(self.btn_hist_bookmark)
        row.addStretch()
        row.addWidget(self.btn_hist_clear)
        lay.addLayout(row)
        return page

    def _load_history(self):
        self.list_history.clear()
        try:
            entries = history_db.get_all()
        except Exception:
            entries = []
        for e in entries:
            preview = e.get("preview") or e.get("text", "")[:80]
            star = "★  " if library_db.is_bookmarked(e.get("text", "")) else ""
            meta = f"{star}{e.get('voice', '')} · {e.get('speed', 1.0)}× · {e.get('timestamp', '')}"
            it = QListWidgetItem(f"{preview}\n{meta}")
            it.setData(Qt.ItemDataRole.UserRole, e.get("text", ""))
            it.setData(Qt.ItemDataRole.UserRole + 1, e)
            self.list_history.addItem(it)
        has = self.list_history.count() > 0
        self.list_history.setVisible(has)
        self.lbl_hist_empty.setVisible(not has)
        for b in (self.btn_hist_replay, self.btn_hist_copy, self.btn_hist_bookmark, self.btn_hist_clear):
            b.setEnabled(has)
        if has:
            self.list_history.setCurrentRow(0)
        self._refresh_bookmark_button()

    def _refresh_bookmark_button(self):
        text = self._history_text()
        self.btn_hist_bookmark.setText(" Bookmarked" if text and library_db.is_bookmarked(text) else " Bookmark")

    def _history_toggle_bookmark(self):
        it = self.list_history.currentItem()
        if not it:
            return
        text = it.data(Qt.ItemDataRole.UserRole)
        if library_db.is_bookmarked(text):
            library_db.remove_bookmark(text=text)
        else:
            e = it.data(Qt.ItemDataRole.UserRole + 1) or {}
            library_db.add_bookmark(text, e.get("voice", ""), e.get("speed", 1.0), e.get("timestamp", ""))
        row = self.list_history.currentRow()
        self._load_history()
        self.list_history.setCurrentRow(row)

    def _history_text(self) -> str:
        it = self.list_history.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else ""

    def _history_replay(self):
        text = self._history_text()
        if text:
            self._speak(text)

    def _history_copy(self):
        text = self._history_text()
        if text:
            QApplication.clipboard().setText(text)

    def _history_clear(self):
        ok = QMessageBox.question(self, "Clear history", "Delete all history? This cannot be undone.",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                  QMessageBox.StandardButton.No)
        if ok == QMessageBox.StandardButton.Yes:
            history_db.clear()
            self._load_history()

    # ── Settings ────────────────────────────────────────────────────────────
    def _create_settings_page(self) -> QWidget:
        def build(l: QVBoxLayout):
            # GENERAL
            c = Card("General")
            self.chk_startup = self._switch()
            c.add(setting_row("Start at login", self.chk_startup))
            self.chk_trigger = self._switch()
            c.add(setting_row("Show floating bubble on selection", self.chk_trigger))
            f = self._fold("More options")
            self.chk_prebuffer = self._switch()
            f.add(setting_row("Instant start", self.chk_prebuffer, "Prepare audio when you hover the bubble"))
            c.add(f, divider=False)
            l.addWidget(c)

            # VOICE
            c = Card("Voice")
            self.combo_voice = QComboBox()
            for v in VOICES:
                self.combo_voice.addItem(v["label"], v["id"])
            self.combo_voice.setMinimumWidth(200)
            self.combo_voice.setMaximumWidth(320)
            self.combo_voice.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
            self.combo_voice.currentIndexChanged.connect(self._schedule_apply)
            c.add(setting_row("Voice", self.combo_voice))
            self.row_speed = SliderRow("Reading speed", 50, 200, 100, lambda v: f"{v / 100:.2f}×")
            self.slider_speed = self.row_speed.slider
            self.lbl_speed_val = self.row_speed.pill
            self.slider_speed.valueChanged.connect(self._on_speed_slider_changed)
            c.add(self.row_speed)
            self.combo_emotion = QComboBox()
            for m in EMOTION_MODES:
                short, _, detail = m["label"].partition(" (")
                self.combo_emotion.addItem(short, m["id"])
                if detail:
                    self.combo_emotion.setItemData(self.combo_emotion.count() - 1, detail.rstrip(")"), Qt.ItemDataRole.ToolTipRole)
            self.combo_emotion.setMinimumWidth(200)
            self.combo_emotion.setMaximumWidth(320)
            self.combo_emotion.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
            self.combo_emotion.currentIndexChanged.connect(self._schedule_apply)
            c.add(setting_row("Tone", self.combo_emotion))
            test = QWidget()
            tl = QHBoxLayout(test)
            tl.setContentsMargins(0, 8, 0, 8)
            tl.setSpacing(10)
            self.btn_test_perf = self._btn(" Test voice")
            self.btn_test_perf.clicked.connect(self._run_performance_test)
            tl.addWidget(self.btn_test_perf)
            self.equalizer_preview = EqualizerPreviewWidget(120, 14)
            tl.addWidget(self.equalizer_preview)
            self.lbl_test_status = QLabel("")
            self.lbl_test_status.setObjectName("RowHint")
            tl.addWidget(self.lbl_test_status)
            tl.addStretch()
            c.add(test)
            f = self._fold("Advanced")
            self.row_pitch = SliderRow("Pitch", -50, 50, 0, lambda v: f"{v:+d} Hz" if v else "0 Hz")
            self.slider_pitch = self.row_pitch.slider
            self.lbl_pitch_val = self.row_pitch.pill
            self.slider_pitch.valueChanged.connect(self._on_pitch_slider_changed)
            f.add(self.row_pitch)
            eqw = QWidget()
            el = QVBoxLayout(eqw)
            el.setContentsMargins(0, 10, 0, 10)
            el.setSpacing(6)
            lt = QLabel("Equalizer")
            lt.setObjectName("RowTitle")
            el.addWidget(lt)
            self.equalizer_widget = VoiceEqualizerWidget()
            if hasattr(self.equalizer_widget, "settings_changed"):
                self.equalizer_widget.settings_changed.connect(self._schedule_apply)
            el.addWidget(self.equalizer_widget)
            f.add(eqw)
            c.add(f, divider=False)
            l.addWidget(c)

            # PLAYBACK
            c = Card("Playback")
            self.combo_device = QComboBox()
            self.combo_device.addItem("System default", "default")
            self.combo_device.setMinimumWidth(200)
            self.combo_device.setMaximumWidth(320)
            self.combo_device.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
            c.add(setting_row("Output device", self.combo_device))
            self.row_volume = SliderRow("Volume", 0, 100, 80, lambda v: f"{v}%")
            self.slider_volume = self.row_volume.slider
            self.lbl_vol_val = self.row_volume.pill
            self.slider_volume.valueChanged.connect(self._on_volume_slider_changed)
            c.add(self.row_volume)
            rec_dir = str(get_recordings_dir())
            self.btn_open_recordings = self._btn(" Open folder", "BtnGhost")
            self.btn_open_recordings.clicked.connect(open_recordings_folder)
            rec_row = setting_row("Recordings", self.btn_open_recordings, " ")
            hint = rec_row.findChild(QLabel, "RowHint")
            if hint:
                hint.setWordWrap(False)
                hint.setText(QFontMetrics(hint.font()).elidedText(rec_dir, Qt.TextElideMode.ElideMiddle, 330))
                hint.setToolTip(rec_dir)
            c.add(rec_row)
            self.chk_autoclose = self._switch()
            c.add(setting_row("Close player when finished", self.chk_autoclose))
            self.row_close_delay = SliderRow("Close after", 20, 300, 100, lambda v: f"{v / 100:.1f} s")
            self.slider_fade_out = self.row_close_delay.slider
            self.lbl_fade_out_val = self.row_close_delay.pill
            self.slider_fade_out.valueChanged.connect(self._schedule_apply)
            self.chk_autoclose.toggled.connect(self.row_close_delay.setEnabled)
            c.add(self.row_close_delay)
            f = self._fold("Advanced")
            self.switch_fade_in = self._switch()
            f.add(setting_row("Smooth fade-in", self.switch_fade_in))
            c.add(f, divider=False)
            l.addWidget(c)

            # APPEARANCE
            c = Card("Appearance")
            self.seg_theme = Segmented([("Light", "light"), ("Dark", "dark"), ("System", "system")])
            self.seg_theme.changed.connect(self._on_theme_chosen)
            c.add(setting_row("Theme", self.seg_theme))
            self.seg_bubble_style = Segmented([("Minimal", "Minimal"), ("Frosted", "Frosted Glass")])
            self.seg_bubble_style.changed.connect(self._select_bubble_style)
            c.add(setting_row("Bubble style", self.seg_bubble_style))
            self.seg_bubble_size = Segmented([("Small", "Small Dot"), ("Medium", "Medium"), ("Large", "Large")])
            self.seg_bubble_size.changed.connect(self._schedule_apply)
            c.add(setting_row("Bubble size", self.seg_bubble_size))
            f = self._fold("Advanced")
            self.row_opacity = SliderRow("Opacity", 30, 100, 90, lambda v: f"{v}%")
            self.slider_transparency = self.row_opacity.slider
            self.lbl_trans_val = self.row_opacity.pill
            self.slider_transparency.valueChanged.connect(self._schedule_apply)
            f.add(self.row_opacity)
            self.seg_corner = Segmented([("Square", "Square"), ("Medium", "Medium"), ("Round", "Round")])
            self.seg_corner.changed.connect(self._select_corner_radius)
            f.add(setting_row("Corner radius", self.seg_corner))
            self.row_distance = SliderRow("Distance from text", 15, 75, 28, lambda v: f"{v} px")
            self.slider_distance = self.row_distance.slider
            self.lbl_dist_val = self.row_distance.pill
            self.slider_distance.valueChanged.connect(self._schedule_apply)
            f.add(self.row_distance)
            logo_w = QWidget()
            lw = QHBoxLayout(logo_w)
            lw.setContentsMargins(0, 10, 0, 10)
            lw.setSpacing(10)
            lt = QLabel("Custom logo")
            lt.setObjectName("RowTitle")
            lw.addWidget(lt, 1)
            self.lbl_logo_preview = QLabel()
            lw.addWidget(self.lbl_logo_preview)
            self.btn_change_logo = self._btn(" Change")
            self.btn_change_logo.clicked.connect(self._on_change_logo)
            lw.addWidget(self.btn_change_logo)
            self.btn_restore_logo = self._btn(" Reset", "BtnGhost")
            self.btn_restore_logo.clicked.connect(self._on_restore_default_logo)
            lw.addWidget(self.btn_restore_logo)
            f.add(logo_w)
            c.add(f, divider=False)
            l.addWidget(c)

            # ACCESSIBILITY
            c = Card("Accessibility")
            self.lbl_perm_page_status = QLabel()
            self.lbl_perm_page_status.setObjectName("RowTitle")
            c.add(setting_row("Text selection", self.lbl_perm_page_status))
            if IS_MAC:
                b = self._btn(" Open settings")
                b.clicked.connect(open_accessibility_settings)
                c.add(setting_row("Allow Voxel", b, "System Settings → Privacy & Security → Accessibility → turn Voxel on"))
                from src.utils.mac_permissions import restart_voxel_app
                b = self._btn(" Restart Voxel", "BtnGhost")
                b.clicked.connect(restart_voxel_app)
                c.add(setting_row("After allowing", b, "Restart once so macOS applies the permission"))
            else:
                c.add(setting_row("Windows", None, "No permission is needed. If Windows blocks the app, start it with run.bat (unsigned test build)."))
            b = self._btn(" Show bubble", "BtnGhost")
            b.clicked.connect(lambda: self.test_bubble_requested.emit())
            c.add(setting_row("Test the bubble", b))
            l.addWidget(c)

            # ABOUT
            self.card_about = c = Card("About")
            about = QWidget()
            al = QHBoxLayout(about)
            al.setContentsMargins(0, 10, 0, 10)
            al.setSpacing(14)
            self.lbl_about_logo = QLabel()
            al.addWidget(self.lbl_about_logo)
            ac = QVBoxLayout()
            ac.setSpacing(2)
            v = QLabel(f"Version {VERSION}")
            v.setObjectName("RowTitle")
            ac.addWidget(v)
            d = QLabel(f"Free and open source (MIT) · made by {COMPANY_NAME} · no telemetry")
            d.setObjectName("RowHint")
            ac.addWidget(d)
            al.addLayout(ac, 1)
            c.add(about, divider=False)
            links = QWidget()
            ll = QHBoxLayout(links)
            ll.setContentsMargins(0, 8, 0, 6)
            ll.setSpacing(8)
            for label, url in [("GitHub", GITHUB_URL), (COMPANY_NAME, COMPANY_URL), ("LinkedIn", LINKEDIN_URL)]:
                b = self._btn(f" {label}", "BtnGhost")
                b.clicked.connect(lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u)))
                b._link = True
                ll.addWidget(b)
            ll.addStretch()
            c.add(links)
            l.addWidget(c)

            reset = QHBoxLayout()
            reset.addStretch()
            self.btn_reset_defaults = self._btn(" Reset to defaults", "BtnGhost")
            self.btn_reset_defaults.clicked.connect(self._confirm_reset)
            reset.addWidget(self.btn_reset_defaults)
            l.addLayout(reset)

        self.settings_scroll = self._scroll(build)
        self.sw_listen_selection.toggled.connect(lambda v: self.chk_trigger.setChecked(v))
        self.chk_trigger.toggled.connect(lambda v: self.sw_listen_selection.setChecked(v))
        return self.settings_scroll

    def _refresh_perm_page_status(self):
        if not hasattr(self, "lbl_perm_page_status"):
            return
        pal = PALETTES[self.current_theme]
        if not IS_MAC:
            self.lbl_perm_page_status.setText(f"<span style='color:{pal['ok']}'>● Ready</span>")
        elif is_accessibility_trusted(prompt=False):
            self.lbl_perm_page_status.setText(f"<span style='color:{pal['ok']}'>● Allowed</span>")
        else:
            self.lbl_perm_page_status.setText(f"<span style='color:{pal['warn']}'>● Not allowed yet</span>")

    # ── Handlers ────────────────────────────────────────────────────────────
    def _on_theme_chosen(self, pref):
        self.apply_theme(pref)
        self._schedule_apply()

    def _on_speed_slider_changed(self, val: int):
        if self.tts:
            self.tts.set_speed(round(val / 100.0, 2))
        self._update_reader_count()
        self._schedule_apply()

    def _on_pitch_slider_changed(self, val: int):
        if self.tts and hasattr(self.tts, "set_pitch"):
            self.tts.set_pitch(val)
        self._schedule_apply()

    def _on_volume_slider_changed(self, val: int):
        if self.tts and hasattr(self.tts, "set_volume"):
            self.tts.set_volume(val / 100.0)
        self._schedule_apply()

    def _on_fade_out_slider_changed(self, val: int):
        """Kept for compatibility."""

    def _select_bubble_style(self, style_name: str):
        self.current_bubble_style = style_name or "Frosted Glass"
        self.seg_bubble_style.set_value(self.current_bubble_style)
        self._schedule_apply()

    def _select_corner_radius(self, corner_name: str):
        if corner_name not in ("Square", "Medium", "Round"):
            corner_name = "Medium"
        self.current_corner_radius = corner_name
        self.seg_corner.set_value(corner_name)
        self._schedule_apply()

    def _on_change_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose logo", "", "Images (*.png *.jpg *.jpeg *.svg *.ico)")
        if path and os.path.exists(path):
            settings_db.set("custom_logo_path", path)
            self._update_all_logos()

    def _on_restore_default_logo(self):
        # SettingsManager has no 'in' / remove(); an empty path means "use the built-in logo"
        if settings_db.get("custom_logo_path", ""):
            settings_db.set("custom_logo_path", "")
        self._update_all_logos()

    def _update_sidebar_logo(self):
        if not hasattr(self, "lbl_sidebar_logo"):
            return
        if self._collapsed:
            self.lbl_sidebar_logo.setPixmap(create_app_icon(28).pixmap(28, 28))
        else:
            pix = get_brand_logo_pixmap(is_dark=(self.current_theme == "dark"), target_width=110)
            if not pix.isNull():
                self.lbl_sidebar_logo.setPixmap(pix)

    def _update_all_logos(self):
        self._update_sidebar_logo()
        if hasattr(self, "lbl_logo_preview"):
            self.lbl_logo_preview.setPixmap(create_app_icon(28).pixmap(28, 28))
        if hasattr(self, "lbl_about_logo"):
            self.lbl_about_logo.setPixmap(create_app_icon(44).pixmap(44, 44))

    # ── Navigation ──────────────────────────────────────────────────────────
    def _go_to(self, page: int, remember: bool = True):
        meta = next((m for m in self.pages_meta if m[0] == page), self.pages_meta[0])
        self.stacked_pages.setCurrentIndex(meta[0])
        self._nav_by_page[meta[0]].setChecked(True)
        self.lbl_header_title.setText(meta[3])
        self.lbl_header_subtitle.setText(meta[4])
        if meta[0] == self.PAGE_HISTORY:
            self._load_history()
        elif meta[0] == self.PAGE_RESOURCES:
            self._load_resources()
        elif meta[0] == self.PAGE_SETTINGS:
            self._refresh_perm_page_status()
        elif meta[0] == self.PAGE_LISTEN:
            self._refresh_now_playing()
        if remember:
            settings_db.set("ui_last_page", self.PAGE_KEYS[meta[0]])

    def _on_nav_clicked(self, page_idx: int, *_args):
        self._go_to(page_idx)

    def _show_page(self, page: int):
        self._go_to(page)
        self.show()
        self.raise_()
        self.activateWindow()

    def open_main(self):
        last = settings_db.get("ui_last_page", "listen")
        self._show_page(next((k for k, v in self.PAGE_KEYS.items() if v == last), self.PAGE_LISTEN))

    def open_preferences(self):
        self._show_page(self.PAGE_SETTINGS)

    def open_about(self):
        self._show_page(self.PAGE_SETTINGS)
        QTimer.singleShot(50, lambda: self.settings_scroll.ensureWidgetVisible(self.card_about, 0, 40))

    def open_reader(self, text: str = ""):
        if text:
            self.txt_reader.setPlainText(text)
        self._show_page(self.PAGE_READ)
        self.txt_reader.setFocus()

    def open_history(self):
        self._show_page(self.PAGE_HISTORY)

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

    def _refresh_now_playing(self):
        text = getattr(self.tts, "current_text", "") if self.tts else ""
        self.lbl_listen_preview.setText((text[:220] + "…") if len(text) > 220 else text)
        self._refresh_pause_buttons()

    def _on_tts_started(self):
        if self._test_running:
            self.lbl_test_status.setText("Playing…")
            return
        self._set_status("Reading")
        self._set_reading_ui(True)
        self._refresh_now_playing()

    def _on_chunk_progress(self, current: int, total: int):
        if not self._test_running and total > 1:
            self._set_status(f"Reading · part {current} of {total}")

    def _on_tts_finished(self):
        self._test_running = False
        self.btn_test_perf.setText(" Test voice")
        if hasattr(self, "_icon_play_soft"):
            self.btn_test_perf.setIcon(self._icon_play_soft)
        self.lbl_test_status.setText("")
        self.equalizer_preview.set_active(False)
        self._set_reading_ui(False)
        self._set_status("")
        self._refresh_now_playing()

    def _run_performance_test(self):
        if not self.tts:
            self.lbl_test_status.setText("Audio engine not available")
            return
        if self.tts.is_speaking:
            self._stop_all()
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
        QLabel#Section {{ color: {pal['faint']}; font-size: 11px; font-weight: 600; padding: 6px 10px 2px 10px; }}
        QPushButton#NavBtn {{ background: transparent; color: {pal['muted']}; border: none; border-radius: 8px;
                              padding: 8px 10px; text-align: left; font-size: 13px; font-weight: 500; }}
        QPushButton#NavBtn:hover {{ background: {pal['border']}; color: {pal['text']}; }}
        QPushButton#NavBtn:checked {{ background: {pal['accent_soft']}; color: {pal['accent_text']}; }}
        QPushButton#IconBtn {{ background: transparent; border: none; border-radius: 8px; padding: 0; }}
        QPushButton#IconBtn:hover {{ background: {pal['border']}; }}

        QLabel#PageTitle {{ font-size: 22px; font-weight: 600; }}
        QLabel#PageSub {{ font-size: 13px; color: {pal['muted']}; }}
        QLabel#HeroTitle {{ font-size: 16px; font-weight: 600; }}
        QLabel#Status {{ font-size: 15px; font-weight: 600; }}
        QLabel#Faint {{ font-size: 11px; color: {pal['faint']}; }}
        QLabel#Kbd {{ background: {pal['surface2']}; color: {pal['text']}; border: 1px solid {pal['border']};
                      border-radius: 6px; padding: 3px 8px; font-size: 12px; }}

        QFrame#Card {{ background: {pal['surface']}; border: 1px solid {pal['border']}; border-radius: 12px; }}
        QLabel#CardTitle {{ font-size: 12px; font-weight: 600; color: {pal['muted']}; }}
        QFrame#Divider {{ background: {pal['border']}; border: none; }}
        QLabel#RowTitle {{ font-size: 13px; font-weight: 500; }}
        QLabel#RowHint {{ font-size: 12px; color: {pal['muted']}; }}
        QLabel#Pill {{ background: {pal['accent_soft']}; color: {pal['accent_text']}; border-radius: 8px; padding: 3px 6px; font-size: 12px; font-weight: 600; }}
        QFrame#Bar {{ background: {pal['surface']}; border: 1px solid {pal['border']}; border-radius: 12px; }}
        QPushButton#Fold {{ background: transparent; border: none; color: {pal['muted']}; font-size: 12px;
                            font-weight: 500; padding: 8px 2px; text-align: left; }}
        QPushButton#Fold:hover {{ color: {pal['text']}; }}

        QFrame#Segmented {{ background: {pal['surface2']}; border: 1px solid {pal['border']}; border-radius: 9px; }}
        QPushButton#SegBtn {{ background: transparent; color: {pal['muted']}; border: none; border-radius: 7px;
                              padding: 5px 12px; font-size: 12px; font-weight: 500; min-width: 40px; }}
        QPushButton#SegBtn:hover {{ color: {pal['text']}; }}
        QPushButton#SegBtn:checked {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']}; }}

        QPlainTextEdit#Reader {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
                                 border-radius: 12px; padding: 16px; font-size: 15px;
                                 selection-background-color: {pal['accent']}; selection-color: #FFFFFF; }}
        QPlainTextEdit#Reader:focus {{ border: 1px solid {pal['accent']}; }}

        QListWidget#List {{ background: transparent; border: none; outline: none; font-size: 13px; }}
        QListWidget#List::item {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
                                  border-radius: 10px; padding: 10px 14px; margin: 0 4px 8px 0; }}
        QListWidget#List::item:hover {{ border-color: {pal['faint']}; }}
        QListWidget#List::item:selected {{ background: {pal['accent_soft']}; color: {pal['text']}; border-color: {pal['accent']}; }}

        QComboBox {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
                     border-radius: 8px; padding: 6px 30px 6px 10px; font-size: 13px; min-height: 20px; }}
        QComboBox:hover {{ border-color: {pal['faint']}; }}
        QComboBox:focus {{ border-color: {pal['accent']}; }}
        QComboBox::drop-down {{ border: none; width: 26px; }}
        QComboBox::down-arrow {{ image: url("{chevron}"); width: 12px; height: 12px; }}
        QComboBox QAbstractItemView {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
                                       border-radius: 8px; padding: 4px; outline: none;
                                       selection-background-color: {pal['accent_soft']}; selection-color: {pal['text']}; }}

        QSlider::groove:horizontal {{ height: 4px; background: {pal['track_off']}; border-radius: 2px; }}
        QSlider::sub-page:horizontal {{ background: {pal['accent']}; border-radius: 2px; }}
        QSlider::handle:horizontal {{ background: #FFFFFF; border: 1px solid {pal['faint']}; width: 16px; height: 16px; margin: -7px 0; border-radius: 9px; }}
        QSlider::handle:horizontal:hover {{ border-color: {pal['accent']}; }}
        QSlider::handle:horizontal:focus {{ border: 2px solid {pal['accent']}; }}
        QSlider::sub-page:horizontal:disabled {{ background: {pal['track_off']}; }}

        QPushButton {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
                       border-radius: 8px; padding: 7px 14px; font-size: 13px; font-weight: 500; }}
        QPushButton:focus {{ border-color: {pal['accent']}; }}
        QPushButton:disabled {{ color: {pal['faint']}; }}
        QPushButton#BtnPrimary {{ background: {pal['btn']}; color: {pal['on_accent']}; border: none; padding: 8px 20px; font-weight: 600; }}
        QPushButton#BtnPrimary:hover {{ background: {pal['btn_hover']}; }}
        QPushButton#BtnSoft {{ background: {pal['accent_soft']}; color: {pal['accent_text']}; border: none; }}
        QPushButton#BtnSoft:hover {{ background: {pal['border']}; }}
        QPushButton#BtnSoft:disabled {{ background: {pal['surface2']}; color: {pal['faint']}; }}
        QPushButton#BtnGhost {{ background: transparent; color: {pal['text']}; border: 1px solid {pal['border']}; }}
        QPushButton#BtnGhost:hover {{ background: {pal['surface2']}; }}

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
        for s in self.switches:
            s.set_theme_mode(theme)
        for page, btn in self._nav_by_page.items():
            icon = next(m[2] for m in self.pages_meta if m[0] == page)
            btn.setIcon(line_icon(icon, pal["muted"], pal["accent_text"], 18))
        self.btn_collapse.setIcon(line_icon("panel-left", pal["muted"], size=18))
        soft, muted = pal["accent_text"], pal["muted"]
        self._icon_play = line_icon("play", pal["on_accent"], size=14)
        self._icon_stop = line_icon("square", pal["on_accent"], size=14)
        self._icon_play_soft = line_icon("play", soft, size=14)
        self._icon_stop_soft = line_icon("square", soft, size=14)
        self._icon_pause_soft = line_icon("pause", soft, size=14)
        self.btn_paste.setIcon(line_icon("clipboard", soft, size=16))
        self.btn_clear.setIcon(line_icon("x", muted, size=16))
        self.btn_listen_stop.setIcon(line_icon("square", muted, size=14))
        self.btn_listen_replay.setIcon(line_icon("rotate-ccw", soft, size=14))
        self.btn_hist_replay.setIcon(line_icon("play", soft, size=14))
        self.btn_hist_copy.setIcon(line_icon("copy", muted, size=14))
        self.btn_hist_clear.setIcon(line_icon("trash-2", muted, size=14))
        self.btn_rec_open.setIcon(line_icon("folder-open", muted, size=14))
        self.btn_rec_play.setIcon(line_icon("play", soft, size=14))
        self.btn_save_text.setIcon(line_icon("save", muted, size=14))
        self.btn_hist_bookmark.setIcon(line_icon("bookmark", muted, size=14))
        self.btn_text_open.setIcon(line_icon("file-text", soft, size=14))
        self.btn_text_read.setIcon(line_icon("play", muted, size=14))
        self.btn_text_delete.setIcon(line_icon("trash-2", muted, size=14))
        self.btn_bm_read.setIcon(line_icon("play", soft, size=14))
        self.btn_bm_copy.setIcon(line_icon("copy", muted, size=14))
        self.btn_bm_remove.setIcon(line_icon("x", muted, size=14))
        self.btn_open_recordings.setIcon(line_icon("folder-open", muted, size=14))
        self.btn_reset_defaults.setIcon(line_icon("rotate-ccw", muted, size=14))
        for b in self.findChildren(QPushButton):
            if getattr(b, "_link", False):
                b.setIcon(line_icon("external-link", muted, size=14))
        for f in self._folds:
            f.set_icons(line_icon("chevron-right", muted, size=14), line_icon("chevron-down", muted, size=14))
        self.reader_viz.color = QColor(pal["accent"])
        self.equalizer_preview.color = QColor(pal["accent"])
        self.equalizer_widget.set_theme_mode(theme)
        self.btn_test_perf.setIcon(self._icon_stop_soft if self._test_running else self._icon_play_soft)
        self._set_reading_ui(bool(self.tts and self.tts.is_speaking and not self._test_running))
        self._update_all_logos()
        self._refresh_perm_page_status()

    # ── Load / apply ────────────────────────────────────────────────────────
    def _schedule_apply(self, *_args):
        if not self._loading:
            self._apply_timer.start()

    def _apply_now(self):
        settings_db.set("default_voice", self.combo_voice.currentData())
        settings_db.set("emotion_mode", self.combo_emotion.currentData())
        settings_db.set("default_speed", round(self.slider_speed.value() / 100.0, 2))
        settings_db.set("default_pitch", self.slider_pitch.value())
        settings_db.set("prebuffer_enabled", self.chk_prebuffer.isChecked())
        settings_db.set("selection_popup_enabled", self.chk_trigger.isChecked())
        settings_db.set("auto_close_finished", self.chk_autoclose.isChecked())
        settings_db.set("auto_close_delay", round(self.slider_fade_out.value() / 100.0, 2))
        settings_db.set("volume", self.slider_volume.value())
        settings_db.set("bubble_transparency", self.slider_transparency.value())
        settings_db.set("bubble_size", self.seg_bubble_size.value() or "Large")
        settings_db.set("bubble_distance", self.slider_distance.value())
        settings_db.set("bubble_corner_radius", self.current_corner_radius)
        settings_db.set("bubble_appearance", self.current_bubble_style)
        settings_db.set("smooth_fade_in", self.switch_fade_in.isChecked())
        settings_db.set("settings_theme", self.theme_pref)
        if self.chk_startup.isChecked() != is_startup_enabled():
            set_startup_enabled(self.chk_startup.isChecked())
        self.settings_applied.emit()

    def save_and_apply(self):
        """Kept for compatibility: settings now apply automatically."""
        self._apply_timer.stop()
        self._apply_now()

    def _confirm_reset(self):
        ok = QMessageBox.question(self, "Reset settings", "Reset all settings to their defaults?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                  QMessageBox.StandardButton.No)
        if ok == QMessageBox.StandardButton.Yes:
            self.reset_to_defaults()

    def reset_to_defaults(self):
        self._loading = True
        try:
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
            self.current_bubble_style = "Frosted Glass"
            self.seg_bubble_style.set_value("Frosted Glass")
            self.current_corner_radius = "Medium"
            self.seg_corner.set_value("Medium")
            self._on_restore_default_logo()
        finally:
            self._loading = False
        self.save_and_apply()

    def load_values(self):
        self._loading = True
        try:
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
            self.sw_listen_selection.setChecked(self.chk_trigger.isChecked(), animate=False)
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
            corner = settings_db.get("bubble_corner_radius", "Medium")
            self.current_corner_radius = corner if corner in ("Square", "Medium", "Round") else "Medium"
            self.seg_corner.set_value(self.current_corner_radius)
            # keep legacy styles (Default / Transparent) untouched unless the user picks a new one
            self.current_bubble_style = settings_db.get("bubble_appearance", "Frosted Glass")
            self.seg_bubble_style.set_value(self.current_bubble_style)
            self._update_all_logos()
        finally:
            self._loading = False
