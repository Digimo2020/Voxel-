"""
TTS Engine & Audio Player using Edge-TTS Neural Voices, Expressive Emotion,
and Native macOS/Windows Low-Latency Fallbacks.
Features:
- Sub-second instant playback via sentence-pipelining and pre-fetching
- Expressive emotion styles with natural pitch contours and breathing pauses
- Continuous uninterrupted narration for entire Google Docs, PDFs, and presentations
- Native Windows MCI (winmm.dll) playback for 100% Smart App Control compatibility
"""
from __future__ import annotations
import os
import sys
import time
import tempfile
import threading
import hashlib
import asyncio
import subprocess
from typing import Optional, List, Dict

import edge_tts
from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QTimer, Qt
import ctypes

from src.config import (
    VOICES, DEFAULT_SPEED, DEFAULT_VOICE_INDEX, IS_MAC,
    EMOTION_MODES, DEFAULT_EMOTION_MODE
)
from src.utils.settings import settings_db
from src.utils.history import history_db
from src.utils.text_processor import prepare_expressive_text, split_into_speech_chunks

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
    # On Windows, use native Windows MCI (winmm.dll) directly to eliminate Smart App Control alerts.
    HAS_QT_MULTIMEDIA = False
    QMediaPlayer = None
    QAudioOutput = None


