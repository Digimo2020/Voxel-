"""
Frosted Glass Mini Player Capsule widget for Voxel.
Faithfully implements the modern, compact frosted glass design:
- Sleek, ultra-compact translucent acrylic capsule (approx 310px width x 48px height).
- Authentic frosted glass effect: translucent milky gradient, top specular edge highlight, and soft celestial glow.
- Animated Voxel microphone logo with equalizer waveform and breathing radial aura.
- Full "Voxel" brand name displayed cleanly without clipping.
- Dual-state circular Play/Pause button with cyan-to-purple gradient glow.
- Compact clickable speed pill (e.g. "1.0x ▾") with popup selection menu.
- Streamlined layout: No redundant stop button or voice selector pill.
- Smooth fade-in + slide-up on launch, and smooth 1.0s fade-out after speech completes.
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
    QLinearGradient, QAction, QRadialGradient
)

from src.config import SPEED_STEPS, DEFAULT_SPEED, THEME, FONT_FAMILY
from src.tts_engine import TTSEngine
from src.utils.settings import settings_db
from src.ui.voxel_logo_widget import VoxelLogoWidget
from assets.icons import (
    create_play_icon, create_pause_icon, create_gear_icon, create_close_icon, create_document_icon,
    create_record_icon
)
from src.utils.audio_recorder import save_recording_from_chunks


class GradientGlowPlayButton(QPushButton):
    """
    Circular button with vibrant cyan-to-purple gradient and pulsating outer glow.
    Toggles between Play (▶) and Pause (❚❚).
    """
    def __init__(self, size: int = 34, parent=None):
        super().__init__(parent)
        self.btn_size = size
        self.setFixedSize(size, size)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.is_playing = False
        self.is_hovered = False

    def set_playing(self, playing: bool):
        self.is_playing = playing
        self.setIcon(create_pause_icon(16, "#FFFFFF") if playing else create_play_icon(16, "#FFFFFF"))
        self.setToolTip("Pause" if playing else "Play")
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
        glow.setColorAt(0.0, QColor(0, 198, 255, 150 if self.is_hovered else 100))
        glow.setColorAt(0.6, QColor(124, 58, 237, 90 if self.is_hovered else 50))
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
            grad.setColorAt(0.5, QColor("#0084FF"))  # Electric blue
            grad.setColorAt(1.0, QColor("#9333EA"))  # Deep purple
        else:
            grad.setColorAt(0.0, QColor("#00C6FF"))  # Cyan
            grad.setColorAt(0.5, QColor("#0075FF"))  # Electric blue
            grad.setColorAt(1.0, QColor("#7C3AED"))  # Violet

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(255, 255, 255, 140), 1.0))
        painter.drawEllipse(btn_rect)

        # Draw Play / Pause Icon centered
        icon = self.icon()
        if not icon.isNull():
            icon_s = int(s * 0.46)
            pix = icon.pixmap(icon_s, icon_s)
            painter.drawPixmap(int(cx - icon_s / 2.0), int(cy - icon_s / 2.0), pix)

        painter.end()


class MiniPlayer(QWidget):
    """
    Compact translucent frosted glass capsule player.
    Animates smoothly from the bottom right with fade-in and slide-up.
    Fades out gently when speech playback completes.
    """
    closed = pyqtSignal()
    settings_requested = pyqtSignal()
    read_document_requested = pyqtSignal(str)
    recording_saved = pyqtSignal(str)

    def __init__(self, tts_engine: TTSEngine, parent=None):
        super().__init__(parent)
        self.tts = tts_engine
        self.is_recording = False
        self._drag_pos = QPoint()
        self._is_dragging = False
        self._user_moved = False
        self._theme_mode = "light_glass"
        self._separators = []

        # Frameless, transparent floating tool window
        self.setWindowFlags(
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFixedHeight(48)
        self.setFixedWidth(380)

        # Soft ethereal drop shadow for frosted glass depth
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(24)
        self.shadow_effect.setOffset(0, 6)
        self.setGraphicsEffect(self.shadow_effect)

        # Connect TTS engine signals
        self.tts.playback_started.connect(self._on_playback_started)
        self.tts.playback_paused.connect(self._on_playback_paused)
        self.tts.playback_resumed.connect(self._on_playback_resumed)
        self.tts.playback_finished.connect(self._on_playback_finished)
        self.tts.playback_error.connect(self._on_playback_error)
        self.tts.chunk_progress.connect(self._on_chunk_progress)

        self._init_ui()
        self._init_animations()
        self.apply_theme(settings_db.get("theme_mode", "light_glass"))

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 12, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Branding: Animated Voxel Logo + "Voxel" Text
        brand_widget = QWidget(self)
        brand_layout = QHBoxLayout(brand_widget)
        brand_layout.setContentsMargins(0, 0, 2, 0)
        brand_layout.setSpacing(6)

        self.logo = VoxelLogoWidget(size=28, animated=False, parent=brand_widget)
        brand_layout.addWidget(self.logo)

        self.lbl_brand = QLabel("Voxel", brand_widget)
        self.lbl_brand.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        brand_layout.addWidget(self.lbl_brand)
        layout.addWidget(brand_widget)

        # Hairline separator
        layout.addWidget(self._create_separator())

        # 2. Glowing Play / Pause Toggle Button
        self.btn_play_pause = GradientGlowPlayButton(size=34, parent=self)
        self.btn_play_pause.set_playing(False)
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        layout.addWidget(self.btn_play_pause)

        # Hairline separator
        layout.addWidget(self._create_separator())

        # 3. Compact Speed Dropdown Pill (e.g. "1.0x ▾")
        curr_speed = getattr(self.tts, "current_speed", DEFAULT_SPEED)
        self.btn_speed = QPushButton(f"{curr_speed}x ▾", self)
        self.btn_speed.setFixedHeight(26)
        self.btn_speed.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_speed.setToolTip("Change Playback Speed")
        self.btn_speed.clicked.connect(self._show_speed_menu)
        layout.addWidget(self.btn_speed)

        # Hairline separator
        layout.addWidget(self._create_separator())

        # 4. Document / Presentation Reader Button
        self.btn_doc = QPushButton(self)
        self.btn_doc.setFixedSize(26, 26)
        self.btn_doc.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_doc.setToolTip("Read Entire Document / Presentation (Ctrl+Alt+D)")
        self.btn_doc.clicked.connect(lambda: self.read_document_requested.emit(getattr(self.tts, "current_text", "")))
        layout.addWidget(self.btn_doc)

        layout.addWidget(self._create_separator())

        # 5. Audio Recording Button (Saves to Documents/Voxel Recordings)
        self.btn_record = QPushButton(self)
        self.btn_record.setFixedSize(26, 26)
        self.btn_record.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_record.setToolTip("Record Speech to MP3 (Saved to Documents/Voxel Recordings)")
        self.btn_record.clicked.connect(self._toggle_recording)
        layout.addWidget(self.btn_record)

        layout.addWidget(self._create_separator())

        # 6. Settings Gear Button
        self.btn_settings = QPushButton(self)
        self.btn_settings.setFixedSize(26, 26)
        self.btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_settings.setIcon(create_gear_icon(15, "#475569"))
        self.btn_settings.setToolTip("Settings & Preferences")
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.btn_settings)

        # 7. Close Button
        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(26, 26)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setIcon(create_close_icon(15, "#475569"))
        self.btn_close.setToolTip("Close Player")
        self.btn_close.clicked.connect(self.hide_player)
        layout.addWidget(self.btn_close)

    def _create_separator(self) -> QWidget:
        sep = QWidget(self)
        sep.setFixedSize(1, 16)
        sep.setStyleSheet("background-color: rgba(140, 160, 200, 0.30);")
        self._separators.append(sep)
        return sep

    def apply_theme(self, theme_mode: str = "light_glass"):
        """Switches player between Frosted Glass (signature light acrylic) and Dark Glass appearance."""
        self._theme_mode = theme_mode

        if theme_mode == "dark_glass":
            # ── Dark Frosted Glass (Obsidian Glass) ──────────────────────
            self.lbl_brand.setStyleSheet(f"""
                QLabel {{
                    color: #FFFFFF;
                    font-family: {FONT_FAMILY};
                    font-size: 15px;
                    font-weight: 700;
                    letter-spacing: 0.4px;
                }}
            """)
            self.btn_speed.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 0.10);
                    color: #FFFFFF;
                    font-family: {FONT_FAMILY};
                    font-size: 11px;
                    font-weight: 600;
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    border-radius: 13px;
                    padding: 0 9px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.20);
                    border-color: rgba(255, 255, 255, 0.35);
                }}
                QPushButton:pressed {{
                    background-color: rgba(255, 255, 255, 0.28);
                }}
            """)
            self.btn_doc.setIcon(create_document_icon(15, "#CBD5E1"))
            self.btn_doc.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 13px; }
                QPushButton:hover { background-color: rgba(255, 255, 255, 0.14); }
            """)
            if not self.is_recording:
                self.btn_record.setIcon(create_record_icon(17, "#F87171", recording=False))
                self.btn_record.setStyleSheet("""
                    QPushButton { background: transparent; border: none; border-radius: 13px; }
                    QPushButton:hover { background-color: rgba(239, 68, 68, 0.16); }
                """)
            self.btn_settings.setIcon(create_gear_icon(15, "#CBD5E1"))
            self.btn_settings.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 13px; }
                QPushButton:hover { background-color: rgba(255, 255, 255, 0.14); }
            """)
            self.btn_close.setIcon(create_close_icon(15, "#CBD5E1"))
            self.btn_close.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 13px; }
                QPushButton:hover { background-color: rgba(255, 255, 255, 0.14); }
            """)
            for sep in self._separators:
                sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.16);")
            self.shadow_effect.setColor(QColor(0, 0, 0, 120))

        else:
            # ── Signature Frosted Glass (Light Acrylic Ethereal) ────────
            self.lbl_brand.setStyleSheet(f"""
                QLabel {{
                    color: #0F172A;
                    font-family: {FONT_FAMILY};
                    font-size: 15px;
                    font-weight: 750;
                    letter-spacing: 0.4px;
                }}
            """)
            self.btn_speed.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 0.70);
                    color: #0F172A;
                    font-family: {FONT_FAMILY};
                    font-size: 11px;
                    font-weight: 650;
                    border: 1px solid rgba(255, 255, 255, 0.95);
                    border-radius: 13px;
                    padding: 0 9px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.95);
                    border-color: #FFFFFF;
                }}
                QPushButton:pressed {{
                    background-color: rgba(230, 240, 255, 0.95);
                }}
            """)
            self.btn_doc.setIcon(create_document_icon(15, "#475569"))
            self.btn_doc.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 13px; }
                QPushButton:hover { background-color: rgba(0, 0, 0, 0.06); }
            """)
            if not self.is_recording:
                self.btn_record.setIcon(create_record_icon(17, "#EF4444", recording=False))
                self.btn_record.setStyleSheet("""
                    QPushButton { background: transparent; border: none; border-radius: 13px; }
                    QPushButton:hover { background-color: rgba(239, 68, 68, 0.12); }
                """)
            self.btn_settings.setIcon(create_gear_icon(15, "#475569"))
            self.btn_settings.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 13px; }
                QPushButton:hover { background-color: rgba(0, 0, 0, 0.06); }
            """)
            self.btn_close.setIcon(create_close_icon(15, "#475569"))
            self.btn_close.setStyleSheet("""
                QPushButton { background: transparent; border: none; border-radius: 13px; }
                QPushButton:hover { background-color: rgba(0, 0, 0, 0.06); }
            """)
            for sep in self._separators:
                sep.setStyleSheet("background-color: rgba(140, 160, 200, 0.30);")
            self.shadow_effect.setColor(QColor(100, 140, 220, 80))

        self.update()

    def update_voice_label(self):
        """Maintained for backwards-compatibility."""
        pass

    def _show_speed_menu(self):
        """Displays speed selection menu."""
        menu = QMenu(self)
        is_light = (self._theme_mode != "dark_glass")
        bg = "#FFFFFF" if is_light else "#161926"
        fg = "#0F172A" if is_light else "#FFFFFF"
        border = "rgba(0, 0, 0, 0.12)" if is_light else "rgba(255, 255, 255, 0.16)"

        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: 8px;
                padding: 4px;
                font-family: {FONT_FAMILY};
                font-size: 12px;
            }}
            QMenu::item {{
                padding: 5px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: #0084FF;
                color: #FFFFFF;
            }}
        """)

        for s in SPEED_STEPS:
            label = f"{s}x (Normal)" if s == 1.0 else f"{s}x"
            action = QAction(label, menu)
            action.setCheckable(True)
            if abs(s - self.tts.current_speed) < 0.05:
                action.setChecked(True)
            action.triggered.connect(lambda checked, val=s: self._on_speed_selected(val))
            menu.addAction(action)

        btn_geo = self.btn_speed.geometry()
        pos = self.mapToGlobal(QPoint(btn_geo.left(), btn_geo.top() - 10))
        menu.exec(pos)

    def _on_speed_selected(self, speed: float):
        """Applies selected speed and updates button label."""
        self.tts.set_speed(speed)
        self.btn_speed.setText(f"{speed}x ▾")
        settings_db.set("default_speed", speed)

    def _init_animations(self):
        # Entry animation group (Gentle slide up + Fade in)
        self.anim_group_in = QParallelAnimationGroup(self)
        self.pos_anim_in = QPropertyAnimation(self, b"pos")
        self.pos_anim_in.setDuration(280)
        self.pos_anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.fade_anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim_in.setDuration(280)
        self.fade_anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_group_in.addAnimation(self.pos_anim_in)
        self.anim_group_in.addAnimation(self.fade_anim_in)

        # Exit animation group (Slide down + Fade out)
        self.anim_group_out = QParallelAnimationGroup(self)
        self.pos_anim_out = QPropertyAnimation(self, b"pos")
        self.pos_anim_out.setDuration(200)
        self.pos_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)

        self.fade_anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim_out.setDuration(200)
        self.fade_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)

        self.anim_group_out.addAnimation(self.pos_anim_out)
        self.anim_group_out.addAnimation(self.fade_anim_out)
        self.anim_group_out.finished.connect(self._on_exit_finished)

        # Smooth auto-close fade-out animation
        self.auto_close_anim = QPropertyAnimation(self, b"windowOpacity")
        self.auto_close_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.auto_close_anim.finished.connect(self._on_auto_close_finished)

    def _get_bottom_right_pos(self) -> QPoint:
        """Calculates bottom-right docking position above dock/taskbar."""
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
        """Starts speaking text and animates the player in with smooth fade-in."""
        self.anim_group_out.stop()
        self.auto_close_anim.stop()

        dock_mode = settings_db.get("dock_position", "bottom_right")
        if dock_mode == "near_cursor" and show_at_pos:
            target_pos = show_at_pos
        else:
            target_pos = self._get_bottom_right_pos() if not self._user_moved else self.pos()

        start_pos = QPoint(target_pos.x(), target_pos.y() + 16)

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

    def _toggle_play_pause(self):
        """Toggles play / pause state. Resumes or replays on click."""
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
        else:
            # If playback was finished or idle, replay current text
            if getattr(self.tts, "current_text", None):
                self.btn_play_pause.set_playing(True)
                self.logo.start_voice_animation()
                self.tts.speak(self.tts.current_text)

    def hide_player(self):
        """Animates out and hides."""
        self.tts.stop()
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()
        self.auto_close_anim.stop()
        self.anim_group_in.stop()

        curr_pos = self.pos()
        end_pos = QPoint(curr_pos.x(), curr_pos.y() + 20)

        self.pos_anim_out.setStartValue(curr_pos)
        self.pos_anim_out.setEndValue(end_pos)

        self.fade_anim_out.setStartValue(self.windowOpacity())
        self.fade_anim_out.setEndValue(0.0)

        self.anim_group_out.start()

    def _on_exit_finished(self):
        self.hide()
        self.setWindowOpacity(1.0)
        self._user_moved = False
        self.closed.emit()

    # ─── Auto-Close Fadeout ──────────────────────────────────────────
    def _start_auto_close_fadeout(self, duration_sec: float):
        """Smoothly fades out player over duration_sec and dismisses it."""
        self.auto_close_anim.stop()
        self.auto_close_anim.setDuration(int(duration_sec * 1000))
        self.auto_close_anim.setStartValue(self.windowOpacity())
        self.auto_close_anim.setEndValue(0.0)
        self.auto_close_anim.start()

    def _on_auto_close_finished(self):
        """Hides player once fadeout is complete."""
        if self.windowOpacity() <= 0.05:
            self.hide()
            self.setWindowOpacity(1.0)
            self._user_moved = False
            self.closed.emit()

    def enterEvent(self, event):
        """Interrupts auto-close if user hovers mouse over player."""
        if self.auto_close_anim.state() == QPropertyAnimation.State.Running:
            self.auto_close_anim.stop()
            self.setWindowOpacity(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Restarts auto-close fadeout if user leaves and playback has ended."""
        if not self.btn_play_pause.is_playing and self.isVisible():
            if settings_db.get("auto_close_finished", True):
                delay = float(settings_db.get("auto_close_delay", 1.0))
                self._start_auto_close_fadeout(delay)
        super().leaveEvent(event)

    def _toggle_recording(self):
        """Toggles speech recording mode."""
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.btn_record.setIcon(create_record_icon(17, "#EF4444", recording=True))
            self.btn_record.setToolTip("Recording Speech... Click to finish & save to Documents/Voxel Recordings")
            self.btn_record.setStyleSheet("background-color: rgba(239, 68, 68, 0.25); border: 1px solid #EF4444; border-radius: 6px;")
            if not self.tts.is_speaking and getattr(self.tts, "current_text", ""):
                self.tts.speak(self.tts.current_text)
        else:
            self._finish_and_save_recording()

    def _finish_and_save_recording(self):
        """Saves accumulated audio chunks to the Voxel Recordings folder in Documents."""
        self.is_recording = False
        is_dark = (self._theme_mode == "dark_glass")
        rec_color = "#F87171" if is_dark else "#EF4444"
        self.btn_record.setIcon(create_record_icon(17, rec_color, recording=False))
        self.btn_record.setToolTip("Record Speech to MP3 (Saved to Documents/Voxel Recordings)")
        self.apply_theme(self._theme_mode)

        chunks = self.tts.get_speech_audio_chunks()
        text_hint = getattr(self.tts, "current_text", "")
        saved_file = save_recording_from_chunks(chunks, text_hint)
        if saved_file:
            self.recording_saved.emit(saved_file)

    # Audio Engine Callbacks
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
        if self.is_recording:
            self._finish_and_save_recording()
        if settings_db.get("auto_close_finished", True):
            delay_sec = float(settings_db.get("auto_close_delay", 1.0))
            self._start_auto_close_fadeout(delay_sec)

    def _on_playback_error(self, err: str):
        self.btn_play_pause.set_playing(False)
        self.logo.stop_voice_animation()

    # Window Dragging
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        r = h / 2.0  # Capsule round radius

        capsule_rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)

        if self._theme_mode == "dark_glass":
            # ── Dark Frosted Glass (Obsidian Glass) ──────────────────────
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor(22, 28, 44, 215))   # ~84% opacity
            grad.setColorAt(1.0, QColor(12, 16, 28, 225))   # ~88% opacity

            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor(255, 255, 255, 45), 1.2))
            painter.drawRoundedRect(capsule_rect, r, r)

            # Top specular glass edge reflection
            shine_rect = QRectF(r / 2.0, 2.0, w - r, h * 0.44)
            shine = QLinearGradient(0, 2.0, 0, h * 0.44)
            shine.setColorAt(0.0, QColor(255, 255, 255, 55))
            shine.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(shine))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(shine_rect, r * 0.8, r * 0.8)

        else:
            # ── Solid Elegant Light Capsule (No see-through white artifacts) ──
            # Premium clean off-white / porcelain capsule with subtle blue tint
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor(255, 255, 255, 255))
            grad.setColorAt(0.5, QColor(246, 249, 254, 255))
            grad.setColorAt(1.0, QColor(238, 243, 252, 255))

            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor(203, 213, 225, 220), 1.2))  # Clean refined slate border
            painter.drawRoundedRect(capsule_rect, r, r)

            # Ethereal top specular reflection sheen
            shine_rect = QRectF(r / 2.0, 1.5, w - r, h * 0.38)
            shine = QLinearGradient(0, 1.5, 0, h * 0.38)
            shine.setColorAt(0.0, QColor(255, 255, 255, 240))
            shine.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setBrush(QBrush(shine))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(shine_rect, r * 0.8, r * 0.8)

        painter.end()

    def _on_chunk_progress(self, current: int, total: int):
        if total > 1:
            self.lbl_brand.setText(f"Voxel {current}/{total}")
        else:
            self.lbl_brand.setText("Voxel")
