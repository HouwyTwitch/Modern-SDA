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
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QByteArray, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QIcon
from PyQt5.QtSvg import QSvgRenderer
from urllib.request import urlopen
from urllib.error import URLError
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# Import account management classes
from src.account_manager import AccountData, AccountManager, AuthenticationManager, ConfirmationManager
from src.theme import ThemeManager


class FloatingAddButton(QPushButton):
    """Floating action button for adding accounts"""
    
    def __init__(self, parent=None):
        super().__init__("+", parent)
        self.setFixedSize(56, 56)  # Square dimensions
        self.apply_styling()

        self._base_geometry = None
        self.hover_anim = QPropertyAnimation(self, b"geometry", self)
        self.hover_anim.setDuration(160)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(16)
        self.shadow_effect.setOffset(0, 6)
        self.shadow_effect.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(self.shadow_effect)
        self.shadow_anim = QPropertyAnimation(self.shadow_effect, b"blurRadius", self)
        self.shadow_anim.setDuration(160)
        self.shadow_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Add tooltip
        self.setToolTip("Add new Steam account")
    
    def apply_styling(self):
        """Apply current theme styling to the button"""
        current_theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.ACCENT};
                border: none;
                border-radius: 28px;
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

    def enterEvent(self, event):
        self._animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_hover(False)
        super().leaveEvent(event)

    def _animate_hover(self, is_hovered: bool):
        if self._base_geometry is None:
            self._base_geometry = self.geometry()
        target = self._base_geometry
        if is_hovered:
            target = target.adjusted(-4, -4, 4, 4)
            shadow_value = 22
        else:
            shadow_value = 16
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self.geometry())
        self.hover_anim.setEndValue(target)
        self.hover_anim.start()
        self.shadow_anim.stop()
        self.shadow_anim.setStartValue(self.shadow_effect.blurRadius())
        self.shadow_anim.setEndValue(shadow_value)
        self.shadow_anim.start()
