# Changelog

All notable changes to the **Voxel** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

Versioning structure: `v<Major>.<Minor>.<Patch:02d>` (e.g. `v1.0.01`).
Every 10th patch increments minor, and every 10th minor increments major.

---

## [v1.1.02] - 2026-10-30

### Fixed & Enhanced
- **Maximized Standalone System Tray Microphone Icon**:
  - Removed low-contrast outer container padding and light grey pill background that blended into the Windows taskbar.
  - Re-rendered vector microphone paths directly to fill 93% vertical height and 79% width of the tray canvas with crisp transparent background.
  - Sized and weighted to match the visual prominence of standard Windows notification tray icons (PowerToys, Windows Voice Mic, Index).
  - Preserved all prior version binaries (`v1.0.06` through `v1.1.01`) and produced new `Voxel-v1.1.02.exe`.

---

## [v1.1.01] - 2026-10-29

### Added & Enhanced
- **High-Definition PNG Branding Integration Across 3 Surfaces**:
  - Replaced SVG rendering with high-resolution 32-bit transparent PNG assets formatted with clean square aspect-ratios to ensure crisp, un-distorted presentation:
    - **Startup / System Tray Logo**: `assets/branding/png/tray_bar_logo_square.png` rendered at crisp DPI-aware icon sizes for the Windows notification area / taskbar tray.
    - **Main Application Logo & Window Icon**: `assets/branding/png/app_logo_square.png` applied to all application windows, taskbar groupings, and converted into multi-resolution `assets/icon.ico` (16, 24, 32, 48, 64, 128, 256 px).
    - **Text Selection Bubble Trigger**: `assets/branding/png/selection_bubble_logo_square.png` rendered inside `src/ui/floating_bubble.py` with smooth hover glow effects whenever text is selected on screen.
  - Preserved previous standalone builds (`Voxel-v1.0.06.exe` through `Voxel-v1.1.00.exe`) and produced new `Voxel-v1.1.01.exe`.

---

## [v1.1.00] - 2026-10-29

### Added & Enhanced
- **Official Vector SVG Startup Bar & System Tray Logo**:
  - Integrated the official vector logo from `assets/branding/svg/fiNAL/Voxel Logo.svg`.
  - Replaced procedural icon generation in `assets/icons.py` with direct `QSvgRenderer` vector rendering across all resolutions (16px, 20px, 24px, 32px, 48px, 64px, 128px, 256px).
  - Regenerated `assets/icon.ico` with full multi-size Windows icon layers matching the official logo.
  - Bundled asset paths in PyInstaller standalone packages (`--add-data "assets;assets"`).

---

## [v1.0.09] - 2026-10-29

### Fixed
- **Windows Smart App Control (SAC) "Part of this app has been blocked" Resolution**:
  - Excluded unused `PyQt6.QtMultimedia`, `windowsmediaplugin.dll`, and `ffmpegmediaplugin.dll` from the PyInstaller standalone build.
  - Microsoft Smart App Control in Windows 11 previously flagged unsigned `ffmpegmediaplugin.dll` unpacked to `%TEMP%`.
  - Switched Windows audio exclusively to native Windows Media Control Interface (`winmm.dll`), which is fully recognized and trusted by Windows Security.
  - Reduced executable footprint and improved startup launch time.

---

## [v1.0.08] - 2026-10-29

### Fixed & Enhanced
- **Windows Application Control / AppLocker Crash Resolution**:
  - Implemented automatic native Windows Media Control Interface (`winmm.dll`) audio playback engine in `src/tts_engine.py`.
  - Bypasses DLL blockage of `Qt6Multimedia.dll` by Windows AppLocker and WDAC security policies.
- **Thread-Safe Audio Playback Dispatch**:
  - Replaced direct background thread GUI calls with Qt Queued Connections (`_request_play` signal) to prevent UI thread lockups and race conditions.
- **Universal Batch Launchers & PyInstaller**:
  - Upgraded `run.bat` to detect and run Python from system PATH and modern Python 3.14+ installations automatically.
  - Enhanced `build_windows.bat` and `build_exe.bat` to build standalone versioned executable `Voxel-v1.0.08.exe` alongside `Voxel.exe`.
- **Global Deployment & Versioning Standards**:
  - Created `VERSIONING_RULES.md` and added strict version archiving preserving every previous standalone executable build.

