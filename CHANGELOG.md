# Changelog

All notable changes to the **Text 2 Voice** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

Versioning structure: `v<Major>.<Minor>.<Patch:02d>` (e.g. `v1.0.01`).
Every 10th patch increments minor, and every 10th minor increments major.

---

## [v1.0.01] - 2026-10-28

### Added
- **Settings & About Dialog** (`src/ui/settings_dialog.py`):
  - Accessible via the player gear button (⚙️) or taskbar tray icon.
  - Preference controls for default voice, default speed, docking position, and bubble trigger timeout.
  - About view displaying current version (`v1.0.01`), versioning schema explanation, and a direct link to the [GitHub Repository](https://github.com/Digimo2020/Voxel-).
- **Persistent Settings Manager** (`src/utils/settings.py`):
  - Stores and loads preferences from `%LOCALAPPDATA%/Text2Voice/settings.json`.
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
