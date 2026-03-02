"""
Standalone aiosteampy login test.
Run:  python test_login.py path/to/account.mafile
"""

import sys
import json
import asyncio
import logging
import traceback

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.FileHandler("test_login.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logging.getLogger("aiohttp").setLevel(logging.DEBUG)
logging.getLogger("aiosteampy").setLevel(logging.DEBUG)
log = logging.getLogger("test_login")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_mafile(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


async def _test_login(mafile_path: str, username: str, password: str) -> None:
    import aiosteampy
    from aiosteampy.client import SteamClient
    from aiohttp import ClientSession

    log.info("aiosteampy version : %s", aiosteampy.__version__)
    log.info("aiosteampy location: %s", aiosteampy.__file__)

    mafile = _load_mafile(mafile_path)
    shared_secret   = mafile.get("shared_secret", "")
    identity_secret = mafile.get("identity_secret", "")
    steam_id        = int(str(mafile.get("Session", {}).get("SteamID") or
                              mafile.get("steam_id") or 0))

    log.info("steam_id=%d  username=%s", steam_id, username)
    log.info("shared_secret present=%s  identity_secret present=%s",
             bool(shared_secret), bool(identity_secret))

    session = ClientSession(raise_for_status=True)
    try:
        log.info("Building SteamClient (no pre-set tokens) …")
        client = SteamClient(
            steam_id=steam_id,
            username=username,
            password=password,
            shared_secret=shared_secret,
            identity_secret=identity_secret,
            session=session,
        )

        log.info("Calling client.login() …")
        await client.login()

        log.info("LOGIN SUCCEEDED")
        log.info("  access_token  present=%s", bool(client.access_token))
        log.info("  refresh_token present=%s", bool(client.refresh_token))
        log.info("  is_access_token_expired =%s", client.is_access_token_expired)
        log.info("  is_refresh_token_expired=%s", client.is_refresh_token_expired)

    except Exception:
        log.error("LOGIN FAILED:\n%s", traceback.format_exc())
    finally:
        await session.close()
        log.info("Session closed.")


def main() -> None:
    if len(sys.argv) < 4:
        print()
        print("Usage:")
        print("  python test_login.py <path/to/account.mafile> <username> <password>")
        print()
        print("Example:")
        print("  python test_login.py accounts/myaccount.mafile myuser mypass")
        print()
        sys.exit(1)

    mafile_path = sys.argv[1]
    username    = sys.argv[2]
    password    = sys.argv[3]

    asyncio.run(_test_login(mafile_path, username, password))


if __name__ == "__main__":
    main()
