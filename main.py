# main.py

import sys
from PyQt5 import QtWidgets
from ui_manager import App

# ВЕРСИЯ ПРИЛОЖЕНИЯ
APP_VERSION = "1.2"

if __name__ == "__main__":
    q_app = QtWidgets.QApplication(sys.argv)

    # Стиль для темной темы
    dark_stylesheet = """
        QWidget {
            background-color: #2b2b2b;
            color: #f0f0f0;
            font-family: Arial;
        }
        QMainWindow {
            background-color: #2b2b2b;
        }
        QGroupBox {
            background-color: #3c3f41;
            border: 1px solid #555;
            border-radius: 5px;
            margin-top: 1ex;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
        }
        QLineEdit {
            background-color: #3c3f41;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 5px;
        }
        QListWidget {
            background-color: #3c3f41;
            border: 1px solid #555;
            border-radius: 4px;
        }
        QTextEdit {
            background-color: #3c3f41;
            border: 1px solid #555;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #555;
            border: 1px solid #666;
            border-radius: 4px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #666;
        }
        QPushButton:pressed {
            background-color: #777;
        }
        QListWidget::item:selected {
            background-color: #0078d4;
        }
        QGroupBox {
            background-color: #2b2b2b;
        }
        QSizeGrip {
            background-color: transparent;
            width: 16px;
            height: 16px;
        }
    """
    q_app.setStyleSheet(dark_stylesheet)

    main_window = App(app_version=APP_VERSION)
    main_window.show()
    sys.exit(q_app.exec_())
