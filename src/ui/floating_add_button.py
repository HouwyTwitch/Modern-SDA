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
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QByteArray
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QIcon
from PyQt5.QtSvg import QSvgRenderer
from urllib.request import urlopen
from urllib.error import URLError

# Import account management classes
from src.account_manager import AccountData, AccountManager, AuthenticationManager, ConfirmationManager
from src.theme import ThemeManager, NoctuaTheme


class FloatingAddButton(QPushButton):
    """Floating action button for adding accounts"""
    
    def __init__(self, parent=None):
        super().__init__("+", parent)
        self.setFixedSize(56, 56)  # Square dimensions
        self.apply_styling()
        
        # Add tooltip
        self.setToolTip("Add new Steam account")
    
    def apply_styling(self):
        """Apply current theme styling to the button"""
        current_theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.ACCENT};
                border: none;
                border-radius: 12px;
                font-size: 24px;
                font-weight: bold;
                color: {current_theme.TEXT_PRIMARY};
                text-align: center;
                padding: 0px;
                line-height: 56px;
            }}
            QPushButton:hover {{
                background-color: {current_theme.ACCENT_HOVER};
                border: 2px solid {current_theme.BORDER_FOCUS};
            }}
            QPushButton:pressed {{
                background-color: {current_theme.ACCENT_PRESSED};
            }}
        """)