import tkinter as tk
from tkinter import messagebox

class BotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Control Panel")
        self.root.geometry("400x300")

        # Заголовок
        self.label = tk.Label(root, text="Управление ботом", font=("Arial", 16))
        self.label.pack(pady=10)

        # Кнопка запуска бота
        self.start_button = tk.Button(root, text="Запустить бота", command=self.start_bot, width=20)
        self.start_button.pack(pady=10)

        # Кнопка остановки бота
        self.stop_button = tk.Button(root, text="Остановить бота", command=self.stop_bot, width=20)
        self.stop_button.pack(pady=10)

        # Кнопка выхода
        self.exit_button = tk.Button(root, text="Выход", command=self.exit_app, width=20)
        self.exit_button.pack(pady=10)

    def start_bot(self):
        # Логика запуска бота
        messagebox.showinfo("Информация", "Бот запущен!")

    def stop_bot(self):
        # Логика остановки бота
        messagebox.showinfo("Информация", "Бот остановлен!")

    def exit_app(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()
