from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from auto_update import auto_update
import sys
import logging

# Настройка логирования
logging.basicConfig(
    filename="error.log",
    level=logging.DEBUG,  # Установим уровень DEBUG для более подробного вывода
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.debug("Инициализация окна приложения.")  # Логирование
        self.setWindowTitle("Bot Control Panel")
        self.setGeometry(100, 100, 400, 300)

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Макет
        layout = QVBoxLayout()

        # Кнопка запуска бота
        self.start_button = QPushButton("Запустить бота")
        self.start_button.clicked.connect(self.start_bot)
        layout.addWidget(self.start_button)

        # Кнопка остановки бота
        self.stop_button = QPushButton("Остановить бота")
        self.stop_button.clicked.connect(self.stop_bot)
        layout.addWidget(self.stop_button)

        # Кнопка выхода
        self.exit_button = QPushButton("Выход")
        self.exit_button.clicked.connect(self.exit_app)
        layout.addWidget(self.exit_button)

        # Кнопка автообновления
        self.update_button = QPushButton("Обновить приложение")
        self.update_button.clicked.connect(self.update_app)
        layout.addWidget(self.update_button)

        # Установка макета
        central_widget.setLayout(layout)
        logging.debug("Окно приложения успешно инициализировано.")  # Логирование

    def start_bot(self):
        logging.info("Запуск бота.")  # Логирование
        QMessageBox.information(self, "Информация", "Бот запущен!")

    def stop_bot(self):
        logging.info("Остановка бота.")  # Логирование
        QMessageBox.information(self, "Информация", "Бот остановлен!")

    def exit_app(self):
        logging.info("Выход из приложения.")  # Логирование
        QApplication.quit()

    def update_app(self):
        logging.info("Обновление приложения.")  # Логирование
        repo_path = "./BotRepo"  # Локальная папка для репозитория
        repo_url = "https://github.com/MaR1XyAnA/Bot.git"  # URL вашего репозитория
        try:
            auto_update(repo_path, repo_url)
        except Exception as e:
            logging.error(f"Ошибка при обновлении приложения: {e}", exc_info=True)
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить приложение: {e}")

if __name__ == "__main__":
    try:
        logging.debug("Запуск приложения...")  # Логирование
        print("Запуск приложения...")  # Отладочный вывод
        app = QApplication(sys.argv)
        window = BotApp()
        window.show()
        logging.debug("Окно приложения отображено.")  # Логирование
        print("Окно приложения отображено.")  # Отладочный вывод
        sys.exit(app.exec_())
    except Exception as e:
        error_message = f"Ошибка при запуске приложения: {e}"
        print(error_message)  # Вывод ошибки в консоль
        logging.error(error_message, exc_info=True)  # Логирование ошибки
