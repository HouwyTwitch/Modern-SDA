import sys
import json
import os
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy,
    QSpacerItem, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QStackedWidget, QButtonGroup, QComboBox, QFileDialog,
    QAbstractItemView, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QByteArray
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QIcon
from PyQt5.QtSvg import QSvgRenderer
from urllib.request import urlopen
from urllib.error import URLError

# Import account management classes
from src.account_manager import AccountData, AccountManager, AuthenticationManager, ConfirmationManager
from src.theme import ThemeManager, NoctuaTheme, ThemedComboBox
from src.settings import SettingsManager


class SettingsScreen(QWidget):
    """Screen for application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.theme_combo = None
        self.auto_refresh_checkbox = None
        self.refresh_interval_spinbox = None
        self.copy_on_click_checkbox = None
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

        auth_section_label = QLabel("Auth Code")
        auth_section_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        auth_section_label.setStyleSheet(
            f"color: {ThemeManager.get_current_theme().TEXT_PRIMARY};"
        )
        settings_layout.addWidget(auth_section_label)

        auto_refresh_layout = QHBoxLayout()
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh code")
        self.auto_refresh_checkbox.setChecked(
            SettingsManager.get_setting("auto_refresh_enabled")
        )
        self.auto_refresh_checkbox.stateChanged.connect(self.on_auto_refresh_changed)
        auto_refresh_layout.addWidget(self.auto_refresh_checkbox)
        auto_refresh_layout.addStretch()
        settings_layout.addLayout(auto_refresh_layout)

        refresh_interval_layout = QHBoxLayout()
        refresh_interval_label = QLabel("Refresh interval (seconds):")
        refresh_interval_label.setFont(QFont("Segoe UI", 12))
        refresh_interval_label.setStyleSheet(
            f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};"
        )
        refresh_interval_layout.addWidget(refresh_interval_label)

        self.refresh_interval_spinbox = QSpinBox()
        self.refresh_interval_spinbox.setRange(1, 60)
        self.refresh_interval_spinbox.setValue(
            SettingsManager.get_setting("auto_refresh_interval_seconds")
        )
        self.refresh_interval_spinbox.setSuffix(" sec")
        self.refresh_interval_spinbox.valueChanged.connect(
            self.on_refresh_interval_changed
        )
        refresh_interval_layout.addWidget(self.refresh_interval_spinbox)
        refresh_interval_layout.addStretch()
        settings_layout.addLayout(refresh_interval_layout)

        copy_layout = QHBoxLayout()
        self.copy_on_click_checkbox = QCheckBox("Click code to copy")
        self.copy_on_click_checkbox.setChecked(
            SettingsManager.get_setting("copy_code_on_click")
        )
        self.copy_on_click_checkbox.stateChanged.connect(
            self.on_copy_on_click_changed
        )
        copy_layout.addWidget(self.copy_on_click_checkbox)
        copy_layout.addStretch()
        settings_layout.addLayout(copy_layout)

        self.refresh_interval_spinbox.setEnabled(
            SettingsManager.get_setting("auto_refresh_enabled")
        )
        self.update_control_styles()
        
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
        self.update_control_styles()

    def update_control_styles(self):
        """Update styles for additional settings controls."""
        current_theme = ThemeManager.get_current_theme()
        checkbox_style = f"""
            QCheckBox {{
                color: {current_theme.TEXT_PRIMARY};
                font-size: 14px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {current_theme.BORDER};
                background-color: {current_theme.SURFACE_ELEVATED};
            }}
            QCheckBox::indicator:checked {{
                background-color: {current_theme.ACCENT};
                border-color: {current_theme.BORDER_FOCUS};
            }}
        """
        spinbox_style = f"""
            QSpinBox {{
                background-color: {current_theme.SURFACE};
                border: 2px solid {current_theme.BORDER};
                border-radius: 8px;
                padding: 6px 10px;
                color: {current_theme.TEXT_PRIMARY};
                min-width: 90px;
            }}
            QSpinBox:focus {{
                border-color: {current_theme.BORDER_FOCUS};
            }}
        """
        if self.auto_refresh_checkbox:
            self.auto_refresh_checkbox.setStyleSheet(checkbox_style)
        if self.copy_on_click_checkbox:
            self.copy_on_click_checkbox.setStyleSheet(checkbox_style)
        if self.refresh_interval_spinbox:
            self.refresh_interval_spinbox.setStyleSheet(spinbox_style)
    
    def on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        if ThemeManager.set_theme(theme_name):
            SettingsManager.set_setting("theme", theme_name)
            # Update the entire application with new theme
            if self.parent_window:
                self.parent_window.apply_theme()

    def on_auto_refresh_changed(self, state: int):
        """Toggle auto-refresh setting."""
        enabled = state == Qt.Checked
        SettingsManager.set_setting("auto_refresh_enabled", enabled)
        if self.refresh_interval_spinbox:
            self.refresh_interval_spinbox.setEnabled(enabled)
        if self.parent_window and hasattr(self.parent_window, "apply_settings"):
            self.parent_window.apply_settings()

    def on_refresh_interval_changed(self, value: int):
        """Update refresh interval setting."""
        SettingsManager.set_setting("auto_refresh_interval_seconds", value)
        if self.parent_window and hasattr(self.parent_window, "apply_settings"):
            self.parent_window.apply_settings()

    def on_copy_on_click_changed(self, state: int):
        """Toggle copy-on-click setting."""
        SettingsManager.set_setting("copy_code_on_click", state == Qt.Checked)
        if self.parent_window and hasattr(self.parent_window, "apply_settings"):
            self.parent_window.apply_settings()
