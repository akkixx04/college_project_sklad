import sys
from functools import partial

import db
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QStackedWidget, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter, QPainterPath

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

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # ===== Левая таблица: критические остатки =====
        self.critical_table = QTableWidget()
        self.critical_table.setColumnCount(4)
        self.critical_table.setHorizontalHeaderLabels([
            "Склад",
            "Номенклатура",
            "Ед. изм.",
            "Остаток"
        ])
        self._style_table(self.critical_table)

        # ===== Правая таблица: последние операции =====
        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(5)
        self.operations_table.setHorizontalHeaderLabels(
            ["Дата", "Тип", "Номенклатура", "Кол-во", "Склад"]
        )
        self._style_table(self.operations_table)

        # ===== ЛЕВАЯ ЧАСТЬ =====
        left_layout = QVBoxLayout()

        # ===== Левый заголовок =====
        critical_title = QLabel("Критические остатки по складам")
        critical_title.setAlignment(Qt.AlignCenter)  # выравнивание по центру
        critical_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: black;
            margin-bottom: 25px;
            margin-top: 20px;                         
        """)
        left_layout.addWidget(critical_title)
        left_layout.addWidget(self.critical_table)

        # ===== Правая часть =====
        right_layout = QVBoxLayout()

        operations_title = QLabel("Последние операции")
        operations_title.setAlignment(Qt.AlignCenter)  # выравнивание по центру
        operations_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: black;
            margin-bottom: 25px;
            margin-top: 20px;                            
        """)
        right_layout.addWidget(operations_title)
        right_layout.addWidget(self.operations_table)

        # ===== Объединяем в горизонтальный layout =====
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
        # Критические остатки
        crit_rows = db.get_critical_stock()
        self.critical_table.setRowCount(len(crit_rows))
        for r, row in enumerate(crit_rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # выравнивание текста
                item.setFlags(Qt.ItemIsEnabled)
                self.critical_table.setItem(r, c, item)

        self.critical_table.resizeRowsToContents()  # подгоняем высоту строк


        # Последние операции
        op_rows = db.get_last_operations()
        self.operations_table.setRowCount(len(op_rows))
        for r, row in enumerate(op_rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setFlags(Qt.ItemIsEnabled)
                self.operations_table.setItem(r, c, item)
        self.operations_table.resizeRowsToContents()

# Универсальный класс таблицы
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


class ReferenceTablePage(TablePage):
    def __init__(self, title, headers, data_loader,
                 table_name, id_field, fields):
        super().__init__(title, headers, data_loader)
        self.table_name = table_name
        self.id_field = id_field
        self.fields = fields
        self._init_top_panel()

    # Верхняя панель
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

    # Диалог формы с поддержкой FK
    def _open_form(self, item_id=None, data=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование" if item_id else "Добавление")
        dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        layout.addLayout(form)
        font = QFont()
        font.setPointSize(10)

        inputs = {}

        for field_def in self.fields:
            field = field_def[0]
            label = field_def[1]

            if len(field_def) == 3:  # FK поле
                fk = field_def[2]
                combo = QComboBox()
                combo.setFont(font)
                combo.setStyleSheet("background-color: white; color: black;")  # Белый фон, черный текст
                fk_data = self._load_fk_data(fk)
                for fk_id, fk_title in fk_data:
                    combo.addItem(str(fk_title), fk_id)
                if data:
                    index = combo.findData(data.get(field))
                    if index >= 0:
                        combo.setCurrentIndex(index)
                inputs[field] = combo
                form.addRow(label + ":", combo)

            else:  # обычное текстовое поле
                edit = QLineEdit()
                edit.setFont(font)
                edit.setStyleSheet("background-color: white; color: black;")  # Белый фон, черный текст
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

    # Сохранение с учетом FK
    def _save_item(self, dialog, item_id, inputs):
        conn = db.get_connection()
        cur = conn.cursor()

        values = []
        for f in inputs:
            widget = inputs[f]
            if isinstance(widget, QComboBox):
                values.append(widget.currentData())
            else:
                values.append(widget.text())

        fields_sql = ", ".join(inputs.keys())
        if item_id is None:
            placeholders = ", ".join(["%s"] * len(values))
            cur.execute(f"INSERT INTO {self.table_name} ({fields_sql}) VALUES ({placeholders})", values)
        else:
            set_sql = ", ".join(f"{f}=%s" for f in inputs.keys())
            cur.execute(f"UPDATE {self.table_name} SET {set_sql} WHERE {self.id_field}=%s", values + [item_id])

        conn.commit()
        cur.close()
        conn.close()
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

    # Загрузка данных для FK
    def _load_fk_data(self, fk):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT {fk['id']}, {fk['title']} FROM {fk['table']} ORDER BY {fk['title']}")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows


class DocumentTablePage(TablePage):
    def __init__(self, title, headers, data_loader, doc_type):
        super().__init__(title, headers, data_loader)
        self.doc_type = doc_type

        # Верхняя панель с кнопками
        self.top_panel = QWidget()
        self.top_panel.setStyleSheet("background-color: #E5E5E5;")
        top_layout = QHBoxLayout(self.top_panel)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(5)

        # Кнопки
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

        # Подключаем действия
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


    def get_selected_document_id(self):
        selected = self.table.currentRow()
        if selected < 0:
            return None
        return int(self.table.item(selected, 0).text())

    # Добавление документа 
    def add_document(self):
        dialog = QDialog()
        dialog.setWindowTitle("Добавление документа")
        dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        layout.addLayout(form)
        font = QFont(); font.setPointSize(10)

        # Поля документа
        number_input = QLineEdit(); date_input = QLineEdit()
        employee_input = QComboBox(); counterparty_input = QComboBox(); warehouse_input = QComboBox()
        for w in [number_input, date_input, employee_input, counterparty_input, warehouse_input]:
            w.setFont(font)
            w.setStyleSheet("background-color: white; color: black;")
        for emp in db.get_employees():
            employee_input.addItem(f"{emp[1]} {emp[2]}", emp[0])
        for c in db.get_contractors():
            counterparty_input.addItem(c[1], c[0])
        for w in db.get_warehouses():
            warehouse_input.addItem(w[1], w[0])

        # Таблица номенклатуры
        nomenclature_table = QTableWidget()
        nomenclature_table.setColumnCount(2)
        nomenclature_table.setHorizontalHeaderLabels(["Номенклатура", "Количество"])
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
        nomenclature_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        nomenclature_table.setFont(font)
        nomenclature_table.setSelectionBehavior(QTableWidget.SelectRows)
        nomenclature_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Кнопки работы с номенклатурой
        btn_layout = QHBoxLayout()
        btn_add_row = QPushButton("Добавить позицию")
        btn_edit_row = QPushButton("Редактировать позицию")
        btn_delete_row = QPushButton("Удалить позицию")
        for b in [btn_add_row, btn_edit_row, btn_delete_row]:
            b.setStyleSheet("background-color: #AAAAAA; color: black; font-weight: bold;")
            b.setMinimumHeight(30)
            btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        # Логика кнопок номенклатуры
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

        # Добавляем на форму
        form.addRow("Номер документа:", number_input)
        form.addRow("Дата:", date_input)
        form.addRow("Сотрудник:", employee_input)
        form.addRow("Контрагент:", counterparty_input)
        form.addRow("Склад:", warehouse_input)
        form.addRow("Номенклатура:", nomenclature_table)
        comment_input = QLineEdit(); comment_input.setFont(font)
        comment_input.setStyleSheet("background-color: white; color: black;")
        form.addRow("Комментарий:", comment_input)

        save_btn = QPushButton("Сохранить"); save_btn.setMinimumHeight(35)
        save_btn.setStyleSheet("background-color: #999999; color: black; font-weight: bold;")
        save_btn.clicked.connect(lambda: self.save_new_document_table(
            dialog, number_input, date_input, employee_input, counterparty_input,
            warehouse_input, nomenclature_table, comment_input
        ))
        layout.addWidget(save_btn)
        dialog.exec()

    # Сохранение нового документа 
    def save_new_document_table(self, dialog, number_input, date_input, employee_input,
                                counterparty_input, warehouse_input, nomenclature_table, comment_input):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO document (document_type, number, date, id_employee, comment, is_processed)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_document;
        """, (self.doc_type, number_input.text(), date_input.text(),
              employee_input.currentData(), comment_input.text(), False))
        doc_id = cur.fetchone()[0]

        # Заполнение связанных таблиц
        if self.doc_type == 'приход':
            cur.execute("INSERT INTO document_prihoda (id_document, id_counterparty, id_warehouse) VALUES (%s, %s, %s)",
                        (doc_id, counterparty_input.currentData(), warehouse_input.currentData()))
        elif self.doc_type == 'расход':
            cur.execute("INSERT INTO document_rashoda (id_document, id_warehouse) VALUES (%s, %s)",
                        (doc_id, warehouse_input.currentData()))
        elif self.doc_type == 'перемещение':
            cur.execute("INSERT INTO document_peremeshenie (id_document, id_warehouse_from, id_warehouse_to) VALUES (%s, %s, %s)",
                        (doc_id, warehouse_input.currentData(), warehouse_input.currentData()))

        # Сохранение номенклатуры
        for row in range(nomenclature_table.rowCount()):
            nc_id = nomenclature_table.item(row, 0).data(Qt.UserRole)
            qty = float(nomenclature_table.item(row, 1).text())
            cur.execute("INSERT INTO nomenclature_document (id_document, id_nomenclature, quantity) VALUES (%s, %s, %s)",
                        (doc_id, nc_id, qty))

        conn.commit()
        cur.close()
        conn.close()
        dialog.accept()
        self.load_data()

    # Редактирование документа 
    def edit_document(self):
        doc_id = self.get_selected_document_id()
        if not doc_id:
            return

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT number, date, comment, id_employee FROM document WHERE id_document=%s", (doc_id,))
        doc_row = cur.fetchone()
        number_val, date_val, comment_val, employee_val = doc_row

        cur.execute("SELECT id_nomenclature, quantity FROM nomenclature_document WHERE id_document=%s", (doc_id,))
        nomenclatures = cur.fetchall()

        if self.doc_type == 'приход':
            cur.execute("SELECT id_warehouse, id_counterparty FROM document_prihoda WHERE id_document=%s", (doc_id,))
            wh_row = cur.fetchone()
            warehouse_id, counterparty_id = wh_row
        else:
            warehouse_id = counterparty_id = None

        cur.close()
        conn.close()

        dialog = QDialog()
        dialog.setWindowTitle("Редактирование документа")
        dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        form = QFormLayout()
        layout.addLayout(form)
        font = QFont(); font.setPointSize(10)

        # Поля документа
        number_input = QLineEdit(str(number_val)); number_input.setFont(font)
        number_input.setStyleSheet("background-color: white; color: black;")
        date_input = QLineEdit(str(date_val)); date_input.setFont(font)
        date_input.setStyleSheet("background-color: white; color: black;")
        employee_input = QComboBox(); employee_input.setFont(font)
        employee_input.setStyleSheet("background-color: white; color: black;")
        for emp in db.get_employees():
            employee_input.addItem(f"{emp[1]} {emp[2]}", emp[0])
        index = employee_input.findData(employee_val)
        if index >= 0:
            employee_input.setCurrentIndex(index)

        counterparty_input = QComboBox(); counterparty_input.setFont(font)
        counterparty_input.setStyleSheet("background-color: white; color: black;")
        for c in db.get_contractors():
            counterparty_input.addItem(c[1], c[0])
        if counterparty_id:
            index = counterparty_input.findData(counterparty_id)
            if index >= 0:
                counterparty_input.setCurrentIndex(index)

        warehouse_input = QComboBox(); warehouse_input.setFont(font)
        warehouse_input.setStyleSheet("background-color: white; color: black;")
        for w in db.get_warehouses():
            warehouse_input.addItem(w[1], w[0])
        if warehouse_id:
            index = warehouse_input.findData(warehouse_id)
            if index >= 0:
                warehouse_input.setCurrentIndex(index)

        # Таблица номенклатуры
        nomenclature_table = QTableWidget()
        nomenclature_table.setColumnCount(2)
        nomenclature_table.setHorizontalHeaderLabels(["Номенклатура", "Количество"])
        nomenclature_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

        # Заполняем таблицу существующими номенклатурами
        all_nomenclature = db.get_nomenclature()
        for nc_id, qty in nomenclatures:
            row = nomenclature_table.rowCount()
            nomenclature_table.insertRow(row)
            name_item = QTableWidgetItem(next((n[1] for n in all_nomenclature if n[0] == nc_id), ""))
            name_item.setData(Qt.UserRole, nc_id)
            qty_item = QTableWidgetItem(str(qty))
            nomenclature_table.setItem(row, 0, name_item)
            nomenclature_table.setItem(row, 1, qty_item)

        # Кнопки работы с таблицей номенклатуры
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
            current_nc = nomenclature_table.item(selected, 0).text()
            current_qty = nomenclature_table.item(selected, 1).text()
            row_dialog = QDialog()
            row_dialog.setWindowTitle("Редактировать номенклатуру")
            row_layout = QFormLayout(row_dialog)
            row_dialog.setStyleSheet("background-color: #CCCCCC; color: black;")
            nc_combo = QComboBox(); nc_combo.setFont(font)
            nc_combo.setStyleSheet("background-color: white; color: black;")
            for n in all_nomenclature:
                nc_combo.addItem(f"{n[1]} (ед: {n[3]})", n[0])
            for i in range(nc_combo.count()):
                if nc_combo.itemText(i) == current_nc:
                    nc_combo.setCurrentIndex(i)
                    break
            qty_input = QLineEdit(current_qty); qty_input.setFont(font)
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

        # Добавляем поля на форму
        form.addRow("Номер документа:", number_input)
        form.addRow("Дата:", date_input)
        form.addRow("Сотрудник:", employee_input)
        form.addRow("Контрагент:", counterparty_input)
        form.addRow("Склад:", warehouse_input)
        form.addRow("Номенклатура и количество:", nomenclature_table)
        layout.addLayout(table_btn_layout)

        comment_input = QLineEdit(str(comment_val)); comment_input.setFont(font)
        comment_input.setStyleSheet("background-color: white; color: black;")
        form.addRow("Комментарий:", comment_input)

        save_btn = QPushButton("Сохранить"); save_btn.setStyleSheet("background-color: #999999; color: black; font-weight: bold;")
        save_btn.setMinimumHeight(35)
        save_btn.clicked.connect(lambda: self.save_edit_document(
            dialog, doc_id, number_input, date_input, employee_input, counterparty_input,
            warehouse_input, nomenclature_table, comment_input
        ))
        layout.addWidget(save_btn)
        dialog.exec()

    def save_edit_document(self, dialog, doc_id, number_input, date_input, employee_input, counterparty_input,
                           warehouse_input, nomenclature_table, comment_input):
        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE document SET number=%s, date=%s, id_employee=%s, comment=%s WHERE id_document=%s
        """, (str(number_input.text()), str(date_input.text()), employee_input.currentData(), str(comment_input.text()), doc_id))

        if self.doc_type == 'приход':
            cur.execute("UPDATE document_prihoda SET id_warehouse=%s, id_counterparty=%s WHERE id_document=%s",
                        (warehouse_input.currentData(), counterparty_input.currentData(), doc_id))
        elif self.doc_type == 'расход':
            cur.execute("UPDATE document_rashoda SET id_warehouse=%s WHERE id_document=%s",
                        (warehouse_input.currentData(), doc_id))
        elif self.doc_type == 'перемещение':
            cur.execute("UPDATE document_peremeshenie SET id_warehouse_from=%s, id_warehouse_to=%s WHERE id_document=%s",
                        (warehouse_input.currentData(), warehouse_input.currentData(), doc_id))

        # Сначала удаляем старые строки номенклатуры
        cur.execute("DELETE FROM nomenclature_document WHERE id_document=%s", (doc_id,))
        for row in range(nomenclature_table.rowCount()):
            name_item = nomenclature_table.item(row, 0)
            qty_item = nomenclature_table.item(row, 1)
            if name_item and qty_item:
                nomenclature_id = int(name_item.data(Qt.UserRole)) if name_item.data(Qt.UserRole) else None
                try:
                    quantity = float(qty_item.text())
                except:
                    quantity = 0
                if nomenclature_id:
                    cur.execute(
                        "INSERT INTO nomenclature_document (id_document, id_nomenclature, quantity) VALUES (%s, %s, %s)",
                        (doc_id, nomenclature_id, quantity)
                    )

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

        # Кнопки
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
                ("last_name", "Фамилия"),
                ("first_name", "Имя"),
                ("middle_name", "Отчество"),
                ("position", "Должность"),
                ("phone", "Телефон"),
                ("email", "Email")
            ]
        )
        self.pages.addWidget(self.employees_page)
        self.pages_dict["Сотрудники"] = self.employees_page


        # Контрагенты
        self.contractors_page = ReferenceTablePage(
            "Контрагенты",
            ["ID", "Наименование", "Менеджер", "Телефон", "Email", "Адрес"],
            db.get_contractors,
            table_name="contractors",
            id_field="id_contractor",
            fields=[
                ("name", "Наименование"),
                ("manager", "Менеджер"),
                ("phone", "Телефон"),
                ("email", "Email"),
                ("address", "Адрес")
            ]
        )
        self.pages.addWidget(self.contractors_page)
        self.pages_dict["Контрагенты"] = self.contractors_page


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
                ("capacity_m2", "Вместимость (м²)"),
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

