<!-- CHANGELOG.md (v1.3) - [2026-11-01] -->
# Changelog

All notable changes to the **Voxel** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

Versioning structure: `v<Major>.<Minor>.<Patch:02d>` (e.g. `v1.0.01`).
Every 10th patch increments minor, and every 10th minor increments major.

---

## [v1.1.22] - 2026-11-02

### Workable Bubble Sizes (Small Dot, Medium, Large) & Selection Distance Padding
- **Workable Bubble Sizing in Settings**:
  - Implemented 3 distinct, functional bubble formats:
    - **🔴 Small Dot (Mini 28px)**: Minimalist circular floating dot badge with centered Voxel logo. Unobtrusive, zero screen obstruction. Single click reads selected text; right click opens full options menu.
    - **💊 Medium Capsule (Compact 62×32px)**: Sleek streamlined dual-action capsule (Selection + Document Reader).
    - **🏷️ Large Capsule (Full 82×40px)**: Standard full-size dual-action capsule.
- **Smart Distance Padding & Clearance Offset from Selected Text**:
  - Added configurable **Distance Padding** slider (default 28px, range 15px–75px) in Settings Appearance tab.
  - Ensures the floating bubble hovers safely distanced above the selection without covering text lines or colliding with third-party software popups (e.g., Google Docs inline menus, Chrome `Quote Ctrl+L` toolbar).
- **Multi-Line Selection Paragraph Collision Prevention**:
  - Selection listener captures selection start and release coordinates.
  - For multi-line selections, places the bubble safely above the *top line* (`top_y = min(start_y, cursor_y)`) near the left margin rather than inside the middle of the selected block.

---

## [v1.1.21] - 2026-11-01

### Always-Fixed Bottom Test Voice Bar & Clean Minimalist Voice Controls
- **Always-Fixed Bottom Test Voice Bar (Voice & Speech Tab)**:
  - Docked the Test Voice control bar permanently at the bottom of the Voice & Speech tab, outside the vertical scroll area.
  - The bar remains 100% visible at all times regardless of scroll position, allowing users to instantly preview voice changes while adjusting Voice, Emotion, Pitch, Speed, or Equalizer presets without scrolling down.
- **Minimalist, Clutter-Free Controls**:
  - Removed verbose title and description headers ("nothing to put more").
  - Clean, concise button label: **`▶ Test Voice`** (toggles to **`⏹ Stop Voice`** while synthesizing/speaking).
  - Clean status indicator: displays `"⚡ Synthesizing live audio..."` during generation and clears automatically when idle/stopped.
  - Integrated the buttery-smooth 18-bar harmonic audio visualizer directly into the fixed bottom bar.
- **Themed Docked Container**:
  - Styled with `#FixedTestVoiceBar` across Light (`#FFFFFF` with `#E2E8F0` border) and Dark (`#161F30` with `rgba(255, 255, 255, 0.08)` border) themes.
  - Zero horizontal overflow guaranteed (`max=0`) across all 5 Settings tabs.

---

## [v1.1.20] - 2026-11-01

### Buttery Harmonic Voice Spectrum, Voice Tuning Controls, and External-App Floating Bubble Detection
- **Buttery-Smooth Harmonic Equalizer Animation**:
  - Replaced random jitter bars with an organic multi-harmonic vocal physics simulation (`sin`/`cos` fundamental and formant waves).
  - Upgraded animation loop to ultra-smooth 60 FPS (16ms refresh) with exponential low-pass smoothing (`0.18` decay factor) for liquid, organic motion.
  - Widened from 140px to 240px with 18 anti-aliased pill bars (6px width, 3px corner radius) featuring a vibrant gradient from Violet (`#8B5CF6`) to Cyan (`#06B6D4`).
  - Added subtle ambient breathing wave when idle so visualizer stays lively without jarring motion.
- **Dedicated Voice Tuning & Audio Controls Card (Voice & Speech Tab)**:
  - **Speaking Speed Slider**: Moved from Playback to Voice & Speech tab (`0.50x` to `2.00x`, live `1.00x` badge, scale marks).
  - **Voice Pitch Tuning Slider**: Dedicated slider from `-50Hz` (deeper voice) to `+50Hz` (higher pitch), default `0Hz`, wired directly into Edge-TTS synthesis parameters.
  - **Master Listening Volume Slider**: Continuous `0%` to `100%` listening volume slider with real-time level badge.
