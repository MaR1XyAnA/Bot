import os
from git import Repo
from tkinter import messagebox

def auto_update(repo_path, repo_url):
    try:
        if not os.path.exists(repo_path):
            # Клонируем репозиторий, если он не существует
            Repo.clone_from(repo_url, repo_path)
            messagebox.showinfo("Обновление", "Репозиторий успешно клонирован!")
        else:
            # Обновляем существующий репозиторий
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            messagebox.showinfo("Обновление", "Репозиторий успешно обновлён!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось обновить репозиторий: {e}")
