"""
Universal Document & Presentation Reader utility for Voxel.
Enables instant full-document reading from Google Docs, Word, PDFs, PowerPoint,
Google Slides, Notion, and web pages by capturing text from the active document window.
Also supports extracting text directly from local document files (.pdf, .txt, .md, .docx).
"""
import os
import sys
import time
import subprocess
import pyperclip
from pynput import keyboard

IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
MODIFIER_KEY = keyboard.Key.cmd if IS_MAC else keyboard.Key.ctrl

_kb_controller = keyboard.Controller()

if IS_WIN:
    import ctypes
    _user32 = ctypes.windll.user32
    VK_CONTROL = 0x11
    VK_A = 0x41
    VK_C = 0x43
    VK_RIGHT = 0x27
    KEYEVENTF_KEYUP = 0x0002
else:
    _user32 = None


def _send_key_combo_mac(keycode: int):
    """Sends a Cmd+Key combination using native macOS Quartz CoreGraphics Event Tap."""
    try:
        from Quartz.CoreGraphics import (
            CGEventCreateKeyboardEvent, CGEventSetFlags, CGEventPost,
            kCGSessionEventTap, kCGHIDEventTap, kCGEventFlagMaskCommand
        )
        down = CGEventCreateKeyboardEvent(None, keycode, True)
        up = CGEventCreateKeyboardEvent(None, keycode, False)
        CGEventSetFlags(down, kCGEventFlagMaskCommand)
        CGEventSetFlags(up, kCGEventFlagMaskCommand)
        try:
            CGEventPost(kCGSessionEventTap, down)
            time.sleep(0.025)
            CGEventPost(kCGSessionEventTap, up)
        except Exception:
            CGEventPost(kCGHIDEventTap, down)
            time.sleep(0.025)
            CGEventPost(kCGHIDEventTap, up)
        return True
    except Exception as e:
        print(f"[DocumentReader] Mac Quartz key error: {e}")
        return False


def _send_key_mac_plain(keycode: int):
    """Sends a plain keystroke (like Right Arrow) using native macOS Quartz."""
    try:
        from Quartz.CoreGraphics import (
            CGEventCreateKeyboardEvent, CGEventPost, kCGSessionEventTap, kCGHIDEventTap
        )
        down = CGEventCreateKeyboardEvent(None, keycode, True)
        up = CGEventCreateKeyboardEvent(None, keycode, False)
        try:
            CGEventPost(kCGSessionEventTap, down)
            time.sleep(0.02)
            CGEventPost(kCGSessionEventTap, up)
        except Exception:
            CGEventPost(kCGHIDEventTap, down)
            time.sleep(0.02)
            CGEventPost(kCGHIDEventTap, up)
        return True
    except Exception:
        return False


def _send_key_combo_win(vk_key: int):
    """Sends a Ctrl+Key combination using native Windows keybd_event."""
    if not _user32:
        return
    _user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.03)
    _user32.keybd_event(vk_key, 0, 0, 0)
    time.sleep(0.04)
    _user32.keybd_event(vk_key, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)
    _user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.03)


def capture_full_document_from_active_window(timeout_ms: int = 1400) -> str:
    """
    Simulates select-all (Ctrl+A / Cmd+A) and copy (Ctrl+C / Cmd+C)
    in the currently active application window (Google Docs, Word, PDF, Google Slides).
    
    Includes Canvas-aware pauses for browser-based editors, foreground window focus restoration,
    and safely restores the prior clipboard contents afterwards.
    """
    if IS_WIN and _user32:
        try:
            hwnd = _user32.GetForegroundWindow()
            if hwnd:
                _user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

    old_clip = ""
    try:
        old_clip = pyperclip.paste()
    except Exception:
        old_clip = ""

    sentinel = f"__VOXEL_DOC_SENTINEL_{time.time_ns()}__"
    try:
        pyperclip.copy(sentinel)
    except Exception:
        pass

    # Brief delay for mouse release and target window to settle
    time.sleep(0.12)

    # 1. Send Select All (Ctrl+A on Windows, Cmd+A on Mac)
    if IS_MAC:
        # Keycode 0 = 'a', Keycode 8 = 'c'
        _send_key_combo_mac(0)
        time.sleep(0.18)
        _send_key_combo_mac(8)
    elif IS_WIN and _user32:
        _send_key_combo_win(VK_A)
        # Google Docs HTML5 Canvas editor needs ~180ms to update internal selection model
        time.sleep(0.18)
        _send_key_combo_win(VK_C)
    else:
        # Cross-platform fallback via pynput
        try:
            with _kb_controller.pressed(MODIFIER_KEY):
                time.sleep(0.04)
                _kb_controller.press("a")
                time.sleep(0.05)
                _kb_controller.release("a")
            time.sleep(0.18)
            with _kb_controller.pressed(MODIFIER_KEY):
                time.sleep(0.04)
                _kb_controller.press("c")
                time.sleep(0.05)
                _kb_controller.release("c")
        except Exception as e:
            print(f"[DocumentReader] Keystroke error: {e}")

    # 2. Poll clipboard for new text
    start_time = time.time()
    new_text = ""
    max_wait = timeout_ms / 1000.0

    while time.time() - start_time < max_wait:
        time.sleep(0.04)
        try:
            curr = pyperclip.paste()
            if curr and curr != sentinel:
                new_text = curr
                break
        except Exception:
            continue

    # 3. Deselect text so the document returns to normal visual state
    if IS_MAC:
        _send_key_mac_plain(124)  # Keycode 124 = Right Arrow
    elif IS_WIN and _user32:
        _user32.keybd_event(VK_RIGHT, 0, 0, 0)
        time.sleep(0.02)
        _user32.keybd_event(VK_RIGHT, 0, KEYEVENTF_KEYUP, 0)
    else:
        try:
            _kb_controller.press(keyboard.Key.right)
            time.sleep(0.02)
            _kb_controller.release(keyboard.Key.right)
        except Exception:
            pass

    # 4. Restore user's previous clipboard text
    try:
        pyperclip.copy(old_clip)
    except Exception:
        pass

    if new_text and new_text != sentinel:
        cleaned = new_text.strip()
        if len(cleaned) >= 2:
            return cleaned

    return ""


def extract_text_from_file(file_path: str) -> str:
    """
    Extracts plain text from local files:
    - .pdf: Uses pypdf
    - .txt, .md, .csv, .log, .rtf: Plain text reading
    - .docx: XML/plain text extraction
    """
    if not file_path or not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()

    # 1. PDF Files
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            pages_text = []
            for i, page in enumerate(reader.pages):
                txt = page.extract_text()
                if txt and txt.strip():
                    pages_text.append(txt.strip())
            return "\n\n".join(pages_text)
        except Exception as e:
            print(f"[DocumentReader] PDF extraction error: {e}")
            return ""

    # 2. DOCX Files
    if ext == ".docx":
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(file_path) as z:
                xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            paragraphs = []
            for node in tree.iter():
                if node.tag.endswith("}p"):
                    texts = [t.text for t in node.iter() if t.tag.endswith("}t") and t.text]
                    if texts:
                        paragraphs.append("".join(texts))
            return "\n\n".join(paragraphs)
        except Exception as e:
            print(f"[DocumentReader] DOCX extraction error: {e}")

    # 3. Plain Text / Markdown / Code
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"[DocumentReader] File read error: {e}")
            break

    return ""
