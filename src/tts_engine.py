"""
TTS Engine & Audio Player using Edge-TTS Neural Voices and Native macOS Speech Fallback.
Powered by PyQt6.QtMultimedia for zero-dependency, ultra-smooth playback on macOS and Windows.
"""
from __future__ import annotations
import os
import sys
import time
import tempfile
import threading
import asyncio
import subprocess
from typing import Optional

import edge_tts
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QTimer, Qt
import ctypes

from src.config import VOICES, DEFAULT_SPEED, DEFAULT_VOICE_INDEX, IS_MAC
from src.utils.history import history_db

if IS_MAC:
    try:
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
        HAS_QT_MULTIMEDIA = True
    except (ImportError, Exception) as _qt_media_err:
        print(f"[TTS Engine] QtMultimedia unavailable ({_qt_media_err}), falling back to native macOS audio.")
        HAS_QT_MULTIMEDIA = False
        QMediaPlayer = None
        QAudioOutput = None
else:
    # On Windows, use native Windows MCI (winmm.dll) directly.
    # This prevents Windows Smart App Control (SAC) from triggering "Part of this app has been blocked"
    # caused by unsigned ffmpegmediaplugin.dll and QtMultimedia.pyd.
    HAS_QT_MULTIMEDIA = False
    QMediaPlayer = None
    QAudioOutput = None


