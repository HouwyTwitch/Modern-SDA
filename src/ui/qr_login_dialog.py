"""QR login approval dialog.

Lets the user paste a Steam QR challenge URL (from "Sign in on computer") and
approve or deny it on behalf of the selected account. Optionally decodes the
URL from a clipboard image when pyzbar + Pillow are available.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QApplication, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from src.account_manager import AccountData, AuthenticationManager
from src.theme import ThemeManager


class _QrApproveWorker(QThread):
    """Runs ``auth_manager.approve_qr_login`` off the UI thread."""

    finished_result = pyqtSignal(dict)

    def __init__(self, auth_manager: AuthenticationManager, account: AccountData,
                 url: str, confirm: bool, parent=None):
        super().__init__(parent)
        self._auth = auth_manager
        self._account = account
        self._url = url
        self._confirm = confirm

    def run(self):
        try:
            future = self._auth.submit(
                self._auth.approve_qr_login(self._account, self._url, confirm=self._confirm)
            )
            result = future.result(timeout=30)
        except Exception as e:
            result = {'success': False, 'error': str(e)}
        self.finished_result.emit(result or {'success': False, 'error': 'No response'})


class QrLoginDialog(QDialog):
    """Paste-a-URL dialog for approving Steam QR logins."""

    def __init__(self, auth_manager: AuthenticationManager, account: AccountData, parent=None):
        super().__init__(parent)
        self._auth = auth_manager
        self._account = account
        self._worker: _QrApproveWorker | None = None

        self.setWindowTitle("QR Login")
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build_ui()
        self._apply_theme()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Approve QR Login")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)

        account_label = QLabel(f"Account: {self._account.account_name}")
        account_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(account_label)

        hint = QLabel(
            "Paste the Steam QR login URL (from scanning the 'Sign in on computer' QR)."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://s.team/q/1/12345678901234567890…")
        self.url_input.setMinimumHeight(40)
        self.url_input.textChanged.connect(self._update_buttons)
        layout.addWidget(self.url_input)

        paste_row = QHBoxLayout()
        paste_row.setSpacing(8)
        self.paste_button = QPushButton("Paste from Clipboard")
        self.paste_button.clicked.connect(self._paste_from_clipboard)
        paste_row.addWidget(self.paste_button)
        paste_row.addStretch()
        layout.addLayout(paste_row)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Action buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.deny_button = QPushButton("Deny")
        self.deny_button.clicked.connect(lambda: self._run(confirm=False))
        self.approve_button = QPushButton("Approve")
        self.approve_button.setDefault(True)
        self.approve_button.clicked.connect(lambda: self._run(confirm=True))
        button_row.addWidget(self.cancel_button)
        button_row.addStretch()
        button_row.addWidget(self.deny_button)
        button_row.addWidget(self.approve_button)
        layout.addLayout(button_row)

        self._update_buttons()

    def _apply_theme(self):
        theme = ThemeManager.get_current_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.BACKGROUND};
                color: {theme.TEXT_PRIMARY};
            }}
            QLabel {{
                color: {theme.TEXT_PRIMARY};
                background: transparent;
            }}
            QLineEdit {{
                background-color: {theme.SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 2px solid {theme.BORDER};
                border-radius: 8px;
                padding: 8px 12px;
            }}
            QLineEdit:focus {{
                border-color: {theme.BORDER_FOCUS};
            }}
            QPushButton {{
                background-color: {theme.SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 96px;
            }}
            QPushButton:hover {{
                background-color: {theme.SURFACE_HOVER};
            }}
            QPushButton:disabled {{
                color: {theme.TEXT_TERTIARY};
            }}
        """)
        # Highlight the primary action.
        self.approve_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 96px;
            }}
            QPushButton:hover {{ background-color: {theme.ACCENT_HOVER}; }}
            QPushButton:disabled {{ background-color: {theme.BORDER}; color: {theme.TEXT_TERTIARY}; }}
        """)
        self.deny_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.ERROR};
                border: 1px solid {theme.ERROR};
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 96px;
            }}
            QPushButton:hover {{ background-color: {theme.SURFACE_HOVER}; }}
        """)

    def _update_buttons(self):
        has_url = bool(self.url_input.text().strip())
        busy = self._worker is not None
        self.approve_button.setEnabled(has_url and not busy)
        self.deny_button.setEnabled(has_url and not busy)
        self.paste_button.setEnabled(not busy)
        self.url_input.setEnabled(not busy)

    def _paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = (clipboard.text() or '').strip()
        if text:
            self.url_input.setText(text)
            return

        # Try decoding an image on the clipboard if the optional deps exist.
        image = clipboard.image()
        if image.isNull():
            self._show_status("Clipboard is empty.", error=True)
            return
        decoded = self._decode_qr_from_qimage(image)
        if decoded:
            self.url_input.setText(decoded)
        else:
            self._show_status(
                "Couldn't read a QR code from the clipboard image. "
                "Install pyzbar + Pillow, or paste the URL directly.",
                error=True,
            )

    def _decode_qr_from_qimage(self, qimage) -> str | None:
        try:
            from PIL import Image  # type: ignore
            from pyzbar.pyzbar import decode  # type: ignore
        except Exception:
            return None
        try:
            from PyQt5.QtCore import QBuffer, QIODevice
            buf = QBuffer()
            buf.open(QIODevice.ReadWrite)
            qimage.save(buf, "PNG")
            buf.seek(0)
            import io
            pil = Image.open(io.BytesIO(bytes(buf.data())))
            results = decode(pil)
            for r in results:
                data = r.data.decode('utf-8', errors='ignore')
                if data:
                    return data
        except Exception:
            return None
        return None

    def _run(self, confirm: bool):
        url = self.url_input.text().strip()
        if not url:
            return
        self._show_status("Contacting Steam…", error=False)
        self._worker = _QrApproveWorker(self._auth, self._account, url, confirm, self)
        self._worker.finished_result.connect(self._on_finished)
        self._update_buttons()
        self._worker.start()

    def _on_finished(self, result: dict):
        self._worker = None
        self._update_buttons()
        if result.get('success'):
            confirmed = result.get('confirmed', True)
            msg = "Login approved." if confirmed else "Login denied."
            QMessageBox.information(self, "QR Login", msg)
            self.accept()
        else:
            self._show_status(result.get('error') or 'Unknown error', error=True)

    def _show_status(self, text: str, error: bool):
        theme = ThemeManager.get_current_theme()
        colour = theme.ERROR if error else theme.TEXT_SECONDARY
        self.status_label.setStyleSheet(f"color: {colour}; background: transparent;")
        self.status_label.setText(text)
        self.status_label.setVisible(True)