- **Audio & Playback Page Modernization & Renaming**:
  - Renamed tab from `"Playback"` to **`"🎛️  Audio & Playback"`** across sidebar navigation, title, and subtitle.
  - Unified fade controls into **`"Audio Transitions & Fading"`** card (smooth fade-in toggle switch + horizontal fade-out decay duration slider with scale marks).
  - Renamed behavior card to **`"Auto-Read & Trigger Behavior"`**.
  - Renamed hardware card to **`"Hardware Output & Auto-Recordings"`**.
  - Renamed permissions card to **`"macOS System Permissions"`**.
- **External Application Floating Bubble Fix (macOS Cocoa NSPanel)**:
  - Switched floating capsule window flags from `Qt.WindowType.ToolTip` (suppressed by macOS Cocoa when third-party apps like Chrome/Safari are active) to `Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint`.
  - Added `Qt.WidgetAttribute.WA_AlwaysShowToolTips` and `QGuiApplication.screenAt()` multi-monitor coordinate detection.
  - Integrated high-speed native `AppKit.NSPasteboard` change count tracking (`_MAC_PB.changeCount()`) to capture highlighted text in `< 5ms` with zero subprocess overhead.
- **macOS Gatekeeper Verification & Packaging**:
  - Complete technical explanation and documentation of the Voxel native architecture (Pure Python 3.14 + PyQt6 Native Cocoa, NOT Electron/React, compiled via PyInstaller and packaged with Apple `hdiutil`).
  - Clear user walkthrough for Gatekeeper bypass (`xattr -cr`, Control-Click -> Open, or System Settings -> "Open Anyway").

---

## [v1.1.19] - 2026-11-01

### Interactive Checkmark Indicators, Single-Row Playback Controls & Zero Horizontal Scroll
- **Crisp Vector Checkmark Indicators**:
  - Replaced solid purple blocks with anti-aliased white vector checkmark indicators (`assets/branding/png/checkbox_check.png`) rendered when checkboxes are checked.
  - When unchecked, checkboxes are completely blank (clean white rectangle with subtle gray border).
  - Checkbox labels and indicator hitboxes now feature pointer cursors (`Qt.PointingHandCursor`).
- **Dedicated Single-Row Playback Layout**:
  - **Row 1 - Playback Speed**: Full-width card with horizontal speed slider, scale marks (`0.5x`, `1.0x`, `2.0x`), and live `1.00x` badge.
  - **Row 2 - Fade-In Timing**: Full-width card with smooth iOS-style toggle switch.
  - **Row 3 - Fade-Out Timing**: Full-width card with horizontal duration slider (replacing spinbox), live `1.00s` badge, and scale marks (`0.2s` to `3.0s`).
  - **Row 4 - Playback Behavior**: 4 distinct full-width option rows with macOS-native startup label ("Launch Voxel automatically at system startup").
  - **Row 5 - Audio Output & Recordings**: Structured into 2 distinct rows (Row 1: Output device selector; Row 2: Volume slider & Recordings folder with wrapped path).
  - **Row 6 - macOS Permissions**: Compact status pill, 1-click settings button, word-wrapped descriptions, zero horizontal overflow.
- **Zero Horizontal Scrolling Across All 5 Settings Tabs**:
  - Enforced `ScrollBarAlwaysOff` for horizontal scrolling across Voice & Speech, Playback, Appearance, About, and Permissions.
  - Resolved wide elements in Appearance (`frame_logo_req`), About (word-wrapped open source freedom & disclaimer cards), and Permissions (`card_status` 2-row button layout).
- **macOS Gatekeeper First-Launch Documentation & Guide**:
  - Comprehensive guide and scripts for bypassing macOS Gatekeeper quarantine (`com.apple.quarantine`) on unsigned community builds: Right-click -> Open, System Settings -> "Open Anyway", or `xattr -cr /Applications/Voxel.app`.

---

## [v1.1.18] - 2026-11-01

