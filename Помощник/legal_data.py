# legal_data.py

import json
from pathlib import Path

def load_legal_data():
    """Загружает все кодексы из JSON-файла."""
    try:
        # Ищем файл legal_codes.json в той же директории, где находится скрипт
        path = Path(__file__).parent / "legal_codes.json"
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as e:
        print(f"Ошибка загрузки данных: {e}")
        return {"Ошибка": {"Файл не найден": {"title": "Файл legal_codes.json не найден", "description": "Убедитесь, что файл legal_codes.json находится в той же папке, что и скрипт."}}}
    except json.JSONDecodeError as e:
        # Эта ошибка возникает, если файл пустой или содержит некорректный JSON
        print(f"Ошибка чтения JSON: {e}")
        return {"Ошибка": {"Неверный формат": {"title": "Файл legal_codes.json пуст или поврежден", "description": "Проверьте содержимое файла. Он должен начинаться с символа '{'."}}}

# Загружаем данные один раз при импорте модуля
LEGAL_DATA = load_legal_data()

def get_all_codes():
    """Возвращает словарь со всеми кодексами и их статьями."""
    return LEGAL_DATA
