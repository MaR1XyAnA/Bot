import tkinter as tk
from tkinter import messagebox
import os
import sys
import requests
import zipfile
import io
import tempfile

current_version = "v1.0.0"  # Обновляйте вручную при релизе

def check_for_update():
    """
    Проверяет наличие новой версии на GitHub и обновляет файлы без использования git.
    После обновления автоматически перезапускает приложение.
    """
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
            try:
                # Сохраняем архив во временный файл, чтобы избежать проблем с памятью
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmpfile:
                    for chunk in requests.get(zip_url, stream=True, timeout=30).iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            tmpfile.write(chunk)
                    tmpfile_path = tmpfile.name
                with zipfile.ZipFile(tmpfile_path, "r") as z:
                    root_folder = z.namelist()[0]
                    for member in z.namelist():
                        if member.endswith('/'):
                            continue
                        filename = os.path.relpath(member, start=root_folder)
                        if filename == ".":
                            continue
                        target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with open(target_path, "wb") as f:
                            f.write(z.read(member))
                os.remove(tmpfile_path)
                print("Обновление завершено. Перезапускаем программу для применения изменений.")
                messagebox.showinfo("Обновление", f"Доступна новая версия: {latest_version}.\nОбновление завершено.\nПрограмма будет перезапущена.")
                python = sys.executable
                os.execl(python, python, *sys.argv)
            except requests.exceptions.RequestException as e:
                print("Ошибка сети при скачивании архива:", e)
                messagebox.showerror("Ошибка обновления", f"Ошибка сети при скачивании архива:\n{e}\nПроверьте подключение к интернету и повторите попытку.")
                return
            except Exception as e:
                print("Ошибка при распаковке архива:", e)
                messagebox.showerror("Ошибка обновления", f"Ошибка при распаковке архива:\n{e}")
                return
        else:
            print("Установлена последняя версия.")
    except Exception as e:
        print(f"Ошибка при автообновлении: {e}")

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
