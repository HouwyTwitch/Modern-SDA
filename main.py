import sys
import asyncio
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Import the main application window
from src.ui.main_window import SteamAuthenticatorGUI


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    window = SteamAuthenticatorGUI()
    window.show()
    
    # Start the asyncio event loop in a separate thread or integrate with Qt
    # For simplicity, we'll use QTimer to periodically process async events
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()