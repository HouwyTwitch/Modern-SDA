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


class NoctuaTheme:
    """Noctua-inspired color palette"""
    
    # Colors
    BACKGROUND = "#1A1611"      # Very dark brown
    SURFACE = "#251F18"        # Dark brown surface
    SURFACE_ELEVATED = "#332A21"  # Elevated surface
    SURFACE_HOVER = "#3D332A"   # Hover surface
    ACCENT = "#8B7355"         # Noctua brown
    ACCENT_HOVER = "#A08968"   # Lighter brown for hover
    ACCENT_PRESSED = "#786349" # Pressed state
    TEXT_PRIMARY = "#F0EBE1"   # Light beige
    TEXT_SECONDARY = "#C4B9A7" # Muted beige
    TEXT_TERTIARY = "#9A8F7E" # Even more muted
    BORDER = "#453A30"        # Border color
    BORDER_FOCUS = "#6B5D4F"  # Focused border
    SUCCESS = "#6B8B47"       # Success green with brown tint
    ERROR = "#B85C57"         # Error red with brown tint
    SHADOW = "#0F0D0A"        # Shadow color
    
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
        theme = ThemeManager.get_current_theme() if 'ThemeManager' in globals() else NoctuaTheme
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
            border: 2px solid {theme.BORDER};
            border-radius: 10px;
            padding: 14px 18px;
            font-size: 14px;
            color: {theme.TEXT_PRIMARY};
            selection-background-color: {theme.ACCENT};
            selection-color: {theme.TEXT_PRIMARY};
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
            border-radius: 10px;
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
            border-radius: 12px;
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
            border-radius: 4px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme.ACCENT};
            border-radius: 4px;
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
        """


class LightTheme:
    """Light theme color palette"""
    
    # Colors
    BACKGROUND = "#FFFFFF"        # White background
    SURFACE = "#F5F5F5"          # Light gray surface
    SURFACE_ELEVATED = "#EEEEEE"  # Elevated surface
    SURFACE_HOVER = "#E0E0E0"     # Hover surface
    ACCENT = "#2196F3"           # Blue accent
    ACCENT_HOVER = "#1976D2"     # Darker blue for hover
    ACCENT_PRESSED = "#0D47A1"   # Pressed state
    TEXT_PRIMARY = "#212121"     # Dark gray
    TEXT_SECONDARY = "#757575"   # Medium gray
    TEXT_TERTIARY = "#BDBDBD"    # Light gray
    BORDER = "#E0E0E0"          # Border color
    BORDER_FOCUS = "#2196F3"    # Focused border
    SUCCESS = "#4CAF50"         # Green
    ERROR = "#F44336"           # Red
    SHADOW = "#000000"          # Shadow color
    
    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24):
        return NoctuaTheme.create_svg_icon(svg_content, color, size)
    
    @staticmethod
    def get_accounts_svg():
        return NoctuaTheme.get_accounts_svg()
    
    @staticmethod
    def get_confirmations_svg():
        return NoctuaTheme.get_confirmations_svg()
    
    @staticmethod
    def get_settings_svg():
        return NoctuaTheme.get_settings_svg()
    
    @staticmethod
    def get_stylesheet():
        return NoctuaTheme.get_stylesheet().replace(NoctuaTheme.BACKGROUND, LightTheme.BACKGROUND)\
            .replace(NoctuaTheme.SURFACE, LightTheme.SURFACE)\
            .replace(NoctuaTheme.SURFACE_ELEVATED, LightTheme.SURFACE_ELEVATED)\
            .replace(NoctuaTheme.SURFACE_HOVER, LightTheme.SURFACE_HOVER)\
            .replace(NoctuaTheme.ACCENT, LightTheme.ACCENT)\
            .replace(NoctuaTheme.ACCENT_HOVER, LightTheme.ACCENT_HOVER)\
            .replace(NoctuaTheme.ACCENT_PRESSED, LightTheme.ACCENT_PRESSED)\
            .replace(NoctuaTheme.TEXT_PRIMARY, LightTheme.TEXT_PRIMARY)\
            .replace(NoctuaTheme.TEXT_SECONDARY, LightTheme.TEXT_SECONDARY)\
            .replace(NoctuaTheme.TEXT_TERTIARY, LightTheme.TEXT_TERTIARY)\
            .replace(NoctuaTheme.BORDER, LightTheme.BORDER)\
            .replace(NoctuaTheme.BORDER_FOCUS, LightTheme.BORDER_FOCUS)\
            .replace(NoctuaTheme.SUCCESS, LightTheme.SUCCESS)\
            .replace(NoctuaTheme.ERROR, LightTheme.ERROR)


class DarkTheme:
    """Dark theme color palette"""
    
    # Colors
    BACKGROUND = "#121212"        # Very dark gray
    SURFACE = "#1E1E1E"          # Dark gray surface
    SURFACE_ELEVATED = "#2C2C2C"  # Elevated surface
    SURFACE_HOVER = "#383838"     # Hover surface
    ACCENT = "#BB86FC"           # Purple accent
    ACCENT_HOVER = "#985EFF"     # Lighter purple for hover
    ACCENT_PRESSED = "#7C4DFF"   # Pressed state
    TEXT_PRIMARY = "#FFFFFF"     # White
    TEXT_SECONDARY = "#B3B3B3"   # Light gray
    TEXT_TERTIARY = "#666666"    # Medium gray
    BORDER = "#333333"          # Border color
    BORDER_FOCUS = "#BB86FC"    # Focused border
    SUCCESS = "#4CAF50"         # Green
    ERROR = "#CF6679"           # Red
    SHADOW = "#000000"          # Shadow color
    
    @staticmethod
    def create_svg_icon(svg_content: str, color: str, size: int = 24):
        return NoctuaTheme.create_svg_icon(svg_content, color, size)
    
    @staticmethod
    def get_accounts_svg():
        return NoctuaTheme.get_accounts_svg()
    
    @staticmethod
    def get_confirmations_svg():
        return NoctuaTheme.get_confirmations_svg()
    
    @staticmethod
    def get_settings_svg():
        return NoctuaTheme.get_settings_svg()
    
    @staticmethod
    def get_stylesheet():
        return NoctuaTheme.get_stylesheet().replace(NoctuaTheme.BACKGROUND, DarkTheme.BACKGROUND)\
            .replace(NoctuaTheme.SURFACE, DarkTheme.SURFACE)\
            .replace(NoctuaTheme.SURFACE_ELEVATED, DarkTheme.SURFACE_ELEVATED)\
            .replace(NoctuaTheme.SURFACE_HOVER, DarkTheme.SURFACE_HOVER)\
            .replace(NoctuaTheme.ACCENT, DarkTheme.ACCENT)\
            .replace(NoctuaTheme.ACCENT_HOVER, DarkTheme.ACCENT_HOVER)\
            .replace(NoctuaTheme.ACCENT_PRESSED, DarkTheme.ACCENT_PRESSED)\
            .replace(NoctuaTheme.TEXT_PRIMARY, DarkTheme.TEXT_PRIMARY)\
            .replace(NoctuaTheme.TEXT_SECONDARY, DarkTheme.TEXT_SECONDARY)\
            .replace(NoctuaTheme.TEXT_TERTIARY, DarkTheme.TEXT_TERTIARY)\
            .replace(NoctuaTheme.BORDER, DarkTheme.BORDER)\
            .replace(NoctuaTheme.BORDER_FOCUS, DarkTheme.BORDER_FOCUS)\
            .replace(NoctuaTheme.SUCCESS, DarkTheme.SUCCESS)\
            .replace(NoctuaTheme.ERROR, DarkTheme.ERROR)


# Global theme manager
class ThemeManager:
    """Manages application themes"""
    
    themes = {
        "Noctua": NoctuaTheme,
        "Light": LightTheme,
        "Dark": DarkTheme
    }
    
    current_theme = "Noctua"
    
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
