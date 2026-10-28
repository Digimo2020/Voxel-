# Voxel — Text to Speech, Anywhere

<p align="left">
  <a href="https://github.com/Digimo2020/Voxel---V.002/releases"><img src="https://img.shields.io/badge/Version-v1.0.01-0084FF?style=flat-square" alt="Version v1.0.01"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License: MIT"></a>
  <a href="https://github.com/Digimo2020/Voxel---V.002"><img src="https://img.shields.io/badge/GitHub-Digimo2020%2FVoxel-181717?style=flat-square&logo=github" alt="GitHub Repository"></a>
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-6366F1?style=flat-square" alt="Platform: macOS & Windows">
</p>

A lightweight, frosted glass desktop utility for reading selected text aloud across any application on **macOS** and **Windows**, featuring a voice-reactive microphone logo with real-time waveform animations and an animated capsule mini-player.

---

## 🎨 Features & Visual Design

- **Floating Voxel Logo Trigger**: Smoothly fades in near selected text without stealing window focus. Fades out automatically on dismissal or click.
- **Voice-Reactive Animated Mic Logo**: The 3 horizontal lines inside the microphone capsule dynamically animate and pulse like an audio equalizer in real-time as speech plays, accompanied by a soft breathing glow.
- **Frosted Glass Capsule Mini-Player**: Sleek translucent acrylic capsule that slides up with smooth easing curves from the bottom-right of the screen above the Dock/Taskbar.
- **Vibrant Gradient Controls**: Glowing electric cyan & violet play/pause button, delicate stop button, segmented speed controller (`[-] 1.0x [+]`), and instant voice switcher.
- **High-Definition Neural Voices**: Microsoft Edge Neural TTS voices (Jenny, Guy, Sonia, Aria) with automatic offline fallback to native macOS Speech (`Samantha`, `Alex`) or Windows SAPI5.
- **Menu Bar / System Tray Integration**: Native macOS Menu Bar status item and Windows notification icon with quick access to voice switching, history, settings, and one-click clipboard reading.
- **Zero-Dependency Audio Stack**: Built directly on `PyQt6.QtMultimedia` with native CoreAudio and AVFoundation hardware acceleration.
- **macOS Accessibility Assistance**: Built-in permission checker and quick-launch helper to enable required Accessibility permissions seamlessly.

---

## 🚀 Quick Start on macOS

### Option 1: Run from Source (Development)
```bash
git clone https://github.com/Digimo2020/Voxel---V.002.git
cd Voxel---V.002
chmod +x run.sh
./run.sh
```

### Option 2: Build Native macOS App & DMG
```bash
chmod +x build_mac.sh
./build_mac.sh
```
This generates:
- Standalone App Bundle: `dist/Voxel.app`
- Drag-and-Drop Installer: `dist/Voxel.dmg`

---

## 💻 Quick Start on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
*(Or double-click `run.bat`). To build `Voxel.exe`, run `build_exe.bat`.*

---

## ⌨️ Workflow & Shortcuts

1. **Highlight text** in any document, browser, PDF, or text editor.
2. The **Voxel Logo badge** smoothly fades in near your cursor.
3. Click the logo (or press `Cmd+Alt+S` on Mac / `Ctrl+Alt+S` on Windows) to start listening.
4. The capsule mini-player slides up smoothly in the bottom-right corner.
5. The 3 voice lines inside the microphone animate in sync with playback.
6. Adjust speed, switch voices, view speech history, or configure preferences anytime.

---

## 🗺 Repository Architecture

```text
main.py                      Application entry point & event orchestrator
src/config.py                Voxel brand tokens, themes, voice presets & paths
src/selection_listener.py    Global mouse drag & hotkey interception (macOS & Windows)
src/tts_engine.py            QtMultimedia player, Edge-TTS & native macOS 'say' fallback
src/ui/voxel_logo_widget.py  Vector Voxel logo with 40 FPS voice-reactive wave animation
src/ui/floating_bubble.py    Floating Voxel logo trigger with smooth fade animations
src/ui/mini_player.py        Frosted glass capsule player with glowing controls
src/ui/tray_icon.py          Menu bar & system tray controller
src/ui/settings_dialog.py    Preferences, about dialog & macOS accessibility checker
src/ui/history_dialog.py     Persistent JSON speech history viewer & replay
src/utils/mac_permissions.py macOS Accessibility check and System Settings URL launcher
src/utils/clipboard.py       Safe clipboard extraction with original contents restoration
src/utils/settings.py        Cross-platform preferences (~/Library/Application Support/Voxel)
src/utils/history.py         Cross-platform history database
assets/icons.py              High-DPI vector icons (cradle, mic, play, pause, stop, etc.)
build_mac.sh                 Automated macOS .app and .dmg compiler
run.sh                       One-click macOS launcher
.github/workflows/build.yml  Multi-platform automated CI/CD for macOS & Windows releases
```

---

## 📄 License

Distributed under the [MIT License](LICENSE). Created and maintained by **Digimo2020**.
