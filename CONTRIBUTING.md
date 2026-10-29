# Contributing to Text 2 Voice (T2V) 🤝

Thank you for your interest in contributing to **Text 2 Voice**! We welcome community contributions, bug fixes, feature requests, and platform ports (especially the macOS and Linux implementations).

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Git**

### 2. Fork and Clone
```bash
git clone https://github.com/Digimo2020/Voxel-.git
cd Voxel-
```

### 3. Create a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 5. Run Locally in Development Mode
```bash
python main.py
```

---

## 🏗️ Architecture Overview

The codebase is intentionally modular and decoupled:

- **[`src/config.py`](src/config.py)**: Central configuration for voices, speed presets, UI themes, and hotkeys.
- **[`src/selection_listener.py`](src/selection_listener.py)**: Low-level global mouse drag and hotkey interception powered by `pynput`.
- **[`src/utils/clipboard.py`](src/utils/clipboard.py)**: Safe clipboard extraction that captures selected text without overwriting the user's prior clipboard.
- **[`src/tts_engine.py`](src/tts_engine.py)**: Speech synthesis utilizing `edge-tts` (online neural) with fallback to `pyttsx3` (offline SAPI5).
- **[`src/utils/history.py`](src/utils/history.py)**: Lightweight JSON database storing spoken history to `%LOCALAPPDATA%/Text2Voice/history.json`.
- **[`src/ui/floating_bubble.py`](src/ui/floating_bubble.py)**: Frameless floating micro-UI trigger with cubic fade-in animation.
- **[`src/ui/mini_player.py`](src/ui/mini_player.py)**: Sleek floating player pill with draggable window handling, speed regulator, and voice cycling.
- **[`src/ui/history_dialog.py`](src/ui/history_dialog.py)**: History list with replay and clipboard copy buttons.
- **[`src/ui/tray_icon.py`](src/ui/tray_icon.py)**: System tray icon and context menu.

---

## 💡 How to Add a New Voice

Open `src/config.py` and append your desired Edge-TTS voice to `VOICES`:

```python
{
    "id": "en-AU-NatashaNeural",
    "name": "Natasha (Female)",
    "gender": "Female",
    "country": "AU",
    "label": "Natasha (AU Female)",
    "short_label": "Natasha"
}
```

---

## 📦 Building the Standalone `.exe`

To compile the application into a single executable:
```bash
build_exe.bat
# or manually via:
pyinstaller Text2Voice.spec
```
The output binary will be generated in `dist/Text2Voice.exe`.

---

## 📝 Pull Request Guidelines

1. Create a feature branch (`git checkout -b feature/amazing-feature`).
2. Keep code clean and self-documenting.
3. Verify that selection detection works across both desktop apps (Notepad) and web apps (Chrome, Google Docs).
4. Commit your changes (`git commit -m 'feat: Add amazing feature'`).
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request!