### Asynchronous Selection Tap, High-Contrast Permission Dialog & Dedicated Permissions Tab
- **Non-Blocking Quartz Event Tap Architecture**:
  - Moved mouse drag detection and clipboard polling (`time.sleep` / `grab_selected_text`) into an asynchronous background worker thread.
  - The Quartz mouse callback returns in `< 1ms`, completely preventing macOS from disabling the event tap due to timeout (`kCGEventTapDisabledByTimeout`).
- **High-Contrast, Ultra-Readable Permission Dialog**:
  - Completely redesigned `MacPermissionDialog` with high-contrast `#FFFFFF` typography, colored step badges (`1`, `2`, `3`), and rich HTML tags.
  - Added dedicated **"Restart Voxel Now"** button to immediately apply new macOS permissions.
  - Added **"Test Floating Bubble"** button so users can instantly verify the floating trigger badge on their screen.
- **Dedicated Permissions Page in Settings & System Tray**:
  - Added a prominent **"🛡️ Permissions"** sidebar tab in the Settings Dialog on macOS with live real-time status, 1-click System Settings opener, refresh button, and bubble testing.
  - Added **"🛡️ macOS Permissions..."** to the System Tray right-click menu.
- **Kernel-Level Single Instance Lock (`fcntl.flock`)**:
  - Replaced fragile `QSharedMemory` on macOS/Linux with kernel-level `fcntl.flock` file locking.
  - Prevents stale lock bugs and ensures Voxel always launches cleanly even after force-quits or crashes.
- **Session Event Tap Routing**:
  - Enhanced `CGEventPost` to target `kCGSessionEventTap` for active focused application windows with automatic fallback to `kCGHIDEventTap`.

---

## [v1.1.17] - 2026-11-01

### Hardware-Level Quartz Event Tap, Full Document Reader & Interactive Mac Permission Helper
- **Native Quartz CoreGraphics Event Simulation**:
  - Replaced fragile AppleScript and high-level virtual keyboard injection with hardware-level Apple Quartz CoreGraphics (`CGEventCreateKeyboardEvent` + `CGEventPost(kCGHIDEventTap)`).
  - Eliminates macOS AppleScript `-54` permission errors and guarantees instantaneous text capture on `Cmd+C`.
- **Full Document Narration (Select All & Read)**:
  - Upgraded `capture_full_document_from_active_window()` to issue native `Cmd+A` (Mac) / `Ctrl+A` (Win) followed by copy and clean deselect via Right Arrow.
  - Clicking the right Document icon (or pressing `Cmd+Option+D` / `Ctrl+Alt+D`) captures and reads entire Google Docs, Word documents, PDFs, and browser articles from top to bottom.
- **Interactive macOS Accessibility Helper Dialog**:
  - Created `MacPermissionDialog` (`src/ui/mac_permission_dialog.py`):
    - Shows beautiful brand guidance card with 1-click button to open System Settings.
    - Live polls macOS TCC status every 1.2s; as soon as permission is toggled ON, automatically restarts selection listeners with zero app restart needed.
  - Added dedicated **macOS Permissions & Text Selection** status card inside the Settings Dialog Playback tab.
- **Clipboard Resilience**:
  - Increased copy poll timeout from 180ms to 320ms with automatic secondary retry for heavy browser and PDF applications.

---

## [v1.1.16] - 2026-11-01

### Official Brand Logo Overhaul, macOS Gatekeeper Quarantine Bypass & Icon Regeneration
- **Official Brand Logo Integration**:
  - Replaced legacy navy-blue icon (`#171b2d` / `#6abfff`) with the authentic official Voxel purple (`#7441F9`) and electric cyan (`#00F0FF`) emblem across all platforms.
  - Sourced directly from `assets/Fainal/Voxel Logo (1)/apps icon (2).png` and user brand package.
  - Regenerated native Apple `assets/icon.icns` using `/usr/bin/iconutil` with high-DPI Retina resolutions (16px to 1024px).
  - Regenerated Windows `assets/icon.ico` packing 7 multi-resolution PNG streams (16, 24, 32, 48, 64, 128, 256 px) with anti-aliased alpha transparency.
- **Voice-Reactive MiniPlayer Logo**:
  - Upgraded `VoxelLogoWidget` (`src/ui/voxel_logo_widget.py`) to render the authentic brand emblem with crisp high-DPI scaling when idle.
  - Dynamically pulses the electric cyan/purple radial glow and modulates the 3 white equalizer lines during speech playback.
