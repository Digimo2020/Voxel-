"""
History Dialog displaying recent spoken texts stored in history.json for Voxel.
Allows users to replay past clips, copy text, or clear history.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
import pyperclip

from src.config import THEME, APP_NAME, FONT_FAMILY
from src.utils.history import history_db


class HistoryDialog(QDialog):
    replay_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{APP_NAME} — History")
        self.setFixedSize(500, 440)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME["bg_window"]};
                color: {THEME["text_primary"]};
                font-family: {FONT_FAMILY};
            }}
            QListWidget {{
                background-color: #171B2D;
                border: 1px solid {THEME["border_window"]};
                border-radius: 8px;
                padding: 6px;
                color: {THEME["text_primary"]};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #252B44;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: #242942;
            }}
            QListWidget::item:selected {{
                background-color: #0084FF;
                color: #FFFFFF;
            }}
            QPushButton {{
                background-color: #242942;
                color: {THEME["text_primary"]};
                border: 1px solid {THEME["border_window"]};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #313859;
            }}
        """)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel(f"Recent Spoken Snippets", self)
        header.setStyleSheet("font-size: 14px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(header)

        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        # Action Buttons
        btn_layout = QHBoxLayout()

        self.btn_replay = QPushButton("▶ Replay", self)
        self.btn_replay.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_replay.setStyleSheet("background-color: #0084FF; color: #FFFFFF; border: none;")
        self.btn_replay.clicked.connect(self._replay_selected)
        btn_layout.addWidget(self.btn_replay)

        self.btn_copy = QPushButton("Copy Text", self)
        self.btn_copy.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_copy.clicked.connect(self._copy_selected)
        btn_layout.addWidget(self.btn_copy)

        self.btn_clear = QPushButton("Clear All", self)
        self.btn_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_clear.clicked.connect(self._clear_history)
        btn_layout.addWidget(self.btn_clear)

        btn_layout.addStretch()

        self.btn_close = QPushButton("Close", self)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def load_history(self):
        """Populates list with stored entries."""
        self.list_widget.clear()
        entries = history_db.get_all()

        if not entries:
            empty_item = QListWidgetItem("No recent speech history found.")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            empty_item.setForeground(QColor(148, 163, 184))
            self.list_widget.addItem(empty_item)
            return

        for entry in entries:
            ts = entry.get("timestamp", "")
            preview = entry.get("preview", "")
            voice = entry.get("voice", "")
            speed = entry.get("speed", 1.0)
            item_text = f"[{ts}] ({voice}, {speed}x)\n{preview}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, entry.get("text", ""))
            self.list_widget.addItem(item)

    def _get_current_entry_text(self) -> str:
        curr = self.list_widget.currentItem()
        if curr:
            return curr.data(Qt.ItemDataRole.UserRole) or ""
        return ""

    def _replay_selected(self):
        text = self._get_current_entry_text()
        if text:
            self.replay_requested.emit(text)
            self.close()

    def _copy_selected(self):
        text = self._get_current_entry_text()
        if text:
            try:
                pyperclip.copy(text)
            except Exception:
                pass

    def _clear_history(self):
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to delete all speech history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            history_db.clear()
            self.load_history()

    def _on_item_double_clicked(self, item):
        self._replay_selected()
