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
        """Инициализирует игру змейка, загружая уровень."""
        super().__init__()
        # Создаем словарь для быстрого доступа к классам элементов по имени
        self.classes_names = {cls.designer_name: cls for cls in ITEMS_CLASSES}
        self.load_level(level)  # Загрузка уровня при создании объекта
        self.pen_width = math.ceil(self.tile_size / 7)

    def load_level(self, levelname: str):
        """Загружает уровень из CSV файла и инициализирует игру."""
        self.levelname = levelname
        self.apples_eaten = 0  # Счётчик съеденных яблок
        self.tick = 0  # Счётчик тиков игры
        self.new_direction = "right"  # Направление движения змейки

        try:
            with open('levels.csv', 'r', encoding='utf-8') as levels_file:
                levels = csv.reader(levels_file)
                next(levels)  # Пропуск заголовка
                for level in levels:
                    if level[0] == levelname:
                        self.difficulty_name = level[1]
                        self.items_json = json.loads(level[2])
                        break  # Выход из цикла после нахождения уровня
                else:
                    raise FileNotFoundError(f"Уровень '{levelname}' не найден.")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки уровня: {e}")
            QApplication.quit()
            return

        try:
            with open('options.json', 'r', encoding='utf-8') as options_file:
                options = json.load(options_file)
                # Находим параметры сложности по имени
                self.selected_options = next(
                    (option for option in options if option["name"] == self.difficulty_name), None)
                if self.selected_options is None:
                    raise ValueError(f"Параметры сложности '{self.difficulty_name}' не найдены.")

        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки параметров: {e}")
            QApplication.quit()
            return

        # Установка размера окна после успешной загрузки параметров
        self.set_window_size(self.selected_options['grid_size'])
        self.level_items = {}

        for item_data in self.items_json:
            x, y = int(item_data['x']), int(item_data['y'])
            # Добавляем элементы уровня с учётом размера тайла
            self.level_items.setdefault(item_data["class"], []).append(
                self.classes_names[item_data['class']](x * self.tile_size, y * self.tile_size))

        # Настройка таймера игры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game_state)
        self.timer.start(round((1000 / self.selected_options['updates_per_second'])))

    def set_window_size(self, field_size: int) -> None:
        """Устанавливает размер окна игры в зависимости от размера поля."""
        self.field_size = field_size
        screen_size = QApplication.primaryScreen().availableGeometry()
        max_tile_size = min(screen_size.width() // self.field_size,
                            screen_size.height() // self.field_size)
        self.tile_size = max_tile_size
        ideal_size = self.field_size * self.tile_size
        self.setFixedSize(ideal_size, ideal_size)

    def update_game_state(self):
        """Основной игровой цикл."""
        self.tick += 1
        self.spawn_food()
        self.move_snake()
        self.check_collision()
        self.update()

    def closeEvent(self, event):
        """Остановить таймер при закрытии окна."""
        self.timer.stop()
        event.accept()

    def spawn_food(self):
        """Генерирует еду с вероятностью 10%."""
        if random.random() < 0.1:
            x = random.randrange(0, self.field_size) * self.tile_size
            y = random.randrange(0, self.field_size) * self.tile_size

            # Проверка на возможность размещения еды
            can_spawn = True
            for items in self.level_items.values():
                for item in items:
                    if item.x == x and item.y == y:
                        can_spawn = False
                        break
                if not can_spawn:
                    break

            if can_spawn:
                self.level_items.setdefault("Еда", []).append(Food(x, y))

    def keyPressEvent(self, event):
        """Обрабатывает нажатие клавиш для управления змейкой."""
        allowed_keys = {
            Qt.Key_W: "up",
            Qt.Key_A: "left",
            Qt.Key_S: "down",
            Qt.Key_D: "right"
        }
        if event.key() in allowed_keys and self.new_direction != allowed_keys[event.key()]:
            self.new_direction = allowed_keys[event.key()]

    def paintEvent(self, event):
        """Рисует игровое поле и все элементы на нём."""
        qp = QPainter(self)
        qp.fillRect(self.rect(), Qt.black)
        self.draw_level_items(qp)

    def draw_level_items(self, qp: QPainter):
        """Рисует все элементы уровня."""
        for items in self.level_items.values():
            for item in items:
                pen = QPen(item.edge_color, self.pen_width)
                qp.setPen(pen)
                qp.setBrush(QBrush(item.body_color))
                rect = QRect(item.x + self.pen_width // 2, item.y + self.pen_width // 2,
                             self.tile_size - self.pen_width, self.tile_size - self.pen_width)
                qp.drawRect(rect)

    def move_snake(self):
        """Перемещает змейку."""
        head = self.level_items["Змея"][0]
        new_head_x = head.x
        new_head_y = head.y

        opposite_directions = {"up": "down", "down": "up", "left": "right", "right": "left"}
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

        # Обработка столкновений со стенами в зависимости от настроек
        if self.selected_options.get("is_surrounded_by_walls", False):
            if (new_head_x < 0 or new_head_x >= self.field_size * self.tile_size or
                    new_head_y < 0 or new_head_y >= self.field_size * self.tile_size):
                self.game_over()
                return
        else:  # Телепортация через стены
            new_head_x = new_head_x % (self.field_size * self.tile_size)
            new_head_y = new_head_y % (self.field_size * self.tile_size)

        # Перемещение сегментов змеи
        new_coords = [(new_head_x, new_head_y)]
        for i in range(1, len(self.level_items["Змея"])):
            new_coords.append((self.level_items["Змея"][i - 1].x, self.level_items["Змея"][i - 1].y))
        for i, (x, y) in enumerate(new_coords):
            self.level_items["Змея"][i].x, self.level_items["Змея"][i].y = x, y

    def check_collision(self):
        """Проверяет столкновения змейки с другими объектами."""
        head = self.level_items["Змея"][0]
        for item_name, items in self.level_items.items():
            for item in items:
                if head.x == item.x and head.y == item.y:
                    if item_name == "Еда":
                        # Добавление нового сегмента змеи при поедании еды
                        last_segment = self.level_items["Змея"][-1]
                        new_segment = SnakeTile(last_segment.x, last_segment.y)
                        self.level_items["Змея"].append(new_segment)
                        self.level_items["Еда"].remove(item)
                        self.apples_eaten += 1
                    elif item_name == "Стена" or (item_name == "Змея" and item is not head):
                        # Игра заканчивается при столкновении со стеной или собой
                        self.game_over()
                    break  # Выход из внутреннего цикла после обнаружения столкновения

    def check_achievements(self, curr_score, lifetime, snake_length):
        """Проверяет и разблокирует достижения."""
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
        """Обрабатывает окончание игры."""
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
                    ORDER BY score DESC
                """, (self.levelname,))
            all_level_scores = cur.fetchall()
            if all_level_scores:
                high_score = all_level_scores[0][0]
            else:
                high_score = 0

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка в работе с БД", str(e))
            QApplication.quit()
            return

        finally:
            conn.close()

        # Окно Game Over с предложением начать заново
        if QMessageBox.question(
                self, "Game Over",
                "Вы проиграли! Начать заново? \n"
                f"Результат: {curr_score} очков \n"
                f"Рекорд: {high_score} очков \n"
                f"Всего попыток: {len(all_level_scores) if all_level_scores else 0}",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.load_level(self.levelname)
        else:
            self.close()