- **macOS Gatekeeper Quarantine Bypass & Error Fix Documentation**:
  - Documented root cause and 1-line solution for `"Voxel is damaged and can't be opened. You should move it to the Trash"` and `"Apple could not verify Voxel is free of malware"`:
    - Added instant terminal fix: `xattr -cr /Applications/Voxel.app`.
    - Added GUI bypass steps for macOS System Settings > Privacy & Security > Open Anyway.
    - Updated DMG installer `READ ME - First Launch.txt` bundled inside `Voxel.dmg`.
  - Documented resolution for early `QPaintDevice::devicePixelRatio()` backingstore crash (`SIGSEGV`).
- **Automated Brand Pipeline**:
  - Created `scripts/generate_official_brand_assets.py` to automate edge anti-aliasing, transparent PNG export, and icon generation on any workstation.
- **Repository Single Source of Truth**:
  - Completely updated `README.md` with detailed branding specifications, file locations, build commands, and instructions for future AI assistants.

---

## [v1.1.15] - 2026-10-31

### Appearance Tab Redesign, Custom Logo Uploader & Official Document Logo
- **Official Circular Document Logo Integration**:
  - Embedded newly provided official circular purple document icon with crisp white folded page (`assets/Fainal/Voxel Logo for Doc.png` and `assets/branding/png/selection_bubble_doc.png`).
  - Updated the floating selection bubble right-action button to display the official document logo, providing visual balance with the circular mic icon.
- **Custom Application Logo Uploader**:
  - Implemented **App Logo & Icons** card in Appearance tab matching user mockup:
    - Real-time logo preview container.
    - **Change Logo** button with file picker (`*.png`, `*.jpg`, `*.svg`, `*.ico`) to upload and apply custom logos across the app.
    - **Restore Default** button to revert to official Voxel brand logo.
    - Styled **Logo Requirements** info box with format and dimension specifications.
- **Dynamic Floating Bubble Settings**:
  - **Bubble Appearance Cards**: 4 selectable cards (`Default`, `Frosted Glass`, `Transparent`, `Minimal`) featuring mini dual-action capsule previews and active checkmark badges (`✓`).
  - **Corner Radius Selector**: 3 selectable corner styles (`Square`, `Medium`, `Round`) with custom vector graphics and active checkmark badges (`✓`).
  - **Bubble Size & Transparency Controls**: Sliders for fine-grained bubble dimensions (Small, Medium, Large) and transparency (30% to 100%).
  - Immediate real-time sync with floating bubble geometry, corner radius, and window opacity.

---

## [v1.1.14] - 2026-10-31

### Official Brand Logo & Custom CSS/QSS Refinement
- **Official Brand Header Logo Integration**:
  - Embedded high-resolution official logo from `assets/Fainal/Voxel Logo Main.png` (light mode) and `assets/Fainal/Voxel Logo Main Dark.png` (dark mode) directly into the Settings sidebar header.
  - Replaced legacy vector mic placeholder with authentic Voxel brand typography and microphone mark.
- **Custom CSS / QSS Polish & Modern Toggle Switches**:
  - Replaced plain checkboxes with styled, smooth sliding `ToggleSwitch` for settings like "Smooth fade-in at start".
  - Injected crisp custom checkmark indicator asset (`checkbox_check.png`) for `QCheckBox::indicator:checked`, eliminating solid blank purple square rendering.
  - Styled mini preview cards with active ring states and custom vector art for theme and bubble selection.
- **Mnemonic Ampersand Bug Fixes**:
  - Escaped all literal ampersands as `&&` in Qt groupboxes and labels (`Fade && Timing`, `Voice && Speech`, `Audio Output && Recordings`) so Windows doesn't render them as unwanted underscores (`Fade_Timing`).
- **Clean Window Titlebars**:
  - Removed redundant application name concatenation on Windows title bars (`setApplicationDisplayName("")`).
- **Dark & Light Palette Synchronization**:
  - Sleek dark theme palette matching user design: deep charcoal background (`#0B0F19`), surface card containers (`#161F30`), borders (`#1E293B`), and vibrant accent purple (`#7C3AED`).

