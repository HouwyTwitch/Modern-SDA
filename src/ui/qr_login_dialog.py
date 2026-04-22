"""QR login approval dialog.

Lets the user approve (or deny) a Steam QR login request on behalf of the
selected account by **decoding a QR code image from the clipboard** — the
same flow as the Android app. The user takes a screenshot of the "Sign in on
computer" QR, copies the image to the clipboard, opens this dialog, and the
URL is extracted automatically. A file-picker fallback accepts .png/.jpg
screenshots, and the URL can still be pasted as text if preferred.

Requires ``pyzbar`` + ``Pillow`` for image decoding.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QApplication, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from src.account_manager import AccountData, AuthenticationManager
from src.theme import ThemeManager


def _qr_decoder_available() -> bool:
    """Return True when pyzbar + Pillow are importable."""
    try:
        from PIL import Image  # noqa: F401
        from pyzbar.pyzbar import decode  # noqa: F401
        return True
    except Exception:
        return False


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
    """QR-image-first dialog for approving Steam QR logins."""

    def __init__(self, auth_manager: AuthenticationManager, account: AccountData, parent=None):
        super().__init__(parent)
        self._auth = auth_manager
        self._account = account
        self._worker: _QrApproveWorker | None = None

        self.setWindowTitle("QR Login")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()
        self._apply_theme()

        # Auto-decode whatever is already on the clipboard as soon as we open.
        QTimer.singleShot(0, self._try_decode_clipboard_silent)

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
            "Copy a screenshot of Steam's QR code to your clipboard, then click "
            "\"Decode QR from Clipboard\". The sign-in URL will be extracted "
            "automatically."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # Primary action row — image-based decoding
        image_row = QHBoxLayout()
        image_row.setSpacing(8)
        self.decode_clipboard_button = QPushButton("Decode QR from Clipboard")
        self.decode_clipboard_button.setMinimumHeight(40)
        self.decode_clipboard_button.clicked.connect(self._decode_from_clipboard)
        image_row.addWidget(self.decode_clipboard_button, 1)

        self.open_image_button = QPushButton("Open Image…")
        self.open_image_button.setMinimumHeight(40)
        self.open_image_button.clicked.connect(self._decode_from_file)
        image_row.addWidget(self.open_image_button)
        layout.addLayout(image_row)

        # Show the decoded URL (or let the user paste one as a fallback).
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Decoded URL appears here — or paste one manually")
        self.url_input.setMinimumHeight(40)
        self.url_input.textChanged.connect(self._update_buttons)
        layout.addWidget(self.url_input)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # If the optional deps are missing, say so upfront.
        if not _qr_decoder_available():
            self._show_status(
                "QR image decoding needs extra packages. Install with: "
                "pip install pyzbar Pillow",
                error=True,
            )
            self.decode_clipboard_button.setEnabled(False)
            self.open_image_button.setEnabled(False)

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
        self.decode_clipboard_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {theme.ACCENT_HOVER}; }}
            QPushButton:disabled {{ background-color: {theme.BORDER}; color: {theme.TEXT_TERTIARY}; }}
        """)
        self.approve_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.SUCCESS};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 96px;
            }}
            QPushButton:hover {{ background-color: {theme.SUCCESS_HOVER}; }}
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
        self.url_input.setEnabled(not busy)
        if _qr_decoder_available():
            self.decode_clipboard_button.setEnabled(not busy)
            self.open_image_button.setEnabled(not busy)

    # ── Image-based decoding ────────────────────────────────────────────

    def _try_decode_clipboard_silent(self):
        """On open, attempt a silent clipboard decode so the user can just click Approve."""
        if not _qr_decoder_available():
            return
        clipboard = QApplication.clipboard()
        image = clipboard.image()
        if image.isNull():
            return
        decoded = self._decode_qr_from_qimage(image)
        if decoded:
            self.url_input.setText(decoded)
            self._show_status("QR decoded from clipboard image.", error=False)

    def _decode_from_clipboard(self):
        if not _qr_decoder_available():
            self._show_status(
                "Install pyzbar + Pillow first: pip install pyzbar Pillow",
                error=True,
            )
            return
        clipboard = QApplication.clipboard()
        image = clipboard.image()
        if image.isNull():
            # No image on the clipboard — but maybe the user copied text this time.
            text = (clipboard.text() or '').strip()
            if text:
                self.url_input.setText(text)
                self._show_status("Loaded URL from clipboard text.", error=False)
                return
            self._show_status(
                "Clipboard is empty. Copy a QR screenshot or URL first.",
                error=True,
            )
            return

        decoded = self._decode_qr_from_qimage(image)
        if decoded:
            self.url_input.setText(decoded)
            self._show_status("QR decoded from clipboard image.", error=False)
        else:
            self._show_status(
                "Couldn't find a QR code in the clipboard image.",
                error=True,
            )

    def _decode_from_file(self):
        if not _qr_decoder_available():
            self._show_status(
                "Install pyzbar + Pillow first: pip install pyzbar Pillow",
                error=True,
            )
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select QR Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)",
        )
        if not path:
            return
        decoded = self._decode_qr_from_path(path)
        if decoded:
            self.url_input.setText(decoded)
            self._show_status("QR decoded from file.", error=False)
        else:
            self._show_status("Couldn't find a QR code in that image.", error=True)

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
            return self._decode_pil(pil)
        except Exception:
            return None

    def _decode_qr_from_path(self, path: str) -> str | None:
        try:
            from PIL import Image  # type: ignore
        except Exception:
            return None
        try:
            with Image.open(path) as pil:
                return self._decode_pil(pil)
        except Exception:
            return None

    @staticmethod
    def _decode_pil(pil_image) -> str | None:
        """Decode a PIL image, trying a grayscale pass if colour fails."""
        try:
            from pyzbar.pyzbar import decode  # type: ignore
        except Exception:
            return None
        try:
            for candidate in (pil_image, pil_image.convert('L')):
                for result in decode(candidate):
                    data = result.data.decode('utf-8', errors='ignore')
                    if data:
                        return data
        except Exception:
            return None
        return None

    # ── Approve / Deny ──────────────────────────────────────────────────

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