---

## [v1.0.07] - 2026-10-29

### Fixed
- **macOS QPaintDevice & Windowing Crash Resolution**:
  - Resolved `QPaintDevice::devicePixelRatio` crash in `QBackingStore::flush`.
  - Fixed missing `QLinearGradient` and exception safety in floating trigger `paintEvent`.
  - Switched MiniPlayer window flags from invalid `SubWindow` to `Tool`.
  - Thread-safe collision geometry caching (eliminates cross-thread QWidget access).
  - Automated ad-hoc codesigning verification and gatekeeper bypass helper.

### Added
- **Streamlined Ultra-Compact Frosted Glass Player** (`src/ui/mini_player.py`):
  - Reduced capsule footprint from 480px to **310px width x 48px height** for a minimal desktop presence.
  - Authentic signature frosted glass appearance matching the reference mockup: translucent milky glass fill, luminous white specular edge crescent, and celestial blue/lavender shadow.
  - **Single Play/Pause Toggle**: Removed redundant Stop button; circular glowing gradient button smoothly toggles between Play (▶) and Pause (⏸), allowing instant replay.
  - **Clickable Speed Dropdown Pill**: Replaced plus/minus buttons with a single glass pill (`1.0x ▾`) that opens a speed preset menu.
  - **Streamlined Layout**: Removed in-player voice artist selector to keep the player focused and compact.
  - **Smooth Fade-In & Fade-Out**: Fades in with gentle slide-up on launch, and fades out smoothly over 1.0s upon speech completion.

---

## [v1.0.02] - 2026-10-29

### Added
- **Dark Glass & Frosted Glass Themes** (`src/ui/mini_player.py`, `src/ui/settings_dialog.py`):
  - Translucent Obsidian Dark Glass player with frosted edge gradient and specular glass shine.
  - User selectable "Dark Glass" vs "Frosted Glass" themes in Settings with immediate live switching.
- **Playback Auto-Close with 1-Second Fade-Out**:
  - Automatically fades out the player capsule smoothly (default 1.0s, configurable 0.5s–5.0s) when speech completes.
  - Hovering the mouse over the player pauses/cancels fadeout.
- **Windows High-Contrast Text Fix**:
  - Explicitly styled form labels and text elements in the Settings dialog to eliminate unreadable black-on-dark text on Windows.
- **Capsule Width Expansion & Logo Fix**:
  - Widened the player capsule to 480px, eliminating label truncation so "Voxel" and speed "1.0x" display cleanly without clipping.
- **Voxel.exe Standalone Binary**:
  - Renamed the output executable in `dist/` to `Voxel.exe`.

---

## [v1.0.01] - 2026-10-28

### Added
- **Settings & About Dialog** (`src/ui/settings_dialog.py`):
  - Accessible via the player gear button (⚙️) or taskbar tray icon.
  - Preference controls for default voice, default speed, docking position, and bubble trigger timeout.
  - About view displaying current version (`v1.0.01`), versioning schema explanation, and a direct link to the [GitHub Repository](https://github.com/Digimo2020/Voxel-).
- **Persistent Settings Manager** (`src/utils/settings.py`):
  - Stores and loads preferences from `%LOCALAPPDATA%/Voxel/settings.json`.
- **Version Rollover Utility** (`src/utils/version.py`):
  - Implements the base-10 rollover versioning system (`v<Major>.<Minor>.<Patch:02d>`).
- **Bottom-Right Slide-Up Animation**:
  - Mini player pill smoothly docks above the Windows taskbar with slide-up and fade-in entry/exit transitions.
- **Transparent 30px Floating Speaker Trigger**:
  - Replaced the dark background bubble with an ultra-light transparent frosted glass trigger with sky-blue vector speaker.

---

## [v1.0.00] - 2026-10-28

### Added
- Universal text selection detection across desktop apps, browsers, and Google Docs.
- Safe clipboard interception with automatic restoration of user clipboard history.
- Frosted glass floating player pill with play/pause, stop, and speed regulation (`0.5x` to `2.0x`).
- Microsoft Edge TTS neural speech synthesis with offline SAPI5 fallback.
- Persistent JSON history logging and history browser dialog.
- System tray integration and PyInstaller standalone `.exe` build pipeline.
