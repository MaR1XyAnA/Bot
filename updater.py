"""
Updater Module
Handles checking for and downloading updates from GitHub without using git.
"""
import os
import json
import logging
import time
import shutil
import tempfile
import zipfile
import requests
from datetime import datetime

class Updater:
    """Handles application updates from GitHub releases"""
    
    def __init__(self, config_manager, update_callback=None):
        """
        Initialize the updater
        
        Args:
            config_manager: Config manager object
            update_callback: Callback for update progress and status
        """
        self.config = config_manager
        self.update_callback = update_callback
        self.github_repo = self.config.get_settings().get("github_repo", "username/fishing-bot")
        self.current_version = self.config.get_settings().get("version", "1.0.0")
        self.last_check_time = 0
        self.update_in_progress = False
    
    def _notify_progress(self, status, progress=0, message=""):
        """Send update progress to callback if set"""
        if self.update_callback:
            self.update_callback(status, progress, message)
    
    def check_for_updates(self, force=False):
        """
        Check for updates from GitHub
        
        Args:
            force: Force check even if checked recently
            
        Returns:
            dict with update info or None if no update available
        """
        # Don't check too frequently unless forced
        current_time = time.time()
        if not force and (current_time - self.last_check_time) < 3600:  # 1 hour
            logging.info("Update check skipped (checked recently)")
            return None
            
        self.last_check_time = current_time
        
        try:
            self._notify_progress("checking", 0, "Checking for updates...")
            
            # Get latest release info from GitHub API
            api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get("tag_name", "").strip("v")
            
            # Compare versions
            if self._is_newer_version(latest_version, self.current_version):
                logging.info(f"Update available: {self.current_version} -> {latest_version}")
                
                # Find zip asset
                zip_asset = None
                for asset in release_data.get("assets", []):
                    if asset.get("name", "").endswith(".zip"):
                        zip_asset = asset
                        break
                
                if not zip_asset:
                    self._notify_progress("error", 0, "No zip file found in release")
                    return None
                    
                update_info = {
                    "current_version": self.current_version,
                    "latest_version": latest_version,
                    "release_date": release_data.get("published_at"),
                    "release_notes": release_data.get("body", ""),
                    "download_url": zip_asset.get("browser_download_url"),
                    "asset_name": zip_asset.get("name")
                }
                
                self._notify_progress("available", 100, f"Update available: {latest_version}")
                return update_info
            else:
                logging.info("No updates available")
                self._notify_progress("up-to-date", 100, "No updates available")
                return None
                
        except Exception as e:
            logging.error(f"Error checking for updates: {str(e)}")
            self._notify_progress("error", 0, f"Update check failed: {str(e)}")
            return None
    
    def download_and_install_update(self, update_info):
        """
        Download and install the update
        
        Args:
            update_info: Update information from check_for_updates
            
        Returns:
            bool: Success status
        """
        if self.update_in_progress:
            logging.warning("Update already in progress")
            return False
            
        self.update_in_progress = True
        
        try:
            download_url = update_info.get("download_url")
            if not download_url:
                logging.error("No download URL in update info")
                self._notify_progress("error", 0, "Missing download URL")
                self.update_in_progress = False
                return False
                
            # Create temp directory for download
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "update.zip")
                
                # Download the update file
                self._notify_progress("downloading", 10, "Downloading update...")
                response = requests.get(download_url, stream=True, timeout=60)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                downloaded = 0
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = int(30 * downloaded / total_size) + 10
                                self._notify_progress("downloading", progress, 
                                                    f"Downloading: {downloaded}/{total_size} bytes")
                
                # Extract the update
                self._notify_progress("extracting", 40, "Extracting update...")
                extract_dir = os.path.join(temp_dir, "extracted")
                os.makedirs(extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Prepare for installation
                self._notify_progress("installing", 60, "Installing update...")
                
                # Get the current application directory
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                # Create backup of current version
                backup_dir = os.path.join(app_dir, f"backup_{self.current_version}_{int(time.time())}")
                os.makedirs(backup_dir, exist_ok=True)
                
                # Copy current files to backup (excluding backup directory itself)
                for item in os.listdir(app_dir):
                    if item != os.path.basename(backup_dir) and item != '__pycache__':
                        s = os.path.join(app_dir, item)
                        d = os.path.join(backup_dir, item)
                        if os.path.isdir(s):
                            shutil.copytree(s, d, symlinks=False, ignore=shutil.ignore_patterns('__pycache__'))
                        else:
                            shutil.copy2(s, d)
                
                # Copy new files to app directory
                for item in os.listdir(extract_dir):
                    s = os.path.join(extract_dir, item)
                    d = os.path.join(app_dir, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        if os.path.exists(d):
                            os.remove(d)
                        shutil.copy2(s, d)
                
                # Update version in config
                settings = self.config.get_settings()
                settings['version'] = update_info.get('latest_version')
                settings['last_update'] = datetime.now().isoformat()
                self.config.save_settings(settings)
                
                self._notify_progress("complete", 100, "Update completed successfully!")
                self.update_in_progress = False
                return True
                
        except Exception as e:
            logging.error(f"Update installation failed: {str(e)}")
            self._notify_progress("error", 0, f"Update failed: {str(e)}")
            self.update_in_progress = False
            return False
    
    def _is_newer_version(self, latest, current):
        """
        Compare version strings to determine if latest is newer than current
        
        Args:
            latest: Latest version string (e.g. "1.2.3")
            current: Current version string
            
        Returns:
            bool: True if latest is newer
        """
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad with zeros if needed
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)
            while len(current_parts) < len(latest_parts):
                current_parts.append(0)
                
            # Compare each part
            for l, c in zip(latest_parts, current_parts):
                if l > c:
                    return True
                elif l < c:
                    return False
                    
            # If we get here, they're equal
            return False
            
        except Exception as e:
            logging.error(f"Version comparison error: {str(e)}")
            return False
