import sqlite3

from PyQt6.QtWidgets import (QWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6 import QtCore, QtWidgets


class Achievements(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

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
        self.tableWidget.clearContents()
        con = sqlite3.connect("snake.db")

        cur = con.cursor()
        achievements = cur.execute("""
            SELECT name, description, level_name FROM achievements
            WHERE level_name is not NULL""").fetchall()

        if not achievements:
            self.tableWidget.setColumnCount(1)
            self.tableWidget.setHorizontalHeaderLabels(["Нет достижений"])
            self.tableWidget.setRowCount(1)
            self.tableWidget.setItem(0, 0, QTableWidgetItem("Нет достижений"))
            self.tableWidget.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.Stretch
            )
            return

        column_headers = ["Название", "Описание", "Получена на"]

        self.tableWidget.setColumnCount(len(column_headers))
        self.tableWidget.setHorizontalHeaderLabels(column_headers)
        self.tableWidget.setRowCount(len(achievements))

        for row in range(len(achievements)):
            for col in range(len(achievements[0])):
                item = QTableWidgetItem(str(achievements[row][col]))
                self.tableWidget.setItem(row, col, item)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)

    def reset_achievement(self):
        selected_row = [item.text() for item in self.tableWidget.selectedItems()]

        con = sqlite3.connect("snake.db")
        cur = con.cursor()

        try:
            cur.execute("""
                  UPDATE achievements 
                  SET level_name = NULL  -- <<<---  Устанавливаем level_name = NULL
                  WHERE name = ? AND description = ?
              """, (selected_row[0], selected_row[1]))
            con.commit()
            self.update_achievements_table()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка при сбросе", f"Ошибка при обновлении базы данных: {e}")
            con.rollback()

        finally:
            con.close()
