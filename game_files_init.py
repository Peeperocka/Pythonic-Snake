import csv
import json
import os
import sqlite3


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

    conn.commit()
    conn.close()
