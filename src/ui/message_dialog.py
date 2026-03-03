from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.theme import ThemeManager
from src.ui.title_bar import DialogTitleBar


class MessageDialog(QDialog):
    """Frameless themed replacement for QMessageBox."""

    def __init__(self, parent, title: str, message: str, buttons: list):
        """
        buttons: list of (label: str, is_primary: bool) tuples, left-to-right.
        The last button with is_primary=True triggers accept(); others reject().
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._confirmed = False
        self._setup_ui(title, message, buttons)
        self.apply_theme()

    def _setup_ui(self, title: str, message: str, buttons: list):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Custom titlebar
        self.title_bar = DialogTitleBar(title, self)
        root.addWidget(self.title_bar)

        # Content
        content = QVBoxLayout()
        content.setContentsMargins(28, 20, 28, 24)
        content.setSpacing(20)

        self.message_label = QLabel(message)
        self.message_label.setFont(QFont("Segoe UI", 11))
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.message_label.setMinimumWidth(300)
        content.addWidget(self.message_label)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        for label, is_primary in buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(90)
            btn.setProperty("primary", is_primary)
            btn.clicked.connect(lambda _=False, p=is_primary: self._on_click(p))
            btn_row.addWidget(btn)

        content.addLayout(btn_row)
        root.addLayout(content)

        self.adjustSize()
        # Enforce a sensible minimum width
        if self.width() < 360:
            self.setFixedWidth(360)

    def _on_click(self, is_primary: bool):
        self._confirmed = is_primary
        if is_primary:
            self.accept()
        else:
            self.reject()

    def apply_theme(self):
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BACKGROUND};
                border: 1px solid {theme.BORDER};
            }}
            QLabel {{
                color: {theme.TEXT_PRIMARY};
                background-color: transparent;
                border: none;
            }}
        """)
        for btn in self.findChildren(QPushButton):
            if btn.property("primary"):
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {theme.ACCENT};
                        border: none;
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: 600;
                        color: {theme.TEXT_PRIMARY};
                        padding: 0 16px;
                    }}
                    QPushButton:hover {{ background-color: {theme.ACCENT_HOVER}; }}
                    QPushButton:pressed {{ background-color: {theme.ACCENT_PRESSED}; }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {theme.SURFACE_ELEVATED};
                        border: 2px solid {theme.BORDER};
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: 600;
                        color: {theme.TEXT_SECONDARY};
                        padding: 0 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {theme.SURFACE_HOVER};
                        border-color: {theme.BORDER_FOCUS};
                        color: {theme.TEXT_PRIMARY};
                    }}
                """)

    # ── Static convenience methods (drop-in QMessageBox replacements) ─────

    @staticmethod
    def information(parent, title: str, message: str) -> None:
        MessageDialog(parent, title, message, [("OK", True)]).exec_()

    @staticmethod
    def warning(parent, title: str, message: str) -> None:
        MessageDialog(parent, title, message, [("OK", True)]).exec_()

    @staticmethod
    def question(parent, title: str, message: str) -> bool:
        """Returns True if the user clicked Yes, False otherwise."""
        dlg = MessageDialog(parent, title, message, [("No", False), ("Yes", True)])
        dlg.exec_()
        return dlg._confirmed
