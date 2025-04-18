import tkinter as tk
from tkinter import messagebox
import threading
import time
import keyboard  # Библиотека для эмуляции нажатий клавиш
import pyautogui  # Для эмуляции нажатий мыши
from PIL import ImageGrab  # Для захвата экрана
import cv2  # Для обработки изображений
import numpy as np  # Для работы с массивами
import os  # Для работы с файловой системой
import sys
import requests  # Для автообновления

# Текущая версия скрипта
current_version = "v1.0.0"  # Обновляйте вручную при релизе

def check_for_update():
    """
    Проверяет наличие новой версии на GitHub и обновляет файлы через git, если доступна.
    """
    repo_url = "https://github.com/MaR1XyAnA/Bot.git"
    local_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        # Проверяем, установлен ли git
        if os.system("git --version") != 0:
            print("Git не установлен. Автообновление невозможно.")
            return

        # Если директория .git есть, делаем pull, иначе clone
        if os.path.exists(os.path.join(local_dir, ".git")):
            print("Проверяем обновления через git pull...")
            res = os.system(f'git -C "{local_dir}" pull')
            if res == 0:
                print("Обновление завершено. Перезапустите программу для применения изменений.")
            else:
                print("Ошибка при выполнении git pull.")
        else:
            print("Клонируем репозиторий заново...")
            res = os.system(f'git clone "{repo_url}" "{local_dir}"')
            if res == 0:
                print("Репозиторий успешно склонирован. Перезапустите программу.")
            else:
                print("Ошибка при выполнении git clone.")
        # Можно добавить messagebox, если нужно GUI-уведомление
    except Exception as e:
        print(f"Ошибка при автообновлении через git: {e}")

# Проверка обновлений при запуске
check_for_update()

