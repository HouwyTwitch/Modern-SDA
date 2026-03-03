from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.theme import ThemeManager

# Shared button style template so main titlebar and dialog titlebar are pixel-perfect.
_BTN_BASE = """
    QPushButton {{
        background-color: transparent;
        border: none;
        border-radius: 6px;
        color: {text_secondary};
        font-size: 18px;
        font-weight: 300;
    }}
    QPushButton:hover {{
        background-color: {hover_bg};
        color: {hover_fg};
    }}
    QPushButton:pressed {{
        background-color: {pressed_bg};
        color: {hover_fg};
    }}
"""


class CustomTitleBar(QWidget):
    """Frameless window title bar with drag, minimize, and close."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self._drag_pos = None
        self.setFixedHeight(42)
        self._setup_ui()
        self.apply_theme()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(0)

        self.title_label = QLabel("Steam Authenticator")
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(36, 32)
        self.minimize_btn.setToolTip("Minimize")
        self.minimize_btn.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.minimize_btn)

        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(36, 32)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_btn)

    def apply_theme(self):
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            CustomTitleBar {{
                background-color: {theme.SURFACE};
                border-bottom: 1px solid {theme.BORDER};
            }}
        """)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.TEXT_TERTIARY};
                background-color: transparent;
                border: none;
                letter-spacing: 0.3px;
            }}
        """)
        self.minimize_btn.setStyleSheet(_BTN_BASE.format(
            text_secondary=theme.TEXT_SECONDARY,
            hover_bg=theme.SURFACE_HOVER,
            hover_fg=theme.TEXT_PRIMARY,
            pressed_bg=theme.SURFACE_ELEVATED,
        ))
        self.close_btn.setStyleSheet(_BTN_BASE.format(
            text_secondary=theme.TEXT_SECONDARY,
            hover_bg=theme.ERROR,
            hover_fg="#FFFFFF",
            pressed_bg=theme.ERROR_HOVER,
        ))

    # ── Window dragging ───────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.parent_window.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.parent_window.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()


class DialogTitleBar(QWidget):
    """Minimal title bar for frameless dialogs — title + close button only."""

    def __init__(self, title: str, parent):
        super().__init__(parent)
        self.parent_window = parent
        self._drag_pos = None
        self._title_text = title
        self.setFixedHeight(42)
        self._setup_ui()
        self.apply_theme()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(0)

        self.title_label = QLabel(self._title_text)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(36, 32)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.parent_window.reject)
        layout.addWidget(self.close_btn)

    def apply_theme(self):
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            DialogTitleBar {{
                background-color: {theme.SURFACE};
                border-bottom: 1px solid {theme.BORDER};
            }}
        """)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.TEXT_TERTIARY};
                background-color: transparent;
                border: none;
                letter-spacing: 0.3px;
            }}
        """)
        self.close_btn.setStyleSheet(_BTN_BASE.format(
            text_secondary=theme.TEXT_SECONDARY,
            hover_bg=theme.ERROR,
            hover_fg="#FFFFFF",
            pressed_bg=theme.ERROR_HOVER,
        ))

    # ── Window dragging ───────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.parent_window.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.parent_window.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
