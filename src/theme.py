from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QDialog, QFormLayout,
    QComboBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt5.QtSvg import QSvgRenderer


class MidnightTheme:
    BACKGROUND = "#0E1116"
    SURFACE = "#141A23"
    SURFACE_ELEVATED = "#182131"
    SURFACE_HOVER = "#1D283A"

    ACCENT = "#4C7DFF"
    ACCENT_HOVER = "#5A8BFF"
    ACCENT_PRESSED = "#3E69E6"

    TEXT_PRIMARY = "#EEF2FF"
    TEXT_SECONDARY = "#AEB8CE"
    TEXT_TERTIARY = "#7F8AA3"

    BORDER = "#273245"
    BORDER_FOCUS = "#4C7DFF"

    SUCCESS = "#3DBE7A"
    SUCCESS_HOVER = "#33A86B"

    ERROR = "#E45D5D"
    ERROR_HOVER = "#C94E4E"

    SHADOW = "#05060A"
    
    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24) -> QIcon:
        """Create a colored SVG icon"""
        # Replace fill color in SVG
        colored_svg = svg_content.replace('currentColor', color)
        
        # Create QPixmap from SVG
        svg_bytes = QByteArray(colored_svg.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Using QColor for transparent instead of Qt.transparent
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    @staticmethod
    def get_accounts_svg() -> str:
        """SVG for accounts icon"""
        return '''
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z" fill="currentColor"/>
            <path d="M12 14C7.58172 14 4 17.5817 4 22H20C20 17.5817 16.4183 14 12 14Z" fill="currentColor"/>
        </svg>
        '''
    
    @staticmethod
    def get_confirmations_svg() -> str:
        """SVG for confirmations icon"""
        return '''
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
        </svg>
        '''
    
    @staticmethod
    def get_settings_svg() -> str:
        """SVG for settings icon"""
        return '''
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z" fill="currentColor"/>
        </svg>
        '''
    
    @staticmethod
    def get_accept_svg() -> str:
        """SVG for accept/checkmark icon"""
        return '''
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
        </svg>
        '''
    
    @staticmethod
    def get_decline_svg() -> str:
        """SVG for decline/X icon"""
        return '''
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" fill="currentColor"/>
        </svg>
        '''
    
    @staticmethod
    def get_stylesheet():
        # Always use MidnightTheme's own class attributes so that other themes
        # can call this and then reliably str.replace() the Noctua colours.
        theme = MidnightTheme
        return f"""
        QMainWindow {{
            background-color: {theme.BACKGROUND};
            color: {theme.TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }}
        
        QWidget {{
            background-color: transparent;
            color: {theme.TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }}
        
        QLineEdit {{
            background-color: {theme.SURFACE_ELEVATED};
            border: 1px solid {theme.BORDER};
            border-radius: 6px;
            padding: 14px 18px;
            font-size: 14px;
            color: {theme.TEXT_PRIMARY};
            selection-background-color: {theme.ACCENT};
            selection-color: {theme.TEXT_PRIMARY};
        }}

        QLineEdit:hover {{
            border-color: {theme.BORDER_FOCUS};
        }}

        QLineEdit:focus {{
            border-color: {theme.BORDER_FOCUS};
            background-color: {theme.SURFACE_HOVER};
        }}

        QLineEdit::placeholder {{
            color: {theme.TEXT_TERTIARY};
        }}

        QPushButton {{
            background-color: {theme.ACCENT};
            border: none;
            border-radius: 6px;
            padding: 14px 24px;
            font-size: 14px;
            font-weight: 600;
            color: {theme.TEXT_PRIMARY};
            min-height: 20px;
        }}

        QPushButton:hover {{
            background-color: {theme.ACCENT_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {theme.ACCENT_PRESSED};
        }}

        QDialog {{
            background-color: {theme.SURFACE};
            border: 1px solid {theme.BORDER};
            border-radius: 6px;
        }}

        QComboBox {{
            background-color: {theme.SURFACE_ELEVATED};
            border: 1px solid {theme.BORDER};
            border-radius: 5px;
            padding: 8px 12px;
            color: {theme.TEXT_PRIMARY};
        }}

        QComboBox:hover {{
            border-color: {theme.BORDER_FOCUS};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 28px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border: none;
        }}

        QFormLayout QLabel {{
            color: {theme.TEXT_SECONDARY};
            font-weight: 500;
            margin-bottom: 4px;
        }}

        QScrollArea {{
            border: none;
            background-color: transparent;
        }}

        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}

        QScrollBar:vertical {{
            background-color: {theme.SURFACE};
            width: 8px;
            border-radius: 2px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {theme.ACCENT};
            border-radius: 2px;
            min-height: 20px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {theme.ACCENT_HOVER};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0px;
        }}

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QToolTip {{
            background-color: {theme.SURFACE_ELEVATED};
            color: {theme.TEXT_PRIMARY};
            border: 1px solid {theme.BORDER};
            border-radius: 4px;
            padding: 6px 8px;
        }}
        """


class LightTheme:
    BACKGROUND = "#F3F5F8"
    SURFACE = "#E9EDF3"
    SURFACE_ELEVATED = "#DDE3EC"
    SURFACE_HOVER = "#D3DAE6"

    ACCENT = "#2F6BFF"
    ACCENT_HOVER = "#3A77FF"
    ACCENT_PRESSED = "#2457D8"

    TEXT_PRIMARY = "#101828"
    TEXT_SECONDARY = "#344054"
    TEXT_TERTIARY = "#667085"

    BORDER = "#C7D0DD"
    BORDER_FOCUS = "#2F6BFF"

    SUCCESS = "#12B76A"
    SUCCESS_HOVER = "#0E9F5A"

    ERROR = "#F04438"
    ERROR_HOVER = "#D92D20"

    SHADOW = "#AAB4C5"

    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24):
        return MidnightTheme.create_svg_icon(svg_content, color, size)

    @staticmethod
    def get_accounts_svg():
        return MidnightTheme.get_accounts_svg()

    @staticmethod
    def get_confirmations_svg():
        return MidnightTheme.get_confirmations_svg()

    @staticmethod
    def get_settings_svg():
        return MidnightTheme.get_settings_svg()

    @staticmethod
    def get_stylesheet():
        return MidnightTheme.get_stylesheet().replace(MidnightTheme.BACKGROUND, LightTheme.BACKGROUND)\
            .replace(MidnightTheme.SURFACE, LightTheme.SURFACE)\
            .replace(MidnightTheme.SURFACE_ELEVATED, LightTheme.SURFACE_ELEVATED)\
            .replace(MidnightTheme.SURFACE_HOVER, LightTheme.SURFACE_HOVER)\
            .replace(MidnightTheme.ACCENT, LightTheme.ACCENT)\
            .replace(MidnightTheme.ACCENT_HOVER, LightTheme.ACCENT_HOVER)\
            .replace(MidnightTheme.ACCENT_PRESSED, LightTheme.ACCENT_PRESSED)\
            .replace(MidnightTheme.TEXT_PRIMARY, LightTheme.TEXT_PRIMARY)\
            .replace(MidnightTheme.TEXT_SECONDARY, LightTheme.TEXT_SECONDARY)\
            .replace(MidnightTheme.TEXT_TERTIARY, LightTheme.TEXT_TERTIARY)\
            .replace(MidnightTheme.BORDER, LightTheme.BORDER)\
            .replace(MidnightTheme.BORDER_FOCUS, LightTheme.BORDER_FOCUS)\
            .replace(MidnightTheme.SUCCESS, LightTheme.SUCCESS)\
            .replace(MidnightTheme.ERROR, LightTheme.ERROR)


