#def run():
    #print("⛏ Бот Карьер запущен!")

import cv2
import numpy as np
import pyautogui
from PIL import Image

def find_image_on_screen(template_path, threshold=0.8):
    # Сделать скриншот экрана
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    # Загрузить шаблон для поиска
    template = cv2.imread(template_path)
    if template is None:
        raise FileNotFoundError(f"Файл {template_path} не найден")
    
    # Поиск шаблона на скриншоте
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    
    if locations[0].size > 0:
        # Найти центр первого совпадения
        y, x = locations[0][0], locations[1][0]
        h, w = template.shape[:2]
        center_x = x + w // 2
        center_y = y + h // 2
        return center_x, center_y
    return None

def click_on_image(template_path, threshold=0.8):
    # Найти изображение на экране
    coords = find_image_on_screen(template_path, threshold)
    
    if coords:
        x, y = coords
        # Переместить курсор к найденному изображению и кликнуть правой кнопкой
        pyautogui.moveTo(x, y)
        pyautogui.rightClick()
        print(f"Изображение найдено! Кликнуто правой кнопкой по координатам: ({x}, {y})")
        return True
    else:
        print("Изображение не найдено")
        return False

def get_delay_from_settings(default=1.0):
    """Чтение задержки из файла настроек"""
    try:
        with open("settings.ini", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("delay="):
                    return float(line.strip().split("=", 1)[1])
    except Exception:
        pass
    return default

def run(stop_flag=None):
    """Запуск поиска и клика по изображению правой кнопкой мыши с задержкой из настроек"""
    template_path = "templates/ore.jpg"  # Путь к искомому изображению
    import time
    delay = get_delay_from_settings(default=1.0)
    while True:
        if stop_flag and stop_flag():
            print("Бот quarry остановлен по запросу.")
            break
        click_on_image(template_path, threshold=0.8)
        delay = get_delay_from_settings(default=1.0)  # перечитываем задержку на каждом цикле
        time.sleep(delay)  # Задержка между попытками

# Использование
if __name__ == "__main__":
    template_path = "templates/ore.jpg"  # Путь к искомому изображению
    
    click_on_image(template_path, threshold=0.8)