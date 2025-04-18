"""
Main Window Module
The primary user interface for the fishing bot application.
"""
import os
import sys
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QTextEdit, QGroupBox, 
                           QTabWidget, QCheckBox, QSpinBox, QComboBox,
                           QSlider, QSystemTrayIcon, QMenu, QAction, 
                           QMessageBox, QProgressBar, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt5.QtGui import QIcon, QFont, QTextCursor

from ui.settings_dialog import SettingsDialog
from ui.update_dialog import UpdateDialog
from ui.styles import get_style_sheet, set_dark_theme
from bot_interface import BotInterface
from updater import Updater

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config_manager):
        """
        Initialize the main window
        
        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        self.config_manager = config_manager
        self.bot_interface = BotInterface(
            config_manager, 
            status_callback=self.update_bot_status,
            log_callback=self.add_log_message
        )
        self.updater = Updater(
            config_manager,
            update_callback=self.update_progress
        )
        
        # Set window properties
        self.setWindowTitle("Fishing Bot")
        self.setMinimumSize(800, 600)
        
        # Apply stylesheet
        set_dark_theme(self)
        self.setStyleSheet(get_style_sheet())
        
        # Initialize UI components
        self._init_ui()
        
        # Setup tray icon
        self._setup_tray_icon()
        
        # Setup timers
        self._setup_timers()
        
        # Check for updates on startup if enabled
        settings = self.config_manager.get_settings()
        if settings.get("check_for_updates_on_startup", True):
            QTimer.singleShot(2000, self.check_for_updates)
    
    def _init_ui(self):
        """Initialize the user interface"""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Status bar at the top
        status_bar = QHBoxLayout()
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_bar.addWidget(self.status_label)
        
        status_bar.addStretch()
        
        self.version_label = QLabel(f"Version: {self.config_manager.get_settings().get('version', '1.0.0')}")
        status_bar.addWidget(self.version_label)
        
        main_layout.addLayout(status_bar)
        
        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)
        
        # Upper section - Controls and stats
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        
        # Control panel
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout(control_group)
        
        # Start/Stop buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Fishing")
        self.start_button.setIcon(QIcon("assets/fishing_icon.svg"))
        self.start_button.clicked.connect(self.start_bot)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setIcon(QIcon("assets/fishing_icon.svg"))
        self.stop_button.clicked.connect(self.stop_bot)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        control_layout.addLayout(button_layout)
        
        # Pause/Resume buttons
        button_layout2 = QHBoxLayout()
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_bot)
        self.pause_button.setEnabled(False)
        button_layout2.addWidget(self.pause_button)
        
        self.resume_button = QPushButton("Resume")
        self.resume_button.clicked.connect(self.resume_bot)
        self.resume_button.setEnabled(False)
        button_layout2.addWidget(self.resume_button)
        
        control_layout.addLayout(button_layout2)
        
        # Quick settings
        self.auto_cast_check = QCheckBox("Auto Cast")
        self.auto_cast_check.setChecked(True)
        control_layout.addWidget(self.auto_cast_check)
        
        cast_layout = QHBoxLayout()
        cast_layout.addWidget(QLabel("Cast interval:"))
        self.cast_interval = QSpinBox()
        self.cast_interval.setRange(5, 300)
        self.cast_interval.setValue(self.config_manager.get_fishing_settings().get("cast_interval", 30))
        self.cast_interval.setSuffix(" sec")
        cast_layout.addWidget(self.cast_interval)
        control_layout.addLayout(cast_layout)
        
        detection_layout = QHBoxLayout()
        detection_layout.addWidget(QLabel("Detection:"))
        self.detection_method = QComboBox()
        self.detection_method.addItems(["Color", "Motion", "Sound"])
        current_method = self.config_manager.get_fishing_settings().get("detection_method", "color")
        self.detection_method.setCurrentText(current_method.capitalize())
        detection_layout.addWidget(self.detection_method)
        control_layout.addLayout(detection_layout)
        
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(0, 100)
        self.sensitivity_slider.setValue(self.config_manager.get_fishing_settings().get("detection_sensitivity", 50))
        sensitivity_layout.addWidget(self.sensitivity_slider)
        self.sensitivity_value = QLabel(f"{self.sensitivity_slider.value()}%")
        sensitivity_layout.addWidget(self.sensitivity_value)
        control_layout.addLayout(sensitivity_layout)
        
        # Connect slider value change
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity_label)
        
        # Add save button for quick settings
        save_settings_button = QPushButton("Save Settings")
        save_settings_button.clicked.connect(self.save_quick_settings)
        control_layout.addWidget(save_settings_button)
        
        # Add settings button
        settings_button = QPushButton("Advanced Settings")
        settings_button.setIcon(QIcon("assets/settings_icon.svg"))
        settings_button.clicked.connect(self.open_settings)
        control_layout.addWidget(settings_button)
        
        # Add check for updates button
        update_button = QPushButton("Check for Updates")
        update_button.setIcon(QIcon("assets/update_icon.svg"))
        update_button.clicked.connect(self.check_for_updates)
        control_layout.addWidget(update_button)
        
        upper_layout.addWidget(control_group)
        
        # Stats panel
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_session_time = QLabel("Session time: 00:00:00")
        stats_layout.addWidget(self.stats_session_time)
        
        self.stats_fish_caught = QLabel("Fish caught: 0")
        stats_layout.addWidget(self.stats_fish_caught)
        
        self.stats_fish_per_hour = QLabel("Fish per hour: 0")
        stats_layout.addWidget(self.stats_fish_per_hour)
        
        stats_layout.addStretch()
        
        upper_layout.addWidget(stats_group)
        
        splitter.addWidget(upper_widget)
        
        # Lower section - Log
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # Clear log button
        clear_log_button = QPushButton("Clear Log")
        clear_log_button.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_button)
        
        splitter.addWidget(log_group)
        
        # Set initial splitter sizes (33% top, 67% bottom)
        splitter.setSizes([200, 400])
        
        main_layout.addWidget(splitter)
        
        # Update progress bar at the bottom
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Initial log message
        self.add_log_message("Application started")
    
    def _setup_tray_icon(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/app_icon.svg"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        start_action = QAction("Start Fishing", self)
        start_action.triggered.connect(self.start_bot)
        tray_menu.addAction(start_action)
        
        stop_action = QAction("Stop Fishing", self)
        stop_action.triggered.connect(self.stop_bot)
        tray_menu.addAction(stop_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Show tray icon
        self.tray_icon.show()
    
    def _setup_timers(self):
        """Setup application timers"""
        # Timer for updating statistics (every second)
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)
    
    @pyqtSlot()
    def update_stats(self):
        """Update statistics display"""
        if hasattr(self.bot_interface.fishing_bot, 'session_start_time') and self.bot_interface.fishing_bot.session_start_time:
            # Get stats from the bot
            stats = self.bot_interface.fishing_bot.get_stats()
            
            # Update UI elements
            session_seconds = int(stats.get("session_duration", 0))
            hours, remainder = divmod(session_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            self.stats_session_time.setText(f"Session time: {hours:02}:{minutes:02}:{seconds:02}")
            self.stats_fish_caught.setText(f"Fish caught: {stats.get('fish_caught', 0)}")
            self.stats_fish_per_hour.setText(f"Fish per hour: {stats.get('fish_per_hour', 0):.1f}")
    
    @pyqtSlot()
    def start_bot(self):
        """Start the fishing bot"""
        if self.bot_interface.start_bot():
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
    
    @pyqtSlot()
    def stop_bot(self):
        """Stop the fishing bot"""
        if self.bot_interface.stop_bot():
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(False)
    
    @pyqtSlot()
    def pause_bot(self):
        """Pause the fishing bot"""
        if self.bot_interface.pause_bot():
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)
    
    @pyqtSlot()
    def resume_bot(self):
        """Resume the fishing bot"""
        if self.bot_interface.resume_bot():
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
    
    @pyqtSlot(str)
    def update_bot_status(self, status):
        """
        Update the bot status display
        
        Args:
            status: New status string
        """
        status_text = "Status: "
        
        if status == "running":
            status_text += "Running"
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
        elif status == "stopped":
            status_text += "Stopped"
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
        elif status == "paused":
            status_text += "Paused"
            self.status_label.setStyleSheet("font-weight: bold; color: orange;")
        elif status == "error":
            status_text += "Error"
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
        else:
            status_text += status.capitalize()
            self.status_label.setStyleSheet("font-weight: bold;")
            
        self.status_label.setText(status_text)
    
    @pyqtSlot(str)
    def add_log_message(self, message):
        """
        Add a message to the log
        
        Args:
            message: Message to add
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Append to log and scroll to bottom
        self.log_text.append(log_entry)
        self.log_text.moveCursor(QTextCursor.End)
    
    @pyqtSlot()
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.clear()
        self.add_log_message("Log cleared")
    
    @pyqtSlot(int)
    def update_sensitivity_label(self, value):
        """
        Update sensitivity label when slider changes
        
        Args:
            value: New sensitivity value
        """
        self.sensitivity_value.setText(f"{value}%")
    
    @pyqtSlot()
    def save_quick_settings(self):
        """Save the quick settings to configuration"""
        # Get current values
        cast_interval = self.cast_interval.value()
        detection_method = self.detection_method.currentText().lower()
        sensitivity = self.sensitivity_slider.value()
        
        # Update configuration
        fishing_settings = self.config_manager.get_fishing_settings()
        fishing_settings["cast_interval"] = cast_interval
        fishing_settings["detection_method"] = detection_method
        fishing_settings["detection_sensitivity"] = sensitivity
        
        # Save configuration
        self.config_manager.update_setting("fishing_settings", fishing_settings)
        
        # Log message
        self.add_log_message("Settings saved")
    
    @pyqtSlot()
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self, self.config_manager)
        if dialog.exec_():
            # Settings were saved in the dialog
            self.add_log_message("Advanced settings updated")
            
            # Update quick settings display to match
            fishing_settings = self.config_manager.get_fishing_settings()
            self.cast_interval.setValue(fishing_settings.get("cast_interval", 30))
            self.detection_method.setCurrentText(fishing_settings.get("detection_method", "color").capitalize())
            self.sensitivity_slider.setValue(fishing_settings.get("detection_sensitivity", 50))
    
    @pyqtSlot()
    def check_for_updates(self):
        """Check for application updates"""
        self.add_log_message("Checking for updates...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        # Check in a separate thread to not block UI
        update_info = self.updater.check_for_updates(force=True)
        
        if update_info:
            # Show update dialog
            dialog = UpdateDialog(self, update_info, self.updater)
            dialog.exec_()
        else:
            # Fail silently if update_info is None - error messages are shown via callback
            pass
    
    @pyqtSlot(str, int, str)
    def update_progress(self, status, progress, message):
        """
        Update progress bar and log for updates
        
        Args:
            status: Current status
            progress: Progress percentage (0-100)
            message: Status message
        """
        # Update progress bar
        self.progress_bar.setValue(progress)
        self.progress_bar.setVisible(progress < 100 or status == "error")
        
        # Log the message
        self.add_log_message(message)
        
        # Show notification for important status changes
        if status in ["available", "complete", "error"]:
            if self.config_manager.get_ui_settings().get("show_notifications", True):
                self.tray_icon.showMessage("Fishing Bot", message, QSystemTrayIcon.Information, 5000)
    
    def tray_icon_activated(self, reason):
        """
        Handle tray icon activation
        
        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def closeEvent(self, event):
        """
        Handle window close event
        
        Args:
            event: Close event
        """
        # Check if minimize to tray is enabled
        if self.config_manager.get_ui_settings().get("minimize_to_tray", True) and self.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("Fishing Bot", "Application minimized to tray", QSystemTrayIcon.Information, 2000)
        else:
            self.close_application()
    
    def close_application(self):
        """Properly close the application"""
        # Stop the bot if running
        if self.bot_interface.running:
            self.bot_interface.stop_bot()
        
        # Save any pending settings
        self.save_quick_settings()
        
        # Exit the application
        QApplication.quit()
