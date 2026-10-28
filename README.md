# Text 2 Voice (T2V) 🎙️🔊

A lightweight, system-wide floating utility for **Windows** (and **macOS**) that instantly speaks any selected text out loud with natural neural voices.

---

## ✨ Features

- **Universal Text Detection**: Select any text or word anywhere on your screen—in Chrome, Edge, Word, Notepad, VS Code, or even inside canvas-based web apps like **Google Docs**.
- **Smooth Floating Mic Bubble**: A minimal floating mic icon fades in smoothly right next to your mouse selection. Click to play, or keep typing to let it disappear automatically.
- **Sleek Floating Mini Player**:
  - **▶ / ⏸ Play & Pause**: Toggle playback at any moment.
  - **⏹ Stop**: Instantly halt speech and unload audio.
  - **Speed Controls (`-` / `+`)**: Easily change playback speed in steps (`0.5x`, `0.75x`, `1.0x`, `1.25x`, `1.5x`, `1.75x`, `2.0x`).
  - **Simple Voice Switcher**: One-click toggle between natural voices:
    - ♀ **Jenny** (US Female - Natural Neural)
    - ♂ **Guy** (US Male - Natural Neural)
    - ♀ **Sonia** (UK Female - Natural Neural)
  - **Offline Fallback**: Automatically falls back to built-in system voices (Microsoft SAPI5 on Windows / NSSpeech on Mac) if offline.
  - **Draggable Anywhere**: Click and drag the player pill anywhere on your screen.
- **Global Hotkey**: Prefer keyboard shortcuts? Press `Ctrl+Alt+S` (or `Cmd+Alt+S` on Mac) on any highlighted text to listen instantly.
- **System Tray Integration**: Discreetly sits in the Windows notification area (near the clock). Right-click to change default voice, test voices, toggle auto-popup on/off, or quit.
- **Clipboard Safe**: Reads highlighted text without corrupting or wiping your previous clipboard history.

---

## 🚀 Quick Start (Windows)

### Option 1: One-Click Run
Simply double-click:
```bat
run.bat
```

### Option 2: Running with Python
1. Ensure Python 3.10+ is installed:
   ```bash
   python --version
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## 📂 Project Structure

```text
Text 2 Voice/
│
├── src/
│   ├── config.py             # App configurations, voices, speed steps, theme
│   ├── tts_engine.py         # Neural TTS synthesis (Edge-TTS) & audio player
│   ├── selection_listener.py # Global mouse drag & double-click listener
│   ├── ui/
│   │   ├── floating_bubble.py# Smooth fade-in circular mic button
│   │   ├── mini_player.py    # Sleek floating mini player pill
│   │   └── tray_icon.py      # System tray icon & settings menu
│   └── utils/
│       └── clipboard.py      # Universal text grabber & clipboard restorer
│
├── assets/
│   └── icons.py              # High-DPI resolution-independent vector icons
│
├── run.bat                   # 1-click Windows launcher
├── main.py                   # Main application entry point
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # Documentation
```

---

## 🍎 macOS Porting Notes

The application is written using cross-platform components (`PyQt6`, `pynput`, `pyperclip`, `edge-tts`, `pygame`).

To run on macOS:
1. Run `python3 main.py`.
2. When prompted, grant **Accessibility** permissions in `System Settings > Privacy & Security > Accessibility` (required by macOS for global mouse hooks and selection capture).
3. Modifier keys automatically map from `Ctrl` to `Cmd`.

---

## 🐙 How to Push to GitHub

When you are ready to publish this to GitHub:

1. **Create a new repository** on GitHub (e.g. `Text-2-Voice`). Do **not** initialize it with a README or .gitignore (we already created them for you).
2. Open your terminal in this project folder and run:
   ```bash
   git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>.git
   git branch -M main
   git push -u origin main
   ```
