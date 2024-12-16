import csv

import sqlite3

from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6 import QtCore, QtWidgets


class Scores(QWidget):
    def __init__(self):
        """Инициализирует окно с таблицей рекордов."""
        super().__init__()
        self.setupUi(self)

        self.update_levels()  # Инициализация списка уровней при запуске
        # Подключение слота для обработки изменения выбранного уровня
        self.levelChooseBox.currentTextChanged.connect(self.on_levelchoose_changed)

        self.fill_scores_table()  # Инициализация таблицы рекордов

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtWidgets.QTableWidget(parent=Form)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.levelChooseBox = QtWidgets.QComboBox(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.levelChooseBox.sizePolicy().hasHeightForWidth())
        self.levelChooseBox.setSizePolicy(sizePolicy)
        self.levelChooseBox.setObjectName("levelChooseBox")
        self.horizontalLayout.addWidget(self.levelChooseBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Результаты"))

    def on_levelchoose_changed(self):
        """Обрабатывает изменение выбора уровня в выпадающем списке."""
        if self.levelChooseBox.currentText() == "Перезагрузить список":
            self.update_levels()
            return  # Важно: выход из функции, чтобы избежать повторного заполнения таблицы

        self.fill_scores_table()  # Обновление таблицы рекордов для нового уровня

    def update_levels(self):
        """Обновляет список уровней из файла levels.csv."""
        try:
            with open('levels.csv', 'r', encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # Пропуск заголовка
                levels = [level[0] for level in reader]  # Извлечение имен уровней
        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл levels.csv не найден.")
            return  # Прерывание выполнения функции при ошибке

        self.levelChooseBox.clear()
        self.levelChooseBox.addItems(levels)
        self.levelChooseBox.addItem("Перезагрузить список")

    def fill_scores_table(self):
        """Заполняет таблицу рекордов данными из базы данных."""
        self.tableWidget.clearContents()  # Очистка таблицы перед обновлением

        try:
            con = sqlite3.connect("snake.db")
            cur = con.cursor()

            # Запрос данных из базы данных для выбранного уровня
            level_scores = cur.execute(f"""
                SELECT score, date, life_time_sec, snake_length FROM scores
                    WHERE level_name = ?
                    ORDER BY score DESC""", (self.levelChooseBox.currentText(),)).fetchall()

            # Обработка пустого результата запроса
            if not level_scores:
                self.tableWidget.setColumnCount(1)
                self.tableWidget.setHorizontalHeaderLabels(["Нет результатов"])
                self.tableWidget.setRowCount(1)
                self.tableWidget.setItem(0, 0, QTableWidgetItem("Нет результатов"))
                self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
                return

            # Заголовки столбцов
            column_headers = ["Результат", "Дата", "Время жизни", "Длина змеи"]
            self.tableWidget.setColumnCount(len(column_headers))
            self.tableWidget.setHorizontalHeaderLabels(column_headers)
            self.tableWidget.setRowCount(len(level_scores))

            # Заполнение таблицы данными
            for row, score_data in enumerate(level_scores):
                for col, value in enumerate(score_data):
                    item = QTableWidgetItem(str(value))
                    self.tableWidget.setItem(row, col, item)

            # Автоматическое изменение размера столбцов
            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.Stretch)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка работы с базой данных: {e}")
        finally:
            if 'con' in locals() and con:  # Проверка на существование соединения
                con.close()
