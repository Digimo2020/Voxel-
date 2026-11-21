<p align="center">
  <img src="assets/banner.png" alt="Voxel" width="100%">
</p>

<h1 align="center">Voxel</h1>
<p align="center"><b>Select text anywhere. Hear it instantly.</b><br>Free text-to-speech for Windows & macOS, a <a href="https://www.digimo.pt/">Digimo</a> product.</p>

<p align="center">
  <a href="https://github.com/Digimo2020/Voxel-/releases/latest"><img src="https://img.shields.io/github/v/release/Digimo2020/Voxel-?style=for-the-badge&color=7441F9&label=Latest" alt="Latest version"></a>
  <a href="https://github.com/Digimo2020/Voxel-/releases"><img src="https://img.shields.io/github/downloads/Digimo2020/Voxel-/total?style=for-the-badge&color=00BCD4&label=Downloads" alt="Downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-6366F1?style=for-the-badge" alt="MIT"></a>
</p>

<p align="center">
  <a href="https://github.com/Digimo2020/Voxel-/releases/latest/download/Voxel.exe"><img src="https://img.shields.io/badge/%E2%AC%87%20Download%20for%20Windows-7441F9?style=for-the-badge&logo=windows&logoColor=white" alt="Download for Windows"></a>
  &nbsp;
  <a href="https://github.com/Digimo2020/Voxel-/releases/latest"><img src="https://img.shields.io/badge/%E2%AC%87%20Download%20for%20macOS-0F172A?style=for-the-badge&logo=apple&logoColor=white" alt="Download for macOS"></a>
</p>

---

## How it works

| 1. Select | 2. Click the bubble | 3. Listen |
| :---: | :---: | :---: |
| Highlight text in any app: browser, Word, PDF | A small floating badge appears near your cursor | Neural voices read it in a mini player |

<p align="center">
  <img src="assets/branding/mini_player_themes.png" alt="Voxel mini player, dark and frosted glass" width="90%">
</p>

## Features

- 🎙 **Natural voices**: Microsoft Edge neural voices, with offline fallback (macOS Speech / Windows SAPI)
- 🫧 **Never steals focus**: the bubble sits on top of your work without interrupting it
- 📄 **Read whole documents** with one click
- 🎚 **Your pace**: speed, pitch, volume and equalizer presets
- 🌗 **Light, dark and frosted-glass** themes; small / medium / large bubble sizes

## Install

**Windows**: download `Voxel.exe`, run it. If SmartScreen warns, choose *More info → Run anyway*.

**macOS**: open the `.dmg`, drag Voxel to Applications, then run once in Terminal:

```bash
xattr -cr /Applications/Voxel.app
```

Then allow Voxel under *System Settings → Privacy & Security → Accessibility*.

**From source**

```bash
pip install -r requirements.txt
python main.py
```

## Tech

Python 3.11 · PyQt6 · pynput · edge-tts · pypdf · PyInstaller · GitHub Actions

## More

[Full details](docs/DETAILS.md) · [Changelog](CHANGELOG.md) · [Roadmap](ROADMAP.md) · [Versioning rules](VERSIONING_RULES.md) · [Contributing](CONTRIBUTING.md) · [All releases](https://github.com/Digimo2020/Voxel-/releases)

<p align="center"><sub>MIT License · Made by Digimo</sub></p>
