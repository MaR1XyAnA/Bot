import os
from git import Repo
from PyQt5.QtWidgets import QMessageBox

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
        QMessageBox.critical(None, "Ошибка", f"Не удалось обновить репозиторий: {e}")
        raise
