# Text 2 Voice

<p align="left">
  <a href="https://github.com/Digimo2020/Text-2-Voice/releases"><img src="https://img.shields.io/badge/Version-v1.0.01-60A5FA?style=flat-square" alt="Version v1.0.01"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License: MIT"></a>
  <a href="https://github.com/Digimo2020/Text-2-Voice"><img src="https://img.shields.io/badge/GitHub-Digimo2020%2FText--2--Voice-181717?style=flat-square&logo=github" alt="GitHub Repository"></a>
</p>

A lightweight, frosted glass desktop utility for reading selected text aloud using a transparent floating trigger and an animated bottom-right mini player.

---

## Current Implementation (v1.0.01)

The current source includes:
- **Transparent 30px Floating Speaker Trigger**: Subtle, non-intrusive vector speaker icon near text selections without dark backgrounds.
- **Bottom-Right Slide-Up Mini Player**: Frosted glass capsule pill that animates smoothly from the bottom right corner above the taskbar.
- **Playback Controls**: Play/Pause, Stop, and fine-tuned `[-] 1.0x [+]` speed regulation (`0.5x` to `2.0x`).
- **Natural Neural Voices**: Microsoft Edge TTS (Jenny, Guy, Sonia) with automatic offline Microsoft SAPI5 fallback.
- **Settings & About Dialog**: Configure default voice, speed, trigger timeout, docking positions, view version information, and open the GitHub repository.
- **Local JSON History Database**: Automatically records spoken snippets to `%LOCALAPPDATA%/Text2Voice/history.json` with replay support.
- **System Tray Integration**: Taskbar notification area menu with direct access to settings, history, and voice switching.
- **Standalone Windows Build**: PyInstaller workflow generating a zero-dependency `Text2Voice.exe`.

---

## 🔢 Versioning Scheme

Text 2 Voice follows a structured base-10 rollover versioning system:

**Format:** `v<Major>.<Minor>.<Patch:02d>` *(Current: `v1.0.01`)*

- The **patch** number runs from `01` to `09`. On the 10th iteration, it resets to `00` and the **minor** number (left) increments by 1:
  - `v1.0.09` ➔ `v1.1.00`
- On every 10th minor cycle, the minor number resets to `0` and the **major** number increments:
  - `v1.9.09` ➔ `v2.0.00`

---

## Intended Workflow

1. Select text in any desktop application, browser, or document.
2. A transparent floating speaker button appears near the pointer.
3. Click the speaker to start listening.
4. The mini-player slides up smoothly in the bottom-right corner of your screen.
5. Use the player to pause/resume, adjust speed, switch voices, access settings, or close.
6. Access preferences and history anytime from the system tray or player gear icon.

---

## Technology Stack

- **Python 3.11**
- **PyQt6**: Translucent frosted glass GUI and vector QPainter rendering
- **pynput**: Cross-platform global mouse drag and hotkey interception
- **pyperclip**: Safe clipboard extraction with instant restoration
- **edge-tts**: Neural speech synthesis
- **pyttsx3**: Offline Windows SAPI5 voice fallback
- **pygame.mixer**: Low-latency audio streaming
- **PyInstaller**: Windows standalone executable packaging

---

## Quick Start on Windows

### Option 1: Standalone Executable (For Users)
Download `Text2Voice.exe` from the [Releases](https://github.com/Digimo2020/Text-2-Voice/releases) tab and double-click to run. No Python installation required.

### Option 2: Run from Source (For Developers)
```powershell
git clone https://github.com/Digimo2020/Text-2-Voice.git
cd Text-2-Voice
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```
*(Or simply double-click `run.bat`).*

---

## Building the Executable

```powershell
build_exe.bat
```
Output executable will be placed in `dist/Text2Voice.exe`.

---

## Repository Map

```text
main.py                    Application entry point & event orchestrator
src/config.py              Voice profiles, speed presets, and theme palettes
src/selection_listener.py  Global mouse drag & hotkey listeners
src/tts_engine.py          Multi-threaded speech synthesis & audio playback
src/ui/                    Floating bubble, mini player, tray, settings, history dialog
src/utils/                 Settings, clipboard, history, and version utilities
assets/icons.py            Vector icons (speaker, play, pause, stop, gear, close)
scripts/                   Preview-image generation script
.github/workflows/         Build and CI automation
requirements.txt           Python dependencies
build_exe.bat              Windows packaging helper
run.bat                    Windows development launcher
ROADMAP.md                 Planned features (macOS port, multi-language, OCR)
CONTRIBUTING.md            Contributor onboarding guide
SECURITY.md                Responsible vulnerability reporting
CHANGELOG.md               Verified version changelog
LICENSE                    MIT License
```

---

## Project & Community

- **Repository**: [https://github.com/Digimo2020/Text-2-Voice](https://github.com/Digimo2020/Text-2-Voice)
- **Maintainer**: Digimo2020
- **License**: [MIT License](LICENSE)
