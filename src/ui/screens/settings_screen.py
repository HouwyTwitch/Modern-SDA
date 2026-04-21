from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.theme import ThemeManager, ThemedComboBox
from src.settings import SettingsManager


APP_VERSION = "1.1.0"


class SettingsScreen(QWidget):
    """Screen for application settings.

    Reorganised to mirror the Android app's sectioned layout
    (Appearance / Auth Code / Confirmations / About).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.theme_combo = None
        self.auto_refresh_checkbox = None
        self.refresh_interval_spinbox = None
        self.copy_on_click_checkbox = None
        self.auto_refresh_confirmations_checkbox = None
        self.confirmations_interval_spinbox = None
        self.auto_confirm_trades_checkbox = None
        self.auto_confirm_market_checkbox = None
        self._section_frames = []
        self._section_title_labels = []
        self._body_labels = []
        self.setup_ui()

    # ── Build UI ────────────────────────────────────────────────────────

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(16)

        scroll_layout.addWidget(self._build_appearance_section())
        scroll_layout.addWidget(self._build_auth_code_section())
        scroll_layout.addWidget(self._build_confirmations_section())
        scroll_layout.addWidget(self._build_about_section())
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.update_combo_style()
        self.update_control_styles()

    def _build_section_frame(self, title: str) -> tuple:
        """Return (frame, body_layout) — body_layout is where the section
        contents go. Frame/title are stored for theme updates."""
        frame = QFrame()
        frame.setObjectName("SettingsSection")
        self._section_frames.append(frame)

        wrapper = QVBoxLayout(frame)
        wrapper.setContentsMargins(20, 16, 20, 16)
        wrapper.setSpacing(12)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        wrapper.addWidget(title_label)
        self._section_title_labels.append(title_label)

        body = QVBoxLayout()
        body.setSpacing(10)
        wrapper.addLayout(body)

        return frame, body

    def _add_row(self, body_layout, left_widget, right_widget=None):
        row = QHBoxLayout()
        row.addWidget(left_widget)
        row.addStretch()
        if right_widget is not None:
            row.addWidget(right_widget)
        body_layout.addLayout(row)

    # ── Appearance ──────────────────────────────────────────────────────

    def _build_appearance_section(self) -> QFrame:
        frame, body = self._build_section_frame("Appearance")

        theme_label = QLabel("Theme")
        theme_label.setFont(QFont("Segoe UI", 13))
        self._body_labels.append(theme_label)

        self.theme_combo = ThemedComboBox()
        self.theme_combo.addItems(ThemeManager.get_theme_names())
        self.theme_combo.setCurrentText(ThemeManager.current_theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)

        self._add_row(body, theme_label, self.theme_combo)

        return frame

    # ── Auth Code ───────────────────────────────────────────────────────

    def _build_auth_code_section(self) -> QFrame:
        frame, body = self._build_section_frame("Auth Code")

        self.auto_refresh_checkbox = QCheckBox("Auto-refresh displayed code")
        self.auto_refresh_checkbox.setChecked(
            SettingsManager.get_setting("auto_refresh_enabled")
        )
        self.auto_refresh_checkbox.stateChanged.connect(self.on_auto_refresh_changed)
        body.addWidget(self.auto_refresh_checkbox)

        interval_label = QLabel("Refresh interval")
        interval_label.setFont(QFont("Segoe UI", 12))
        self._body_labels.append(interval_label)

        self.refresh_interval_spinbox = QSpinBox()
        self.refresh_interval_spinbox.setRange(1, 60)
        self.refresh_interval_spinbox.setValue(
            SettingsManager.get_setting("auto_refresh_interval_seconds")
        )
        self.refresh_interval_spinbox.setSuffix(" sec")
        self.refresh_interval_spinbox.valueChanged.connect(self.on_refresh_interval_changed)
        self.refresh_interval_spinbox.setEnabled(
            SettingsManager.get_setting("auto_refresh_enabled")
        )

        self._add_row(body, interval_label, self.refresh_interval_spinbox)

        self.copy_on_click_checkbox = QCheckBox("Click code to copy to clipboard")
        self.copy_on_click_checkbox.setChecked(
            SettingsManager.get_setting("copy_code_on_click")
        )
        self.copy_on_click_checkbox.stateChanged.connect(self.on_copy_on_click_changed)
        body.addWidget(self.copy_on_click_checkbox)

        return frame

    # ── Confirmations ───────────────────────────────────────────────────

    def _build_confirmations_section(self) -> QFrame:
        frame, body = self._build_section_frame("Confirmations")

        self.auto_refresh_confirmations_checkbox = QCheckBox(
            "Auto-refresh pending confirmations in background"
        )
        self.auto_refresh_confirmations_checkbox.setChecked(
            SettingsManager.get_setting("auto_refresh_confirmations_enabled")
        )
        self.auto_refresh_confirmations_checkbox.stateChanged.connect(
            self.on_auto_refresh_confirmations_changed
        )
        body.addWidget(self.auto_refresh_confirmations_checkbox)

        sync_label = QLabel("Background refresh interval")
        sync_label.setFont(QFont("Segoe UI", 12))
        self._body_labels.append(sync_label)

        self.confirmations_interval_spinbox = QSpinBox()
        self.confirmations_interval_spinbox.setRange(15, 600)
        self.confirmations_interval_spinbox.setSingleStep(15)
        self.confirmations_interval_spinbox.setValue(
            SettingsManager.get_setting("auto_refresh_confirmations_interval_seconds")
        )
        self.confirmations_interval_spinbox.setSuffix(" sec")
        self.confirmations_interval_spinbox.valueChanged.connect(
            self.on_confirmations_interval_changed
        )
        self.confirmations_interval_spinbox.setEnabled(
            SettingsManager.get_setting("auto_refresh_confirmations_enabled")
        )
        self._add_row(body, sync_label, self.confirmations_interval_spinbox)

        warn_label = QLabel("Auto-accept (use with caution — confirmations run automatically)")
        warn_label.setFont(QFont("Segoe UI", 10))
        warn_label.setWordWrap(True)
        self._body_labels.append(warn_label)
        body.addWidget(warn_label)

        self.auto_confirm_trades_checkbox = QCheckBox("Auto-accept trade offers")
        self.auto_confirm_trades_checkbox.setChecked(
            SettingsManager.get_setting("auto_confirm_trades")
        )
        self.auto_confirm_trades_checkbox.stateChanged.connect(
            self.on_auto_confirm_trades_changed
        )
        body.addWidget(self.auto_confirm_trades_checkbox)

        self.auto_confirm_market_checkbox = QCheckBox("Auto-accept market listings")
        self.auto_confirm_market_checkbox.setChecked(
            SettingsManager.get_setting("auto_confirm_market")
        )
        self.auto_confirm_market_checkbox.stateChanged.connect(
            self.on_auto_confirm_market_changed
        )
        body.addWidget(self.auto_confirm_market_checkbox)

        return frame

    # ── About ───────────────────────────────────────────────────────────

    def _build_about_section(self) -> QFrame:
        frame, body = self._build_section_frame("About")

        version_label = QLabel(f"Modern SDA {APP_VERSION}")
        version_label.setFont(QFont("Segoe UI", 13, QFont.Medium))
        self._body_labels.append(version_label)
        body.addWidget(version_label)

        desc_label = QLabel(
            "A modern Steam Desktop Authenticator.\n"
            "Feature parity ported from the Android companion app."
        )
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setWordWrap(True)
        self._body_labels.append(desc_label)
        body.addWidget(desc_label)

        return frame

    # ── Theming ─────────────────────────────────────────────────────────

    def update_combo_style(self):
        """Update combo box styling and all dynamic elements with current theme."""
        current_theme = ThemeManager.get_current_theme()

        # Section frames
        for frame in self._section_frames:
            frame.setStyleSheet(f"""
                QFrame#SettingsSection {{
                    background-color: {current_theme.SURFACE_ELEVATED};
                    border-radius: 8px;
                    border: 1px solid {current_theme.BORDER};
                }}
            """)
        for label in self._section_title_labels:
            label.setStyleSheet(f"color: {current_theme.TEXT_PRIMARY}; background: transparent; border: none;")
        for label in self._body_labels:
            label.setStyleSheet(f"color: {current_theme.TEXT_SECONDARY}; background: transparent; border: none;")

        if self.theme_combo:
            style = f"""
                QComboBox {{
                    background-color: {current_theme.SURFACE};
                    border: 2px solid {current_theme.BORDER};
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 14px;
                    color: {current_theme.TEXT_PRIMARY};
                    min-width: 120px;
                }}
                QComboBox:focus {{
                    border-color: {current_theme.BORDER_FOCUS};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                    background-color: transparent;
                }}
                QComboBox::down-arrow {{
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid {current_theme.TEXT_SECONDARY};
                    margin-right: 8px;
                }}
                QAbstractItemView {{
                    background-color: {current_theme.SURFACE};
                    border: 2px solid {current_theme.BORDER};
                    border-radius: 4px;
                    selection-background-color: {current_theme.ACCENT};
                    selection-color: {current_theme.TEXT_PRIMARY};
                    color: {current_theme.TEXT_PRIMARY};
                    padding: 4px;
                    outline: none;
                }}
                QAbstractItemView::item {{
                    background-color: {current_theme.SURFACE};
                    color: {current_theme.TEXT_PRIMARY};
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 2px;
                    outline: none;
                }}
                QAbstractItemView::item:selected {{
                    background-color: {current_theme.ACCENT};
                    color: {current_theme.TEXT_PRIMARY};
                }}
                QAbstractItemView::item:hover {{
                    background-color: {current_theme.SURFACE_HOVER};
                    color: {current_theme.TEXT_PRIMARY};
                }}
            """
            if hasattr(self.theme_combo, 'setThemedStyleSheet'):
                self.theme_combo.setThemedStyleSheet(style)
            else:
                self.theme_combo.setStyleSheet(style)
        self.update_control_styles()

    def update_control_styles(self):
        current_theme = ThemeManager.get_current_theme()
        checkbox_style = f"""
            QCheckBox {{
                color: {current_theme.TEXT_PRIMARY};
                font-size: 13px;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {current_theme.BORDER};
                background-color: {current_theme.SURFACE};
            }}
            QCheckBox::indicator:checked {{
                background-color: {current_theme.ACCENT};
                border-color: {current_theme.BORDER_FOCUS};
            }}
            QCheckBox:disabled {{
                color: {current_theme.TEXT_TERTIARY};
            }}
        """
        spinbox_style = f"""
            QSpinBox {{
                background-color: {current_theme.SURFACE};
                border: 2px solid {current_theme.BORDER};
                border-radius: 4px;
                padding: 6px 10px;
                color: {current_theme.TEXT_PRIMARY};
                min-width: 90px;
            }}
            QSpinBox:focus {{
                border-color: {current_theme.BORDER_FOCUS};
            }}
            QSpinBox:disabled {{
                color: {current_theme.TEXT_TERTIARY};
            }}
        """
        for cb in (
            self.auto_refresh_checkbox,
            self.copy_on_click_checkbox,
            self.auto_refresh_confirmations_checkbox,
            self.auto_confirm_trades_checkbox,
            self.auto_confirm_market_checkbox,
        ):
            if cb:
                cb.setStyleSheet(checkbox_style)
        for sb in (self.refresh_interval_spinbox, self.confirmations_interval_spinbox):
            if sb:
                sb.setStyleSheet(spinbox_style)

    # ── Handlers ────────────────────────────────────────────────────────

    def on_theme_changed(self, theme_name: str):
        if ThemeManager.set_theme(theme_name):
            SettingsManager.set_setting("theme", theme_name)
            if self.parent_window:
                self.parent_window.apply_theme()

    def on_auto_refresh_changed(self, state: int):
        enabled = state == Qt.Checked
        SettingsManager.set_setting("auto_refresh_enabled", enabled)
        if self.refresh_interval_spinbox:
            self.refresh_interval_spinbox.setEnabled(enabled)
        self._notify_parent_settings_changed()

    def on_refresh_interval_changed(self, value: int):
        SettingsManager.set_setting("auto_refresh_interval_seconds", value)
        self._notify_parent_settings_changed()

    def on_copy_on_click_changed(self, state: int):
        SettingsManager.set_setting("copy_code_on_click", state == Qt.Checked)
        self._notify_parent_settings_changed()

    def on_auto_refresh_confirmations_changed(self, state: int):
        enabled = state == Qt.Checked
        SettingsManager.set_setting("auto_refresh_confirmations_enabled", enabled)
        if self.confirmations_interval_spinbox:
            self.confirmations_interval_spinbox.setEnabled(enabled)
        self._notify_parent_settings_changed()

    def on_confirmations_interval_changed(self, value: int):
        SettingsManager.set_setting("auto_refresh_confirmations_interval_seconds", value)
        self._notify_parent_settings_changed()

    def on_auto_confirm_trades_changed(self, state: int):
        SettingsManager.set_setting("auto_confirm_trades", state == Qt.Checked)
        self._notify_parent_settings_changed()

    def on_auto_confirm_market_changed(self, state: int):
        SettingsManager.set_setting("auto_confirm_market", state == Qt.Checked)
        self._notify_parent_settings_changed()

    def _notify_parent_settings_changed(self):
        if self.parent_window and hasattr(self.parent_window, "apply_settings"):
            self.parent_window.apply_settings()
