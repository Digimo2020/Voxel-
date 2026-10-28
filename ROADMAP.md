# Text 2 Voice — Product Roadmap 🗺️

This document outlines planned milestones and feature directions for the open-source community.

---

## 📌 Phase 1: Windows Core MVP *(Completed ✅)*
- [x] Universal text selection detection across all apps (Browser, Word, Google Docs).
- [x] Safe clipboard interception (preserves user clipboard history).
- [x] Floating Mic Bubble with smooth fade-in and auto-hide.
- [x] Floating Mini Player Pill with Play/Pause, Stop, and Drag-to-Move.
- [x] Speed Regulation: `[-] 1.0x [+]` stepping from `0.5x` to `2.0x`.
- [x] Neural Voice Support: Jenny (US Female), Guy (US Male), Sonia (UK Female).
- [x] Offline Voice Fallback (Microsoft SAPI5).
- [x] Local JSON History Database & Replay Dialog.
- [x] Global Hotkey (`Ctrl+Alt+S`).
- [x] Windows Standalone `.exe` packaging (PyInstaller).

---

## 📌 Phase 2: macOS Port *(Next Up 🚀)*
- [ ] Implement macOS Accessibility permission checks on first launch.
- [ ] Map modifier keys from `Ctrl` to `Cmd` (`Cmd+C` clipboard grab).
- [ ] Adapt `pynput` mouse listener for macOS Quartz event tap.
- [ ] Test offline TTS fallback with `NSSpeechSynthesizer` (`say`).
- [ ] Build macOS standalone `.app` bundle & `.dmg` installer.

---

## 📌 Phase 3: Enhanced Features & Power-User Tools
- [ ] **Multi-Language Voice Support**: Spanish, French, German, Japanese, Chinese, Hindi.
- [ ] **Custom Hotkey Settings UI**: Configurable global shortcuts via settings dialog.
- [ ] **Word-by-Word Subtitle Highlighting**: Synchronized karaoke-style word highlighting while speaking.
- [ ] **OCR for Screen Text**: Select text directly from images, videos, and protected PDFs using local OCR (Tesseract / EasyOCR).
- [ ] **Audio Export**: One-click "Save as MP3 / WAV" option for any selected text.

---

## 📌 Phase 4: Linux Support
- [ ] X11 / Wayland global selection hook support via `xclip` / `wl-clipboard`.
- [ ] Package into AppImage, Flatpak, and Debian `.deb` packages.
