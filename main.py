import sys
import db
from functools import partial
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QFont

# --- Экран загрузки ---
class SplashScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Полноэкранный splash
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #F9F9F9;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Заголовок
        title = QLabel("Складской учет")
        title.setFont(QFont("Arial", 48, QFont.Bold))
        title.setStyleSheet("color: black;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Надпись "Загрузка" поменьше
        self.loading_label = QLabel("Загрузка")
        self.loading_label.setFont(QFont("Arial", 16))
        self.loading_label.setStyleSheet("color: black;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_label)

        # Прогресс-бар с тонкой границей
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(20)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid black;
                background-color: #BBBBBB;
            }
            QProgressBar::chunk {
                background-color: #999999;
            }
        """)
        layout.addWidget(self.progress)

        # Таймер для имитации загрузки
        self.progress_value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(20)

    def update_progress(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            self.close()
            # Показ главного окна после завершения splash
            self.main_window.showFullScreen()
            self.main_window.setFixedSize(self.main_window.size())  # фиксируем размер

# --- Логотип ---
class Logo(QLabel):
    def __init__(self, image_path, size=120, border_width=2):
        super().__init__()
        pix = QPixmap(image_path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        circle = QPixmap(size, size)
        circle.fill(Qt.transparent)
        painter = QPainter(circle)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pix)
        pen = painter.pen()
        pen.setWidth(border_width)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(border_width//2, border_width//2, size-border_width, size-border_width)
        painter.end()
        self.setPixmap(circle)
        self.setFixedSize(size, size)

# --- Выпадающая секция бокового меню ---
class ExpandableSection(QWidget):
    def __init__(self, title, items, main_window):
        super().__init__()
        self.main_window = main_window
        self.title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QPushButton(f"▶  {self.title}")
        self.button.setCheckable(True)
        self.button.setStyleSheet("""
            QPushButton {
                padding: 15px;
                text-align: left;
                background-color: #AAAAAA;
                color: black;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #999999; }
        """)
        layout.addWidget(self.button)

        self.submenu = QWidget()
        sub_layout = QVBoxLayout(self.submenu)
        sub_layout.setContentsMargins(30, 0, 0, 0)

        self.sub_buttons = []
        for name in items:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    text-align: left;
                    background-color: #CCCCCC;
                    color: black;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #BBBBBB; }
            """)
            sub_layout.addWidget(btn)
            btn.clicked.connect(partial(self.open_page, name))
            self.sub_buttons.append(btn)

        self.submenu.setVisible(False)
        layout.addWidget(self.submenu)
        self.button.clicked.connect(self.toggle)

    def toggle(self):
        state = self.button.isChecked()
        self.submenu.setVisible(state)
        self.button.setText(f"▼  {self.title}" if state else f"▶  {self.title}")

    def open_page(self, page_name):
        # Сброс подсветки всех кнопок
        for btn in self.sub_buttons:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    text-align: left;
                    background-color: #CCCCCC;
                    color: black;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #BBBBBB; }
            """)
        # Подсветка текущей
        for btn in self.sub_buttons:
            if btn.text() == page_name:
                btn.setStyleSheet("""
                    QPushButton {
                        padding: 10px;
                        text-align: left;
                        background-color: #999999;
                        color: black;
                        font-size: 14px;
                        font-weight: bold;
                        border: none;
                        border-radius: 4px;
                    }
                """)
                break

        if page_name in self.main_window.pages_dict:
            self.main_window.pages.setCurrentWidget(self.main_window.pages_dict[page_name])
            widget = self.main_window.pages_dict[page_name]
            if hasattr(widget, "load_data"):
                widget.load_data()
        else:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setAlignment(Qt.AlignCenter)
            label = QLabel(page_name)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")
            layout.addWidget(label)
            self.main_window.pages.addWidget(page)
            self.main_window.pages_dict[page_name] = page
            self.main_window.pages.setCurrentWidget(page)

# --- Универсальный класс таблицы ---
class TablePage(QWidget):
    def __init__(self, title, headers, data_loader):
        super().__init__()
        self.data_loader = data_loader
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; margin: 20px; color: black;")
        layout.addWidget(title_label)

        self.table = QTableWidget()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 16px;
                gridline-color: #333;
                background-color: #F9F9F9;
            }
            QHeaderView::section {
                background-color: #DDDDDD;
                font-weight: bold;
                font-size: 16px;
                color: black;
                border: 1px solid #888;
            }
            QTableWidget::item {
                border: 1px solid #AAA;
            }
        """)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        layout.addWidget(self.table)
        QTimer.singleShot(0, self.load_data)

    def load_data(self):
        rows = self.data_loader()
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled)
                item.setForeground(Qt.black)
                self.table.setItem(row_index, col_index, item)
        self.table.resizeRowsToContents()
        total_width = self.width() - 40
        if self.table.columnCount() > 0:
            col_width = total_width // self.table.columnCount()
            for i in range(self.table.columnCount()):
                self.table.setColumnWidth(i, col_width)

