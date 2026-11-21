"""Off-screen UI regression checks for the redesign. Run: python tests/test_stage2_ui.py (uses demo settings; plays a short quiet voice sample)."""
import os, sys, traceback
repo = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo); os.chdir(repo)
from PyQt6.QtWidgets import QApplication, QMenu
from PyQt6.QtCore import Qt, QTimer
app = QApplication(sys.argv)

from src.utils import settings as S
DEMO = {"settings_theme": "light", "bubble_appearance": "Transparent", "bubble_size": "Medium", "volume": 64,
        "default_speed": 1.2, "selection_popup_enabled": True, "ui_last_page": "history"}
S.settings_db.get = lambda k, d=None: DEMO.get(k, d)
S.settings_db.set = lambda k, v: DEMO.__setitem__(k, v)
from src.utils import history as H
H.history_db.get_all = lambda: [{"timestamp": "t", "voice": "Jenny", "speed": 1.0, "text": "History text", "preview": "History text"}]
H.history_db.clear = lambda: None
import src.ui.settings_dialog as SD
STARTUP = {"on": False}
SD.is_startup_enabled = lambda: STARTUP["on"]
SD.set_startup_enabled = lambda v: STARTUP.__setitem__("on", v)
SD.QMessageBox.question = staticmethod(lambda *a, **k: SD.QMessageBox.StandardButton.Yes)

from src.tts_engine import TTSEngine
from src.ui.mini_player import MiniPlayer
from src.ui.tray_icon import AppTrayIcon

results = []
def check(name, cond):
    results.append((name, bool(cond)))

def pump(n=5):
    for _ in range(n): app.processEvents()

tts = TTSEngine(); tts.set_volume(0.2)
d = SD.SettingsDialog(tts_engine=tts)
d.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
player = MiniPlayer(tts); player.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
d.read_text_requested.connect(player.play_text)
applied = []
d.settings_applied.connect(lambda: applied.append(1))
d.show(); pump()

# navigation + last page memory
check("opens on remembered page (history)", d.stacked_pages.currentIndex() == d.PAGE_HISTORY)
for p in range(5):
    d._go_to(p); pump()
check("history list shows entry", d.list_history.count() == 1)
check("last page remembered", DEMO["ui_last_page"] == "settings")

# settings kept from saved values
check("legacy bubble style kept on load", d.current_bubble_style == "Transparent")
check("bubble size loaded", d.seg_bubble_size.value() == "Medium")
check("volume loaded (engine saved 20)", d.slider_volume.value() == 20)
check("speed loaded", d.slider_speed.value() == 120)

# instant apply (no save button)
d.slider_volume.setValue(70); d.chk_prebuffer.setChecked(False)
QTimer.singleShot(600, app.quit); app.exec()
check("autosave volume", DEMO.get("volume") == 70)
check("autosave toggle", DEMO.get("prebuffer_enabled") is False)
check("settings_applied emitted", len(applied) >= 1)
check("legacy style untouched by other changes", DEMO.get("bubble_appearance") == "Transparent")
check("no Save changes button", not any(b.text().strip().lower().startswith("save changes") for b in d.findChildren(SD.QPushButton)))

# listen toggle <-> settings toggle sync
d.sw_listen_selection.setChecked(False); pump()
check("listen toggle syncs settings", d.chk_trigger.isChecked() is False)
d.chk_trigger.setChecked(True); pump()
check("settings toggle syncs listen", d.sw_listen_selection.isChecked() is True)

# startup only written when changed
d.chk_startup.setChecked(True)
QTimer.singleShot(600, app.quit); app.exec()
check("startup applied", STARTUP["on"] is True)

# themes
for pref in ("dark", "system", "light"):
    d.apply_theme(pref); pump()
    check(f"theme {pref} saved", DEMO["settings_theme"] == pref)

# sidebar collapse
d._set_sidebar_collapsed(True, remember=True); pump()
check("sidebar collapses", d.sidebar_widget.width() == 64 and DEMO.get("ui_sidebar_collapsed") is True)
d._set_sidebar_collapsed(False, remember=True)

# reset to defaults
d.reset_to_defaults(); pump()
check("reset volume", DEMO.get("volume") == 80)
check("reset style", DEMO.get("bubble_appearance") == "Frosted Glass")

# folds open/close
f = d._folds[0]; f.header.setChecked(True); pump()
check("advanced section opens", f.body.isVisibleTo(d))

# open_* API
d.open_about(); pump(); check("open_about -> settings", d.stacked_pages.currentIndex() == d.PAGE_SETTINGS)
d.open_reader("hello"); pump(); check("open_reader", d.stacked_pages.currentIndex() == d.PAGE_READ and d.txt_reader.toPlainText() == "hello")
d.open_history(); pump(); check("open_history", d.stacked_pages.currentIndex() == d.PAGE_HISTORY)
d.open_main(); pump(); check("open_main -> last page", d.stacked_pages.currentIndex() == d.PAGE_HISTORY)

# read / pause / resume / stop with the real engine (through the mini player, like the app)
ev = []
tts.playback_started.connect(lambda: ev.append("started"))
tts.playback_paused.connect(lambda: ev.append("paused"))
tts.playback_resumed.connect(lambda: ev.append("resumed"))
d.open_reader("Voxel stage two test. This sentence is long enough to pause and resume while it is being read aloud.")
d._toggle_read()
def step1():
    check("mini player shown", player.isVisible())
    check("read button shows Stop", d.btn_read.text().strip() == "Stop")
    d._toggle_pause()
    QTimer.singleShot(600, step2)
def step2():
    check("pause button shows Resume", d.btn_reader_pause.text().strip() == "Resume")
    d._toggle_pause()
    QTimer.singleShot(600, step3)
def step3():
    d._toggle_read()  # stop
    QTimer.singleShot(400, step4)
def step4():
    check("stopped -> Read aloud", d.btn_read.text().strip() == "Read aloud" and not tts.is_speaking)
    app.quit()
def wait_started(tries=[0]):
    if "started" in ev: QTimer.singleShot(800, step1)
    elif tries[0] > 60: check("tts started", False); app.quit()
    else:
        tries[0] += 1; QTimer.singleShot(250, wait_started)
QTimer.singleShot(250, wait_started); app.exec()
check("tts events", ev[:1] == ["started"] and "paused" in ev and "resumed" in ev)

# mini player pieces
player.apply_theme("dark_glass"); player.apply_theme("light_glass")
player._on_speed_selected(1.5)
check("speed button", player.btn_speed.text() == "1.5×")
check("mini player compact", player.width() <= 300)
player._on_chunk_progress(2, 4); check("progress shown", abs(player._progress - 0.5) < 1e-6)
player._toggle_recording(); check("recording state", player.is_recording and player.lbl_brand.text() == "Recording")
player._toggle_recording(); check("recording stops", not player.is_recording)

# tray
tray = AppTrayIcon(tts)
labels = [a.text() for a in tray.contextMenu().actions() if a.text()]
check("tray has Open/Read/History/Settings", all(x in labels for x in ["Open Voxel", "Read Text...", "History", "Settings"]))

fails = [n for n, ok in results if not ok]
for n, ok in results:
    print(("PASS " if ok else "FAIL ") + n)
print(f"\n{len(results) - len(fails)}/{len(results)} passed")
sys.exit(1 if fails else 0)
