from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QSizePolicy, QStackedWidget, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from src.theme import ThemeManager


# Colour cues per confirmation type. Keys use the aiosteampy ``conf.type.name``
# values so we get a stable match.
_TYPE_BADGES = {
    "TRADE": ("Trade", "accent"),
    "LISTING": ("Market", "success"),
    "MARKET": ("Market", "success"),
    "CREATE_LISTING": ("Market", "success"),
    "PHONE_NUMBER_CHANGE": ("Phone", "warning"),
    "ACCOUNT_RECOVERY": ("Recovery", "warning"),
    "API_KEY": ("API key", "warning"),
    "NEW_WEB_API_KEY": ("API key", "warning"),
    "UNKNOWN": ("Other", "neutral"),
}


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
        self.is_processing = False
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the confirmation item UI"""
        self.setMinimumHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)

        # Create main container for better styling
        self.container = QFrame(self)

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
        content_layout.setSpacing(6)

        # Header row: type label + coloured badge
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        header_row.setContentsMargins(0, 0, 0, 0)

        self.type_label = QLabel(self._friendly_type_label())
        self.type_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.type_label.setWordWrap(False)
        header_row.addWidget(self.type_label)

        self.badge_label = QLabel(self._badge_text())
        self.badge_label.setFont(QFont("Segoe UI", 9, QFont.DemiBold))
        self.badge_label.setAlignment(Qt.AlignCenter)
        self.badge_label.setContentsMargins(8, 2, 8, 2)
        self.badge_label.setFixedHeight(20)
        header_row.addWidget(self.badge_label)
        header_row.addStretch()

        content_layout.addLayout(header_row)

        # Description
        self.desc_label = QLabel(self.description)
        self.desc_label.setFont(QFont("Segoe UI", 11))
        self.desc_label.setWordWrap(True)
        self.desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_layout.addWidget(self.desc_label)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(content_widget, 1)

        # Right-hand slot: either the accept/decline buttons or a progress spinner
        self.right_stack = QStackedWidget()
        self.right_stack.setFixedWidth(96)
        self.right_stack.setStyleSheet("background: transparent;")

        # Buttons page
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)

        self.accept_button = QPushButton()
        self.accept_button.setFixedSize(40, 40)
        self.accept_button.setToolTip("Accept")
        self.accept_button.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(self.accept_button)

        self.decline_button = QPushButton()
        self.decline_button.setFixedSize(40, 40)
        self.decline_button.setToolTip("Decline")
        self.decline_button.setCursor(Qt.PointingHandCursor)
        buttons_layout.addWidget(self.decline_button)

        self.right_stack.addWidget(buttons_widget)

        # Spinner page
        spinner_widget = QWidget()
        spinner_layout = QVBoxLayout(spinner_widget)
        spinner_layout.setContentsMargins(0, 0, 0, 0)
        spinner_layout.setSpacing(4)
        spinner_layout.setAlignment(Qt.AlignCenter)

        self.spinner_bar = QProgressBar()
        self.spinner_bar.setRange(0, 0)  # indeterminate
        self.spinner_bar.setTextVisible(False)
        self.spinner_bar.setFixedHeight(6)
        self.spinner_bar.setFixedWidth(80)
        spinner_layout.addWidget(self.spinner_bar)

        self.spinner_label = QLabel("Processing…")
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_label.setFont(QFont("Segoe UI", 9))
        spinner_layout.addWidget(self.spinner_label)

        self.right_stack.addWidget(spinner_widget)
        self.right_stack.setCurrentIndex(0)

        layout.addWidget(self.right_stack)

        self.apply_styling()

    # ── Labels ─────────────────────────────────────────────────────────────

    def _friendly_type_label(self) -> str:
        """Human-readable version of the raw confirmation type name."""
        raw = (self.confirmation_type or "").upper()
        mapping = {
            "TRADE": "Trade Offer",
            "LISTING": "Market Listing",
            "MARKET": "Market Listing",
            "CREATE_LISTING": "Market Listing",
            "PHONE_NUMBER_CHANGE": "Phone Change",
            "ACCOUNT_RECOVERY": "Account Recovery",
            "API_KEY": "API Key",
            "NEW_WEB_API_KEY": "Web API Key",
            "UNKNOWN": "Confirmation",
        }
        return mapping.get(raw, raw.replace("_", " ").title() or "Confirmation")

    def _badge_text(self) -> str:
        raw = (self.confirmation_type or "").upper()
        entry = _TYPE_BADGES.get(raw, _TYPE_BADGES["UNKNOWN"])
        return entry[0]

    def _badge_role(self) -> str:
        raw = (self.confirmation_type or "").upper()
        entry = _TYPE_BADGES.get(raw, _TYPE_BADGES["UNKNOWN"])
        return entry[1]

    def connect_signals(self):
        """Connect button signals to slots"""
        self.accept_button.clicked.connect(self.on_accept_clicked)
        self.decline_button.clicked.connect(self.on_decline_clicked)

    def on_accept_clicked(self):
        if self.is_processing:
            return
        self.set_processing(True)
        self.confirmation_accepted.emit(self.confirmation_id)

    def on_decline_clicked(self):
        if self.is_processing:
            return
        self.set_processing(True)
        self.confirmation_declined.emit(self.confirmation_id)

    def set_processing(self, processing: bool):
        """Swap the action buttons out for a spinner while the op is in flight."""
        self.is_processing = processing
        self.right_stack.setCurrentIndex(1 if processing else 0)
        self.accept_button.setEnabled(not processing)
        self.decline_button.setEnabled(not processing)

    def apply_styling(self):
        """Apply current theme styling to the confirmation item"""
        current_theme = ThemeManager.get_current_theme()

        # Container
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme.SURFACE};
                border: 1px solid {current_theme.BORDER};
                border-radius: 6px;
                margin: 1px;
            }}
        """)

        # Text
        self.type_label.setStyleSheet(
            f"QLabel {{ color: {current_theme.TEXT_PRIMARY};"
            f" background-color: transparent; border: none; }}"
        )
        self.desc_label.setStyleSheet(
            f"QLabel {{ color: {current_theme.TEXT_SECONDARY};"
            f" background-color: transparent; border: none; }}"
        )

        # Badge colour depends on role
        role = self._badge_role()
        if role == "accent":
            badge_bg = current_theme.ACCENT
            badge_fg = current_theme.TEXT_PRIMARY
        elif role == "success":
            badge_bg = current_theme.SUCCESS
            badge_fg = current_theme.TEXT_PRIMARY
        elif role == "warning":
            badge_bg = "#F5A623"
            badge_fg = "#1A1A1A"
        else:
            badge_bg = current_theme.SURFACE_ELEVATED
            badge_fg = current_theme.TEXT_SECONDARY
        self.badge_label.setStyleSheet(
            f"QLabel {{ background-color: {badge_bg}; color: {badge_fg};"
            f" border-radius: 8px; padding: 1px 8px; }}"
        )

        # Buttons
        accept_icon = current_theme.create_svg_icon(
            current_theme.get_accept_svg(),
            current_theme.TEXT_PRIMARY,
            20,
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
            QPushButton:disabled {{
                background-color: {current_theme.SURFACE_ELEVATED};
            }}
        """)

        decline_icon = current_theme.create_svg_icon(
            current_theme.get_decline_svg(),
            current_theme.TEXT_PRIMARY,
            20,
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
            QPushButton:disabled {{
                background-color: {current_theme.SURFACE_ELEVATED};
            }}
        """)

        # Spinner
        self.spinner_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {current_theme.BORDER};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {current_theme.ACCENT};
                border-radius: 3px;
            }}
        """)
        self.spinner_label.setStyleSheet(
            f"QLabel {{ color: {current_theme.TEXT_TERTIARY}; background: transparent; }}"
        )
