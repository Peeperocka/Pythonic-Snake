import sqlite3

from PyQt6 import uic

from PyQt6.QtWidgets import (QWidget, QTableWidgetItem, QHeaderView, QMessageBox)


class Achievements(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("QT files/achievements.ui", self)

        self.update_achievements_table()
        self.resetButton.clicked.connect(self.reset_achievement)

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
