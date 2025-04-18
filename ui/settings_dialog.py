"""
Settings Dialog Module
Dialog for configuring application settings.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                           QGroupBox, QLabel, QLineEdit, QCheckBox,
                           QSpinBox, QComboBox, QPushButton, QFormLayout,
                           QDialogButtonBox, QSlider)
from PyQt5.QtCore import Qt, pyqtSlot

class SettingsDialog(QDialog):
    """Settings dialog for configuring the application"""
    
    def __init__(self, parent, config_manager):
        """
        Initialize the settings dialog
        
        Args:
            parent: Parent widget
            config_manager: Configuration manager instance
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.settings = config_manager.get_settings()
        
        self.setWindowTitle("Advanced Settings")
        self.setMinimumWidth(500)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # GitHub repo settings
        github_group = QGroupBox("GitHub Updates")
        github_layout = QFormLayout(github_group)
        
        self.github_repo = QLineEdit()
        self.github_repo.setText(self.settings.get("github_repo", "username/fishing-bot"))
        github_layout.addRow("GitHub Repository:", self.github_repo)
        
        self.check_updates = QCheckBox("Check for updates on startup")
        self.check_updates.setChecked(self.settings.get("check_for_updates_on_startup", True))
        github_layout.addRow("", self.check_updates)
        
        general_layout.addWidget(github_group)
        
        # UI settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout(ui_group)
        
        ui_settings = self.settings.get("ui_settings", {})
        
        self.show_notifications = QCheckBox("Show notifications")
        self.show_notifications.setChecked(ui_settings.get("show_notifications", True))
        ui_layout.addRow("", self.show_notifications)
        
        self.minimize_to_tray = QCheckBox("Minimize to tray when closed")
        self.minimize_to_tray.setChecked(ui_settings.get("minimize_to_tray", True))
        ui_layout.addRow("", self.minimize_to_tray)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(ui_settings.get("theme", "dark").capitalize())
        ui_layout.addRow("Theme:", self.theme_combo)
        
        general_layout.addWidget(ui_group)
        
        # Add reset to defaults button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        general_layout.addWidget(reset_button)
        
        general_layout.addStretch()
        
        # Fishing settings tab
        fishing_tab = QWidget()
        fishing_layout = QVBoxLayout(fishing_tab)
        
        fishing_group = QGroupBox("Fishing Bot Settings")
        fishing_form = QFormLayout(fishing_group)
        
        fishing_settings = self.settings.get("fishing_settings", {})
        
        self.auto_start = QCheckBox("Start bot automatically on application launch")
        self.auto_start.setChecked(fishing_settings.get("auto_start", False))
        fishing_form.addRow("", self.auto_start)
        
        self.cast_interval = QSpinBox()
        self.cast_interval.setRange(5, 300)
        self.cast_interval.setValue(fishing_settings.get("cast_interval", 30))
        self.cast_interval.setSuffix(" sec")
        fishing_form.addRow("Cast interval:", self.cast_interval)
        
        self.detection_method = QComboBox()
        self.detection_method.addItems(["Color", "Motion", "Sound"])
        self.detection_method.setCurrentText(fishing_settings.get("detection_method", "color").capitalize())
        fishing_form.addRow("Detection method:", self.detection_method)
        
        sens_layout = QHBoxLayout()
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(0, 100)
        self.sensitivity_slider.setValue(fishing_settings.get("detection_sensitivity", 50))
        self.sensitivity_value = QLabel(f"{self.sensitivity_slider.value()}%")
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity_label)
        
        sens_layout.addWidget(self.sensitivity_slider)
        sens_layout.addWidget(self.sensitivity_value)
        
        fishing_form.addRow("Detection sensitivity:", sens_layout)
        
        fishing_layout.addWidget(fishing_group)
        
        # Hotkey settings
        hotkey_group = QGroupBox("Hotkeys")
        hotkey_form = QFormLayout(hotkey_group)
        
        hotkeys = self.settings.get("hotkeys", {})
        
        self.toggle_hotkey = QLineEdit()
        self.toggle_hotkey.setText(hotkeys.get("toggle_bot", "F9"))
        hotkey_form.addRow("Toggle bot:", self.toggle_hotkey)
        
        self.stop_hotkey = QLineEdit()
        self.stop_hotkey.setText(hotkeys.get("emergency_stop", "F10"))
        hotkey_form.addRow("Emergency stop:", self.stop_hotkey)
        
        fishing_layout.addWidget(hotkey_group)
        fishing_layout.addStretch()
        
        # Add tabs to tab widget
        tab_widget.addTab(general_tab, "General")
        tab_widget.addTab(fishing_tab, "Fishing")
        
        main_layout.addWidget(tab_widget)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    @pyqtSlot(int)
    def update_sensitivity_label(self, value):
        """
        Update sensitivity label when slider changes
        
        Args:
            value: New sensitivity value
        """
        self.sensitivity_value.setText(f"{value}%")
    
    @pyqtSlot()
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        # Ask user for confirmation
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to defaults
            self.config_manager.reset_to_defaults()
            self.settings = self.config_manager.get_settings()
            
            # Update UI with new defaults
            self.github_repo.setText(self.settings.get("github_repo", "username/fishing-bot"))
            self.check_updates.setChecked(self.settings.get("check_for_updates_on_startup", True))
            
            ui_settings = self.settings.get("ui_settings", {})
            self.show_notifications.setChecked(ui_settings.get("show_notifications", True))
            self.minimize_to_tray.setChecked(ui_settings.get("minimize_to_tray", True))
            self.theme_combo.setCurrentText(ui_settings.get("theme", "dark").capitalize())
            
            fishing_settings = self.settings.get("fishing_settings", {})
            self.auto_start.setChecked(fishing_settings.get("auto_start", False))
            self.cast_interval.setValue(fishing_settings.get("cast_interval", 30))
            self.detection_method.setCurrentText(fishing_settings.get("detection_method", "color").capitalize())
            self.sensitivity_slider.setValue(fishing_settings.get("detection_sensitivity", 50))
            
            hotkeys = self.settings.get("hotkeys", {})
            self.toggle_hotkey.setText(hotkeys.get("toggle_bot", "F9"))
            self.stop_hotkey.setText(hotkeys.get("emergency_stop", "F10"))
    
    @pyqtSlot()
    def save_settings(self):
        """Save settings and close dialog"""
        # Update settings with values from UI
        self.settings["github_repo"] = self.github_repo.text()
        self.settings["check_for_updates_on_startup"] = self.check_updates.isChecked()
        
        # UI settings
        ui_settings = {
            "show_notifications": self.show_notifications.isChecked(),
            "minimize_to_tray": self.minimize_to_tray.isChecked(),
            "theme": self.theme_combo.currentText().lower()
        }
        self.settings["ui_settings"] = ui_settings
        
        # Fishing settings
        fishing_settings = {
            "auto_start": self.auto_start.isChecked(),
            "cast_interval": self.cast_interval.value(),
            "detection_method": self.detection_method.currentText().lower(),
            "detection_sensitivity": self.sensitivity_slider.value()
        }
        self.settings["fishing_settings"] = fishing_settings
        
        # Hotkeys
        hotkeys = {
            "toggle_bot": self.toggle_hotkey.text(),
            "emergency_stop": self.stop_hotkey.text()
        }
        self.settings["hotkeys"] = hotkeys
        
        # Save settings
        self.config_manager.save_settings(self.settings)
        
        # Close dialog
        self.accept()
