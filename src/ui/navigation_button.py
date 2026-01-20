from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QPushButton, QVBoxLayout, QLabel
)
from src.theme import ThemeManager
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class NavigationButton(QPushButton):
    """Custom navigation button for bottom navigation bar"""
    
    def __init__(self, text: str, svg_icon: str, parent=None):
        super().__init__(parent)
        self.text_label = text
        self.svg_icon = svg_icon
        self.is_active = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the navigation button UI"""
        self.setFixedHeight(70)
        self.setCheckable(True)
        
        # Create layout for icon and text
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)  # Increased horizontal margins for better sizing
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)  # Center the entire content
        
        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        self.icon_opacity = QGraphicsOpacityEffect(self.icon_label)
        self.icon_label.setGraphicsEffect(self.icon_opacity)
        self.icon_opacity.setOpacity(0.85)
        layout.addWidget(self.icon_label, 0, Qt.AlignCenter)  # Center the icon
        
        # Text label
        self.label = QLabel(self.text_label)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        self.label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)
        self.label_opacity = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.label_opacity)
        self.label_opacity.setOpacity(0.85)
        layout.addWidget(self.label, 0, Qt.AlignCenter)  # Center the text
        
        # Set minimum width based on text
        text_width = self.label.fontMetrics().horizontalAdvance(self.text_label)
        self.setFixedWidth(max(text_width + 32, 80))  # Minimum 80px or text width + padding

        self.icon_opacity_anim = QPropertyAnimation(self.icon_opacity, b"opacity", self)
        self.icon_opacity_anim.setDuration(180)
        self.icon_opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.label_opacity_anim = QPropertyAnimation(self.label_opacity, b"opacity", self)
        self.label_opacity_anim.setDuration(180)
        self.label_opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.update_style()
    
    def set_active(self, active: bool):
        """Set the active state of the button"""
        self.is_active = active
        self.setChecked(active)
        self.update_style()
    
    def update_style(self):
        """Update button styling based on active state"""
        current_theme = ThemeManager.get_current_theme()
        
        if self.is_active:
            icon_color = current_theme.TEXT_PRIMARY
            text_color = current_theme.TEXT_PRIMARY
            bg_color = current_theme.ACCENT
        else:
            icon_color = current_theme.TEXT_SECONDARY
            text_color = current_theme.TEXT_SECONDARY
            bg_color = "transparent"
        
        # Create colored icon
        icon = current_theme.create_svg_icon(self.svg_icon, icon_color, 24)
        pixmap = icon.pixmap(24, 24)
        self.icon_label.setPixmap(pixmap)

        target_opacity = 1.0 if self.is_active else 0.8
        self._animate_opacity(target_opacity)
        
        # Update button style
        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    border: none;
                    border-radius: 12px;
                    color: {text_color};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    border: none;
                    border-radius: 12px;
                    color: {text_color};
                }}
                QPushButton:hover {{
                    background-color: {current_theme.SURFACE_HOVER};
                    color: {current_theme.TEXT_PRIMARY};
                }}
            """)
    
    def enterEvent(self, event):
        """Handle mouse enter for icon color change"""
        if not self.is_active:
            # Update icon color on hover
            current_theme = ThemeManager.get_current_theme()
            icon = current_theme.create_svg_icon(self.svg_icon, current_theme.TEXT_PRIMARY, 24)
            pixmap = icon.pixmap(24, 24)
            self.icon_label.setPixmap(pixmap)
            self._animate_opacity(1.0)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave for icon color change"""
        if not self.is_active:
            # Restore original icon color
            current_theme = ThemeManager.get_current_theme()
            icon = current_theme.create_svg_icon(self.svg_icon, current_theme.TEXT_SECONDARY, 24)
            pixmap = icon.pixmap(24, 24)
            self.icon_label.setPixmap(pixmap)
            self._animate_opacity(0.8)
        super().leaveEvent(event)

    def _animate_opacity(self, value: float):
        self.icon_opacity_anim.stop()
        self.label_opacity_anim.stop()
        self.icon_opacity_anim.setStartValue(self.icon_opacity.opacity())
        self.label_opacity_anim.setStartValue(self.label_opacity.opacity())
        self.icon_opacity_anim.setEndValue(value)
        self.label_opacity_anim.setEndValue(value)
        self.icon_opacity_anim.start()
        self.label_opacity_anim.start()
