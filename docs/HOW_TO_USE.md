# How to use Voxel

A picture-first guide. Every image below is a real Voxel window.

<p align="center"><img src="images/how-it-works.png" alt="Select text, click the bubble, listen" width="100%"></p>

---

## 1. Install

| Windows | macOS |
| :--- | :--- |
| Download `Voxel-v<version>.exe` from [Releases](https://github.com/Digimo2020/Voxel-/releases/latest) and double-click it. | Download `Voxel-v<version>.dmg`, drag **Voxel** into *Applications*, then run `xattr -cr /Applications/Voxel.app` once in Terminal. |
| Windows blocks it ("Smart App Control")? Test builds are not code-signed yet. Run from source with `run.bat` instead. See [signing plan](WINDOWS_STORE_GUIDE.md). | Allow Voxel in *System Settings → Privacy & Security → Accessibility*, then restart it. |

Voxel lives in the **system tray** (Windows) or **menu bar** (macOS) after it starts.

---

## 2. Read selected text (the main way)

### Step 1: Highlight text in any app
<img src="images/step1-select.png" alt="Highlight text" width="620">

### Step 2: Click the wave icon on the bubble
<img src="images/step2-click.png" alt="Click the wave icon on the bubble" width="620">

- **Wave icon** reads your selection. **Page icon** reads the whole document or PDF.
- Shortcuts: **Ctrl+Alt+S** reads the selection, **Ctrl+Alt+D** reads the whole document (macOS uses the same keys with Cmd+Option).

### Step 3: Listen
<img src="images/step3-listen.png" alt="Mini player reading aloud" width="620">

### The mini player

<img src="images/player.png" alt="Mini player in light and dark" width="420">

At rest the player shows only two things: the **wave** (grey when idle, moving blue while reading, red while recording) and the **blue Play/Pause** button. **Hover the player** and it slides open:

| Control | What it does |
| :--- | :--- |
| Blue round button | Play / Pause |
| `1×` | Change speed |
| `•••` More | Read the whole document · Record to MP3 |
| Sliders icon | Open Settings |
| ✕ | Close the player |

A thin line along the bottom of the player shows progress through long texts.

--- | :--- |
| ⏯ Round blue button | Pause / resume |
| `1.0x ▾` | Change speed |
| 📄 Page icon | Read the entire document |
| ⏺ Red circle | Record the speech to an MP3 (saved in *Documents/Voxel Recordings*) |
| ⚙ Gear | Open Settings |
| ✕ | Close the player |

---

## 3. Read Text: for apps that block selection

Some apps and websites do not let Voxel read a selection. Copy the text yourself and use **Read Text**.

<img src="images/read-text-annotated.png" alt="Read Text page with numbered steps" width="620">

1. **Paste** from the clipboard (or type).
2. Check the text. The window shows word count and how long it will take.
3. **Read aloud**. Press it again to stop. Shortcut: **Ctrl+Enter**.

Open it any time: right-click the tray icon → **Read Text...**, or open Voxel and pick **Read Text** in the sidebar.

<img src="images/tray-menu.png" alt="Tray menu" width="240">

---

## 4. The Voxel window

Double-click the tray icon (or tray menu → **Open Voxel**). The sidebar has:

| Page | What it is for |
| :--- | :--- |
| **Listen** | Turn selection reading on/off, see what is playing, shortcuts |
| **Read Text** | Paste text and listen |
| **Resources** | Saved text, bookmarks and recordings |
| **History** | Everything Voxel read: replay, copy, clear |
| **Settings** | General, Voice, Playback, Appearance, Accessibility, About |

<img src="images/settings-listen-light.png" alt="Listen page" width="620">

### Resources: keep what matters

| Tab | How things get there |
| :--- | :--- |
| **Saved text** | In **Read Text**, press **Save**. Open it again later, read it aloud, or delete it. |
| **Bookmarks** | In **History**, press **Bookmark** (★). History keeps only the latest 50 items; bookmarks stay. |
| **Recordings** | In the mini player, **More → Record to MP3**. |

<img src="images/settings-resources-light.png" alt="Resources page" width="620">

### Settings

Changes are saved automatically. Less common options are under **More options** / **Advanced**. Theme (Light, Dark, System) is in **Appearance**.

<img src="images/settings-settings-light.png" alt="Settings page" width="620">

<img src="images/bubble-styles.png" alt="Bubble styles and sizes" width="620">

### Dark theme

<p>
  <img src="images/settings-read-text-dark.png" alt="Read Text, dark" width="49%">
  <img src="images/settings-history-dark.png" alt="History, dark" width="49%">
</p>

---

## 5. Problems?

| Problem | Try this |
| :--- | :--- |
| No bubble appears when I highlight text | **Listen** page → turn on **Read selected text**. On macOS check Accessibility permission. |
| App or website does not allow selecting | Use **Read Text** (section 3). |
| Windows says "blocked an app" | Not signed yet. Run `run.bat`, or see the [signing plan](WINDOWS_STORE_GUIDE.md). |
| No sound | Settings → Playback → **Volume** and **Output device**. |
| Which version do I have? | Bottom of the sidebar, or Settings → About. |

Still stuck? [Open an issue](https://github.com/Digimo2020/Voxel-/issues). Privacy: [PRIVACY.md](PRIVACY.md).

---

<sub>Images are generated from the real app by <code>python scripts/generate_docs_images.py</code> (demo data only).</sub>
