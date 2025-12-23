import sys
from functools import partial

import db
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox, QDateEdit, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QIcon

# Логотип
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

# Выпадающая секция бокового меню
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

# Главная страница — критические остатки и последние операции
class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        self.critical_table = QTableWidget()
        self.critical_table.setColumnCount(4)
        self.critical_table.setHorizontalHeaderLabels([
            "Склад",
            "Номенклатура",
            "Ед. изм.",
            "Остаток"
        ])
        self._style_table(self.critical_table)

        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(5)
        self.operations_table.setHorizontalHeaderLabels(
            ["Дата", "Тип", "Номенклатура", "Кол-во", "Склад"]
        )
        self._style_table(self.operations_table)

        left_layout = QVBoxLayout()

        critical_title = QLabel("Критические остатки по складам")
        critical_title.setAlignment(Qt.AlignCenter)
        critical_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: black;
            margin-bottom: 25px;
            margin-top: 20px;                         
        """)
        left_layout.addWidget(critical_title)
        left_layout.addWidget(self.critical_table)

        right_layout = QVBoxLayout()

        operations_title = QLabel("Последние операции")
        operations_title.setAlignment(Qt.AlignCenter) 
        operations_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: black;
            margin-bottom: 25px;
            margin-top: 20px;                            
        """)
        right_layout.addWidget(operations_title)
        right_layout.addWidget(self.operations_table)

        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)

        content_layout.setStretch(0, 1)
        content_layout.setStretch(1, 1)

        self.load_data()

    def _style_table(self, table):
        table.setSortingEnabled(True)
        table.setStyleSheet("""
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
                color: black;
            }
        """)
        table.verticalHeader().setVisible(False)
        table.setWordWrap(True)
        table.setShowGrid(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)

    def load_data(self):
        crit_rows = db.get_critical_stock()
        self.critical_table.setRowCount(len(crit_rows))
        for r, row in enumerate(crit_rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  
                item.setFlags(Qt.ItemIsEnabled)
                self.critical_table.setItem(r, c, item)

        self.critical_table.resizeRowsToContents() 

        op_rows = db.get_last_operations()
        self.operations_table.setRowCount(len(op_rows))
        for r, row in enumerate(op_rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setFlags(Qt.ItemIsEnabled)

                if c == 1:  
                    if str(value).lower() == "приход":
                        item.setIcon(QIcon(QPixmap("images/plus.png")))
                        item.setForeground(Qt.green)
                    elif str(value).lower() == "расход":
                        item.setIcon(QIcon(QPixmap("images/minus.png")))
                        item.setForeground(Qt.red)

                self.operations_table.setItem(r, c, item)

        self.operations_table.resizeRowsToContents()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()  

# Универсальная страница с таблицей
class TablePage(QWidget):
    def __init__(self, title, headers, data_loader):
        super().__init__()
        self.data_loader = data_loader
        self.table_title = title
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; margin: 20px; color: black;")
        layout.addWidget(title_label)

        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        QTimer.singleShot(0, self.load_data)

        if "Остатки на складах" in title or "Движение по номенклатуре" in title or "Оборотная ведомость" in title:
            search_layout = QHBoxLayout()
            search_layout.addStretch()

            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("Поиск...")
            self.search_edit.setMaximumWidth(300)
            self.search_edit.setMinimumHeight(35)
            self.search_edit.textChanged.connect(self.apply_filter)

            search_layout.addWidget(self.search_edit)
            layout.insertLayout(1, search_layout)
            self.search_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #AAAAAA;
                    color: black;
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QLineEdit:hover {
                    background-color: #999999;
                }
            """)

    def load_data(self):
        rows = self.data_loader()
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled)
                item.setForeground(Qt.black)

                if "Движение по номенклатуре" in getattr(self, "table_title", ""):
                    if self.table.horizontalHeaderItem(col_index).text() == "Тип операции":
                        if str(value).lower() in ["приход", "поступление", "+"]:
                            item.setIcon(QIcon(QPixmap("images/plus.png")))
                        elif str(value).lower() in ["расход", "-", "списание"]:
                            item.setIcon(QIcon(QPixmap("images/minus.png")))

                self.table.setItem(row_index, col_index, item)
        self.table.resizeRowsToContents()

    def apply_filter(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

# Расширенная страница с поддержкой редактирования, добавления и удаления записей справочников
class ReferenceTablePage(TablePage):
    def __init__(self, title, headers, data_loader,
                 table_name, id_field, fields):
        super().__init__(title, headers, data_loader)
        self.table_name = table_name
        self.id_field = id_field
        self.fields = fields
        self._init_top_panel()

    def _init_top_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #E5E5E5;")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")

        for btn in (self.btn_add, self.btn_edit, self.btn_delete):
            btn.setMinimumHeight(35)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #AAAAAA;
                    color: black;
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #999999; }
            """)
            layout.addWidget(btn)

        self.layout().insertWidget(0, panel)
        self.btn_add.clicked.connect(self.add_item)
        self.btn_edit.clicked.connect(self.edit_item)
        self.btn_delete.clicked.connect(self.delete_item)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск...")
        self.search_edit.setMinimumHeight(35)
        self.search_edit.textChanged.connect(self.apply_filter)
        layout.addWidget(self.search_edit)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #AAAAAA;
                color: black;
                font-weight: bold;
                font-size: 16px;
                border-radius: 5px;
            }
            QLineEdit:hover {
                background-color: #999999;
            }
        """)

    # Получение выбранного ID
    def _get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    # Добавление / редактирование
    def add_item(self):
        self._open_form()

    def edit_item(self):
        item_id = self._get_selected_id()
        if not item_id:
            return

        conn = db.get_connection()
        cur = conn.cursor()
        fields_sql = ", ".join(f[0] for f in self.fields)
        cur.execute(f"SELECT {fields_sql} FROM {self.table_name} WHERE {self.id_field}=%s", (item_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        data = dict(zip([f[0] for f in self.fields], row))
        self._open_form(item_id, data)

    # Диалог формы 
    def _open_form(self, item_id=None, data=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование" if item_id else "Добавление")
        dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
        dialog.resize(700, 500)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        layout.addLayout(form)
        font = QFont()
        font.setPointSize(10)

        inputs = {}

        for field_def in self.fields:
            field = field_def[0]
            label = field_def[1]

            if len(field_def) == 3 and isinstance(field_def[2], dict):
                fk = field_def[2]
                combo = QComboBox()
                combo.setFont(font)
                combo.setStyleSheet("background-color: white; color: black;")

                fk_data = self._load_fk_data(fk)
                for fk_id, fk_title in fk_data:
                    combo.addItem(str(fk_title), fk_id)

                if data:
                    index = combo.findData(data.get(field))
                    if index >= 0:
                        combo.setCurrentIndex(index)

                inputs[field] = combo
                form.addRow(label + ":", combo)

            elif len(field_def) == 3 and field_def[2] == "numeric":
                edit = QDoubleSpinBox()
                edit.setRange(0, 10_000_000)
                edit.setDecimals(2)
                edit.setSingleStep(1)
                edit.setSuffix(" м²")
                edit.setFont(font)
                edit.setMinimumHeight(28)
                edit.setStyleSheet("background-color: white; color: black;")

                if data and data.get(field) is not None:
                    edit.setValue(float(data.get(field)))

                inputs[field] = edit
                form.addRow(label + ":", edit)

            else:
                edit = QLineEdit()
                edit.setFont(font)
                edit.setStyleSheet("background-color: white; color: black;")

                if data:
                    edit.setText(str(data.get(field, "")))

                inputs[field] = edit
                form.addRow(label + ":", edit)

        save_btn = QPushButton("Сохранить")
        save_btn.setMinimumHeight(35)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #999999;
                color: black;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #777777; }
        """)
        layout.addWidget(save_btn)
        save_btn.clicked.connect(lambda: self._save_item(dialog, item_id, inputs))
        dialog.exec()

    def _save_item(self, dialog, item_id, inputs):
        values = {}
        conn = db.get_connection()
        
        required_fields = {
            "categories_nomenclature": ["title"],
            "counterparties": ["name"],
            "employees": ["familia", "imya", "position"],
            "nomenclature": ["title", "id_category", "id_unit"],
            "units": ["title"],
            "warehouses": ["title"]
        }
        
        unique_fields = {
            "categories_nomenclature": ["title"],
            "counterparties": ["name", "email"],
            "employees": ["email", "phone"],
            "nomenclature": ["title", "article"],
            "units": ["title", "code_unit"],
            "warehouses": ["title"]
        }

        for field, widget in inputs.items():
            if isinstance(widget, QLineEdit):
                value = widget.text().strip()

            elif isinstance(widget, QComboBox):
                value = widget.currentData()

            elif isinstance(widget, QDateEdit):
                value = widget.date().toPython()

            elif isinstance(widget, QDoubleSpinBox):
                value = widget.value()

            else:
                value = None

            values[field] = value

        # Проверка обязательных полей
        for field in required_fields.get(self.table_name, []):
            if not values.get(field):
                QMessageBox.warning(
                    dialog,
                    "Ошибка заполнения",
                    f"Поле '{field}' обязательно для заполнения."
                )
                return

        # Проверка уникальности
        with conn.cursor() as cur:
            for field in unique_fields.get(self.table_name, []):
                if item_id:
                    cur.execute(
                        f"SELECT COUNT(*) FROM {self.table_name} WHERE {field}=%s AND {self.id_field}<>%s",
                        (values[field], item_id)
                    )
                else:
                    cur.execute(
                        f"SELECT COUNT(*) FROM {self.table_name} WHERE {field}=%s",
                        (values[field],)
                    )
                count = cur.fetchone()[0]
                if count > 0:
                    QMessageBox.warning(dialog, "Ошибка заполнения", f"Значение '{values[field]}' в поле '{field}' уже существует!")
                    return

            fields_sql = ", ".join(values.keys())
            placeholders = ", ".join(["%s"] * len(values))
            if item_id: 
                set_sql = ", ".join([f"{f}=%s" for f in values.keys()])
                cur.execute(
                    f"UPDATE {self.table_name} SET {set_sql} WHERE {self.id_field}=%s",
                    list(values.values()) + [item_id]
                )
            else: 
                cur.execute(
                    f"INSERT INTO {self.table_name} ({fields_sql}) VALUES ({placeholders})",
                    list(values.values())
                )
            conn.commit()

        dialog.accept()  
        self.load_data() 

    # Удаление с подтверждением
    def delete_item(self):
        item_id = self._get_selected_id()
        if not item_id:
            return

        confirm = QMessageBox(self)
        confirm.setWindowTitle("Удаление")
        confirm.setText(f"Вы уверены, что хотите удалить запись {item_id}?")
        confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        yes_button = confirm.button(QMessageBox.Yes)
        no_button = confirm.button(QMessageBox.No)
        yes_button.setText("Да")
        no_button.setText("Нет")
        for btn in [yes_button, no_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #999999;
                    color: black;
                    font-weight: bold;
                    border-radius: 5px;
                    min-width: 80px;
                    min-height: 30px;
                }
                QPushButton:hover { background-color: #777777; }
            """)
        confirm.setStyleSheet("background-color: #CCCCCC; color: black;")

        if confirm.exec() == QMessageBox.Yes:
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {self.table_name} WHERE {self.id_field}=%s", (item_id,))
            conn.commit()
            cur.close()
            conn.close()
            self.load_data()

    def _load_fk_data(self, fk):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT {fk['id']}, {fk['title']} FROM {fk['table']} ORDER BY {fk['title']}")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

# Страница для работы с документами (приход, расход, перемещение)
class DocumentTablePage(TablePage):
    def __init__(self, title, headers, data_loader, doc_type):
        super().__init__(title, headers, data_loader)
        self.doc_type = doc_type

        self.top_panel = QWidget()
        self.top_panel.setStyleSheet("background-color: #E5E5E5;")
        top_layout = QHBoxLayout(self.top_panel)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(5)

        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_process = QPushButton("Провести")
        self.btn_unprocess = QPushButton("Отменить проведение")

        for btn in [self.btn_add, self.btn_edit, self.btn_delete, self.btn_process, self.btn_unprocess]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #AAAAAA;
                    color: black;
                    font-weight: bold;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #999999; }
            """)
            btn.setMinimumHeight(35)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            top_layout.addWidget(btn)

        self.layout().insertWidget(0, self.top_panel)

        self.btn_add.clicked.connect(self.add_document)
        self.btn_edit.clicked.connect(self.edit_document)
        self.btn_delete.clicked.connect(self.delete_document)
        self.btn_process.clicked.connect(self.process_document)
        self.btn_unprocess.clicked.connect(self.unprocess_document)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск...")
        self.search_edit.setMinimumHeight(35)
        self.search_edit.textChanged.connect(self.apply_filter)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #AAAAAA;
                color: black;
                font-weight: bold;
                font-size: 16px;
                border-radius: 5px;
            }
            QLineEdit:hover {
                background-color: #999999;
            }
        """)
        top_layout.addWidget(self.search_edit)

    def load_data(self):
        rows = self.data_loader()
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                if col_index == self.table.columnCount() - 1 and isinstance(value, bool):
                    text = "Проведен" if value else "Не проведен"
                else:
                    text = str(value)

                item = QTableWidgetItem(text)
                item.setFlags(Qt.ItemIsEnabled)
                item.setForeground(Qt.black)
                self.table.setItem(row_index, col_index, item)

        self.table.resizeRowsToContents()

    def get_selected_document_id(self):
        selected = self.table.currentRow()
        if selected < 0:
            return None
        return int(self.table.item(selected, 0).text())

    # Добавление документа 
    def add_document(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление документа")
        dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
        dialog.resize(900, 650)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        layout.addLayout(form)
        font = QFont(); font.setPointSize(10)

        number_input = QLineEdit()
        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        date_input.setDisplayFormat("dd.MM.yyyy")
        date_input.setDate(QDate.currentDate())
        date_input.setFont(font)
        date_input.setStyleSheet("background-color: white; color: black;")
        date_input.setMaximumDate(QDate.currentDate())
        employee_input = QComboBox()

        for w in [number_input, date_input, employee_input]:
            w.setFont(font)
            w.setStyleSheet("background-color: white; color: black;")

        for emp in db.get_employees():
            employee_input.addItem(f"{emp[1]} {emp[2]}", emp[0])

        counterparty_input = QComboBox()
        counterparty_input.setFont(font)
        counterparty_input.setStyleSheet("background-color: white; color: black;")

        for c in db.get_contractors():
            counterparty_input.addItem(c[1], c[0])

        warehouse_input = QComboBox()
        warehouse_from = QComboBox()
        warehouse_to = QComboBox()

        for w in db.get_warehouses():
            warehouse_input.addItem(w[1], w[0])
            warehouse_from.addItem(w[1], w[0])
            warehouse_to.addItem(w[1], w[0])

        nomenclature_table = QTableWidget()
        nomenclature_table.setColumnCount(2)
        nomenclature_table.setHorizontalHeaderLabels(["Номенклатура", "Количество"])
        nomenclature_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        nomenclature_table.setMaximumHeight(220)
        nomenclature_table.setMinimumHeight(180)
        nomenclature_table.setFont(font)
        nomenclature_table.setSelectionBehavior(QTableWidget.SelectRows)
        nomenclature_table.setEditTriggers(QTableWidget.NoEditTriggers)
        nomenclature_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: black;
                border: 1px solid black;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid black;
            }
        """)

        form.addRow("Номер документа:", number_input)
        form.addRow("Дата:", date_input)
        form.addRow("Сотрудник:", employee_input)

        if self.doc_type == 'приход':
            counterparty_input.setFont(font)
            counterparty_input.setStyleSheet("background-color: white; color: black;")
            warehouse_input.setFont(font)
            warehouse_input.setStyleSheet("background-color: white; color: black;")
            form.addRow("Контрагент:", counterparty_input)
            form.addRow("Склад:", warehouse_input)

        elif self.doc_type == "расход":
            warehouse_input.setFont(font)
            warehouse_input.setStyleSheet("background-color: white; color: black;")
            form.addRow("Склад:", warehouse_input)

        elif self.doc_type == "перемещение":
            warehouse_from.setFont(font)
            warehouse_from.setStyleSheet("background-color: white; color: black;")
            warehouse_to.setFont(font)
            warehouse_to.setStyleSheet("background-color: white; color: black;")
            form.addRow("Склад-отправитель:", warehouse_from)
            form.addRow("Склад-получатель:", warehouse_to)

        table_btn_layout = QHBoxLayout()

        btn_add_row = QPushButton("Добавить позицию")
        btn_edit_row = QPushButton("Редактировать позицию")
        btn_delete_row = QPushButton("Удалить позицию")

        def add_row():
            row_dialog = QDialog(); row_dialog.setWindowTitle("Добавить номенклатуру")
            row_dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
            row_layout = QFormLayout(row_dialog)
            nc_combo = QComboBox(); qty_input = QLineEdit()
            nc_combo.setStyleSheet("background-color: white; color: black;")
            nc_combo.setFont(font); qty_input.setFont(font)
            for n in db.get_nomenclature():
                nc_combo.addItem(f"{n[1]} (ед: {n[3]})", n[0])
            row_layout.addRow("Номенклатура:", nc_combo)
            row_layout.addRow("Количество:", qty_input)
            qty_input.setStyleSheet("background-color: white; color: black;")
            save_btn = QPushButton("Сохранить"); row_layout.addWidget(save_btn)
            save_btn.setStyleSheet("background-color: #999999; color: black; font-weight: bold;")

            def accept_row():
                try:
                    qty = float(qty_input.text())
                except ValueError:
                    QMessageBox.warning(row_dialog, "Ошибка", "Количество должно быть числом")
                    return
                row_pos = nomenclature_table.rowCount()
                nomenclature_table.insertRow(row_pos)
                name_item = QTableWidgetItem(nc_combo.currentText())
                name_item.setData(Qt.UserRole, nc_combo.currentData())
                nomenclature_table.setItem(row_pos, 0, name_item)
                nomenclature_table.setItem(row_pos, 1, QTableWidgetItem(str(qty)))
                row_dialog.accept()

            save_btn.clicked.connect(accept_row)
            row_dialog.exec()

        def edit_row_func():
            sel = nomenclature_table.currentRow()
            if sel < 0: return
            current_name = nomenclature_table.item(sel, 0).text()
            current_qty = nomenclature_table.item(sel, 1).text()
            row_dialog = QDialog(); row_dialog.setWindowTitle("Редактировать номенклатуру")
            row_dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
            row_layout = QFormLayout(row_dialog)
            nc_combo = QComboBox(); qty_input = QLineEdit(current_qty)
            nc_combo.setFont(font); qty_input.setFont(font)
            for n in db.get_nomenclature():
                nc_combo.addItem(f"{n[1]} (ед: {n[3]})", n[0])
            for i in range(nc_combo.count()):
                if nc_combo.itemText(i) == current_name:
                    nc_combo.setCurrentIndex(i)
                    break
            row_layout.addRow("Номенклатура:", nc_combo)
            row_layout.addRow("Количество:", qty_input)
            qty_input.setStyleSheet("background-color: white; color: black;")
            nc_combo.setStyleSheet("background-color: white; color: black;")
            save_btn = QPushButton("Сохранить"); row_layout.addWidget(save_btn)
            save_btn.setStyleSheet("background-color: #999999; color: black; font-weight: bold;")

            def accept_row():
                try: qty = float(qty_input.text())
                except: qty = 0
                nomenclature_table.item(sel, 0).setText(nc_combo.currentText())
                nomenclature_table.item(sel, 0).setData(Qt.UserRole, nc_combo.currentData())
                nomenclature_table.item(sel, 1).setText(str(qty))
                row_dialog.accept()

            save_btn.clicked.connect(accept_row)
            row_dialog.exec()

        def delete_row_func():
            sel = nomenclature_table.currentRow()
            if sel >= 0: nomenclature_table.removeRow(sel)

        btn_add_row.clicked.connect(add_row)
        btn_edit_row.clicked.connect(edit_row_func)
        btn_delete_row.clicked.connect(delete_row_func)

        for btn in [btn_add_row, btn_edit_row, btn_delete_row]:
            btn.setStyleSheet("background-color: #AAAAAA; color: black; font-weight: bold;")
            btn.setMinimumHeight(30)
            table_btn_layout.addWidget(btn)

        table_container = QVBoxLayout()
        table_container.addLayout(table_btn_layout)
        table_container.addWidget(nomenclature_table)

        form.addRow("Номенклатура:", table_container)

        comment_input = QLineEdit()
        comment_input.setFont(font)
        comment_input.setStyleSheet("background-color: white; color: black;")
        form.addRow("Комментарий:", comment_input)

        save_btn = QPushButton("Сохранить")
        save_btn.setMinimumHeight(35)
        save_btn.setStyleSheet("background-color: #999999; color: black; font-weight: bold;")

        save_btn.clicked.connect(lambda: self.save_new_document_table(
            dialog, number_input, date_input, employee_input,
            counterparty_input,
            warehouse_input, warehouse_from, warehouse_to,
            nomenclature_table, comment_input
        ))

        layout.addWidget(save_btn)
        dialog.exec()

    def save_new_document_table(self, dialog, number_input, date_input, employee_input,
                                counterparty_input,
                                warehouse_input, warehouse_from, warehouse_to,
                                nomenclature_table, comment_input):

        if not number_input.text().strip():
            QMessageBox.warning(dialog, "Ошибка", "Номер документа обязателен!")
            return
        if not employee_input.currentData():
            QMessageBox.warning(dialog, "Ошибка", "Сотрудник обязателен!")
            return
        if self.doc_type == "приход" and not counterparty_input.currentData():
            QMessageBox.warning(dialog, "Ошибка", "Контрагент обязателен!")
            return
        if self.doc_type in ["расход", "перемещение"] and not warehouse_input.currentData() and self.doc_type=="расход":
            QMessageBox.warning(dialog, "Ошибка", "Склад обязателен!")
            return
        if self.doc_type == "перемещение":
            if not warehouse_from.currentData() or not warehouse_to.currentData():
                QMessageBox.warning(dialog, "Ошибка", "Выберите склады для перемещения!")
                return
            if warehouse_from.currentData() == warehouse_to.currentData():
                QMessageBox.warning(dialog, "Ошибка", "Склад отправителя и получателя не могут совпадать!")
                return

        if nomenclature_table.rowCount() == 0:
            QMessageBox.warning(dialog, "Ошибка", "Добавьте хотя бы одну позицию номенклатуры!")
            return

        for row in range(nomenclature_table.rowCount()):
            qty_text = nomenclature_table.item(row, 1).text()
            try:
                qty = float(qty_text)
                if qty <= 0:
                    raise ValueError
            except:
                QMessageBox.warning(dialog, "Ошибка", f"Количество для позиции {nomenclature_table.item(row,0).text()} должно быть > 0!")
                return

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM document WHERE number=%s", (number_input.text(),))
        if cur.fetchone()[0] > 0:
            QMessageBox.warning(dialog, "Ошибка", f"Документ с номером {number_input.text()} уже существует!")
            cur.close()
            conn.close()
            return
        
        if self.doc_type == "расход":
            for row in range(nomenclature_table.rowCount()):
                nc_id = nomenclature_table.item(row, 0).data(Qt.UserRole)
                qty = float(nomenclature_table.item(row, 1).text())
                available_qty = db.get_nomenclature_balance(nc_id, warehouse_input.currentData())
                if qty > available_qty:
                    QMessageBox.warning(dialog, "Ошибка", 
                        f"На складе {warehouse_input.currentText()} недостаточно номенклатуры {nomenclature_table.item(row,0).text()}. Доступно: {available_qty}")
                    return

        elif self.doc_type == "перемещение":
            for row in range(nomenclature_table.rowCount()):
                nc_id = nomenclature_table.item(row, 0).data(Qt.UserRole)
                qty = float(nomenclature_table.item(row, 1).text())
                available_qty = db.get_nomenclature_balance(nc_id, warehouse_from.currentData())
                if qty > available_qty:
                    QMessageBox.warning(dialog, "Ошибка", 
                        f"На складе {warehouse_from.currentText()} недостаточно номенклатуры {nomenclature_table.item(row,0).text()}. Доступно: {available_qty}")
                    return

        cur.execute("""
            INSERT INTO document (document_type, number, date, id_employee, comment, is_processed)
            VALUES (%s, %s, %s, %s, %s, false)
            RETURNING id_document
        """, (
            self.doc_type,
            number_input.text(),
            date_input.date().toString("yyyy-MM-dd"),
            employee_input.currentData(),
            comment_input.text()
        ))

        doc_id = cur.fetchone()[0]

        if self.doc_type == "приход":
            cur.execute("""
                INSERT INTO document_prihoda (id_document, id_counterparty, id_warehouse)
                VALUES (%s, %s, %s)
            """, (doc_id, counterparty_input.currentData(), warehouse_input.currentData()))
        elif self.doc_type == "расход":
            cur.execute("""
                INSERT INTO document_rashoda (id_document, id_warehouse)
                VALUES (%s, %s)
            """, (doc_id, warehouse_input.currentData()))
        elif self.doc_type == "перемещение":
            cur.execute("""
                INSERT INTO document_peremeshenie (id_document, id_warehouse_from, id_warehouse_to)
                VALUES (%s, %s, %s)
            """, (doc_id, warehouse_from.currentData(), warehouse_to.currentData()))

        for row in range(nomenclature_table.rowCount()):
            nc_id = nomenclature_table.item(row, 0).data(Qt.UserRole)
            qty = float(nomenclature_table.item(row, 1).text())
            cur.execute("""
                INSERT INTO nomenclature_document (id_document, id_nomenclature, quantity)
                VALUES (%s, %s, %s)
            """, (doc_id, nc_id, qty))

        conn.commit()
        cur.close()
        conn.close()
        dialog.accept()
        self.load_data()

    def edit_document(self):
        doc_id = self.get_selected_document_id()
        if not doc_id:
            return

        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT number, date, comment, id_employee
            FROM document
            WHERE id_document = %s
        """, (doc_id,))
        number_val, date_val, comment_val, employee_val = cur.fetchone()

        wh_from = None
        wh_to = None

        counterparty_id = None

        if self.doc_type == "приход":
            cur.execute("""
                SELECT id_warehouse, id_counterparty
                FROM document_prihoda
                WHERE id_document = %s
            """, (doc_id,))
            wh_from, counterparty_id = cur.fetchone()


        elif self.doc_type == "расход":
            cur.execute("""
                SELECT id_warehouse
                FROM document_rashoda
                WHERE id_document = %s
            """, (doc_id,))
            wh_from = cur.fetchone()[0]

        elif self.doc_type == "перемещение":
            cur.execute("""
                SELECT id_warehouse_from, id_warehouse_to
                FROM document_peremeshenie
                WHERE id_document = %s
            """, (doc_id,))
            wh_from, wh_to = cur.fetchone()

        cur.execute("""
            SELECT id_nomenclature, quantity
            FROM nomenclature_document
            WHERE id_document = %s
        """, (doc_id,))

        nomenclatures = cur.fetchall()

        cur.close()
        conn.close()

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование документа")
        dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
        dialog.resize(900, 650)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        layout.addLayout(form)

        font = QFont()
        font.setPointSize(10)

        number_input = QLineEdit(number_val)
        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        date_input.setDisplayFormat("dd.MM.yyyy")
        date_input.setDate(QDate.fromString(date_val.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        date_input.setFont(font)
        date_input.setStyleSheet("background-color: white; color: black;")
        date_input.setMaximumDate(QDate.currentDate())
        comment_input = QLineEdit(comment_val)

        employee_input = QComboBox()
        for emp in db.get_employees():
            employee_input.addItem(f"{emp[1]} {emp[2]}", emp[0])
            if emp[0] == employee_val:
                employee_input.setCurrentIndex(employee_input.count() - 1)

        for w in [number_input, date_input, comment_input, employee_input]:
            w.setFont(font)
            w.setStyleSheet("background-color: white; color: black;")

        counterparty_input = QComboBox()
        counterparty_input.setFont(font)
        counterparty_input.setStyleSheet("background-color: white; color: black;")

        for c in db.get_contractors():
            counterparty_input.addItem(c[1], c[0])
            if c[0] == counterparty_id:
                counterparty_input.setCurrentIndex(counterparty_input.count() - 1)

        warehouse_input = QComboBox()
        warehouse_from = QComboBox()
        warehouse_to = QComboBox()

        for w in db.get_warehouses():
            warehouse_input.addItem(w[1], w[0])
            warehouse_from.addItem(w[1], w[0])
            warehouse_to.addItem(w[1], w[0])

            if w[0] == wh_from:
                warehouse_input.setCurrentIndex(warehouse_input.count() - 1)
                warehouse_from.setCurrentIndex(warehouse_from.count() - 1)
            if w[0] == wh_to:
                warehouse_to.setCurrentIndex(warehouse_to.count() - 1)

        nomenclature_table = QTableWidget()
        nomenclature_table.setColumnCount(2)
        nomenclature_table.setHorizontalHeaderLabels(["Номенклатура", "Количество"])
        nomenclature_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        nomenclature_table.setMaximumHeight(220)
        nomenclature_table.setMinimumHeight(180)
        nomenclature_table.setFont(font)
        nomenclature_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: black;    
                border: 1px solid black;   
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid black; 
            }
        """)
        nomenclature_table.setSelectionBehavior(QTableWidget.SelectRows)
        nomenclature_table.setEditTriggers(QTableWidget.NoEditTriggers)

        all_nomenclature = db.get_nomenclature()
        for nc_id, qty in nomenclatures:
            row = nomenclature_table.rowCount()
            nomenclature_table.insertRow(row)
            name_item = QTableWidgetItem(next((n[1] for n in all_nomenclature if n[0] == nc_id), ""))
            name_item.setData(Qt.UserRole, nc_id)
            qty_item = QTableWidgetItem(str(qty))
            nomenclature_table.setItem(row, 0, name_item)
            nomenclature_table.setItem(row, 1, qty_item)

        table_btn_layout = QHBoxLayout()
        btn_add_row = QPushButton("Добавить позицию")
        btn_edit_row = QPushButton("Редактировать позицию")
        btn_delete_row = QPushButton("Удалить позицию")
        for btn in [btn_add_row, btn_edit_row, btn_delete_row]:
            btn.setStyleSheet("background-color: #AAAAAA; color: black; font-weight: bold;")
            btn.setMinimumHeight(30)
            table_btn_layout.addWidget(btn)

        def add_row():
            row_dialog = QDialog()
            row_dialog.setWindowTitle("Добавить номенклатуру")
            row_layout = QFormLayout(row_dialog)
            row_dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
            nc_combo = QComboBox(); nc_combo.setFont(font)
            nc_combo.setStyleSheet("background-color: white; color: black;")
            for n in all_nomenclature:
                nc_combo.addItem(f"{n[1]} (ед: {n[3]})", n[0])
            qty_input = QLineEdit(); qty_input.setFont(font)
            qty_input.setStyleSheet("background-color: white; color: black;")
            row_layout.addRow("Номенклатура:", nc_combo)
            row_layout.addRow("Количество:", qty_input)
            save_btn = QPushButton("Сохранить"); save_btn.setStyleSheet("background-color: #999999; color: black; font-weight: bold;")
            row_layout.addWidget(save_btn)

            def accept_row():
                try:
                    qty = float(qty_input.text())
                except ValueError:
                    QMessageBox.warning(row_dialog, "Ошибка", "Количество должно быть числом")
                    return
                row_position = nomenclature_table.rowCount()
                nomenclature_table.insertRow(row_position)
                nomenclature_table.setItem(row_position, 0, QTableWidgetItem(nc_combo.currentText()))
                nomenclature_table.item(row_position, 0).setData(Qt.UserRole, nc_combo.currentData())
                nomenclature_table.setItem(row_position, 1, QTableWidgetItem(str(qty)))
                row_dialog.accept()

            save_btn.clicked.connect(accept_row)
            row_dialog.exec()

        def edit_row_func():
            selected = nomenclature_table.currentRow()
            if selected < 0:
                return

            current_nc_id = nomenclature_table.item(selected, 0).data(Qt.UserRole)
            current_qty = nomenclature_table.item(selected, 1).text()

            row_dialog = QDialog()
            row_dialog.setWindowTitle("Редактировать номенклатуру")
            row_dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
            row_layout = QFormLayout(row_dialog)

            nc_combo = QComboBox()
            nc_combo.setFont(font)
            nc_combo.setStyleSheet("background-color: white; color: black;")

            for n in all_nomenclature:
                nc_combo.addItem(f"{n[1]} (ед: {n[3]})", n[0])

            index = nc_combo.findData(current_nc_id)
            if index >= 0:
                nc_combo.setCurrentIndex(index)

            qty_input = QLineEdit(current_qty)
            qty_input.setFont(font)
            qty_input.setStyleSheet("background-color: white; color: black;")

            row_layout.addRow("Номенклатура:", nc_combo)
            row_layout.addRow("Количество:", qty_input)

            save_btn = QPushButton("Сохранить")
            save_btn.setStyleSheet("background-color: #999999; color: black; font-weight: bold;")
            row_layout.addWidget(save_btn)

            def accept_row():
                try:
                    qty = float(qty_input.text())
                except ValueError:
                    QMessageBox.warning(row_dialog, "Ошибка", "Количество должно быть числом")
                    return

                nomenclature_table.item(selected, 0).setText(nc_combo.currentText())
                nomenclature_table.item(selected, 0).setData(Qt.UserRole, nc_combo.currentData())
                nomenclature_table.item(selected, 1).setText(str(qty))

                row_dialog.accept()

            save_btn.clicked.connect(accept_row)
            row_dialog.exec()

        def delete_row_func():
            selected = nomenclature_table.currentRow()
            if selected >= 0:
                nomenclature_table.removeRow(selected)

        btn_add_row.clicked.connect(add_row)
        btn_edit_row.clicked.connect(edit_row_func)
        btn_delete_row.clicked.connect(delete_row_func)

        for btn in [btn_add_row, btn_edit_row, btn_delete_row]:
            btn.setStyleSheet("background-color: #AAAAAA; color: black; font-weight: bold;")
            btn.setMinimumHeight(30)
            table_btn_layout.addWidget(btn)

        form.addRow("Номер документа:", number_input)
        form.addRow("Дата:", date_input)
        form.addRow("Сотрудник:", employee_input)

        if self.doc_type == "приход":
            counterparty_input.setFont(font)
            counterparty_input.setStyleSheet("background-color: white; color: black;")
            warehouse_input.setFont(font)
            warehouse_input.setStyleSheet("background-color: white; color: black;")
            form.addRow("Контрагент:", counterparty_input)  
            form.addRow("Склад:", warehouse_input)
        elif self.doc_type == "расход":
            warehouse_input.setFont(font)
            warehouse_input.setStyleSheet("background-color: white; color: black;")
            form.addRow("Склад:", warehouse_input)
        elif self.doc_type == "перемещение":
            warehouse_from.setFont(font)
            warehouse_from.setStyleSheet("background-color: white; color: black;")
            warehouse_to.setFont(font)
            warehouse_to.setStyleSheet("background-color: white; color: black;")
            form.addRow("Склад-отправитель:", warehouse_from)
            form.addRow("Склад-получатель:", warehouse_to)

        table_container = QVBoxLayout()
        table_container.addLayout(table_btn_layout)
        table_container.addWidget(nomenclature_table)

        form.addRow("Номенклатура:", table_container)

        form.addRow("Комментарий:", comment_input)

        save_btn = QPushButton("Сохранить изменения")
        save_btn.setMinimumHeight(35)
        save_btn.setStyleSheet(
            "background-color: #999999; color: black; font-weight: bold;"
        )

        save_btn.clicked.connect(lambda: self.save_edit_document(
            dialog, doc_id,
            number_input, date_input, employee_input,
            counterparty_input,
            warehouse_input, warehouse_from, warehouse_to,
            nomenclature_table, comment_input
        ))

        layout.addWidget(save_btn)
        dialog.exec()

    def save_edit_document(self, dialog, doc_id, number_input, date_input, employee_input,
                        counterparty_input, warehouse_input, warehouse_from, warehouse_to,
                        nomenclature_table, comment_input):

        if not number_input.text().strip():
            QMessageBox.warning(dialog, "Ошибка", "Номер документа обязателен!")
            return
        if not employee_input.currentData():
            QMessageBox.warning(dialog, "Ошибка", "Сотрудник обязателен!")
            return
        if self.doc_type == "приход" and not counterparty_input.currentData():
            QMessageBox.warning(dialog, "Ошибка", "Контрагент обязателен!")
            return
        if self.doc_type in ["расход", "перемещение"] and self.doc_type=="расход" and not warehouse_input.currentData():
            QMessageBox.warning(dialog, "Ошибка", "Склад обязателен!")
            return
        if self.doc_type == "перемещение":
            if not warehouse_from.currentData() or not warehouse_to.currentData():
                QMessageBox.warning(dialog, "Ошибка", "Выберите склады для перемещения!")
                return
            if warehouse_from.currentData() == warehouse_to.currentData():
                QMessageBox.warning(dialog, "Ошибка", "Склад отправителя и получателя не могут совпадать!")
                return

        if nomenclature_table.rowCount() == 0:
            QMessageBox.warning(dialog, "Ошибка", "Добавьте хотя бы одну позицию номенклатуры!")
            return

        for row in range(nomenclature_table.rowCount()):
            qty_text = nomenclature_table.item(row, 1).text()
            try:
                qty = float(qty_text)
                if qty <= 0:
                    raise ValueError
            except:
                QMessageBox.warning(dialog, "Ошибка", f"Количество для позиции {nomenclature_table.item(row,0).text()} должно быть > 0!")
                return

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM document WHERE number=%s AND id_document<>%s", (number_input.text(), doc_id))
        if cur.fetchone()[0] > 0:
            QMessageBox.warning(dialog, "Ошибка", f"Документ с номером {number_input.text()} уже существует!")
            cur.close()
            conn.close()
            return

        if self.doc_type == "расход":
            for row in range(nomenclature_table.rowCount()):
                nc_id = nomenclature_table.item(row, 0).data(Qt.UserRole)
                qty = float(nomenclature_table.item(row, 1).text())
                available_qty = db.get_nomenclature_balance(nc_id, warehouse_input.currentData())
                if qty > available_qty:
                    QMessageBox.warning(dialog, "Ошибка", 
                        f"На складе {warehouse_input.currentText()} недостаточно номенклатуры {nomenclature_table.item(row,0).text()}. Доступно: {available_qty}")
                    return

        elif self.doc_type == "перемещение":
            for row in range(nomenclature_table.rowCount()):
                nc_id = nomenclature_table.item(row, 0).data(Qt.UserRole)
                qty = float(nomenclature_table.item(row, 1).text())
                available_qty = db.get_nomenclature_balance(nc_id, warehouse_from.currentData())
                if qty > available_qty:
                    QMessageBox.warning(dialog, "Ошибка", 
                        f"На складе {warehouse_from.currentText()} недостаточно номенклатуры {nomenclature_table.item(row,0).text()}. Доступно: {available_qty}")
                    return

        cur.execute("""
            UPDATE document
            SET number=%s, date=%s, id_employee=%s, comment=%s
            WHERE id_document=%s
        """, (
            number_input.text(),
            date_input.date().toString("yyyy-MM-dd"),
            employee_input.currentData(),
            comment_input.text(),
            doc_id
        ))

        if self.doc_type == "приход":
            cur.execute("""
                UPDATE document_prihoda
                SET id_warehouse=%s, id_counterparty=%s
                WHERE id_document=%s
            """, (warehouse_input.currentData(), counterparty_input.currentData(), doc_id))
        elif self.doc_type == "расход":
            cur.execute("""
                UPDATE document_rashoda
                SET id_warehouse=%s
                WHERE id_document=%s
            """, (warehouse_input.currentData(), doc_id))
        elif self.doc_type == "перемещение":
            cur.execute("""
                UPDATE document_peremeshenie
                SET id_warehouse_from=%s, id_warehouse_to=%s
                WHERE id_document=%s
            """, (warehouse_from.currentData(), warehouse_to.currentData(), doc_id))

        cur.execute("DELETE FROM nomenclature_document WHERE id_document=%s", (doc_id,))
        for row in range(nomenclature_table.rowCount()):
            nc_id = nomenclature_table.item(row, 0).data(Qt.UserRole)
            qty = float(nomenclature_table.item(row, 1).text())
            cur.execute("""
                INSERT INTO nomenclature_document (id_document, id_nomenclature, quantity)
                VALUES (%s, %s, %s)
            """, (doc_id, nc_id, qty))

        conn.commit()
        cur.close()
        conn.close()
        dialog.accept()
        self.load_data()

    # Удаление документа 
    def delete_document(self):
        doc_id = self.get_selected_document_id()
        if not doc_id:
            return

        confirm = QMessageBox(self)
        confirm.setWindowTitle("Удаление документа")
        confirm.setText(f"Точно ли вы хотите удалить документ {doc_id}?")
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        yes_button = confirm.button(QMessageBox.StandardButton.Yes)
        no_button = confirm.button(QMessageBox.StandardButton.No)
        yes_button.setText("Да")
        no_button.setText("Нет")
        for btn in [yes_button, no_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #777777;
                    color: black;
                    font-weight: bold;
                    border-radius: 5px;
                    min-width: 80px;
                    min-height: 30px;
                }
                QPushButton:hover { background-color: #555555; }
            """)
        confirm.setStyleSheet("background-color: #CCCCCC; color: black;")
        ret = confirm.exec()
        if ret == QMessageBox.StandardButton.Yes:
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM document WHERE id_document=%s", (doc_id,))
            cur.execute("DELETE FROM nomenclature_document WHERE id_document=%s", (doc_id,))
            if self.doc_type == 'приход':
                cur.execute("DELETE FROM document_prihoda WHERE id_document=%s", (doc_id,))
            elif self.doc_type == 'расход':
                cur.execute("DELETE FROM document_rashoda WHERE id_document=%s", (doc_id,))
            elif self.doc_type == 'перемещение':
                cur.execute("DELETE FROM document_peremeshenie WHERE id_document=%s", (doc_id,))
            conn.commit()
            cur.close()
            conn.close()
            self.load_data()

    # Проведение документа 
    def process_document(self):
        doc_id = self.get_selected_document_id()
        if not doc_id:
            return
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE document SET is_processed=true WHERE id_document=%s", (doc_id,))
        conn.commit()
        cur.close()
        conn.close()
        self.load_data()

    # Отмена проведения
    def unprocess_document(self):
        doc_id = self.get_selected_document_id()
        if not doc_id:
            return
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE document SET is_processed=false WHERE id_document=%s", (doc_id,))
        conn.commit()
        cur.close()
        conn.close()
        self.load_data()

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

        self.pages = QStackedWidget()

        # Таблицы
        self.dashboard_page = DashboardPage()
        self.pages.addWidget(self.dashboard_page)
        self.pages_dict["Главная"] = self.dashboard_page

        # Единицы измерения
        self.units_page = ReferenceTablePage(
            "Единицы измерения",
            ["ID", "Наименование", "Код"],
            db.get_units,
            table_name="units",
            id_field="id_unit",
            fields=[
                ("title", "Наименование"),
                ("code_unit", "Код"),
            ]
        )
        self.pages.addWidget(self.units_page)
        self.pages_dict["Единицы измерения"] = self.units_page

        # Категории номенклатуры
        self.categories_page = ReferenceTablePage(
            "Категории номенклатуры",
            ["ID", "Наименование", "Описание"],
            db.get_categories,
            table_name="categories_nomenclature",
            id_field="id_category",
            fields=[
                ("title", "Наименование"),
                ("description", "Описание"),
            ]
        )
        self.pages.addWidget(self.categories_page)
        self.pages_dict["Категории номенклатуры"] = self.categories_page

        # Номенклатура
        self.nomenclature_page = ReferenceTablePage(
            "Номенклатура",
            ["ID", "Наименование", "Категория", "Единица измерения", "Артикул", "Описание"],
            db.get_nomenclature,
            table_name="nomenclature",
            id_field="id_nomenclature",
            fields=[
                ("title", "Наименование"),
                ("id_category", "Категория", {
                    "table": "categories_nomenclature",
                    "id": "id_category",
                    "title": "title"
                }),
                ("id_unit", "Единица измерения", {
                    "table": "units",
                    "id": "id_unit",
                    "title": "title"
                }),
                ("article", "Артикул"),
                ("description", "Описание"),
            ]
        )
        self.pages.addWidget(self.nomenclature_page)
        self.pages_dict["Номенклатура"] = self.nomenclature_page

        # Сотрудники
        self.employees_page = ReferenceTablePage(
            "Сотрудники",
            ["ID", "Фамилия", "Имя", "Отчество", "Должность", "Телефон", "Email"],
            db.get_employees,
            table_name="employees",
            id_field="id_employee",
            fields=[
                ("familia", "Фамилия"),
                ("imya", "Имя"),
                ("otchestvo", "Отчество"),
                ("position", "Должность"),
                ("phone", "Телефон"),
                ("email", "Email")
            ]
        )
        self.pages.addWidget(self.employees_page)
        self.pages_dict["Сотрудники"] = self.employees_page

        # Контрагенты
        self.counterparties_page = ReferenceTablePage(
            "Контрагенты",
            ["ID", "Наименование", "Менеджер", "Телефон", "Email", "Адрес"],
            db.get_contractors,
            table_name="counterparties",
            id_field="id_counterparty",
            fields=[
                ("name", "Наименование"),
                ("manager", "Менеджер"),
                ("phone", "Телефон"),
                ("email", "Email"),
                ("address", "Адрес")
            ]
        )
        self.pages.addWidget(self.counterparties_page)
        self.pages_dict["Контрагенты"] = self.counterparties_page

        # Склады
        self.warehouses_page = ReferenceTablePage(
            "Склады",
            ["ID", "Наименование", "Адрес", "Вместимость (м²)", "Ответственный"],
            db.get_warehouses,
            table_name="warehouses",
            id_field="id_warehouse",
            fields=[
                ("title", "Наименование"),
                ("address", "Адрес"),
                ("capacity_m2", "Вместимость (м²)", "numeric"),
                ("responsible", "Ответственный", {
                    "table": "employees",
                    "id": "id_employee",
                    "title": "familia"
                }),
            ]
        )
        self.pages.addWidget(self.warehouses_page)
        self.pages_dict["Склады"] = self.warehouses_page


        self.prihod_page = DocumentTablePage("Оприходование",["ID документа", "Номер", "Дата", "Сотрудник","Контрагент", "Склад", "Номенклатура",
        "Количество", "Комментарий", "Проведен"],db.get_prihod_documents_full, doc_type='приход')
        self.pages.addWidget(self.prihod_page)
        self.pages_dict["Оприходование"] = self.prihod_page

        self.rashod_page = DocumentTablePage("Расход",["ID документа", "Номер", "Дата", "Сотрудник","Склад", 
        "Номенклатура","Количество", "Комментарий", "Проведен"],db.get_rashod_documents_full, doc_type='расход')
        self.pages.addWidget(self.rashod_page)
        self.pages_dict["Расход"] = self.rashod_page

        self.peremeshchenie_page = DocumentTablePage("Перемещение",["ID документа", "Номер", "Дата", "Сотрудник",
        "Отправитель", "Получатель", "Номенклатура", "Количество","Комментарий", "Проведен"],db.get_peremeshchenie_documents_full, doc_type='перемещение')
        self.pages.addWidget(self.peremeshchenie_page)
        self.pages_dict["Перемещение"] = self.peremeshchenie_page

        self.stock_page = TablePage("Остатки на складах",["Склад", "Номенклатура","Ед.измерения", "Остаток"],db.get_stock_balances)
        self.pages.addWidget(self.stock_page)
        self.pages_dict["Остатки на складах"] = self.stock_page

        self.move_page = TablePage("Движение по номенклатуре",["ID", "Дата", "Тип операции", "Номенклатура", "Количество", "Склад"],db.get_operations)
        self.pages.addWidget(self.move_page)
        self.pages_dict["Движение по номенклатуре"] = self.move_page

        self.turnover_page = TablePage("Оборотная ведомость",["Склад", "Номенклатура", "Ед.изм.", "Приход", "Расход", "Конечный остаток"],db.get_turnover_report)
        self.pages.addWidget(self.turnover_page)
        self.pages_dict["Оборотная ведомость"] = self.turnover_page

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

# Запуск приложения 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen() 
    sys.exit(app.exec())