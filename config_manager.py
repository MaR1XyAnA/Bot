"""
Configuration Manager Module
Handles loading, saving, and accessing application configuration.
"""
import os
import json
import logging
from datetime import datetime

class ConfigManager:
    """Manages application configuration and settings"""
    
    # Default settings
    DEFAULT_SETTINGS = {
        "version": "1.0.0",
        "last_update_check": None,
        "github_repo": "MaR1XyAnA/Bot",
        "check_for_updates_on_startup": True,
        "fishing_settings": {
            "cast_interval": 30,  # seconds
            "detection_method": "color",  # color, motion, sound
            "detection_sensitivity": 50,  # 0-100
            "auto_start": False
        },
        "ui_settings": {
            "show_notifications": True,
            "minimize_to_tray": True,
            "theme": "dark"
        },
        "hotkeys": {
            "toggle_bot": "F9",
            "emergency_stop": "F10"
        }
    }
    
    def __init__(self, config_path):
        """
        Initialize the config manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.settings = self._load_config()
    
    def _load_config(self):
        """
        Load configuration from file or create with defaults if not exists
        
        Returns:
            dict: Configuration settings
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Update with any missing default settings
                updated = False
                for key, value in self.DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                        updated = True
                    elif isinstance(value, dict) and key in settings:
                        for sub_key, sub_value in value.items():
                            if sub_key not in settings[key]:
                                settings[key][sub_key] = sub_value
                                updated = True
                
                if updated:
                    self.save_settings(settings)
                    
                return settings
            else:
                # Create new config with defaults
                self.save_settings(self.DEFAULT_SETTINGS)
                return self.DEFAULT_SETTINGS.copy()
                
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            # Return defaults on error
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self, settings=None):
        """
        Save settings to configuration file
        
        Args:
            settings: Settings to save (uses current if None)
            
        Returns:
            bool: Success status
        """
        if settings is None:
            settings = self.settings
        else:
            self.settings = settings
            
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get_settings(self):
        """
        Get current settings
        
        Returns:
            dict: Current settings
        """
        return self.settings
    
    def update_setting(self, key, value):
        """
        Update a specific setting
        
        Args:
            key: Setting key (can be nested with dots, e.g. "fishing_settings.cast_interval")
            value: New value
            
        Returns:
            bool: Success status
        """
        try:
            # Handle nested keys
            keys = key.split('.')
            settings_ref = self.settings
            
            # Navigate to the right level
            for k in keys[:-1]:
                if k not in settings_ref:
                    settings_ref[k] = {}
                settings_ref = settings_ref[k]
                
            # Update the value
            settings_ref[keys[-1]] = value
            
            # Save the updated settings
            return self.save_settings()
            
        except Exception as e:
            logging.error(f"Error updating setting {key}: {str(e)}")
            return False
    
    def reset_to_defaults(self):
        """
        Reset all settings to defaults
        
        Returns:
            bool: Success status
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save_settings()
    
    def get_fishing_settings(self):
        """
        Get fishing-specific settings
        
        Returns:
            dict: Fishing settings
        """
        return self.settings.get("fishing_settings", {})
    
    def get_ui_settings(self):
        """
        Get UI-specific settings
        
        Returns:
            dict: UI settings
        """
        return self.settings.get("ui_settings", {})
