<!-- README.md (v1.2) - [2026-10-31] -->
# Voxel — Text to Speech, Anywhere

<p align="center">
  <img src="assets/banner.png" alt="Voxel Banner" width="100%">
</p>

<p align="center">
  <a href="https://github.com/Digimo2020/Voxel-/releases"><img src="https://img.shields.io/badge/Version-v1.1.12-0084FF?style=for-the-badge&logo=apple" alt="Version v1.1.12"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-6366F1?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://github.com/Digimo2020/Voxel-"><img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-00C6FF?style=for-the-badge" alt="Platform: macOS & Windows"></a>
  <a href="https://github.com/Digimo2020/Voxel-/releases/latest"><img src="https://img.shields.io/github/downloads/Digimo2020/Voxel-/total?style=for-the-badge&color=7C3AED&label=Downloads" alt="GitHub Downloads"></a>
</p>

---

## 🎙 What is Voxel?

**Voxel** is an open-source, frosted glass desktop text-to-speech utility created as an official **Digimo Product** ([digimo.pt](https://www.digimo.pt/)) for reading highlighted text aloud anywhere on **macOS** and **Windows**. 

Featuring a **voice-reactive microphone logo** with real-time waveform equalizer animations, a subtle floating selection trigger, and an animated bottom-right capsule player, Voxel blends seamlessly into your workflow across any document, web browser, PDF, or text editor.

---

## ✨ Key Features & UX Design

- 🌊 **Voice-Reactive Waveform Animation**: The 3 internal lines of the microphone capsule pulse and dance at 40 FPS like a real-time audio equalizer during playback, accented by a soft breathing radial glow.
- 🫧 **Non-Intrusive Floating Trigger**: Appears smoothly with fade-in easing near your cursor whenever you highlight text, without stealing window focus (`WA_ShowWithoutActivating`).
- 💊 **Frosted Glass Capsule Player**: Slides up above your Dock/Taskbar with smooth cubic easing. Includes a glowing electric blue-to-violet play/pause button, delicate stop button, segmented speed regulator (`[-] 1.0x [+]`), and voice switcher.
- 💿 **macOS DMG Installer**: A simple drag-and-drop disk image that places `Voxel.app` in the Applications folder.
- 👁️ **Platform-Adaptive Downloads**: Download options automatically adapt to the user's operating system, showing the relevant macOS or Windows build.
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

## 🧠 How It Works & Technologies Used (Explained Simply)

Ever wondered how Voxel seamlessly detects highlighted text in any app, animates like an equalizer, and reads it aloud with zero lag? Here is the complete breakdown in simple, clear terms:

### 1. The 4-Step Experience (How the Program Operates)

```text
 ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
 │ 1. You Select   │ ────> │ 2. Floating     │ ────> │ 3. Instant      │ ────> │ 4. Animated     │
 │    Any Text     │       │    Trigger      │       │    Speech       │       │    Capsule      │
 │ (Word, Web, PDF)│       │ (Fade-in Badge) │       │ (Neural Voices) │       │ (Equalizer Mic) │
 └─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

1. **Selection Detection (`pynput`)**:
   - Voxel runs a lightweight background daemon that monitors mouse release events and keyboard shortcuts.
   - When you finish dragging your mouse over text in any application (Chrome, Safari, Word, Slack, VS Code, or a PDF reader), Voxel checks whether text was highlighted.
   - **Clipboard Safety**: To read the text, Voxel safely copies it using a temporary bridge, reads the text, and **immediately restores your original clipboard**. Any image, password, or file you previously had copied stays 100% intact!

2. **Floating Vector Trigger (`PyQt6` + `WA_ShowWithoutActivating`)**:
   - Once text is detected, a subtle circular frosted-glass badge hosting the Voxel logo smoothly fades in near your mouse cursor.
   - Using native macOS/Windows window manager flags (`Qt.WindowType.ToolTip` and `WA_ShowWithoutActivating`), the bubble **never steals focus or interrupts your typing cursor**.

3. **Neural Speech Synthesis (`edge-tts` + Offline Fallback)**:
   - Clicking the logo sends the text to the speech engine.
   - By default, Voxel streams crystal-clear Microsoft Edge Neural AI voices (Jenny, Guy, Sonia, Aria).
   - **Offline Resilience**: If you are on an airplane or disconnected from Wi-Fi, Voxel automatically falls back to native offline operating system speech synthesis without crashing or throwing an error!

4. **Frosted Glass Capsule Player (`voxel_logo_widget.py` + `QtMultimedia`)**:
   - The capsule mini-player slides up smoothly in the bottom-right corner with cubic easing.
   - **Voice-Reactive Animated Mic**: While speaking, an internal 40 FPS timer drives the **3 horizontal equalizer lines** inside the microphone. They pulse, expand, and contract dynamically to simulate audio waveforms, surrounded by a soft breathing radial aura.
   - On completion or pressing Stop, the waveform gently settles back to resting position.

---

### 2. Technology Stack Breakdown

| Layer | Technology | Why We Chose It |
| :--- | :--- | :--- |
| **GUI Framework** | **PyQt6 (Qt 6.7+)** | Native hardware-accelerated rendering, buttery smooth 60 FPS CSS animations, native translucency, and seamless cross-platform styling. |
| **Vector Graphics** | **`QPainter` Canvas** | All logos, microphone capsules, sound waves, and player controls are pure mathematical vector paths. They remain pixel-sharp on Apple Retina 5K displays and 4K Windows monitors. |
| **Audio Playback** | **`PyQt6.QtMultimedia`** | Uses system CoreAudio on macOS and DirectSound/WASAPI on Windows. Zero external C-library dependencies (no SDL/pygame compilation issues on new Python releases). |
| **Neural TTS** | **Microsoft Edge-TTS** | Free, high-fidelity neural text-to-speech with natural intonation, dynamic speed pacing (0.5x to 2.0x), and zero API keys required. |
| **Offline TTS** | **macOS `/usr/bin/say` / Windows SAPI5** | Instant offline fallback guaranteeing speech even without an internet connection. |
| **Input Hooks** | **`pynput`** | Low-latency global mouse and keyboard listener thread utilizing macOS CoreGraphics Accessibility and Windows Win32 hooks. |
| **Clipboard Bridge** | **`pyperclip`** | Non-destructive clipboard capture and automatic state restoration. |
| **Packaging** | **PyInstaller + macOS Native Tools** | Bundles Python code, Qt runtime, and assets into standalone native binaries without requiring users to install Python. |

---

### 3. macOS vs. Windows Architecture Comparison

| Component |  macOS Implementation | ⊞ Windows Implementation |
| :--- | :--- | :--- |
| **Application Windowing** | Frameless borderless window with `NSWindow` shadow and Cocoa layer | Frameless window with Acrylic / DWM blurred border |
| **Input Hook Backend** | macOS Quartz CoreGraphics Event Tap (requires Accessibility permission) | Win32 Low-Level Mouse & Keyboard Hooks (`SetWindowsHookEx`) |
| **Audio Driver** | Native Apple CoreAudio via QtMultimedia | WASAPI / DirectSound via QtMultimedia |
| **Offline Speech Engine** | `/usr/bin/say` with built-in voice selection (`Samantha`, `Alex`) | Windows SAPI5 (`win32com.client` / `pyttsx3`) |
| **Settings Storage** | `~/Library/Application Support/Voxel/settings.json` | `%LOCALAPPDATA%\Voxel\settings.json` |
| **Global Activation Key** | `Cmd + Option + S` | `Ctrl + Alt + S` |
| **Menu / Tray Item** | macOS Menu Bar (Status Bar) with Quick Read | Windows Notification Area (System Tray) |
| **Installer Formats** | **`.dmg`** (Drag-and-Drop) | **`.exe`** (Single-file Portable) |

---

### 4. macOS Installation

Voxel for macOS is distributed as a **`.dmg` disk image**:

1. Open the downloaded `Voxel.dmg` file.
2. Drag `Voxel.app` onto the **Applications** shortcut.
3. Eject the Voxel disk image.
4. Open Voxel from your Applications folder.

The current release is not signed with an Apple Developer ID certificate or notarised by Apple. macOS may therefore ask you to approve Voxel before its first launch. See the macOS download instructions below.


---

## 🚀 Quick Download & Installation

### ⊞ For Windows Users

| Package Format | Version | Description | Target | Direct Download |
| :--- | :---: | :--- | :---: | :---: |
| **Voxel Windows Standalone** | **`v1.1.12`** *(Latest)* | Zero-dependency standalone portable executable with dedicated circular purple system tray logo | Windows 10 / 11 | [**📥 Download Voxel-v1.1.12.exe**](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.12/Voxel-v1.1.12.exe) *(Recommended)* |
| **Voxel Windows (Latest Alias)** | `latest` | Automatically resolves to newest release | Windows 10 / 11 | [📥 Download Voxel.exe](https://github.com/Digimo2020/Voxel-/releases/latest/download/Voxel.exe) |

> [!IMPORTANT]
> **First launch on Windows (Microsoft Defender SmartScreen / Smart App Control)**
>
> Because Voxel is a freshly released open-source project without an enterprise EV code-signing certificate ($300+/year), Microsoft Defender SmartScreen may display: **“Windows protected your PC: Microsoft Defender SmartScreen prevented an unrecognized app from starting”**.
>
> This is standard security behavior on Windows for new downloads and does not indicate malware.
>
> **How to open in 2 clicks:**
> 1. On the blue SmartScreen popup, click **More info**.
> 2. Click **Run anyway**.
>
> *Alternatively (Unblock via File Properties):* Right-click `Voxel-v1.1.08.exe` → select **Properties** → at the bottom of the General tab, check **☑ Unblock** → click **Apply** / **OK**.
>
> *Or 1-Click Automated Setup:* Run [`install.bat`](file:///c:/Users/ksfah/Downloads/git/voxel/install.bat) which unblocks the binary, installs Voxel to `%LOCALAPPDATA%\Programs\Voxel`, and creates Start Menu and Desktop shortcuts.

#### Run from Source (Windows)
```powershell
git clone https://github.com/Digimo2020/Voxel-.git
cd Voxel-
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
*(Or double-click `run.bat`).*

---

###  For macOS Users

| Package Format | Version | Description | Target | Direct Download |
| :--- | :---: | :--- | :---: | :---: |
| **Voxel macOS Disk Image (.dmg)** | **`v1.1.07`** *(Latest)* | Drag-and-drop application installer | macOS / Applications | [**📥 Download Voxel-v1.1.07.dmg**](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.07/Voxel-v1.1.07.dmg) |
| **Voxel DMG (Latest Alias)** | `latest` | Automatically resolves to the newest macOS disk image | macOS / Applications | [📥 Download Voxel.dmg](https://github.com/Digimo2020/Voxel-/releases/latest/download/Voxel.dmg) |

> [!IMPORTANT]
> **First launch on macOS**
>
> This build is not signed with an Apple Developer ID certificate and has not been notarised by Apple. macOS may show **“Apple could not verify ‘Voxel’ is free of malware”**. This warning does not mean Apple detected malware; it means the app has not completed Apple's trusted-developer and notarisation checks.
>
> Only continue when the DMG came from the official [Digimo Voxel GitHub Releases](https://github.com/Digimo2020/Voxel-/releases) page and you trust the download.
>
> 1. Move `Voxel.app` into **Applications** and try to open it once.
> 2. Open **System Settings → Privacy & Security**.
> 3. Find the Voxel message and select **Open Anyway**.
> 4. Confirm **Open** when macOS asks again.
>
> This approval is a per-app exception. Do not disable Gatekeeper globally or run scripts that remove quarantine attributes. If macOS reports that the app is damaged or its contents have changed, stop and download a fresh copy.


#### Run from Source (macOS)
```bash
git clone https://github.com/Digimo2020/Voxel-.git
cd Voxel-
chmod +x run.sh
./run.sh
```

---

## 📦 Releases & Version Archive (Historical Builds)

All past and current versions are preserved below for historical reference and instant download:

| Release Tag | Status | Windows Executable (.exe) | macOS Package (.pkg) | macOS Disk Image (.dmg) | Key Changes & Highlights |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **`v1.1.12`** | 🟢 **Latest** | [**📥 Voxel-v1.1.12.exe**](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.12/Voxel-v1.1.12.exe) | — | [**📥 Voxel-v1.1.12.dmg**](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.12/Voxel-v1.1.12.dmg) | • Dedicated Circular System Tray Logo: Exclusively updated tray/startup bar icon to official purple badge with 4x supersampled antialiasing<br>• Kept main app icon untouched for upcoming dedicated app logo |
| **`v1.1.10`** | 📦 Archived | [📥 Voxel-v1.1.10.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.10/Voxel-v1.1.10.exe) | — | [📥 Voxel-v1.1.10.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.10/Voxel-v1.1.10.dmg) | • Startup Bar & System Tray Logo Update: Integrated official purple-to-blue badge and bold white microphone (`assets/Fainal/Voxel Logo.png`)<br>• Alpha-antialiased contours with transparent background for dark and light taskbars<br>• Regenerated Windows `icon.ico` and HiDPI PNGs |
| **`v1.1.09`** | 📦 Archived | [📥 Voxel-v1.1.09.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.09/Voxel-v1.1.09.exe) | — | [📥 Voxel-v1.1.09.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.09/Voxel-v1.1.09.dmg) | • UI/UX Overhaul: Reduced tabs to 2 clean sections (Preferences & About)<br>• Fixed LinkedIn connection button and full link visibility<br>• Widened, simplified right-click tray context menu (Preferences, About, Quit)<br>• Eliminated underscores and organized typography |
| **`v1.1.08`** | 📦 Archived | [📥 Voxel-v1.1.08.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.08/Voxel-v1.1.08.exe) | — | [📥 Voxel-v1.1.08.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.08/Voxel-v1.1.08.dmg) | • Flameshot & Lightshot compatibility: Added screenshot overlay process detection to prevent drag-to-copy interference<br>• Solid porcelain light capsule styling: Eliminated white square clipping artifacts behind player on close<br>• Window hierarchy: Replaced SubWindow with Tool + WA_ShowWithoutActivating |
| **`v1.1.07`** | 📦 Archived | [📥 Voxel-v1.1.07.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.07/Voxel-v1.1.07.exe) | — | [📥 Voxel-v1.1.07.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.07/Voxel-v1.1.07.dmg) | • macOS DMG-only distribution; removed the quarantine-removal helper; added first-launch Gatekeeper guidance and SHA-256 checksums |
| **`v1.1.06`** | 📦 Archived | [**📥 Voxel-v1.1.06.exe**](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.06/Voxel-v1.1.06.exe) | [**📥 Voxel-v1.1.06.pkg**](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.06/Voxel-v1.1.06.pkg) | [**📥 Voxel-v1.1.06.dmg**](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.06/Voxel-v1.1.06.dmg) | • Fixed full-document reader for Google Docs & PDFs (active window focus restoration & 1400ms canvas timing)<br>• Light & Dark theme modes for floating selection bubble (Light Frosted Glass default)<br>• System tray startup bar icon double-click activation<br>• Reorganized Settings: Added Appearance & Theme tab, audio spectrum Equalizer, and fixed LinkedIn link |
| **`v1.1.05`** | 📦 Archived | [📥 Voxel-v1.1.05.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.05/Voxel-v1.1.05.exe) | [📥 Voxel-v1.1.05.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.05/Voxel-v1.1.05.pkg) | [📥 Voxel-v1.1.05.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.05/Voxel-v1.1.05.dmg) | • Fixed Document Reader: Canvas-aware timing for Google Docs & seamless fallback<br>• Dual Light/Dark Settings views with 1-click theme switcher<br>• Live Voice & Latency Performance Test button in Settings<br>• Creator & Architecture credits (Fahim - [LinkedIn](https://www.linkedin.com/in/fahimdigital/)) |
| **`v1.1.04`** | 📦 Archived | [📥 Voxel-v1.1.04.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.04/Voxel-v1.1.04.exe) | [📥 Voxel-v1.1.04.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.04/Voxel-v1.1.04.pkg) | [📥 Voxel-v1.1.04.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.04/Voxel-v1.1.04.dmg) | • Smart Document & Presentation Reader (Google Docs, Word, PDFs, Slides)<br>• Expressive Copilot Neural Voices (Ava, Andrew, Emma, Brian) & 4 Emotion Modes<br>• Sub-second instant playback pipeline (<300ms start) & hover pre-buffering<br>• Left-click startup tray icon opens Settings immediately |
| **`v1.1.03`** | 📦 Archived | [📥 Voxel-v1.1.03.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.03/Voxel-v1.1.03.exe) | [📥 Voxel-v1.1.03.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.03/Voxel-v1.1.03.pkg) | [📥 Voxel-v1.1.03.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.03/Voxel-v1.1.03.dmg) | • Integrated vibrant blue/purple full-frame logo into startup system tray bar<br>• Maximized icon to 100% full-frame squircle with 91% height white microphone for maximum size and prominence<br>• Full preservation of historical version binaries |
| **`v1.1.02`** | 📦 Archived | [📥 Voxel-v1.1.02.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.02/Voxel-v1.1.02.exe) | [📥 Voxel-v1.1.02.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.02/Voxel-v1.1.02.pkg) | [📥 Voxel-v1.1.02.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.02/Voxel-v1.1.02.dmg) | • Maximized Standalone System Tray Microphone Icon to fill 93% vertical height and 79% width<br>• Removed low-contrast outer padding and grey container to match visual weight of PowerToys and Windows Voice mic<br>• Preserved historical version binaries |
| **`v1.1.01`** | 📦 Archived | [📥 Voxel-v1.1.01.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.01/Voxel-v1.1.01.exe) | [📥 Voxel-v1.1.01.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.01/Voxel-v1.1.01.pkg) | [📥 Voxel-v1.1.01.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.01/Voxel-v1.1.01.dmg) | • Replaced SVG rendering with crisp high-definition transparent PNGs across all 3 visual surfaces<br>• Dedicated Startup Bar & System Tray icon (`tray_bar_logo_square.png`)<br>• Main app icon & regenerated multi-res `assets/icon.ico` (`app_logo_square.png`)<br>• Dedicated floating selection bubble trigger logo with hover aura (`selection_bubble_logo_square.png`)<br>• Full preservation of historical version binaries |
| **`v1.1.00`** | 📦 Archived | [📥 Voxel-v1.1.00.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.00/Voxel-v1.1.00.exe) | [📥 Voxel-v1.1.00.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.00/Voxel-v1.1.00.pkg) | [📥 Voxel-v1.1.00.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.1.00/Voxel-v1.1.00.dmg) | • Integrated official vector SVG logo from `assets/branding/svg/fiNAL/` directly into the system tray and taskbar startup bar<br>• Regenerated multi-resolution `icon.ico` (16–256px) for Windows taskbar and file icon<br>• Bundled assets into PyInstaller standalone executable<br>• Preserved historical version archive policy (`VERSIONING_RULES.md`) |
| **`v1.0.09`** | 📦 Archived | [📥 Voxel-v1.0.09.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.09/Voxel-v1.0.09.exe) | [📥 Voxel-v1.0.09.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.09/Voxel-v1.0.09.pkg) | [📥 Voxel-v1.0.09.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.09/Voxel-v1.0.09.dmg) | • Excluded unused `QtMultimedia`, `windowsmediaplugin.dll`, and `ffmpegmediaplugin.dll` from Windows executable<br>• Fully resolves Windows 11 Smart App Control (SAC) *"Part of this app has been blocked"* alert<br>• Zero-dependency native Windows MCI (`winmm.dll`) audio playback |
| **`v1.0.08`** | 📦 Archived | [📥 Voxel-v1.0.08.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.08/Voxel-v1.0.08.exe) | [📥 Voxel-v1.0.08.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.08/Voxel-v1.0.08.pkg) | [📥 Voxel-v1.0.08.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.08/Voxel-v1.0.08.dmg) | • Automatic Windows native MCI audio engine fallback<br>• Thread-safe queued audio playback dispatch<br>• Universal Python 3.14+ launcher and PyInstaller builder |
| **`v1.0.07`** | 📦 Archived | [📥 Voxel-v1.0.07.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.07/Voxel-v1.0.07.exe) | [📥 Voxel-v1.0.07.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.07/Voxel-v1.0.07.pkg) | [📥 Voxel-v1.0.07.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.07/Voxel-v1.0.07.dmg) | • Fixed macOS `QPaintDevice::devicePixelRatio` crash in `QBackingStore::flush`<br>• Fixed missing `QLinearGradient` and exception safety in floating trigger `paintEvent`<br>• Switched MiniPlayer window flags from invalid `SubWindow` to `Tool`<br>• Thread-safe collision geometry caching (eliminates cross-thread QWidget access)<br>• Automated ad-hoc codesigning verification and gatekeeper bypass helper |
| **`v1.0.06`** | 📦 Archived | [📥 Voxel-v1.0.06.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.06/Voxel-v1.0.06.exe) | [📥 Voxel-v1.0.06.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.06/Voxel-v1.0.06.pkg) | [📥 Voxel-v1.0.06.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.06/Voxel-v1.0.06.dmg) | • Light frosted glass round tray icon (larger & high contrast for light taskbars)<br>• Single-instance process lock (prevents duplicate tray icons)<br>• Embedded Windows .ico application icon<br>• Preserved historical release archive |
| **`v1.0.05`** | 📦 Archived | [📥 Voxel-v1.0.05.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.05/Voxel-v1.0.05.exe) | [📥 Voxel-v1.0.05.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.05/Voxel-v1.0.05.pkg) | [📥 Voxel-v1.0.05.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.05/Voxel-v1.0.05.dmg) | • Large round glass tray icon maximized for taskbar legibility<br>• Multi-resolution HiDPI icons (16–256px) for Windows & macOS<br>• Embedded Windows .ico application icon |
| **`v1.0.04`** | 📦 Archived | [📥 Voxel-v1.0.04.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.04/Voxel-v1.0.04.exe) | [📥 Voxel-v1.0.04.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.04/Voxel-v1.0.04.pkg) | [📥 Voxel-v1.0.04.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.04/Voxel-v1.0.04.dmg) | • Bluish frosted glass floating selection trigger with glossy top sheen<br>• Luminous glass specular dome reflection on Voxel mic logo<br>• Digimo product attribution ([digimo.pt](https://www.digimo.pt/))<br>• 100% Free & Open Source statement & disclaimer |
| **`v1.0.03`** | 📦 Archived | [📥 Voxel-v1.0.03.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.03/Voxel-v1.0.03.exe) | [📥 Voxel-v1.0.03.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.03/Voxel-v1.0.03.pkg) | [📥 Voxel-v1.0.03.dmg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.03/Voxel-v1.0.03.dmg) | • Redesigned ultra-compact frosted acrylic glass player (310×48 capsule)<br>• Combined Play/Pause toggle (`▶` / `⏸`) with cyan glowing aura<br>• Clickable speed dropdown pill (`1.0x ▾`)<br>• Smooth 280ms fade-in and 1.0s auto-close fade-out |
| **`v1.0.02`** | 📦 Archived | [📥 Voxel-v1.0.02.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.02/Voxel-v1.0.02.exe) | [📥 Voxel-v1.0.02.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.02/Voxel.pkg) | *(Bundled in .pkg)* | • Rebranded application from Text 2 Voice to **Voxel**<br>• Introduced Dark Obsidian Glass theme with high-contrast text<br>• Added macOS `.pkg` wizard with embedded UX previews<br>• Fixed VOXEL vector logo geometry width |
| **`v1.0.01`** | 📦 Archived | [📥 Text2Voice-v1.0.01.exe](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.01/Text2Voice-v1.0.01.exe) | [📥 Text2Voice-v1.0.01.pkg](https://github.com/Digimo2020/Voxel-/releases/download/v1.0.01/Text2Voice.pkg) | *(Bundled in .pkg)* | • Initial release of Text 2 Voice desktop application<br>• Microsoft Edge-TTS neural voice streaming with offline fallback<br>• Floating trigger badge and animated mic equalizer |

> 🔗 *To download release source code or view automated CI builds, visit the [GitHub Releases Directory](https://github.com/Digimo2020/Voxel-/releases).*

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

### Building on macOS (`.app` & `.dmg`)
```bash
chmod +x build_mac.sh
./build_mac.sh
```
Outputs:
- **`dist/Voxel.app`**: Native standalone application bundle.
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
build_mac.sh                 Compiles Voxel.app and Voxel.dmg
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

## 🏢 About Digimo & Open Source Freedom

**Voxel** is proud to be an open-source product created and published by **[Digimo](https://www.digimo.pt/)**.

- 🌐 **Official Website**: [https://www.digimo.pt/](https://www.digimo.pt/)
- 🔓 **100% Free & Open Source**: Voxel is released completely free with no copyright restrictions. Anyone is welcome to experiment, modernize, fork, or build upon it.
- 💻 **100% Local Machine Processing**: Operates entirely on your local machine. No telemetry, no background analytics, and your clipboard text is never stored or transmitted to external servers.

---

## ⚖️ Disclaimer & Setup Guide

> **Disclaimer**: This software is provided "as is" for personal and experimental use. The creators and Digimo assume no responsibility or liability for any use, loss, or consequences arising from running this program.
>
> Please read the documentation and [Setup Guides](#-quick-download--installation) carefully before setting up and running Voxel on your system.

---

## 📄 License & Community

- **License**: Distributed under the [MIT License](LICENSE) (Free and Open Source).
- **Organization & Brand**: [Digimo](https://www.digimo.pt/) ([@Digimo2020](https://github.com/Digimo2020))
- **Repository**: [https://github.com/Digimo2020/Voxel-](https://github.com/Digimo2020/Voxel-)
