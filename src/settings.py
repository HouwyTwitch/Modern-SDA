import json
import os
from typing import Any, Dict


class SettingsManager:
    """Manages persistent app settings."""

    _settings: Dict[str, Any] = {}
    _loaded = False
    _settings_path = os.path.join(os.path.expanduser("~"), ".sda_settings.json")

    DEFAULTS: Dict[str, Any] = {
        "theme": "Noctua",
        "auto_refresh_enabled": True,
        "auto_refresh_interval_seconds": 1,
        "copy_code_on_click": True,
    }

    @classmethod
    def load_settings(cls) -> Dict[str, Any]:
        if cls._loaded:
            return cls._settings

        cls._settings = dict(cls.DEFAULTS)
        try:
            if os.path.exists(cls._settings_path):
                with open(cls._settings_path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                    if isinstance(data, dict):
                        cls._settings.update(data)
        except (OSError, json.JSONDecodeError):
            cls._settings = dict(cls.DEFAULTS)

        cls._loaded = True
        cls._normalize_settings()
        return cls._settings

    @classmethod
    def _normalize_settings(cls) -> None:
        interval = cls._settings.get("auto_refresh_interval_seconds")
        if not isinstance(interval, int):
            interval = cls.DEFAULTS["auto_refresh_interval_seconds"]
        interval = max(1, min(60, interval))
        cls._settings["auto_refresh_interval_seconds"] = interval

        for key in ("auto_refresh_enabled", "copy_code_on_click"):
            if not isinstance(cls._settings.get(key), bool):
                cls._settings[key] = cls.DEFAULTS[key]

        theme = cls._settings.get("theme")
        if not isinstance(theme, str):
            cls._settings["theme"] = cls.DEFAULTS["theme"]

    @classmethod
    def save_settings(cls) -> None:
        try:
            with open(cls._settings_path, "w", encoding="utf-8") as handle:
                json.dump(cls._settings, handle, indent=2, sort_keys=True)
        except OSError:
            pass

    @classmethod
    def get_setting(cls, key: str) -> Any:
        cls.load_settings()
        return cls._settings.get(key, cls.DEFAULTS.get(key))

    @classmethod
    def set_setting(cls, key: str, value: Any) -> None:
        cls.load_settings()
        cls._settings[key] = value
        cls._normalize_settings()
        cls.save_settings()
