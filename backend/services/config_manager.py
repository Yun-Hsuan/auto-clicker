"""
Configuration Manager for Orange Clicker

Handles loading and saving of the application's configuration to a JSON file.
Automatically creates the config directory on first run.
"""

import json
import os
from pathlib import Path
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages reading and writing of the application's configuration file.
    """

    def __init__(self):
        """
        Initialize the configuration manager.

        Important: When a ConfigManager instance is created for the first time,
        the config directory is automatically created if it does not exist.
        """
        self.config_dir = self._get_config_directory()
        # Automatically create directory on initialization if it doesn't exist
        self._ensure_config_directory()
        self.config_file = self.config_dir / "config.json"

    def _get_config_directory(self) -> Path:
        """
        Get the configuration directory path.

        Returns:
            Path: The path to the configuration directory.
              - On Windows: %APPDATA%\OrangeClicker
              - On other platforms: './config' under the current directory (fallback)
        """
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA')
            if appdata:
                return Path(appdata) / "OrangeClicker"
        # Fallback: use 'config' folder in the current working directory
        return Path.cwd() / "config"

    def _ensure_config_directory(self):
        """
        Ensure that the configuration directory exists.

        If the directory does not exist, create it (including all parents).

        Uses mkdir(parents=True, exist_ok=True) to:
        - parents=True: Create all parent directories if they do not exist
        - exist_ok=True: Do not raise an error if the directory exists
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Config directory ensured: {self.config_dir}")
        except OSError as e:
            logger.error(f"Failed to create config directory: {e}")
            raise

    def load_config(self) -> Dict:
        """
        Load the configuration file.

        Returns:
            Dict: The configuration dictionary. If the file does not exist or is corrupted, returns the default config.
        """
        if not self.config_file.exists():
            logger.info("Config file not found, using default config")
            return self._get_default_config()
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info("Config file loaded successfully")
                # Validate and migrate config version
                return self._migrate_config(config)
        except json.JSONDecodeError as e:
            logger.error(f"Config file is corrupted (JSON error): {e}")
            # Backup the corrupted file
            self._backup_corrupted_config()
            return self._get_default_config()
        except IOError as e:
            logger.error(f"Failed to read config file: {e}")
            return self._get_default_config()

    def save_config(self, config: Dict):
        """
        Save the configuration file using atomic write.

        First creates a backup if the file exists, writes to a temporary file, then replaces the original.
        If saving fails, attempts to restore the backup.

        Args:
            config: The configuration dictionary.
        """
        try:
            backup_file = None
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix('.json.bak')
                try:
                    self.config_file.rename(backup_file)
                except OSError as e:
                    logger.warning(f"Failed to create backup: {e}")

            temp_file = self.config_file.with_suffix('.json.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # Atomically replace the original with the temp file
            temp_file.replace(self.config_file)

            # Delete backup if saving succeeded
            if backup_file and backup_file.exists():
                try:
                    backup_file.unlink()
                except OSError:
                    pass  # Ignore backup deletion failures

            logger.info("Config file saved successfully")
        except IOError as e:
            logger.error(f"Failed to save config file: {e}")
            # Restore the backup if saving failed
            if backup_file and backup_file.exists():
                try:
                    backup_file.replace(self.config_file)
                    logger.info("Restored backup config file")
                except OSError:
                    pass
            raise

    def _get_default_config(self) -> Dict:
        """
        Get the default configuration.

        Returns:
            Dict: The default configuration dictionary.
        """
        return {
            "version": "1.0.0",
            "app_settings": {
                "language": "en",
                "theme": "light",
                "window_geometry": {
                    "x": 100,
                    "y": 100,
                    "width": 800,
                    "height": 600
                }
            },
            "profiles": []
        }

    def _migrate_config(self, config: Dict) -> Dict:
        """
        Migrate old configuration versions to the latest version.

        Args:
            config: The configuration dictionary.

        Returns:
            Dict: The migrated configuration dictionary.
        """
        version = config.get("version", "0.0.0")
        if version != "1.0.0":
            logger.info(f"Migrating config from version {version} to 1.0.0")
            # Future migration logic can be implemented here
            config["version"] = "1.0.0"
        return config

    def _backup_corrupted_config(self):
        """
        Backup a corrupted configuration file.

        Renames the corrupted config file with a .corrupted suffix and a timestamp.
        """
        if self.config_file.exists():
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                corrupted_file = self.config_file.parent / f"config_{timestamp}.json.corrupted"
                self.config_file.rename(corrupted_file)
                logger.info(f"Backed up corrupted config to: {corrupted_file}")
            except OSError as e:
                logger.error(f"Failed to backup corrupted config: {e}")

    def get_config_path(self) -> Path:
        """
        Get the path to the configuration file (for debugging or display).

        Returns:
            Path: The configuration file path.
        """
        return self.config_file

    def get_config_directory(self) -> Path:
        """
        Get the configuration directory path (for debugging or display).

        Returns:
            Path: The configuration directory path.
        """
        return self.config_dir

