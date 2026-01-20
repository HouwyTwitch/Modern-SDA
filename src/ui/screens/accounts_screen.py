from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QScrollArea, QFrame
)
from src.theme import ThemeManager, NoctuaTheme
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QClipboard
from PyQt5.QtWidgets import QApplication

# Import account management classes
from src.account_manager import AccountData
from src.settings import SettingsManager
from src.theme import ThemeManager
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QClipboard
from PyQt5.QtWidgets import QApplication

# Import account management classes
from src.account_manager import AccountData


class AccountsScreen(QWidget):
    """Screen for displaying and managing accounts"""
    
    # Signal for when the auth code label is clicked
    code_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.selected_account = None
        self.refresh_timer = None
        self.copy_on_click_enabled = SettingsManager.get_setting("copy_code_on_click")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the accounts screen UI"""
        current_theme = ThemeManager.get_current_theme()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(12)
        
        # Title - SDA (will show auth code when account selected)
        self.title_label = QLabel("SDA")
        self.title_label.setFont(QFont("Segoe UI", 26, QFont.Bold))
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {current_theme.TEXT_PRIMARY};
                margin-bottom: 4px;
            }}
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        # Make the label clickable for clipboard copy
        self.title_label.setCursor(Qt.PointingHandCursor)
        self.title_label.mousePressEvent = self.on_code_clicked
        header_layout.addWidget(self.title_label)
        
        # Subtitle - account selection status
        self.subtitle_label = QLabel("No account was selected")
        self.subtitle_label.setFont(QFont("Segoe UI", 12))
        self.subtitle_label.setStyleSheet(f"color: {current_theme.TEXT_SECONDARY};")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by account name or Steam ID...")
        self.search_input.setMinimumHeight(50)
        layout.addWidget(self.search_input)
        
        # Accounts list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.accounts_widget = QWidget()
        self.accounts_layout = QVBoxLayout(self.accounts_widget)
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(6)
        self.accounts_layout.addStretch()
        
        self.scroll_area.setWidget(self.accounts_widget)
        layout.addWidget(self.scroll_area)
    
    def on_account_selected(self, selected_widget):
        """Handle account selection"""
        # Notify parent window about account selection
        if self.parent_window:
            self.parent_window.on_account_selected(selected_widget)
    
    def on_code_clicked(self, event):
        """Handle click on the auth code label to copy to clipboard"""
        if (
            self.selected_account
            and self.copy_on_click_enabled
            and hasattr(self, 'title_label')
        ):
            code = self.title_label.text()
            if code and code != "SDA" and code != "...":
                clipboard = QApplication.clipboard()
                clipboard.setText(code)
                # Optional: Show visual feedback
                original_text = self.title_label.text()
                self.title_label.setText("Copied!")
                self.title_label.setDisabled(True)
                QTimer.singleShot(1000, lambda: self.title_label.setText(original_text))
                QTimer.singleShot(1000, lambda: self.title_label.setDisabled(False))
    
    def start_auto_refresh(self):
        """Start automatic refresh of the auth code every second"""
        if self.refresh_timer:
            self.refresh_timer.stop()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_auth_code)
        interval_ms = SettingsManager.get_setting("auto_refresh_interval_seconds") * 1000
        self.refresh_timer.start(interval_ms)
    
    def stop_auto_refresh(self):
        """Stop automatic refresh"""
        if self.refresh_timer:
            self.refresh_timer.stop()
            self.refresh_timer = None
    
    def refresh_auth_code(self):
        """Refresh the auth code"""
        if self.selected_account and self.parent_window:
            # Request a new code from the auth manager
            code = self.parent_window.auth_manager.generate_auth_code(self.selected_account)
            self.title_label.setText(code)
    
    def set_selected_account(self, account):
        """Set the selected account and start auto-refresh"""
        self.selected_account = account
        if account and SettingsManager.get_setting("auto_refresh_enabled"):
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()

    def apply_settings(self):
        """Apply settings to the account screen behavior."""
        self.copy_on_click_enabled = SettingsManager.get_setting("copy_code_on_click")
        auto_refresh_enabled = SettingsManager.get_setting("auto_refresh_enabled")
        if self.selected_account and auto_refresh_enabled:
            self.start_auto_refresh()
        else:
    def set_selected_account(self, account):
        """Set the selected account and start auto-refresh"""
        self.selected_account = account
        if account:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
