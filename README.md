# Text 2 Voice

A lightweight desktop utility for reading selected text aloud using a floating trigger and compact player.

> **Status: In development.** The repository contains a Python/PyQt6 implementation. Features and platform compatibility must be verified on target systems before being described as production-ready.

## Current implementation

The current source includes:
- A PyQt6 desktop application entry point.
- Global mouse and keyboard listeners built with `pynput`.
- Clipboard-based selected-text capture.
- A floating trigger and compact mini-player UI.
- An `edge-tts` speech synthesis path with a `pyttsx3` fallback attempt.
- Playback speed and voice selection.
- A system-tray menu and local JSON speech history.
- A Windows executable build workflow.

These are source-code features, not a claim that every feature has been tested successfully in every application or operating system.

## Intended workflow

1. Select text in an application.
2. A small floating trigger appears near the pointer.
3. Click the trigger to start reading.
4. Use the player to pause/resume, stop, adjust speed, select a voice, or close it.
5. Access the app from the system tray.

Text-selection capture depends on the target app accepting simulated copy commands. Canvas editors, protected PDFs, remote desktops, and some elevated applications may behave differently.

## Technology

- Python 3.11 recommended
- PyQt6
- pynput
- pyperclip
- edge-tts
- pygame
- pyttsx3
- PyInstaller for Windows packaging

## Requirements

Install a supported Python version and Git. Because global input hooks and clipboard capture interact with the desktop, run the application in a trusted local session and review permissions before use.

## Run on Windows

Clone the repository and create an isolated environment:

```powershell
git clone https://github.com/Digimo2020/Text-2-Voice.git
cd Text-2-Voice
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Alternatively, use `run.bat` after dependencies are installed.

## Build a Windows executable

```powershell
python -m pip install pyinstaller
.uild_exe.bat
```

The intended output is `dist/Text2Voice.exe`. A successful build does not by itself guarantee that selection hooks, speech playback, or packaging works correctly on every machine. Verify it on a clean Windows test system before distributing.

## Configuration

`.env.example` documents proposed settings. Check the actual code before assuming every listed environment variable is currently loaded or effective. Do not put real credentials, private tokens, or personal data in the repository.

## Privacy and clipboard behaviour

Text selection uses a simulated copy shortcut and temporarily writes a sentinel value to the system clipboard before attempting restoration. Clipboard restoration cannot be guaranteed for every clipboard manager, rich clipboard format, or timing condition. The current implementation also saves spoken text in local JSON history.

Before using the app with confidential text:
- Understand that selected text may be submitted to the configured online Edge TTS service when online synthesis is used.
- Review the privacy terms of any remote service.
- Avoid sensitive content until the clipboard and history behaviours have been thoroughly tested.
- Keep local history private and clear it when no longer needed.
- Disable or exit global listeners when you do not need them.

## Platform support

- **Windows:** Primary target; runtime and packaging still require real-device validation.
- **macOS:** Not yet verified. Accessibility permissions and platform-specific clipboard, hotkey, and offline TTS behaviour need testing.
- **Linux:** Not currently supported.

## Testing and CI

The repository includes a GitHub Actions workflow that attempts dependency imports and builds a Windows executable. Review the Actions results for the current branch to confirm whether the latest run passed. Automated build success is not a substitute for interactive testing.

Recommended manual tests:
- Notepad and a browser text field/document
- Google Docs and a PDF reader
- Single-click, double-click, and drag selection
- No-selection and empty-selection cases
- Clipboard text and rich-format preservation
- Play/pause/stop, speed and voice changes
- Network loss and offline fallback
- Unicode, long text, punctuation, and non-English text
- Shutdown during synthesis and playback

## Repository map

```text
main.py                    Application entry point
src/config.py              Voice, speed, and UI settings
src/selection_listener.py  Global input listeners
src/tts_engine.py          Speech synthesis and audio playback
src/ui/                    Floating trigger, player, tray, history dialog
src/utils/                 Clipboard and JSON history helpers
assets/icons.py            Vector icons
scripts/                   Preview-image generation script
.github/workflows/         Build automation
requirements.txt            Python dependencies
build_exe.bat              Windows packaging helper
run.bat                    Windows launcher
ROADMAP.md                 Planned work
CONTRIBUTING.md             Contributor guide
SECURITY.md                 Vulnerability reporting
CHANGELOG.md                Change history
```

## Roadmap

See [ROADMAP.md](ROADMAP.md). Roadmap checkboxes should reflect verified implementation status, not intended functionality.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please describe platform, Python version, reproduction steps, and test results in bug reports.

## Security

Read [SECURITY.md](SECURITY.md). Never commit API keys, GitHub tokens, access credentials, private text, generated history files, or personal clipboard data.

## License

See [LICENSE](LICENSE) for the repository's current license file. Confirm licensing and third-party dependency terms before redistributing builds.
