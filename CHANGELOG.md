# Changelog

All notable changes to the **Text 2 Voice** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-28

### Added
- **Universal Text Detection**: Global mouse drag and double-click listener (`src/selection_listener.py`) powered by `pynput`, capturing highlighted text across browsers, document editors, IDEs, and canvas apps like Google Docs.
- **Safe Clipboard Restorer**: Universal clipboard interception (`src/utils/clipboard.py`) simulating silent copy and immediately restoring previous clipboard data.
- **24px Frosted Glass Speaker Trigger**: Unobtrusive floating trigger bubble (`src/ui/floating_bubble.py`) with line-art speaker icon and smooth cubic fade-in animation.
- **Translucent Frosted Glass Mini Player**: Draggable pill widget (`src/ui/mini_player.py`) with play/pause, stop, and clean circular line-art controls.
- **Speed Regulation**: Responsive `-` and `+` speed adjustments with presets (`0.5x`, `0.75x`, `1.0x`, `1.25x`, `1.5x`, `1.75x`, `2.0x`).
- **Neural Voice Synthesis**: Edge-TTS integration supporting Jenny (US Female), Guy (US Male), and Sonia (UK Female) with automatic offline Microsoft SAPI5 fallback (`src/tts_engine.py`).
- **Local JSON History Database**: Lightweight JSON storage (`src/utils/history.py`) persisting recent speech snippets, timestamps, voice used, and speed.
- **History Viewer & Replay Dialog**: Dedicated UI (`src/ui/history_dialog.py`) to browse past texts, copy to clipboard, or replay audio.
- **System Tray Integration**: Taskbar notification area icon (`src/ui/tray_icon.py`) with popup toggle, voice selector, and quick exit.
- **Standalone Windows Build**: PyInstaller build pipeline (`build_exe.bat`) producing a standalone zero-dependency `Text2Voice.exe`.
