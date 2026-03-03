import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QProgressBar, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from src.account_manager import AccountData
from src.settings import SettingsManager
from src.theme import ThemeManager


class AccountsScreen(QWidget):
    """Screen for displaying and managing accounts"""

    # Signal for when the auth code label is clicked
    code_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.selected_account = None
        self.refresh_timer = None
        self.code_timer = None
        self.copy_on_click_enabled = SettingsManager.get_setting("copy_code_on_click")
        self.setup_ui()

    def setup_ui(self):
        """Setup the accounts screen UI"""
        current_theme = ThemeManager.get_current_theme()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # ── Header section ──────────────────────────────────────────────
        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        # Auth code / app title label
        self.title_label = QLabel("SDA")
        self.title_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setCursor(Qt.PointingHandCursor)
        self.title_label.setToolTip("Click to copy code")
        self.title_label.mousePressEvent = self.on_code_clicked
        header_layout.addWidget(self.title_label)

        # Account name / status subtitle
        self.subtitle_label = QLabel("No account selected")
        self.subtitle_label.setFont(QFont("Segoe UI", 12))
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.subtitle_label)

        layout.addLayout(header_layout)

        # ── Code expiry progress bar (hidden until account selected) ────
        self.code_timer_bar = QProgressBar()
        self.code_timer_bar.setRange(0, 30)
        self.code_timer_bar.setValue(30)
        self.code_timer_bar.setFixedHeight(5)
        self.code_timer_bar.setTextVisible(False)
        self.code_timer_bar.setVisible(False)
        layout.addWidget(self.code_timer_bar)

        # ── Search bar ───────────────────────────────────────────────────
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by account name or Steam ID…")
        self.search_input.setMinimumHeight(48)
        layout.addWidget(self.search_input)

        # ── Accounts scroll area ─────────────────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.accounts_widget = QWidget()
        self.accounts_layout = QVBoxLayout(self.accounts_widget)
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(6)

        # Empty state (position 0 – shown when no accounts exist)
        self.empty_state_widget = self._build_empty_state()
        self.accounts_layout.addWidget(self.empty_state_widget)

        # Trailing stretch keeps accounts pinned to top
        self.accounts_layout.addStretch()

        self.scroll_area.setWidget(self.accounts_widget)
        layout.addWidget(self.scroll_area)

        # Apply initial styles
        self._apply_label_styles()
        self._apply_search_style()

        # Start the code-expiry countdown timer (always ticking)
        self._start_code_timer()

    # ── Empty state ──────────────────────────────────────────────────────

    def _build_empty_state(self) -> QWidget:
        """Create the empty-state widget shown when no accounts are added."""
        current_theme = ThemeManager.get_current_theme()

        widget = QWidget()
        widget.setMinimumHeight(260)
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(10)

        icon = QLabel("🔐")
        icon.setFont(QFont("Segoe UI", 44))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background: transparent; border: none;")
        vbox.addWidget(icon)

        title = QLabel("No accounts yet")
        title.setFont(QFont("Segoe UI", 15, QFont.Medium))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {current_theme.TEXT_SECONDARY}; background: transparent; border: none;")
        vbox.addWidget(title)

        hint = QLabel("Tap  ＋  below to add your first account")
        hint.setFont(QFont("Segoe UI", 11))
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {current_theme.TEXT_TERTIARY}; background: transparent; border: none;")
        vbox.addWidget(hint)

        return widget

    def set_has_accounts(self, has: bool):
        """Show or hide the empty-state placeholder."""
        self.empty_state_widget.setVisible(not has)

    # ── Code-expiry countdown ────────────────────────────────────────────

    def _start_code_timer(self):
        self.code_timer = QTimer(self)
        self.code_timer.timeout.connect(self._tick_code_timer)
        self.code_timer.start(1000)

    def _tick_code_timer(self):
        """Update the expiry progress bar every second."""
        if not self.selected_account or not self.code_timer_bar.isVisible():
            return
        remaining = 30 - (int(time.time()) % 30)
        self.code_timer_bar.setValue(remaining)

        current_theme = ThemeManager.get_current_theme()
        if remaining > 10:
            bar_color = current_theme.SUCCESS
        elif remaining > 5:
            bar_color = "#F5A623"
        else:
            bar_color = current_theme.ERROR

        self.code_timer_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {current_theme.BORDER};
                border-radius: 2px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 2px;
            }}
        """)

    # ── Clipboard copy ───────────────────────────────────────────────────

    def on_code_clicked(self, event):
        """Handle click on the auth code label – copy to clipboard."""
        if not (self.selected_account and self.copy_on_click_enabled):
            return
        code = self.title_label.text()
        if code and code not in ("SDA", "..."):
            QApplication.clipboard().setText(code)
            original = code
            self.title_label.setText("Copied!")
            QTimer.singleShot(900, lambda: self.title_label.setText(original))

    # ── Auto-refresh ─────────────────────────────────────────────────────

    def start_auto_refresh(self):
        """Start periodic auth code refresh."""
        if self.refresh_timer:
            self.refresh_timer.stop()
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_auth_code)
        interval_ms = SettingsManager.get_setting("auto_refresh_interval_seconds") * 1000
        self.refresh_timer.start(interval_ms)

    def stop_auto_refresh(self):
        if self.refresh_timer:
            self.refresh_timer.stop()
            self.refresh_timer = None

    def refresh_auth_code(self):
        if self.selected_account and self.parent_window:
            code = self.parent_window.auth_manager.generate_auth_code(self.selected_account)
            self.title_label.setText(code)

    def set_selected_account(self, account):
        """Set the selected account and manage timers/progress bar."""
        self.selected_account = account
        if account:
            self.code_timer_bar.setVisible(True)
            self._tick_code_timer()
            if SettingsManager.get_setting("auto_refresh_enabled"):
                self.start_auto_refresh()
        else:
            self.code_timer_bar.setVisible(False)
            self.stop_auto_refresh()

    # ── Account selection passthrough ────────────────────────────────────

    def on_account_selected(self, selected_widget):
        if self.parent_window:
            self.parent_window.on_account_selected(selected_widget)

    # ── Settings / theme ─────────────────────────────────────────────────

    def apply_settings(self):
        self.copy_on_click_enabled = SettingsManager.get_setting("copy_code_on_click")
        auto_refresh_enabled = SettingsManager.get_setting("auto_refresh_enabled")
        if self.selected_account and auto_refresh_enabled:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()

    def update_theme(self):
        """Re-apply theme colours to all dynamically-styled elements."""
        self._apply_label_styles()
        self._apply_search_style()
        self._tick_code_timer()
        # Rebuild empty state labels with new theme colours
        current_theme = ThemeManager.get_current_theme()
        labels = self.empty_state_widget.findChildren(QLabel)
        if len(labels) >= 3:
            labels[1].setStyleSheet(
                f"color: {current_theme.TEXT_SECONDARY}; background: transparent; border: none;"
            )
            labels[2].setStyleSheet(
                f"color: {current_theme.TEXT_TERTIARY}; background: transparent; border: none;"
            )

    def _apply_label_styles(self):
        current_theme = ThemeManager.get_current_theme()
        self.title_label.setStyleSheet(
            f"color: {current_theme.TEXT_PRIMARY}; background: transparent;"
        )
        self.subtitle_label.setStyleSheet(
            f"color: {current_theme.TEXT_SECONDARY}; background: transparent;"
        )

    def _apply_search_style(self):
        current_theme = ThemeManager.get_current_theme()
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {current_theme.SURFACE};
                border: 2px solid {current_theme.BORDER};
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                color: {current_theme.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {current_theme.BORDER_FOCUS};
                background-color: {current_theme.SURFACE_HOVER};
            }}
            QLineEdit::placeholder {{
                color: {current_theme.TEXT_TERTIARY};
            }}
        """)
