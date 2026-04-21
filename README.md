# Modern SDA

A modern PyQt5-based Steam Desktop Authenticator GUI.

<img width="479" height="718" alt="image" src="https://github.com/user-attachments/assets/702a9120-2e5b-4686-bebc-363ae38a7745" />
<img width="480" height="714" alt="image" src="https://github.com/user-attachments/assets/86ee6030-05bf-4eff-a03d-6e485aaae47e" />
<img width="474" height="718" alt="image" src="https://github.com/user-attachments/assets/145b51d5-9ce9-4a54-84b9-84441e65045b" />
<img width="481" height="545" alt="image" src="https://github.com/user-attachments/assets/d03417bc-32b5-4f7f-b746-555a5a586e3c" />



## Features

- **Multiple accounts** — add and manage as many Steam accounts as you need
- **TOTP auth codes** — generates Steam Guard codes with a live countdown timer
- **QR login approval** — paste the "Sign in on computer" QR URL to approve (or deny) Steam sign-in from this app
- **All confirmation types** — accepts any Steam confirmation: trades, market listings, Steam API key activations, and more
- **Trade confirmations** — view, accept, and decline pending confirmations
- **Accept All** — bulk-accept every pending confirmation at once (shown when 2+ are pending)
- **Auto-confirm** — opt-in background auto-acceptance of trade offers and/or market listings
- **Auto-refresh confirmations** — optional background polling for new pending confirmations
- **Confirmation type badges** — visual indicators for Trade, Market, API key, and other types
- **Session persistence** — stores refresh tokens so you don't re-login on every launch
- **Remembers selection** — auto-selects the last-used account on launch
- **Proxy support** — per-account HTTP proxy configuration (`http://user:pass@ip:port`)
- **Themes** — built-in dark, light, and high-contrast themes with live switching
- **Search** — filter accounts by name or Steam ID

## Requirements

- Python 3.10+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [aiosteampy](https://github.com/somespecialone/aiosteampy)
- [aiohttp](https://pypi.org/project/aiohttp/)

Install dependencies:

```bash
pip install PyQt5 aiosteampy aiohttp
```

## Usage

```bash
python main.py
```

## Adding an Account

1. Click the **+** button in the bottom-right corner.
2. Select your `.mafile` (exported from Steam Desktop Authenticator or compatible tools).
3. Enter your Steam account password.
4. Optionally, enter an HTTP proxy URL.
5. Click **Add Account**.

The app reads `shared_secret` and `identity_secret` from the mafile to generate auth codes and confirm trades without additional network calls on startup.

## Project Structure

```
main.py                        # Entry point
src/
  account_manager.py           # AccountManager, AuthenticationManager, ConfirmationManager
  settings.py                  # Persistent settings (JSON)
  theme.py                     # ThemeManager, colour tokens, ThemedComboBox
  ui/
    main_window.py             # Top-level window, navigation, signal routing
    account_widget.py          # Per-account card widget
    floating_add_button.py     # Animated FAB
    confirmation_item.py       # Per-confirmation row widget
    add_account_dialog.py      # Dialog for adding an account
    edit_account_dialog.py     # Dialog for editing an account
    screens/
      accounts_screen.py       # Accounts tab (code display + account list)
      confirmations_screen.py  # Confirmations tab
      settings_screen.py       # Settings tab
```

## Data Files

| File | Purpose |
|---|---|
| `accounts.json` | Stored account metadata (tokens, paths) — keep private |
| `settings.json` | User preferences (theme, refresh interval, etc.) |

> **Note:** `accounts.json` contains session tokens. Do not share it.

## License

MIT



