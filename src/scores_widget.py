import csv

import sqlite3

from PyQt6.QtWidgets import (QWidget, QTableWidgetItem, QHeaderView)
from PyQt6 import QtCore, QtWidgets


class Scores(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.update_levels()
        self.levelChooseBox.currentTextChanged.connect(self.on_levelchoose_changed)

        self.fill_scores_table()

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
        if self.levelChooseBox.currentText() == "Перезагрузить список":
            self.update_levels()
            return 0

        self.fill_scores_table()

    def update_levels(self):
        with open('levels.csv', 'r', encoding="utf-8") as f:
            levels = csv.reader(f)
            next(levels)
            levels = [level[0] for level in levels]

        self.levelChooseBox.clear()
        self.levelChooseBox.addItems(level for level in levels)
        self.levelChooseBox.addItem("Перезагрузить список")

    def fill_scores_table(self):
        self.tableWidget.clearContents()

        con = sqlite3.connect("snake.db")

        cur = con.cursor()
        level_scores = cur.execute(f"""
            SELECT score, date, life_time_sec, snake_length FROM scores
                WHERE level_name = ?
                ORDER BY score DESC""", (self.levelChooseBox.currentText(),)).fetchall()

        if not level_scores:
            self.tableWidget.setColumnCount(1)
            self.tableWidget.setHorizontalHeaderLabels(["Нет результатов"])
            self.tableWidget.setRowCount(1)
            self.tableWidget.setItem(0, 0, QTableWidgetItem("Нет результатов"))
            self.tableWidget.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.Stretch
            )
            return

        column_headers = ["Результат", "Дата", "Время жизни", "Длина змеи"]

        self.tableWidget.setColumnCount(len(column_headers))
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        self.tableWidget.setRowCount(len(level_scores))

        for row in range(len(level_scores)):
            for col, value in enumerate(level_scores[row]):
                item_score = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row, col, item_score)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
