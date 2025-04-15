import tkinter as tk
from tkinter import messagebox

def on_start():
    messagebox.showinfo("Старт", "Скрипт запущен!")

def on_stop():
    messagebox.showinfo("Стоп", "Скрипт остановлен!")

root = tk.Tk()
root.title("Управление Скриптом")
root.geometry("300x200")
root.configure(bg="#f0f0f0")

label = tk.Label(root, text="Добро пожаловать!", font=("Arial", 14), bg="#f0f0f0")
label.pack(pady=20)

start_btn = tk.Button(root, text="Запустить", command=on_start, width=15, bg="#4CAF50", fg="white")
start_btn.pack(pady=5)

stop_btn = tk.Button(root, text="Остановить", command=on_stop, width=15, bg="#F44336", fg="white")
stop_btn.pack(pady=5)

exit_btn = tk.Button(root, text="Выход", command=root.quit, width=15)
exit_btn.pack(pady=20)

root.mainloop()