---

## [v1.1.13] - 2026-10-31

### Audio Recording & Automatic Documents Folder
- **Integrated Player Record Button**:
  - Added dedicated one-click recording button (`btn_record`) to the floating MiniPlayer with studio-style red indicator icon.
  - Active recording state shows glowing red indicator and tooltips.
  - Automatically captures and stitches all synthesized speech chunks for the current narration into a clean MP3 file.
- **Automatic Voxel Recordings Folder**:
  - Automatically creates and manages the `Documents\Voxel Recordings` directory.
  - Saves all recordings as timestamped MP3 files (e.g. `Voxel_Recording_YYYYMMDD_HHMMSS.mp3`).
  - Added direct **"Open Recordings Folder"** action in Settings and instant system notifications upon save.

### Settings UI Redesign Matching Mockups
- **Faithful 4-Tab Sidebar Navigation Layout**:
  - Left sidebar streamlined to `🎙️ Voice & Speech`, `▶ Playback`, `🎨 Appearance`, and `ℹ️ About`.
  - Added custom organic purple/lavender decorative wave at the bottom-left of the sidebar.
- **Playback Tab**:
  - Re-architected matching user mockup with purple playback speed slider, `1.25x` badge, fade & timing controls, 2x2 playback behavior checkboxes, audio output device selector, and volume slider.
- **Appearance Tab**:
  - Interactive Light / Dark theme selection cards with visual previews and selected checkmarks.
  - 4 selectable Floating Bubble appearance cards: `Default`, `Frosted Glass`, `Transparent`, `Minimal`.
  - Bubble transparency and size sliders.
- **Action Bar**:
  - Redesigned with `↺ Reset to Default` and primary purple `✓ Save Changes`.

---

## [v1.1.12] - 2026-10-31

### Branding, App Icon & Dual-Action Capsule Assets
- **Official Voxel App Icon**:
  - Processed and integrated official application logo (`assets/Fainal/Voxel Logo for apps.png`) into `assets/branding/png/app_logo.png`, `app_logo_square.png`, and generated high-resolution Windows `icon.ico` (16, 24, 32, 48, 64, 128, 256 px).
  - Window icon, taskbar preview, and Windows PE metadata updated with official branding.
- **Selection Bubble Official Dual Icons**:
  - Integrated official microphone logo on the left of the floating capsule.
  - Integrated official document reader icon (`assets/Fainal/Voxel Logo for Doc.png`) on the right of the floating capsule.

### UI/UX Modernization & Interactive Voice Equalizer
- **Modern Sidebar Navigation Preferences Layout**:
  - Redesigned Preferences dialog into professional desktop layout with left sidebar (Preferences, Voice & Speech, Playback, General, Appearance, About).
  - Segmented pill theme toggle (`☀️ Light` | `🌙 Dark`) on top header with live preview.
  - Clean card architecture with soft borders, rounded corners, and clear typography.
- **Interactive Voice Equalizer (EQ)**:
  - Interactive parametric EQ curve widget with frequency bands: HPF, 100Hz, 200Hz, 500Hz, 1kHz, 2kHz, LPF.
  - Vocal presets: `Podcast Warmth`, `Vocal Clarity`, `Bright & Airy`, `Flat / Natural`.
  - Draggable control nodes with live dB indicators and double-click reset to 0dB.
- **Wider, Focused Context Menus**:
  - Right-click menus on both system tray and floating capsule streamlined to `⚙️ Preferences...`, `ℹ️ About Voxel...`, and `Quit Voxel` with min-width of 200–220px.
- **About Section Refinements**:
  - Clean `🔗 Connect on LinkedIn` button (with correct spelling and direct link).
  - Prominent version badge `v1.1.12`, Digimo, and GitHub repository links.

---

## [v1.1.11] - 2026-10-31

### Branding & System Tray Update
- **Refined System Tray Logo**:
  - Exclusively updated system tray icon to the user's high-visibility circular purple microphone badge (`assets/Fainal/Voxel Logo.png`), keeping main app icon untouched for upcoming app logo release.
  - Applied 4x supersampled subpixel antialiasing to circular boundaries with smooth transparent margins for light and dark taskbars.

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
