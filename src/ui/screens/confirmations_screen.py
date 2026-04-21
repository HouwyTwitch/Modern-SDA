from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from src.account_manager import AccountData
from src.ui.confirmation_item import ConfirmationItem
from src.theme import ThemeManager
from src.settings import SettingsManager


class ConfirmationsScreen(QWidget):
    """Screen for displaying trade confirmations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.confirmation_items = []
        self.selected_account = None
        self.is_loading = False
        # Background polling timer (ported from Android's background sync)
        self._auto_refresh_timer = QTimer(self)
        self._auto_refresh_timer.timeout.connect(self._on_auto_refresh_tick)
        # Remember IDs of auto-confirmed items so we don't attempt twice
        self._auto_confirmed_ids = set()
        self.setup_ui()
        self.show_no_account_selected()
        self._apply_auto_refresh_setting()

    def _get_main_window(self):
        """Safely obtain reference to the main window regardless of current parent."""
        if self.parent_window:
            return self.parent_window
        try:
            p = self.parent()
            while p is not None:
                if hasattr(p, 'account_manager') and hasattr(p, 'auth_manager'):
                    return p
                p = p.parent()
        except Exception:
            pass
        return None

    def setup_ui(self):
        """Setup the confirmations screen UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header row: Accept All (left) + Refresh (right)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 10)
        header_layout.setSpacing(12)

        # Accept All button — only shown when there are >=2 pending confirmations.
        # Ported from the Android app.
        self.accept_all_button = QPushButton("Accept All")
        self.accept_all_button.setMinimumHeight(40)
        self.accept_all_button.setCursor(Qt.PointingHandCursor)
        self.accept_all_button.clicked.connect(self._on_accept_all_clicked)
        self.accept_all_button.setVisible(False)
        header_layout.addWidget(self.accept_all_button)

        header_layout.addStretch()

        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setFixedSize(44, 44)
        self.refresh_button.setToolTip("Refresh Confirmations")
        self.refresh_button.clicked.connect(self.refresh_confirmations)
        header_layout.addWidget(self.refresh_button)
        main_layout.addLayout(header_layout)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.scroll_content = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_content)
        scroll_layout.setContentsMargins(20, 10, 20, 20)
        scroll_layout.setSpacing(12)

        # Status container
        self.status_container = QWidget()
        self.status_layout = QVBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0, 40, 0, 40)
        self.status_layout.setSpacing(16)

        self.status_icon = QLabel()
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setFont(QFont("Segoe UI", 48))
        self.status_layout.addWidget(self.status_icon)

        self.status_text = QLabel()
        self.status_text.setAlignment(Qt.AlignCenter)
        self.status_text.setFont(QFont("Segoe UI", 14))
        self.status_text.setWordWrap(True)
        self.status_layout.addWidget(self.status_text)

        scroll_layout.addWidget(self.status_container)

        self.confirmations_container = QWidget()
        self.confirmations_layout = QVBoxLayout(self.confirmations_container)
        self.confirmations_layout.setContentsMargins(0, 0, 0, 0)
        self.confirmations_layout.setSpacing(8)
        scroll_layout.addWidget(self.confirmations_container)
        scroll_layout.addStretch()

        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)

        self.apply_theme()

    # ── Visibility helpers ──────────────────────────────────────────────

    def show_no_account_selected(self):
        self.status_container.setVisible(True)
        self.confirmations_container.setVisible(False)
        self.refresh_button.setEnabled(False)
        self.accept_all_button.setVisible(False)

        self.status_icon.setText("👤")
        self.status_icon.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_TERTIARY};")
        self.status_text.setText("Select an account to view confirmations")
        self.status_text.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};")

    def show_loading(self):
        self.status_container.setVisible(True)
        self.confirmations_container.setVisible(False)
        self.refresh_button.setEnabled(False)
        self.accept_all_button.setVisible(False)
        self.is_loading = True

        self.status_icon.setText("⏳")
        self.status_icon.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};")
        self.status_text.setText("Loading confirmations...")
        self.status_text.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};")

    def show_no_confirmations(self):
        self.status_container.setVisible(True)
        self.confirmations_container.setVisible(False)
        self.refresh_button.setEnabled(True)
        self.accept_all_button.setVisible(False)
        self.is_loading = False

        self.status_icon.setText("✅")
        self.status_icon.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_TERTIARY};")
        self.status_text.setText("No confirmations at this moment")
        self.status_text.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};")

    def show_confirmations(self):
        self.status_container.setVisible(False)
        self.confirmations_container.setVisible(True)
        self.refresh_button.setEnabled(True)
        self.is_loading = False
        # Reveal Accept All once at least two pending items exist
        self._update_accept_all_visibility()

    def _update_accept_all_visibility(self):
        count = len([i for i in self.confirmation_items if not i.is_processing])
        self.accept_all_button.setVisible(count >= 2)
        self.accept_all_button.setText(f"Accept All ({count})" if count >= 2 else "Accept All")

    def on_account_selected(self, account):
        self.selected_account = account
        self._auto_confirmed_ids.clear()

        if account is None:
            self.show_no_account_selected()
            self.clear_confirmations()
        else:
            self.load_confirmations_for_account(account)

    def refresh_confirmations(self):
        if not self.selected_account and self.parent_window:
            self.selected_account = getattr(self.parent_window, 'selected_account', None)

        if self.selected_account and not self.is_loading:
            self.load_confirmations_for_account(self.selected_account)

    def load_confirmations_for_account(self, account):
        self.show_loading()
        self.clear_confirmations()
        self._load_real_confirmations_for_account(account)

    def _load_real_confirmations_for_account(self, account):
        if not self.selected_account or self.selected_account != account:
            return

        main_window = self._get_main_window()
        if not main_window:
            self._show_error_state("Main window not available")
            return

        if not hasattr(main_window, 'confirmation_manager') or not hasattr(main_window, 'auth_manager'):
            self._show_error_state("Managers not initialized")
            return

        try:
            authm = main_window.auth_manager
            steam_id_str = str(account.steam_id)
            if steam_id_str not in getattr(authm, '_steam_clients', {}):
                self._async_login_then_load(account, main_window)
                return
        except Exception:
            pass

        self._async_load_confirmations(account, main_window)

    def _async_login_then_load(self, account, main_window):
        try:
            from PyQt5.QtCore import QThread

            class LoginLoader(QThread):
                def __init__(self, auth_manager, account):
                    super().__init__()
                    self.auth_manager = auth_manager
                    self.account = account
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        fut = self.auth_manager.submit(self.auth_manager.login_account(self.account))
                        self.result = fut.result()
                    except Exception as e:
                        self.error = str(e)

            loader = LoginLoader(main_window.auth_manager, account)
            loader.finished.connect(lambda: self._on_login_then_load_finished(loader, account, main_window))
            loader.start()
        except Exception as e:
            self._show_error_state(f"Failed to start login: {e}")

    def _on_login_then_load_finished(self, loader, account, main_window):
        if loader.error:
            self._show_error_state(f"Login failed: {loader.error}")
            return
        result = loader.result or {}
        if not result.get('success'):
            self._show_error_state(result.get('error', 'Login failed'))
            return
        self._async_load_confirmations(account, main_window)

    def _async_load_confirmations(self, account, main_window):
        try:
            from PyQt5.QtCore import QThread

            class ConfirmationLoader(QThread):
                def __init__(self, confirmation_manager, auth_manager, account):
                    super().__init__()
                    self.confirmation_manager = confirmation_manager
                    self.auth_manager = auth_manager
                    self.account = account
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        fut = self.auth_manager.submit(
                            self.confirmation_manager.load_confirmations(self.account, self.auth_manager)
                        )
                        self.result = fut.result()
                    except Exception as e:
                        self.error = str(e)

            loader = ConfirmationLoader(
                main_window.confirmation_manager,
                main_window.auth_manager,
                account,
            )
            loader.finished.connect(lambda: self._on_confirmations_loaded(loader, account))
            loader.start()
        except Exception as e:
            self._show_error_state(f"Failed to load confirmations: {e}")

    def _on_confirmations_loaded(self, loader, account):
        if not self.selected_account or self.selected_account != account:
            return

        try:
            if loader.error:
                print(f"Error loading confirmations: {loader.error}")
                self._show_error_state(f"Failed to load: {loader.error}")
                return

            result = loader.result
            if not result or not result.get('success', False):
                error_text = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Unknown error'
                print(f"Failed to load confirmations: {error_text}")
                self.show_no_confirmations()
                return

            self.clear_confirmations()
            confirmations = result.get('confirmations', [])

            if not confirmations:
                self.show_no_confirmations()
            else:
                self.show_confirmations()
                for confirmation in confirmations:
                    conf_type = confirmation.get('type', 'UNKNOWN')
                    description = confirmation.get('description')
                    if not description:
                        summary = confirmation.get('summary') or ''
                        if conf_type == 'TRADE':
                            description = f"Trade: {summary}"
                        elif conf_type in ('LISTING', 'MARKET'):
                            description = f"Market: {summary}"
                        else:
                            description = f"Confirmation {confirmation.get('id', 'N/A')}"
                    confirmation_id = str(confirmation.get('id', ''))
                    self.add_confirmation_item(conf_type, description, confirmation_id)

                # After the list is populated, run any enabled auto-confirm rules.
                self._auto_confirm_if_enabled()
                self._update_accept_all_visibility()

        except Exception as e:
            print(f"Error processing confirmations: {e}")
            self._show_error_state("Failed to process confirmations")

    # ── Item management ────────────────────────────────────────────────

    def clear_confirmations(self):
        for item in self.confirmation_items[:]:
            self.remove_confirmation_item(item)
        self._update_accept_all_visibility()

    def add_confirmation_item(self, confirmation_type: str, description: str, confirmation_id: str = None):
        item = ConfirmationItem(confirmation_type, description, confirmation_id)
        item.confirmation_accepted.connect(self.on_accept_confirmation)
        item.confirmation_declined.connect(self.on_decline_confirmation)

        self.confirmation_items.append(item)
        self.confirmations_layout.addWidget(item)
        self._update_accept_all_visibility()

    def _find_item(self, confirmation_id: str):
        for item in self.confirmation_items:
            if item.confirmation_id == confirmation_id:
                return item
        return None

    def on_accept_confirmation(self, confirmation_id: str):
        # Don't remove the widget yet — let the processing spinner run and
        # drop the row after the worker returns success.
        main_window = self._get_main_window()
        if main_window:
            main_window.on_accept_confirmation(confirmation_id)

    def on_decline_confirmation(self, confirmation_id: str):
        main_window = self._get_main_window()
        if main_window:
            main_window.on_decline_confirmation(confirmation_id)

    def remove_confirmation_item(self, item: ConfirmationItem):
        if item in self.confirmation_items:
            self.confirmation_items.remove(item)
            self.confirmations_layout.removeWidget(item)
            item.setParent(None)
            item.deleteLater()
            self._update_accept_all_visibility()

    def apply_theme(self):
        """Apply current theme to all confirmation items and UI elements"""
        current_theme = ThemeManager.get_current_theme()

        refresh_svg = '''
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 12C4 16.4183 7.58172 20 12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C9.25022 4 6.82447 5.38734 5.38451 7.50024" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 7H5V4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
        refresh_icon = current_theme.create_svg_icon(
            refresh_svg,
            current_theme.TEXT_PRIMARY,
            20,
        )
        self.refresh_button.setIcon(refresh_icon)
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.SURFACE_ELEVATED};
                border: 2px solid {current_theme.BORDER};
                border-radius: 12px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {current_theme.SURFACE_HOVER};
                border-color: {current_theme.BORDER_FOCUS};
            }}
            QPushButton:pressed {{
                background-color: {current_theme.ACCENT};
            }}
        """)

        self.accept_all_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {current_theme.SUCCESS};
                border: none;
                border-radius: 8px;
                padding: 6px 18px;
                font-weight: 600;
                color: {current_theme.TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {current_theme.SUCCESS_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {current_theme.SURFACE_ELEVATED};
                color: {current_theme.TEXT_TERTIARY};
            }}
        """)

        self.status_icon.setStyleSheet(f"color: {current_theme.TEXT_TERTIARY};")
        self.status_text.setStyleSheet(f"color: {current_theme.TEXT_SECONDARY};")

        for item in self.confirmation_items:
            item.apply_styling()

    # ── Accept All ─────────────────────────────────────────────────────

    def _on_accept_all_clicked(self):
        if not self.selected_account:
            return
        # Disable while bulk op runs and mark all items as processing for
        # clear visual feedback.
        self.accept_all_button.setEnabled(False)
        for item in self.confirmation_items:
            item.set_processing(True)
        self._run_accept_all()

    def _run_accept_all(self, type_filter: str = None):
        main_window = self._get_main_window()
        if not main_window:
            return
        try:
            from PyQt5.QtCore import QThread

            class BulkAcceptWorker(QThread):
                def __init__(self, confirmation_manager, auth_manager, steam_id, type_filter):
                    super().__init__()
                    self.confirmation_manager = confirmation_manager
                    self.auth_manager = auth_manager
                    self.steam_id = steam_id
                    self.type_filter = type_filter
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        fut = self.auth_manager.submit(
                            self.confirmation_manager.accept_all_confirmations(
                                self.steam_id, self.auth_manager, type_filter=self.type_filter,
                            )
                        )
                        self.result = fut.result()
                    except Exception as e:
                        self.error = str(e)

            worker = BulkAcceptWorker(
                main_window.confirmation_manager,
                main_window.auth_manager,
                str(self.selected_account.steam_id),
                type_filter,
            )
            worker.finished.connect(lambda: self._on_accept_all_finished(worker, type_filter))
            worker.start()
        except Exception as e:
            print(f"Failed to start bulk accept: {e}")
            self.accept_all_button.setEnabled(True)

    def _on_accept_all_finished(self, worker, type_filter):
        try:
            self.accept_all_button.setEnabled(True)

            if worker.error:
                self._show_error_state(f"Accept all failed: {worker.error}", temporary=True)
                for item in self.confirmation_items:
                    item.set_processing(False)
                return

            result = worker.result or {}
            accepted_ids = set(str(i) for i in result.get('accepted', []))
            failed = result.get('failed', [])

            # Remove the accepted rows
            for item in list(self.confirmation_items):
                if str(item.confirmation_id) in accepted_ids:
                    self.remove_confirmation_item(item)
                else:
                    # The filter may have left some rows untouched; clear their
                    # processing state.
                    item.set_processing(False)

            if not self.confirmation_items:
                self.show_no_confirmations()
            else:
                self._update_accept_all_visibility()

            if failed:
                self._show_error_state(
                    f"{len(accepted_ids)} accepted, {len(failed)} failed",
                    temporary=True,
                )
        except Exception as e:
            print(f"Error in bulk accept finish: {e}")

    # ── Auto-confirm (trades / market) ──────────────────────────────────

    def _auto_confirm_if_enabled(self):
        """After a confirmation refresh, apply auto-confirm rules when set.

        Ported from Android: user can opt into auto-accepting all pending
        market-listing or trade confirmations.
        """
        auto_trades = SettingsManager.get_setting("auto_confirm_trades")
        auto_market = SettingsManager.get_setting("auto_confirm_market")

        if not (auto_trades or auto_market):
            return

        pending = [i for i in self.confirmation_items
                   if i.confirmation_id not in self._auto_confirmed_ids]

        should_run = False
        for item in pending:
            raw = (item.confirmation_type or "").upper()
            if auto_trades and raw == "TRADE":
                should_run = True
                self._auto_confirmed_ids.add(item.confirmation_id)
                item.set_processing(True)
            elif auto_market and raw in ("MARKET", "LISTING", "CREATE_LISTING"):
                should_run = True
                self._auto_confirmed_ids.add(item.confirmation_id)
                item.set_processing(True)

        if not should_run:
            return

        # Run both types one after another. If only one is enabled, only that
        # type is processed.
        if auto_trades:
            self._run_accept_all(type_filter="TRADE")
        if auto_market:
            # Queue market after a short delay so the two passes don't stomp
            # on each other's progress updates.
            QTimer.singleShot(300, lambda: self._run_accept_all(type_filter="MARKET"))

    # ── Background auto-refresh ─────────────────────────────────────────

    def _apply_auto_refresh_setting(self):
        """Start/stop the background polling timer from current settings."""
        enabled = SettingsManager.get_setting("auto_refresh_confirmations_enabled")
        interval = SettingsManager.get_setting("auto_refresh_confirmations_interval_seconds")
        self._auto_refresh_timer.stop()
        if enabled and isinstance(interval, int) and interval > 0:
            self._auto_refresh_timer.start(max(15, interval) * 1000)

    def apply_settings(self):
        """Called by the main window whenever settings change."""
        self._apply_auto_refresh_setting()

    def _on_auto_refresh_tick(self):
        if self.is_loading or self.selected_account is None:
            return
        # Don't steal focus from the user; silently re-fetch.
        self.load_confirmations_for_account(self.selected_account)

    # ── Processing callbacks from main window ───────────────────────────

    def process_accept_confirmation(self, confirmation_id):
        """Handle accepting a confirmation"""
        if not self.selected_account:
            return
        main_window = self._get_main_window()
        if not main_window or not hasattr(main_window, 'confirmation_manager') or not hasattr(main_window, 'auth_manager'):
            self._show_error_state("Unable to process confirmation", temporary=True)
            return
        QTimer.singleShot(100, lambda: self._async_process_confirmation(confirmation_id, True, main_window))

    def process_decline_confirmation(self, confirmation_id):
        """Handle declining a confirmation"""
        if not self.selected_account:
            return
        main_window = self._get_main_window()
        if not main_window or not hasattr(main_window, 'confirmation_manager') or not hasattr(main_window, 'auth_manager'):
            self._show_error_state("Unable to process confirmation", temporary=True)
            return
        self._async_process_confirmation(confirmation_id, False, main_window)

    def _async_process_confirmation(self, confirmation_id, accept, main_window):
        try:
            from PyQt5.QtCore import QThread

            class ConfirmationProcessor(QThread):
                def __init__(self, confirmation_manager, auth_manager, steam_id, confirmation_id, accept):
                    super().__init__()
                    self.confirmation_manager = confirmation_manager
                    self.auth_manager = auth_manager
                    self.steam_id = steam_id
                    self.confirmation_id = confirmation_id
                    self.accept = accept
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        if self.accept:
                            fut = self.auth_manager.submit(
                                self.confirmation_manager.accept_confirmation(
                                    self.steam_id, self.confirmation_id, self.auth_manager,
                                )
                            )
                        else:
                            fut = self.auth_manager.submit(
                                self.confirmation_manager.decline_confirmation(
                                    self.steam_id, self.confirmation_id, self.auth_manager,
                                )
                            )
                        self.result = fut.result()
                    except Exception as e:
                        self.error = str(e)

            processor = ConfirmationProcessor(
                main_window.confirmation_manager,
                main_window.auth_manager,
                str(self.selected_account.steam_id),
                confirmation_id,
                accept,
            )
            processor.finished.connect(lambda: self._on_confirmation_processed(processor, confirmation_id))
            processor.start()
        except Exception as e:
            self._show_error_state(f"Failed to process confirmation: {e}", temporary=True)

    def _on_confirmation_processed(self, processor, confirmation_id):
        try:
            item = self._find_item(confirmation_id)

            if processor.error:
                print(f"Error processing confirmation: {processor.error}")
                if item:
                    item.set_processing(False)
                self._show_error_state(f"Could not process: {processor.error}", temporary=True)
                return

            result = processor.result
            if not result or not result.get('success', False):
                error_msg = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Unknown error'
                print(f"Failed to process confirmation: {error_msg}")
                if item:
                    item.set_processing(False)
                self._show_error_state(f"Could not process: {error_msg}", temporary=True)
                return

            # Success — drop the row.
            if item:
                self.remove_confirmation_item(item)

            if not self.confirmation_items:
                self.show_no_confirmations()
            else:
                self._update_accept_all_visibility()

        except Exception as e:
            print(f"Error handling confirmation result: {e}")

    def _show_error_state(self, message: str, temporary: bool = False):
        current_theme = ThemeManager.get_current_theme()
        self.status_container.setVisible(True)
        self.confirmations_container.setVisible(False)
        self.refresh_button.setEnabled(True)
        self.accept_all_button.setVisible(False)
        self.is_loading = False

        self.status_icon.setText("⚠️")
        self.status_icon.setStyleSheet(f"color: {current_theme.ERROR};")
        self.status_text.setText(message)
        self.status_text.setStyleSheet(f"color: {current_theme.TEXT_SECONDARY};")

        if temporary:
            QTimer.singleShot(3000, self._restore_confirmations_view)

    def _restore_confirmations_view(self):
        if self.confirmation_items:
            self.show_confirmations()
        else:
            self.show_no_confirmations()
