"""Configuration management for Jarvis."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseSettings, validator

from jarvis.core.logger import logger


class JarvisConfig(BaseSettings):
    """Main configuration schema."""

    app_name: str = "Jarvis"
    debug: bool = False
    log_level: str = "INFO"

    # Speech settings
    stt_provider: str = "google"  # google, azure, offline
    tts_provider: str = "google"  # google, azure, pyttsx3
    language: str = "tr-TR"  # Turkish
    speech_timeout: float = 10.0

    # NLU settings
    use_local_llm: bool = False
    llm_api_url: Optional[str] = None
    llm_model: Optional[str] = None
    intent_confidence_threshold: float = 0.7

    # OS Control
    enable_app_control: bool = True
    enable_volume_control: bool = True
    enable_system_diagnostics: bool = True
    enable_file_operations: bool = False  # Disabled by default

    # Plugins
    plugin_directory: str = "jarvis/plugins/builtin"
    auto_load_plugins: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class ConfigManager:
    """Manage Jarvis configuration from YAML and environment."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path or self._find_default_config()
        self.config: JarvisConfig = self._load_config()
        self.permissions: Dict[str, bool] = self._load_permissions()
        self.intents: Dict[str, Any] = self._load_intents()

        logger.info(f"Configuration loaded from {self.config_path}")

    def _find_default_config(self) -> str:
        """Find default configuration file."""
        config_dir = Path(__file__).parent.parent.parent / "config"
        default_config = config_dir / "default.yaml"

        if not default_config.exists():
            raise FileNotFoundError(
                f"Configuration file not found at {default_config}"
            )

        return str(default_config)

    def _load_config(self) -> JarvisConfig:
        """Load main configuration from YAML."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f) or {}
                return JarvisConfig(**yaml_config.get("config", {}))
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            return JarvisConfig()

    def _load_permissions(self) -> Dict[str, bool]:
        """Load permission policies."""
        permissions_file = (
            Path(self.config_path).parent / "permissions.yaml"
        )

        try:
            if permissions_file.exists():
                with open(permissions_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    return data.get("permissions", {})
        except Exception as e:
            logger.warning(f"Failed to load permissions: {e}")

        # Default permissions
        return {
            "app_launch": True,
            "app_kill": True,
            "volume_control": True,
            "system_diagnostics": True,
            "file_operations": False,
        }

    def _load_intents(self) -> Dict[str, Any]:
        """Load intent definitions."""
        intents_file = Path(self.config_path).parent / "intents.yaml"

        try:
            if intents_file.exists():
                with open(intents_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    return data.get("intents", {})
        except Exception as e:
            logger.warning(f"Failed to load intents: {e}")

        return {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self.config, key, default)

    def has_permission(self, action: str) -> bool:
        """Check if an action is permitted."""
        return self.permissions.get(action, False)


# Global config instance
_config_instance: Optional[ConfigManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """Get or create global config instance."""
    global _config_instance

    if _config_instance is None:
        _config_instance = ConfigManager(config_path)

    return _config_instance
