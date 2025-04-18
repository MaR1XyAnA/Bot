"""
Logger Module
Sets up logging for the application.
"""
import os
import logging
from datetime import datetime

def setup_logger():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.expanduser("~/.fishing_bot/logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"fishing_bot_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Logging initialized")
    return log_file