# --- Главное окно ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Складской учет")
        self.setStyleSheet("background-color: white;")
        self.pages_dict = {}

        central = QWidget()
        main_layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        # Боковая панель
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #E5E5E5;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        logo = Logo("images/box.jpg", size=120)
        sidebar_layout.addWidget(logo, alignment=Qt.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        btn_main = QPushButton("Главное меню")
        btn_main.setStyleSheet("""
            QPushButton { padding: 15px; text-align: left; background-color: #AAAAAA;
                color: black; font-size: 18px; font-weight: bold; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #999999; }
        """)
        scroll_layout.addWidget(btn_main)
        btn_main.clicked.connect(lambda: self.pages.setCurrentWidget(self.pages_dict["Главная"]))

        refs = ExpandableSection("Справочники", [
            "Номенклатура", "Категории номенклатуры", "Единицы измерения",
            "Склады", "Сотрудники", "Контрагенты"
        ], self)
        docs = ExpandableSection("Документы", [
            "Оприходование", "Расход", "Перемещение"
        ], self)
        reports = ExpandableSection("Отчёты", [
            "Остатки на складах", "Движение по номенклатуре", "Оборотная ведомость"
        ], self)
        scroll_layout.addWidget(refs)
        scroll_layout.addWidget(docs)
        scroll_layout.addWidget(reports)
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        sidebar_layout.addWidget(scroll)

        exit_btn = QPushButton("Выход")
        exit_btn.setStyleSheet("""
            QPushButton { padding: 15px; text-align: center; background-color: #AAAAAA;
                color: black; font-size: 18px; font-weight: bold; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #999999; }
        """)
        exit_btn.clicked.connect(QApplication.quit)
        sidebar_layout.addWidget(exit_btn)

        # Страницы
        self.pages = QStackedWidget()

        placeholder = QWidget()
        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.setAlignment(Qt.AlignCenter)
        placeholder_label = QLabel("Главная")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")
        placeholder_layout.addWidget(placeholder_label)
        self.pages.addWidget(placeholder)
        self.pages_dict["Главная"] = placeholder

        # Таблицы
        self.units_page = TablePage("Единицы измерения", ["ID", "Наименование", "Код"], db.get_units)
        self.pages.addWidget(self.units_page)
        self.pages_dict["Единицы измерения"] = self.units_page

        self.categories_page = TablePage("Категории номенклатуры", ["ID", "Наименование", "Описание"], db.get_categories)
        self.pages.addWidget(self.categories_page)
        self.pages_dict["Категории номенклатуры"] = self.categories_page

        self.nomenclature_page = TablePage("Номенклатура", ["ID", "Наименование", "ID категории", "ID единицы", "Артикул", "Описание"], db.get_nomenclature)
        self.pages.addWidget(self.nomenclature_page)
        self.pages_dict["Номенклатура"] = self.nomenclature_page

        self.employees_page = TablePage("Сотрудники", ["Фамилия", "Имя", "Отчество", "Должность", "Телефон", "Email"], db.get_employees)
        self.pages.addWidget(self.employees_page)
        self.pages_dict["Сотрудники"] = self.employees_page

        self.contractors_page = TablePage("Контрагенты", ["ID", "Наименование", "Тип", "Менеджер", "Телефон", "Email", "Адрес"], db.get_contractors)
        self.pages.addWidget(self.contractors_page)
        self.pages_dict["Контрагенты"] = self.contractors_page

        self.warehouses_page = TablePage("Склады", ["ID", "Наименование", "Адрес", "Вместимость (м²)", "Ответственный"], db.get_warehouses)
        self.pages.addWidget(self.warehouses_page)
        self.pages_dict["Склады"] = self.warehouses_page

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

# --- Запуск приложения ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    splash = SplashScreen(window)
    splash.show()
    sys.exit(app.exec())
