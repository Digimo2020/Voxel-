# Voxel UI/UX Concept Pack

This document records the Voxel visual direction for the existing desktop text-to-speech app.

## Brand direction

- **Product name:** Voxel
- **Tagline:** Text to speech, anywhere
- **Visual identity:** microphone/speech-bubble mark with blue-to-violet gradient; dark navy wordmark.
- **Palette:** electric blue, violet, cyan, deep navy, neutral white/gray.
- **Themes:** dark glass as the high-contrast default; light frosted glass as an option.
- **Player order:** logo/name, Play/Pause, Stop, speed control, voice selector, Settings, Close.

## Mockup gallery

The supplied images are preserved individually, resized for practical repository viewing, and saved as JPEG previews.

- [Primary brand logo](../assets/mockups/01-brand-primary.jpg)
- [Brand system and app icons](../assets/mockups/02-brand-system.jpg)
- [Dark and light player concepts](../assets/mockups/03-player-dark-light.jpg)
- [Settings, tray menu and selection trigger](../assets/mockups/04-settings-and-tray.jpg)
- [Glass player — wide](../assets/mockups/05-player-glass-wide.jpg)
- [Glass player — compact](../assets/mockups/06-player-glass-compact.jpg)
- [Dark and light player alternative](../assets/mockups/07-player-dark-light-alt.jpg)
- [Primary logo alternative](../assets/mockups/08-brand-primary-alt.jpg)
- [Final player direction](../assets/mockups/09-player-final-direction.jpg)

## UX recommendations

1. **Keep the player focused.** Maintain a compact order and group related controls with subtle separators.
2. **Accessible controls.** Add tooltips, accessible labels, visible keyboard focus, and 32–40 px minimum targets for frequent actions.
3. **Visible playback state.** Change Play to Pause while reading; Stop halts speech. Show a concise Ready/Reading/Paused status without moving the controls.
4. **Speed control.** Support 0.5×–2.0× and disable step buttons at the limits.
5. **Voice menu.** Show the active voice and persist the user's last choice.
6. **Glass fallback.** Offer an opaque surface when transparency is unsupported or reduced transparency is preferred; keep contrast high.
7. **Tray parity.** Include Pause/Resume, Settings, Open Voxel and Exit in the tray menu.
8. **Selection trigger.** Position beside the selection without covering text; dismiss after timeout or outside click.
9. **Platform integration.** The current codebase is Python/PyQt and Windows-first. Treat the images as targets; system permissions and OS-specific behavior need separate implementation and testing.
10. **Quality checks.** Test 100%, 125%, 150% and 200% scaling, focus order, contrast, reduced motion, and both themes.

## Browser preview

Open [preview/index.html](../preview/index.html) directly. It is a no-build interaction mockup; the controls update UI state but do not synthesize speech.

## Integrating with the current desktop app

- Retain the existing TTS engine, selection listener, tray, settings, and history architecture.
- Implement the visual direction in `src/ui/mini_player.py` and the floating trigger in `src/ui/floating_bubble.py`.
- Centralize palette and spacing tokens in shared UI helpers.
- Add theme preference with migration-safe defaults.
- Use vector paths for production branding rather than embedding screenshot images in the app.

## Scope

The nine concept images were supplied by the project owner and added individually as reference assets. No existing source files are replaced by this concept pack.
