import sys
import os

# Prefer vendored aiosteampy (bundled in project) over system installation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication

# Import the main application window
from src.ui.main_window import SteamAuthenticatorGUI


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    window = SteamAuthenticatorGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
