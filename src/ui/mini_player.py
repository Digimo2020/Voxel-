"""
Voxel compact floating mini-player.
Supports a dark capsule and a pale glass variant through a shared theme setting.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QApplication
from PyQt6.QtCore import (
    Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QRectF
)
from PyQt6.QtGui import (
    QColor, QFont, QCursor, QMouseEvent, QPainter, QBrush, QPen, QLinearGradient
)

from src.config import SPEED_STEPS, DEFAULT_SPEED, BRAND
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from src.ui.theme import player_styles
from assets.icons import (
    create_voxel_logo, create_play_icon, create_pause_icon, create_stop_icon,
    create_close_icon, create_gear_icon
)


class MiniPlayer(QWidget):
    closed = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self._drag_pos = QPoint()
        self._is_dragging = False
        self._user_moved = False
        self._theme_mode = "dark"
        self._theme = player_styles("dark")

        self.setWindowFlags(
            Qt.WindowType.SubWindow |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedHeight(52)
        self.setFixedWidth(386)

        self.tts.playback_started.connect(self._on_playback_started)
        self.tts.playback_paused.connect(self._on_playback_paused)
        self.tts.playback_resumed.connect(self._on_playback_resumed)
        self.tts.playback_finished.connect(self._on_playback_finished)
        self.tts.playback_error.connect(self._on_playback_error)

        self._init_ui()
        self._init_animations()
        self.apply_theme(settings_db.get("player_theme", "dark"))

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_brand = QPushButton(self)
        self.btn_brand.setFixedSize(28, 32)
        self.btn_brand.setIcon(create_voxel_logo(30))
        self.btn_brand.setIconSize(self.btn_brand.size())
        self.btn_brand.setToolTip("Voxel — Text to Speech, Anywhere")
        self.btn_brand.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.btn_brand.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; }")
        self.btn_brand.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.btn_brand)

        self.btn_play_pause = QPushButton(self)
        self.btn_play_pause.setFixedSize(32, 32)
        self.btn_play_pause.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_play_pause.setIcon(create_play_icon(18, BRAND["blue"]))
        self.btn_play_pause.setToolTip("Play or pause reading")
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        layout.addWidget(self.btn_play_pause)

        self.btn_stop = QPushButton(self)
        self.btn_stop.setFixedSize(28, 28)
        self.btn_stop.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_stop.setIcon(create_stop_icon(16, "#F87171"))
        self.btn_stop.setToolTip("Stop reading")
        self.btn_stop.clicked.connect(self._stop_playback)
        layout.addWidget(self.btn_stop)

        layout.addWidget(self._create_separator())

        self.btn_speed_down = QPushButton("−", self)
        self.btn_speed_down.setFixedSize(25, 26)
        self.btn_speed_down.setToolTip("Decrease speech speed")
        self.btn_speed_down.clicked.connect(self._decrease_speed)
        layout.addWidget(self.btn_speed_down)

        self.lbl_speed = QLabel(f"{DEFAULT_SPEED:.1f}x", self)
        self.lbl_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_speed.setFixedWidth(38)
        self.lbl_speed.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        layout.addWidget(self.lbl_speed)

        self.btn_speed_up = QPushButton("+", self)
        self.btn_speed_up.setFixedSize(25, 26)
        self.btn_speed_up.setToolTip("Increase speech speed")
        self.btn_speed_up.clicked.connect(self._increase_speed)
        layout.addWidget(self.btn_speed_up)

        layout.addWidget(self._create_separator())

        self.btn_voice = QPushButton(self.tts.current_voice["short_label"], self)
        self.btn_voice.setFixedHeight(29)
        self.btn_voice.setMinimumWidth(66)
        self.btn_voice.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voice.setToolTip("Switch speech voice")
        self.btn_voice.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.btn_voice.clicked.connect(self._cycle_voice)
        layout.addWidget(self.btn_voice)

        self.btn_settings = QPushButton(self)
        self.btn_settings.setFixedSize(25, 25)
        self.btn_settings.setIcon(create_gear_icon(16, "#94A3B8"))
        self.btn_settings.setToolTip("Settings and appearance")
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.btn_settings)

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(25, 25)
        self.btn_close.setIcon(create_close_icon(16, "#94A3B8"))
        self.btn_close.setToolTip("Close player")
        self.btn_close.clicked.connect(self.close_player)
        layout.addWidget(self.btn_close)

    def apply_theme(self, mode: str):
        self._theme_mode = "glass" if str(mode).lower() == "glass" else "dark"
        t = player_styles(self._theme_mode)
        self._theme = t
        self.btn_play_pause.setStyleSheet(f"""
            QPushButton {{
                background: rgba(22, 139, 255, 0.18);
                border: 1.4px solid {BRAND['blue']};
                border-radius: 16px;
                padding: 0;
            }}
            QPushButton:hover {{ background: rgba(104, 71, 255, 0.24); }}
            QPushButton:pressed {{ background: rgba(22, 139, 255, 0.32); }}
        """)
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{ background: {t['button']}; border: 1px solid {t['border']}; border-radius: 14px; padding: 0; }}
            QPushButton:hover {{ background: {t['button_hover']}; }}
        """)
        for button in (self.btn_speed_down, self.btn_speed_up):
            button.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            button.setStyleSheet(f"""
                QPushButton {{ background: {t['button']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 12px; padding: 0; }}
                QPushButton:hover {{ background: {t['button_hover']}; }}
            """)
        self.lbl_speed.setStyleSheet(f"color: {t['text']}; background: transparent;")
        self.btn_voice.setStyleSheet(f"""
            QPushButton {{ background: {t['surface_alt']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 14px; padding: 0 9px; }}
            QPushButton:hover {{ background: {t['button_hover']}; }}
        """)
        for button in (self.btn_settings, self.btn_close):
            button.setStyleSheet(f"""
                QPushButton {{ background: transparent; border: 1px solid transparent; border-radius: 12px; }}
                QPushButton:hover {{ background: {t['button_hover']}; border-color: {t['border']}; }}
            """)
        self.btn_settings.setIcon(create_gear_icon(16, t["muted"]))
        self.btn_close.setIcon(create_close_icon(16, t["muted"]))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)
        radius = (h - 2.0) / 2.0

        grad = QLinearGradient(0, 0, 0, h)
        if self._theme_mode == "glass":
            grad.setColorAt(0.0, QColor(248, 250, 255, 223))
            grad.setColorAt(0.45, QColor(226, 237, 255, 198))
            grad.setColorAt(1.0, QColor(224, 221, 255, 213))
            border = QColor(255, 255, 255, 230)
        else:
            grad.setColorAt(0.0, QColor(35, 44, 63, 248))
            grad.setColorAt(0.42, QColor(21, 28, 43, 246))
            grad.setColorAt(1.0, QColor(15, 22, 36, 250))
            border = QColor(255, 255, 255, 36)
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(border, 1.0))
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()

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
        self.pos_anim_out.setDuration(170)
        self.pos_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim_out.setDuration(170)
        self.fade_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim_group_out.addAnimation(self.pos_anim_out)
        self.anim_group_out.addAnimation(self.fade_anim_out)
        self.anim_group_out.finished.connect(self._on_exit_finished)

    def _create_separator(self):
        sep = QWidget(self)
        sep.setFixedSize(1, 18)
        sep.setStyleSheet(f"background-color: {self._theme.get('separator', 'rgba(255,255,255,0.14)')};")
        return sep

    def _get_bottom_right_pos(self):
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            return QPoint(geo.right() - self.width() - 24, geo.bottom() - self.height() - 18)
        return QPoint(100, 100)

    def play_text(self, text: str, show_at_pos: QPoint = None):
        self.anim_group_out.stop()
        dock_mode = settings_db.get("dock_position", "bottom_right")
        if dock_mode == "near_cursor" and show_at_pos:
            target_pos = show_at_pos
        else:
            target_pos = self._get_bottom_right_pos() if not self._user_moved else self.pos()
        start_pos = QPoint(target_pos.x(), target_pos.y() + 22)
        self.pos_anim_in.setStartValue(start_pos)
        self.pos_anim_in.setEndValue(target_pos)
        self.fade_anim_in.setStartValue(0.0)
        self.fade_anim_in.setEndValue(1.0)
        self.move(start_pos)
        self.setWindowOpacity(0.0)
        self.show()
        self.anim_group_in.start()
        self.btn_play_pause.setIcon(create_pause_icon(18, BRAND["blue"]))
        self.tts.speak(text)

    def update_voice_label(self):
        self.btn_voice.setText(self.tts.current_voice["short_label"])

    def _toggle_play_pause(self):
        self.tts.toggle_play_pause()

    def _stop_playback(self):
        self.tts.stop()
        self.btn_play_pause.setIcon(create_play_icon(18, BRAND["blue"]))

    def _decrease_speed(self):
        lower = [s for s in SPEED_STEPS if s < self.tts.current_speed - 0.05]
        self._apply_speed(lower[-1] if lower else SPEED_STEPS[0])

    def _increase_speed(self):
        higher = [s for s in SPEED_STEPS if s > self.tts.current_speed + 0.05]
        self._apply_speed(higher[0] if higher else SPEED_STEPS[-1])

    def _apply_speed(self, speed: float):
        self.tts.set_speed(speed)
        self.lbl_speed.setText(f"{speed:g}x")
        if self.tts.is_speaking:
            self.tts.speak(self.tts.current_text)

    def _cycle_voice(self):
        voice = self.tts.cycle_voice()
        self.btn_voice.setText(voice["short_label"])
        if self.tts.is_speaking:
            self.tts.speak(self.tts.current_text)

    def close_player(self):
        self.tts.stop()
        curr = self.pos()
        self.pos_anim_out.setStartValue(curr)
        self.pos_anim_out.setEndValue(QPoint(curr.x(), curr.y() + 18))
        self.fade_anim_out.setStartValue(self.windowOpacity())
        self.fade_anim_out.setEndValue(0.0)
        self.anim_group_in.stop()
        self.anim_group_out.start()

    def _on_exit_finished(self):
        self.hide()
        self.closed.emit()

    def _on_playback_started(self):
        self.btn_play_pause.setIcon(create_pause_icon(18, BRAND["blue"]))

    def _on_playback_paused(self):
        self.btn_play_pause.setIcon(create_play_icon(18, BRAND["blue"]))

    def _on_playback_resumed(self):
        self.btn_play_pause.setIcon(create_pause_icon(18, BRAND["blue"]))

    def _on_playback_finished(self):
        self.btn_play_pause.setIcon(create_play_icon(18, BRAND["blue"]))

    def _on_playback_error(self, err_msg: str):
        self.btn_play_pause.setIcon(create_play_icon(18, BRAND["blue"]))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self._user_moved = True
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._is_dragging = False
        super().mouseReleaseEvent(event)
