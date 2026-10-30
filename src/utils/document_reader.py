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

IS_MAC = sys.platform == "darwin"
MODIFIER_KEY = keyboard.Key.cmd if IS_MAC else keyboard.Key.ctrl

_kb_controller = keyboard.Controller()


def capture_full_document_from_active_window(timeout_ms: int = 450) -> str:
    """
    Simulates select-all (Ctrl+A / Cmd+A) and copy (Ctrl+C / Cmd+C)
    in the currently active application window (e.g. Google Docs, Word,
    PDF viewer, Google Slides presentation).
    
    Captures the full document text, preserves the user's prior clipboard,
    and returns the extracted text ready for narration.
    """
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

    time.sleep(0.04)

    # 1. Simulate Select All (Ctrl+A / Cmd+A)
    try:
        with _kb_controller.pressed(MODIFIER_KEY):
            time.sleep(0.02)
            _kb_controller.press("a")
            time.sleep(0.02)
            _kb_controller.release("a")
            time.sleep(0.03)

        # 2. Simulate Copy (Ctrl+C / Cmd+C)
        with _kb_controller.pressed(MODIFIER_KEY):
            time.sleep(0.02)
            _kb_controller.press("c")
            time.sleep(0.02)
            _kb_controller.release("c")
            time.sleep(0.03)
    except Exception as e:
        print(f"[DocumentReader] Keystroke simulation error: {e}")

    # Fallback to AppleScript on macOS
    if IS_MAC:
        try:
            subprocess.run(
                [
                    "osascript", "-e",
                    'tell application "System Events" to keystroke "a" using {command down}\n'
                    'delay 0.05\n'
                    'tell application "System Events" to keystroke "c" using {command down}'
                ],
                timeout=0.6,
                capture_output=True
            )
        except Exception:
            pass

    # 3. Poll clipboard for document contents
    start_time = time.time()
    new_text = ""
    max_wait = timeout_ms / 1000.0

    while time.time() - start_time < max_wait:
        time.sleep(0.025)
        try:
            curr = pyperclip.paste()
            if curr != sentinel:
                new_text = curr
                break
        except Exception:
            continue

    # 4. Deselect text so the document returns to normal visual state (press right arrow or escape)
    try:
        _kb_controller.press(keyboard.Key.right)
        time.sleep(0.01)
        _kb_controller.release(keyboard.Key.right)
    except Exception:
        pass

    # 5. Restore user's previous clipboard text
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
