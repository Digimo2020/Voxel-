# Voxel interface direction

## Approved product identity
- Name: **Voxel**
- Tagline: **Text to Speech, Anywhere.**
- Use the approved mark from `assets/branding/voxel-logo.svg`: rounded speech/text capsule with three horizontal text lines and integrated lower speech tail.
- Brand palette: violet `#6847FF`, blue `#168BFF`, navy `#111B2E`.
- Do not use a generic recording microphone or Windows volume glyph as the primary brand mark.

## Player variants
1. **Dark** — default; deep charcoal/navy pill, pale line-art controls, blue-purple play accent, slim separators, subtle border and shadow.
2. **Glass** — optional appearance; translucent pale surface, white edge, faint blue-lavender tint, dark navy controls, high text contrast. Keep the effect restrained so text remains readable over arbitrary desktop content.

## Suggested player order
Brand mark (small) · Play/Pause · Stop · Speed decrement · speed value · Speed increment · Voice selector · Settings · Close.

The player is a compact utility, not a dashboard. Keep the controls accessible at Windows scaling factors. Use tooltips, hit areas of at least approximately 28 px, and clear keyboard focus. Avoid sound/recording states that could imply microphone capture; playback state should be communicated by play/pause and a subtle progress indication.

## First-launch/intro screen
Show the approved Voxel icon centred on a clean light or dark background, with “Voxel” and “Text to Speech, Anywhere.” beneath it. Use a brief fade only; proceed into the tray-resident experience rather than a mandatory dashboard.

## Behaviour and accessibility
- Player remains above other windows while active but should not steal focus unnecessarily.
- Make the player draggable.
- Close dismisses the player; Stop halts playback without quitting the app.
- Voice selector should expose the full voice name in an accessible dropdown rather than relying only on cycle behavior.
- Respect system theme by default; allow Dark and Glass as user-selectable options.
- Provide accessible names/tooltips and visible focus indicators.
- Validate contrast, DPI scaling, monitor-edge docking, multi-monitor behaviour and keyboard navigation.

## Implementation note
This file describes design direction. It is not a claim that every item has already been implemented.
