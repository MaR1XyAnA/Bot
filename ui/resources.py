"""
Resources Module
Contains utility functions for loading resources.
"""
import os
import logging
from PyQt5.QtGui import QIcon, QPixmap

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    
    Args:
        relative_path: Relative path to the resource
        
    Returns:
        str: Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    return os.path.join(base_path, relative_path)

def get_icon(name):
    """
    Get an icon by name
    
    Args:
        name: Icon name (without extension)
        
    Returns:
        QIcon: Icon object or default icon if not found
    """
    try:
        path = resource_path(f"../assets/{name}.svg")
        if os.path.exists(path):
            return QIcon(path)
        else:
            logging.warning(f"Icon not found: {name}.svg")
            return QIcon()
    except Exception as e:
        logging.error(f"Error loading icon {name}: {str(e)}")
        return QIcon()