class FishingBot:
    def __init__(self):
        self.running = False
        self.hook_template_path = "hook_template.png"  # Путь к шаблону крючка
        self.hook_position = None  # Координаты крючка

        # Проверяем текущую рабочую директорию
        print(f"Текущая рабочая директория: {os.getcwd()}")

        # Загружаем шаблон, если он существует
        if os.path.exists(self.hook_template_path):
            print(f"Путь к шаблону: {os.path.abspath(self.hook_template_path)}")  # Отладочный вывод пути
            self.hook_template = cv2.imread(self.hook_template_path, cv2.IMREAD_COLOR)
            if self.hook_template is not None:
                self.hook_template = cv2.cvtColor(self.hook_template, cv2.COLOR_BGR2RGB)  # Преобразуем в RGB
                print("Шаблон крючка успешно загружен.")
            else:
                print(f"Ошибка: Не удалось загрузить шаблон из {self.hook_template_path}. Проверьте формат файла.")
                raise FileNotFoundError(f"Файл найден, но не удалось загрузить шаблон из {self.hook_template_path}. Проверьте формат файла.")
        else:
            print(f"Шаблон крючка ({self.hook_template_path}) не найден. Убедитесь, что файл существует.")
            self.hook_template = None

    def save_screenshot(self, folder="screenshots"):
        # Создаем папку, если она не существует
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Делаем скриншот всей области экрана
        screenshot = ImageGrab.grab()
        filepath = os.path.join(folder, "screenshot.png")
        screenshot.save(filepath)
        print(f"Скриншот сохранен: {filepath}")

    def save_area_screenshot(self, bbox, folder="screenshots"):
        # Создаем папку, если она не существует
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Делаем скриншот указанной области
        screenshot = ImageGrab.grab(bbox=bbox)
        filepath = os.path.join(folder, "hook_template.png")
        screenshot.save(filepath)
        print(f"Скриншот области сохранен: {filepath}")

        # Проверяем, существует ли файл после сохранения
        if os.path.exists(filepath):
            print(f"Файл шаблона успешно сохранен: {filepath}")
        else:
            print(f"Ошибка: Файл шаблона не был сохранен. Проверьте доступ к папке {folder}.")

        # Выводим абсолютный путь к сохраненному файлу
        print(f"Абсолютный путь к шаблону: {os.path.abspath(filepath)}")

        # Обновляем путь к шаблону и перезагружаем его
        self.hook_template_path = filepath
        self.hook_template = cv2.imread(self.hook_template_path, cv2.IMREAD_COLOR)
        if self.hook_template is not None:
            self.hook_template = cv2.cvtColor(self.hook_template, cv2.COLOR_BGR2RGB)
            print("Шаблон крючка обновлен.")
        else:
            print(f"Ошибка: Не удалось загрузить шаблон из {self.hook_template_path}. Проверьте формат файла.")
            raise FileNotFoundError(f"Не удалось загрузить шаблон из {self.hook_template_path}")

    def analyze_and_click(self):
        if self.hook_template is None:
            print("Шаблон крючка не загружен. Нажмите кнопку для создания шаблона.")
            return

        print("Начинаем поиск крючка в реальном времени...")
        while self.running:
            # Захват области экрана с мини-игрой
            screenshot = ImageGrab.grab(bbox=(767, 487, 810, 527))  # Обновленные координаты области
            screenshot = np.array(screenshot)  # Преобразуем в массив numpy
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)  # Конвертируем в формат OpenCV

            # Сравнение текущего скриншота с шаблоном
            result = cv2.matchTemplate(screenshot, self.hook_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # Визуализация совпадения
            print(f"Максимальное совпадение: {max_val}")

            # Проверка совпадения
            threshold = 0.5  # Уменьшен порог совпадения
            if max_val >= threshold:
                print("Рыбалка пошла")  # Вывод в консоль
                pyautogui.click()  # Нажать левую кнопку мыши
                time.sleep(2)  # Задержка перед следующим поиском
            else:
                print("Крючок не найден. Продолжаем поиск...")

            time.sleep(0.1)  # Небольшая задержка между итерациями

    def analyze_hook_position(self):
        if self.hook_template is None:
            print("Шаблон крючка не загружен. Нажмите кнопку для создания шаблона.")
            return "Шаблон крючка не загружен"

        # Захват области экрана с мини-игрой (обновлены координаты)
        screenshot = ImageGrab.grab(bbox=(767, 487, 810, 527))  # Обновленные координаты области
        screenshot = np.array(screenshot)  # Преобразуем в массив numpy
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)  # Конвертируем в формат OpenCV

        # Обнаружение зеленой зоны
        lower_green = np.array([50, 100, 50])  # Нижняя граница зеленого цвета (HSV)
        upper_green = np.array([70, 255, 255])  # Верхняя граница зеленого цвета (HSV)
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)  # Преобразуем в HSV
        mask = cv2.inRange(hsv, lower_green, upper_green)  # Создаем маску для зеленого цвета

        # Поиск крючка с использованием шаблона
        result = cv2.matchTemplate(screenshot, self.hook_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # Если совпадение выше порога, проверяем пересечение с зеленой зоной
        threshold = 0.8  # Порог совпадения
        if max_val >= threshold:
            hook_x, hook_y = max_loc
            if mask[hook_y:hook_y + self.hook_template.shape[0], hook_x:hook_x + self.hook_template.shape[1]].any():
                return "Крючок в зеленой зоне"
        return "Крючок не в зеленой зоне"

    def find_hook_by_color(self):
        print("Начинаем однократный поиск крючка по цвету...")
        self.running = True

        # Определяем диапазон цвета крючка (пример: белый цвет)
        lower_color = np.array([200, 200, 200])  # Нижняя граница (RGB)
        upper_color = np.array([255, 255, 255])  # Верхняя граница (RGB)

        # Захват области экрана с мини-игрой
        screenshot = ImageGrab.grab(bbox=(767, 487, 810, 527))  # Обновленные координаты области
        screenshot = np.array(screenshot)  # Преобразуем в массив numpy
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)  # Конвертируем в формат OpenCV

        # Создаем маску для заданного диапазона цвета
        mask = cv2.inRange(screenshot, lower_color, upper_color)

        # Поиск координат крючка
        coords = cv2.findNonZero(mask)  # Находим все пиксели, соответствующие маске
        if coords is not None:
            # Сохраняем координаты центра крючка
            x, y, w, h = cv2.boundingRect(coords)
            self.hook_position = (x + w // 2, y + h // 2)
            print(f"Крючок найден по цвету на координатах: {self.hook_position}")
        else:
            self.hook_position = None
            print("Крючок не найден. Проверьте диапазон цвета.")

        self.running = False

    def click_on_hook(self):
        if self.hook_position:
            print(f"Кликаем по крючку на координатах: {self.hook_position}")
            pyautogui.click(self.hook_position[0], self.hook_position[1])
        else:
            print("Координаты крючка не найдены. Выполните поиск крючка.")

    def click_until_in_green_zone(self):
        print("Начинаем нажатия кнопки мыши для поднятия рыбки...")
        self.running = True

        # Определяем диапазон зеленой зоны
        lower_green = np.array([50, 100, 50])  # Нижняя граница зеленого цвета (HSV)
        upper_green = np.array([70, 255, 255])  # Верхняя граница зеленого цвета (HSV)

        while self.running:
            # Захват области экрана с мини-игрой
            screenshot = ImageGrab.grab(bbox=(975, 506, 1041, 578))  # Обновленные координаты области
            screenshot = np.array(screenshot)  # Преобразуем в массив numpy
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)  # Преобразуем в HSV

            # Создаем маску для зеленой зоны
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Поиск координат рыбки (пример: белый цвет)
            lower_fish = np.array([200, 200, 200])  # Нижняя граница (RGB)
            upper_fish = np.array([255, 255, 255])  # Верхняя граница (RGB)
            fish_mask = cv2.inRange(screenshot, lower_fish, upper_fish)
            fish_coords = cv2.findNonZero(fish_mask)

            if fish_coords is not None:
                # Сохраняем координаты центра рыбки
                x, y, w, h = cv2.boundingRect(fish_coords)
                fish_center = (x + w // 2, y + h // 2)

                # Проверяем, находится ли рыбка в зеленой зоне
                if mask[fish_center[1], fish_center[0]] > 0:
                    print("Рыбка в зеленой зоне. Останавливаем нажатия.")
                    break
                else:
                    print("Рыбка не в зеленой зоне. Нажимаем кнопку мыши.")
                    pyautogui.click()  # Нажимаем левую кнопку мыши
            else:
                print("Рыбка не найдена. Продолжаем поиск...")

            time.sleep(0.1)  # Небольшая задержка между итерациями

        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.analyze_and_click, daemon=True).start()  # Запускаем поиск в отдельном потоке
        print("Бот запущен и ищет крючок в реальном времени.")

    def stop(self):
        self.running = False

