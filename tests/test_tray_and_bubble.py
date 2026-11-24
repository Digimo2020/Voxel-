"""Regression checks: the bubble still appears (Voxel's own copy keys are not 'user typing'),
tray reading actions, and settings apply without errors. Run: python tests/test_tray_and_bubble.py"""
import os, sys, time, ctypes
repo = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo); os.chdir(repo)
from PyQt6.QtWidgets import QApplication
results = []
def check(n, c): results.append((n, bool(c)))

from src.utils import settings as S
SET = {"skip_text_fields": True, "selection_popup_enabled": True}
S.settings_db.get = lambda k, d=None: SET.get(k, d)
S.settings_db.set = lambda k, v: SET.__setitem__(k, v)

# ── 1. The v1.1.26 regression: the copy's own Ctrl/Cmd+C reached the key listener ──
import src.selection_listener as SL
SL.is_typing_in_text_box = lambda: False
SL._is_screenshot_app_active = lambda: False
L = SL.SelectionListener()
emitted = []
L.text_selected.connect(lambda *a: emitted.append(a))

def copy_that_presses_keys(injected_flag):
    def fake(timeout_ms=0, persistent=True):
        # what really happens: our Ctrl down + C down arrive at our own keyboard listener
        if injected_flag is None:
            L._on_any_key("ctrl"); L._on_any_key("c")
        else:
            L._on_any_key("ctrl", injected_flag); L._on_any_key("c", injected_flag)
        return "Selected words on a page"
    return fake

app = QApplication(sys.argv)
for label, flag in (("keys reported as injected", True), ("keys NOT reported as injected", None)):
    emitted.clear()
    SL.grab_selected_text = copy_that_presses_keys(flag)
    L._handle_possible_selection(5, 5, 0, 0, time.time())
    app.processEvents()
    check(f"bubble appears although copy pressed Ctrl+C ({label})", len(emitted) == 1)

emitted.clear()
SL.grab_selected_text = copy_that_presses_keys(None)
L._ignore_keys_until = 0.0  # fresh selection, no copy just happened
released = time.time()
import threading
threading.Timer(0.04, lambda: L._on_any_key("a")).start()   # real user typing during the wait
L._handle_possible_selection(5, 5, 0, 0, released); app.processEvents()
check("still backs off when the user really types", len(emitted) == 0)

# ── 2. Tray menu ──
from src.tts_engine import TTSEngine
from src.ui.tray_icon import AppTrayIcon
tts = TTSEngine()
tray = AppTrayIcon(tts)
labels = [a.text().split("\t")[0] for a in tray.contextMenu().actions() if a.text()]
for want in ["Read selected text", "Read whole document", "Read copied text", "Bubble on selection"]:
    check(f"tray has '{want}'", want in labels)
tray._refresh_playback_actions()
check("Pause/Stop hidden when idle", not tray.pause_action.isVisible() and not tray.stop_action.isVisible())
tts.is_speaking = True; tts.is_paused = True
tray._refresh_playback_actions()
check("Resume/Stop shown while reading", tray.stop_action.isVisible() and tray.pause_action.text() == "Resume")
tts.is_speaking = False; tts.is_paused = False
got = []
tray.read_document_requested.connect(lambda t: got.append(("doc", t)))
tray.read_selection_requested.connect(lambda: got.append(("sel",)))
for a in tray.contextMenu().actions():
    if a.text().startswith("Read selected text") or a.text().startswith("Read whole document"):
        a.trigger()
check("tray actions emit", ("sel",) in got and ("doc", "") in got)

# ── 3. Remembering the working window (Windows) ──
from src.utils import foreground as FG
if sys.platform == "win32":
    taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    check("taskbar is never remembered as the working window", FG._class_name(taskbar) in FG._SHELL_CLASSES)
FG._last_hwnd = 0
check("restore without a remembered window is safe", FG.restore() is False or sys.platform != "win32")

# ── 4. The app: tray read + settings apply ──
import main as M
played = []
v = M.VoxelApp.__new__(M.VoxelApp)
v.app = app
from src.ui.mini_player import MiniPlayer
v.tts = tts; v.player = MiniPlayer(tts); v.tray = tray; v.listener = L
v.player.play_text = lambda t, *a: played.append(t)
v._read_bridge = M._ReadBridge()
v._read_bridge.text_ready.connect(lambda t: v.player.play_text(t))
msgs = []
v._read_bridge.nothing_selected.connect(lambda: msgs.append(1))
M.foreground.restore = lambda: True
M.grab_selected_text = lambda timeout_ms=0, persistent=True: "Text the user selected in their browser"
v._on_tray_read_selection()
end = time.time() + 1.5
while time.time() < end and not played: app.processEvents(); time.sleep(0.02)
check("tray 'Read selected text' plays the selection", played == ["Text the user selected in their browser"])
M.grab_selected_text = lambda timeout_ms=0, persistent=True: ""
v._on_tray_read_selection()
end = time.time() + 1.5
while time.time() < end and not msgs: app.processEvents(); time.sleep(0.02)
check("nothing selected -> friendly message, no crash", msgs == [1])
v._apply_initial_settings = lambda: None
try:
    v._on_settings_applied(); ok = True
except Exception as e:
    print("settings error:", e); ok = False
check("settings apply without error (tray enable_action)", ok)

for n, ok in results: print(("PASS " if ok else "FAIL ") + n)
print(f"\n{sum(ok for _, ok in results)}/{len(results)} passed")
