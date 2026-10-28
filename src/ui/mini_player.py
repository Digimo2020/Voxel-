"""
Frosted Glass Mini Player Pill widget.
Refined minimalist aesthetic: translucent acrylic glass, simple line-art controls,
smooth circular buttons with delicate frosted borders, and settings gear button.
Animates smoothly from the bottom-right of the screen for a clean, non-intrusive experience.
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QApplication
)
from PyQt6.QtCore import (
    Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QRectF
)
from PyQt6.QtGui import (
    QColor, QFont, QCursor, QMouseEvent, QPainter, QBrush, QPen, QLinearGradient
)

from src.config import SPEED_STEPS, DEFAULT_SPEED
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from assets.icons import (
    create_play_icon, create_pause_icon, create_stop_icon,
    create_close_icon, create_gear_icon
)


class MiniPlayer(QWidget):
    """
    Translucent frosted glass player pill with line-art rounded buttons.
    Animates smoothly in the bottom-right corner of the screen with settings access.
    """
    closed = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self._drag_pos = QPoint()
        self._is_dragging = False
        self._user_moved = False

        # Frameless, transparent floating tool window
        self.setWindowFlags(
            Qt.WindowType.SubWindow |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedHeight(48)
        self.setFixedWidth(356)

        # Connect TTS engine signals
        self.tts.playback_started.connect(self._on_playback_started)
        self.tts.playback_paused.connect(self._on_playback_paused)
        self.tts.playback_resumed.connect(self._on_playback_resumed)
        self.tts.playback_finished.connect(self._on_playback_finished)
        self.tts.playback_error.connect(self._on_playback_error)

        self._init_ui()
        self._init_animations()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(7)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Play / Pause Button (Line-art circle)
        self.btn_play_pause = QPushButton(self)
        self.btn_play_pause.setFixedSize(32, 32)
        self.btn_play_pause.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_play_pause.setIcon(create_play_icon(18, "#60A5FA"))
        self.btn_play_pause.setToolTip("Play / Pause")
        self.btn_play_pause.setStyleSheet("""
            QPushButton {
                background-color: rgba(96, 165, 250, 0.16);
                border: 1.2px solid rgba(96, 165, 250, 0.70);
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: rgba(96, 165, 250, 0.32);
                border-color: #93C5FD;
            }
            QPushButton:pressed {
                background-color: rgba(96, 165, 250, 0.45);
            }
        """)
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        layout.addWidget(self.btn_play_pause)

        # 2. Stop Button (Delicate rounded circle)
        self.btn_stop = QPushButton(self)
        self.btn_stop.setFixedSize(28, 28)
        self.btn_stop.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_stop.setIcon(create_stop_icon(16, "#F87171"))
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: rgba(248, 113, 113, 0.14);
                border: 1px solid rgba(248, 113, 113, 0.55);
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(248, 113, 113, 0.28);
                border-color: #FCA5A5;
            }
        """)
        self.btn_stop.clicked.connect(self._stop_playback)
        layout.addWidget(self.btn_stop)

        # Separator 1
        layout.addWidget(self._create_separator())

        # 3. Speed Controls: [-] 1.0x [+]
        self.btn_speed_down = QPushButton("-", self)
        self.btn_speed_down.setFixedSize(24, 24)
        self.btn_speed_down.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_speed_down.setToolTip("Slow Down")
        self._style_round_line_btn(self.btn_speed_down)
        self.btn_speed_down.clicked.connect(self._decrease_speed)
        layout.addWidget(self.btn_speed_down)

        self.lbl_speed = QLabel(f"{DEFAULT_SPEED}x", self)
        self.lbl_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_speed.setFixedWidth(40)
        self.lbl_speed.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.lbl_speed.setStyleSheet("color: #E2E8F0; background: transparent;")
        layout.addWidget(self.lbl_speed)

        self.btn_speed_up = QPushButton("+", self)
        self.btn_speed_up.setFixedSize(24, 24)
        self.btn_speed_up.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_speed_up.setToolTip("Speed Up")
        self._style_round_line_btn(self.btn_speed_up)
        self.btn_speed_up.clicked.connect(self._increase_speed)
        layout.addWidget(self.btn_speed_up)

        # Separator 2
        layout.addWidget(self._create_separator())

        # 4. Voice Switcher (Capsule pill)
        self.btn_voice = QPushButton(self.tts.current_voice["short_label"], self)
        self.btn_voice.setFixedHeight(26)
        self.btn_voice.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voice.setToolTip("Switch Voice")
        self.btn_voice.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.btn_voice.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #E2E8F0;
                border: 1px solid rgba(255, 255, 255, 0.20);
                border-radius: 13px;
                padding: 0 9px;
            }
            QPushButton:hover {
                background-color: rgba(96, 165, 250, 0.20);
                border-color: rgba(96, 165, 250, 0.60);
                color: #FFFFFF;
            }
        """)
        self.btn_voice.clicked.connect(self._cycle_voice)
        layout.addWidget(self.btn_voice)

        # 5. Settings Button (Line-art gear)
        self.btn_settings = QPushButton(self)
        self.btn_settings.setFixedSize(24, 24)
        self.btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_settings.setIcon(create_gear_icon(14, "#94A3B8"))
        self.btn_settings.setToolTip("Settings & About")
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
                border-color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.btn_settings)

        # 6. Close Button (Line-art cross)
        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setIcon(create_close_icon(14, "#94A3B8"))
        self.btn_close.setToolTip("Close")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
                border-color: rgba(255, 255, 255, 0.25);
            }
        """)
        self.btn_close.clicked.connect(self.close_player)
        layout.addWidget(self.btn_close)

    def paintEvent(self, event):
        """Paints a true translucent frosted glass capsule with no black corners."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)
        radius = (h - 2.0) / 2.0  # Perfect pill capsule

        # Translucent Frosted Glass with subtle lighting reflection
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(38, 44, 64, 215))    # Subtle top light rim
        grad.setColorAt(0.4, QColor(22, 25, 38, 205))    # Translucent glass body
        grad.setColorAt(1.0, QColor(16, 18, 28, 220))    # Deep base

        painter.setBrush(QBrush(grad))
        # Delicate frosted glass border
        painter.setPen(QPen(QColor(255, 255, 255, 48), 1.0))
        painter.drawRoundedRect(rect, radius, radius)

        painter.end()

    def _init_animations(self):
        # Entry animation group (Slide up + Fade in)
        self.anim_group_in = QParallelAnimationGroup(self)
        self.pos_anim_in = QPropertyAnimation(self, b"pos")
        self.pos_anim_in.setDuration(240)
        self.pos_anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.fade_anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim_in.setDuration(240)
        self.fade_anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_group_in.addAnimation(self.pos_anim_in)
        self.anim_group_in.addAnimation(self.fade_anim_in)

        # Exit animation group (Slide down + Fade out)
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

    def _create_separator(self) -> QWidget:
        sep = QWidget(self)
        sep.setFixedSize(1, 18)
        sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.14);")
        return sep

    def _style_round_line_btn(self, btn: QPushButton):
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #CBD5E1;
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.18);
                border-color: rgba(255, 255, 255, 0.40);
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.28);
            }
        """)

    def _get_bottom_right_pos(self) -> QPoint:
        """Calculates bottom-right docking position above taskbar."""
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            margin_right = 24
            margin_bottom = 24
            target_x = geo.right() - self.width() - margin_right
            target_y = geo.bottom() - self.height() - margin_bottom
            return QPoint(int(target_x), int(target_y))
        return QPoint(100, 100)

    def play_text(self, text: str, show_at_pos: QPoint = None):
        """Starts speaking text and animates the player in at the configured position."""
        self.anim_group_out.stop()

        dock_mode = settings_db.get("dock_position", "bottom_right")
        if dock_mode == "near_cursor" and show_at_pos:
            target_pos = show_at_pos
        else:
            target_pos = self._get_bottom_right_pos() if not self._user_moved else self.pos()

        start_pos = QPoint(target_pos.x(), target_pos.y() + 25)

        self.pos_anim_in.setStartValue(start_pos)
        self.pos_anim_in.setEndValue(target_pos)

        self.fade_anim_in.setStartValue(0.0)
        self.fade_anim_in.setEndValue(1.0)

        self.move(start_pos)
        self.setWindowOpacity(0.0)
        self.show()
        self.anim_group_in.start()

        self.btn_play_pause.setIcon(create_pause_icon(18, "#60A5FA"))
        self.tts.speak(text)

    def update_voice_label(self):
        """Refreshes voice label from current TTS voice."""
        self.btn_voice.setText(self.tts.current_voice["short_label"])

    def _toggle_play_pause(self):
        self.tts.toggle_play_pause()

    def _stop_playback(self):
        self.tts.stop()
        self.btn_play_pause.setIcon(create_play_icon(18, "#60A5FA"))

    def _decrease_speed(self):
        curr = self.tts.current_speed
        lower_steps = [s for s in SPEED_STEPS if s < curr - 0.05]
        new_speed = lower_steps[-1] if lower_steps else SPEED_STEPS[0]
        self._apply_speed(new_speed)

    def _increase_speed(self):
        curr = self.tts.current_speed
        higher_steps = [s for s in SPEED_STEPS if s > curr + 0.05]
        new_speed = higher_steps[0] if higher_steps else SPEED_STEPS[-1]
        self._apply_speed(new_speed)

    def _apply_speed(self, speed: float):
        self.tts.set_speed(speed)
        self.lbl_speed.setText(f"{speed}x")
        if self.tts.is_speaking:
            self.tts.speak(self.tts.current_text)

    def _cycle_voice(self):
        voice = self.tts.cycle_voice()
        self.btn_voice.setText(voice["short_label"])
        if self.tts.is_speaking:
            self.tts.speak(self.tts.current_text)

    def close_player(self):
        """Animates out (slides down & fades out)."""
        self.tts.stop()
        curr_pos = self.pos()
        end_pos = QPoint(curr_pos.x(), curr_pos.y() + 20)

        self.pos_anim_out.setStartValue(curr_pos)
        self.pos_anim_out.setEndValue(end_pos)

        self.fade_anim_out.setStartValue(self.windowOpacity())
        self.fade_anim_out.setEndValue(0.0)

        self.anim_group_in.stop()
        self.anim_group_out.start()

    def _on_exit_finished(self):
        self.hide()
        self.closed.emit()

    # --- TTS Callbacks ---
    def _on_playback_started(self):
        self.btn_play_pause.setIcon(create_pause_icon(18, "#60A5FA"))

    def _on_playback_paused(self):
        self.btn_play_pause.setIcon(create_play_icon(18, "#60A5FA"))

    def _on_playback_resumed(self):
        self.btn_play_pause.setIcon(create_pause_icon(18, "#60A5FA"))

    def _on_playback_finished(self):
        self.btn_play_pause.setIcon(create_play_icon(18, "#60A5FA"))

    def _on_playback_error(self, err_msg: str):
        self.btn_play_pause.setIcon(create_play_icon(18, "#60A5FA"))

    # --- Smooth Window Dragging ---
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
