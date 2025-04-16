import os
from git import Repo
from PyQt5.QtWidgets import QMessageBox
import logging
import traceback

# Настройка логирования
logging.basicConfig(
    filename="auto_update.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def auto_update(repo_path, repo_url):
    try:
        if not os.path.exists(repo_path):
            Repo.clone_from(repo_url, repo_path)
            QMessageBox.information(None, "Обновление", "Репозиторий успешно клонирован!")
        else:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            QMessageBox.information(None, "Обновление", "Репозиторий успешно обновлён!")
    except Exception as e:
        logging.error(f"Ошибка при обновлении репозитория: {e}\n{traceback.format_exc()}")
        QMessageBox.critical(None, "Ошибка", f"Не удалось обновить репозиторий: {e}")
        raise
