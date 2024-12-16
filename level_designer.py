import csv
import json
import math
import os

from PyQt6 import uic
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QBrush, QPen
from PyQt6.QtWidgets import (QApplication, QMessageBox,
                             QMainWindow, QInputDialog)
from models import *


class LevelDesigner(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = uic.loadUi("QT files/levelDesigner.ui", self)

        self.init_difficulty_box()

        self.update_field_size()
        self.set_window_size()

        self.loadButton.clicked.connect(self.load_level)
        self.saveButton.clicked.connect(self.save_level)

        self.tools = sorted(ITEMS_CLASSES, key=lambda x: x.designer_name)

        self.item_widgets = [
            {"button": self.firstItemButton, "combobox": self.firstItemBox},
            {"button": self.secondItemButton, "combobox": self.secondItemBox},
            {"button": self.thirdItemButton, "combobox": self.thirdItemBox}
        ]

        for index, item_widget in enumerate(self.item_widgets):
            button = item_widget["button"]
            combobox = item_widget["combobox"]

            for tool in self.tools:
                combobox.addItem(tool.designer_name)

            selected_tool = self.tools[index % len(self.tools)]
            combobox.setCurrentText(selected_tool.designer_name)
            button.setText(selected_tool.designer_name)
            item_widget["selected_tool"] = selected_tool

            combobox.currentIndexChanged.connect(self.change_comboboxes_items)
            button.clicked.connect(self.tool_button_clicked)

        self.selected_tool = self.tools[0]

    def init_difficulty_box(self):
        with open('options.json', 'r', encoding='utf-8') as f:
            options = json.load(f)
            difficulty_options_names = [option["name"] for option in options]

        self.difficultyBox.addItems(difficulty_options_names)
        self.difficultyBox.currentIndexChanged.connect(self.update_field_size)

    def change_comboboxes_items(self):
        sender_combobox = self.sender()
        for item_widget in self.item_widgets:
            if item_widget["combobox"] == sender_combobox:
                selected_tool_name = sender_combobox.currentText()
                item_widget["selected_tool"] = next(
                    (tool for tool in self.tools if tool.designer_name == selected_tool_name), None)
                item_widget["button"].setText(selected_tool_name)
                break

    def tool_button_clicked(self):
        sender_button = self.sender()
        for item_widget in self.item_widgets:
            if item_widget["button"] == sender_button:
                self.selected_tool = item_widget["selected_tool"]
                break

    def update_field_size(self):
        try:
            with open('options.json', 'r', encoding='utf-8') as f:
                options = json.load(f)
                difficulty_option = next(
                    (option for option in options
                     if option["name"] == self.difficultyBox.currentText()), None)

                if difficulty_option:
                    self.field_size = difficulty_option["grid_size"]
                    self.init_field()

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка чтения файла options.json: {e}")
            QApplication.quit()
            return

        self.init_field()
        self.pen_width = math.ceil(self.tile_size / 7)
        self.update()

    def init_field(self):
        self.field = [[0] * self.field_size for _ in range(self.field_size)]
        self.set_window_size()

    def set_window_size(self):
        self.tile_size = 800 // self.field_size
        ideal_size = self.field_size * self.tile_size + 1
        self.setFixedSize(ideal_size, ideal_size + 115)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        row = int(event.position().x() // self.tile_size)
        col = int((event.position().y() - 100) // self.tile_size)

        if not (0 <= row < self.field_size and 0 <= col < self.field_size):
            return

        if event.button() == Qt.MouseButton.RightButton:
            self.field[row][col] = 0
        else:
            self.field[row][col] = self.selected_tool()

        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)

        for i in range(self.field_size):
            for j in range(self.field_size):
                qp.setPen(QPen(QColor(255, 0, 0), 0))
                qp.setBrush(QBrush(QColor(0, 0, 0, 0)))

                qp.drawRect(QRect(
                    (i * self.tile_size),
                    (j * self.tile_size) + 100,
                    self.tile_size, self.tile_size
                ))

                if self.field[i][j] != 0:
                    qp.setBrush(QBrush(self.field[i][j].body_color))
                    qp.setPen(QPen(self.field[i][j].edge_color, self.pen_width))

                    qp.drawRect(QRect(
                        int(i * self.tile_size + self.pen_width / 2),
                        int(j * self.tile_size + 100 + self.pen_width / 2),
                        int(self.tile_size - self.pen_width),
                        int(self.tile_size - self.pen_width)
                    ))

    def load_level(self):
        levelname, ok = QInputDialog.getText(self, "Загрузка файла", "Название уровня:")
        if not (levelname and ok):
            return

        with open('levels.csv', 'r', encoding='utf-8') as levels:
            levels = csv.reader(levels)
            next(levels)
            try:
                for level in levels:
                    if level[0] == levelname:
                        level_options = level[1]
                        level_items = json.loads(level[2])
                        break
                else:
                    QMessageBox.warning(self, "Ошибка", f"Уровня с именем '{levelname}' не существует.")
                    return
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при декодировании JSON: {e}")
                return

        classes_names = {}
        for class_item in ITEMS_CLASSES:
            classes_names[class_item.designer_name] = class_item

        self.difficultyBox.setCurrentText(level_options)

        self.init_field()

        for item_data in level_items:
            self.field[int(item_data['x'])][item_data['y']] = classes_names[item_data['class']]

        self.update()
        self.statusBar().showMessage(f"Уровень '{levelname}' успешно загружен.")

    def save_level(self):
        levelname, ok = QInputDialog.getText(self, "Сохранение файла", "Название уровня:")
        if not (levelname and ok):
            return

        with open('levels.csv', 'r', encoding='utf-8') as levels:
            levels = csv.DictReader(levels)

            for level in levels:
                if level['name'] == levelname:
                    QMessageBox.warning(self, "Ошибка", f"Уровень с именем '{levelname}' уже существует.")
                    return

        level_items = []

        has_snake = False

        for row in range(self.field_size):
            for col in range(self.field_size):
                if self.field[row][col] != 0:
                    level_items.append({
                        'x': row,
                        'y': col,
                        'class': self.field[row][col].designer_name
                    })

                    if isinstance(self.field[row][col], SnakeHead):
                        if has_snake:
                            QMessageBox.warning(self, "Ошибка",
                                                f"Уровень не может более 1 змеи.")
                            return

                        has_snake = True

        if not has_snake:
            QMessageBox.warning(self, "Ошибка", f"Уровень должен содержать змею.")
            return

        file_exists = os.path.exists('levels.csv')

        with open('levels.csv', 'a', encoding='utf-8', newline='') as levels:
            writer = csv.writer(levels)
            if not file_exists:
                writer.writerow(['levelname', 'difficulty', 'items'])
            writer.writerow([levelname, self.difficultyBox.currentText(),
                             json.dumps(level_items, ensure_ascii=False)])

        self.statusBar().showMessage(f"Уровень '{levelname}' успешно сохранен.")
