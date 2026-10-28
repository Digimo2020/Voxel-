"""
Frosted Glass Mini Player Capsule widget for Voxel.
Faithfully implements the Voxel branding and visual design:
- Sleek translucent acrylic capsule with subtle border and drop shadow.
- Animated Voxel microphone logo whose 3 voice lines and radial glow react in real-time to speech playback.
- Glowing gradient Play/Pause circular button.
- Segmented Speed control pill [- 1.0x +].
- Quick voice selector pill with pop-up menu.
- Smooth slide-up and fade-in animations on bottom-right of the screen.
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QApplication,
    QMenu, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QRectF, QPointF
)
from PyQt6.QtGui import (
    QColor, QFont, QCursor, QMouseEvent, QPainter, QBrush, QPen,
    QLinearGradient, QAction, QActionGroup, QRadialGradient
)

from src.config import SPEED_STEPS, DEFAULT_SPEED, VOICES, THEME, FONT_FAMILY
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from src.ui.voxel_logo_widget import VoxelLogoWidget
from assets.icons import (
    create_play_icon, create_pause_icon, create_stop_icon,
    create_close_icon, create_gear_icon, create_minus_icon,
    create_plus_icon, create_chevron_down_icon
)


class GradientGlowPlayButton(QPushButton):
    """
    Circular button with vibrant cyan-to-purple gradient and pulsating outer glow.
    """
    def __init__(self, size: int = 36, parent=None):
        super().__init__(parent)
        self.btn_size = size
        self.setFixedSize(size, size)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.is_playing = False
        self.is_hovered = False

    def set_playing(self, playing: bool):
        self.is_playing = playing
        self.setIcon(create_pause_icon(16, "#FFFFFF") if playing else create_play_icon(16, "#FFFFFF"))
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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        s = float(self.btn_size)
        cx, cy = s / 2.0, s / 2.0

        # Outer glowing halo
        glow_rad = s / 2.0
        glow = QRadialGradient(cx, cy, glow_rad)
        glow.setColorAt(0.0, QColor(0, 132, 255, 140 if self.is_hovered else 90))
        glow.setColorAt(0.7, QColor(124, 58, 237, 80 if self.is_hovered else 40))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QRectF(0, 0, s, s))

        # Vibrant Circular Gradient Button
        btn_pad = 2.0
        btn_rect = QRectF(btn_pad, btn_pad, s - 2 * btn_pad, s - 2 * btn_pad)

        grad = QLinearGradient(btn_rect.topLeft(), btn_rect.bottomRight())
        if self.is_hovered:
            grad.setColorAt(0.0, QColor("#38BDF8"))  # Light cyan
            grad.setColorAt(1.0, QColor("#9333EA"))  # Deep purple
        else:
            grad.setColorAt(0.0, QColor("#0084FF"))  # Electric blue
            grad.setColorAt(1.0, QColor("#7C3AED"))  # Violet

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(255, 255, 255, 120), 1.0))
        painter.drawEllipse(btn_rect)

        # Draw Icon centered
        icon = self.icon()
        if not icon.isNull():
            icon_s = int(s * 0.48)
            pix = icon.pixmap(icon_s, icon_s)
            painter.drawPixmap(int(cx - icon_s / 2.0), int(cy - icon_s / 2.0), pix)

        painter.end()


class MiniPlayer(QWidget):
    """
    Translucent frosted glass capsule player.
    Animates smoothly from the bottom right above the dock/taskbar.
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
        self.setFixedHeight(54)
        self.setFixedWidth(430)

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
        layout.setContentsMargins(14, 0, 12, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Branding: Animated Voxel Logo + "Voxel" Text
        brand_widget = QWidget(self)
        brand_layout = QHBoxLayout(brand_widget)
        brand_layout.setContentsMargins(0, 0, 4, 0)
        brand_layout.setSpacing(6)

        self.logo = VoxelLogoWidget(size=32, animated=False, parent=brand_widget)
        brand_layout.addWidget(self.logo)

        self.lbl_brand = QLabel("Voxel", brand_widget)
        self.lbl_brand.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                font-family: {FONT_FAMILY};
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
        """)
        brand_layout.addWidget(self.lbl_brand)
        layout.addWidget(brand_widget)

        # 2. Glowing Play / Pause Button
        self.btn_play_pause = GradientGlowPlayButton(size=36, parent=self)
        self.btn_play_pause.set_playing(False)
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        layout.addWidget(self.btn_play_pause)

        # 3. Stop Button (Subtle circle)
        self.btn_stop = QPushButton(self)
        self.btn_stop.setFixedSize(30, 30)
        self.btn_stop.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_stop.setIcon(create_stop_icon(16, "#94A3B8"))
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(248, 113, 113, 0.20);
                border-color: rgba(248, 113, 113, 0.50);
            }
            QPushButton:pressed {
                background-color: rgba(248, 113, 113, 0.35);
            }
        """)
        self.btn_stop.clicked.connect(self._stop_playback)
        layout.addWidget(self.btn_stop)

        # Separator Line
        layout.addWidget(self._create_separator())

        # 4. Speed Pill Container [- 1.0x +]
        speed_pill = QWidget(self)
        speed_pill.setFixedHeight(30)
        speed_pill.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 15px;
            }
        """)
        speed_layout = QHBoxLayout(speed_pill)
        speed_layout.setContentsMargins(4, 0, 4, 0)
        speed_layout.setSpacing(2)

        # Minus button
        self.btn_speed_down = QPushButton(speed_pill)
        self.btn_speed_down.setFixedSize(22, 22)
        self.btn_speed_down.setIcon(create_minus_icon(14, "#CBD5E1"))
        self.btn_speed_down.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_speed_down.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.16); border-radius: 11px; }
        """)
        self.btn_speed_down.clicked.connect(self._decrease_speed)
        speed_layout.addWidget(self.btn_speed_down)

        # Speed Label
        self.lbl_speed = QLabel(f"{DEFAULT_SPEED}x", speed_pill)
        self.lbl_speed.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                font-family: {FONT_FAMILY};
                font-size: 11px;
                font-weight: 600;
                border: none;
                background: transparent;
                padding: 0 4px;
            }}
        """)
        speed_layout.addWidget(self.lbl_speed)

        # Plus button
        self.btn_speed_up = QPushButton(speed_pill)
        self.btn_speed_up.setFixedSize(22, 22)
        self.btn_speed_up.setIcon(create_plus_icon(14, "#CBD5E1"))
        self.btn_speed_up.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_speed_up.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.16); border-radius: 11px; }
        """)
        self.btn_speed_up.clicked.connect(self._increase_speed)
        speed_layout.addWidget(self.btn_speed_up)

        layout.addWidget(speed_pill)

        # Separator Line
        layout.addWidget(self._create_separator())

        # 5. Voice Selector Pill with Chevron
        self.btn_voice = QPushButton(self)
        self.btn_voice.setFixedHeight(30)
        self.btn_voice.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voice.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.08);
                color: #FFFFFF;
                font-family: {FONT_FAMILY};
                font-size: 11px;
                font-weight: 500;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 15px;
                padding: 0 10px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.18);
                border-color: rgba(255, 255, 255, 0.30);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.25);
            }}
        """)
        self.btn_voice.clicked.connect(self._show_voice_menu)
        self.update_voice_label()
        layout.addWidget(self.btn_voice)

        # 6. Settings Gear Button
        self.btn_settings = QPushButton(self)
        self.btn_settings.setFixedSize(28, 28)
        self.btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_settings.setIcon(create_gear_icon(16, "#94A3B8"))
        self.btn_settings.setToolTip("Settings & About")
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
            }
        """)
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.btn_settings)

        # 7. Close Button
        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setIcon(create_close_icon(16, "#94A3B8"))
        self.btn_close.setToolTip("Close Player")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
            }
        """)
        self.btn_close.clicked.connect(self.hide_player)
        layout.addWidget(self.btn_close)

    def _create_separator(self) -> QWidget:
        sep = QWidget(self)
        sep.setFixedSize(1, 18)
        sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.12);")
        return sep

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

    def _get_bottom_right_pos(self) -> QPoint:
        """Calculates bottom-right docking position above dock/taskbar."""
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            margin_right = 28
            margin_bottom = 28
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

        self.btn_play_pause.set_playing(True)
        self.tts.speak(text)

    def update_voice_label(self):
        """Refreshes voice label from current TTS voice."""
        short_name = self.tts.current_voice["short_label"]
        self.btn_voice.setText(f"{short_name}  ▾")

    def _show_voice_menu(self):
        """Opens popup menu with available voices."""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #161926;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 8px;
                padding: 4px;
                font-family: {FONT_FAMILY};
                font-size: 12px;
            }}
            QMenu::item {{
                padding: 6px 18px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: #0084FF;
                color: #FFFFFF;
            }}
        """)

        for i, v in enumerate(VOICES):
            action = QAction(v["label"], menu)
            action.setCheckable(True)
            if i == self.tts.current_voice_index:
                action.setChecked(True)
            action.triggered.connect(lambda checked, idx=i: self._on_voice_selected(idx))
            menu.addAction(action)

        # Position menu above voice button
        btn_geo = self.btn_voice.geometry()
        pos = self.mapToGlobal(QPoint(btn_geo.left(), btn_geo.top() - 10))
        menu.exec(pos)

    def _on_voice_selected(self, index: int):
        self.tts.set_voice_index(index)
        self.update_voice_label()
        settings_db.set("default_voice", self.tts.current_voice["id"])

    def _toggle_play_pause(self):
        self.tts.toggle_play_pause()

    def _stop_playback(self):
        self.tts.stop()
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()

    def _decrease_speed(self):
        curr = self.tts.current_speed
        for s in reversed(SPEED_STEPS):
            if s < curr - 0.05:
                self.tts.set_speed(s)
                self.lbl_speed.setText(f"{s}x")
                settings_db.set("default_speed", s)
                break

    def _increase_speed(self):
        curr = self.tts.current_speed
        for s in SPEED_STEPS:
            if s > curr + 0.05:
                self.tts.set_speed(s)
                self.lbl_speed.setText(f"{s}x")
                settings_db.set("default_speed", s)
                break

    def hide_player(self):
        """Animates out and hides."""
        self._stop_playback()
        self.anim_group_in.stop()

        curr_pos = self.pos()
        end_pos = QPoint(curr_pos.x(), curr_pos.y() + 25)

        self.pos_anim_out.setStartValue(curr_pos)
        self.pos_anim_out.setEndValue(end_pos)

        self.fade_anim_out.setStartValue(self.windowOpacity())
        self.fade_anim_out.setEndValue(0.0)

        self.anim_group_out.start()

    def _on_exit_finished(self):
        self.hide()
        self._user_moved = False
        self.closed.emit()

    # Audio Engine Callbacks
    def _on_playback_started(self):
        self.btn_play_pause.set_playing(True)
        self.logo.start_voice_animation()

    def _on_playback_paused(self):
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()

    def _on_playback_resumed(self):
        self.btn_play_pause.set_playing(True)
        self.logo.start_voice_animation()

    def _on_playback_finished(self):
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()

    def _on_playback_error(self, err: str):
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()

    # Window Dragging
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        r = h / 2.0  # Perfect capsule rounded ends

        capsule_rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)

        # Translucent Acrylic Glass Background
        painter.setBrush(QBrush(QColor(18, 21, 34, 225)))  # ~88% opacity
        painter.setPen(QPen(QColor(255, 255, 255, 35), 1.2))
        painter.drawRoundedRect(capsule_rect, r, r)

        painter.end()
