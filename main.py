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


class Updater:
    def __init__(self, repo_owner, repo_name, current_version):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.latest_version = None
        self.update_url = None

    def check_for_updates(self):
        """Проверяет наличие обновлений на GitHub"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.latest_version = data['tag_name']
                self.update_url = data['zipball_url']
                return self.latest_version != self.current_version
            return False
        except Exception as e:
            print(f"[Ошибка проверки обновлений]: {e}")
            return False

    def download_and_install_update(self):
        """Скачивает и устанавливает обновление"""
        try:
            if not self.update_url:
                return False

            # Создаем временную директорию
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")
            
            # Скачиваем архив
            print(f"[Обновление] Скачивание обновления {self.latest_version}...")
            response = requests.get(self.update_url, stream=True, timeout=30)
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Распаковываем архив
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Находим корневую директорию распакованного содержимого
            extracted_items = os.listdir(extract_dir)
            if len(extracted_items) == 1:
                update_src_dir = os.path.join(extract_dir, extracted_items[0])
            else:
                update_src_dir = extract_dir

            # Копируем файлы обновления (кроме настроек)
            self._copy_update_files(update_src_dir, os.getcwd())
            
            # Очищаем временные файлы
            shutil.rmtree(temp_dir)
            
            print("[Обновление] Обновление успешно установлено!")
            return True
            
        except Exception as e:
            print(f"[Ошибка обновления]: {e}")
            return False

    def _copy_update_files(self, src_dir, dest_dir):
        """Копирует файлы обновления, исключая конфигурационные файлы"""
        exclude_files = {'settings.ini', 'config.json'}  # Файлы которые не должны обновляться
        exclude_dirs = {'.git', '__pycache__', 'logs'}   # Директории которые не должны обновляться
        
        for root, dirs, files in os.walk(src_dir):
            # Исключаем директории
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                    
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, src_dir)
                dest_file = os.path.join(dest_dir, rel_path)
                
                # Создаем директории если нужно
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                
                # Копируем файл
                shutil.copy2(src_file, dest_file)
                print(f"[Обновление] Обновлен: {rel_path}")


class Controller:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = MajesticBotWindow()
        self.settings_window = None
        self.bot_threads = {}  # Для потоков ботов
        self.bot_stop_flags = {}  # Для остановки ботов
        
        # Инициализация системы обновлений
        self.updater = Updater(
            repo_owner="MaR1XyAnA",  # Ваше имя пользователя GitHub
            repo_name="Bot",         # Название вашего репозитория
            current_version="1.0.0"  # Текущая версия приложения
        )
        
        # Флаг для отслеживания статуса обновления
        self.update_in_progress = False
        
        self.connect_signals()
        
        # Запускаем проверку обновлений через небольшой таймаут, чтобы UI успел загрузиться
        QtCore.QTimer.singleShot(1000, self.check_updates_on_start)

    def connect_signals(self):
        for button in self.main_window.findChildren(QtWidgets.QPushButton):
            action = button.property("action")
            if action:
                button.clicked.connect(lambda _, a=action: self.run_bot(a))
        self.main_window.settings_btn.clicked.connect(self.open_settings)
        
        # Добавляем кнопку проверки обновлений если она есть в UI
        if hasattr(self.main_window, 'update_btn'):
            self.main_window.update_btn.clicked.connect(self.check_for_updates_manual)

    def check_updates_on_start(self):
        """Проверяет обновления при запуске приложения"""
        if not self.update_in_progress:
            threading.Thread(target=self._auto_check_updates, daemon=True).start()

    def _auto_check_updates(self):
        """Автоматическая проверка обновлений при старте"""
        try:
            if self.updater.check_for_updates():
                print(f"[Обновление] Доступна новая версия: {self.updater.latest_version}")
                # Используем QTimer для вызова в главном потоке
                QtCore.QTimer.singleShot(0, lambda: self.show_update_notification(self.updater.latest_version, auto=True))
            else:
                print("[Обновление] У вас актуальная версия")
        except Exception as e:
            print(f"[Ошибка автообновления]: {e}")

    def check_for_updates_manual(self):
        """Ручная проверка обновлений"""
        if self.update_in_progress:
            return
            
        def update_check():
            try:
                if self.updater.check_for_updates():
                    QtCore.QTimer.singleShot(0, lambda: self.show_update_dialog(self.updater.latest_version))
                else:
                    QtCore.QTimer.singleShot(0, self.show_no_updates_message)
            except Exception as e:
                QtCore.QTimer.singleShot(0, lambda: self.show_update_error(str(e)))

        threading.Thread(target=update_check, daemon=True).start()

    def show_no_updates_message(self):
        """Показывает сообщение об отсутствии обновлений"""
        QtWidgets.QMessageBox.information(
            self.main_window, 
            "Проверка обновлений", 
            "У вас актуальная версия программы!"
        )

    def show_update_notification(self, new_version, auto=False):
        """Показывает уведомление о доступном обновлении"""
        title = "Доступно обновление" if auto else "Обновление доступно"
        message = f"Доступна новая версия {new_version}. Хотите обновить программу сейчас?"
        
        reply = QtWidgets.QMessageBox.question(
            self.main_window,
            title,
            message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.install_update()

    def show_update_dialog(self, new_version):
        """Показывает диалог обновления"""
        self.show_update_notification(new_version, auto=False)

    def show_update_error(self, error_message):
        """Показывает ошибку обновления"""
        QtWidgets.QMessageBox.warning(
            self.main_window,
            "Ошибка обновления",
            f"Произошла ошибка при проверке обновлений: {error_message}"
        )

    def install_update(self):
        """Устанавливает обновление"""
        if self.update_in_progress:
            return
            
        self.update_in_progress = True
        
        # Показываем диалог прогресса
        self.progress = QtWidgets.QProgressDialog("Установка обновления...", "Отмена", 0, 0, self.main_window)
        self.progress.setWindowTitle("Обновление")
        self.progress.setWindowModality(QtCore.Qt.WindowModal)
        self.progress.show()
        
        def install_thread():
            try:
                success = self.updater.download_and_install_update()
                
                # Закрываем диалог прогресса и показываем результат в главном потоке
                QtCore.QTimer.singleShot(0, lambda: self._finish_update(success))
                    
            except Exception as e:
                QtCore.QTimer.singleShot(0, lambda: self._finish_update(False, str(e)))

        threading.Thread(target=install_thread, daemon=True).start()

    def _finish_update(self, success, error_message=None):
        """Завершает процесс обновления"""
        self.update_in_progress = False
        
        if hasattr(self, 'progress'):
            self.progress.close()
        
        if success:
            reply = QtWidgets.QMessageBox.information(
                self.main_window,
                "Обновление завершено",
                "Обновление успешно установлено! Программа будет перезапущена.",
                QtWidgets.QMessageBox.Ok
            )
            if reply == QtWidgets.QMessageBox.Ok:
                self.restart_application()
        else:
            if error_message:
                QtWidgets.QMessageBox.warning(
                    self.main_window,
                    "Ошибка",
                    f"Не удалось установить обновление: {error_message}"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self.main_window,
                    "Ошибка",
                    "Не удалось установить обновление. Попробуйте позже."
                )

    def restart_application(self):
        """Перезапускает приложение"""
        QtWidgets.QApplication.quit()
        os.execv(sys.executable, [sys.executable] + sys.argv)

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