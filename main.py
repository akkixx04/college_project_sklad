import sys
import db
from functools import partial
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

class Logo(QLabel):
    def __init__(self, image_path, size=120, border_width=2):
        super().__init__()
        pix = QPixmap(image_path).scaled(
            size, size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
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

# Выпадающая секция
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

        self.submenu.setVisible(False)
        layout.addWidget(self.submenu)
        self.button.clicked.connect(self.toggle)

    def toggle(self):
        state = self.button.isChecked()
        self.submenu.setVisible(state)
        self.button.setText(f"▼  {self.title}" if state else f"▶  {self.title}")

    def open_page(self, page_name):
        # Страница "Единицы измерения" со своей таблицей
        if page_name == "Единицы измерения":
            self.main_window.pages.setCurrentWidget(self.main_window.units_page)
            self.main_window.units_page.load_data()
            return

        if page_name not in self.main_window.pages_dict:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setAlignment(Qt.AlignCenter)
            label = QLabel(page_name)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")
            layout.addWidget(label)
            self.main_window.pages.addWidget(page)
            self.main_window.pages_dict[page_name] = page

        self.main_window.pages.setCurrentWidget(self.main_window.pages_dict[page_name])

# Единицы измерения
class UnitsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок страницы
        title = QLabel("Единицы измерения")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; margin: 20px; color: black;"
        )
        layout.addWidget(title)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Наименование", "Код"])
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

        total_width = self.width() - 40  
        id_width = 50
        name_width = int(total_width * 0.8)
        code_width = int(total_width * 0.4) - id_width

        self.table.setColumnWidth(0, id_width)     # ID
        self.table.setColumnWidth(1, name_width)   # Наименование
        self.table.setColumnWidth(2, code_width)   # Код

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        QTimer.singleShot(0, self.load_data)

    def load_data(self):
        rows = db.get_units()
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled)
                item.setForeground(Qt.black)
                self.table.setItem(row_index, col_index, item)
        self.table.resizeRowsToContents()

# Главное окно 
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

        # Создаем разделы
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

        self.units_page = UnitsPage()
        self.pages.addWidget(self.units_page)
        self.pages_dict["Единицы измерения"] = self.units_page

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

# Запуск
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    app.exec()
