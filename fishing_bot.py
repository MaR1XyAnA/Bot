import threading
import time
import cv2  # Добавлен импорт OpenCV

class FishingBot:
    def __init__(self, log_callback=None):
        self._running = False
        self._thread = None
        self.log_callback = log_callback or (lambda msg: None)
        self.fish_count = 0  # Новый атрибут для подсчёта рыбы

    def start(self):
        if self._running:
            self.log_callback("Бот уже запущен.")
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.log_callback("Бот запущен.")

    def stop(self):
        if not self._running:
            self.log_callback("Бот не запущен.")
            return
        self._running = False
        self.log_callback("Бот остановлен.")

    def _run(self):
        while self._running:
            # Здесь должна быть логика рыбалки
            self.fish_count += 1  # Увеличиваем счётчик
            self.log_callback(f"Бот ловит рыбу... Всего поймано: {self.fish_count}")

            # Пример использования OpenCV: попытка загрузить изображение
            try:
                img = cv2.imread('sample.jpg')  # Замените на актуальный путь или логику
                if img is not None:
                    self.log_callback("OpenCV: изображение успешно загружено.")
                else:
                    self.log_callback("OpenCV: не удалось загрузить изображение.")
            except Exception as e:
                self.log_callback(f"OpenCV ошибка: {e}")

            time.sleep(2)
