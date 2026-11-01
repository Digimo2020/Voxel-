"""
macOS Accessibility Permission Guidance Dialog for Voxel.
Displays an interactive helper window with a 1-click button to open System Settings,
crystal-clear high-contrast readable steps, auto-polling, restart, and test bubble actions.
"""
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QCursor

from src.config import THEME, FONT_FAMILY
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings, restart_voxel_app
from assets.icons import get_selection_bubble_pixmap


class MacPermissionDialog(QDialog):
    """
    Modern modal dialog guiding macOS users to grant Accessibility permissions.
    Provides clear readable typography, live polling, restart, and bubble testing.
    """
    permission_granted = pyqtSignal()
    test_bubble_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Voxel — Enable Text Selection on macOS")
        self.setFixedSize(500, 420)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #0F172A;
                color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.16);
                font-family: {FONT_FAMILY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 22)
        layout.setSpacing(14)

        # Header with Logo & Title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        logo_label = QLabel(self)
        logo_pix = get_selection_bubble_pixmap(48)
        if logo_pix and not logo_pix.isNull():
            logo_label.setPixmap(logo_pix)
        logo_label.setFixedSize(48, 48)
        header_layout.addWidget(logo_label)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(3)
        title_label = QLabel("Enable Text Selection on macOS", self)
        title_label.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFFFFF; font-weight: 700;")

        sub_label = QLabel("Required for Floating Bubble & Full Document Reading", self)
        sub_label.setFont(QFont(FONT_FAMILY, 11))
        sub_label.setStyleSheet("color: #94A3B8;")

        title_vbox.addWidget(title_label)
        title_vbox.addWidget(sub_label)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # High-Contrast Instruction Card
        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                padding: 10px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(14, 12, 14, 12)

        def make_step(num_str: str, main_text: str, badge_color: str) -> QHBoxLayout:
            row = QHBoxLayout()
            row.setSpacing(12)
            badge = QLabel(num_str, card)
            badge.setFixedSize(24, 24)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet(f"""
                background-color: {badge_color};
                color: #FFFFFF;
                font-weight: 800;
                font-size: 12px;
                border-radius: 12px;
            """)
            row.addWidget(badge)

            lbl = QLabel(main_text, card)
            lbl.setStyleSheet("color: #F8FAFC; font-size: 13px; font-weight: 500;")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            row.addWidget(lbl)
            row.addStretch()
            return row

        card_layout.addLayout(make_step("1", "Click <b>Open Accessibility Settings</b> below.", "#7C3AED"))
        card_layout.addLayout(make_step("2", "Find <b>Voxel</b> under Accessibility and switch it <span style='color: #38BDF8; font-weight: bold;'>ON</span>.", "#0284C7"))
        card_layout.addLayout(make_step("3", "Click <b>Restart Voxel</b> if macOS asks to apply permissions.", "#10B981"))

        layout.addWidget(card)

        # Live Status Indicator
        self.status_label = QLabel("Waiting for permission in System Settings...", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.status_label)

        # Main Action Buttons (Row 1)
        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(10)

        self.btn_open = QPushButton("⚙️  Open Accessibility Settings", self)
        self.btn_open.setFixedHeight(40)
        self.btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_open.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7441F9, stop:1 #00F0FF);
                color: #FFFFFF;
                font-weight: 700;
                font-size: 13px;
                border-radius: 10px;
                border: none;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #38BDF8);
            }
            QPushButton:pressed {
                background: #6366F1;
            }
        """)
        self.btn_open.clicked.connect(self._on_open_clicked)
        btn_row1.addWidget(self.btn_open)

        self.btn_restart = QPushButton("🔄 Restart Voxel", self)
        self.btn_restart.setFixedHeight(40)
        self.btn_restart.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_restart.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 13px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                padding: 0 14px;
            }
            QPushButton:hover {
                background-color: #475569;
                color: #FFFFFF;
            }
        """)
        self.btn_restart.clicked.connect(self._on_restart_clicked)
        btn_row1.addWidget(self.btn_restart)

        layout.addLayout(btn_row1)

        # Secondary Actions (Row 2)
        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(10)

        self.btn_test = QPushButton("🎯 Test Floating Bubble", self)
        self.btn_test.setFixedHeight(36)
        self.btn_test.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_test.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #38BDF8;
                font-size: 12px;
                font-weight: 600;
                border-radius: 8px;
                border: 1px solid rgba(56, 189, 248, 0.3);
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: rgba(56, 189, 248, 0.15);
                color: #7DD3FC;
            }
        """)
        self.btn_test.clicked.connect(self._on_test_clicked)
        btn_row2.addWidget(self.btn_test)

        btn_row2.addStretch()

        self.btn_close = QPushButton("Later", self)
        self.btn_close.setFixedSize(70, 36)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.06);
                color: #94A3B8;
                font-size: 12px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.12);
                color: #FFFFFF;
            }
        """)
        self.btn_close.clicked.connect(self.reject)
        btn_row2.addWidget(self.btn_close)

        layout.addLayout(btn_row2)

        # Polling Timer to auto-detect permission grant
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(1200)
        self.poll_timer.timeout.connect(self._check_permission)
        self.poll_timer.start()

    def _on_open_clicked(self):
        open_accessibility_settings()
        self.status_label.setText("Opened System Settings. Toggle Voxel to ON...")
        self.status_label.setStyleSheet("color: #F59E0B; font-size: 12px; font-weight: 600;")

    def _on_restart_clicked(self):
        self.status_label.setText("Restarting Voxel...")
        self.status_label.setStyleSheet("color: #10B981; font-weight: 700;")
        QTimer.singleShot(400, restart_voxel_app)

    def _on_test_clicked(self):
        self.test_bubble_requested.emit()

    def _check_permission(self):
        if is_accessibility_trusted(prompt=False):
            self.poll_timer.stop()
            self.status_label.setText("✓ Permission Granted! Voxel is active.")
            self.status_label.setStyleSheet("color: #10B981; font-weight: 700; font-size: 13px;")
            self.btn_open.setText("✓ Ready")
            self.btn_open.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;
                    color: #FFFFFF;
                    font-weight: 700;
                    font-size: 13px;
                    border-radius: 10px;
                    border: none;
                }
            """)
            self.permission_granted.emit()
            QTimer.singleShot(1400, self.accept)
