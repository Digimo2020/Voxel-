"""
TTS Engine & Audio Player supporting Edge-TTS Neural Voices and Offline SAPI5 Fallback.
Provides asynchronous synthesis, pause/resume, speed regulation, and playback callbacks.
"""
import os
import sys
import time
import tempfile
import threading
import asyncio
from typing import Optional, Callable

import pygame
import edge_tts
from PyQt6.QtCore import QObject, pyqtSignal

from src.config import VOICES, DEFAULT_SPEED, DEFAULT_VOICE_INDEX
from src.utils.history import history_db

# Initialize pygame mixer once
try:
    pygame.mixer.init()
except Exception as e:
    print(f"[TTS Engine] Warning initializing pygame mixer: {e}")


class TTSEngine(QObject):
    """
    Handles speech synthesis and playback control.
    Emits Qt signals so the UI updates smoothly without threading issues.
    """
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_resumed = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_speed: float = DEFAULT_SPEED
        self.current_voice_index: int = DEFAULT_VOICE_INDEX
        self.current_text: str = ""
        self.is_paused: bool = False
        self.is_speaking: bool = False

        self._active_thread: Optional[threading.Thread] = None
        self._watcher_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._temp_audio_file: Optional[str] = None

        # Offline pyttsx3 engine cache
        self._offline_engine = None

    @property
    def current_voice(self) -> dict:
        return VOICES[self.current_voice_index]

    def set_speed(self, speed: float):
        """Set speed multiplier (e.g. 0.75, 1.0, 1.25, 1.5, 2.0)."""
        self.current_speed = round(max(0.5, min(2.5, speed)), 2)

    def set_voice_index(self, index: int):
        """Change current voice index."""
        if 0 <= index < len(VOICES):
            self.current_voice_index = index

    def cycle_voice(self) -> dict:
        """Cycles to the next available voice and returns it."""
        self.current_voice_index = (self.current_voice_index + 1) % len(VOICES)
        return self.current_voice

    def speak(self, text: str):
        """Synthesizes and speaks text asynchronously."""
        if not text or not text.strip():
            return

        self.stop()
        self.current_text = text.strip()
        self._stop_event.clear()

        # Log to JSON history database
        try:
            history_db.add_entry(self.current_text, self.current_voice["name"], self.current_speed)
        except Exception as e:
            print(f"[TTS Engine] History logging error: {e}")

        # Start synthesis worker thread
        self._active_thread = threading.Thread(
            target=self._synthesize_and_play_worker,
            args=(self.current_text, self.current_voice["id"], self.current_speed),
            daemon=True
        )
        self._active_thread.start()

    def pause(self):
        """Pauses currently playing speech."""
        if self.is_speaking and not self.is_paused:
            try:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.playback_paused.emit()
            except Exception as e:
                print(f"[TTS Engine] Pause error: {e}")

    def resume(self):
        """Resumes paused speech."""
        if self.is_speaking and self.is_paused:
            try:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.playback_resumed.emit()
            except Exception as e:
                print(f"[TTS Engine] Resume error: {e}")

    def toggle_play_pause(self):
        """Toggles between play and pause, or restarts if stopped."""
        if not self.is_speaking:
            if self.current_text:
                self.speak(self.current_text)
        elif self.is_paused:
            self.resume()
        else:
            self.pause()

    def stop(self):
        """Stops playback and halts any running synthesis."""
        self._stop_event.set()
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except Exception:
            pass

        self.is_speaking = False
        self.is_paused = False
        self._clean_temp_audio()

    def _format_rate_str(self, speed: float) -> str:
        """Converts float multiplier (e.g. 1.25) to Edge-TTS rate string (e.g. '+25%')."""
        pct = int((speed - 1.0) * 100)
        return f"{pct:+d}%"

    def _synthesize_and_play_worker(self, text: str, voice_id: str, speed: float):
        """Worker thread for synthesizing audio and starting playback."""
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3", prefix="t2v_")
        os.close(temp_fd)
        self._temp_audio_file = temp_path

        rate_str = self._format_rate_str(speed)
        success = False

        # 1. Try high quality Edge-TTS
        try:
            async def run_edge():
                comm = edge_tts.Communicate(text, voice_id, rate=rate_str)
                await comm.save(temp_path)

            asyncio.run(run_edge())
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                success = True
        except Exception as e:
            print(f"[TTS Engine] Edge-TTS error (will fallback to offline SAPI5): {e}")

        # 2. Fallback to offline pyttsx3 if edge-tts fails (e.g. offline)
        if not success:
            if self._stop_event.is_set():
                self._clean_temp_audio()
                return
            success = self._synthesize_offline(text, speed, temp_path)

        if not success or self._stop_event.is_set():
            self._clean_temp_audio()
            if not self._stop_event.is_set():
                self.playback_error.emit("Failed to synthesize speech.")
            return

        # 3. Play audio through pygame.mixer
        try:
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            self.is_speaking = True
            self.is_paused = False
            self.playback_started.emit()

            # Start watcher thread to monitor playback finish
            self._start_watcher_thread()
        except Exception as e:
            print(f"[TTS Engine] Playback error: {e}")
            self.playback_error.emit(str(e))
            self.is_speaking = False

    def _synthesize_offline(self, text: str, speed: float, out_path: str) -> bool:
        """Generates audio using offline SAPI5 engine."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", int(190 * speed))
            # Match female / male
            voices = engine.getProperty("voices")
            target_gender = self.current_voice.get("gender", "Female")
            for v in voices:
                if target_gender.lower() in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break

            # Save to wav format
            wav_path = out_path.replace(".mp3", ".wav")
            engine.save_to_file(text, wav_path)
            engine.runAndWait()
            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                self._temp_audio_file = wav_path
                return True
        except Exception as ex:
            print(f"[TTS Engine] Offline fallback error: {ex}")
        return False

    def _start_watcher_thread(self):
        """Watches for music playback completion."""
        def watch():
            while self.is_speaking and not self._stop_event.is_set():
                time.sleep(0.08)
                try:
                    if not pygame.mixer.music.get_busy() and not self.is_paused:
                        # Finished speaking
                        break
                except Exception:
                    break

            if not self._stop_event.is_set() and self.is_speaking:
                self.is_speaking = False
                self.is_paused = False
                self.playback_finished.emit()
                self._clean_temp_audio()

        self._watcher_thread = threading.Thread(target=watch, daemon=True)
        self._watcher_thread.start()

    def _clean_temp_audio(self):
        """Removes the temporary audio file."""
        if self._temp_audio_file and os.path.exists(self._temp_audio_file):
            try:
                os.remove(self._temp_audio_file)
            except Exception:
                pass
            self._temp_audio_file = None
