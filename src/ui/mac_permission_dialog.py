"""
macOS Accessibility Permission Guidance Dialog for Voxel.
Displays an interactive helper window with a 1-click button to open System Settings,
and live-polls for permission approval so the app activates automatically without restarting.
"""
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QCursor

from src.config import THEME, FONT_FAMILY
from src.utils.mac_permissions import is_accessibility_trusted, open_accessibility_settings
from assets.icons import get_selection_bubble_pixmap


class MacPermissionDialog(QDialog):
    """
    Modern modal dialog guiding macOS users to grant Accessibility permissions.
    Auto-detects when the user toggles the switch in System Settings.
    """
    permission_granted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Voxel — macOS Permission Required")
        self.setFixedSize(460, 360)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #0F172A;
                color: #F8FAFC;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.12);
                font-family: {FONT_FAMILY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(16)

        # Header with Logo & Title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        logo_label = QLabel(self)
        logo_pix = get_selection_bubble_pixmap(44)
        if logo_pix and not logo_pix.isNull():
            logo_label.setPixmap(logo_pix)
        logo_label.setFixedSize(44, 44)
        header_layout.addWidget(logo_label)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        title_label = QLabel("Enable Text Selection on macOS", self)
        title_font = QFont(FONT_FAMILY, 15, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #FFFFFF;")

        sub_label = QLabel("Required for Floating Bubble & Document Reading", self)
        sub_font = QFont(FONT_FAMILY, 11)
        sub_label.setFont(sub_font)
        sub_label.setStyleSheet("color: #94A3B8;")

        title_vbox.addWidget(title_label)
        title_vbox.addWidget(sub_label)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Instruction Card
        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        step1 = QLabel("1. Click the button below to open <b>Privacy & Security</b>.", self)
        step2 = QLabel("2. Find <b>Voxel</b> under Accessibility and switch it <b>ON</b>.", self)
        step3 = QLabel("3. This dialog will detect it and close automatically!", self)
        for s in [step1, step2, step3]:
            s.setStyleSheet("color: #E2E8F0; font-size: 12px; line-height: 1.4;")
            card_layout.addWidget(s)

        layout.addWidget(card)

        # Live Status Indicator
        self.status_label = QLabel("Waiting for permission in System Settings...", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 500;")
        layout.addWidget(self.status_label)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_open = QPushButton("Open Accessibility Settings", self)
        self.btn_open.setFixedHeight(40)
        self.btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_open.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7441F9, stop:1 #00F0FF);
                color: #FFFFFF;
                font-weight: 600;
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
        btn_layout.addWidget(self.btn_open)

        self.btn_close = QPushButton("Later", self)
        self.btn_close.setFixedSize(70, 40)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #94A3B8;
                font-size: 12px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.10);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.14);
                color: #FFFFFF;
            }
        """)
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # Polling Timer to auto-detect permission grant
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(1200)
        self.poll_timer.timeout.connect(self._check_permission)
        self.poll_timer.start()

    def _on_open_clicked(self):
        open_accessibility_settings()
        self.status_label.setText("Checking System Settings...")
        self.status_label.setStyleSheet("color: #F59E0B; font-size: 11px;")

    def _check_permission(self):
        if is_accessibility_trusted(prompt=False):
            self.poll_timer.stop()
            self.status_label.setText("✓ Permission Granted! Starting Voxel...")
            self.status_label.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12px;")
            self.btn_open.setText("✓ Ready")
            self.btn_open.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;
                    color: #FFFFFF;
                    font-weight: 600;
                    border-radius: 10px;
                    border: none;
                }
            """)
            self.permission_granted.emit()
            QTimer.singleShot(1200, self.accept)
