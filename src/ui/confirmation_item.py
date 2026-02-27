import sys
import json
import os
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy,
    QSpacerItem, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QStackedWidget, QButtonGroup, QComboBox, QFileDialog,
    QAbstractItemView
)
from src.theme import ThemeManager, NoctuaTheme
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QByteArray
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QIcon
from PyQt5.QtSvg import QSvgRenderer
from urllib.request import urlopen
from urllib.error import URLError

# Import account management classes
from src.account_manager import AccountData, AccountManager, AuthenticationManager, ConfirmationManager


class ConfirmationItem(QWidget):
    """Widget for individual confirmation items"""
    
    # Signals for confirmation actions
    confirmation_accepted = pyqtSignal(str)  # confirmation_id
    confirmation_declined = pyqtSignal(str)  # confirmation_id
    
    def __init__(self, confirmation_type: str, description: str, confirmation_id: str = None, parent=None):
        super().__init__(parent)
        self.confirmation_type = confirmation_type
        self.description = description
        self.confirmation_id = confirmation_id or str(id(self))  # Use object id as fallback
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the confirmation item UI"""
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)
        
        # Create main container for better styling
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.get_current_theme().SURFACE};
                border: 1px solid {ThemeManager.get_current_theme().BORDER};
                border-radius: 6px;
                margin: 1px;
            }}
        """)

        # Layout for the main widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.container)
        
        # Layout for the container
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # Content section
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Confirmation type
        self.type_label = QLabel(self.confirmation_type)
        self.type_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.type_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.get_current_theme().TEXT_PRIMARY};
                background-color: transparent;
                border: none;
            }}
        """)
        self.type_label.setWordWrap(False)
        content_layout.addWidget(self.type_label)
        
        # Description
        self.desc_label = QLabel(self.description)
        self.desc_label.setFont(QFont("Segoe UI", 11))
        self.desc_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.get_current_theme().TEXT_SECONDARY};
                background-color: transparent;
                border: none;
            }}
        """)
        self.desc_label.setWordWrap(True)  # Enable word wrapping for long descriptions
        self.desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_layout.addWidget(self.desc_label)
        
        # Make content layout expandable
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(content_widget, 1)  # Give it stretch factor of 1
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Accept button with icon
        self.accept_button = QPushButton()
        self.accept_button.setFixedSize(40, 40)
        self.accept_button.setToolTip("Accept")
        accept_icon = ThemeManager.get_current_theme().create_svg_icon(
            ThemeManager.get_current_theme().get_accept_svg(),
            ThemeManager.get_current_theme().TEXT_PRIMARY,
            20
        )
        self.accept_button.setIcon(accept_icon)
        self.accept_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.get_current_theme().SUCCESS};
                border: none;
                border-radius: 4px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.get_current_theme().SUCCESS_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.get_current_theme().SUCCESS_HOVER};
            }}
        """)
        buttons_layout.addWidget(self.accept_button)

        # Decline button with icon
        self.decline_button = QPushButton()
        self.decline_button.setFixedSize(40, 40)
        self.decline_button.setToolTip("Decline")
        decline_icon = ThemeManager.get_current_theme().create_svg_icon(
            ThemeManager.get_current_theme().get_decline_svg(),
            ThemeManager.get_current_theme().TEXT_PRIMARY,
            20
        )
        self.decline_button.setIcon(decline_icon)
        self.decline_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.get_current_theme().ERROR};
                border: none;
                border-radius: 4px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.get_current_theme().ERROR_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.get_current_theme().ERROR_HOVER};
            }}
        """)
        buttons_layout.addWidget(self.decline_button)
        
        # Buttons container with fixed width to prevent squashing
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        buttons_widget.setFixedWidth(96)  # Fixed width for buttons (40+40+8+8 padding)
        layout.addWidget(buttons_widget)
    
    def connect_signals(self):
        """Connect button signals to slots"""
        self.accept_button.clicked.connect(self.on_accept_clicked)
        self.decline_button.clicked.connect(self.on_decline_clicked)
    
    def on_accept_clicked(self):
        """Handle accept button click"""
        self.confirmation_accepted.emit(self.confirmation_id)
    
    def on_decline_clicked(self):
        """Handle decline button click"""
        self.confirmation_declined.emit(self.confirmation_id)
    
    def apply_styling(self):
        """Apply current theme styling to the confirmation item"""
        current_theme = ThemeManager.get_current_theme()
        
        # Update container styling
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme.SURFACE};
                border: 1px solid {current_theme.BORDER};
                border-radius: 6px;
                margin: 1px;
            }}
        """)
        
        # Update text label styling
        self.type_label.setStyleSheet(f"""
            QLabel {{
                color: {current_theme.TEXT_PRIMARY};
                background-color: transparent;
                border: none;
            }}
        """)
        
        self.desc_label.setStyleSheet(f"""
            QLabel {{
                color: {current_theme.TEXT_SECONDARY};
                background-color: transparent;
                border: none;
            }}
        """)
        
        # Update button icons and styling
        accept_icon = current_theme.create_svg_icon(
            current_theme.get_accept_svg(),
            current_theme.TEXT_PRIMARY,
            20
        )
        self.accept_button.setIcon(accept_icon)
        self.accept_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.SUCCESS};
                border: none;
                border-radius: 4px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {current_theme.SUCCESS_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {current_theme.SUCCESS_HOVER};
            }}
        """)

        decline_icon = current_theme.create_svg_icon(
            current_theme.get_decline_svg(),
            current_theme.TEXT_PRIMARY,
            20
        )
        self.decline_button.setIcon(decline_icon)
        self.decline_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.ERROR};
                border: none;
                border-radius: 4px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {current_theme.ERROR_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {current_theme.ERROR_HOVER};
            }}
        """)