class DarkTheme:
    BACKGROUND = "#0F0F12"
    SURFACE = "#17181C"
    SURFACE_ELEVATED = "#1E2026"
    SURFACE_HOVER = "#262A33"

    ACCENT = "#7B61FF"
    ACCENT_HOVER = "#8A74FF"
    ACCENT_PRESSED = "#6447FF"

    TEXT_PRIMARY = "#F5F7FF"
    TEXT_SECONDARY = "#B5B9C6"
    TEXT_TERTIARY = "#7D8292"

    BORDER = "#2B2E36"
    BORDER_FOCUS = "#7B61FF"

    SUCCESS = "#2ECC71"
    SUCCESS_HOVER = "#27B863"

    ERROR = "#FF5C7A"
    ERROR_HOVER = "#E24B67"

    SHADOW = "#000000"

    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24):
        return MidnightTheme.create_svg_icon(svg_content, color, size)

    @staticmethod
    def get_accounts_svg():
        return MidnightTheme.get_accounts_svg()

    @staticmethod
    def get_confirmations_svg():
        return MidnightTheme.get_confirmations_svg()

    @staticmethod
    def get_settings_svg():
        return MidnightTheme.get_settings_svg()

    @staticmethod
    def get_stylesheet():
        return MidnightTheme.get_stylesheet().replace(MidnightTheme.BACKGROUND, DarkTheme.BACKGROUND)\
            .replace(MidnightTheme.SURFACE, DarkTheme.SURFACE)\
            .replace(MidnightTheme.SURFACE_ELEVATED, DarkTheme.SURFACE_ELEVATED)\
            .replace(MidnightTheme.SURFACE_HOVER, DarkTheme.SURFACE_HOVER)\
            .replace(MidnightTheme.ACCENT, DarkTheme.ACCENT)\
            .replace(MidnightTheme.ACCENT_HOVER, DarkTheme.ACCENT_HOVER)\
            .replace(MidnightTheme.ACCENT_PRESSED, DarkTheme.ACCENT_PRESSED)\
            .replace(MidnightTheme.TEXT_PRIMARY, DarkTheme.TEXT_PRIMARY)\
            .replace(MidnightTheme.TEXT_SECONDARY, DarkTheme.TEXT_SECONDARY)\
            .replace(MidnightTheme.TEXT_TERTIARY, DarkTheme.TEXT_TERTIARY)\
            .replace(MidnightTheme.BORDER, DarkTheme.BORDER)\
            .replace(MidnightTheme.BORDER_FOCUS, DarkTheme.BORDER_FOCUS)\
            .replace(MidnightTheme.SUCCESS, DarkTheme.SUCCESS)\
            .replace(MidnightTheme.ERROR, DarkTheme.ERROR)


