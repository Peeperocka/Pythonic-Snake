import csv
import datetime
import json
import math
import os
import random
import sqlite3
import sys

from contextlib import suppress

from PyQt6 import uic
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen
from PyQt6.QtWidgets import (QApplication, QWidget, QMessageBox,
                             QMainWindow, QTableWidgetItem, QInputDialog, QHeaderView)


class GameItem:
    body_color = QColor(255, 255, 255)
    edge_color = QColor(255, 255, 255)

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def get_coords(self) -> tuple:
        return self.x, self.y


class SnakeTile(GameItem):
    designer_name = 'Тело змеи'
    body_color = QColor(0, 128, 0)
    edge_color = QColor(0, 128, 0)

    def __init__(self, x: int = 0, y: int = 0) -> None:
        super().__init__(x, y)


class SnakeHead(SnakeTile):
    designer_name = 'Змея'
    body_color = QColor(0, 255, 0)
    edge_color = QColor(0, 255, 0)

    def __init__(self, x: int = 0, y: int = 0, direction: str = 'right') -> None:
        super().__init__(x, y)
        self.direction = direction


class Food(GameItem):
    designer_name = 'Еда'
    body_color = QColor(255, 0, 0)
    edge_color = QColor(128, 0, 0)

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y)


class Obstacle(GameItem):
    designer_name = 'Стена'
    body_color = QColor(128, 128, 128)
    edge_color = QColor(128, 128, 128)

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y)


ITEMS_CLASSES = [Food, Obstacle, SnakeHead]


