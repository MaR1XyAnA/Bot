import sys
import os
import shutil
import tempfile
import requests
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QHBoxLayout
)

class FishingBotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Бот для автоматизации рыбалки")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Старт")
        self.stop_btn = QPushButton("Стоп")
        self.settings_btn = QPushButton("Настройки")
        self.update_btn = QPushButton("Обновить")  # Новая кнопка
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addWidget(self.update_btn)  # Добавляем кнопку

        # Логи
        self.log_label = QLabel("Логи:")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        layout.addLayout(btn_layout)
        layout.addWidget(self.log_label)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

        # Пример подключения событий
        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.settings_btn.clicked.connect(self.open_settings)
        self.update_btn.clicked.connect(self.update_from_github)  # Подключаем обновление

    def start_bot(self):
        self.log_text.append("Бот запущен.")

    def stop_bot(self):
        self.log_text.append("Бот остановлен.")

    def open_settings(self):
        self.log_text.append("Открыто окно настроек (в разработке).")

    def update_from_github(self):
        repo_url = "https://github.com/MaR1XyAnA/Bot/archive/refs/heads/main.zip"
        self.log_text.append("Начинаю обновление с GitHub...")
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "repo.zip")
                # Скачиваем архив
                r = requests.get(repo_url, stream=True)
                if r.status_code == 200:
                    with open(zip_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    self.log_text.append("Архив скачан, распаковка...")
                    # Распаковываем архив
                    with zipfile.ZipFile(zip_path, "r") as zip_ref:
                        zip_ref.extractall(tmpdir)
                    repo_folder = os.path.join(tmpdir, "Bot-main")
                    # Копируем файлы в текущую папку (кроме самого этого файла)
                    for root, dirs, files in os.walk(repo_folder):
                        rel_path = os.path.relpath(root, repo_folder)
                        dest_dir = os.path.join(os.getcwd(), rel_path)
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir, exist_ok=True)
                        for file in files:
                            src_file = os.path.join(root, file)
                            dest_file = os.path.join(dest_dir, file)
                            # Не перезаписываем сам файл приложения во время работы
                            if os.path.abspath(dest_file) == os.path.abspath(__file__):
                                continue
                            shutil.copy2(src_file, dest_file)
                    self.log_text.append("Обновление завершено успешно.")
                else:
                    self.log_text.append(f"Ошибка скачивания: {r.status_code}")
        except Exception as e:
            self.log_text.append(f"Ошибка обновления: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FishingBotApp()
    window.show()
    sys.exit(app.exec_())