class OceanTheme:
    BACKGROUND = "#071A23"
    SURFACE = "#0E2430"
    SURFACE_ELEVATED = "#123040"
    SURFACE_HOVER = "#173C51"

    ACCENT = "#2BB8AE"
    ACCENT_HOVER = "#3AC7BD"
    ACCENT_PRESSED = "#219A93"

    TEXT_PRIMARY = "#EAF6F7"
    TEXT_SECONDARY = "#A7C6CC"
    TEXT_TERTIARY = "#7196A3"

    BORDER = "#204053"
    BORDER_FOCUS = "#2BB8AE"

    SUCCESS = "#38D39F"
    SUCCESS_HOVER = "#2DBB8C"

    ERROR = "#FF6B6B"
    ERROR_HOVER = "#E25555"

    SHADOW = "#061219"

    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24):
        return MidnightTheme.create_svg_icon(svg_content, color, size)

    @staticmethod
    def get_accounts_svg():
        return MidnightTheme.get_accounts_svg()

    @staticmethod
    def get_confirmations_svg():
        return MidnightTheme.get_confirmations_svg()

    @staticmethod
    def get_settings_svg():
        return MidnightTheme.get_settings_svg()

    @staticmethod
    def get_stylesheet():
        return MidnightTheme.get_stylesheet().replace(MidnightTheme.BACKGROUND, OceanTheme.BACKGROUND)\
            .replace(MidnightTheme.SURFACE, OceanTheme.SURFACE)\
            .replace(MidnightTheme.SURFACE_ELEVATED, OceanTheme.SURFACE_ELEVATED)\
            .replace(MidnightTheme.SURFACE_HOVER, OceanTheme.SURFACE_HOVER)\
            .replace(MidnightTheme.ACCENT, OceanTheme.ACCENT)\
            .replace(MidnightTheme.ACCENT_HOVER, OceanTheme.ACCENT_HOVER)\
            .replace(MidnightTheme.ACCENT_PRESSED, OceanTheme.ACCENT_PRESSED)\
            .replace(MidnightTheme.TEXT_PRIMARY, OceanTheme.TEXT_PRIMARY)\
            .replace(MidnightTheme.TEXT_SECONDARY, OceanTheme.TEXT_SECONDARY)\
            .replace(MidnightTheme.TEXT_TERTIARY, OceanTheme.TEXT_TERTIARY)\
            .replace(MidnightTheme.BORDER, OceanTheme.BORDER)\
            .replace(MidnightTheme.BORDER_FOCUS, OceanTheme.BORDER_FOCUS)\
            .replace(MidnightTheme.SUCCESS, OceanTheme.SUCCESS)\
            .replace(MidnightTheme.ERROR, OceanTheme.ERROR)