class SettingsDesigner(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = uic.loadUi("QT files/gameOptions.ui", self)
        self.setFixedSize(400, 350)
        self.load_and_display_options()
        self.saveButton.clicked.connect(self.save_option)
        self.loadButton.clicked.connect(self.load_option)

    def load_and_display_options(self, option_name="Базовые настройки"):
        try:
            with open('options.json', 'r', encoding='utf-8') as f:
                options = json.load(f)

        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл options.json не найден.")
            QApplication.quit()

        for option in options:
            if option["name"] == option_name:
                selected_option = option
                break

        else:
            QMessageBox.warning(self, "Ошибка",
                                f"Не найдена настройка с названием '{option_name}'.")
            return

        self.tableWidget.setRowCount(len(selected_option))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Переменная", "Значение"])

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)

        row = 0
        for key, value in selected_option.items():
            item_key = QTableWidgetItem(str(key))
            item_value = QTableWidgetItem(str(value))

            if key == "option_id":
                item_value.setFlags(item_value.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.tableWidget.setItem(row, 0, item_key)
            item_key.setFlags(item_key.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tableWidget.setItem(row, 1, item_value)
            row += 1

    def get_tablewidget_items(self):
        data = {}

        for row in range(self.tableWidget.rowCount()):
            key_item = self.tableWidget.item(row, 0)
            value_item = self.tableWidget.item(row, 1)

            if key_item is not None and value_item is not None:
                key = key_item.text()
                value = value_item.text()

                if value.isdigit():
                    value = int(value)
                elif value.lower() in ["true", "false"]:
                    value = value.lower() == "true"

                data[key] = value

        return data

    def save_option(self):
        items = self.get_tablewidget_items()

        # Валидация введенных настроек
        try:
            for key, value in items.items():
                if key == "name":
                    if not isinstance(value, str):
                        raise ValueError("Имя должно быть строкой.")

                elif key == "grid_size":
                    if not isinstance(value, int) or value <= 0:
                        raise ValueError("Размер уровня должен быть "
                                         "положительным целым числом.")
                    elif not (9 < value < 61):
                        raise ValueError("Размер уровня должен быть в пределах от 10 до 60.")

                elif key == "updates_per_second":
                    if not isinstance(value, int) or value <= 0:
                        raise ValueError("Updates per second должно быть "
                                         "положительным целым числом.")
                    elif not (1 < value < 31):
                        print(value)
                        raise ValueError("Updates per second должен быть в пределах от 1 до 30.")

                elif key == "is_surrounded_by_walls":
                    if not isinstance(value, bool):
                        raise ValueError("is_surrounded_by_walls должно быть True/False.")

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка настроек", str(e))
            return

        # Пытаемся сохранить настройку
        try:
            with open('options.json', 'r', encoding='utf-8') as f:
                existing_options = json.load(f)

            for option in existing_options:
                if option.get("name") == items["name"]:
                    raise ValueError(f"Настройка с именем '{items['name']}' уже существует.")

            existing_options.append(items)

            with open('options.json', 'w', encoding='utf-8') as f:
                json.dump(existing_options, f, indent=4, ensure_ascii=False)

            self.statusBar().showMessage(f"Настройки сохранены как {items['name']}")

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка чтения файла options.json: {e}")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def load_option(self):
        option_name, ok = QInputDialog.getText(self, "Загрузка настроек", "Имя настройки:")

        if not (option_name and ok):
            return

        self.load_and_display_options(option_name)


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


class SnakeGame(QWidget):
    def __init__(self, level: str = 'Уровень') -> None:
        super().__init__()

        self.classes_names = {}
        for class_item in ITEMS_CLASSES:
            self.classes_names[class_item.designer_name] = class_item

        self.load_level(level)
        self.pen_width = math.ceil(self.tile_size / 7)

    def load_level(self, levelname: str):
        self.levelname = levelname

        with open('levels.csv', 'r', encoding='utf-8') as levels:
            levels = csv.reader(levels)
            next(levels)
            try:
                for level in levels:
                    if level[0] == levelname:
                        self.difficulty_name = level[1]
                        self.items_json = json.loads(level[2])

            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Ошибка при декодировании JSON: {e}")
                QApplication.quit()
                return

        with open('options.json', 'r', encoding='utf-8') as options:
            options = json.load(options)
            for option in options:
                if option["name"] == self.difficulty_name:
                    self.selected_options = option
                    break

        # Подключаем графику после удачного парсинга информации о уровне
        self.set_window_size(self.selected_options['grid_size'])

        self.level_items = {}

        for item_data in self.items_json:
            x, y = item_data['x'], item_data['y']
            self.level_items.setdefault(
                item_data["class"], []).append(
                self.classes_names[item_data['class']](x * self.tile_size,
                                                       y * self.tile_size))

        self.new_direction = "right"
        self.tick = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game_state)
        self.timer.start(round((1000 / self.selected_options['updates_per_second'])))

    def set_window_size(self, field_size: int) -> None:
        self.field_size = field_size
        screen_size = QApplication.primaryScreen().availableGeometry()
        max_tile_size = min(screen_size.width() // self.field_size,
                            screen_size.height() // self.field_size)
        self.tile_size = max_tile_size
        ideal_size = self.field_size * self.tile_size
        self.setFixedSize(ideal_size, ideal_size)

    def update_game_state(self):
        """Основной цикл игры"""
        self.tick += 1
        self.spawn_food()
        self.move_snake()
        self.check_collision()
        self.update()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

    def spawn_food(self):
        if random.random() < 0.1:
            x = random.randrange(0, self.field_size) * self.tile_size
            y = random.randrange(0, self.field_size) * self.tile_size

            can_spawn = True

            for item_name in self.level_items.keys():
                if any(segment.x == x and segment.y == y
                       for segment in self.level_items.get(item_name, [])):
                    can_spawn = False

            if can_spawn:
                self.level_items.setdefault("Еда", []).append(Food(x, y))

    def keyPressEvent(self, event):
        allowed_keys = {
            Qt.Key.Key_W: "up",
            Qt.Key.Key_A: "left",
            Qt.Key.Key_S: "down",
            Qt.Key.Key_D: "right"
        }
        if event.key() in allowed_keys.keys():
            self.new_direction = allowed_keys[event.key()]

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(self.rect(), Qt.GlobalColor.black)
        self.draw_level_items(qp)

    def draw_level_items(self, qp: QPainter):
        for item_name, items in self.level_items.items():
            for item in items:
                pen = QPen(item.edge_color, self.pen_width)
                qp.setPen(pen)
                qp.setBrush(QBrush(item.body_color))

                x, y = item.x, item.y

                rect = QRect(
                    x + self.pen_width // 2,
                    y + self.pen_width // 2,
                    self.tile_size - self.pen_width,
                    self.tile_size - self.pen_width,
                )
                qp.drawRect(rect)

    def move_snake(self):
        new_coords = []
        head = self.level_items["Змея"][0]

        new_head_x = head.x
        new_head_y = head.y

        opposite_directions = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left",
        }
        if self.new_direction != opposite_directions.get(head.direction):
            head.direction = self.new_direction

        if head.direction == "up":
            new_head_y -= self.tile_size
        elif head.direction == "down":
            new_head_y += self.tile_size
        elif head.direction == "left":
            new_head_x -= self.tile_size
        elif head.direction == "right":
            new_head_x += self.tile_size

        if self.selected_options.get("is_surrounded_by_walls", False):
            if new_head_x < 0 or new_head_x >= self.field_size * self.tile_size or \
                    new_head_y < 0 or new_head_y >= self.field_size * self.tile_size:
                self.game_over()
                return

        else:
            if new_head_x < 0:
                new_head_x = (self.field_size - 1) * self.tile_size
            elif new_head_x >= self.field_size * self.tile_size:
                new_head_x = 0

            if new_head_y < 0:
                new_head_y = (self.field_size - 1) * self.tile_size
            elif new_head_y >= self.field_size * self.tile_size:
                new_head_y = 0

        new_coords.append((new_head_x, new_head_y))

        for i in range(1, len(self.level_items["Змея"])):
            new_coords.append((self.level_items["Змея"][i - 1].x,
                               self.level_items["Змея"][i - 1].y))

        for i in range(len(self.level_items["Змея"])):
            self.level_items["Змея"][i].x = new_coords[i][0]
            self.level_items["Змея"][i].y = new_coords[i][1]

    def check_collision(self):
        head = self.level_items["Змея"][0]

        for item_name in self.level_items:
            for item in self.level_items.get(item_name, []):
                if head.x == item.x and head.y == item.y:
                    if item_name == "Еда":
                        last_segment = self.level_items["Змея"][-1]
                        new_segment = SnakeTile(last_segment.x, last_segment.y)
                        self.level_items["Змея"].append(new_segment)
                        self.level_items[item_name].remove(item)

                    elif item_name == "Стена":
                        self.game_over()
                    elif item_name == "Змея":
                        if (item.designer_name != "Змея"
                                and len(self.level_items["Змея"]) > 2):
                            self.game_over()

    def game_over(self):
        self.timer.stop()

        conn = sqlite3.connect("snake.db")
        cur = conn.cursor()

        curr_score = self.tick * (len(self.level_items["Змея"]) - 1)

        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lifetime = round(self.tick / self.selected_options['updates_per_second'], 2)
            snake_length = len(self.level_items["Змея"])

            cur.execute("""
                INSERT INTO scores (score, level_name, date, life_time_sec, snake_length)
                VALUES (?, ?, ?, ?, ?)
            """, (curr_score, self.levelname, now, lifetime, snake_length))

            conn.commit()

            cur.execute("""
                    SELECT score
                    FROM scores
                    WHERE level_name = ?
                    ORDER BY score
                """, (self.levelname,))

            all_level_scores = cur.fetchall()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка в работе с БД",
                                 str(e), QMessageBox.StandardButton.Ok)
            QApplication.quit()
            return

        finally:
            conn.close()

        if QMessageBox.question(
                self, "Game Over",
                "Вы проиграли! Начать заново? \n"
                f"Результат: {curr_score} очков \n"
                f"Рекорд: {all_level_scores[-1][0]} очков \n"
                f"Всего попыток: {len(all_level_scores)}",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No) \
                == QMessageBox.StandardButton.No:
            self.close()

        else:
            self.load_level(self.levelname)


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("QT files/main.ui", self)

        self.fill_level_choose_box()

        self.playButton.clicked.connect(self.open_snake_game)
        self.exitButton.clicked.connect(self.close)
        self.levelDesignerButton.clicked.connect(self.open_designer)
        self.settingsDesignerButton.clicked.connect(self.open_settings_designer)
        self.levelChoose.currentTextChanged.connect(self.on_levelchoose_changed)
        self.scoresButton.clicked.connect(self.open_scores)

    def on_levelchoose_changed(self):
        if self.levelChoose.currentText() == "Перезагрузить список":
            self.fill_level_choose_box()

    def fill_level_choose_box(self):
        self.levelChoose.clear()

        with open('levels.csv', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.levelChoose.addItem(row['name'])

        self.levelChoose.addItem("Перезагрузить список")

    def open_designer(self):
        self.designer = LevelDesigner()
        self.designer.show()
        self.designer.activateWindow()

    def open_snake_game(self):
        self.snake_game = SnakeGame(self.levelChoose.currentText())
        self.snake_game.show()
        self.snake_game.activateWindow()

    def open_settings_designer(self):
        self.settings_designer = SettingsDesigner()
        self.settings_designer.show()
        self.settings_designer.activateWindow()

    def open_scores(self):
        self.scores = Scores()
        self.scores.show()
        self.scores.activateWindow()


if __name__ == '__main__':
    with suppress(FileExistsError):
        with open('options.json', 'x', encoding='utf-8') as f:
            # База, не трогать
            initial_options = [
                {"name": "Базовые настройки", "updates_per_second": 10, "grid_size": 10,
                 "is_surrounded_by_walls": False},
            ]
            json.dump(initial_options, f, indent=4, ensure_ascii=False)

        with open('levels.csv', 'x', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['name', 'option_name', 'items'])
            json_data = json.dumps([{"x": 0, "y": 0, "class": "Змея"}])
            writer.writerow(["Базовый уровень", 'Базовые настройки', json_data])

    conn = sqlite3.connect('snake.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER NOT NULL,
            life_time_sec INTEGER NOT NULL,
            snake_length INTEGER NOT NULL,
            level_name TEXT NOT NULL,
            date TEXT NOT NULL
        )""")

    conn.commit()
    conn.close()

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
