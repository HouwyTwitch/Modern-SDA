# Modern SDA

A modern PyQt5-based Steam Desktop Authenticator GUI.

## Features

- **Multiple accounts** — add and manage as many Steam accounts as you need
- **TOTP auth codes** — generates Steam Guard codes with a live countdown timer
- **Trade confirmations** — view, accept, and decline pending trade/market confirmations
- **Session persistence** — stores refresh tokens so you don't re-login on every launch
- **Proxy support** — per-account HTTP proxy configuration (`http://user:pass@ip:port`)
- **Themes** — built-in dark, light, and high-contrast themes with live switching
- **Search** — filter accounts by name or Steam ID

## Requirements

- Python 3.10+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [aiosteampy](https://github.com/somespecialone/aiosteampy) (vendored copy included)
- [aiohttp](https://pypi.org/project/aiohttp/)

Install dependencies:

```bash
pip install PyQt5 aiohttp
```

> `aiosteampy` is bundled in the `aiosteampy/` directory and does not need to be installed separately.

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
