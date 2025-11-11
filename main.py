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
import subprocess


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
        except requests.exceptions.RequestException as e:
            print(f"[Ошибка проверки обновлений]: Сетевая ошибка - {e}")
            return False
        except Exception as e:
            print(f"[Ошибка проверки обновлений]: {e}")
            return False

    def download_and_install_update(self, progress_callback=None):
        """Скачивает и устанавливает обновление"""
        try:
            if not self.update_url:
                print("[Ошибка обновления] URL обновления не найден")
                return False

            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")
            
            print(f"[Обновление] Скачивание обновления {self.latest_version}...")
            response = requests.get(self.update_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size:
                            progress = int((downloaded / total_size) * 100)
                            progress_callback(progress)

            print("[Обновление] Распаковка архива...")
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            extracted_items = os.listdir(extract_dir)
            if len(extracted_items) == 1:
                update_src_dir = os.path.join(extract_dir, extracted_items[0])
            else:
                update_src_dir = extract_dir

            print("[Обновление] Копирование файлов...")
            self._copy_update_files(update_src_dir, os.getcwd())
            
            shutil.rmtree(temp_dir)
            print("[Обновление] Обновление успешно установлено!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"[Ошибка обновления] Ошибка загрузки: {e}")
            return False
        except Exception as e:
            print(f"[Ошибка обновления]: {e}")
            return False

    def _copy_update_files(self, src_dir, dest_dir):
        """Копирует файлы обновления, исключая конфигурационные файлы"""
        exclude_files = {'settings.ini', 'config.json', '.gitignore'}
        exclude_dirs = {'.git', '__pycache__', 'logs', '.github'}
        
        for root, dirs, files in os.walk(src_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                    
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, src_dir)
                dest_file = os.path.join(dest_dir, rel_path)
                
                try:
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    shutil.copy2(src_file, dest_file)
                    print(f"[Обновление] Обновлен: {rel_path}")
                except Exception as e:
                    print(f"[Ошибка копирования] {rel_path}: {e}")


class Controller(QtCore.QObject):
    update_check_done = QtCore.pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.main_window = MajesticBotWindow()
        self.settings_window = None
        self.bot_threads = {}
        self.bot_stop_flags = {}
        
        self.updater = Updater(
            repo_owner="MaR1XyAnA",
            repo_name="Bot",
            current_version="1.0.0"
        )
        
        self.connect_signals()
        self.check_updates_on_start()

    def connect_signals(self):
        for button in self.main_window.findChildren(QtWidgets.QPushButton):
            action = button.property("action")
            if action:
                button.clicked.connect(lambda _, a=action: self.run_bot(a))
        self.main_window.settings_btn.clicked.connect(self.open_settings)
        
        if hasattr(self.main_window, 'update_btn'):
            self.main_window.update_btn.clicked.connect(self.check_for_updates)

    def check_updates_on_start(self):
        """Проверяет обновления при запуске приложения"""
        threading.Thread(target=self._auto_check_updates, daemon=True).start()

    def _auto_check_updates(self):
        """Автоматическая проверка обновлений при старте"""
        if self.updater.check_for_updates():
            print(f"[Обновление] Доступна новая версия: {self.updater.latest_version}")
            self.show_update_notification(self.updater.latest_version)
        else:
            print("[Обновление] У вас актуальная версия")

    def check_for_updates(self):
        """Ручная проверка обновлений"""
        def update_check():
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            try:
                if self.updater.check_for_updates():
                    self.show_update_dialog(self.updater.latest_version)
                else:
                    QtWidgets.QMessageBox.information(
                        self.main_window, 
                        "Проверка обновлений", 
                        "У вас актуальная версия программы!"
                    )
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self.main_window, 
                    "Ошибка", 
                    f"Не удалось проверить обновления: {e}"
                )
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()

        threading.Thread(target=update_check, daemon=True).start()

    @QtCore.pyqtSlot(str)
    def show_update_notification(self, new_version):
        """Показывает уведомление о доступном обновлении"""
        reply = QtWidgets.QMessageBox.question(
            self.main_window,
            "Доступно обновление",
            f"Доступна новая версия {new_version}. Хотите обновить программу сейчас?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.install_update()

    def show_update_dialog(self, new_version):
        """Показывает диалог обновления"""
        reply = QtWidgets.QMessageBox.question(
            self.main_window,
            "Обновление доступно",
            f"Найдена новая версия: {new_version}\n\nУстановить обновление?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.install_update()

    def install_update(self):
        """Устанавливает обновление"""
        def install_thread():
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            progress = None
            try:
                progress = QtWidgets.QProgressDialog(
                    "Установка обновления...", "Отмена", 0, 100, self.main_window
                )
                progress.setWindowTitle("Обновление")
                progress.setWindowModality(QtCore.Qt.WindowModal)
                progress.show()
                
                def update_progress(value):
                    progress.setValue(value)
                    QtWidgets.QApplication.processEvents()
                
                if self.updater.download_and_install_update(progress_callback=update_progress):
                    if progress:
                        progress.close()
                    QtWidgets.QMessageBox.information(
                        self.main_window,
                        "Обновление завершено",
                        "Обновление успешно установлено! Программа будет перезапущена."
                    )
                    self.restart_application()
                else:
                    if progress:
                        progress.close()
                    QtWidgets.QMessageBox.warning(
                        self.main_window,
                        "Ошибка",
                        "Не удалось установить обновление. Попробуйте позже."
                    )
                    
            except Exception as e:
                if progress:
                    progress.close()
                QtWidgets.QMessageBox.warning(
                    self.main_window,
                    "Ошибка",
                    f"Ошибка при установке обновления: {e}"
                )
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()

        threading.Thread(target=install_thread, daemon=True).start()

    def restart_application(self):
        """Перезапускает приложение"""
        subprocess.Popen([sys.executable] + sys.argv)
        self.app.quit()

    def run_bot(self, bot_name):
        bots_map = {
            "oranges": oranges,
            "lumberjack": lumberjack,
            "mine": mine,
            "quarry": quarry,
            "captcha": captcha,
            "mushrooms": mushrooms,
        }
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
        try:
            with open("settings.ini", "w", encoding="utf-8") as f:
                f.write(f"delay={delay}\n")
                f.write(f"key={key}\n")
        except Exception as e:
            print(f"[Ошибка] Не удалось сохранить настройки: {e}")

    def open_settings(self):
        if not self.settings_window or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow()
            try:
                with open("settings.ini", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("delay="):
                            self.settings_window.delay_input.setText(line.strip().split("=", 1)[1])
                        elif line.startswith("key="):
                            self.settings_window.key_input.setText(line.strip().split("=", 1)[1])
            except FileNotFoundError:
                pass
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