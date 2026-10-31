<!-- CHANGELOG.md (v1.1) - [2026-10-31] -->
# Changelog

All notable changes to the **Voxel** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

Versioning structure: `v<Major>.<Minor>.<Patch:02d>` (e.g. `v1.0.01`).
Every 10th patch increments minor, and every 10th minor increments major.

---

## [v1.1.10] - 2026-10-31

### Branding & Startup Bar Logo Update
- **Updated Official Startup Bar Logo**:
  - Replaced system tray and notification area icon with the user's new vibrant purple-to-blue badge and bold white microphone icon (`assets/Fainal/Voxel Logo.png`).
  - Extracted clean, alpha-antialiased contours with transparent background so the badge renders crisply on both light and dark Windows/macOS taskbars without white halo artifacts.
  - Centered onto 512x512 master assets (`tray_bar_logo_square.png` and `tray_bar_logo.png`) and regenerated multi-resolution Windows `icon.ico` (16, 24, 32, 48, 64, 128, 256 px).

---

## [v1.1.09] - 2026-10-31

### UI/UX Overhaul & Menu Simplification
- **Streamlined 2-Tab Preferences Dialog**:
  - Eliminated redundant tabs down to two clear, focused sections: **Preferences** and **About**.
  - Merged voice settings, audio spectrum equalizer preview, system/startup options, and appearance controls cleanly.
  - Removed all accidental underscores from UI text labels, headings, and buttons (e.g. `Save Changes` instead of `Save_Apply`).
- **Refined About Us Section & Verified Social Links**:
  - Fixed LinkedIn button text truncation and missing 'C' (`🔗 Connect on LinkedIn`).
  - Added clean, full-width action links for **LinkedIn**, **Digimo**, and **GitHub Repository**.
  - Prominent version badge `v1.1.09` with clean open-source freedom and disclaimer cards.
- **Wider, Focused Right-Click System Tray Menu**:
  - Simplified context menu down to essential actions: Header title with version, **Preferences...**, **About Voxel...**, and **Quit Voxel**.
  - Expanded menu width (min-width: 220px) with elegant dark acrylic styling, generous padding, and clean hover highlights.
  - Removed noisy submenus (Voices, History, Download buttons) to keep right-click interaction fast and modern.

---

## [v1.1.08] - 2026-10-31

### Fixed & Enhanced
- **Flameshot & Lightshot Screenshot Compatibility**:
  - Added real-time screenshot app detection guard (`_is_screenshot_app_active`) covering Flameshot, Lightshot, Snipping Tool, Snipaste, ShareX, and Greenshot.
  - Prevents Voxel's mouse selection listener from injecting simulated `Ctrl+C` copy events and clipboard locks into screenshot drawing overlays, allowing screenshot tools and their annotation menus to work 100% normally.
- **Solid Porcelain Light Capsule (No White Background Artifacts)**:
  - Replaced translucent milky gradients with solid high-definition porcelain acrylic fill (`#FFFFFF` to `#EEF3FC`) with crisp slate borders.
  - Eliminated the white ghost box artifact and white rectangular clipping behind the floating player capsule when closing or hovering.
- **Window Hierarchy & Focus Fix**:
  - Changed MiniPlayer window flag from `SubWindow` to `Tool` with `WA_ShowWithoutActivating` so it never captures desktop focus or shows solid window frame boxes.

---

## [v1.1.07] - 2026-10-31

### Distribution & Packaging
- Switched macOS distribution to a drag-and-drop `.dmg` only; new releases no longer generate or publish `.pkg` installers.
- Removed the bundled shell helper that recursively cleared macOS quarantine attributes.
- Added first-launch instructions inside the DMG and in the README, using macOS Privacy & Security approval rather than disabling Gatekeeper.
- Added SHA-256 checksums for the versioned and latest DMG files.
- **Signing status:** this build is not signed with an Apple Developer ID certificate and is not notarised. macOS may still show a first-launch security warning; this packaging update does not remove that warning.

---

## [v1.1.06] - 2026-10-30

### Fixed & Enhanced
- **Full Document Capture Reliability (Google Docs & PDFs)**:
  - Fixed issue where clicking the document icon mistakenly read only the selected word.
  - Implemented automatic target window focus restoration before simulating capture keystrokes.
  - Extended canvas processing timing to 1400ms for heavy Google Docs and eliminated premature fallback to single words.
- **Instant Audio Playback & Latency Optimization**:
  - Eliminated playback lag and manual play button stalls.
  - Pre-buffers first sentence in background with zero-delay dispatch to Windows MCI.
- **Light & Dark Mode for Floating Selection Bubble**:
  - Implemented crisp Light Frosted Glass as the default bubble mode with high-contrast icons.
  - Full theme switching synchronized with Settings dialog.
- **Tray Icon Activation**:
  - Changed system tray startup bar icon from single-click to **Double-Click** to open Settings, preventing accidental popups.
