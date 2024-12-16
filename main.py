import csv
import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow

from level_designer import LevelDesigner
from game import SnakeGame
from settings_designer import SettingsDesigner
from scores_widget import Scores
from game_files_init import create_files


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
    create_files()

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
