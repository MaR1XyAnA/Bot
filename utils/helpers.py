"""
Helpers Module
Utility functions for the application.
"""
import os
import json
import logging
import platform
import subprocess
from datetime import datetime, timedelta

def format_time(seconds):
    """
    Format seconds into human readable time
    
    Args:
        seconds: Number of seconds
        
    Returns:
        str: Formatted time string (HH:MM:SS)
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_app_version(config_manager=None):
    """
    Get the application version
    
    Args:
        config_manager: Optional config manager instance
        
    Returns:
        str: Application version
    """
    if config_manager:
        return config_manager.get_settings().get("version", "1.0.0")
    return "1.0.0"  # Default fallback version

def format_date(iso_date_string):
    """
    Format ISO date string to human readable format
    
    Args:
        iso_date_string: ISO format date string
        
    Returns:
        str: Formatted date string
    """
    try:
        date_obj = datetime.fromisoformat(iso_date_string.replace('Z', '+00:00'))
        return date_obj.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        logging.warning(f"Date format error: {str(e)}")
        return iso_date_string

def restart_application():
    """
    Restart the application
    
    Returns:
        bool: True if restart was initiated
    """
    try:
        # Get the current executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_path = sys.executable
        else:
            # Running as script
            app_path = os.path.abspath(__file__)
            app_path = os.path.join(os.path.dirname(os.path.dirname(app_path)), "main.py")
        
        # Use different restart method based on platform
        if platform.system() == "Windows":
            # Use pythonw.exe to avoid console window
            os.startfile(app_path)
        else:
            # For Unix-like systems
            subprocess.Popen([sys.executable, app_path])
            
        return True
    except Exception as e:
        logging.error(f"Failed to restart application: {str(e)}")
        return False
