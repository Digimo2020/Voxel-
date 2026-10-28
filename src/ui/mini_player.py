"""
Mini Floating Player Pill widget.
Provides clean, minimal controls: Play/Pause, Stop, Speed (- / +), Voice Switcher, and Close.
Draggable anywhere on screen with smooth styling and responsive feedback.
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QCursor, QMouseEvent

from src.config import SPEED_STEPS, DEFAULT_SPEED, THEME
from src.tts_engine import TTSEngine
from assets.icons import (
    create_play_icon, create_pause_icon, create_stop_icon, create_close_icon
)


class MiniPlayer(QWidget):
    """
    Sleek floating player pill.
    """
    closed = pyqtSignal()

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self._drag_pos = QPoint()
        self._is_dragging = False

        # Configure window: frameless, stays on top, tool window
        self.setWindowFlags(
            Qt.WindowType.SubWindow |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedHeight(54)
        self.setMinimumWidth(330)

        # Connect TTS engine signals
        self.tts.playback_started.connect(self._on_playback_started)
        self.tts.playback_paused.connect(self._on_playback_paused)
        self.tts.playback_resumed.connect(self._on_playback_resumed)
        self.tts.playback_finished.connect(self._on_playback_finished)
        self.tts.playback_error.connect(self._on_playback_error)

        self._init_ui()
        self._init_animations()

    def _init_ui(self):
        # Outer container widget with rounded background and shadow
        self.container = QWidget(self)
        self.container.setObjectName("playerContainer")
        self.container.setStyleSheet(f"""
            QWidget#playerContainer {{
                background-color: {THEME["bg_player"]};
                border: 1.5px solid {THEME["border_player"]};
                border-radius: 26px;
            }}
        """)

        # Drop shadow for clean floating elevation
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 6)
        self.container.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(8)

        # 1. Play / Pause Button
        self.btn_play_pause = QPushButton(self)
        self.btn_play_pause.setFixedSize(36, 36)
        self.btn_play_pause.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_play_pause.setIcon(create_play_icon(20, "#FFFFFF"))
        self.btn_play_pause.setToolTip("Play / Pause")
        self.btn_play_pause.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME["accent"]};
                border-radius: 18px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {THEME["accent_hover"]};
            }}
        """)
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        layout.addWidget(self.btn_play_pause)

        # 2. Stop Button
        self.btn_stop = QPushButton(self)
        self.btn_stop.setFixedSize(30, 30)
        self.btn_stop.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_stop.setIcon(create_stop_icon(16, "#FFFFFF"))
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME["button_bg"]};
                border-radius: 15px;
                border: 1px solid {THEME["border_player"]};
            }}
            QPushButton:hover {{
                background-color: {THEME["stop_bg"]};
            }}
        """)
        self.btn_stop.clicked.connect(self._stop_playback)
        layout.addWidget(self.btn_stop)

        # Separator line
        layout.addWidget(self._create_separator())

        # 3. Speed Controls: [-] 1.0x [+]
        self.btn_speed_down = QPushButton("-", self)
        self.btn_speed_down.setFixedSize(26, 26)
        self.btn_speed_down.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_speed_down.setToolTip("Decrease Speed")
        self._style_pill_btn(self.btn_speed_down)
        self.btn_speed_down.clicked.connect(self._decrease_speed)
        layout.addWidget(self.btn_speed_down)

        self.lbl_speed = QLabel(f"{DEFAULT_SPEED}x", self)
        self.lbl_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_speed.setFixedWidth(46)
        self.lbl_speed.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_speed.setStyleSheet(f"color: {THEME['text_primary']};")
        layout.addWidget(self.lbl_speed)

        self.btn_speed_up = QPushButton("+", self)
        self.btn_speed_up.setFixedSize(26, 26)
        self.btn_speed_up.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_speed_up.setToolTip("Increase Speed")
        self._style_pill_btn(self.btn_speed_up)
        self.btn_speed_up.clicked.connect(self._increase_speed)
        layout.addWidget(self.btn_speed_up)

        # Separator line
        layout.addWidget(self._create_separator())

        # 4. Voice Switcher Button
        self.btn_voice = QPushButton(self.tts.current_voice["short_label"], self)
        self.btn_voice.setFixedHeight(28)
        self.btn_voice.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voice.setToolTip("Click to Switch Voice (Female / Male)")
        self.btn_voice.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.btn_voice.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME["button_bg"]};
                color: {THEME["text_primary"]};
                border-radius: 14px;
                padding: 0 10px;
                border: 1px solid {THEME["border_player"]};
            }}
            QPushButton:hover {{
                background-color: {THEME["button_hover"]};
                border-color: {THEME["accent"]};
            }}
        """)
        self.btn_voice.clicked.connect(self._cycle_voice)
        layout.addWidget(self.btn_voice)

        # 5. Close Button
        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(26, 26)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setIcon(create_close_icon(14, THEME["text_secondary"]))
        self.btn_close.setToolTip("Close Player")
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 13px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """)
        self.btn_close.clicked.connect(self.close_player)
        layout.addWidget(self.btn_close)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 4, 6, 6)
        main_layout.addWidget(self.container)

    def _init_animations(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(180)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _create_separator(self) -> QWidget:
        sep = QWidget(self)
        sep.setFixedSize(1, 20)
        sep.setStyleSheet(f"background-color: {THEME['border_player']};")
        return sep

    def _style_pill_btn(self, btn: QPushButton):
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME["button_bg"]};
                color: {THEME["text_primary"]};
                border-radius: 13px;
                border: 1px solid {THEME["border_player"]};
            }}
            QPushButton:hover {{
                background-color: {THEME["button_hover"]};
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: {THEME["button_active"]};
            }}
        """)

    def play_text(self, text: str, show_at_pos: QPoint = None):
        """Starts speaking text and displays the player near position."""
        if show_at_pos:
            self._position_near(show_at_pos)

        self.fade_anim.stop()
        self.setWindowOpacity(0.0)
        self.show()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

        # Update button to show loading / play
        self.btn_play_pause.setIcon(create_pause_icon(20, "#FFFFFF"))
        self.tts.speak(text)

    def _position_near(self, center_pos: QPoint):
        """Positions the player near the given point while remaining on-screen."""
        w = self.sizeHint().width() if self.width() < 100 else self.width()
        h = self.height()
        target_x = center_pos.x() - (w // 2)
        target_y = center_pos.y() + 20

        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            # If goes below screen, position above
            if target_y + h > geo.bottom() - 10:
                target_y = center_pos.y() - h - 20
            target_x = max(geo.left() + 10, min(geo.right() - w - 10, target_x))
            target_y = max(geo.top() + 10, min(geo.bottom() - h - 10, target_y))

        self.move(int(target_x), int(target_y))

    def _toggle_play_pause(self):
        self.tts.toggle_play_pause()

    def _stop_playback(self):
        self.tts.stop()
        self.btn_play_pause.setIcon(create_play_icon(20, "#FFFFFF"))

    def _decrease_speed(self):
        curr = self.tts.current_speed
        # Find next lower speed step
        lower_steps = [s for s in SPEED_STEPS if s < curr - 0.05]
        new_speed = lower_steps[-1] if lower_steps else SPEED_STEPS[0]
        self._apply_speed(new_speed)

    def _increase_speed(self):
        curr = self.tts.current_speed
        # Find next higher speed step
        higher_steps = [s for s in SPEED_STEPS if s > curr + 0.05]
        new_speed = higher_steps[0] if higher_steps else SPEED_STEPS[-1]
        self._apply_speed(new_speed)

    def _apply_speed(self, speed: float):
        self.tts.set_speed(speed)
        self.lbl_speed.setText(f"{speed}x")
        # If currently playing or paused, restart with new speed
        if self.tts.is_speaking:
            self.tts.speak(self.tts.current_text)

    def _cycle_voice(self):
        voice = self.tts.cycle_voice()
        self.btn_voice.setText(voice["short_label"])
        # If currently speaking, restart with new voice
        if self.tts.is_speaking:
            self.tts.speak(self.tts.current_text)

    def close_player(self):
        self.tts.stop()
        self.hide()
        self.closed.emit()

    # --- TTS Callback Handlers ---
    def _on_playback_started(self):
        self.btn_play_pause.setIcon(create_pause_icon(20, "#FFFFFF"))

    def _on_playback_paused(self):
        self.btn_play_pause.setIcon(create_play_icon(20, "#FFFFFF"))

    def _on_playback_resumed(self):
        self.btn_play_pause.setIcon(create_pause_icon(20, "#FFFFFF"))

    def _on_playback_finished(self):
        self.btn_play_pause.setIcon(create_play_icon(20, "#FFFFFF"))

    def _on_playback_error(self, err_msg: str):
        self.btn_play_pause.setIcon(create_play_icon(20, "#FFFFFF"))

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
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._is_dragging = False
        super().mouseReleaseEvent(event)
