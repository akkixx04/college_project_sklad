import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath


# Класс для логотипа
class CircleLogo(QLabel):
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
    def __init__(self, title, items):
        super().__init__()
        self.title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QPushButton(f"▶  {self.title}")
        self.button.setCheckable(True)
        self.button.setStyleSheet("""
            QPushButton {
                padding: 15px;
                text-align: left;
                background-color: #AAAAAA;  /* более светлый цвет */
                color: black;
                font-size: 18px;             /* крупнее */
                font-weight: bold;           /* жирный */
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #999999;
            }
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
                    background-color: #CCCCCC;  /* светлее */
                    color: black;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #BBBBBB;
                }
            """)
            sub_layout.addWidget(btn)

        self.submenu.setVisible(False)
        layout.addWidget(self.submenu)
        self.button.clicked.connect(self.toggle)

    def toggle(self):
        state = self.button.isChecked()
        self.submenu.setVisible(state)
        self.button.setText(f"▼  {self.title}" if state else f"▶  {self.title}")

# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Складской учет")
        self.setStyleSheet("background-color: white;")

        central = QWidget()
        main_layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        # Боковая панель
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("background-color: #E5E5E5;") 
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        logo = CircleLogo("images/box.jpg", size=120)
        sidebar_layout.addWidget(logo, alignment=Qt.AlignLeft)

        # Прокручиваемая область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Главное меню
        btn_main = QPushButton("Главное меню")
        btn_main.setStyleSheet("""
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
            QPushButton:hover {
                background-color: #999999;
            }
        """)
        scroll_layout.addWidget(btn_main)

        # Разделы
        refs = ExpandableSection("Справочники", [
            "Номенклатура", "Категории номенклатуры", "Единицы измерения",
            "Склады", "Сотрудники", "Контрагенты"
        ])
        scroll_layout.addWidget(refs)

        docs = ExpandableSection("Документы", [
            "Оприходование", "Расход", "Перемещение"
        ])
        scroll_layout.addWidget(docs)

        reports = ExpandableSection("Отчёты", [
            "Остатки на складах", "Движение по номенклатуре", "Оборотная ведомость"
        ])
        scroll_layout.addWidget(reports)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        sidebar_layout.addWidget(scroll)

        # Выход
        exit_btn = QPushButton("Выход")
        exit_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                text-align: center;
                background-color: #AAAAAA;
                color: black;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #999999;
            }
        """)
        exit_btn.clicked.connect(QApplication.quit)
        sidebar_layout.addWidget(exit_btn)

        # Центральная область
        self.pages = QStackedWidget()
        page = QLabel("Пустое окно")
        page.setAlignment(Qt.AlignCenter)
        page.setStyleSheet("background-color: white; font-size: 20px; font-weight: bold; color: black;")
        self.pages.addWidget(page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)


# запуск
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    app.exec()
