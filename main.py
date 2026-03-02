import sys
import os
import logging
import traceback

# ---------------------------------------------------------------------------
# Logging setup — writes to modern_sda.log AND stderr
# ---------------------------------------------------------------------------
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modern_sda.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)

# Also capture aiohttp / aiosteampy debug output
logging.getLogger("aiohttp").setLevel(logging.DEBUG)
logging.getLogger("aiosteampy").setLevel(logging.DEBUG)

logger = logging.getLogger("main")
logger.info("=== Modern-SDA starting ===")
logger.info("Log file: %s", LOG_FILE)
logger.info("Python: %s", sys.version)
logger.info("aiosteampy location: %s", __import__("aiosteampy").__file__)

# Catch all unhandled exceptions and log them
def _excepthook(exc_type, exc_value, exc_tb):
    logger.critical(
        "Unhandled exception:\n%s",
        "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
    )
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _excepthook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import SteamAuthenticatorGUI


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = SteamAuthenticatorGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
