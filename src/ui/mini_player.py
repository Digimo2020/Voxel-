"""
Voxel mini player (design v2): a calm, compact capsule.

Visible: logo + name, Play/Pause, speed, More (read whole document, record), Settings, Close.
A thin progress line runs along the bottom while a long text is read in parts.
Flat surface, thin border, very soft shadow. No separators, no gradients, no glow.

Behaviour kept from v1: frameless always-on-top tool window that never steals focus, drag to
move, slide/fade in, auto-close fade after speech (paused while hovered), recording to MP3,
document reading, replay of the last text.
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QApplication, QMenu,
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QLayout)
from PyQt6.QtCore import (
    Qt, QPoint, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QRectF,
    QTimer, QVariantAnimation
)
from PyQt6.QtGui import QColor, QCursor, QMouseEvent, QPainter, QPen, QAction

from src.config import SPEED_STEPS, DEFAULT_SPEED, IS_MAC
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from src.ui.voxel_logo_widget import VoxelLogoWidget
from src.ui.design import PALETTES, FONT_STACK, line_icon
from src.utils.audio_recorder import save_recording_from_chunks


def _pal(theme_mode: str) -> dict:
    return PALETTES["dark" if theme_mode == "dark_glass" else "light"]


class GradientGlowPlayButton(QPushButton):
    """Round Play/Pause button. Name kept for compatibility; it is flat now (no gradient, no glow)."""

    def __init__(self, size: int = 30, parent=None):
        super().__init__(parent)
        self.btn_size = size
        self.setFixedSize(size, size)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.is_playing = False
        self.is_hovered = False
        self.accent = QColor(PALETTES["light"]["accent"])
        self.accent_hover = QColor(PALETTES["light"]["accent_hover"])
        self.icon_color = "#FFFFFF"

    def set_colors(self, accent: str, hover: str, icon: str = "#FFFFFF"):
        self.accent, self.accent_hover, self.icon_color = QColor(accent), QColor(hover), icon
        self.update()

    def set_playing(self, playing: bool):
        self.is_playing = playing
        self.setToolTip(("Pause" if playing else "Play") + "  ·  hover the player for more")
        self.setAccessibleName("Pause" if playing else "Play")
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = float(self.btn_size)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self.accent_hover if (self.is_hovered or self.isDown()) else self.accent)
        p.drawEllipse(QRectF(0, 0, s, s))
        ic = int(s * 0.46)
        pm = line_icon("pause" if self.is_playing else "play", self.icon_color, size=ic).pixmap(ic, ic)
        dx = 0 if self.is_playing else 1  # optical centre for the play triangle
        p.drawPixmap(int((s - ic) / 2 + dx), int((s - ic) / 2), pm)
        p.end()


class MiniPlayer(QWidget):
    closed = pyqtSignal()
    settings_requested = pyqtSignal()
    read_document_requested = pyqtSignal(str)
    recording_saved = pyqtSignal(str)

    HEIGHT = 46
    COLLAPSED_W = 96    # wave + play
    EXPANDED_W = 236    # + speed, more, settings, close

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.is_recording = False
        self._drag_pos = QPoint()
        self._is_dragging = False
        self._user_moved = False
        self._theme_mode = "light_glass"
        self._progress = 0.0           # 0..1 for multi-part reading, 0 = hidden
        self._separators = []          # kept for compatibility (none are created)

        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.NoDropShadowWindowHint |
            Qt.WindowType.WindowDoesNotAcceptFocus   # never steal focus from the app you are typing in
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedHeight(self.HEIGHT + 10)   # room for the soft shadow
        self.setFixedWidth(self.COLLAPSED_W)
        self._expanded = False
        self._menu_open = False

        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(16)
        self.shadow_effect.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow_effect)

        self.tts.playback_started.connect(self._on_playback_started)
        self.tts.playback_paused.connect(self._on_playback_paused)
        self.tts.playback_resumed.connect(self._on_playback_resumed)
        self.tts.playback_finished.connect(self._on_playback_finished)
        self.tts.playback_error.connect(self._on_playback_error)
        self.tts.chunk_progress.connect(self._on_chunk_progress)

        self._init_ui()
        self._init_animations()
        self.apply_theme(settings_db.get("theme_mode", "light_glass"))

    # ── Layout ──────────────────────────────────────────────────────────────
    def _icon_button(self, tooltip: str) -> QPushButton:
        b = QPushButton(self)
        b.setFixedSize(28, 28)
        b.setIconSize(QSize(16, 16))
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        b.setToolTip(tooltip)
        b.setAccessibleName(tooltip)
        b.setObjectName("IconBtn")
        return b

    def _init_ui(self):
        lay = QHBoxLayout(self)
        lay.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)  # window width is animated, not driven by layout
        lay.setContentsMargins(16, 5, 8, 5 + 10)
        lay.setSpacing(4)

        # status mark: outline wave, grey at rest, blue while reading, red while recording (not a button)
        self.logo = VoxelLogoWidget(size=20, animated=False, parent=self, badge=False)
        self.logo.setToolTip("Voxel")
        lay.addWidget(self.logo)
        lay.addSpacing(10)
        self.lbl_brand = QLabel("Voxel", self)   # kept for compatibility; not shown
        self.lbl_brand.hide()

        # the one primary action
        self.btn_play_pause = GradientGlowPlayButton(size=32, parent=self)
        self.btn_play_pause.set_playing(False)
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        lay.addWidget(self.btn_play_pause)

        # secondary controls appear on hover
        self.extras = QWidget(self)
        ex = QHBoxLayout(self.extras)
        ex.setContentsMargins(8, 0, 0, 0)
        ex.setSpacing(2)
        curr_speed = getattr(self.tts, "current_speed", DEFAULT_SPEED)
        self.btn_speed = QPushButton(self._speed_text(curr_speed), self.extras)
        self.btn_speed.setObjectName("Speed")
        self.btn_speed.setFixedHeight(28)
        self.btn_speed.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_speed.setToolTip("Speed")
        self.btn_speed.setAccessibleName("Speed")
        self.btn_speed.clicked.connect(self._show_speed_menu)
        ex.addWidget(self.btn_speed)
        self.btn_more = self._icon_button("More: read whole document, record")
        self.btn_more.clicked.connect(self._show_more_menu)
        ex.addWidget(self.btn_more)
        self.btn_settings = self._icon_button("Settings")
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        ex.addWidget(self.btn_settings)
        self.btn_close = self._icon_button("Close")
        self.btn_close.clicked.connect(self.hide_player)
        ex.addWidget(self.btn_close)
        lay.addWidget(self.extras)
        lay.addStretch()
        # no fade effect here: a graphics effect nested inside the window shadow is drawn offset by Qt;
        # the width animation already reveals the controls smoothly
        self.extras.hide()

        # v1 attribute names, still used by other code paths
        self.btn_doc = self.btn_more
        self.btn_record = self.btn_more

        # hover expand / collapse
        self._width_anim = QVariantAnimation(self)
        self._width_anim.setDuration(200)
        self._width_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._width_anim.valueChanged.connect(self._on_width_anim)
        self._width_anim.finished.connect(self._on_width_anim_done)
        self._collapse_timer = QTimer(self)
        self._collapse_timer.setSingleShot(True)
        self._collapse_timer.setInterval(700)
        self._collapse_timer.timeout.connect(self.collapse)

    # ── Expand on hover ─────────────────────────────────────────────────────
    def expand(self):
        self._collapse_timer.stop()
        if self._expanded:
            return
        self._expanded = True
        self.extras.show()
        self._animate_width(self.EXPANDED_W)

    def collapse(self):
        if not self._expanded or self._menu_open or self._is_dragging:
            return
        self._expanded = False
        self._animate_width(self.COLLAPSED_W)

    def _animate_width(self, target: int):
        self._width_anim.stop()
        self._width_anim.setStartValue(self.width())
        self._width_anim.setEndValue(target)
        self._width_anim.start()

    def _on_width_anim(self, w):
        w = int(w)
        right = self.x() + self.width()          # grow / shrink towards the left, right edge stays put
        self.setFixedWidth(w)
        self.move(right - w, self.y())
        self.update()

    def _on_width_anim_done(self):
        if not self._expanded:
            self.extras.hide()

    def _collapse_now(self):
        """Back to the compact size without animation (used when the player is shown)."""
        self._width_anim.stop()
        self._expanded = False
        self.extras.hide()
        self.setFixedWidth(self.COLLAPSED_W)

    @staticmethod
    def _speed_text(speed: float) -> str:
        return f"{speed:g}×"

    def _create_separator(self) -> QWidget:
        """Kept for compatibility; the v2 design has no separators."""
        w = QWidget(self)
        w.setFixedSize(0, 0)
        return w

    # ── Theme ───────────────────────────────────────────────────────────────
    def apply_theme(self, theme_mode: str = "light_glass"):
        self._theme_mode = theme_mode
        pal = _pal(theme_mode)
        dark = theme_mode == "dark_glass"
        self.btn_play_pause.set_colors(pal["btn"], pal["btn_hover"], pal["on_accent"])
        rec = "#E5484D"
        self.logo.set_bar_colors(rec if self.is_recording else pal["faint"], rec if self.is_recording else pal["accent"])
        brand_color = rec if self.is_recording else pal["text"]
        # Style each child directly: re-applying a parent style sheet does not reliably repolish children.
        self.lbl_brand.setStyleSheet(
            f"QLabel {{ color: {brand_color}; font-family: {FONT_STACK}; font-size: 13px; font-weight: 600; background: transparent; }}")
        self.btn_speed.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {pal['text']}; border: 1px solid {pal['border']};
                           border-radius: 8px; padding: 0 8px; font-family: {FONT_STACK}; font-size: 12px; font-weight: 500; }}
            QPushButton:hover {{ background: {pal['surface2']}; }}
        """)
        icon_css = f"""
            QPushButton {{ background: transparent; border: none; border-radius: 8px; }}
            QPushButton:hover {{ background: {pal['surface2']}; }}
            QPushButton:pressed {{ background: {pal['border']}; }}
        """
        for b in (self.btn_more, self.btn_settings, self.btn_close):
            b.setStyleSheet(icon_css)
        self.btn_more.setIcon(line_icon("ellipsis", pal["muted"], size=16))
        self.btn_settings.setIcon(line_icon("settings-2", pal["muted"], size=16))
        self.btn_close.setIcon(line_icon("x", pal["muted"], size=16))
        self.shadow_effect.setColor(QColor(0, 0, 0, 90 if dark else 34))
        self.update()

    def update_voice_label(self):
        """Kept for compatibility."""

    def _menu_style(self) -> str:
        pal = _pal(self._theme_mode)
        return f"""
            QMenu {{ background: {pal['surface']}; color: {pal['text']}; border: 1px solid {pal['border']};
                     border-radius: 10px; padding: 4px; font-family: {FONT_STACK}; font-size: 12px; }}
            QMenu::item {{ padding: 6px 14px; border-radius: 6px; }}
            QMenu::item:selected {{ background: {pal['accent_soft']}; color: {pal['accent_text']}; }}
            QMenu::separator {{ height: 1px; background: {pal['border']}; margin: 4px 6px; }}
        """

    def _popup(self, menu: QMenu, anchor: QWidget):
        menu.adjustSize()
        top = anchor.mapToGlobal(QPoint(0, 0))
        self._menu_open = True
        try:
            menu.exec(QPoint(top.x(), top.y() - menu.sizeHint().height() - 6))
        finally:
            self._menu_open = False
            if not self.underMouse():
                self._collapse_timer.start()

    # ── Menus ───────────────────────────────────────────────────────────────
    def _show_speed_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        for s in SPEED_STEPS:
            a = QAction(f"{s:g}×  (normal)" if s == 1.0 else f"{s:g}×", menu)
            a.setCheckable(True)
            a.setChecked(abs(s - self.tts.current_speed) < 0.05)
            a.triggered.connect(lambda _=False, val=s: self._on_speed_selected(val))
            menu.addAction(a)
        self._popup(menu, self.btn_speed)

    def _on_speed_selected(self, speed: float):
        self.tts.set_speed(speed)
        self.btn_speed.setText(self._speed_text(speed))
        settings_db.set("default_speed", speed)

    def _show_more_menu(self):
        pal = _pal(self._theme_mode)
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        doc_key = "⌘⌥D" if IS_MAC else "Ctrl+Alt+D"
        a_doc = QAction(line_icon("file-text", pal["muted"], size=16), f"Read whole document\t{doc_key}", menu)
        a_doc.triggered.connect(lambda: self.read_document_requested.emit(getattr(self.tts, "current_text", "")))
        menu.addAction(a_doc)
        rec_label = "Stop and save recording" if self.is_recording else "Record to MP3"
        a_rec = QAction(line_icon("circle-dot", "#E5484D" if self.is_recording else pal["muted"], size=16), rec_label, menu)
        a_rec.triggered.connect(self._toggle_recording)
        menu.addAction(a_rec)
        self._popup(menu, self.btn_more)

    # ── Show / hide ─────────────────────────────────────────────────────────
    def _init_animations(self):
        self.anim_group_in = QParallelAnimationGroup(self)
        self.pos_anim_in = QPropertyAnimation(self, b"pos")
        self.pos_anim_in.setDuration(220)
        self.pos_anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim_in.setDuration(220)
        self.fade_anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_group_in.addAnimation(self.pos_anim_in)
        self.anim_group_in.addAnimation(self.fade_anim_in)

        self.anim_group_out = QParallelAnimationGroup(self)
        self.pos_anim_out = QPropertyAnimation(self, b"pos")
        self.pos_anim_out.setDuration(180)
        self.pos_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim_out.setDuration(180)
        self.fade_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim_group_out.addAnimation(self.pos_anim_out)
        self.anim_group_out.addAnimation(self.fade_anim_out)
        self.anim_group_out.finished.connect(self._on_exit_finished)

        self.auto_close_anim = QPropertyAnimation(self, b"windowOpacity")
        self.auto_close_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.auto_close_anim.finished.connect(self._on_auto_close_finished)

    def _get_bottom_right_pos(self) -> QPoint:
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            return QPoint(int(geo.right() - self.width() - 24), int(geo.bottom() - self.height() - 20))
        return QPoint(100, 100)

    def play_text(self, text: str, show_at_pos: QPoint = None):
        self.anim_group_out.stop()
        self.auto_close_anim.stop()
        dock_mode = settings_db.get("dock_position", "bottom_right")
        if dock_mode == "near_cursor" and show_at_pos:
            target_pos = show_at_pos
        else:
            target_pos = self._get_bottom_right_pos() if not self._user_moved else self.pos()
        start_pos = QPoint(target_pos.x(), target_pos.y() + 12)
        self.pos_anim_in.setStartValue(start_pos)
        self.pos_anim_in.setEndValue(target_pos)
        self.fade_anim_in.setStartValue(0.0)
        self.fade_anim_in.setEndValue(1.0)
        self._collapse_now()
        if not (dock_mode == "near_cursor" and show_at_pos) and not self._user_moved:
            target_pos = self._get_bottom_right_pos()
            start_pos = QPoint(target_pos.x(), target_pos.y() + 12)
            self.pos_anim_in.setStartValue(start_pos)
            self.pos_anim_in.setEndValue(target_pos)
        self.move(start_pos)
        self.setWindowOpacity(0.0)
        self._set_progress(0.0)
        self.btn_speed.setText(self._speed_text(getattr(self.tts, "current_speed", DEFAULT_SPEED)))
        self.show()
        self.anim_group_in.start()
        self.btn_play_pause.set_playing(True)
        self.tts.speak(text)

    def _toggle_play_pause(self):
        self.auto_close_anim.stop()
        self.setWindowOpacity(1.0)
        if self.tts.is_speaking:
            if self.tts.is_paused:
                self.tts.resume()
                self.btn_play_pause.set_playing(True)
                self.logo.start_voice_animation()
            else:
                self.tts.pause()
                self.btn_play_pause.set_playing(False)
                self.logo.stop_voice_animation()
        elif getattr(self.tts, "current_text", None):
            self.btn_play_pause.set_playing(True)
            self.logo.start_voice_animation()
            self.tts.speak(self.tts.current_text)

    def hide_player(self):
        self.tts.stop()
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()
        self.auto_close_anim.stop()
        self.anim_group_in.stop()
        curr = self.pos()
        self.pos_anim_out.setStartValue(curr)
        self.pos_anim_out.setEndValue(QPoint(curr.x(), curr.y() + 14))
        self.fade_anim_out.setStartValue(self.windowOpacity())
        self.fade_anim_out.setEndValue(0.0)
        self.anim_group_out.start()

    def _on_exit_finished(self):
        self.hide()
        self.setWindowOpacity(1.0)
        self._user_moved = False
        self.closed.emit()

    def _start_auto_close_fadeout(self, duration_sec: float):
        self.auto_close_anim.stop()
        self.auto_close_anim.setDuration(int(duration_sec * 1000))
        self.auto_close_anim.setStartValue(self.windowOpacity())
        self.auto_close_anim.setEndValue(0.0)
        self.auto_close_anim.start()

    def _on_auto_close_finished(self):
        if self.windowOpacity() <= 0.05:
            self.hide()
            self.setWindowOpacity(1.0)
            self._user_moved = False
            self.closed.emit()

    def enterEvent(self, event):
        self.expand()
        if self.auto_close_anim.state() == QPropertyAnimation.State.Running:
            self.auto_close_anim.stop()
            self.setWindowOpacity(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._menu_open:
            self._collapse_timer.start()
        if not self.btn_play_pause.is_playing and self.isVisible() and settings_db.get("auto_close_finished", True):
            self._start_auto_close_fadeout(float(settings_db.get("auto_close_delay", 1.0)))
        super().leaveEvent(event)

    # ── Recording ───────────────────────────────────────────────────────────
    def _toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.lbl_brand.setText("Recording")
            self.logo.setToolTip("Recording to MP3")
            self.apply_theme(self._theme_mode)
            if not self.tts.is_speaking and getattr(self.tts, "current_text", ""):
                self.tts.speak(self.tts.current_text)
        else:
            self._finish_and_save_recording()

    def _finish_and_save_recording(self):
        self.is_recording = False
        self.lbl_brand.setText("Voxel")
        self.logo.setToolTip("Voxel")
        self.apply_theme(self._theme_mode)
        saved = save_recording_from_chunks(self.tts.get_speech_audio_chunks(), getattr(self.tts, "current_text", ""))
        if saved:
            self.recording_saved.emit(saved)

    # ── Engine callbacks ────────────────────────────────────────────────────
    def _on_playback_started(self):
        self.auto_close_anim.stop()
        self.setWindowOpacity(1.0)
        self.btn_play_pause.set_playing(True)
        self.logo.start_voice_animation()

    def _on_playback_paused(self):
        self.auto_close_anim.stop()
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()

    def _on_playback_resumed(self):
        self.auto_close_anim.stop()
        self.setWindowOpacity(1.0)
        self.btn_play_pause.set_playing(True)
        self.logo.start_voice_animation()

    def _on_playback_finished(self):
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()
        self._set_progress(1.0 if self._progress else 0.0)
        if self.is_recording:
            self._finish_and_save_recording()
        if settings_db.get("auto_close_finished", True):
            self._start_auto_close_fadeout(float(settings_db.get("auto_close_delay", 1.0)))

    def _on_playback_error(self, err: str):
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()

    def _on_chunk_progress(self, current: int, total: int):
        self._set_progress(current / float(total) if total > 1 else 0.0)
        tip = f"Part {current} of {total}" if total > 1 else ""
        self.btn_play_pause.setToolTip(("Pause" if self.btn_play_pause.is_playing else "Play") + (f" · {tip}" if tip else ""))

    def _set_progress(self, value: float):
        self._progress = max(0.0, min(1.0, value))
        self.update()

    # ── Dragging ────────────────────────────────────────────────────────────
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.auto_close_anim.stop()
            self.setWindowOpacity(1.0)
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging:
            self._user_moved = True
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._is_dragging = False

    # ── Painting ────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        pal = _pal(self._theme_mode)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.HEIGHT)
        r = h / 2.0
        rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)
        p.setPen(QPen(QColor(pal["border"]), 1.0))
        p.setBrush(QColor(pal["surface"]))
        p.drawRoundedRect(rect, r, r)
        if self._progress > 0:
            # subtle progress line inside the bottom edge
            track = QRectF(r, h - 4.0, w - 2 * r, 2.0)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(pal["border"]))
            p.drawRoundedRect(track, 1, 1)
            p.setBrush(QColor(pal["accent"]))
            p.drawRoundedRect(QRectF(track.x(), track.y(), track.width() * self._progress, 2.0), 1, 1)
        p.end()
