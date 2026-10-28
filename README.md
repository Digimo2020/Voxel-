# Voxel

<p align="left">
  <img src="assets/branding/voxel-logo.svg" alt="Voxel — Text to Speech, Anywhere" width="420">
</p>

**Text to Speech, Anywhere.**

Voxel is a lightweight Windows desktop utility that reads selected text aloud with a small floating trigger and a compact player. The interface is designed to stay out of the way while you work.

> **Project status:** In development. Windows UI, text-selection capture, speech playback, and packaging require testing on the target system. Features below describe repository implementation or design intent; compatibility varies by application.

## Brand and interface

Voxel's approved identity uses the custom text/speech mark with three inner lines, a purple-to-blue gradient, and a dark navy wordmark. The repository keeps a scalable SVG brand mark and a PyQt-rendered version for desktop UI use.

- **Dark player:** charcoal/navy capsule, pale line icons, blue-purple accent.
- **Glass player:** translucent pale surface, fine light border, subtle blue/purple glow.
- **Floating trigger:** small icon-only control near selected text.
- **Typography:** Segoe UI for native Windows UI; Inter is suitable for accompanying web documentation and promotional assets.
- Keep the logo geometry and brand colors consistent. Do not substitute unrelated microphone or volume logos.

## Intended workflow

1. Select text in another desktop application.
2. A compact Voxel trigger appears near the selection/cursor.
3. Activate it to read the selected text aloud.
4. Use the floating player to play/pause, stop, change speed, switch voice, open settings, or close it.
5. Access preferences and history through the system tray.

Text capture depends on the target application allowing a simulated copy shortcut. Some canvas-based editors, protected documents, remote sessions, or elevated applications may behave differently.

## Current implementation

The source includes:
- A PyQt6 desktop application entry point.
- Global mouse and keyboard listener integration.
- Clipboard-based selected-text capture and attempted restoration.
- Floating trigger and bottom-right animated mini-player.
- Edge TTS synthesis with an attempted local `pyttsx3` fallback.
- Voice and speed controls.
- System-tray integration, settings, and local JSON history.
- Windows executable packaging workflow.

This README does not imply every feature is validated in all applications or platforms.

## Installation (Windows)

Requirements: Windows 10/11, Python 3.11 recommended, and Git.

```powershell
git clone https://github.com/Digimo2020/Voxel---V.002.git
cd Voxel---V.002
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Alternatively, use `run.bat` after dependencies have been installed.

## Build

Run the packaging script on Windows:

```powershell
build_exe.bat
```

The intended output is `dist/Text2Voice.exe` until the executable/package naming is deliberately migrated to Voxel. A successful build is not by itself proof that all desktop interactions work correctly.

## Privacy and clipboard considerations

Voxel may temporarily modify the clipboard to retrieve selected text, and the source stores spoken text in a local JSON history file. Clipboard restoration may not preserve every rich clipboard format or clipboard-manager state. Online Edge TTS synthesis sends text to the configured speech service.

Before reading confidential information:
- Review the code and applicable service privacy terms.
- Test clipboard behaviour with your normal clipboard manager.
- Review and clear local speech history as needed.
- Exit the application to stop global listeners when not needed.

## Platform support

- **Windows:** primary target; test on the specific Windows versions and apps before distribution.
- **macOS:** not verified; accessibility permissions and platform TTS/clipboard behaviour require implementation and testing.
- **Linux:** not currently supported.

## Quality checks

The GitHub Actions workflow performs dependency-import checks and attempts a Windows executable build. Check the latest workflow run for the actual result. Manual tests should cover text selection in Notepad, browsers, Google Docs, and PDF readers; clipboard preservation; pause/resume/stop; voice and speed changes; offline behaviour; and shutdown during playback.

## Repository structure

```text
main.py                    Application entry point
src/config.py              Voice profiles, speeds, theme tokens
src/selection_listener.py  Global input and selection listener
src/tts_engine.py          Speech synthesis and playback
src/ui/                    Floating trigger, player, tray, settings, history
src/utils/                 Clipboard, settings, history, version
assets/icons.py            PyQt-rendered brand and interface icons
assets/branding/            Voxel SVG brand mark and variants
assets/screenshots/         Project preview images
requirements.txt            Python dependencies
build_exe.bat               Windows packaging helper
run.bat                     Windows development launcher
ROADMAP.md                  Future development
CONTRIBUTING.md             Contribution guide
SECURITY.md                 Security reporting
CHANGELOG.md                Release notes
LICENSE                     License
```

## Roadmap

See [ROADMAP.md](ROADMAP.md). Treat any future macOS support, extra languages, OCR, appearance options, and distribution improvements as planned until implemented and tested.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and [SECURITY.md](SECURITY.md) for vulnerability reporting. Never commit access tokens, credentials, private clipboard content, or local history data.

## License

See [LICENSE](LICENSE).
