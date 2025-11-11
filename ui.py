from PyQt5 import QtWidgets, QtCore

# Окно настроек
class SettingsWindow(QtWidgets.QWidget):
    """Окно настроек"""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Настройки")  # Заголовок окна
        self.setFixedSize(350, 200)       # Фиксированный размер окна
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2d31;
                color: white;
                font-family: "Segoe UI";
                font-size: 13px;
            }
            QLabel {
                color: #ddd;
            }
            QLineEdit {
                background-color: #40444b;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 4px;
                color: white;
            }
            QPushButton {
                background-color: #5865f2;
                border: none;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
        """)  # Стили для элементов окна

        layout = QtWidgets.QVBoxLayout()  # Основной вертикальный layout

        self.delay_label = QtWidgets.QLabel("Задержка между действиями (сек):")  # Подпись для задержки
        self.delay_input = QtWidgets.QLineEdit("2.0")  # Поле ввода задержки

        self.key_label = QtWidgets.QLabel("Клавиша активации:")  # Подпись для клавиши
        self.key_input = QtWidgets.QLineEdit("F6")  # Поле ввода клавиши

        self.save_btn = QtWidgets.QPushButton("💾 Сохранить")  # Кнопка сохранения настроек

        # Добавление виджетов в layout
        layout.addWidget(self.delay_label)
        layout.addWidget(self.delay_input)
        layout.addSpacing(10)
        layout.addWidget(self.key_label)
        layout.addWidget(self.key_input)
        layout.addStretch()
        layout.addWidget(self.save_btn)

        self.setLayout(layout)  # Установка layout для окна


# Главное окно приложения
class MajesticBotWindow(QtWidgets.QWidget):
    """Главное окно"""
    def __init__(self):
        super().__init__()
        self.settings_window = None  # Ссылка на окно настроек
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Majestic GTA5")  # Заголовок главного окна
        self.setFixedSize(620, 500)           # Фиксированный размер главного окна
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2d31;
                color: white;
                font-family: "Segoe UI";
                font-size: 13px;
            }
            QPushButton {
                background-color: #4f545c;
                border: none;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #5865f2;
            }
            QPushButton#settings {
                background-color: #0078ff;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton#settings:hover {
                background-color: #3399ff;
            }
            QPushButton#update {
                background-color: #43b581;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton#update:hover {
                background-color: #3aa371;
            }
        """)  # Стили для главного окна и кнопок

        grid = QtWidgets.QGridLayout()  # Сетка для кнопок действий
        grid.setSpacing(10)

        # Кнопки с действиями и их идентификаторы
        self.buttons = {
            "🍊 Включить апельсины": "oranges",
            "🪓 Включить лесоруб": "lumberjack",
            "⛏️ Включить шахту": "mine",
            "⛏ Включить карьер": "quarry",
            "🔄 Включить капчу": "captcha",
            "🍄 Включить грибы": "mushrooms"
        }

        # Размеры кнопок действий
        action_btn_width = 270   # ширина кнопки
        action_btn_height = 100   # высота кнопки

        # Создание и добавление кнопок действий в сетку
        self.action_buttons = []  # Список для хранения кнопок
        for i, text in enumerate(self.buttons.keys()):
            btn = QtWidgets.QPushButton(text)  # Кнопка действия
            btn.setProperty("action", self.buttons[text])  # Свойство для идентификации действия
            btn.setFixedSize(action_btn_width, action_btn_height)  # <-- Размер кнопки
            grid.addWidget(btn, i // 2, i % 2)  # Добавление кнопки в сетку
            btn.clicked.connect(lambda checked, t=text: self.log_message(f"Нажата кнопка: {t}"))  # Логирование нажатия
            self.action_buttons.append(btn)

        self.settings_btn = QtWidgets.QPushButton("⚙️ Настройки")  # Кнопка открытия настроек
        self.settings_btn.setObjectName("settings")  # Для применения отдельного стиля
        self.settings_btn.setFixedSize(150, 50)  # <-- Размер кнопки "Настройки"
        self.settings_btn.clicked.connect(lambda: self.log_message("Открыто окно настроек"))  # Логирование открытия настроек

        self.update_btn = QtWidgets.QPushButton("⬇️ Обновить")  # Кнопка проверки обновлений
        self.update_btn.setObjectName("update")  # Для применения отдельного стиля
        self.update_btn.setFixedSize(150, 50)  # <-- Размер кнопки "Обновить"
        self.update_btn.clicked.connect(lambda: self.log_message("Проверка обновлений..."))  # Логирование

        # --- Логи ---
        self.log_view = QtWidgets.QTextEdit()  # Виджет для логов
        self.log_view.setReadOnly(True)
        self.log_view.setFixedHeight(100)  # Высота логов
        self.log_view.setStyleSheet("""
            QTextEdit {
                background-color: #23272a;
                color: #b9bbbe;
                border-radius: 6px;
                font-size: 12px;
            }
        """)

        # Горизонтальный layout для кнопок и логов
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.settings_btn)
        hbox.addWidget(self.update_btn)
        hbox.addWidget(self.log_view, stretch=1)

        vbox = QtWidgets.QVBoxLayout()  # Основной вертикальный layout
        vbox.addLayout(grid)            # Добавление сетки с кнопками
        vbox.addLayout(hbox)            # Добавление горизонтального блока с кнопками и логами
        vbox.setAlignment(self.settings_btn, QtCore.Qt.AlignLeft)  # Кнопка настроек слева
        vbox.setAlignment(self.update_btn, QtCore.Qt.AlignLeft)  # Кнопка обновления слева
        vbox.setContentsMargins(20, 20, 20, 20)  # Отступы
        self.setLayout(vbox)  # Установка layout для главного окна

    def log_message(self, message):
        """Добавить сообщение в лог"""
        self.log_view.append(message)
