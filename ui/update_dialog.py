"""
Update Dialog Module
Dialog for displaying and installing updates.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTextEdit, QProgressBar,
                           QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
from datetime import datetime

class UpdaterThread(QThread):
    """Thread for downloading and installing updates"""
    
    progress_update = pyqtSignal(str, int, str)
    completed = pyqtSignal(bool, str)
    
    def __init__(self, updater, update_info):
        """
        Initialize the updater thread
        
        Args:
            updater: Updater instance
            update_info: Update information
        """
        super().__init__()
        self.updater = updater
        self.update_info = update_info
    
    def run(self):
        """Run the update process"""
        try:
            # Call updater with our own callback
            def progress_callback(status, progress, message):
                self.progress_update.emit(status, progress, message)
            
            # Store original callback
            original_callback = self.updater.update_callback
            self.updater.update_callback = progress_callback
            
            # Perform update
            success = self.updater.download_and_install_update(self.update_info)
            
            # Restore original callback
            self.updater.update_callback = original_callback
            
            # Emit completion signal
            if success:
                self.completed.emit(True, "Update completed successfully!")
            else:
                self.completed.emit(False, "Update failed. See log for details.")
                
        except Exception as e:
            self.completed.emit(False, f"Update error: {str(e)}")

class UpdateDialog(QDialog):
    """Dialog for updating the application"""
    
    def __init__(self, parent, update_info, updater):
        """
        Initialize the update dialog
        
        Args:
            parent: Parent widget
            update_info: Update information
            updater: Updater instance
        """
        super().__init__(parent)
        self.update_info = update_info
        self.updater = updater
        
        self.setWindowTitle("Software Update Available")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Update information
        heading_label = QLabel(f"A new version of Fishing Bot is available")
        heading_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(heading_label)
        
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel(f"Current version: {self.update_info.get('current_version', '?')}"))
        version_layout.addWidget(QLabel(f"New version: {self.update_info.get('latest_version', '?')}"))
        main_layout.addLayout(version_layout)
        
        # Format release date
        release_date_str = self.update_info.get('release_date', '')
        try:
            date_obj = datetime.fromisoformat(release_date_str.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_date = release_date_str
            
        date_label = QLabel(f"Released: {formatted_date}")
        main_layout.addWidget(date_label)
        
        # Release notes
        main_layout.addWidget(QLabel("Release Notes:"))
        
        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setText(self.update_info.get('release_notes', 'No release notes available.'))
        main_layout.addWidget(self.notes_text)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)
        
        # Button box
        button_box = QHBoxLayout()
        
        self.update_button = QPushButton("Update Now")
        self.update_button.setDefault(True)
        self.update_button.clicked.connect(self.start_update)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_box.addStretch()
        button_box.addWidget(self.update_button)
        button_box.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_box)
    
    @pyqtSlot()
    def start_update(self):
        """Start the update process"""
        # Disable buttons during update
        self.update_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Show status label
        self.status_label.setVisible(True)
        self.status_label.setText("Starting update...")
        
        # Create and start updater thread
        self.update_thread = UpdaterThread(self.updater, self.update_info)
        self.update_thread.progress_update.connect(self.update_progress)
        self.update_thread.completed.connect(self.update_completed)
        self.update_thread.start()
    
    @pyqtSlot(str, int, str)
    def update_progress(self, status, progress, message):
        """
        Update progress bar and status
        
        Args:
            status: Current status
            progress: Progress percentage (0-100)
            message: Status message
        """
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    @pyqtSlot(bool, str)
    def update_completed(self, success, message):
        """
        Handle update completion
        
        Args:
            success: Whether update was successful
            message: Completion message
        """
        # Update status
        self.status_label.setText(message)
        
        if success:
            # Change dialog buttons to just "Restart"
            self.update_button.setText("Restart Now")
            self.update_button.setEnabled(True)
            self.update_button.clicked.disconnect()
            self.update_button.clicked.connect(self.restart_application)
            
            self.cancel_button.setText("Restart Later")
            self.cancel_button.setEnabled(True)
        else:
            # Re-enable cancel button
            self.cancel_button.setEnabled(True)
            self.cancel_button.setText("Close")
    
    @pyqtSlot()
    def restart_application(self):
        """Restart the application to apply update"""
        # Tell parent to restart
        self.parent().close_application()
        # Return accept to close dialog
        self.accept()
