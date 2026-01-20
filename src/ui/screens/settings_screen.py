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
from src.theme import ThemeManager, NoctuaTheme, ThemedComboBox


class SettingsScreen(QWidget):
    """Screen for application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.theme_combo = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the settings screen UI"""
        # Clear existing layout if it exists
        existing_layout = self.layout()
        if existing_layout:
            # Clear all widgets from existing layout
            while existing_layout.count():
                child = existing_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
            # Delete the layout
            existing_layout.setParent(None)
        
        # Main layout for the settings screen
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Scrollable content widget
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(20)
        
        # Settings container (original single container)
        settings_container = QFrame()
        settings_container.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.get_current_theme().SURFACE_ELEVATED};
                border-radius: 12px;
                margin: 0px;
            }}
        """)
        
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(20)
        
        # Theme setting (original content)
        theme_layout = QHBoxLayout()
        
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Segoe UI", 14, QFont.Medium))
        theme_label.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_PRIMARY};")
        theme_layout.addWidget(theme_label)
        
        # Create new combo box if it doesn't exist
        if not self.theme_combo:
            self.theme_combo = ThemedComboBox()
            self.theme_combo.addItems(ThemeManager.get_theme_names())
            self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
            # Apply initial styling immediately
            self.update_combo_style()
        
        # Update current selection
        self.theme_combo.setCurrentText(ThemeManager.current_theme)
        # Ensure styling is current
        self.update_combo_style()
        
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        settings_layout.addLayout(theme_layout)
        
        # Add the settings container to scroll layout
        scroll_layout.addWidget(settings_container)
        scroll_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    
    def update_combo_style(self):
        """Update combo box styling with current theme"""
        if self.theme_combo:
            current_theme = ThemeManager.get_current_theme()
            style = f"""
                QComboBox {{
                    background-color: {current_theme.SURFACE};
                    border: 2px solid {current_theme.BORDER};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: {current_theme.TEXT_PRIMARY};
                    min-width: 120px;
                }}
                QComboBox:focus {{
                    border-color: {current_theme.BORDER_FOCUS};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                    background-color: transparent;
                }}
                QComboBox::down-arrow {{
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid {current_theme.TEXT_SECONDARY};
                    margin-right: 8px;
                }}
                QAbstractItemView {{
                    background-color: {current_theme.SURFACE};
                    border: 2px solid {current_theme.BORDER};
                    border-radius: 8px;
                    selection-background-color: {current_theme.ACCENT};
                    selection-color: {current_theme.TEXT_PRIMARY};
                    color: {current_theme.TEXT_PRIMARY};
                    padding: 4px;
                    outline: none;
                }}
                QAbstractItemView::item {{
                    background-color: {current_theme.SURFACE};
                    color: {current_theme.TEXT_PRIMARY};
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 2px;
                    outline: none;
                }}
                QAbstractItemView::item:selected {{
                    background-color: {current_theme.ACCENT};
                    color: {current_theme.TEXT_PRIMARY};
                }}
                QAbstractItemView::item:hover {{
                    background-color: {current_theme.SURFACE_HOVER};
                    color: {current_theme.TEXT_PRIMARY};
                }}
            """
            
            # Use our custom method that properly handles the dropdown view
            if hasattr(self.theme_combo, 'setThemedStyleSheet'):
                self.theme_combo.setThemedStyleSheet(style)
            else:
                self.theme_combo.setStyleSheet(style)
    
    def on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        if ThemeManager.set_theme(theme_name):
            # Update the entire application with new theme
            if self.parent_window:
                self.parent_window.apply_theme()