class TTSEngine(QObject):
    """
    Handles speech synthesis and low-latency audio playback via QtMultimedia.
    """
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_resumed = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_error = pyqtSignal(str)
    _request_play = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_speed: float = DEFAULT_SPEED
        self.current_voice_index: int = DEFAULT_VOICE_INDEX
        self.current_text: str = ""
        self.is_paused: bool = False
        self.is_speaking: bool = False

        self._active_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._temp_audio_file: Optional[str] = None

        self._request_play.connect(self._play_file, Qt.ConnectionType.QueuedConnection)

        if HAS_QT_MULTIMEDIA:
            # Native Qt Audio Player & Output
            self.player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(1.0)

            # Connect Qt Player Signals
            self.player.playbackStateChanged.connect(self._on_player_state_changed)
            self.player.mediaStatusChanged.connect(self._on_media_status_changed)
            self.player.errorOccurred.connect(self._on_player_error)
        else:
            self.player = None
            self.audio_output = None
            if not IS_MAC:
                self.winmm = ctypes.windll.winmm
                self.mci_alias = f"voxel_mci_{os.getpid()}"
                self.mci_timer = QTimer(self)
                self.mci_timer.setInterval(100)
                self.mci_timer.timeout.connect(self._on_mci_poll)
            else:
                self.winmm = None
                self._mac_audio_proc = None

    @property
    def current_voice(self) -> dict:
        return VOICES[self.current_voice_index]

    def set_speed(self, speed: float):
        """Sets playback speed multiplier (0.5x to 2.5x)."""
        self.current_speed = round(max(0.5, min(2.5, speed)), 2)

    def set_voice_index(self, index: int):
        """Sets current voice index."""
        if 0 <= index < len(VOICES):
            self.current_voice_index = index

    def cycle_voice(self) -> dict:
        """Cycles to the next voice in the list."""
        self.current_voice_index = (self.current_voice_index + 1) % len(VOICES)
        return self.current_voice

    def speak(self, text: str):
        """Synthesizes and speaks text asynchronously."""
        if not text or not text.strip():
            return

        self.stop()
        self.current_text = text.strip()
        self._stop_event.clear()

        # Log entry to JSON history database
        try:
            history_db.add_entry(self.current_text, self.current_voice["name"], self.current_speed)
        except Exception as e:
            print(f"[TTS Engine] History logging error: {e}")

        # Launch synthesis in background thread
        self._active_thread = threading.Thread(
            target=self._synthesize_worker,
            args=(self.current_text, self.current_voice["id"], self.current_speed),
            daemon=True
        )
        self._active_thread.start()

    def pause(self):
        """Pauses currently playing speech."""
        if self.is_speaking and not self.is_paused:
            if HAS_QT_MULTIMEDIA and self.player:
                self.player.pause()
            elif not IS_MAC and getattr(self, "winmm", None):
                self.winmm.mciSendStringW(f"pause {self.mci_alias}", None, 0, None)
            self.is_paused = True
            self.playback_paused.emit()

    def resume(self):
        """Resumes paused speech."""
        if self.is_speaking and self.is_paused:
            if HAS_QT_MULTIMEDIA and self.player:
                self.player.play()
            elif not IS_MAC and getattr(self, "winmm", None):
                self.winmm.mciSendStringW(f"resume {self.mci_alias}", None, 0, None)
            self.is_paused = False
            self.playback_resumed.emit()

    def toggle_play_pause(self):
        """Toggles between pause and resume."""
        if not self.is_speaking:
            if self.current_text:
                self.speak(self.current_text)
            return

        if self.is_paused:
            self.resume()
        else:
            self.pause()

    def stop(self):
        """Stops current synthesis and audio playback immediately."""
        self._stop_event.set()
        if HAS_QT_MULTIMEDIA and self.player:
            self.player.stop()
        elif not IS_MAC and getattr(self, "winmm", None):
            if hasattr(self, "mci_timer"):
                self.mci_timer.stop()
            self.winmm.mciSendStringW(f"stop {self.mci_alias}", None, 0, None)
            self.winmm.mciSendStringW(f"close {self.mci_alias}", None, 0, None)
        elif IS_MAC and getattr(self, "_mac_audio_proc", None):
            try:
                self._mac_audio_proc.terminate()
            except Exception:
                pass
            self._mac_audio_proc = None

        self.is_speaking = False
        self.is_paused = False
        self._clean_temp_audio()

    def _format_rate_str(self, speed: float) -> str:
        pct = int(round((speed - 1.0) * 100))
        return f"+{pct}%" if pct >= 0 else f"{pct}%"

    def _synthesize_worker(self, text: str, voice_id: str, speed: float):
        """Background thread worker to synthesize audio to disk."""
        fd, temp_path = tempfile.mkstemp(suffix=".mp3", prefix="voxel_speech_")
        os.close(fd)
        self._temp_audio_file = temp_path

        rate_str = self._format_rate_str(speed)
        success = False

        # 1. Primary: High Quality Neural Edge-TTS
        try:
            async def run_edge():
                comm = edge_tts.Communicate(text, voice_id, rate=rate_str)
                await comm.save(temp_path)

            asyncio.run(run_edge())
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                success = True
        except Exception as e:
            print(f"[TTS Engine] Edge-TTS error (will fallback to offline engine): {e}")

        # 2. Offline Fallback
        if not success and not self._stop_event.is_set():
            success = self._synthesize_offline(text, speed, temp_path)

        if not success or self._stop_event.is_set():
            self._clean_temp_audio()
            if not self._stop_event.is_set():
                self.playback_error.emit("Failed to synthesize speech.")
            return

        # Play generated audio on main thread via Qt queued signal
        self._request_play.emit(self._temp_audio_file)

    def _synthesize_offline(self, text: str, speed: float, out_path: str) -> bool:
        """Synthesizes speech using native macOS 'say' command or Windows fallback."""
        if IS_MAC:
            try:
                # macOS native speech command
                aiff_path = out_path.replace(".mp3", ".aiff")
                voice_name = "Samantha" if self.current_voice.get("gender") == "Female" else "Alex"
                rate = int(185 * speed)
                cmd = ["/usr/bin/say", "-v", voice_name, "-r", str(rate), "-o", aiff_path, text]
                subprocess.run(cmd, check=True, timeout=12)
                if os.path.exists(aiff_path) and os.path.getsize(aiff_path) > 0:
                    self._temp_audio_file = aiff_path
                    return True
            except Exception as e:
                print(f"[TTS Engine] macOS native 'say' fallback error: {e}")
        else:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty("rate", int(190 * speed))
                wav_path = out_path.replace(".mp3", ".wav")
                engine.save_to_file(text, wav_path)
                engine.runAndWait()
                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                    self._temp_audio_file = wav_path
                    return True
            except Exception as ex:
                print(f"[TTS Engine] Windows pyttsx3 fallback error: {ex}")

        return False

    def _play_file(self, file_path: str):
        """Loads and starts playback on QMediaPlayer or Windows MCI."""
        if not file_path or not os.path.exists(file_path):
            return

        if HAS_QT_MULTIMEDIA and self.player:
            url = QUrl.fromLocalFile(file_path)
            self.player.setSource(url)
            self.player.play()
        elif not IS_MAC and getattr(self, "winmm", None):
            self.winmm.mciSendStringW(f"close {self.mci_alias}", None, 0, None)
            ret = self.winmm.mciSendStringW(f'open "{file_path}" type mpegvideo alias {self.mci_alias}', None, 0, None)
            if ret != 0:
                print(f"[TTS Engine] Windows MCI open error: {ret}")
                self.playback_error.emit(f"Windows audio playback error (code {ret})")
                return
            ret_play = self.winmm.mciSendStringW(f"play {self.mci_alias}", None, 0, None)
            if ret_play != 0:
                print(f"[TTS Engine] Windows MCI play error: {ret_play}")
                self.playback_error.emit(f"Windows audio play error (code {ret_play})")
                return
            self.mci_timer.start()
        elif IS_MAC:
            try:
                self._mac_audio_proc = subprocess.Popen(["/usr/bin/afplay", file_path])
            except Exception as e:
                self.playback_error.emit(str(e))
                return

        self.is_speaking = True
        self.is_paused = False
        self.playback_started.emit()

    def _on_mci_poll(self):
        """Polls Windows MCI playback status and signals completion when stopped."""
        if not getattr(self, "winmm", None):
            return
        buf = ctypes.create_unicode_buffer(128)
        self.winmm.mciSendStringW(f"status {self.mci_alias} mode", buf, 128, None)
        mode = buf.value
        if mode == "stopped" and self.is_speaking and not self.is_paused:
            self.is_speaking = False
            self.mci_timer.stop()
            self.winmm.mciSendStringW(f"close {self.mci_alias}", None, 0, None)
            self.playback_finished.emit()
            self._clean_temp_audio()

    def _on_player_state_changed(self, state: QMediaPlayer.PlaybackState):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self.is_speaking:
                self.is_speaking = False
                self.is_paused = False
                self.playback_finished.emit()
                self._clean_temp_audio()

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.is_speaking:
                self.is_speaking = False
                self.is_paused = False
                self.playback_finished.emit()
                self._clean_temp_audio()

    def _on_player_error(self, error: QMediaPlayer.Error, error_string: str):
        if self.is_speaking:
            print(f"[TTS Engine] Playback error: {error_string}")
            self.is_speaking = False
            self.playback_error.emit(error_string)
            self._clean_temp_audio()

    def _clean_temp_audio(self):
        """Cleans up temporary audio files."""
        if self._temp_audio_file and os.path.exists(self._temp_audio_file):
            try:
                os.remove(self._temp_audio_file)
            except Exception:
                pass
            self._temp_audio_file = None
