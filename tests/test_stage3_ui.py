"""Off-screen checks for Resources: saved text, bookmarks, storage safety. Run: python tests/test_stage3_ui.py (temporary files only)."""
import os, sys, json, tempfile
repo = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo); os.chdir(repo)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
app = QApplication(sys.argv)

from src.utils import settings as S
DEMO = {"ui_last_page": "listen"}
S.settings_db.get = lambda k, d=None: DEMO.get(k, d)
S.settings_db.set = lambda k, v: DEMO.__setitem__(k, v)
from src.utils import history as H
HIST = [{"timestamp": "2026-11-21 09:14", "voice": "Jenny", "speed": 1.0, "text": "First history text about voices.", "preview": "First history text"},
        {"timestamp": "2026-11-21 09:02", "voice": "Guy", "speed": 1.2, "text": "Second history text.", "preview": "Second history text"}]
H.history_db.get_all = lambda: list(HIST)
from src.utils.library import LibraryManager
import src.ui.settings_dialog as SD
SD.is_startup_enabled = lambda: False
SD.QMessageBox.question = staticmethod(lambda *a, **k: SD.QMessageBox.StandardButton.Yes)
SD.get_recordings_dir = lambda: tempfile.mkdtemp()

results = []
def check(name, cond): results.append((name, bool(cond)))
def pump(n=4):
    for _ in range(n): app.processEvents()

tmpdir = tempfile.mkdtemp()
path = os.path.join(tmpdir, "library.json")

# ── storage unit tests ───────────────────────────────────────────────────────
lib = LibraryManager(path)
a = lib.save_text("Hello world\nsecond line")
check("save text", a and a["title"] == "Hello world" and os.path.exists(path))
b = lib.save_text("  Hello   world\nsecond line  ")
check("no duplicate for same text", b["id"] == a["id"] and len(lib.saved_texts()) == 1)
c = lib.save_text("Edited text", item_id=a["id"])
check("edit updates in place", c["id"] == a["id"] and lib.saved_texts()[0]["text"] == "Edited text")
lib.save_text("Another")
check("two texts", len(lib.saved_texts()) == 2)
lib.delete_text(a["id"])
check("delete text", len(lib.saved_texts()) == 1)
bm = lib.add_bookmark("Bookmark me", "Jenny", 1.0, "t")
lib.add_bookmark("Bookmark me")
check("bookmark no duplicate", len(lib.bookmarks()) == 1 and lib.is_bookmarked("Bookmark  me"))
lib.remove_bookmark(text="Bookmark me")
check("remove bookmark", not lib.is_bookmarked("Bookmark me"))
check("empty text ignored", lib.save_text("   ") is None and lib.add_bookmark("") is None)
lib2 = LibraryManager(path)
check("persists across restarts", len(lib2.saved_texts()) == 1)
with open(path, "w", encoding="utf-8") as f:
    f.write("{ broken json")
lib3 = LibraryManager(path)
check("corrupt file moved to .bak", os.path.exists(path + ".bak") and lib3.saved_texts() == [])
with open(path, "w", encoding="utf-8") as f:
    json.dump({"saved_texts": [{"id": "x", "text": "old"}, {"bad": 1}], "bookmarks": "nope"}, f)
lib4 = LibraryManager(path)
check("old/partial file migrated", len(lib4.saved_texts()) == 1 and lib4.bookmarks() == [])
check("history.json untouched by library", not os.path.exists(os.path.join(tmpdir, "history.json")))

# ── UI flows ─────────────────────────────────────────────────────────────────
os.remove(path)
SD.library_db = LibraryManager(path)
d = SD.SettingsDialog(tts_engine=None)
d.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
d.show(); pump()

d.open_reader("Saved from Read Text.\nMore words here.")
d._save_reader_text(); pump()
check("save button stores text", len(SD.library_db.saved_texts()) == 1)
check("save shows status", "Saved" in d.lbl_reader_status.text())
d.txt_reader.setPlainText("Saved from Read Text, edited."); d._save_reader_text()
check("second save edits same item", len(SD.library_db.saved_texts()) == 1)
d._clear_reader(); d.txt_reader.setPlainText("A new one"); d._save_reader_text()
check("after clear, save makes a new item", len(SD.library_db.saved_texts()) == 2)

d._go_to(d.PAGE_RESOURCES); d.seg_resources.changed.emit("texts"); pump()
check("resources lists saved text", d.list_texts.count() == 2 and d.list_texts.isVisibleTo(d))
d.list_texts.setCurrentRow(1); d._open_saved_text(); pump()
check("open saved text in Read Text", d.stacked_pages.currentIndex() == d.PAGE_READ and "edited" in d.txt_reader.toPlainText())

spoken = []
d.read_text_requested.connect(spoken.append)
d._go_to(d.PAGE_RESOURCES); d.list_texts.setCurrentRow(0); d._speak_item(d.list_texts)
check("read saved text aloud", spoken and spoken[-1] == "A new one")
d._delete_saved_text(); pump()
check("delete saved text", d.list_texts.count() == 1)

d._go_to(d.PAGE_HISTORY); pump()
d.list_history.setCurrentRow(0); d._history_toggle_bookmark(); pump()
check("bookmark from history", SD.library_db.is_bookmarked(HIST[0]["text"]))
check("history shows star", "★" in d.list_history.item(0).text())
check("button says Bookmarked", d.btn_hist_bookmark.text().strip() == "Bookmarked")
HIST.pop(0)  # history drops the item...
d.seg_resources.changed.emit("bookmarks"); d._go_to(d.PAGE_RESOURCES); pump()
check("bookmark survives history removal", d.list_bookmarks.count() == 1)
d._copy_item(d.list_bookmarks)
check("copy bookmark", QApplication.clipboard().text() == "First history text about voices.")
d._remove_bookmark(); pump()
check("remove bookmark from resources", d.list_bookmarks.count() == 0 and d.lbl_bookmarks_empty.isVisibleTo(d))

d.seg_resources.changed.emit("recordings"); pump()
check("recordings tab empty state", d.lbl_rec_empty.isVisibleTo(d))
check("tab remembered", DEMO.get("ui_resources_tab") == "recordings")
for theme in ("dark", "light"):
    d.apply_theme(theme); pump()
check("themes apply with new buttons", True)

fails = [n for n, ok in results if not ok]
for n, ok in results:
    print(("PASS " if ok else "FAIL ") + n)
print(f"\n{len(results) - len(fails)}/{len(results)} passed")
sys.exit(1 if fails else 0)
