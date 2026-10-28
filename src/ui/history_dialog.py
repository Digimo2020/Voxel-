"""
History Dialog displaying recent spoken texts stored in history.json.
Allows users to replay past clips, copy text, or clear history.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
import pyperclip

from src.config import THEME
from src.utils.history import history_db


class HistoryDialog(QDialog):
    replay_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Text 2 Voice - History")
        self.setFixedSize(480, 420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME["bg_player"]};
                color: {THEME["text_primary"]};
            }}
            QListWidget {{
                background-color: #181825;
                border: 1px solid {THEME["border_player"]};
                border-radius: 8px;
                padding: 6px;
                color: {THEME["text_primary"]};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #313244;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: #313244;
            }}
            QListWidget::item:selected {{
                background-color: #45475A;
                color: #FFFFFF;
            }}
            QPushButton {{
                background-color: {THEME["button_bg"]};
                color: {THEME["text_primary"]};
                border: 1px solid {THEME["border_player"]};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME["button_hover"]};
            }}
        """)

        self._init_ui()
        self.load_history()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title
        title = QLabel("📜 Spoken History (JSON Storage)", self)
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # List Widget
        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self._on_replay)
        layout.addWidget(self.list_widget)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_replay = QPushButton("▶ Replay", self)
        self.btn_replay.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_replay.setStyleSheet(f"background-color: {THEME['accent']}; color: #11111B;")
        self.btn_replay.clicked.connect(self._on_replay)
        btn_layout.addWidget(self.btn_replay)

        self.btn_copy = QPushButton("📋 Copy Text", self)
        self.btn_copy.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_copy.clicked.connect(self._on_copy)
        btn_layout.addWidget(self.btn_copy)

        self.btn_clear = QPushButton("🗑 Clear All", self)
        self.btn_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_clear.clicked.connect(self._on_clear)
        btn_layout.addWidget(self.btn_clear)

        btn_layout.addStretch()

        btn_close = QPushButton("Close", self)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def load_history(self):
        self.list_widget.clear()
        entries = history_db.get_all()
        if not entries:
            item = QListWidgetItem("No speech history yet. Highlight any text to begin!")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            return

        for e in entries:
            ts = e.get("timestamp", "")
            preview = e.get("preview", "")
            voice = e.get("voice", "")
            speed = e.get("speed", 1.0)
            text = f"[{ts}] {preview}\n   Voice: {voice} | Speed: {speed}x"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, e.get("text", ""))
            self.list_widget.addItem(item)

    def _on_replay(self):
        item = self.list_widget.currentItem()
        if item:
            full_text = item.data(Qt.ItemDataRole.UserRole)
            if full_text:
                self.replay_requested.emit(full_text)
                self.close()

    def _on_copy(self):
        item = self.list_widget.currentItem()
        if item:
            full_text = item.data(Qt.ItemDataRole.UserRole)
            if full_text:
                pyperclip.copy(full_text)
                QMessageBox.information(self, "Copied", "Text copied to clipboard!")

    def _on_clear(self):
        history_db.clear()
        self.load_history()
