"""
Account management classes for Steam Desktop Authenticator
This module provides classes for managing Steam accounts and interfacing with aiosteampy
"""

import json
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET
import threading
import asyncio


@dataclass
class AccountData:
    """Data model for Steam account"""
    steam_id: str
    account_name: str
    avatar_url: str = ""
    mafile_path: str = ""
    password: str = ""
    # Session data
    access_token: str = ""
    refresh_token: str = ""
    last_authenticated: Optional[str] = None  # ISO format timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert account data to dictionary"""
        data = asdict(self)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountData':
        """Create account data from dictionary"""
        return cls(
            steam_id=str(data.get('steam_id', '')),
            account_name=data.get('account_name', ''),
            avatar_url=data.get('avatar_url', ''),
            mafile_path=data.get('mafile_path', ''),
            password=data.get('password', ''),
            access_token=data.get('access_token', ''),
            refresh_token=data.get('refresh_token', ''),
            last_authenticated=data.get('last_authenticated')
        )
    
    def needs_reauthentication(self) -> bool:
        """Check if account needs reauthentication (more than 12 hours since last auth)"""
        if not self.last_authenticated:
            return True
            
        try:
            last_auth = datetime.fromisoformat(self.last_authenticated)
            time_diff = datetime.now() - last_auth
            return time_diff.total_seconds() > 12 * 3600  # 12 hours
        except ValueError:
            return True
    
    def update_session(self, access_token: str, refresh_token: str):
        """Update session tokens and timestamp"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.last_authenticated = datetime.now().isoformat()


class AccountValidator:
    """Validator for account data and mafiles"""
    
    @staticmethod
    def validate_mafile(mafile_path: str) -> Dict[str, Any]:
        """
        Validate and parse mafile
        Returns: Dict with validation result and parsed data
        """
        if not os.path.exists(mafile_path):
            return {'valid': False, 'error': 'Mafile does not exist'}
        
        try:
            with open(mafile_path, 'r', encoding='utf-8') as file:
                mafile_data = json.load(file)
            
            # Basic mafile structure validation
            required_fields = ['account_name', 'Session', 'shared_secret', 'identity_secret', 'device_id']
            missing_fields = [field for field in required_fields if field not in mafile_data]
            
            if missing_fields:
                return {
                    'valid': False, 
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }
            
            return {
                'valid': True,
                'data': mafile_data,
                'account_name': mafile_data['account_name'],
                'steam_id': mafile_data['Session']['SteamID'],
                'identity_secret': mafile_data['identity_secret']
            }
            
        except json.JSONDecodeError:
            return {'valid': False, 'error': 'Invalid JSON format'}
        except Exception as e:
            return {'valid': False, 'error': f'Error reading mafile: {str(e)}'}
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate account password"""
        if not password or not password.strip():
            return {'valid': False, 'error': 'Password is required'}
        
        if len(password) < 3:  # Minimal validation for now
            return {'valid': False, 'error': 'Password is too short'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_account_data(account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete account data"""
        mafile_validation = AccountValidator.validate_mafile(account_data.get('mafile_path', ''))
        if not mafile_validation['valid']:
            return mafile_validation
        
        password_validation = AccountValidator.validate_password(account_data.get('password', ''))
        if not password_validation['valid']:
            return password_validation
        
        return {'valid': True, 'mafile_data': mafile_validation['data']}


class AccountManager(QObject):
    """Manages Steam accounts and their operations"""
    
    # Signals for UI updates
    account_added = pyqtSignal(object)  # AccountData
    account_removed = pyqtSignal(str)   # steam_id
    account_updated = pyqtSignal(object)  # AccountData
    accounts_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.accounts: List[AccountData] = []
        self._accounts_file = "accounts.json"
        # Ensure avatars directory exists
        try:
            os.makedirs("avatars", exist_ok=True)
        except Exception:
            pass
    
    def add_account(self, mafile_path: str, password: str) -> Dict[str, Any]:
        """
        Add new account from mafile and password
        Returns: Dict with success status and account data or error message
        """
        try:
            # Validate input data
            validation_result = AccountValidator.validate_account_data({
                'mafile_path': mafile_path,
                'password': password
            })
            
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            mafile_data = validation_result['mafile_data']
            
            # Check for duplicate accounts
            steam_id = mafile_data['Session']['SteamID']
            if self.get_account_by_steam_id(steam_id):
                return {'success': False, 'error': 'Account already exists'}
            
            # Create account data
            account = AccountData(
                steam_id=str(steam_id),
                account_name=mafile_data['account_name'],
                avatar_url="",  # Will be loaded later
                mafile_path=mafile_path,
                password=password  # TODO: Encrypt in production
            )
            
            # Add to accounts list
            self.accounts.append(account)
            
            # Save accounts
            self.save_accounts()
            
            # Emit signal for UI update
            self.account_added.emit(account)
            # Fetch avatar in a real background thread (non-blocking)
            threading.Thread(target=self._fetch_avatar_async, args=(account,), daemon=True).start()
            
            return {'success': True, 'account': account}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to add account: {str(e)}'}
    
    def remove_account(self, steam_id: str) -> bool:
        """Remove account by steam_id"""
        try:
            account = self.get_account_by_steam_id(steam_id)
            if not account:
                return False
            
            self.accounts.remove(account)
            self.save_accounts()
            self.account_removed.emit(steam_id)
            return True
            
        except Exception:
            return False

    def update_account(
        self,
        steam_id: str,
        mafile_path: Optional[str] = None,
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update account details such as mafile path or password."""
        try:
            account = self.get_account_by_steam_id(steam_id)
            if not account:
                return {'success': False, 'error': 'Account not found'}

            if mafile_path:
                mafile_validation = AccountValidator.validate_mafile(mafile_path)
                if not mafile_validation['valid']:
                    return {'success': False, 'error': mafile_validation['error']}

                mafile_data = mafile_validation['data']
                updated_steam_id = str(mafile_data['Session']['SteamID'])
                if updated_steam_id != str(steam_id):
                    return {'success': False, 'error': 'Mafile does not match this account'}

                account.mafile_path = mafile_path
                account.account_name = mafile_data['account_name']

            if password:
                password_validation = AccountValidator.validate_password(password)
                if not password_validation['valid']:
                    return {'success': False, 'error': password_validation['error']}
                account.password = password

            self.save_accounts()
            self.account_updated.emit(account)
            return {'success': True, 'account': account}

        except Exception as e:
            return {'success': False, 'error': f'Failed to update account: {str(e)}'}
    
    def get_account_by_steam_id(self, steam_id: str) -> Optional[AccountData]:
        """Get account by steam_id"""
        for account in self.accounts:
            if account.steam_id == steam_id:
                return account
        return None
    
    def get_all_accounts(self) -> List[AccountData]:
        """Get all accounts"""
        return self.accounts.copy()
    
    def save_accounts(self) -> bool:
        """Save accounts to file"""
        try:
            accounts_data = [account.to_dict() for account in self.accounts]
            with open(self._accounts_file, 'w', encoding='utf-8') as file:
                json.dump(accounts_data, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save accounts: {e}")
            return False
    
    def load_accounts(self) -> bool:
        """Load accounts from file"""
        try:
            if not os.path.exists(self._accounts_file):
                return True  # No file yet, that's OK
            
            with open(self._accounts_file, 'r', encoding='utf-8') as file:
                accounts_data = json.load(file)
            
            self.accounts = [AccountData.from_dict(data) for data in accounts_data]
            self.accounts_loaded.emit()
            # Trigger avatar fetch for all accounts in background threads
            for account in self.accounts:
                threading.Thread(target=self._fetch_avatar_async, args=(account,), daemon=True).start()
            return True
            
        except Exception as e:
            print(f"Failed to load accounts: {e}")
            return False

    def _fetch_avatar_async(self, account: 'AccountData') -> None:
        """Fetch avatar via simple HTTP requests to steam profile XML and save locally"""
        try:
            steam_id_str = str(account.steam_id)
            if not steam_id_str.isdigit():
                return
            # Steam community XML profile
            profile_url = f"https://steamcommunity.com/profiles/{steam_id_str}?xml=1"
            with urllib.request.urlopen(profile_url, timeout=10) as resp:
                xml_data = resp.read()
            # Parse XML for avatarMedium or avatarFull
            root = ET.fromstring(xml_data)
            # Prefer avatarFull, then avatarMedium
            avatar_url_node = root.find('avatarFull') or root.find('avatarMedium') or root.find('avatarIcon')
            if avatar_url_node is None or not avatar_url_node.text:
                return
            avatar_url = avatar_url_node.text.strip()
            # Prefer highest resolution variant by rewriting to `_full` when possible
            try:
                if "steamstatic.com" in avatar_url:
                    if "_full" not in avatar_url:
                        if "_medium" in avatar_url:
                            avatar_url = avatar_url.replace("_medium", "_full")
                        elif "_icon" in avatar_url:
                            avatar_url = avatar_url.replace("_icon", "_full")
                        else:
                            # Append _full before extension if pattern matches hash.ext
                            if avatar_url.rfind('.') > avatar_url.rfind('/'):
                                dot = avatar_url.rfind('.')
                                avatar_url = f"{avatar_url[:dot]}_full{avatar_url[dot:]}"
            except Exception:
                pass
            # Download image
            with urllib.request.urlopen(avatar_url, timeout=10) as img_resp:
                img_bytes = img_resp.read()
            # Save to avatars folder
            ext = '.jpg'
            lower_url = avatar_url.lower()
            if lower_url.endswith('.png'):
                ext = '.png'
            local_path = os.path.join('avatars', f"{steam_id_str}{ext}")
            with open(local_path, 'wb') as f:
                f.write(img_bytes)
            # Update account and persist
            account.avatar_url = local_path
            self.save_accounts()
            # Notify UI that account updated
            self.account_updated.emit(account)
        except Exception:
            # Silently ignore avatar fetch failures
            pass


class AuthenticationManager(QObject):
    """Handles Steam authentication operations"""
    
    # Signals for authentication status
    login_started = pyqtSignal(str)  # steam_id
    login_completed = pyqtSignal(str, bool)  # steam_id, success
    code_generated = pyqtSignal(str, str)  # steam_id, code
    session_refreshed = pyqtSignal(str, bool)  # steam_id, success
    
    def __init__(self):
        super().__init__()
        self._authenticated_accounts: Dict[str, Any] = {}
        self._code_timers: Dict[str, QTimer] = {}
        self._steam_clients: Dict[str, Any] = {}  # Store SteamClient instances
        # Background asyncio loop for all network operations
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None
        self._loop_ready = threading.Event()

        self._ensure_loop()

    def _loop_target(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            self._loop_ready.set()
            loop.run_forever()
        except Exception:
            pass

    def _ensure_loop(self):
        if self._loop is not None and self._loop.is_running():
            return
        self._loop_ready.clear()
        self._loop_thread = threading.Thread(target=self._loop_target, daemon=True)
        self._loop_thread.start()
        self._loop_ready.wait(timeout=5)

    def submit(self, coro: asyncio.Future):
        """Submit coroutine to background event loop and get a concurrent.futures.Future"""
        self._ensure_loop()
        return asyncio.run_coroutine_threadsafe(coro, self._loop)
    
    async def login_account(self, account: AccountData) -> Dict[str, Any]:
        """
        Login to Steam account using aiosteampy
        """
        try:
            self.login_started.emit(str(account.steam_id))
            
            # Import aiosteampy client
            from aiosteampy.client import SteamClient
            from aiohttp import ClientSession
            
            # Create session
            session = ClientSession(raise_for_status=True)
            
            # Parse mafile to get secrets
            with open(account.mafile_path, 'r', encoding='utf-8') as f:
                mafile_data = json.load(f)
            
            shared_secret = mafile_data.get('shared_secret', '')
            identity_secret = mafile_data.get('identity_secret', '')
            
            # Create Steam client
            client = SteamClient(
                steam_id=int(str(account.steam_id) or 0),
                username=account.account_name,
                password=account.password,
                shared_secret=shared_secret,
                identity_secret=identity_secret,
                access_token=account.access_token if account.access_token else None,
                refresh_token=account.refresh_token if account.refresh_token else None,
                session=session
            )
            
            # Try to refresh session if we have tokens
            if account.access_token or account.refresh_token:
                try:
                    # Check if access token is expired
                    if client.is_access_token_expired and not client.is_refresh_token_expired:
                        # Refresh the access token
                        await client.refresh_access_token()
                        self.session_refreshed.emit(str(account.steam_id), True)
                    elif not client.is_access_token_expired:
                        # Access token is still valid
                        self.session_refreshed.emit(str(account.steam_id), True)
                except Exception as e:
                    # If refresh fails, we'll do a full login
                    pass
            
            # If we still need to login (no valid tokens), do full login
            if client.is_access_token_expired or not (account.access_token or account.refresh_token):
                await client.login()
            
            # Store the client for future use
            self._steam_clients[str(account.steam_id)] = client
            
            # Update account with new tokens
            account.update_session(client.access_token or '', client.refresh_token or '')

            # Mark as authenticated
            self._authenticated_accounts[account.steam_id] = True
            
            # Start code generation timer
            self._start_code_timer(account.steam_id, client)
            
            self.login_completed.emit(str(account.steam_id), True)
            return {'success': True, 'message': 'Login successful', 'client': client}
            
        except Exception as e:
            self.login_completed.emit(str(account.steam_id), False)
            return {'success': False, 'error': f'Login failed: {str(e)}'}
    
    async def refresh_session(self, account: AccountData) -> Dict[str, Any]:
        """
        Refresh session using refresh token
        """
        try:
            if str(account.steam_id) not in self._steam_clients:
                return {'success': False, 'error': 'No active session'}
            
            client = self._steam_clients[str(account.steam_id)]
            
            # Refresh the access token
            await client.refresh_access_token()
            
            # Update account with new tokens
            account.update_session(client.access_token or '', client.refresh_token or '')
            
            self.session_refreshed.emit(str(account.steam_id), True)
            return {'success': True, 'message': 'Session refreshed'}
            
        except Exception as e:
            self.session_refreshed.emit(account.steam_id, False)
            return {'success': False, 'error': f'Session refresh failed: {str(e)}'}
    
    def generate_auth_code(self, account: AccountData) -> str:
        """
        Generate Steam Guard authentication code using aiosteampy
        """
        try:
            # Check if we have a client for this account
            if str(account.steam_id) in self._steam_clients:
                client = self._steam_clients[str(account.steam_id)]
                return client.two_factor_code
            else:
                # Fallback to manual generation using the mafile
                # Import aiosteampy utils
                from aiosteampy.utils import gen_two_factor_code
                
                # Parse mafile to get shared_secret
                try:
                    with open(account.mafile_path, 'r', encoding='utf-8') as f:
                        mafile_data = json.load(f)
                    shared_secret = mafile_data.get('shared_secret', '')
                    if not shared_secret:
                        return "00000"
                    
                    return gen_two_factor_code(shared_secret)
                except Exception as e:
                    print(f"Error reading mafile for 2FA code generation: {e}")
                    return "00000"
                
        except Exception as e:
            print(f"Error generating 2FA code: {e}")
            return "00000"
    
    def is_authenticated(self, steam_id: str) -> bool:
        """Check if account is authenticated"""
        # Consider presence of an active client as authenticated
        return str(steam_id) in self._steam_clients
    
    def _start_code_timer(self, steam_id: str, client):
        """Start timer for periodic code generation"""
        if steam_id in self._code_timers:
            self._code_timers[steam_id].stop()
        
        timer = QTimer()
        timer.timeout.connect(lambda: self._generate_periodic_code(steam_id, client))
        timer.start(30000)  # Generate new code every 30 seconds
        self._code_timers[steam_id] = timer
        
        # Generate initial code
        self._generate_periodic_code(steam_id, client)
    
    def _generate_periodic_code(self, steam_id: str, client):
        """Generate periodic authentication code"""
        try:
            # Generate code using the client
            code = client.two_factor_code
            self.code_generated.emit(str(steam_id), str(code))
        except Exception as e:
            print(f"Error generating periodic code: {e}")
            # Fallback to manual generation
            # We need to get the account data to generate the code manually
            # In a real implementation, we would have access to the account manager
            # For now, emit a default code
            self.code_generated.emit(str(steam_id), "00000")


class ConfirmationManager(QObject):
    """Manages Steam trade confirmations"""
    
    # Signals for confirmation updates
    confirmations_loaded = pyqtSignal(str, list)  # steam_id, confirmations
    confirmation_processed = pyqtSignal(str, str, bool)  # steam_id, confirmation_id, accepted
    
    def __init__(self):
        super().__init__()
        self._confirmation_cache: Dict[str, List[Dict[str, Any]]] = {}
    
    async def load_confirmations(self, account: AccountData, auth_manager: AuthenticationManager) -> Dict[str, Any]:
        """
        Load confirmations for account using aiosteampy
        """
        try:
            # Check if we have an authenticated client
            if account.steam_id not in auth_manager._steam_clients:
                return {'success': False, 'error': 'Account not authenticated'}
            
            client = auth_manager._steam_clients[account.steam_id]
            
            # Fetch confirmations using aiosteampy
            try:
                confirmations = await client.get_confirmations()
                
                # Convert to our format with descriptive headlines per type
                formatted_confirmations = []
                for conf in confirmations:
                    conf_type = conf.type.name if hasattr(conf.type, 'name') else str(conf.type)
                    headline = getattr(conf, 'headline', None) or ''
                    summary = getattr(conf, 'summary', None) or ''
                    if headline:
                        description = headline
                    elif conf_type in ('TRADE', 'LISTING', 'MARKET') and summary:
                        description = summary
                    else:
                        description = f"Confirmation {conf.id}"
                    formatted_confirmations.append({
                        'id': conf.id,
                        'type': conf_type,
                        'description': description,
                        'summary': summary,
                        'headline': headline,
                        'creator_id': conf.creator_id,
                        'nonce': conf.nonce
                    })
                
                # Cache confirmations
                self._confirmation_cache[account.steam_id] = formatted_confirmations
                
                # Emit signal
                self.confirmations_loaded.emit(account.steam_id, formatted_confirmations)
                
                return {'success': True, 'confirmations': formatted_confirmations}
                
            except Exception as e:
                # If we get an error, try to refresh the session and retry
                try:
                    refresh_result = await auth_manager.refresh_session(account)
                    if refresh_result['success']:
                        # Retry fetching confirmations
                        confirmations = await client.get_confirmations()
                        
                        # Convert to our format with descriptive headlines per type
                        formatted_confirmations = []
                        for conf in confirmations:
                            conf_type = conf.type.name if hasattr(conf.type, 'name') else str(conf.type)
                            headline = getattr(conf, 'headline', None) or ''
                            summary = getattr(conf, 'summary', None) or ''
                            if headline:
                                description = headline
                            elif conf_type in ('TRADE', 'LISTING', 'MARKET') and summary:
                                description = summary
                            else:
                                description = f"Confirmation {conf.id}"
                            formatted_confirmations.append({
                                'id': conf.id,
                                'type': conf_type,
                                'description': description,
                                'summary': summary,
                                'headline': headline,
                                'creator_id': conf.creator_id,
                                'nonce': conf.nonce
                            })
                        
                        # Cache confirmations
                        self._confirmation_cache[account.steam_id] = formatted_confirmations
                        
                        # Emit signal
                        self.confirmations_loaded.emit(account.steam_id, formatted_confirmations)
                        
                        return {'success': True, 'confirmations': formatted_confirmations}
                    else:
                        return {'success': False, 'error': f'Failed to load confirmations: {str(e)}'}
                except Exception as refresh_error:
                    return {'success': False, 'error': f'Failed to load confirmations: {str(e)}'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to load confirmations: {str(e)}'}
    
    async def accept_confirmation(self, steam_id: str, confirmation_id: str, auth_manager: AuthenticationManager) -> Dict[str, Any]:
        """
        Accept trade confirmation using aiosteampy
        """
        try:
            # Check if we have an authenticated client
            if steam_id not in auth_manager._steam_clients:
                return {'success': False, 'error': 'Account not authenticated'}
            
            client = auth_manager._steam_clients[steam_id]
            
            # Find the confirmation in cache
            confirmation = None
            if steam_id in self._confirmation_cache:
                for conf in self._confirmation_cache[steam_id]:
                    if str(conf['id']) == str(confirmation_id):
                        confirmation = conf
                        break
            
            if not confirmation:
                return {'success': False, 'error': 'Confirmation not found'}
            
            try:
                # Accept the confirmation using aiosteampy
                # Create a simple confirmation object with the required attributes
                from aiosteampy.models import Confirmation
                from aiosteampy.constants import ConfirmationType
                
                # Create a confirmation object with the cached data
                conf_obj = Confirmation(
                    id=int(confirmation['id']),
                    nonce=confirmation['nonce'],
                    creator_id=int(confirmation['creator_id']),
                    creation_time=datetime.min,
                    type=ConfirmationType.UNKNOWN,
                    icon="",
                    multi=False,
                    headline="",
                    summary="",
                    warn=None
                )
                
                # Accept the confirmation
                await client.allow_confirmation(conf_obj)
                
                # Remove from cache
                if steam_id in self._confirmation_cache:
                    self._confirmation_cache[steam_id] = [
                        conf for conf in self._confirmation_cache[steam_id] 
                        if str(conf['id']) != str(confirmation_id)
                    ]
                
                self.confirmation_processed.emit(steam_id, confirmation_id, True)
                return {'success': True, 'message': 'Confirmation accepted'}
                
            except Exception as e:
                return {'success': False, 'error': f'Failed to accept confirmation: {str(e)}'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to accept confirmation: {str(e)}'}
    
    async def decline_confirmation(self, steam_id: str, confirmation_id: str, auth_manager: AuthenticationManager) -> Dict[str, Any]:
        """
        Decline trade confirmation using aiosteampy
        """
        try:
            # Check if we have an authenticated client
            if steam_id not in auth_manager._steam_clients:
                return {'success': False, 'error': 'Account not authenticated'}
            
            client = auth_manager._steam_clients[steam_id]
            
            # Find the confirmation in cache
            confirmation = None
            if steam_id in self._confirmation_cache:
                for conf in self._confirmation_cache[steam_id]:
                    if str(conf['id']) == str(confirmation_id):
                        confirmation = conf
                        break
            
            if not confirmation:
                return {'success': False, 'error': 'Confirmation not found'}
            
            try:
                # Decline the confirmation using aiosteampy
                # Create a simple confirmation object with the required attributes
                from aiosteampy.models import Confirmation
                from aiosteampy.constants import ConfirmationType
                
                # Create a confirmation object with the cached data
                conf_obj = Confirmation(
                    id=int(confirmation['id']),
                    nonce=confirmation['nonce'],
                    creator_id=int(confirmation['creator_id']),
                    creation_time=datetime.min,
                    type=ConfirmationType.UNKNOWN,
                    icon="",
                    multi=False,
                    headline="",
                    summary="",
                    warn=None
                )
                
                # Decline the confirmation
                await client.send_confirmation(conf_obj, "cancel")
                
                # Remove from cache
                if steam_id in self._confirmation_cache:
                    self._confirmation_cache[steam_id] = [
                        conf for conf in self._confirmation_cache[steam_id] 
                        if str(conf['id']) != str(confirmation_id)
                    ]
                
                self.confirmation_processed.emit(steam_id, confirmation_id, False)
                return {'success': True, 'message': 'Confirmation declined'}
                
            except Exception as e:
                return {'success': False, 'error': f'Failed to decline confirmation: {str(e)}'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to decline confirmation: {str(e)}'}
    
    def get_cached_confirmations(self, steam_id: str) -> List[Dict[str, Any]]:
        """Get cached confirmations for account"""
        return self._confirmation_cache.get(steam_id, [])

# Utility functions for integration
def create_account_managers():
    """Create and return account management instances"""
    account_manager = AccountManager()
    auth_manager = AuthenticationManager()
    confirmation_manager = ConfirmationManager()
    
    return account_manager, auth_manager, confirmation_manager
