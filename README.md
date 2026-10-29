# Voxel — Text to Speech, Anywhere

<p align="center">
  <img src="assets/banner.png" alt="Voxel Banner" width="100%">
</p>

<p align="center">
  <a href="https://github.com/Digimo2020/Voxel---V.002/releases"><img src="https://img.shields.io/badge/Version-v1.0.01-0084FF?style=for-the-badge&logo=apple" alt="Version v1.0.01"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-6366F1?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://github.com/Digimo2020/Voxel---V.002"><img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-00C6FF?style=for-the-badge" alt="Platform: macOS & Windows"></a>
  <a href="https://github.com/Digimo2020/Voxel---V.002/releases/latest"><img src="https://img.shields.io/github/downloads/Digimo2020/Voxel---V.002/total?style=for-the-badge&color=7C3AED&label=Downloads" alt="GitHub Downloads"></a>
</p>

---

## 🎙 What is Voxel?

**Voxel** is a lightweight, frosted glass desktop utility for reading highlighted text aloud anywhere on **macOS** and **Windows**. 

Featuring a **voice-reactive microphone logo** with real-time waveform equalizer animations, a subtle floating selection trigger, and an animated bottom-right capsule player, Voxel blends seamlessly into your workflow across any document, web browser, PDF, or text editor.

---

## ✨ Key Features & UX Design

- 🌊 **Voice-Reactive Waveform Animation**: The 3 internal lines of the microphone capsule pulse and dance at 40 FPS like a real-time audio equalizer during playback, accented by a soft breathing radial glow.
- 🫧 **Non-Intrusive Floating Trigger**: Appears smoothly with fade-in easing near your cursor whenever you highlight text, without stealing window focus (`WA_ShowWithoutActivating`).
- 💊 **Frosted Glass Capsule Player**: Slides up above your Dock/Taskbar with smooth cubic easing. Includes a glowing electric blue-to-violet play/pause button, delicate stop button, segmented speed regulator (`[-] 1.0x [+]`), and voice switcher.
- 📦 **System-Wide macOS `.pkg` Installer**: Universal installer package targeting `/Applications/Voxel.app` for **all users** on the system, complete with embedded UX design screenshots in the Apple Installer wizard.
- 👁️ **Platform-Adaptive "Invisible" Downloads**: Download options automatically adapt to the user's operating system. On macOS, Windows executables are hidden; on Windows, macOS packages are hidden.
- 🗣️ **High-Definition Neural Voices**: Microsoft Edge Neural TTS voices (Jenny, Guy, Sonia, Aria) with instant offline fallback to native macOS Speech (`Samantha`, `Alex`) or Windows SAPI5.
- ⚡ **Zero-Dependency Audio Engine**: Modernized with `PyQt6.QtMultimedia` for hardware-accelerated CoreAudio playback without SDL or external C dependencies.
- 🛡️ **macOS Accessibility Assistant**: Proactive permissions checker with 1-click shortcut to macOS Privacy & Security settings.

---

## 🎨 Visual Showcase

<p align="center">
  <img src="assets/branding/mini_player_themes.png" alt="Voxel Mini Player Themes (Dark & Frosted Glass)" width="95%">
</p>

<p align="center">
  <em>Figure 1: Dual Theme Modes — Dark Acrylic Capsule & Frosted Iridescent Glass Capsule</em>
</p>

<p align="center">
  <img src="assets/voxel_mac_preview.png" alt="Voxel macOS Native UI Preview" width="95%">
</p>

<p align="center">
  <em>Figure 2: Native macOS Micro-UI — Floating Selection Badge & Voice-Reactive Mini Player</em>
</p>

---

## 🚀 Quick Download & Installation

###  For macOS Users

