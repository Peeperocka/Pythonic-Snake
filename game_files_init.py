import csv
import json
import os
import sqlite3

from contextlib import suppress

def create_files():
    if not os.path.exists('options.json'):
        with open('options.json', 'x', encoding='utf-8') as f:
            # База, не трогать
            initial_options = [
                {"name": "Базовые настройки", "updates_per_second": 10, "grid_size": 10,
                 "is_surrounded_by_walls": False},
            ]
            json.dump(initial_options, f, indent=4, ensure_ascii=False)

    if not os.path.exists('levels.csv'):
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            condition_type TEXT NOT NULL,
            condition_value INTEGER,
            level_name TEXT DEFAULT NULL
        )""")
    with suppress(sqlite3.IntegrityError):
        cur.execute("""
            INSERT INTO achievements (name, description, condition_type, condition_value)
            VALUES
                ("Окулист", "Набрать 500 очков", "score", 250),
                ("Очкоман", "Набрать 2000 очков", "score", 750),
                ("Очколюб", "Набрать 5000 очков", "score", 2500),
                ("Очковый барон", "Набрать 10000 очков", "score", 10000),
                ("Очковый король", "Набрать 50000 очков", "score", 50000),
                ("Очковый император", "Набрать 250000 очков", "score", 250000),
                ("Очковый бог", "Набрать 1000000 очков", "score", 1000000),
                ("Змей-гурман", "Съесть 100 единиц еды", "eat", 100),
                ("Змей-обжора", "Съесть 250 единиц еды", "eat", 250),
                ("Змей-гигант", "Съесть 500 единиц еды", "eat", 500),
                ("Черепаха", "Прожить 180 секунд (3 минуты)", "time", 180),
                ("Лентяй", "Прожить 300 секунд (5 минут)", "time", 300),
                ("Спящий змей", "Прожить 600 секунд (10 минут)", "time", 600),
                ("Змей, обманувший смерть", "Прожить 3600 секунд (1 час)", "time", 3600),
                ("Дружелюбни змейка", "Достигнуть длины 10", "length", 10),
                ("Подрастающая змейка", "Достигнуть длины 20", "length", 20),
                ("Длинная змейка", "Достигнуть длины 40", "length", 40),
                ("Гигантская змейка", "Достигнуть длины 60", "length", 60),
                ("Анаконда", "Достигнуть длины 80", "length", 80),
                ("Змей-Горыныч", "Достигнуть длины 100", "length", 100)
        """)

    conn.commit()
    conn.close()
