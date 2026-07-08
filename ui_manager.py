# ui_manager.py

from PyQt5 import QtWidgets, QtCore, QtGui
import updater
from legal_data import get_all_codes

class PinnedWindow(QtWidgets.QWidget):
    """Отдельное окно для закрепленной статьи."""
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(150, 150, 400, 300)

        # Делаем окно полупрозрачным, без рамки и поверх всех окон
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)

        # Создаем "тело" окна с фоном и скругленными углами
        body = QtWidgets.QFrame(self)
        body.setStyleSheet("""
            background-color: #2b2b2b;
            border-radius: 8px;
            border: 1px solid #555;
        """)
        body_layout = QtWidgets.QVBoxLayout(body)

        # --- Верхняя панель для перетаскивания и закрытия ---
        top_bar = QtWidgets.QFrame()
        top_bar_layout = QtWidgets.QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-weight: bold; padding: 5px;")

        close_button = QtWidgets.QPushButton("✕")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("border-radius: 12px; font-weight: bold;")
        close_button.clicked.connect(self.close)

        top_bar_layout.addWidget(title_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(close_button)

        text_edit = QtWidgets.QTextEdit(self)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("background-color: #2b2b2b; border: none;")
        text_edit.setHtml(content)
        
        body_layout.addWidget(top_bar)
        body_layout.addWidget(text_edit)

        # Добавляем виджет для изменения размера в правый нижний угол
        sizegrip = QtWidgets.QSizeGrip(self)
        body_layout.addWidget(sizegrip, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)

        layout.addWidget(body)

        # --- Логика для перетаскивания окна ---
        self.drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()
            event.accept()

class App(QtWidgets.QMainWindow):
    def __init__(self, app_version):
        super().__init__()

        self.setWindowTitle("Помощник для госслужащих RMRP")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(600, 400)
        self.app_version = app_version
        # Чтобы установить иконку, раскомментируйте строку ниже и укажите путь к файлу .ico или .png
        # self.setWindowIcon(QtGui.QIcon('path/to/your/icon.png'))

        self.all_codes = get_all_codes()
        self.current_code_name = ""
        self.current_article_key = None
        self.current_code_of_selected_article = "" # Для корректной работы закрепления
        self.pinned_windows = [] # Список для хранения открытых закрепленных окон

        self.create_widgets()
        self.on_tab_change()

    def create_widgets(self):
        # --- Основной виджет и главный layout ---
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # --- Левая колонка (Кодексы) ---
        codes_groupbox = QtWidgets.QGroupBox("Законодательство")
        codes_layout = QtWidgets.QVBoxLayout(codes_groupbox)
        self.codes_listwidget = QtWidgets.QListWidget()
        self.codes_listwidget.addItems(self.all_codes.keys())
        self.codes_listwidget.currentItemChanged.connect(self.on_code_selected)
        
        update_button = QtWidgets.QPushButton("Проверить обновления")
        update_button.clicked.connect(self.run_update_check)

        codes_layout.addWidget(self.codes_listwidget)
        codes_layout.addWidget(update_button)

        # --- Центральная колонка (Статьи) ---
        articles_groupbox = QtWidgets.QGroupBox("Статьи")
        articles_layout = QtWidgets.QVBoxLayout(articles_groupbox)
        self.search_entry = QtWidgets.QLineEdit()
        self.search_entry.setPlaceholderText("Глобальный поиск по всем разделам...")
        self.search_entry.textChanged.connect(self.filter_articles)
        self.articles_listbox = QtWidgets.QListWidget()
        self.articles_listbox.currentItemChanged.connect(self.show_article_details)
        articles_layout.addWidget(self.search_entry)
        articles_layout.addWidget(self.articles_listbox)

        # --- Правая колонка (Описание) ---
        self.details_groupbox = QtWidgets.QGroupBox("Описание статьи")
        details_layout = QtWidgets.QVBoxLayout()
        self.details_groupbox.setLayout(details_layout)

        self.pin_button = QtWidgets.QPushButton("📌 Закрепить")
        self.pin_button.clicked.connect(self.pin_article_window)
        self.details_text = QtWidgets.QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QtGui.QFont("Arial", 11))
        details_layout.addWidget(self.pin_button)
        details_layout.addWidget(self.details_text)

        # --- Сборка главного layout ---
        main_layout.addWidget(codes_groupbox, 1)
        main_layout.addWidget(articles_groupbox, 2)
        main_layout.addWidget(self.details_groupbox, 3)

    def on_tab_change(self, index=None):
        """Вызывается при первом запуске для инициализации."""
        if self.codes_listwidget.count() > 0:
            self.codes_listwidget.setCurrentRow(0)

    def on_code_selected(self, current_item, previous_item):
        """Обработчик выбора кодекса в левом списке."""
        if not current_item:
            return
        self.current_code_name = current_item.text()
        self.search_entry.clear()
        self.load_articles_to_list()
        self.details_text.clear()

    def load_articles_to_list(self, articles_dict=None):
        """Загружает статьи в Listbox."""
        self.articles_listbox.clear()

        if articles_dict is None:
            articles_dict = self.all_codes.get(self.current_code_name, {})

        for article_key in articles_dict:
            item = QtWidgets.QListWidgetItem(article_key)
            # Сохраняем в элементе данные о его принадлежности к кодексу
            item.setData(QtCore.Qt.UserRole, (self.current_code_name, article_key))
            self.articles_listbox.addItem(item)

    def show_article_details(self, current_item, previous_item):
        """Отображает детали выбранной статьи."""
        if not current_item:
            self.current_article_key = None
            self.details_text.clear()
            return

        # Получаем данные, сохраненные в элементе списка (имя кодекса, ключ статьи)
        item_data = current_item.data(QtCore.Qt.UserRole)
        if not item_data: return # На случай, если данных нет
        
        code_name, self.current_article_key = item_data
        self.current_code_of_selected_article = code_name # Сохраняем для кнопки "Закрепить"
        code = self.all_codes.get(code_name, {})
        details = code.get(self.current_article_key, {"title": "Не найдено", "description": "Статья не найдена."})

        # Формируем текст для вывода с учетом темной темы
        title_html = f"<b style='color: #e0e0e0; font-size: 14px;'>{details.get('title', 'Без названия')}</b>"
        description_html = details.get('description', 'Описание отсутствует.').replace('\n', '<br>')
        
        # Используем светлый цвет для текста
        full_text = f"<div style='color: #d0d0d0;'>{title_html}<hr>{description_html}</div>"

        self.details_text.setHtml(full_text)

    def filter_articles(self, *args):
        """Фильтрует список статей по всем кодексам."""
        search_query = self.search_entry.text().lower()

        # Если поиск пуст, возвращаемся к обычному режиму просмотра вкладок
        if not search_query:
            self.codes_listwidget.setEnabled(True) # Включаем список кодексов
            self.load_articles_to_list() # Загружаем статьи для текущей вкладки
            return

        # Если поиск активен, ищем по всем кодексам
        self.codes_listwidget.setEnabled(False) # Отключаем список кодексов на время поиска
        self.articles_listbox.clear()

        for code_name, articles in self.all_codes.items():
            for key, value in articles.items():
                if (search_query in key.lower() or 
                    search_query in value.get("title", "").lower() or 
                    search_query in value.get("description", "").lower()):
                    # Создаем элемент списка с текстом, включающим название кодекса
                    display_text = f"[{code_name[:3].upper()}] {key}: {value.get('title', '')}"
                    item = QtWidgets.QListWidgetItem(display_text)
                    # Сохраняем в элементе полные данные для его идентификации
                    item.setData(QtCore.Qt.UserRole, (code_name, key))
                    self.articles_listbox.addItem(item)

    def pin_article_window(self):
        """Создает новое окно с текстом статьи, которое будет поверх всех окон."""
        if not self.current_article_key:
            return

        title = f"{self.current_code_of_selected_article} - {self.current_article_key}"
        content = self.details_text.toHtml()

        # Создаем и показываем окно
        pinned_win = PinnedWindow(title, content)
        self.pinned_windows.append(pinned_win)
        pinned_win.show()

    def run_update_check(self):
        """Запускает проверку обновлений."""
        updater.check_for_updates(self.app_version, self)
