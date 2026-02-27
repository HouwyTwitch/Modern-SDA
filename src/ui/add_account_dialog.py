from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QFrame, QFileDialog
)
from src.theme import ThemeManager
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import account management classes
from src.account_manager import AccountData


class AddAccountDialog(QDialog):
    """Dialog for adding a new account"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Steam Account")
        self.setFixedSize(480, 380)
        self.setModal(True)
        self.mafile_path = ""
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)
        
        # Title
        title = QLabel("Add Steam Account")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form container
        form_container = QFrame()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(24, 24, 24, 24)
        
        # Mafile selection section
        mafile_section = QVBoxLayout()
        mafile_section.setSpacing(8)
        
        mafile_label = QLabel("Mafile Location:")
        mafile_label.setFont(QFont("Segoe UI", 13, QFont.Medium))
        mafile_section.addWidget(mafile_label)
        
        # Mafile path display and browse button
        mafile_row = QHBoxLayout()
        mafile_row.setSpacing(12)
        
        self.mafile_display = QLineEdit()
        self.mafile_display.setPlaceholderText("Select mafile...")
        self.mafile_display.setReadOnly(True)
        self.mafile_display.setMinimumHeight(48)
        mafile_row.addWidget(self.mafile_display, 1)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.setMinimumHeight(48)
        self.browse_button.setFixedWidth(90)
        self.browse_button.clicked.connect(self.browse_mafile)
        mafile_row.addWidget(self.browse_button)
        
        mafile_section.addLayout(mafile_row)
        form_layout.addLayout(mafile_section)
        
        # Password section
        password_section = QVBoxLayout()
        password_section.setSpacing(8)
        
        password_label = QLabel("Account Password:")
        password_label.setFont(QFont("Segoe UI", 13, QFont.Medium))
        password_section.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter account password...")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(48)
        password_section.addWidget(self.password_input)
        
        # Show/Hide password toggle
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
        
        layout.addWidget(form_container)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.clicked.connect(self.reject)
        
        self.add_button = QPushButton("Add Account")
        self.add_button.setMinimumHeight(48)
        self.add_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        
        layout.addLayout(button_layout)
    
    def apply_theme(self):
        """Apply current theme to dialog elements"""
        current_theme = ThemeManager.get_current_theme()
        
        # Dialog background
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {current_theme.BACKGROUND};
                color: {current_theme.TEXT_PRIMARY};
            }}
        """)
        
        # Title styling
        title_label = self.findChild(QLabel)
        if title_label and title_label.text() == "Add Steam Account":
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {current_theme.TEXT_PRIMARY};
                    background-color: transparent;
                    margin-bottom: 8px;
                }}
            """)
        
        # Form container styling
        form_container = self.findChild(QFrame)
        if form_container:
            form_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {current_theme.SURFACE_ELEVATED};
                    border-radius: 8px;
                    border: 1px solid {current_theme.BORDER};
                }}
            """)
        
        # Labels styling
        for label in self.findChildren(QLabel):
            if label.text() in ["Mafile Location:", "Account Password:"]:
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {current_theme.TEXT_PRIMARY};
                        background-color: transparent;
                        font-weight: 500;
                    }}
                """)
        
        # Input fields styling
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
            QLineEdit::placeholder {{
                color: {current_theme.TEXT_TERTIARY};
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
        
        # Browse button styling
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
        
        # Show password toggle styling
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
        
        # Cancel button styling
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
        
        # Add button styling
        self.add_button.setStyleSheet(f"""
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
        """Open file dialog to select mafile"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Mafile")
        file_dialog.setNameFilter("Mafile (*.maFile);;All Files (*)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.mafile_path = selected_files[0]
                # Show only filename in display, store full path
                import os
                filename = os.path.basename(self.mafile_path)
                self.mafile_display.setText(filename)
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_checkbox.setText("🙈 Hide Password")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_checkbox.setText("👁 Show Password")
    
    def get_account_data(self):
        """Get the entered account data"""
        return {
            'mafile_path': self.mafile_path,
            'password': self.password_input.text().strip()
        }
