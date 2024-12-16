import csv
import datetime
import json
import math

import random
import sqlite3

from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QPainter, QBrush, QPen
from PyQt6.QtWidgets import (QApplication, QWidget, QMessageBox)

from models import *


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
        self.apples_eaten = 0
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
                        self.apples_eaten += 1

                    elif item_name == "Стена":
                        self.game_over()

                    elif item_name == "Змея":
                        if (item.designer_name != "Змея"
                                and len(self.level_items["Змея"]) > 2):
                            self.game_over()

    def check_achievements(self, curr_score, lifetime, snake_length):
        conn = sqlite3.connect("snake.db")
        cur = conn.cursor()

        try:
            achievements = cur.execute("""
                SELECT id, condition_type, condition_value 
                FROM achievements
                WHERE level_name is NULL
            """).fetchall()

            for achievement_id, condition_type, condition_value in achievements:
                unlocked = False
                if condition_type == "score" and condition_value <= curr_score:
                    unlocked = True
                elif condition_type == "eat" and condition_value <= self.apples_eaten:
                    unlocked = True
                elif condition_type == "length" and condition_value <= snake_length:
                    unlocked = True
                elif condition_type == "time" and condition_value <= lifetime:
                    unlocked = True

                if unlocked:
                    cur.execute("""
                        UPDATE achievements 
                        SET level_name = ?
                        WHERE id = ?
                    """, (self.levelname, achievement_id))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка в работе с БД", str(e))
            conn.rollback()
        finally:
            conn.commit()
            conn.close()

    def game_over(self):
        self.timer.stop()

        conn = sqlite3.connect("snake.db")
        cur = conn.cursor()

        curr_score = self.tick * (len(self.level_items["Змея"]) - 1)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lifetime = round(self.tick / self.selected_options['updates_per_second'], 2)
        snake_length = len(self.level_items["Змея"])

        self.check_achievements(curr_score, lifetime, snake_length)

        try:

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
