from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from src.theme import ThemeManager
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from src.account_manager import AccountData


class AccountWidget(QFrame):
    """Custom widget for displaying account information"""

    account_selected = pyqtSignal(object)
    edit_requested = pyqtSignal(object)
    remove_requested = pyqtSignal(object)

    def __init__(self, account: AccountData, parent=None):
        super().__init__(parent)
        self.account = account
        self.is_hovered = False
        self.is_selected = False
        self.setup_ui()
        self.load_avatar()

    def setup_ui(self):
        """Setup the UI for the account widget"""
        self.setFixedHeight(96)
        self.setContentsMargins(0, 0, 0, 0)

        current_theme = ThemeManager.get_current_theme()

        # Outer container frame
        self.container = QFrame(self)
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

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.container)

        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(14)

        # Avatar container (stored as self so update_style can reach it)
        self.avatar_container = QFrame()
        self.avatar_container.setFixedSize(60, 60)
        self.avatar_container.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme.ACCENT};
                border-radius: 14px;
                border: none;
            }}
        """)

        avatar_layout = QVBoxLayout(self.avatar_container)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setSpacing(0)

        self.avatar_label = QLabel()
        self.avatar_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: none;
            }
        """)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setFixedSize(60, 60)
        avatar_layout.addWidget(self.avatar_label)

        layout.addWidget(self.avatar_container, 0, Qt.AlignVCenter)

        # Account info
        info_container = QFrame()
        info_container.setContentsMargins(0, 0, 0, 0)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        self.name_label = QLabel(self.account.account_name)
        self.name_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.name_label.setStyleSheet(f"""
            QLabel {{
                color: {current_theme.TEXT_PRIMARY};
                background-color: transparent;
                border: none;
            }}
        """)
        self.name_label.setWordWrap(False)
        info_layout.addWidget(self.name_label)

        self.steamid_label = QLabel(f"Steam ID: {self.account.steam_id}")
        self.steamid_label.setFont(QFont("Segoe UI", 11))
        self.steamid_label.setStyleSheet(f"""
            QLabel {{
                color: {current_theme.TEXT_SECONDARY};
                background-color: transparent;
                border: none;
            }}
        """)
        self.steamid_label.setWordWrap(False)
        info_layout.addWidget(self.steamid_label)

        layout.addWidget(info_container, 1)

        # Action buttons
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

        self.setMouseTracking(True)
        self.container.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_action_styles()

    # ── Mouse events ──────────────────────────────────────────────────────

    def enterEvent(self, event):
        if not self.is_selected:
            self.is_hovered = True
            self.update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_selected:
            self.account_selected.emit(self)
        super().mousePressEvent(event)

    # ── State management ──────────────────────────────────────────────────

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        """Update widget styling based on hover / selected state."""
        current_theme = ThemeManager.get_current_theme()

        if self.is_selected:
            bg = current_theme.ACCENT
            border = current_theme.ACCENT_HOVER
            # Slightly lighter accent so avatar is distinguishable
            avatar_bg = current_theme.ACCENT_HOVER
            self._animate_shadow(20)
        elif self.is_hovered:
            bg = current_theme.SURFACE_HOVER
            border = current_theme.BORDER_FOCUS
            avatar_bg = current_theme.ACCENT
            self._animate_shadow(14)
        else:
            bg = current_theme.SURFACE
            border = current_theme.BORDER
            avatar_bg = current_theme.ACCENT
            self._animate_shadow(8)

        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 16px;
                margin: 1px;
            }}
        """)

        self.avatar_container.setStyleSheet(f"""
            QFrame {{
                background-color: {avatar_bg};
                border-radius: 14px;
                border: none;
            }}
        """)

        # Labels stay white/primary on accent; secondary becomes primary when selected
        text_color = current_theme.TEXT_PRIMARY
        sub_color = current_theme.TEXT_PRIMARY if self.is_selected else current_theme.TEXT_SECONDARY

        self.name_label.setStyleSheet(
            f"color: {text_color}; background-color: transparent; border: none;"
        )
        self.steamid_label.setStyleSheet(
            f"color: {sub_color}; background-color: transparent; border: none;"
        )

        self.apply_action_styles()

    def apply_action_styles(self):
        """Apply theme styling to action buttons (selected-state aware)."""
        current_theme = ThemeManager.get_current_theme()

        if self.is_selected:
            # Semi-transparent overlays look clean on accent background
            self.edit_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 35);
                    border: 1px solid rgba(255, 255, 255, 60);
                    border-radius: 8px;
                    color: {current_theme.TEXT_PRIMARY};
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 65);
                }}
            """)
            self.remove_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 80, 80, 35);
                    border: 1px solid rgba(255, 80, 80, 70);
                    border-radius: 8px;
                    color: {current_theme.TEXT_PRIMARY};
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 80, 80, 75);
                }}
            """)
        else:
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
                    background-color: {current_theme.ERROR};
                    border-color: {current_theme.ERROR};
                    color: {current_theme.TEXT_PRIMARY};
                }}
            """)

    # ── Avatar ────────────────────────────────────────────────────────────

    def load_avatar(self):
        if getattr(self.account, 'avatar_url', ''):
            try:
                pixmap = QPixmap(self.account.avatar_url)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        60, 60, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                    )
                    self.avatar_label.setPixmap(scaled)
                    self.avatar_label.setText("")
                    return
            except Exception:
                pass
        if self.account.account_name:
            self.avatar_label.setText(self.account.account_name[0].upper())

    def update_account(self, account: AccountData):
        self.account = account
        self.name_label.setText(account.account_name)
        self.steamid_label.setText(f"Steam ID: {account.steam_id}")
        self.load_avatar()

    # ── Shadow animation ──────────────────────────────────────────────────

    def _animate_shadow(self, blur_radius: int):
        self.shadow_anim.stop()
        self.shadow_anim.setStartValue(self.shadow_effect.blurRadius())
        self.shadow_anim.setEndValue(blur_radius)
        self.shadow_anim.start()
