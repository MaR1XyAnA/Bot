try:
    import tkinter as tk
    import threading
    import time
    import keyboard
    import pyautogui
    from PIL import ImageGrab
    import cv2
    import numpy as np
    import os

    print("Все модули успешно импортированы!")
except ImportError as e:
    print(f"Ошибка импорта модуля: {e}")