class ForestTheme:
    BACKGROUND = "#08140E"
    SURFACE = "#0F2218"
    SURFACE_ELEVATED = "#143025"
    SURFACE_HOVER = "#1A3A2E"

    ACCENT = "#5FBF7A"
    ACCENT_HOVER = "#70CD8A"
    ACCENT_PRESSED = "#4FA76A"

    TEXT_PRIMARY = "#F1F7F2"
    TEXT_SECONDARY = "#B6C8BA"
    TEXT_TERTIARY = "#7D9A86"

    BORDER = "#234234"
    BORDER_FOCUS = "#5FBF7A"

    SUCCESS = "#49D18A"
    SUCCESS_HOVER = "#3ABA79"

    ERROR = "#E86767"
    ERROR_HOVER = "#CD5555"

    SHADOW = "#050E0A"

    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24):
        return MidnightTheme.create_svg_icon(svg_content, color, size)

    @staticmethod
    def get_accounts_svg():
        return MidnightTheme.get_accounts_svg()

    @staticmethod
    def get_confirmations_svg():
        return MidnightTheme.get_confirmations_svg()

    @staticmethod
    def get_settings_svg():
        return MidnightTheme.get_settings_svg()

    @staticmethod
    def get_stylesheet():
        return MidnightTheme.get_stylesheet().replace(MidnightTheme.BACKGROUND, ForestTheme.BACKGROUND)\
            .replace(MidnightTheme.SURFACE, ForestTheme.SURFACE)\
            .replace(MidnightTheme.SURFACE_ELEVATED, ForestTheme.SURFACE_ELEVATED)\
            .replace(MidnightTheme.SURFACE_HOVER, ForestTheme.SURFACE_HOVER)\
            .replace(MidnightTheme.ACCENT, ForestTheme.ACCENT)\
            .replace(MidnightTheme.ACCENT_HOVER, ForestTheme.ACCENT_HOVER)\
            .replace(MidnightTheme.ACCENT_PRESSED, ForestTheme.ACCENT_PRESSED)\
            .replace(MidnightTheme.TEXT_PRIMARY, ForestTheme.TEXT_PRIMARY)\
            .replace(MidnightTheme.TEXT_SECONDARY, ForestTheme.TEXT_SECONDARY)\
            .replace(MidnightTheme.TEXT_TERTIARY, ForestTheme.TEXT_TERTIARY)\
            .replace(MidnightTheme.BORDER, ForestTheme.BORDER)\
            .replace(MidnightTheme.BORDER_FOCUS, ForestTheme.BORDER_FOCUS)\
            .replace(MidnightTheme.SUCCESS, ForestTheme.SUCCESS)\
            .replace(MidnightTheme.ERROR, ForestTheme.ERROR)


