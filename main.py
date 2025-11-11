import sys
import os
import requests
import zipfile
import tempfile
import shutil
from PyQt5 import QtWidgets, QtCore
from ui import MajesticBotWindow, SettingsWindow
from bots import oranges, lumberjack, mine, quarry, captcha, mushrooms
import threading


class Controller:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = MajesticBotWindow()
        self.settings_window = None
        self.bot_threads = {}  # Для потоков ботов
        self.bot_stop_flags = {}  # Для остановки ботов
        
        self.connect_signals()

    def connect_signals(self):
        for button in self.main_window.findChildren(QtWidgets.QPushButton):
            action = button.property("action")
            if action:
                button.clicked.connect(lambda _, a=action: self.run_bot(a))
        self.main_window.settings_btn.clicked.connect(self.open_settings)

    def run_bot(self, bot_name):
        bots_map = {
            "oranges": oranges,
            "lumberjack": lumberjack,
            "mine": mine,
            "quarry": quarry,
            "captcha": captcha,
            "mushrooms": mushrooms,
        }
        # Если бот уже запущен — останавливаем
        if bot_name in self.bot_threads and self.bot_threads[bot_name].is_alive():
            print(f"[INFO] Остановка бота: {bot_name}")
            self.bot_stop_flags[bot_name] = True
            if hasattr(self.main_window, "clear_active_action"):
                self.main_window.clear_active_action()
            return

        bot = bots_map.get(bot_name)
        if bot:
            print(f"[INFO] Запуск бота: {bot_name}")
            self.bot_stop_flags[bot_name] = False
            if hasattr(self.main_window, "set_active_action"):
                self.main_window.set_active_action(bot_name)

            def bot_runner():
                try:
                    if hasattr(bot, "run") and callable(bot.run):
                        bot.run(stop_flag=lambda: self.bot_stop_flags[bot_name])
                    elif hasattr(bot, "start") and callable(bot.start):
                        bot.start()
                    elif hasattr(bot, "__call__"):
                        bot()
                    else:
                        print(f"[Ошибка] В модуле '{bot_name}' нет функции run/start или вызываемого класса.")
                except Exception as e:
                    print(f"[Ошибка] Не удалось запустить бота '{bot_name}': {e}")
                finally:
                    if hasattr(self.main_window, "clear_active_action"):
                        self.main_window.clear_active_action()

            t = threading.Thread(target=bot_runner, daemon=True)
            self.bot_threads[bot_name] = t
            t.start()
        else:
            print("[Ошибка] Неизвестный бот:", bot_name)

    def save_settings(self):
        delay = self.settings_window.delay_input.text()
        key = self.settings_window.key_input.text()
        print(f"[Настройки сохранены] Задержка: {delay}s | Клавиша: {key}")
        QtWidgets.QMessageBox.information(self.settings_window, "Сохранено", "Настройки успешно сохранены!")
        # Сохраняем настройки в файл
        try:
            with open("settings.ini", "w", encoding="utf-8") as f:
                f.write(f"delay={delay}\n")
                f.write(f"key={key}\n")
        except Exception as e:
            print(f"[Ошибка] Не удалось сохранить настройки: {e}")

    def open_settings(self):
        if not self.settings_window or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow()
            # Загружаем настройки из файла
            try:
                with open("settings.ini", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("delay="):
                            self.settings_window.delay_input.setText(line.strip().split("=", 1)[1])
                        elif line.startswith("key="):
                            self.settings_window.key_input.setText(line.strip().split("=", 1)[1])
            except FileNotFoundError:
                pass  # Файл настроек еще не создан
            self.settings_window.save_btn.clicked.connect(self.save_settings)
            self.settings_window.show()
        else:
            self.settings_window.activateWindow()

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = Controller()
    controller.run()