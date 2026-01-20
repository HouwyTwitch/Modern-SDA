from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from src.theme import ThemeManager
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# Import account management classes
from src.account_manager import AccountData


class AccountWidget(QFrame):
    """Custom widget for displaying account information"""
    
    account_selected = pyqtSignal(object)  # Signal emitted when account is selected
    edit_requested = pyqtSignal(object)  # Signal emitted when edit is requested
    remove_requested = pyqtSignal(object)  # Signal emitted when removal is requested
    
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
        current_theme = ThemeManager.get_current_theme()
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme.SURFACE};
                border: 1px solid {current_theme.BORDER};
                border-radius: 16px;
                margin: 1px;
            }}
        """)
        self.shadow_effect = QGraphicsDropShadowEffect(self.container)
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setOffset(0, 6)
        self.shadow_effect.setColor(QColor(current_theme.SHADOW))
        self.container.setGraphicsEffect(self.shadow_effect)
        self.shadow_anim = QPropertyAnimation(self.shadow_effect, b"blurRadius", self)
        self.shadow_anim.setDuration(160)
        self.shadow_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Layout for the main widget - minimal margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        main_layout.addWidget(self.container)
        
        # Layout for the container - minimal padding
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(10, 10, 10, 10)  # Balanced container padding
        layout.setSpacing(14)  # Slightly more spacing between elements
        
        # Avatar container with proper centering
        avatar_container = QFrame()
        avatar_container.setFixedSize(60, 60)  # Slightly larger avatar
        avatar_container.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme.ACCENT};
                border-radius: 14px;
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
                color: {current_theme.TEXT_PRIMARY};
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
                color: {current_theme.TEXT_PRIMARY};
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
                color: {current_theme.TEXT_SECONDARY};
                background-color: transparent;
                border: none;
            }}
        """)
        self.steamid_label.setWordWrap(False)  # Prevent word wrapping
        info_layout.addWidget(self.steamid_label)
        
        layout.addWidget(info_container, 1)  # Give it stretch factor of 1

        actions_container = QFrame()
        actions_layout = QVBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)
        actions_layout.setAlignment(Qt.AlignVCenter)

        self.edit_button = QPushButton("Edit")
        self.edit_button.setFixedSize(80, 32)
        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(self.account))

        self.remove_button = QPushButton("Remove")
        self.remove_button.setFixedSize(80, 32)
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.account))

        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.remove_button)

        layout.addWidget(actions_container, 0, Qt.AlignRight | Qt.AlignVCenter)
        
        # Add hover effect and click functionality
        self.setMouseTracking(True)
        self.container.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)  # Show pointer cursor
        self.apply_action_styles()
    
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
                border-radius: 16px;
                margin: 1px;
            }}
        """)
        if self.is_selected:
            self._animate_shadow(20)
        elif self.is_hovered:
            self._animate_shadow(14)
        else:
            self._animate_shadow(8)
        self.apply_action_styles()

    def apply_action_styles(self):
        """Apply theme styling to action buttons"""
        current_theme = ThemeManager.get_current_theme()

        self.edit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.SURFACE_HOVER};
                border: 1px solid {current_theme.BORDER};
                border-radius: 8px;
                color: {current_theme.TEXT_PRIMARY};
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {current_theme.ACCENT};
                border-color: {current_theme.BORDER_FOCUS};
            }}
        """)

        self.remove_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {current_theme.BORDER};
                border-radius: 8px;
                color: {current_theme.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {current_theme.ACCENT_PRESSED};
                border-color: {current_theme.BORDER_FOCUS};
                color: {current_theme.TEXT_PRIMARY};
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

    def update_account(self, account: AccountData):
        """Update account data and refresh display"""
        self.account = account
        self.name_label.setText(self.account.account_name)
        self.steamid_label.setText(f"Steam ID: {self.account.steam_id}")
        self.load_avatar()

    def _animate_shadow(self, blur_radius: int):
        self.shadow_anim.stop()
        self.shadow_anim.setStartValue(self.shadow_effect.blurRadius())
        self.shadow_anim.setEndValue(blur_radius)
        self.shadow_anim.start()
