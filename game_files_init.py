import csv
import json
import sqlite3

from contextlib import suppress


def create_files():
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
