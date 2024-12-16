import sqlite3

from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6 import QtCore, QtWidgets


class Achievements(QWidget):
    def __init__(self):
        """Инициализирует окно достижений."""
        super().__init__()
        self.setupUi(self)

        # Обновление таблицы достижений при запуске
        self.update_achievements_table()
        self.resetButton.clicked.connect(self.reset_achievement)

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 350)
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
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.resetButton = QtWidgets.QPushButton(parent=Form)
        self.resetButton.setObjectName("resetButton")
        self.horizontalLayout.addWidget(self.resetButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Достижения"))
        self.resetButton.setText(_translate("Form", "Сброс"))

    def update_achievements_table(self):
        """Обновляет таблицу достижений данными из базы данных."""
        self.tableWidget.clearContents()  # Очищаем таблицу перед обновлением
        con = sqlite3.connect("snake.db")  # Подключение к базе данных
        cur = con.cursor()  # Получение курсора для выполнения запросов

        # Запрос всех достижений, которые уже получены (level_name != NULL)
        achievements = cur.execute("""
            SELECT name, description, level_name FROM achievements
            WHERE level_name is not NULL""").fetchall()

        # Обработка случая, когда нет достижений
        if not achievements:
            self.tableWidget.setColumnCount(1)
            self.tableWidget.setHorizontalHeaderLabels(["Нет достижений"])
            self.tableWidget.setRowCount(1)
            self.tableWidget.setItem(0, 0, QTableWidgetItem("Нет достижений"))
            self.tableWidget.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.Stretch
            )
            return

        # Заголовки столбцов
        column_headers = ["Название", "Описание", "Получена на"]
        self.tableWidget.setColumnCount(len(column_headers))
        self.tableWidget.setHorizontalHeaderLabels(column_headers)
        self.tableWidget.setRowCount(len(achievements))

        # Заполнение таблицы данными из списка achievements
        for row, achievement in enumerate(achievements):  # enumerate для получения индекса и значения
            for col, value in enumerate(achievement):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row, col, item)

        # Автоматическое изменение размера столбцов
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def reset_achievement(self):
        """Сбрасывает выбранное достижение (устанавливает level_name в NULL)."""
        # Получение данных выбранной строки из таблицы
        selected_items = self.tableWidget.selectedItems()
        if not selected_items or len(selected_items) < 2:  # Проверка на наличие выбранных элементов
            QMessageBox.warning(self, "Предупреждение", "Выберите строку для сброса.")
            return

        selected_row = [item.text() for item in selected_items[:2]]  # Берем только название и описание

        con = sqlite3.connect("snake.db")
        cur = con.cursor()

        try:
            # Обновление данных в базе данных: устанавливаем level_name в NULL для сброса достижения
            cur.execute("""
                  UPDATE achievements 
                  SET level_name = NULL
                  WHERE name = ? AND description = ?
              """, (selected_row[0], selected_row[1]))
            con.commit()  # Фиксируем изменения в базе
            self.update_achievements_table()  # Обновляем таблицу после сброса

        except Exception as e:
            QMessageBox.critical(self, "Ошибка при сбросе", f"Ошибка при обновлении базы данных: {e}")
            con.rollback()  # Отмена изменений в случае ошибки

        finally:
            con.close()  # Закрытие соединения с базой данных