# Функции для управления ботом
def start_bot():
    if not bot.running:
        threading.Thread(target=bot.start, daemon=True).start()
        messagebox.showinfo("Статус", "Бот запущен!")

def stop_bot():
    bot.stop()
    messagebox.showinfo("Статус", "Бот остановлен!")

# Функция для тестового окна
def test_hook_position():
    result = bot.analyze_hook_position()
    messagebox.showinfo("Результат", result)

# Функция для вызова сохранения скриншота
def save_screenshot():
    bot.save_screenshot()

# Функция для вызова сохранения шаблона
def create_hook_template():
    bbox = (767, 487, 810, 527)  # Обновленные координаты области (x1, y1, x2, y2)
    bot.save_area_screenshot(bbox)

# Функция для запуска поиска крючка по цвету
def start_color_search():
    if not bot.running:
        bot.find_hook_by_color()
        messagebox.showinfo("Статус", "Поиск крючка по цвету завершен!")

# Функция для клика по крючку
def click_hook():
    bot.click_on_hook()

# Функция для запуска нажатий кнопки мыши
def click_fish():
    if not bot.running:
        threading.Thread(target=bot.click_until_in_green_zone, daemon=True).start()
        messagebox.showinfo("Статус", "Нажатия кнопки мыши запущены!")

# Создаем интерфейс
bot = FishingBot()
root = tk.Tk()
root.title("GTA 5 Fishing Bot")

start_button = tk.Button(root, text="Запустить бота", command=start_bot, width=20)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Остановить бота", command=stop_bot, width=20)
stop_button.pack(pady=10)

test_button = tk.Button(root, text="Тест крючка", command=test_hook_position, width=20)
test_button.pack(pady=10)

screenshot_button = tk.Button(root, text="Сделать скриншот", command=save_screenshot, width=20)
screenshot_button.pack(pady=10)

create_template_button = tk.Button(root, text="Создать шаблон крючка", command=create_hook_template, width=20)
create_template_button.pack(pady=10)

color_search_button = tk.Button(root, text="Поиск крючка по цвету", command=start_color_search, width=20)
color_search_button.pack(pady=10)

click_hook_button = tk.Button(root, text="Клик по крючку", command=click_hook, width=20)
click_hook_button.pack(pady=10)

click_fish_button = tk.Button(root, text="Нажимать для рыбки", command=click_fish, width=20)
click_fish_button.pack(pady=10)

root.mainloop()
