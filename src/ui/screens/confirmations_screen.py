import sys
import json
import os
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy,
    QSpacerItem, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QStackedWidget, QButtonGroup, QComboBox, QFileDialog,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QByteArray
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QIcon
from PyQt5.QtSvg import QSvgRenderer
from urllib.request import urlopen
from urllib.error import URLError

# Import account management classes
from src.account_manager import AccountData, AccountManager, AuthenticationManager, ConfirmationManager
from src.ui.confirmation_item import ConfirmationItem
from src.theme import ThemeManager, NoctuaTheme


class ConfirmationsScreen(QWidget):
    """Screen for displaying trade confirmations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.confirmation_items = []
        self.selected_account = None
        self.is_loading = False
        self.setup_ui()
        self.show_no_account_selected()

    def _get_main_window(self):
        """Safely obtain reference to the main window regardless of current parent."""
        if self.parent_window:
            return self.parent_window
        try:
            p = self.parent()
            while p is not None:
                # Heuristic: main window should have account_manager/auth_manager
                if hasattr(p, 'account_manager') and hasattr(p, 'auth_manager'):
                    return p
                p = p.parent()
        except Exception:
            pass
        return None
    
    def setup_ui(self):
        """Setup the confirmations screen UI"""
        # Main layout for the confirmations screen
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with refresh button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 10)
        header_layout.setSpacing(16)
        
        # Add stretch to push refresh button to the right
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setFixedSize(44, 44)
        self.refresh_button.setToolTip("Refresh Confirmations")
        self.refresh_button.clicked.connect(self.refresh_confirmations)
        
        # Refresh icon SVG
        refresh_svg = '''
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 12C4 16.4183 7.58172 20 12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C9.25022 4 6.82447 5.38734 5.38451 7.50024" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 7H5V4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
        
        refresh_icon = ThemeManager.get_current_theme().create_svg_icon(
            refresh_svg,
            ThemeManager.get_current_theme().TEXT_PRIMARY,
            20
        )
        self.refresh_button.setIcon(refresh_icon)
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeManager.get_current_theme().SURFACE_ELEVATED};
                border: 2px solid {ThemeManager.get_current_theme().BORDER};
                border-radius: 12px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.get_current_theme().SURFACE_HOVER};
                border-color: {ThemeManager.get_current_theme().BORDER_FOCUS};
            }}
            QPushButton:pressed {{
                background-color: {ThemeManager.get_current_theme().ACCENT};
            }}
        """)
        
        header_layout.addWidget(self.refresh_button)
        main_layout.addLayout(header_layout)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Scrollable content widget
        self.scroll_content = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_content)
        scroll_layout.setContentsMargins(20, 10, 20, 20)
        scroll_layout.setSpacing(12)
        
        # Status container for messages
        self.status_container = QWidget()
        self.status_layout = QVBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0, 40, 0, 40)
        self.status_layout.setSpacing(16)
        
        # Status icon
        self.status_icon = QLabel()
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setFont(QFont("Segoe UI", 48))
        self.status_layout.addWidget(self.status_icon)
        
        # Status text
        self.status_text = QLabel()
        self.status_text.setAlignment(Qt.AlignCenter)
        self.status_text.setFont(QFont("Segoe UI", 14))
        self.status_text.setWordWrap(True)
        self.status_layout.addWidget(self.status_text)
        
        scroll_layout.addWidget(self.status_container)
        
        # Confirmations list container
        self.confirmations_container = QWidget()
        self.confirmations_layout = QVBoxLayout(self.confirmations_container)
        self.confirmations_layout.setContentsMargins(0, 0, 0, 0)
        self.confirmations_layout.setSpacing(8)
        
        scroll_layout.addWidget(self.confirmations_container)
        scroll_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)
    
    def show_no_account_selected(self):
        """Show message when no account is selected"""
        self.status_container.setVisible(True)
        self.confirmations_container.setVisible(False)
        self.refresh_button.setEnabled(False)
        
        self.status_icon.setText("👤")
        self.status_icon.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_TERTIARY};")
        
        self.status_text.setText("Select an account to view confirmations")
        self.status_text.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};")
    
    def show_loading(self):
        """Show loading state"""
        self.status_container.setVisible(True)
        self.confirmations_container.setVisible(False)
        self.refresh_button.setEnabled(False)
        self.is_loading = True
        
        self.status_icon.setText("⏳")
        self.status_icon.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};")
        
        self.status_text.setText("Loading confirmations...")
        self.status_text.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};")
    
    def show_no_confirmations(self):
        """Show message when account has no confirmations"""
        self.status_container.setVisible(True)
        self.confirmations_container.setVisible(False)
        self.refresh_button.setEnabled(True)
        self.is_loading = False
        
        self.status_icon.setText("✅")
        self.status_icon.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_TERTIARY};")
        
        self.status_text.setText("No confirmations at this moment")
        self.status_text.setStyleSheet(f"color: {ThemeManager.get_current_theme().TEXT_SECONDARY};")
    
    def show_confirmations(self):
        """Show confirmations list"""
        self.status_container.setVisible(False)
        self.confirmations_container.setVisible(True)
        self.refresh_button.setEnabled(True)
        self.is_loading = False
    
    def on_account_selected(self, account):
        """Handle account selection change"""
        # Store the selected account
        self.selected_account = account
        
        if account is None:
            self.show_no_account_selected()
            self.clear_confirmations()
        else:
            # Always load confirmations for the newly selected account
            self.load_confirmations_for_account(account)
    
    def refresh_confirmations(self):
        """Refresh confirmations for current account"""
        # Try to get account from main window if not set locally
        if not self.selected_account and self.parent_window:
            self.selected_account = getattr(self.parent_window, 'selected_account', None)
            
        if self.selected_account and not self.is_loading:
            self.load_confirmations_for_account(self.selected_account)
    
    def load_confirmations_for_account(self, account):
        """Load confirmations for the selected account"""
        self.show_loading()
        self.clear_confirmations()
        
        # Load real confirmations using aiosteampy
        self._load_real_confirmations_for_account(account)
    
    def _load_real_confirmations_for_account(self, account):
        """Load real confirmations from Steam using aiosteampy"""
        if not self.selected_account or self.selected_account != account:
            return  # Account changed while loading
        
        # Get the main window to access the confirmation manager
        main_window = self._get_main_window()
        if not main_window:
            QMessageBox.warning(self, "Error", "Main window not available to load confirmations")
            return
        
        # Check if the managers exist as attributes of the main window
        if not hasattr(main_window, 'confirmation_manager') or not hasattr(main_window, 'auth_manager'):
            try:
                # Initialize managers if missing
                from src.account_manager import create_account_managers
                am, authm, confm = create_account_managers()
                # Attach to main window
                main_window.account_manager = am
                main_window.auth_manager = authm
                main_window.confirmation_manager = confm
                # Reconnect signals to the main window instance (must be a SteamAuthenticatorGUI)
                mw = main_window
                confm.confirmations_loaded.connect(mw.on_confirmations_loaded)
                confm.confirmation_processed.connect(mw.on_confirmation_processed)
                authm.login_started.connect(mw.on_login_started)
                authm.login_completed.connect(mw.on_login_completed)
                authm.code_generated.connect(mw.on_code_generated)
                authm.session_refreshed.connect(mw.on_session_refreshed)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to initialize managers: {e}")
                return
        
        # Ensure account is authenticated before attempting to load confirmations
        try:
            authm = main_window.auth_manager
            steam_id_str = str(account.steam_id)
            if steam_id_str not in getattr(authm, '_steam_clients', {}):
                # Login in background then load confirmations
                self._async_login_then_load(account, main_window)
                return
        except Exception as e:
            print(repr(e))
            pass
        
        # Run the confirmation loading in a separate thread to avoid blocking UI
        self._async_load_confirmations(account, main_window)

    def _async_login_then_load(self, account, main_window):
        """Authenticate account and then load confirmations"""
        try:
            import asyncio
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
            QMessageBox.warning(self, "Login Error", f"Failed to start login: {e}")

    def _on_login_then_load_finished(self, loader, account, main_window):
        if loader.error:
            QMessageBox.warning(self, "Login Error", f"Login failed: {loader.error}")
            return
        result = loader.result or {}
        if not result.get('success'):
            QMessageBox.warning(self, "Login Error", result.get('error', 'Unknown error'))
            return
        # Proceed to load confirmations
        self._async_load_confirmations(account, main_window)
    
    def _async_load_confirmations(self, account, main_window):
        """Asynchronously load confirmations"""
        try:
            # Load confirmations using the confirmation manager
            import asyncio
            from PyQt5.QtCore import QThread
            
            # Create a simple worker to run the async function
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
            
            # Create and start the loader
            loader = ConfirmationLoader(
                main_window.confirmation_manager, 
                main_window.auth_manager, 
                account
            )
            
            # Connect completion signal
            loader.finished.connect(lambda: self._on_confirmations_loaded(loader, account))
            loader.start()
            
        except Exception as e:
            print(f"Error starting confirmation loading: {e}")
            # Fallback to sample data on error
            self._load_sample_confirmations_for_account(account)
    
    def _on_confirmations_loaded(self, loader, account):
        """Handle completion of confirmation loading"""
        if not self.selected_account or self.selected_account != account:
            return  # Account changed while loading
        
        try:
            if loader.error:
                print(f"Error loading confirmations: {loader.error}")
                # Show message instead of fake data; ensure we really requested
                QMessageBox.warning(self, "Load Error", f"Failed to load confirmations: {loader.error}")
                return
            
            result = loader.result
            if not result or not result.get('success', False):
                error_text = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Unknown error'
                print(f"Failed to load confirmations: {error_text}")
                QMessageBox.information(self, "No Confirmations", error_text)
                return
            
            # Clear existing items before rendering new list to avoid duplicates
            self.clear_confirmations()
            # Get confirmations from result
            confirmations = result.get('confirmations', [])
            
            if not confirmations:
                self.show_no_confirmations()
            else:
                self.show_confirmations()
                for confirmation in confirmations:
                    # Extract type and description from the confirmation
                    conf_type = confirmation.get('type', 'UNKNOWN')
                    # Prefer headline provided by backend, fall back to summary-based description
                    description = confirmation.get('description')
                    if not description:
                        summary = confirmation.get('summary') or ''
                        if conf_type == 'TRADE':
                            description = f"Trade: {summary}"
                        elif conf_type == 'LISTING' or conf_type == 'MARKET':
                            description = f"Market: {summary}"
                        else:
                            description = f"Confirmation {confirmation.get('id', 'N/A')}"
                    confirmation_id = str(confirmation.get('id', ''))
                    self.add_confirmation_item(conf_type, description, confirmation_id)
                    
        except Exception as e:
            print(f"Error processing confirmations: {e}")
            QMessageBox.warning(self, "Error", "Failed to process confirmations")
    
    def _load_sample_confirmations_for_account(self, account):
        """Load sample confirmations for demonstration"""
        if not self.selected_account or self.selected_account != account:
            return  # Account changed while loading
        
        # Generate account-specific confirmations
        account_confirmations = self._get_sample_confirmations_for_account(account)
        
        if not account_confirmations:
            self.show_no_confirmations()
        else:
            self.show_confirmations()
            # Generate unique IDs for sample confirmations
            for i, (conf_type, description) in enumerate(account_confirmations):
                confirmation_id = f"sample_{i}_{account.steam_id}"
                self.add_confirmation_item(conf_type, description, confirmation_id)
    
    def _get_sample_confirmations_for_account(self, account):
        """Get sample confirmations based on account"""
        # Different confirmations for different accounts
        confirmations_data = {
            "Player1": [
                ("Trade", f"Trade with TestUser123 - 2 item(s)"),
                ("Market", f"Sell AK-47 | Redline (Field-Tested) for $15.50"),
            ],
            "SteamUser456": [
                ("Trade", f"Trade with GamerFriend789 - 1 item(s)"),
                ("Market", f"Buy M4A4 | Howl (Minimal Wear) for $850.00"),
                ("Trade", f"Trade with TradingBot321 - 3 item(s)"),
            ],
            "TestAccount": [
                ("Market", f"Sell Karambit | Fade (Factory New) for $1,200.00"),
            ],
        }
        
        return confirmations_data.get(account.account_name, [])
    
    def clear_confirmations(self):
        """Clear all confirmation items"""
        for item in self.confirmation_items[:]:
            self.remove_confirmation_item(item)
    
    def add_confirmation_item(self, confirmation_type: str, description: str, confirmation_id: str = None):
        """Add a new confirmation item to the list"""
        item = ConfirmationItem(confirmation_type, description, confirmation_id)
        
        # Connect button signals using the new signals
        item.confirmation_accepted.connect(self.on_accept_confirmation)
        item.confirmation_declined.connect(self.on_decline_confirmation)
        
        self.confirmation_items.append(item)
        self.confirmations_layout.addWidget(item)
    
    def on_accept_confirmation(self, confirmation_id: str):
        """Handle confirmation acceptance"""
        # Find and remove the confirmation item
        item_to_remove = None
        for item in self.confirmation_items:
            if item.confirmation_id == confirmation_id:
                item_to_remove = item
                break
        
        if item_to_remove:
            self.remove_confirmation_item(item_to_remove)
        
        # Process the confirmation through the main window
        main_window = self._get_main_window()
        if main_window:
            main_window.on_accept_confirmation(confirmation_id)
    
    def on_decline_confirmation(self, confirmation_id: str):
        """Handle confirmation decline"""
        # Find and remove the confirmation item
        item_to_remove = None
        for item in self.confirmation_items:
            if item.confirmation_id == confirmation_id:
                item_to_remove = item
                break
        
        if item_to_remove:
            self.remove_confirmation_item(item_to_remove)
        
        # Process the confirmation through the main window
        main_window = self._get_main_window()
        if main_window:
            main_window.on_decline_confirmation(confirmation_id)
    
    def remove_confirmation_item(self, item: ConfirmationItem):
        """Remove a confirmation item from the list"""
        if item in self.confirmation_items:
            self.confirmation_items.remove(item)
            self.confirmations_layout.removeWidget(item)
            item.setParent(None)
            item.deleteLater()
    
    def apply_theme(self):
        """Apply current theme to all confirmation items and UI elements"""
        current_theme = ThemeManager.get_current_theme()
        
        # Update refresh button
        refresh_svg = '''
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 12C4 16.4183 7.58172 20 12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C9.25022 4 6.82447 5.38734 5.38451 7.50024" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 7H5V4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
        
        refresh_icon = current_theme.create_svg_icon(
            refresh_svg,
            current_theme.TEXT_PRIMARY,
            20
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
        
        # Update status elements
        self.status_icon.setStyleSheet(f"color: {current_theme.TEXT_TERTIARY};")
        self.status_text.setStyleSheet(f"color: {current_theme.TEXT_SECONDARY};")
        
        # Update confirmation items
        for item in self.confirmation_items:
            item.apply_styling()
    
    def process_accept_confirmation(self, confirmation_id):
        """Handle accepting a confirmation"""
        if not self.selected_account:
            return
        
        main_window = self._get_main_window()
        if not main_window:
            QMessageBox.warning(self, "Error", "Unable to process confirmation")
            return
        
        # Check if the managers exist as attributes of the main window
        if not hasattr(main_window, 'confirmation_manager') or not hasattr(main_window, 'auth_manager'):
            QMessageBox.warning(self, "Error", "Unable to process confirmation")
            return
        
        # Process the confirmation asynchronously
        QTimer.singleShot(100, lambda: self._async_process_confirmation(confirmation_id, True, main_window))
    
    def process_decline_confirmation(self, confirmation_id):
        """Handle declining a confirmation"""
        if not self.selected_account:
            return
        
        main_window = self._get_main_window()
        if not main_window:
            QMessageBox.warning(self, "Error", "Unable to process confirmation")
            return
        
        # Check if the managers exist as attributes of the main window
        if not hasattr(main_window, 'confirmation_manager') or not hasattr(main_window, 'auth_manager'):
            QMessageBox.warning(self, "Error", "Unable to process confirmation")
            return
        
        # Process the confirmation asynchronously
        self._async_process_confirmation(confirmation_id, False, main_window)
    
    def _async_process_confirmation(self, confirmation_id, accept, main_window):
        """Asynchronously process a confirmation"""
        try:
            import asyncio
            from PyQt5.QtCore import QThread
            
            # Create a simple worker to run the async function
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
                                    self.steam_id, self.confirmation_id, self.auth_manager
                                )
                            )
                            self.result = fut.result()
                        else:
                            fut = self.auth_manager.submit(
                                self.confirmation_manager.decline_confirmation(
                                    self.steam_id, self.confirmation_id, self.auth_manager
                                )
                            )
                            self.result = fut.result()
                    except Exception as e:
                        self.error = str(e)
            
            # Create and start the processor
            processor = ConfirmationProcessor(
                main_window.confirmation_manager,
                main_window.auth_manager,
                str(self.selected_account.steam_id),
                confirmation_id,
                accept
            )
            
            # Connect completion signal
            processor.finished.connect(lambda: self._on_confirmation_processed(processor, confirmation_id))
            processor.start()
            
        except Exception as e:
            print(f"Error starting confirmation processing: {e}")
            QMessageBox.warning(self, "Error", "Failed to process confirmation")
    
    def _on_confirmation_processed(self, processor, confirmation_id):
        """Handle completion of confirmation processing"""
        try:
            if processor.error:
                print(f"Error processing confirmation: {processor.error}")
                QMessageBox.warning(self, "Error", f"Failed to process confirmation: {processor.error}")
                return
            
            result = processor.result
            if not result or not result.get('success', False):
                error_msg = result.get('error', 'Unknown error')
                print(f"Failed to process confirmation: {error_msg}")
                QMessageBox.warning(self, "Error", f"Failed to process confirmation: {error_msg}")
                return
            
            # Show success message
            action = "accepted" if result.get('accepted', False) else "declined"
            QMessageBox.information(self, "Success", f"Confirmation {action} successfully")
            
            # Remove the confirmation from the UI
            # Find and remove the confirmation item
            item_to_remove = None
            for item in self.confirmation_items:
                if item.confirmation_id == confirmation_id:
                    item_to_remove = item
                    break
            
            if item_to_remove:
                self.remove_confirmation_item(item_to_remove)
            
        except Exception as e:
            print(f"Error handling confirmation result: {e}")
            QMessageBox.warning(self, "Error", "Failed to handle confirmation result")
