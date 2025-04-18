import tkinter as tk
from tkinter import messagebox
import os
import sys
import requests
import zipfile
import io

current_version = "v1.0.0"  # Обновляйте вручную при релизе

def check_for_update():
    """
    Проверяет наличие новой версии на GitHub и обновляет файлы без использования git.
    """
    # Используем ссылку на репозиторий, но для автообновления нужен API releases/latest
    repo_url = "https://github.com/MaR1XyAnA/Bot.git"
    api_url = "https://api.github.com/repos/MaR1XyAnA/Bot/releases/latest"
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 404:
            print("В репозитории нет опубликованных релизов. Автообновление невозможно.")
            print("Создайте опубликованный релиз (Release) на GitHub, чтобы включить автообновление.")
            return
        latest = response.json()
        if "tag_name" not in latest:
            print("Ошибка: Не удалось получить информацию о релизе.")
            print("Ответ GitHub API:", latest)
            return
        latest_version = latest["tag_name"]
        if latest_version != current_version:
            print(f"Доступна новая версия: {latest_version}. Скачиваем и обновляем файлы...")
            zip_url = latest.get("zipball_url")
            if not zip_url:
                print("Ошибка: Не найден zip-архив для релиза.")
                return
            r = requests.get(zip_url, stream=True)
            if r.status_code != 200:
                print("Ошибка при скачивании архива:", r.status_code)
                return
            z = zipfile.ZipFile(io.BytesIO(r.content))
            for member in z.namelist():
                if member.endswith('/'):
                    continue
                filename = os.path.relpath(member, start=z.namelist()[0])
                if filename == ".":
                    continue
                target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "wb") as f:
                    f.write(z.read(member))
            print("Обновление завершено. Перезапустите программу для применения изменений.")
            messagebox.showinfo("Обновление", f"Доступна новая версия: {latest_version}.\nОбновление завершено.\nПерезапустите программу.")
            sys.exit(0)
        else:
            print("Установлена последняя версия.")
    except Exception as e:
        print(f"Ошибка при автообновлении: {e}")

# Проверка обновлений при запуске
check_for_update()

running = False

def start_bot():
    global running
    running = True
    messagebox.showinfo("Статус", "Бот запущен!")

def stop_bot():
    global running
    running = False
    messagebox.showinfo("Статус", "Бот остановлен!")

root = tk.Tk()
root.title("GTA 5 Fishing Bot")

start_button = tk.Button(root, text="Запустить бота", command=start_bot, width=20)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Остановить бота", command=stop_bot, width=20)
stop_button.pack(pady=10)

root.mainloop()
