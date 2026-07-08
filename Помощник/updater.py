# updater.py

import sys
import os
import requests
import subprocess
from PyQt5 import QtWidgets, QtCore

# --- НАСТРОЙКИ ---
# !!! ВАЖНО: Замените на свои данные перед сборкой .exe !!!
GITHUB_REPO_OWNER = "YourGitHubUsername"
GITHUB_REPO_NAME = "YourRepoName"
# -----------------

API_URL = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"

def check_for_updates(current_version, parent_window):
    """Проверяет наличие обновлений на GitHub."""
    try:
        # Отключаем SSL верификацию для простоты, но в проде лучше настроить сертификаты
        response = requests.get(API_URL, verify=False)
        response.raise_for_status()  # Вызовет исключение для плохих ответов (4xx или 5xx)
        latest_release = response.json()
        latest_version = latest_release.get("tag_name", "0.0.0").lstrip('v')
        current_version = current_version.lstrip('v')

        # Простое сравнение версий. Для сложных случаев (1.10 > 1.9) нужна библиотека packaging
        if latest_version > current_version:
            msg_box = QtWidgets.QMessageBox(parent_window)
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.setText(f"Доступна новая версия: {latest_version}!\nВаша версия: {current_version}.\n\nХотите обновиться?")
            msg_box.setWindowTitle("Обновление")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            reply = msg_box.exec_()

            if reply == QtWidgets.QMessageBox.Yes:
                download_and_apply_update(latest_release, parent_window)
        else:
            QtWidgets.QMessageBox.information(parent_window, "Обновление", "У вас установлена последняя версия.")

    except requests.exceptions.RequestException as e:
        QtWidgets.QMessageBox.warning(parent_window, "Ошибка", f"Не удалось проверить обновления:\n{e}")
    except Exception as e:
        QtWidgets.QMessageBox.critical(parent_window, "Критическая ошибка", f"Произошла непредвиденная ошибка:\n{e}")


def download_and_apply_update(release_data, parent_window):
    """Скачивает и применяет обновление."""
    assets = release_data.get("assets", [])
    exe_asset = None
    for asset in assets:
        if asset.get("name", "").endswith(".exe"):
            exe_asset = asset
            break

    if not exe_asset:
        QtWidgets.QMessageBox.critical(parent_window, "Ошибка", "Не найден .exe файл в последнем релизе на GitHub.")
        return

    download_url = exe_asset["browser_download_url"]
    new_exe_name = "RMRP_Helper_new.exe"
    old_exe_name = os.path.basename(sys.executable)

    try:
        progress = QtWidgets.QProgressDialog("Скачивание обновления...", "Отмена", 0, 100, parent_window)
        progress.setWindowTitle("Обновление")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        with requests.get(download_url, stream=True, verify=False) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0
            with open(new_exe_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if progress.wasCanceled():
                        return
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress.setValue(int((downloaded_size / total_size) * 100))
        progress.setValue(100)

        script = f"""
@echo off
echo Ожидание закрытия приложения...
timeout /t 2 /nobreak > NUL
del "{old_exe_name}"
rename "{new_exe_name}" "{old_exe_name}"
start "" "{old_exe_name}"
del "%~f0"
"""
        with open("update.bat", "w", encoding="cp866") as f:
            f.write(script)

        subprocess.Popen("update.bat", shell=True)
        QtWidgets.QApplication.quit()

    except Exception as e:
        QtWidgets.QMessageBox.critical(parent_window, "Ошибка обновления", f"Не удалось скачать или применить обновление:\n{e}")