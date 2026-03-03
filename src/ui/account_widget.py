import threading
import urllib.request

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter, QPainterPath
from src.theme import ThemeManager

from src.account_manager import AccountData

_AVATAR_SIZE = 60
_AVATAR_RADIUS = 7   # squircle corner radius (halved from 14)


class AccountWidget(QFrame):
    """Custom widget for displaying account information"""

    account_selected = pyqtSignal(object)
    edit_requested = pyqtSignal(object)
    remove_requested = pyqtSignal(object)
    avatar_fetched = pyqtSignal(bytes)

    def __init__(self, account: AccountData, parent=None):
        super().__init__(parent)
        self.account = account
        self.is_hovered = False
        self.is_selected = False
        self.setup_ui()
        self.avatar_fetched.connect(self._on_avatar_fetched)
        self.load_avatar()

    # ── Build UI ──────────────────────────────────────────────────────────

    def setup_ui(self):
        self.setFixedHeight(96)
        self.setContentsMargins(0, 0, 0, 0)

        current_theme = ThemeManager.get_current_theme()

        # Outer container frame
        self.container = QFrame(self)
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme.SURFACE};
                border: 1px solid {current_theme.BORDER};
                border-radius: 8px;
                margin: 1px;
            }}
        """)

        self.shadow_effect = QGraphicsDropShadowEffect(self.container)
        self.shadow_effect.setBlurRadius(10)
        self.shadow_effect.setOffset(0, 4)
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

        # ── Avatar ─────────────────────────────────────────────────────────
        self.avatar_container = QFrame()
        self.avatar_container.setFixedSize(_AVATAR_SIZE, _AVATAR_SIZE)
        self.avatar_container.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme.ACCENT};
                border-radius: {_AVATAR_RADIUS}px;
                border: none;
            }}
        """)

        avatar_vbox = QVBoxLayout(self.avatar_container)
        avatar_vbox.setContentsMargins(0, 0, 0, 0)
        avatar_vbox.setSpacing(0)

        self.avatar_label = QLabel()
        self.avatar_label.setStyleSheet(
            "background-color: transparent; color: white; "
            "font-size: 22px; font-weight: bold; border: none;"
        )
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setFixedSize(_AVATAR_SIZE, _AVATAR_SIZE)
        avatar_vbox.addWidget(self.avatar_label)

        layout.addWidget(self.avatar_container, 0, Qt.AlignVCenter)

        # ── Account info ───────────────────────────────────────────────────
        info_container = QFrame()
        info_container.setContentsMargins(0, 0, 0, 0)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        self.name_label = QLabel(self.account.account_name)
        self.name_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.name_label.setStyleSheet(
            f"color: {current_theme.TEXT_PRIMARY}; background-color: transparent; border: none;"
        )
        self.name_label.setWordWrap(False)
        info_layout.addWidget(self.name_label)

        self.steamid_label = QLabel(f"Steam ID: {self.account.steam_id}")
        self.steamid_label.setFont(QFont("Segoe UI", 11))
        self.steamid_label.setStyleSheet(
            f"color: {current_theme.TEXT_SECONDARY}; background-color: transparent; border: none;"
        )
        self.steamid_label.setWordWrap(False)
        info_layout.addWidget(self.steamid_label)

        layout.addWidget(info_container, 1)

        # ── Action buttons (icon-only, side-by-side, shown on hover) ─────────
        # Container always occupies its fixed width to prevent layout shift when
        # buttons appear/disappear — only the buttons inside are shown/hidden.
        self.actions_container = QFrame()
        self.actions_container.setFixedWidth(80)
        self.actions_container.setStyleSheet("background-color: transparent; border: none;")
        actions_layout = QHBoxLayout(self.actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)
        actions_layout.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        self.edit_button = QPushButton("✎")
        self.edit_button.setFixedSize(34, 34)
        self.edit_button.setToolTip("Edit account")
        self.edit_button.setVisible(False)
        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(self.account))

        self.remove_button = QPushButton("✕")
        self.remove_button.setFixedSize(34, 34)
        self.remove_button.setToolTip("Remove account")
        self.remove_button.setVisible(False)
        self.remove_button.clicked.connect(lambda: self.remove_requested.emit(self.account))

        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.remove_button)

        layout.addWidget(self.actions_container, 0, Qt.AlignRight | Qt.AlignVCenter)

        self.setMouseTracking(True)
        self.container.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_action_styles()

    # ── Mouse events ──────────────────────────────────────────────────────

    def enterEvent(self, event):
        self.is_hovered = True
        self.edit_button.setVisible(True)
        self.remove_button.setVisible(True)
        self.update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        if not self.is_selected:
            self.edit_button.setVisible(False)
            self.remove_button.setVisible(False)
        self.update_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_selected:
            self.account_selected.emit(self)
        super().mousePressEvent(event)

    # ── State management ──────────────────────────────────────────────────

    def set_selected(self, selected: bool):
        self.is_selected = selected
        visible = selected or self.is_hovered
        self.edit_button.setVisible(visible)
        self.remove_button.setVisible(visible)
        self.update_style()

    def update_style(self):
        current_theme = ThemeManager.get_current_theme()

        if self.is_selected:
            bg, border = current_theme.ACCENT, current_theme.ACCENT_HOVER
            avatar_bg = current_theme.ACCENT_HOVER
            self._animate_shadow(20)
        elif self.is_hovered:
            bg, border = current_theme.SURFACE_HOVER, current_theme.BORDER_FOCUS
            avatar_bg = current_theme.ACCENT
            self._animate_shadow(14)
        else:
            bg, border = current_theme.SURFACE, current_theme.BORDER
            avatar_bg = current_theme.ACCENT
            self._animate_shadow(8)

        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
                margin: 1px;
            }}
        """)
        self.avatar_container.setStyleSheet(f"""
            QFrame {{
                background-color: {avatar_bg};
                border-radius: {_AVATAR_RADIUS}px;
                border: none;
            }}
        """)

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
        current_theme = ThemeManager.get_current_theme()

        if self.is_selected:
            edit_bg   = "rgba(255,255,255,40)"
            edit_border = "rgba(255,255,255,80)"
            edit_hover  = "rgba(255,255,255,70)"
        else:
            edit_bg   = current_theme.SURFACE_ELEVATED
            edit_border = current_theme.BORDER
            edit_hover  = current_theme.ACCENT

        self.edit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {edit_bg};
                border: 1px solid {edit_border};
                border-radius: 17px;
                color: {current_theme.TEXT_PRIMARY};
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {edit_hover};
                border-color: {current_theme.BORDER_FOCUS};
            }}
        """)

        if self.is_selected:
            rem_bg     = "rgba(255,80,80,40)"
            rem_border = "rgba(255,80,80,80)"
            rem_hover  = "rgba(255,80,80,80)"
            rem_color  = current_theme.TEXT_PRIMARY
        else:
            rem_bg     = current_theme.SURFACE_ELEVATED
            rem_border = current_theme.BORDER
            rem_hover  = current_theme.ERROR
            rem_color  = current_theme.TEXT_SECONDARY

        self.remove_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {rem_bg};
                border: 1px solid {rem_border};
                border-radius: 17px;
                color: {rem_color};
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {rem_hover};
                border-color: {current_theme.ERROR};
                color: {current_theme.TEXT_PRIMARY};
            }}
        """)

    # ── Avatar ────────────────────────────────────────────────────────────

    def load_avatar(self):
        if self.account.avatar_url:
            threading.Thread(
                target=self._fetch_avatar_bytes,
                args=(self.account.avatar_url,),
                daemon=True,
            ).start()
        elif self.account.account_name:
            self.avatar_label.setPixmap(QPixmap())
            self.avatar_label.setText(self.account.account_name[0].upper())

    def _fetch_avatar_bytes(self, url: str):
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                data = r.read()
            self.avatar_fetched.emit(data)
        except Exception:
            pass

    def _on_avatar_fetched(self, data: bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if not pixmap.isNull():
            pixmap = self._clip_to_squircle(
                pixmap.scaled(_AVATAR_SIZE, _AVATAR_SIZE, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            )
            self.avatar_label.setPixmap(pixmap)
            self.avatar_label.setText("")

    @staticmethod
    def _clip_to_squircle(pixmap: QPixmap) -> QPixmap:
        size = pixmap.size()
        result = QPixmap(size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, size.width(), size.height(), _AVATAR_RADIUS, _AVATAR_RADIUS)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return result

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
