"""
Bot Interface Module
Provides an interface between the UI and the fishing bot logic.
"""
import os
import logging
import threading
import time
from datetime import datetime
from fishing_bot import FishingBot

class BotInterface:
    """Interface to control the fishing bot from the UI"""
    
    def __init__(self, config_manager, status_callback=None, log_callback=None):
        """
        Initialize the bot interface
        
        Args:
            config_manager: Config manager object
            status_callback: Callback for status updates
            log_callback: Callback for log updates
        """
        self.config_manager = config_manager
        self.status_callback = status_callback
        self.log_callback = log_callback
        self.fishing_bot = FishingBot(config_manager)
        self.bot_thread = None
        self.running = False
        self.paused = False
        
    def log(self, message):
        """Log a message and pass it to the UI if callback is set"""
        logging.info(message)
        if self.log_callback:
            self.log_callback(message)
    
    def update_status(self, status):
        """Update the status and notify the UI"""
        if self.status_callback:
            self.status_callback(status)
    
    def start_bot(self):
        """Start the fishing bot in a separate thread"""
        if self.running:
            self.log("Bot is already running")
            return False
        
        self.running = True
        self.paused = False
        self.bot_thread = threading.Thread(target=self._bot_thread)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        self.log("Bot started")
        self.update_status("running")
        return True
    
    def stop_bot(self):
        """Stop the fishing bot"""
        if not self.running:
            self.log("Bot is not running")
            return False
        
        self.running = False
        if self.bot_thread:
            self.log("Stopping bot...")
            self.bot_thread.join(timeout=5.0)
            self.bot_thread = None
        
        self.log("Bot stopped")
        self.update_status("stopped")
        return True
    
    def pause_bot(self):
        """Pause the fishing bot"""
        if not self.running:
            self.log("Bot is not running")
            return False
            
        if self.paused:
            self.log("Bot is already paused")
            return False
            
        self.paused = True
        self.log("Bot paused")
        self.update_status("paused")
        return True
    
    def resume_bot(self):
        """Resume the fishing bot"""
        if not self.running:
            self.log("Bot is not running")
            return False
            
        if not self.paused:
            self.log("Bot is not paused")
            return False
            
        self.paused = False
        self.log("Bot resumed")
        self.update_status("running")
        return True
    
    def _bot_thread(self):
        """Main bot thread function"""
        self.log("Bot thread started")
        
        try:
            while self.running:
                if not self.paused:
                    # Execute fishing bot logic
                    self.fishing_bot.execute_cycle()
                time.sleep(0.1)  # Small delay to prevent CPU hogging
        except Exception as e:
            self.log(f"Error in bot thread: {str(e)}")
            self.running = False
            self.update_status("error")
        
        self.log("Bot thread finished")
