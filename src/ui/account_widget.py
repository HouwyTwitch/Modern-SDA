from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from src.theme import ThemeManager
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

# Import account management classes
from src.account_manager import AccountData


class AccountWidget(QFrame):
    """Custom widget for displaying account information"""
    
    account_selected = pyqtSignal(object)  # Signal emitted when account is selected
    
    def __init__(self, account: AccountData, parent=None):
        super().__init__(parent)
        self.account = account
        self.is_hovered = False
        self.is_selected = False
        self.setup_ui()
        self.load_avatar()
        # React to avatar updates
        try:
            # Parent main window emits account_updated via AccountManager; handled there to refresh widgets
            pass
        except Exception:
            pass
    
    def setup_ui(self):
        """Setup the UI for the account widget"""
        self.setFixedHeight(96)  # Increased height to prevent clipping
        self.setContentsMargins(0, 0, 0, 0)
        
        # Create main container for better styling
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.get_current_theme().SURFACE};
                border: 1px solid {ThemeManager.get_current_theme().BORDER};
                border-radius: 14px;
                margin: 1px;
            }}
        """)
        
        # Layout for the main widget - minimal margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        main_layout.addWidget(self.container)
        
        # Layout for the container - minimal padding
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(8, 8, 8, 8)  # Minimal container padding
        layout.setSpacing(12)  # Reduced spacing between elements
        
        # Avatar container with proper centering
        avatar_container = QFrame()
        avatar_container.setFixedSize(60, 60)  # Slightly larger avatar
        avatar_container.setStyleSheet(f"""
            QFrame {{
                background-color: {ThemeManager.get_current_theme().ACCENT};
                border-radius: 12px;
                border: none;
            }}
        """)
        
        # Avatar layout to center the text properly
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setSpacing(0)
        
        self.avatar_label = QLabel()
        self.avatar_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {ThemeManager.get_current_theme().TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                border: none;
            }}
        """)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setFixedSize(60, 60)  # Match container size
        avatar_layout.addWidget(self.avatar_label)
        
        layout.addWidget(avatar_container, 0, Qt.AlignVCenter)  # Center vertically without wrapper
        
        # Account info container with proper spacing
        info_container = QFrame()
        info_container.setContentsMargins(0, 0, 0, 0)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)  # Reduced spacing to fit text better
        
        # Account name
        self.name_label = QLabel(self.account.account_name)
        self.name_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.get_current_theme().TEXT_PRIMARY};
                background-color: transparent;
                border: none;
            }}
        """)
        self.name_label.setWordWrap(False)  # Prevent word wrapping
        info_layout.addWidget(self.name_label)
        
        # Steam ID
        self.steamid_label = QLabel(f"Steam ID: {self.account.steam_id}")
        self.steamid_label.setFont(QFont("Segoe UI", 11))
        self.steamid_label.setStyleSheet(f"""
            QLabel {{
                color: {ThemeManager.get_current_theme().TEXT_SECONDARY};
                background-color: transparent;
                border: none;
            }}
        """)
        self.steamid_label.setWordWrap(False)  # Prevent word wrapping
        info_layout.addWidget(self.steamid_label)
        
        layout.addWidget(info_container, 1)  # Give it stretch factor of 1
        
        # Add hover effect and click functionality
        self.setMouseTracking(True)
        self.container.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)  # Show pointer cursor
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        if not self.is_selected:
            self.is_hovered = True
            self.update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        self.is_hovered = False
        self.update_style()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click for selection"""
        if event.button() == Qt.LeftButton:
            if not self.is_selected:
                self.account_selected.emit(self)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool):
        """Set the selection state of the account"""
        self.is_selected = selected
        self.update_style()
    
    def update_style(self):
        """Update widget styling based on current state"""
        current_theme = ThemeManager.get_current_theme()
        
        if self.is_selected:
            # Selected state
            background_color = current_theme.ACCENT
            border_color = current_theme.ACCENT_HOVER
        elif self.is_hovered:
            # Hover state
            background_color = current_theme.SURFACE_HOVER
            border_color = current_theme.BORDER_FOCUS
        else:
            # Normal state
            background_color = current_theme.SURFACE
            border_color = current_theme.BORDER
        
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {background_color};
                border: 1px solid {border_color};
                border-radius: 14px;
                margin: 1px;
            }}
        """)
    
    def load_avatar(self):
        """Load avatar image from URL"""
        # Try to load local avatar image if available
        if getattr(self.account, 'avatar_url', ''):
            try:
                pixmap = QPixmap(self.account.avatar_url)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(60, 60, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    self.avatar_label.setPixmap(scaled)
                    self.avatar_label.setText("")
                    return
            except Exception:
                pass
        # Fallback: first letter of account name
        if self.account.account_name:
            self.avatar_label.setText(self.account.account_name[0].upper())