# Changelog

All notable changes to the **Voxel** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

Versioning structure: `v<Major>.<Minor>.<Patch:02d>` (e.g. `v1.0.01`).
Every 10th patch increments minor, and every 10th minor increments major.

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
