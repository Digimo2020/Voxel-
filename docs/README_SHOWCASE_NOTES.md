README Showcase Update Notes (v1.0) - 2026-10-30

This branch replaces the previous long technical README with a more welcoming project story and clearer setup guidance.

Accuracy notes:
- The current repository release documented in CHANGELOG.md is v1.1.04.
- The neural TTS integration is Edge TTS and requires network access.
- Native offline speech fallback is platform-dependent; do not describe all neural voices as offline.
- Speed presets in src/config.py range from 0.5x to 2.0x.
- Emotion/tone presets are defined in src/config.py; exact voice capability depends on the speech engine.
- Current screenshots have not been recaptured from a running app in this environment. The README labels existing assets as previews/design references instead of presenting them as freshly captured runtime screenshots.
- Future subtitles, visual reading aids, further languages and voices are clearly presented as ideas, not current features.

Before merging:
1. Run the app on Windows 10/11 and macOS.
2. Capture individual, unaltered app screenshots for selection bubble, mini-player, settings, and document reader.
3. Record a short real screen capture of selecting text, starting playback, changing speed and pausing.
4. Replace design-preview images in the README with the new runtime captures after checking that each represents the current release.
5. Validate install links against the GitHub Releases page and run the workflow on the updated branch.