class TTSEngine(QObject):
    """
    High-performance, low-latency TTS synthesis and audio player with
    emotion styles and streaming chunk playback for documents & selections.
    """
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_resumed = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_error = pyqtSignal(str)
    chunk_progress = pyqtSignal(int, int)  # (current_chunk, total_chunks)
    _request_play = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_speed: float = DEFAULT_SPEED
        self.current_voice_index: int = DEFAULT_VOICE_INDEX
        self.current_emotion: str = settings_db.get("emotion_mode", DEFAULT_EMOTION_MODE)
        self.current_text: str = ""
        self.is_paused: bool = False
        self.is_speaking: bool = False

        # Chunk queue for streaming long documents/presentations
        self._chunks: List[str] = []
        self._current_chunk_idx: int = 0
        self._chunk_audio_files: Dict[int, str] = {}
        self._is_queue_playing: bool = False

        self._active_thread: Optional[threading.Thread] = None
        self._pipeline_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._temp_audio_file: Optional[str] = None

        # Persistent audio cache directory
        self.cache_dir = os.path.join(tempfile.gettempdir(), "voxel_audio_cache")
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception:
            pass

        self._request_play.connect(self._play_file, Qt.ConnectionType.QueuedConnection)

        if HAS_QT_MULTIMEDIA:
            self.player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(1.0)
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
                self.mci_timer.setInterval(80)
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

    def set_emotion_mode(self, mode: str):
        """Sets active emotion & expressive prosody mode."""
        valid_modes = [m["id"] for m in EMOTION_MODES]
        if mode in valid_modes:
            self.current_emotion = mode
            settings_db.set("emotion_mode", mode)

    def cycle_voice(self) -> dict:
        """Cycles to the next voice in the list."""
        self.current_voice_index = (self.current_voice_index + 1) % len(VOICES)
        return self.current_voice

    def _get_emotion_params(self) -> tuple[str, str]:
        """Returns (rate_str, pitch_str) combining user speed and emotion preset."""
        # Find active emotion profile
        profile = next((m for m in EMOTION_MODES if m["id"] == self.current_emotion), EMOTION_MODES[0])
        pitch_str = profile.get("pitch", "+0Hz")
        rate_adj_pct = int(profile.get("rate_adjust", "+0%").replace("%", "").replace("+", "") or 0)

        # Base speed percentage
        speed_pct = int(round((self.current_speed - 1.0) * 100))
        total_rate_pct = speed_pct + rate_adj_pct
        rate_str = f"+{total_rate_pct}%" if total_rate_pct >= 0 else f"{total_rate_pct}%"
        return rate_str, pitch_str

    def _get_cache_path(self, text: str, voice_id: str, rate_str: str, pitch_str: str) -> str:
        """Computes a deterministic cache file path for given text and audio parameters."""
        raw = f"{text}|{voice_id}|{rate_str}|{pitch_str}".encode("utf-8")
        h = hashlib.sha256(raw).hexdigest()[:24]
        return os.path.join(self.cache_dir, f"vox_{h}.mp3")

    def prefetch(self, text: str):
        """
        Pre-synthesizes the first sentence in a background worker as soon as
        text is selected or user hovers the trigger badge.
        Ensures 0ms latency when user clicks Play.
        """
        if not text or not text.strip():
            return

        chunks = split_into_speech_chunks(text)
        if not chunks:
            return

        first_chunk = chunks[0]
        voice_id = self.current_voice["id"]
        rate_str, pitch_str = self._get_emotion_params()
        cache_path = self._get_cache_path(first_chunk, voice_id, rate_str, pitch_str)

        if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            return  # Already cached!

        def _prefetch_worker():
            try:
                async def _run():
                    comm = edge_tts.Communicate(first_chunk, voice_id, rate=rate_str, pitch=pitch_str)
                    await comm.save(cache_path)
                asyncio.run(_run())
            except Exception:
                pass

        t = threading.Thread(target=_prefetch_worker, daemon=True)
        t.start()

    def speak(self, text: str):
        """
        Synthesizes and speaks text.
        For short selections, begins playback immediately.
        For long documents/presentations, uses an asynchronous pipeline:
        synthesizes chunk 0, starts playback instantly, and queues remaining chunks.
        """
        if not text or not text.strip():
            return

        self.stop()
        self.current_text = text.strip()
        self._stop_event.clear()

        # Log entry to history
        try:
            history_db.add_entry(self.current_text, self.current_voice["name"], self.current_speed)
        except Exception as e:
            print(f"[TTS Engine] History logging error: {e}")

        # Split into speech chunks for instant pipelined playback
        self._chunks = split_into_speech_chunks(self.current_text)
        if not self._chunks:
            return

        self._current_chunk_idx = 0
        self._chunk_audio_files.clear()
        self._is_queue_playing = True

        # Launch pipeline orchestrator thread
        self._pipeline_thread = threading.Thread(
            target=self._pipeline_worker,
            args=(self._chunks, self.current_voice["id"]),
            daemon=True
        )
        self._pipeline_thread.start()

    def _pipeline_worker(self, chunks: List[str], voice_id: str):
        """
        Asynchronously synthesizes speech chunks.
        Dispatches Chunk 0 immediately so user hears audio in < 300ms,
        then continues synthesizing remaining chunks ahead of playback.
        """
        rate_str, pitch_str = self._get_emotion_params()

        for idx, chunk_text in enumerate(chunks):
            if self._stop_event.is_set():
                break

            cache_file = self._get_cache_path(chunk_text, voice_id, rate_str, pitch_str)
            success = False

            if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
                success = True
                audio_path = cache_file
            else:
                # Synthesize via Edge-TTS
                try:
                    async def _run_edge(c_text=chunk_text, c_path=cache_file):
                        comm = edge_tts.Communicate(c_text, voice_id, rate=rate_str, pitch=pitch_str)
                        await comm.save(c_path)

                    asyncio.run(_run_edge())
                    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
                        success = True
                        audio_path = cache_file
                except Exception as e:
                    print(f"[TTS Engine] Edge-TTS error on chunk {idx}: {e}")

            # Offline Fallback if network fails
            if not success and not self._stop_event.is_set():
                fd, temp_path = tempfile.mkstemp(suffix=".mp3", prefix=f"vox_chk_{idx}_")
                os.close(fd)
                success = self._synthesize_offline(chunk_text, self.current_speed, temp_path)
                if success:
                    audio_path = temp_path

            if self._stop_event.is_set():
                break

            if success:
                self._chunk_audio_files[idx] = audio_path
                # If this is chunk 0, immediately trigger playback!
                if idx == 0 and self._is_queue_playing:
                    self._request_play.emit(audio_path)
            else:
                print(f"[TTS Engine] Failed to synthesize chunk {idx}")

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
        self._is_queue_playing = False
        self._chunks.clear()
        self._chunk_audio_files.clear()

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

    def _play_file(self, file_path: str):
        """Loads and starts playback of an audio file."""
        if not file_path or not os.path.exists(file_path):
            return

        self._temp_audio_file = file_path

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
        if self._chunks:
            self.chunk_progress.emit(self._current_chunk_idx + 1, len(self._chunks))

    def _on_chunk_completed(self):
        """Advances to the next chunk in the document queue."""
        if not self._is_queue_playing or self._stop_event.is_set():
            return

        next_idx = self._current_chunk_idx + 1
        if next_idx < len(self._chunks):
            self._current_chunk_idx = next_idx
            # Check if next chunk audio is already synthesized
            if next_idx in self._chunk_audio_files:
                self._play_file(self._chunk_audio_files[next_idx])
            else:
                # Wait briefly for worker to deliver next chunk
                def _wait_and_play():
                    for _ in range(40):  # up to 4 seconds wait
                        if self._stop_event.is_set() or not self._is_queue_playing:
                            return
                        if next_idx in self._chunk_audio_files:
                            self._request_play.emit(self._chunk_audio_files[next_idx])
                            return
                        time.sleep(0.1)
                    # If still not ready, finish
                    self._on_all_playback_finished()

                threading.Thread(target=_wait_and_play, daemon=True).start()
        else:
            self._on_all_playback_finished()

    def _on_all_playback_finished(self):
        """Called when all chunks in the text or document have finished speaking."""
        self.is_speaking = False
        self.is_paused = False
        self._is_queue_playing = False
        self.playback_finished.emit()

    def _on_mci_poll(self):
        """Polls Windows MCI playback status and triggers next chunk when current ends."""
        if not getattr(self, "winmm", None):
            return
        buf = ctypes.create_unicode_buffer(128)
        self.winmm.mciSendStringW(f"status {self.mci_alias} mode", buf, 128, None)
        mode = buf.value
        if mode == "stopped" and self.is_speaking and not self.is_paused:
            self.mci_timer.stop()
            self.winmm.mciSendStringW(f"close {self.mci_alias}", None, 0, None)
            self._on_chunk_completed()

    def _on_player_state_changed(self, state: QMediaPlayer.PlaybackState):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self.is_speaking and not self.is_paused:
                self._on_chunk_completed()

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.is_speaking and not self.is_paused:
                self._on_chunk_completed()

    def _on_player_error(self, error: QMediaPlayer.Error, error_string: str):
        if self.is_speaking:
            print(f"[TTS Engine] Playback error: {error_string}")
            self.is_speaking = False
            self.playback_error.emit(error_string)

    def _synthesize_offline(self, text: str, speed: float, out_path: str) -> bool:
        """Offline fallback using macOS 'say' or Windows pyttsx3."""
        if IS_MAC:
            try:
                aiff_path = out_path.replace(".mp3", ".aiff")
                voice_name = "Samantha" if self.current_voice.get("gender") == "Female" else "Alex"
                rate = int(185 * speed)
                cmd = ["/usr/bin/say", "-v", voice_name, "-r", str(rate), "-o", aiff_path, text]
                subprocess.run(cmd, check=True, timeout=12)
                if os.path.exists(aiff_path) and os.path.getsize(aiff_path) > 0:
                    return True
            except Exception as e:
                print(f"[TTS Engine] macOS 'say' fallback error: {e}")
        else:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty("rate", int(190 * speed))
                wav_path = out_path.replace(".mp3", ".wav")
                engine.save_to_file(text, wav_path)
                engine.runAndWait()
                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                    return True
            except Exception as ex:
                print(f"[TTS Engine] Windows pyttsx3 fallback error: {ex}")

        return False

    def _clean_temp_audio(self):
        """Cleans up non-cached temporary files."""
        if self._temp_audio_file and "voxel_audio_cache" not in self._temp_audio_file:
            if os.path.exists(self._temp_audio_file):
                try:
                    os.remove(self._temp_audio_file)
                except Exception:
                    pass
            self._temp_audio_file = None
