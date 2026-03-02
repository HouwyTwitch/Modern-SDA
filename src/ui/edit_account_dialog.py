from typing import Dict
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.theme import ThemeManager
from src.account_manager import AccountData


class EditAccountDialog(QDialog):
    """Dialog for editing an existing account"""

    def __init__(self, account: AccountData, parent=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("Edit Steam Account")
        self.setFixedSize(480, 470)
        self.setModal(True)
        self.mafile_path = account.mafile_path
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("Edit Steam Account")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form_container = QFrame()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(24, 24, 24, 24)

        mafile_section = QVBoxLayout()
        mafile_section.setSpacing(8)

        mafile_label = QLabel("Mafile Location:")
        mafile_label.setFont(QFont("Segoe UI", 13, QFont.Medium))
        mafile_section.addWidget(mafile_label)

        mafile_row = QHBoxLayout()
        mafile_row.setSpacing(12)

        self.mafile_display = QLineEdit()
        self.mafile_display.setReadOnly(True)
        self.mafile_display.setMinimumHeight(48)
        self.mafile_display.setText(os.path.basename(self.mafile_path))
        mafile_row.addWidget(self.mafile_display, 1)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setMinimumHeight(48)
        self.browse_button.setFixedWidth(90)
        self.browse_button.clicked.connect(self.browse_mafile)
        mafile_row.addWidget(self.browse_button)

        mafile_section.addLayout(mafile_row)
        form_layout.addLayout(mafile_section)

        password_section = QVBoxLayout()
        password_section.setSpacing(8)

        password_label = QLabel("Account Password:")
        password_label.setFont(QFont("Segoe UI", 13, QFont.Medium))
        password_section.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Leave blank to keep current password...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(48)
        password_section.addWidget(self.password_input)

        toggle_layout = QHBoxLayout()
        toggle_layout.setContentsMargins(0, 4, 0, 0)

        self.show_password_checkbox = QPushButton("👁 Show Password")
        self.show_password_checkbox.setCheckable(True)
        self.show_password_checkbox.setFixedHeight(32)
        self.show_password_checkbox.clicked.connect(self.toggle_password_visibility)
        toggle_layout.addWidget(self.show_password_checkbox)
        toggle_layout.addStretch()

        password_section.addLayout(toggle_layout)
        form_layout.addLayout(password_section)

        # Proxy section
        proxy_section = QVBoxLayout()
        proxy_section.setSpacing(8)

        proxy_label = QLabel("Proxy (optional):")
        proxy_label.setFont(QFont("Segoe UI", 13, QFont.Medium))
        proxy_section.addWidget(proxy_label)

        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://user:pass@ip:port")
        self.proxy_input.setMinimumHeight(48)
        self.proxy_input.setText(self.account.proxy)
        proxy_section.addWidget(self.proxy_input)

        form_layout.addLayout(proxy_section)

        layout.addWidget(form_container)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.clicked.connect(self.reject)

        self.save_button = QPushButton("Save Changes")
        self.save_button.setMinimumHeight(48)
        self.save_button.clicked.connect(self.accept)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def apply_theme(self):
        current_theme = ThemeManager.get_current_theme()

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {current_theme.BACKGROUND};
                color: {current_theme.TEXT_PRIMARY};
            }}
        """)

        title_label = self.findChild(QLabel)
        if title_label and title_label.text() == "Edit Steam Account":
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {current_theme.TEXT_PRIMARY};
                    background-color: transparent;
                    margin-bottom: 8px;
                }}
            """)

        form_container = self.findChild(QFrame)
        if form_container:
            form_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {current_theme.SURFACE_ELEVATED};
                    border-radius: 8px;
                    border: 1px solid {current_theme.BORDER};
                }}
            """)

        for label in self.findChildren(QLabel):
            if label.text() in ["Mafile Location:", "Account Password:", "Proxy (optional):"]:
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {current_theme.TEXT_PRIMARY};
                        background-color: transparent;
                        font-weight: 500;
                    }}
                """)

        self.mafile_display.setStyleSheet(f"""
            QLineEdit {{
                background-color: {current_theme.SURFACE};
                border: 2px solid {current_theme.BORDER};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                color: {current_theme.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {current_theme.BORDER_FOCUS};
                background-color: {current_theme.SURFACE_HOVER};
            }}
        """)

        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {current_theme.SURFACE};
                border: 2px solid {current_theme.BORDER};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                color: {current_theme.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {current_theme.BORDER_FOCUS};
                background-color: {current_theme.SURFACE_HOVER};
            }}
            QLineEdit::placeholder {{
                color: {current_theme.TEXT_TERTIARY};
            }}
        """)

        self.proxy_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {current_theme.SURFACE};
                border: 2px solid {current_theme.BORDER};
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                color: {current_theme.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {current_theme.BORDER_FOCUS};
                background-color: {current_theme.SURFACE_HOVER};
            }}
            QLineEdit::placeholder {{
                color: {current_theme.TEXT_TERTIARY};
            }}
        """)

        self.browse_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.SURFACE_HOVER};
                border: 2px solid {current_theme.BORDER};
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                color: {current_theme.TEXT_PRIMARY};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {current_theme.ACCENT};
                border-color: {current_theme.BORDER_FOCUS};
                color: {current_theme.TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {current_theme.ACCENT_PRESSED};
            }}
        """)

        self.show_password_checkbox.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {current_theme.TEXT_SECONDARY};
                font-size: 12px;
                text-align: left;
                padding: 4px 0px;
            }}
            QPushButton:hover {{
                color: {current_theme.TEXT_PRIMARY};
            }}
            QPushButton:checked {{
                color: {current_theme.ACCENT};
            }}
        """)

        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.SURFACE_ELEVATED};
                border: 2px solid {current_theme.BORDER};
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                color: {current_theme.TEXT_SECONDARY};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {current_theme.SURFACE_HOVER};
                border-color: {current_theme.BORDER_FOCUS};
                color: {current_theme.TEXT_PRIMARY};
            }}
        """)

        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.ACCENT};
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                color: {current_theme.TEXT_PRIMARY};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {current_theme.ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {current_theme.ACCENT_PRESSED};
            }}
        """)

    def browse_mafile(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Mafile")
        file_dialog.setNameFilter("Mafile (*.maFile);;All Files (*)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.mafile_path = selected_files[0]
                filename = os.path.basename(self.mafile_path)
                self.mafile_display.setText(filename)

    def toggle_password_visibility(self):
        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_checkbox.setText("🙈 Hide Password")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_checkbox.setText("👁 Show Password")

    def get_account_data(self) -> Dict[str, str]:
        return {
            'mafile_path': self.mafile_path,
            'password': self.password_input.text().strip(),
            'proxy': self.proxy_input.text().strip(),
        }
