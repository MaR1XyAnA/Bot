"""
Styles Module
Contains styling information for the application.
"""

def get_style_sheet():
    """
    Get the application style sheet
    
    Returns:
        str: CSS style sheet
    """
    return """
    QMainWindow, QDialog {
        background-color: #2e2e2e;
        color: #f0f0f0;
    }
    
    QWidget {
        color: #f0f0f0;
    }
    
    QGroupBox {
        border: 1px solid #555;
        border-radius: 5px;
        margin-top: 1em;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px;
    }
    
    QPushButton {
        background-color: #3a3a3a;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 6px 12px;
        min-width: 80px;
    }
    
    QPushButton:hover {
        background-color: #444;
    }
    
    QPushButton:pressed {
        background-color: #333;
    }
    
    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #666;
    }
    
    QLineEdit, QSpinBox, QComboBox {
        background-color: #3a3a3a;
        border: 1px solid #555;
        border-radius: 3px;
        padding: 5px;
    }
    
    QTextEdit {
        background-color: #333;
        border: 1px solid #555;
        border-radius: 3px;
    }
    
    QSlider::groove:horizontal {
        border: 1px solid #555;
        height: 8px;
        background: #333;
        margin: 2px 0;
        border-radius: 4px;
    }
    
    QSlider::handle:horizontal {
        background: #5e8edc;
        border: 1px solid #5e8edc;
        width: 18px;
        margin: -2px 0;
        border-radius: 9px;
    }
    
    QProgressBar {
        border: 1px solid #555;
        border-radius: 3px;
        text-align: center;
    }
    
    QProgressBar::chunk {
        background-color: #5e8edc;
    }
    
    /* Specific button styling */
    #start_button {
        background-color: #45723d;
    }
    
    #start_button:hover {
        background-color: #528a4a;
    }
    
    #stop_button {
        background-color: #8a3c3c;
    }
    
    #stop_button:hover {
        background-color: #9e4545;
    }
    """

def set_dark_theme(app):
    """
    Apply dark theme to the application
    
    Args:
        app: QApplication or QWidget instance
    """
    # Apply stylesheet to app
    app.setStyleSheet(get_style_sheet())
    
    # Add object names to special buttons if they exist
    if hasattr(app, 'start_button'):
        app.start_button.setObjectName("start_button")
    if hasattr(app, 'stop_button'):
        app.stop_button.setObjectName("stop_button")
