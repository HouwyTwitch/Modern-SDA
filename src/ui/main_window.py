import sys
import asyncio
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget,
    QButtonGroup, QDialog, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PyQt5.QtGui import QFont, QPalette, QColor

# Import account management classes
from src.account_manager import AccountData, AccountManager, AuthenticationManager, ConfirmationManager
from src.theme import ThemeManager
from src.settings import SettingsManager
from src.ui.account_widget import AccountWidget
from src.ui.add_account_dialog import AddAccountDialog
from src.ui.edit_account_dialog import EditAccountDialog
from src.ui.navigation_button import NavigationButton
from src.ui.screens.accounts_screen import AccountsScreen
from src.ui.screens.confirmations_screen import ConfirmationsScreen
from src.ui.screens.settings_screen import SettingsScreen
from src.ui.floating_add_button import FloatingAddButton
from src.ui.title_bar import CustomTitleBar
from src.ui.message_dialog import MessageDialog


class SteamAuthenticatorGUI(QMainWindow):
    """Main application window with navigation"""

    def __init__(self):
        super().__init__()
        SettingsManager.load_settings()

        # Migrate legacy "Noctua" setting to renamed "Midnight"
        saved_theme = SettingsManager.get_setting("theme")
        if saved_theme == "Noctua":
            saved_theme = "Midnight"
            SettingsManager.set_setting("theme", "Midnight")

        if not ThemeManager.set_theme(saved_theme):
            ThemeManager.set_theme("Midnight")
            SettingsManager.set_setting("theme", "Midnight")
        # Initialize account management
        self.account_manager = AccountManager()
        self.auth_manager = AuthenticationManager()
        self.confirmation_manager = ConfirmationManager()
        
        # UI state
        self.account_widgets: List[AccountWidget] = []
        self.current_screen = 0
        self.selected_account = None  # Track currently selected account globally
        self.previous_selected_account = None  # Track previously selected account
        
        # Initialize UI first
        self.init_ui()
        self.apply_settings()
        
        # Connect account management signals after UI is initialized
        self.account_manager.account_added.connect(self.on_account_added)
        self.account_manager.account_removed.connect(self.on_account_removed)
        self.account_manager.accounts_loaded.connect(self.on_accounts_loaded)
        self.account_manager.account_updated.connect(self.on_account_updated)
        self.account_manager.avatar_loaded.connect(self.on_avatar_loaded)
        
        # Connect authentication signals
        self.auth_manager.login_started.connect(self.on_login_started)
        self.auth_manager.login_completed.connect(self.on_login_completed)
        self.auth_manager.code_generated.connect(self.on_code_generated)
        self.auth_manager.session_refreshed.connect(self.on_session_refreshed)
        
        # Connect confirmation signals
        self.confirmation_manager.confirmations_loaded.connect(self.on_confirmations_loaded)
        self.confirmation_manager.confirmation_processed.connect(self.on_confirmation_processed)
        
        # Load existing accounts after UI is ready
        self.account_manager.load_accounts()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Steam Desktop Authenticator")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setGeometry(100, 100, 480, 720)
        self.setMinimumSize(400, 600)
        self.apply_theme()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Content area with padding
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(24, 16, 24, 0)
        
        # Stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        
        # Create screens
        self.accounts_screen = AccountsScreen(self)
        self.confirmations_screen = ConfirmationsScreen(self)
        self.settings_screen = SettingsScreen(self)
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.accounts_screen)
        self.stacked_widget.addWidget(self.confirmations_screen)
        self.stacked_widget.addWidget(self.settings_screen)
        
        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_container)

        # Navigation bar
        self.create_navigation_bar()
        main_layout.addWidget(self.nav_bar)

        # Floating add button (only visible on accounts screen)
        self.add_button = FloatingAddButton(self)
        self.add_button.clicked.connect(self.show_add_account_dialog)

        # Position floating button
        self.position_floating_button()

        # Connect search once here (not per account added)
        self.accounts_screen.search_input.textChanged.connect(self.filter_accounts)
        self.accounts_screen.qr_login_requested.connect(self.show_qr_login_dialog)

        # Set initial screen
        self.switch_screen(0)
    
    def create_navigation_bar(self):
        """Create the bottom navigation bar"""
        self.nav_bar = QFrame()
        self.nav_bar.setFixedHeight(90)
        current_theme = ThemeManager.get_current_theme()
        self.nav_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {current_theme.SURFACE};
                border-top: 1px solid {current_theme.BORDER};
                border-radius: 0;
            }}
        """)
        
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        nav_layout.setSpacing(0)
        
        # Add stretch to center the buttons
        nav_layout.addStretch(1)
        
        # Navigation buttons
        self.nav_buttons = []
        current_theme = ThemeManager.get_current_theme()
        nav_items = [
            ("Accounts", current_theme.get_accounts_svg()),
            ("Confirmations", current_theme.get_confirmations_svg()),
            ("Settings", current_theme.get_settings_svg())
        ]
        
        self.button_group = QButtonGroup()
        
        for i, (text, svg_icon) in enumerate(nav_items):
            button = NavigationButton(text, svg_icon, self)
            button.clicked.connect(lambda checked, idx=i: self.switch_screen(idx))
            self.button_group.addButton(button, i)
            self.nav_buttons.append(button)
            nav_layout.addWidget(button)
            
            # Add spacing between buttons (except after the last one)
            if i < len(nav_items) - 1:
                nav_layout.addSpacing(60)  # Increased space between buttons
        
        # Add stretch to center the buttons
        nav_layout.addStretch(1)
    
    def switch_screen(self, index: int):
        """Switch to the specified screen"""
        if 0 <= index < len(self.nav_buttons):
            # Update navigation buttons
            for i, button in enumerate(self.nav_buttons):
                button.set_active(i == index)
            
            # Switch screen with animation
            self.animate_screen_change(index)
            self.current_screen = index
            
            # Show/hide floating add button (only on accounts screen)
            self.add_button.setVisible(index == 0)
            
            # When switching to confirmations screen, sync with current account selection
            if index == 1 and hasattr(self, 'confirmations_screen'):
                # Use the selected account from main window
                selected_account = getattr(self, 'selected_account', None)
                self.confirmations_screen.on_account_selected(selected_account)

    def animate_screen_change(self, index: int):
        """Animate screen change in the stacked widget."""
        if index == self.stacked_widget.currentIndex():
            return

        if hasattr(self, "_screen_animation") and self._screen_animation.state() == QAbstractAnimation.Running:
            self._screen_animation.stop()

        self.stacked_widget.setCurrentIndex(index)
        target_widget = self.stacked_widget.currentWidget()
        opacity_effect = QGraphicsOpacityEffect(target_widget)
        opacity_effect.setOpacity(0.0)
        target_widget.setGraphicsEffect(opacity_effect)

        animation = QPropertyAnimation(opacity_effect, b"opacity", self)
        animation.setDuration(220)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)

        def cleanup_effect():
            target_widget.setGraphicsEffect(None)

        animation.finished.connect(cleanup_effect)
        self._screen_animation = animation
        animation.start()
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        current_theme = ThemeManager.get_current_theme()
        self.setStyleSheet(current_theme.get_stylesheet())

        # Update the window palette so that widgets with background-color:transparent
        # inherit the correct background colour (critical for Light / Solar themes).
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(current_theme.BACKGROUND))
        palette.setColor(QPalette.WindowText, QColor(current_theme.TEXT_PRIMARY))
        palette.setColor(QPalette.Base, QColor(current_theme.SURFACE_ELEVATED))
        palette.setColor(QPalette.AlternateBase, QColor(current_theme.SURFACE))
        palette.setColor(QPalette.Text, QColor(current_theme.TEXT_PRIMARY))
        palette.setColor(QPalette.Button, QColor(current_theme.ACCENT))
        palette.setColor(QPalette.ButtonText, QColor(current_theme.TEXT_PRIMARY))
        self.setPalette(palette)
        
        # Update navigation buttons if they exist
        if hasattr(self, 'nav_buttons'):
            for button in self.nav_buttons:
                button.update_style()
        
        # Update navigation bar styling
        if hasattr(self, 'nav_bar'):
            self.nav_bar.setStyleSheet(f"""
                QFrame {{
                    background-color: {current_theme.SURFACE};
                    border-top: 1px solid {current_theme.BORDER};
                    border-radius: 0;
                }}
            """)
        
        # Update title bar
        if hasattr(self, 'title_bar'):
            self.title_bar.apply_theme()

        # Update floating add button
        if hasattr(self, 'add_button'):
            self.add_button.apply_styling()
        
        # Update account widgets if they exist
        if hasattr(self, 'account_widgets'):
            for widget in self.account_widgets:
                widget.update_style()
        
        # Update accounts screen dynamic labels
        if hasattr(self, 'accounts_screen') and self.accounts_screen:
            self.accounts_screen.update_theme()

        # Update confirmations screen if it exists
        if hasattr(self, 'confirmations_screen') and self.confirmations_screen:
            self.confirmations_screen.apply_theme()

        # Update settings screen if it exists
        if hasattr(self, 'settings_screen') and self.settings_screen:
            self.settings_screen.update_combo_style()

    def apply_settings(self):
        """Apply non-theme settings to relevant screens."""
        if hasattr(self, 'accounts_screen') and self.accounts_screen:
            self.accounts_screen.apply_settings()
        if hasattr(self, 'confirmations_screen') and self.confirmations_screen:
            self.confirmations_screen.apply_settings()
    
    def position_floating_button(self):
        """Position the floating add button"""
        margin = 20
        nav_bar_height = 90
        self.add_button.move(
            self.width() - self.add_button.width() - margin,
            self.height() - self.add_button.height() - margin - nav_bar_height
        )
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.position_floating_button()
    
    def filter_accounts(self, search_text: str):
        """Filter accounts based on search text"""
        search_text = search_text.lower()
        
        for widget in self.account_widgets:
            account = widget.account
            should_show = (
                search_text in account.account_name.lower() or
                search_text in account.steam_id.lower()
            )
            widget.setVisible(should_show)
    
    def show_qr_login_dialog(self):
        """Open the QR login approval dialog for the selected account."""
        if not self.selected_account:
            MessageDialog.warning(
                self,
                "No Account Selected",
                "Select an account first to approve a QR login.",
            )
            return
        if not self.auth_manager.is_authenticated(self.selected_account.steam_id):
            MessageDialog.warning(
                self,
                "Not Authenticated",
                "This account isn't signed in yet. Wait for authentication to finish first.",
            )
            return

        from src.ui.qr_login_dialog import QrLoginDialog
        dialog = QrLoginDialog(self.auth_manager, self.selected_account, self)
        dialog.exec_()

    def show_add_account_dialog(self):
        """Show the add account dialog"""
        dialog = AddAccountDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            account_data = dialog.get_account_data()
            
            # Validation
            if not account_data['mafile_path']:
                MessageDialog.warning(self, "Invalid Input", "Please select a mafile.")
                return

            if not account_data['password']:
                MessageDialog.warning(self, "Invalid Input", "Please enter account password.")
                return

            # Add account through account manager
            result = self.account_manager.add_account(
                account_data['mafile_path'],
                account_data['password'],
                proxy=account_data.get('proxy', ''),
            )

            if not result['success']:
                MessageDialog.warning(self, "Account Addition Failed", result['error'])
                return

            MessageDialog.information(
                self,
                "Account Added",
                f"Successfully added account '{result['account'].account_name}' from mafile."
            )

    def on_accounts_loaded(self):
        if hasattr(self, 'accounts_screen') and self.accounts_screen is not None:
            for account in self.account_manager.get_all_accounts():
                self.on_account_added(account)

        # Auto-select the last-used account across launches (ported from Android).
        last_id = SettingsManager.get_setting("last_selected_steam_id") or ""
        target_widget = None
        if last_id:
            for widget in self.account_widgets:
                if str(widget.account.steam_id) == str(last_id):
                    target_widget = widget
                    break
        if target_widget is None and self.account_widgets:
            # Fall back to the first available account, matching Android's behaviour.
            target_widget = self.account_widgets[0]

        if target_widget is not None:
            QTimer.singleShot(0, lambda w=target_widget: self.on_account_selected(w))
    
    def on_account_added(self, account: AccountData):
        """Handle account added signal"""
        account_widget = AccountWidget(account)
        self.account_widgets.append(account_widget)

        if hasattr(self, 'accounts_screen') and self.accounts_screen is not None:
            account_widget.account_selected.connect(self.accounts_screen.on_account_selected)
            account_widget.edit_requested.connect(self.show_edit_account_dialog)
            account_widget.remove_requested.connect(self.confirm_remove_account)

            # Insert before the trailing stretch
            self.accounts_screen.accounts_layout.insertWidget(
                self.accounts_screen.accounts_layout.count() - 1,
                account_widget
            )

            # Hide empty state now that at least one account exists
            self.accounts_screen.set_has_accounts(True)

    def show_edit_account_dialog(self, account: AccountData):
        """Show edit account dialog and save changes."""
        dialog = EditAccountDialog(account, self)
        if dialog.exec_():
            account_data = dialog.get_account_data()
            mafile_path = account_data['mafile_path']
            password = account_data['password'] or None

            proxy = account_data.get('proxy', '')

            if mafile_path == account.mafile_path:
                mafile_path = None

            if not mafile_path and not password and proxy == account.proxy:
                MessageDialog.information(self, "No Changes", "No changes were provided.")
                return

            result = self.account_manager.update_account(
                account.steam_id,
                mafile_path=mafile_path,
                password=password,
                proxy=proxy,
            )

            if not result['success']:
                MessageDialog.warning(self, "Update Failed", result['error'])
            else:
                MessageDialog.information(
                    self,
                    "Account Updated",
                    f"Successfully updated account '{result['account'].account_name}'."
                )

    def confirm_remove_account(self, account: AccountData):
        """Confirm and remove an account."""
        confirmed = MessageDialog.question(
            self,
            "Remove Account",
            f"Remove account '{account.account_name}'?\nThis will remove it from this app only.",
        )
        if confirmed:
            if not self.account_manager.remove_account(account.steam_id):
                MessageDialog.warning(self, "Remove Failed", "Failed to remove account.")
    
    def on_account_selected(self, selected_widget):
        """Handle account selection with automatic authentication"""
        # Store the previously selected account
        self.previous_selected_account = self.selected_account

        # Deselect all other accounts
        for widget in self.account_widgets:
            widget.set_selected(False)

        # Select the clicked account
        selected_widget.set_selected(True)
        selected_account = selected_widget.account

        # Store selected account reference in main window for global access
        self.selected_account = selected_account
        # Persist the selection so the app auto-selects it on next launch.
        SettingsManager.set_setting("last_selected_steam_id", str(selected_account.steam_id))
        
        # Update accounts screen with selected account
        self.accounts_screen.set_selected_account(selected_account)
        
        # Update header to show selected account
        self.accounts_screen.title_label.setText("...")  # Show loading state
        self.accounts_screen.subtitle_label.setText(selected_account.account_name)
        
        # Check if authentication is needed OR client not initialized
        needs_auth = selected_account.needs_reauthentication()
        has_client = str(selected_account.steam_id) in self.auth_manager._steam_clients
        if needs_auth or not has_client:
            # Start authentication in background.
            # _on_login_worker_finished will notify confirmations_screen once done,
            # so do NOT call it here — that would fire a second concurrent login.
            self.authenticate_account(selected_account)
        else:
            # Generate a code immediately
            code = self.auth_manager.generate_auth_code(selected_account)
            self.accounts_screen.set_code(code)
            # Only notify confirmations screen when we already have a valid session
            if hasattr(self, 'confirmations_screen'):
                self.confirmations_screen.on_account_selected(selected_account)
    
    def authenticate_account(self, account: AccountData):
        """Authenticate account using aiosteampy"""
        # Run the async login in a background QThread to avoid blocking the UI
        QTimer.singleShot(0, lambda: self._authenticate_account_async(account))
    
    def _authenticate_account_async(self, account: AccountData):
        """Async authenticate account using a QThread running an asyncio loop"""
        try:
            from PyQt5.QtCore import QThread
            import asyncio

            self.accounts_screen.title_label.setText("...")

            class LoginWorker(QThread):
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

            worker = LoginWorker(self.auth_manager, account)
            worker.finished.connect(lambda: self._on_login_worker_finished(worker, account))
            worker.start()

        except Exception as e:
            MessageDialog.warning(self, "Authentication Failed", f"Failed to authenticate account: {str(e)}")

    def _on_login_worker_finished(self, worker, account: AccountData):
        """Handle completion of background login"""
        try:
            if worker.error:
                MessageDialog.warning(self, "Login Failed", f"Failed to login: {worker.error}")
                return
            result = worker.result or {}
            if not result.get('success'):
                MessageDialog.warning(self, "Login Failed", result.get('error', 'Unknown error'))
                return

            # Save updated account tokens
            self.account_manager.save_accounts()

            # Update code label immediately
            code = self.auth_manager.generate_auth_code(account)
            self.accounts_screen.set_code(code)

            # If confirmations screen is present, refresh confirmations for this account
            if hasattr(self, 'confirmations_screen') and self.selected_account and self.selected_account.steam_id == account.steam_id:
                self.confirmations_screen.on_account_selected(account)
        except Exception as e:
            MessageDialog.warning(self, "Login Handling Error", f"Failed after login: {str(e)}")
    
    def on_account_removed(self, steam_id: str):
        """Handle account removed signal"""
        for widget in self.account_widgets[:]:
            if widget.account.steam_id == steam_id:
                self.account_widgets.remove(widget)
                self.accounts_screen.accounts_layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()
                break

        # Show empty state if no accounts remain
        if not self.account_widgets:
            self.accounts_screen.set_has_accounts(False)

        if self.selected_account and str(self.selected_account.steam_id) == str(steam_id):
            self.selected_account = None
            self.accounts_screen.set_selected_account(None)
            self.accounts_screen.title_label.setText("SDA")
            self.accounts_screen.subtitle_label.setText("No account selected")
            if hasattr(self, 'confirmations_screen'):
                self.confirmations_screen.on_account_selected(None)
        
    def on_login_started(self, steam_id: str):
        """Handle login started signal"""
        # Could show a loading indicator or status message
        pass
    
    def on_login_completed(self, steam_id: str, success: bool):
        """Handle login completed signal"""
        pass
    
    def on_code_generated(self, steam_id: str, code: str):
        """Handle code generated signal"""
        # Update the UI with the new code if this is the selected account
        if (self.selected_account and
            self.selected_account.steam_id == steam_id):
            self.accounts_screen.set_code(code)
    
    def on_session_refreshed(self, steam_id: str, success: bool):
        pass

    def on_confirmations_loaded(self, steam_id: str, confirmations: list):
        pass
    
    def on_confirmation_processed(self, steam_id: str, confirmation_id: str, accepted: bool):
        """Handle confirmation processed signal"""
        # Could update UI to reflect confirmation processing
        pass
    
    def on_accept_confirmation(self, confirmation_id: str):
        """Handle accepting a confirmation"""
        if not self.selected_account:
            return
        
        # Process the confirmation through the confirmations screen
        if hasattr(self, 'confirmations_screen'):
            self.confirmations_screen.process_accept_confirmation(confirmation_id)
    
    def on_decline_confirmation(self, confirmation_id: str):
        """Handle declining a confirmation"""
        if not self.selected_account:
            return
        
        # Process the confirmation through the confirmations screen
        if hasattr(self, 'confirmations_screen'):
            self.confirmations_screen.process_decline_confirmation(confirmation_id)

    def on_account_updated(self, account: AccountData):
        for widget in self.account_widgets:
            if widget.account.steam_id == account.steam_id:
                widget.update_account(account)
                break

        if self.selected_account and self.selected_account.steam_id == account.steam_id:
            self.selected_account = account
            self.accounts_screen.subtitle_label.setText(account.account_name)

    def on_avatar_loaded(self, steam_id: str, data: bytes):
        for widget in self.account_widgets:
            if widget.account.steam_id == steam_id:
                widget.set_avatar(data)
                break
