"""Checks that Voxel stays out of the way: text-box detection, typing back-off, single copy. Run: python tests/test_selection_guard.py"""
import os, sys, time, ctypes, threading
repo = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, repo); os.chdir(repo)
from PyQt6.QtWidgets import QApplication
app = QApplication(sys.argv)
results = []
def check(n, c): results.append((n, bool(c)))

# 1. Windows: real native text controls
from src.utils.focus_guard import win_hwnd_is_input
u = ctypes.windll.user32
u.CreateWindowExW.restype = ctypes.c_void_p
parent = u.CreateWindowExW(0, "STATIC", "p", 0, 0, 0, 10, 10, None, None, None, None)
WS_CHILD = 0x40000000
single = u.CreateWindowExW(0, "EDIT", "", WS_CHILD, 0, 0, 100, 20, ctypes.c_void_p(parent), None, None, None)
multi = u.CreateWindowExW(0, "EDIT", "", WS_CHILD | 0x0004, 0, 0, 100, 60, ctypes.c_void_p(parent), None, None, None)
button = u.CreateWindowExW(0, "BUTTON", "ok", WS_CHILD, 0, 0, 50, 20, ctypes.c_void_p(parent), None, None, None)
check("single-line Edit = text box (skip)", win_hwnd_is_input(single))
check("multi-line Edit = document (keep)", not win_hwnd_is_input(multi))
check("button = not a text box", not win_hwnd_is_input(button))
check("no window = not a text box", not win_hwnd_is_input(None))

# 2. Listener decisions (copy/grab stubbed, nothing is typed on this PC)
import src.selection_listener as SL
from src.utils import settings as S
SET = {"skip_text_fields": True}
S.settings_db.get = lambda k, d=None: SET.get(k, d)
calls = {"grab": [], "emit": []}
in_box = {"v": False}
SL.is_typing_in_text_box = lambda: in_box["v"]
SL._is_screenshot_app_active = lambda: False
def fake_grab(timeout_ms=0, persistent=True):
    calls["grab"].append(persistent); return "Some selected text"
SL.grab_selected_text = fake_grab
L = SL.SelectionListener()
L.text_selected.connect(lambda *a: calls["emit"].append(a))

def run(prep=None, type_during_wait=False):
    calls["grab"].clear(); calls["emit"].clear()
    released = time.time()
    if prep: prep()
    if type_during_wait:
        threading.Timer(0.05, lambda: setattr(L, "_last_key_time", time.time())).start()
    L._handle_possible_selection(10, 10, 0, 0, released)
    app.processEvents()
    return list(calls["grab"]), list(calls["emit"])

g, e = run()
check("normal selection -> bubble", g and e)
check("automatic copy is a single gentle one (persistent=False)", g == [False])
in_box["v"] = True
g, e = run()
check("inside a search/form box -> no copy, no bubble", not g and not e)
SET["skip_text_fields"] = False
g, e = run()
check("setting off -> works in text boxes again", g and e)
SET["skip_text_fields"] = True; in_box["v"] = False
g, e = run(type_during_wait=True)
check("user starts typing right away -> no copy, no bubble", not g and not e)
g, e = run(prep=lambda: setattr(L, "_press_time", time.time() + 0.01))
check("user clicks again right away -> no copy, no bubble", not g and not e)

# 3. clipboard module signature
import inspect
from src.utils import clipboard as C
check("hotkey path keeps retries (persistent default True)", inspect.signature(C.grab_selected_text).parameters["persistent"].default is True)
src = inspect.getsource(C._simulate_copy_mac)
check("mac sends Cmd+C once (one event tap)", src.count("CGEventPost(") == 2 and "kCGSessionEventTap, down" not in src)

for n, ok in results: print(("PASS " if ok else "FAIL ") + n)
print(f"\n{sum(ok for _, ok in results)}/{len(results)} passed")
