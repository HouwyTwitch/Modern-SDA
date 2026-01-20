import sys
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
