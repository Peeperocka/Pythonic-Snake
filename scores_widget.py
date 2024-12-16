import csv

import sqlite3

from PyQt6 import uic

from PyQt6.QtWidgets import (QWidget, QTableWidgetItem, QHeaderView)


class Scores(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("QT files/scores.ui", self)

        self.update_levels()
        self.levelChooseBox.currentTextChanged.connect(self.on_levelchoose_changed)

        self.fill_scores_table()

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