- **Settings Redesign**:
  - Replaced Downloads tab with a clean **Appearance & Theme** tab featuring one-click Light/Dark toggles.
  - Added real-time voice-reactive animated spectrum **Equalizer** in the Performance Test section.
  - Fixed typo in LinkedIn link button to read *"Connect with Fahim on LinkedIn"*.
  - Kept historical versions preserved and produced `Voxel-v1.1.06.exe`.

---

## [v1.1.05] - 2026-10-30

### Fixed & Enhanced
- **Rock-Solid Document Reader Capture & Seamless Fallback**:
  - Resolved Google Docs canvas and physical mouse-down contention by introducing decoupled asynchronous execution (120ms pause to release mouse and re-focus target window).
  - Implemented native Windows `keybd_event` with Canvas-aware delays (120ms between `Ctrl+A` and `Ctrl+C`) for Google Docs HTML5 canvas and web PDF viewers.
  - Added smart fallback: if an application blocks whole-document select-all, Voxel automatically falls back to your highlighted text with zero error notifications.
- **Dual Theme Views for Settings Window (Light & Dark)**:
  - Added full support for **Light Frosted Acrylic** and **Dark Obsidian Glass** views in the Settings dialog.
  - Quick 1-click toggle switch in the header (`☀️ Light Mode` / `🌙 Dark Mode`) with real-time UI re-theming.
- **Performance & Voice Live Test Button**:
  - Added **`▶ Test Voice & Latency Performance`** directly in the Settings Preferences tab.
  - Lets users instantly audition speech synthesis, latency, speed, and emotion tone before saving.
- **Creator, Architecture & Design Concept Attribution**:
  - Formally credited **Fahim** for system architecture, UX/UI design concept, and product vision.
  - Embedded direct LinkedIn profile link: [https://www.linkedin.com/in/fahimdigital/](https://www.linkedin.com/in/fahimdigital/).

---

## [v1.1.04] - 2026-10-30

### Added & Enhanced
- **Smart Document & Presentation Reader (Google Docs / PDF / Slides / Word)**:
  - Added dedicated **📑 Read Entire Document** action on the floating trigger badge, player capsule bar, tray menu, and global hotkey (`Ctrl+Alt+D` on Windows / `Cmd+Alt+D` on macOS).
  - Automatically captures the full document or slide presentation from the active window and starts narration immediately without manual copying.
  - Added direct local file reader supporting `.pdf` (via `pypdf`), `.docx`, `.txt`, `.md`, and `.rtf`.
- **Expressive Emotion & Neural Copilot Voices**:
  - Integrated 4 new expressive Copilot neural voices: `Ava (Expressive Female)`, `Andrew (Warm Male)`, `Emma (Cheerful Female)`, and `Brian (Conversational Male)`.
  - Added 4 Emotion & Prosody Tone Modes: *Expressive & Empathetic*, *Warm & Storyteller*, *Cheerful & Dynamic (for Presentations)*, and *Calm & Professional*.
  - Intelligent prosody processor cleans URLs, bullet lists, and punctuation for natural human breathing pauses.
- **Sub-Second Instant Playback & Zero-Delay Pipeline**:
  - Sentence-pipelined streaming: starts speaking Chunk 0 in **< 300ms** while subsequent chunks synthesize continuously in the background for gapless long-document playback.
  - Pre-buffering on trigger hover: pre-synthesizes the first sentence while mouse moves toward the badge (0ms start latency on click).
  - Local disk audio cache prevents re-generating identical phrases or repeated slides.
- **Left-Click Startup Tray Icon**:
  - Left-clicking the startup system tray icon now immediately opens the Settings & Preferences dialog.
- **Redesigned Settings & Preferences Dialog**:
  - Added **Launch at System Startup** toggle with automatic Windows Registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` integration.
  - High-contrast obsidian glass card aesthetic, tab navigation, and direct button to open the local `dist/` folder on computer.
- **Dual-Action Floating Trigger Capsule**:
  - Expanded floating trigger badge with dual actions: Left icon (▶ Read Selected Text) and Right icon (📑 Read Entire Document).

---

## [v1.1.03] - 2026-10-30

### Fixed & Enhanced
- **Vibrant Full-Frame Startup Bar & System Tray Logo**:
  - Replaced tray icon with user's official full-color electric blue/purple gradient badge and bold white microphone (`media_1793317370100_47d426df.png`).
  - Maximized the icon to fill **100% of the tray canvas edge-to-edge** in a smooth Windows 11 Fluent squircle frame.
  - White microphone enlarged to fill **90.6% of vertical height** and **78.1% of width** for maximum visibility and size in the startup/notification area.
  - Preserved all prior versions (`v1.0.06` through `v1.1.02`) and produced new standalone executable `Voxel-v1.1.03.exe`.

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