| Package Format | Description | Target |
| :--- | :--- | :--- |
| [**📥 Download Voxel.pkg**](https://github.com/Digimo2020/Voxel---V.002/releases/latest/download/Voxel.pkg) *(Recommended)* | Apple System-Wide Installer with embedded UX design preview wizard | `/Applications` (All Users) |
| [**📥 Download Voxel.dmg**](https://github.com/Digimo2020/Voxel---V.002/releases/latest/download/Voxel.dmg) | Standard drag-and-drop disk image | Portable / `/Applications` |

#### Run from Source (macOS)
```bash
git clone https://github.com/Digimo2020/Voxel---V.002.git
cd Voxel---V.002
chmod +x run.sh
./run.sh
```

---

### ⊞ For Windows Users

| Package Format | Description | Target |
| :--- | :--- | :--- |
| [**📥 Download Voxel.exe**](https://github.com/Digimo2020/Voxel---V.002/releases/latest/download/Voxel.exe) *(Recommended)* | Zero-dependency standalone Windows executable | Windows 10 / 11 |

#### Run from Source (Windows)
```powershell
git clone https://github.com/Digimo2020/Voxel---V.002.git
cd Voxel---V.002
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
*(Or double-click `run.bat`).*

---

## ⌨️ Workflow & Keyboard Shortcuts

```text
  1. Highlight text in any app (Browser, Word, Slack, PDF, Terminal)
                         │
                         ▼
  2. Floating Voxel Logo fades in smoothly near your cursor
                         │
                         ▼
  3. Click the Logo  — OR —  press Global Hotkey:
       • macOS:   Cmd + Option + S
       • Windows: Ctrl + Alt + S
                         │
                         ▼
  4. Frosted Glass Capsule Player slides up in the bottom-right corner
                         │
                         ▼
  5. 3 Voice Lines inside the mic animate in sync with real-time speech!
```

---

## 🛠️ Building Packages from Source

### Building on macOS (`.app`, `.dmg` & `.pkg`)
```bash
chmod +x build_mac.sh
./build_mac.sh
```
Outputs:
- **`dist/Voxel.app`**: Native standalone application bundle.
- **`dist/Voxel.pkg`**: System-wide installer for `/Applications` with embedded UX assets.
- **`dist/Voxel.dmg`**: Drag-and-drop installer disk image.

### Building on Windows (`.exe`)
```powershell
.\build_exe.bat
```
Outputs:
- **`dist/Voxel.exe`**: Zero-dependency standalone executable.

---

## 🗺️ Repository Architecture

```text
main.py                      Application entry point & event coordinator
run.sh                       One-click macOS development launcher
run.bat                      One-click Windows development launcher
build_mac.sh                 Compiles Voxel.app, Voxel.dmg and Voxel.pkg
build_exe.bat                Compiles Voxel.exe for Windows
assets/
 ├── banner.png              Official repository showcase banner
 ├── icon.icns               High-DPI Retina macOS application icon
 ├── icon_1024.png           1024x1024 master icon artwork
 ├── voxel_mac_preview.png   High-resolution micro-UI layout snapshot
 ├── icons.py                QPainter vector graphics generator
 └── branding/               Official design system guidelines & themes
src/
 ├── config.py               Theme tokens, voice profiles, and platform flags
 ├── selection_listener.py   Global mouse drag & hotkey interception (macOS/Win)
 ├── tts_engine.py           PyQt6.QtMultimedia player & neural Edge-TTS with fallback
 ├── ui/
 │    ├── voxel_logo_widget.py Voice-reactive animated mic logo (40 FPS)
 │    ├── floating_bubble.py   Smooth fade-in selection trigger badge
 │    ├── mini_player.py       Frosted glass capsule player with glowing controls
 │    ├── tray_icon.py         macOS Menu Bar / Windows System Tray controller
 │    ├── settings_dialog.py   Preferences & OS-adaptive download center
 │    └── history_dialog.py    Persistent JSON speech history & replay
 └── utils/
      ├── mac_permissions.py  macOS Accessibility permission helper
      ├── clipboard.py        Safe clipboard extraction & restoration
      ├── settings.py         Cross-platform settings (~/Library/Application Support/Voxel)
      ├── history.py          Speech history persistence
      └── version.py          Base-10 rollover version tracking
.github/workflows/
 └── build.yml               Automated multi-platform CI/CD (macOS & Windows releases)
```

---

## 📄 License & Community

- **License**: Distributed under the [MIT License](LICENSE).
- **Author & Maintainer**: [Digimo2020](https://github.com/Digimo2020)
- **Repository**: [https://github.com/Digimo2020/Voxel---V.002](https://github.com/Digimo2020/Voxel---V.002)
