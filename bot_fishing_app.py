import sys
import os
import shutil
import tempfile
import requests
import zipfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QHBoxLayout, QFrame, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

# Импортируем класс бота
from fishing_bot import FishingBot

class FishingBotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.bot = FishingBot(self.log_message)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Бот для автоматизации рыбалки")
        self.setFixedSize(480, 360)

        # Основной шрифт
        font = QFont("Segoe UI", 11)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        self.start_btn = QPushButton("Старт")
        self.start_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_btn.setFont(font)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 18px; border-radius: 6px;")
        self.stop_btn = QPushButton("Стоп")
        self.stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stop_btn.setFont(font)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("background-color: #F44336; color: white; padding: 8px 18px; border-radius: 6px;")
        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.setIcon(QIcon.fromTheme("preferences-system"))
        self.settings_btn.setFont(font)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 18px; border-radius: 6px;")
        self.update_btn = QPushButton("Обновить")
        self.update_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.update_btn.setFont(font)
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px 18px; border-radius: 6px;")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addWidget(self.update_btn)

        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #bbb; background: #bbb; min-height:2px;")
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Логи
        self.log_label = QLabel("Логи:")
        self.log_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.log_label.setStyleSheet("margin-top: 10px; margin-bottom: 4px; color: #333;")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet(
            "background-color: #f5f5f5; border: 1px solid #ccc; border-radius: 6px; padding: 8px;"
        )
        self.log_text.setMinimumHeight(140)

        layout.addLayout(btn_layout)
        layout.addWidget(line)
        layout.addWidget(self.log_label)
        layout.addWidget(self.log_text)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: #f0f4f8;
            }
        """)

        # Пример подключения событий
        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.settings_btn.clicked.connect(self.open_settings)
        self.update_btn.clicked.connect(self.update_from_github)

    def log_message(self, msg):
        self.log_text.append(msg)

    def start_bot(self):
        self.bot.start()

    def stop_bot(self):
        self.bot.stop()

    def open_settings(self):
        self.log_text.append("Открыто окно настроек (в разработке).")

    def update_from_github(self):
        current_version = "v1.0.0"  # Укажите актуальную версию вашего приложения
        repo_api = "https://api.github.com/repos/MaR1XyAnA/Bot/releases/latest"
        self.log_text.append("Проверка обновлений через GitHub Releases...")
        try:
            latest = requests.get(repo_api, timeout=10).json()
            latest_version = latest.get("tag_name")
            if not latest_version:
                self.log_text.append("Не удалось получить информацию о последней версии.")
                return
            self.log_text.append(f"Последняя версия: {latest_version}")
            if latest_version == current_version:
                self.log_text.append("У вас уже установлена последняя версия.")
                return
            assets = latest.get("assets", [])
            if not assets:
                self.log_text.append("В релизе нет доступных файлов для загрузки.")
                return
            url = assets[0].get("browser_download_url")
            if not url:
                self.log_text.append("Не найден файл для загрузки в релизе.")
                return
            self.log_text.append(f"Скачивание новой версии: {url}")
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                r = requests.get(url, stream=True, timeout=30)
                if r.status_code == 200:
                    for chunk in r.iter_content(chunk_size=8192):
                        tmpfile.write(chunk)
                    tmpfile_path = tmpfile.name
                else:
                    self.log_text.append(f"Ошибка скачивания: {r.status_code}")
                    return
            # Заменить исполняемый файл (этот файл)
            app_path = os.path.abspath(__file__)
            try:
                shutil.copy2(tmpfile_path, app_path)
                self.log_text.append("Обновление завершено. Перезапустите приложение.")
            except Exception as e:
                self.log_text.append(f"Ошибка при замене файла: {e}")
            finally:
                os.remove(tmpfile_path)
        except Exception as e:
            self.log_text.append(f"Ошибка обновления: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FishingBotApp()
    window.show()
    sys.exit(app.exec_())