class SolarTheme:
    BACKGROUND = "#17110C"
    SURFACE = "#211A14"
    SURFACE_ELEVATED = "#2C221A"
    SURFACE_HOVER = "#372B21"

    ACCENT = "#D98A3A"
    ACCENT_HOVER = "#E39A52"
    ACCENT_PRESSED = "#BF7430"

    TEXT_PRIMARY = "#F6EBDD"
    TEXT_SECONDARY = "#CDB59C"
    TEXT_TERTIARY = "#9B7C62"

    BORDER = "#3F2F22"
    BORDER_FOCUS = "#D98A3A"

    SUCCESS = "#46C48A"
    SUCCESS_HOVER = "#39AE78"

    ERROR = "#E46363"
    ERROR_HOVER = "#C95252"

    SHADOW = "#0B0704"

    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24):
        return MidnightTheme.create_svg_icon(svg_content, color, size)

    @staticmethod
    def get_accounts_svg():
        return MidnightTheme.get_accounts_svg()

    @staticmethod
    def get_confirmations_svg():
        return MidnightTheme.get_confirmations_svg()

    @staticmethod
    def get_settings_svg():
        return MidnightTheme.get_settings_svg()

    @staticmethod
    def get_stylesheet():
        return MidnightTheme.get_stylesheet().replace(MidnightTheme.BACKGROUND, SolarTheme.BACKGROUND)\
            .replace(MidnightTheme.SURFACE, SolarTheme.SURFACE)\
            .replace(MidnightTheme.SURFACE_ELEVATED, SolarTheme.SURFACE_ELEVATED)\
            .replace(MidnightTheme.SURFACE_HOVER, SolarTheme.SURFACE_HOVER)\
            .replace(MidnightTheme.ACCENT, SolarTheme.ACCENT)\
            .replace(MidnightTheme.ACCENT_HOVER, SolarTheme.ACCENT_HOVER)\
            .replace(MidnightTheme.ACCENT_PRESSED, SolarTheme.ACCENT_PRESSED)\
            .replace(MidnightTheme.TEXT_PRIMARY, SolarTheme.TEXT_PRIMARY)\
            .replace(MidnightTheme.TEXT_SECONDARY, SolarTheme.TEXT_SECONDARY)\
            .replace(MidnightTheme.TEXT_TERTIARY, SolarTheme.TEXT_TERTIARY)\
            .replace(MidnightTheme.BORDER, SolarTheme.BORDER)\
            .replace(MidnightTheme.BORDER_FOCUS, SolarTheme.BORDER_FOCUS)\
            .replace(MidnightTheme.SUCCESS, SolarTheme.SUCCESS)\
            .replace(MidnightTheme.ERROR, SolarTheme.ERROR)

class OldMoneyTheme:
    BACKGROUND = "#14100C"
    SURFACE = "#1D1712"
    SURFACE_ELEVATED = "#271F18"
    SURFACE_HOVER = "#31271E"

    ACCENT = "#B08A4A"
    ACCENT_HOVER = "#C19A59"
    ACCENT_PRESSED = "#96733C"

    TEXT_PRIMARY = "#F3E9D8"
    TEXT_SECONDARY = "#D4C3AA"
    TEXT_TERTIARY = "#A68E72"

    BORDER = "#3A2C21"
    BORDER_FOCUS = "#B08A4A"

    SUCCESS = "#5A8F6B"
    SUCCESS_HOVER = "#4E7F5E"

    ERROR = "#B14A4A"
    ERROR_HOVER = "#9A3F3F"

    SHADOW = "#070503"

    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24):
        return MidnightTheme.create_svg_icon(svg_content, color, size)

    @staticmethod
    def get_accounts_svg():
        return MidnightTheme.get_accounts_svg()

    @staticmethod
    def get_confirmations_svg():
        return MidnightTheme.get_confirmations_svg()

    @staticmethod
    def get_settings_svg():
        return MidnightTheme.get_settings_svg()

    @staticmethod
    def get_accept_svg():
        return MidnightTheme.get_accept_svg()

    @staticmethod
    def get_decline_svg():
        return MidnightTheme.get_decline_svg()

    @staticmethod
    def get_stylesheet():
        return MidnightTheme.get_stylesheet().replace(MidnightTheme.BACKGROUND, OldMoneyTheme.BACKGROUND)\
            .replace(MidnightTheme.SURFACE, OldMoneyTheme.SURFACE)\
            .replace(MidnightTheme.SURFACE_ELEVATED, OldMoneyTheme.SURFACE_ELEVATED)\
            .replace(MidnightTheme.SURFACE_HOVER, OldMoneyTheme.SURFACE_HOVER)\
            .replace(MidnightTheme.ACCENT, OldMoneyTheme.ACCENT)\
            .replace(MidnightTheme.ACCENT_HOVER, OldMoneyTheme.ACCENT_HOVER)\
            .replace(MidnightTheme.ACCENT_PRESSED, OldMoneyTheme.ACCENT_PRESSED)\
            .replace(MidnightTheme.TEXT_PRIMARY, OldMoneyTheme.TEXT_PRIMARY)\
            .replace(MidnightTheme.TEXT_SECONDARY, OldMoneyTheme.TEXT_SECONDARY)\
            .replace(MidnightTheme.TEXT_TERTIARY, OldMoneyTheme.TEXT_TERTIARY)\
            .replace(MidnightTheme.BORDER, OldMoneyTheme.BORDER)\
            .replace(MidnightTheme.BORDER_FOCUS, OldMoneyTheme.BORDER_FOCUS)\
            .replace(MidnightTheme.SUCCESS, OldMoneyTheme.SUCCESS)\
            .replace(MidnightTheme.ERROR, OldMoneyTheme.ERROR)


