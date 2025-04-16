try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
except ImportError:
    print("Ошибка импорта PyQt5. Убедитесь, что PyQt5 установлен: pip install PyQt5")
    import sys
    sys.exit(1)

import sys
import logging
import traceback
import os

# Проверка наличия auto_update.py
if not os.path.exists(os.path.join(os.path.dirname(__file__), "auto_update.py")):
    print("Файл auto_update.py не найден! Поместите auto_update.py в ту же папку, что и app_window.py.")
    sys.exit(1)

# Явное создание файла логов, если он не существует
log_file = "error.log"
if not os.path.exists(log_file):
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("Лог ошибок приложения\n")

try:
    from auto_update import auto_update
except Exception as e:
    print(f"Ошибка импорта auto_update: {e}")
    print(traceback.format_exc())
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.debug("Инициализация окна приложения.")
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
        logging.debug("Окно приложения успешно инициализировано.")

    def start_bot(self):
        logging.info("Запуск бота.")
        QMessageBox.information(self, "Информация", "Бот запущен!")

    def stop_bot(self):
        logging.info("Остановка бота.")
        QMessageBox.information(self, "Информация", "Бот остановлен!")

    def exit_app(self):
        logging.info("Выход из приложения.")
        QApplication.quit()

    def update_app(self):
        logging.info("Обновление приложения.")
        repo_path = "./BotRepo"
        repo_url = "https://github.com/MaR1XyAnA/Bot.git"
        try:
            auto_update(repo_path, repo_url)
        except Exception as e:
            logging.error(f"Ошибка при обновлении приложения: {e}", exc_info=True)
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить приложение: {e}")

if __name__ == "__main__":
    try:
        logging.debug("Запуск приложения...")
        print("Запуск приложения...")
        app = QApplication(sys.argv)
        window = BotApp()
        window.show()
        logging.debug("Окно приложения отображено.")
        print("Окно приложения отображено.")
        sys.exit(app.exec_())
    except Exception as e:
        error_message = f"Ошибка при запуске приложения: {e}"
        print(error_message)
        print(traceback.format_exc())  # Вывод полного стека ошибки в консоль
        logging.error(error_message, exc_info=True)