# Global theme manager
class ThemeManager:
    """Manages application themes"""

    themes = {
        "Midnight": MidnightTheme,  # renamed from "Noctua" to match its dark-blue coloring
        "Light": LightTheme,
        "Dark": DarkTheme,
        "Ocean": OceanTheme,
        "Forest": ForestTheme,
        "Solar": SolarTheme,
        "Old Money": OldMoneyTheme
    }

    current_theme = "Midnight"
    
    @classmethod
    def get_current_theme(cls):
        return cls.themes[cls.current_theme]
    
    @classmethod
    def set_theme(cls, theme_name: str):
        if theme_name in cls.themes:
            cls.current_theme = theme_name
            return True
        return False
    
    @classmethod
    def get_theme_names(cls):
        return list(cls.themes.keys())


class ThemedComboBox(QComboBox):
    """Custom QComboBox that properly applies theme to dropdown view"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_style = ""
        self.current_theme = None
        # Remove scrolling and auto-size to content
        self.setMaxVisibleItems(10)  # Allow more items to be visible
        
    def showPopup(self):
        """Override to ensure dropdown view gets proper styling and sizing"""
        super().showPopup()
        # Force apply styling to the popup view and its container
        view = self.view()
        if view and self.current_theme:
            # Disable scrolling and auto-size
            view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # Calculate proper height for all items
            item_count = self.count()
            item_height = 40  # Approximate height per item including padding
            total_height = item_count * item_height + 8  # +8 for padding
            view.setMinimumHeight(total_height)
            view.setMaximumHeight(total_height)
            
            # Style the view itself (without border to avoid double borders)
            view.setStyleSheet(f"""
                QAbstractItemView {{
                    background-color: {self.current_theme.SURFACE};
                    border: none;
                    border-radius: 6px;
                    selection-background-color: {self.current_theme.ACCENT};
                    selection-color: {self.current_theme.TEXT_PRIMARY};
                    color: {self.current_theme.TEXT_PRIMARY};
                    padding: 4px;
                    outline: none;
                }}
                QAbstractItemView::item {{
                    background-color: {self.current_theme.SURFACE};
                    color: {self.current_theme.TEXT_PRIMARY};
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 2px;
                    outline: none;
                    min-height: 32px;
                }}
                QAbstractItemView::item:selected {{
                    background-color: {self.current_theme.ACCENT};
                    color: {self.current_theme.TEXT_PRIMARY};
                }}
                QAbstractItemView::item:hover {{
                    background-color: {self.current_theme.SURFACE_HOVER};
                    color: {self.current_theme.TEXT_PRIMARY};
                }}
            """)
            
            # Style the parent container (popup window) - this provides the main border
            popup = view.parent()
            if popup and hasattr(popup, 'setStyleSheet') and callable(getattr(popup, 'setStyleSheet', None)):
                popup.setStyleSheet(f"""
                    QWidget {{
                        background-color: {self.current_theme.SURFACE};
                        border: 2px solid {self.current_theme.BORDER};
                        border-radius: 8px;
                    }}
                """)
                # Adjust popup frame size to match view
                # Check if popup has setFixedHeight method before calling it
                if hasattr(popup, 'setFixedHeight') and callable(getattr(popup, 'setFixedHeight', None)):
                    popup.setFixedHeight(total_height + 8)  # +8 for border and padding

    def setThemedStyleSheet(self, style_sheet):
        """Set stylesheet and store current theme for popup styling"""
        self.current_style = style_sheet
        self.current_theme = ThemeManager.get_current_theme()
        self.setStyleSheet(style_sheet)
