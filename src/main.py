import csv
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from level_designer import LevelDesigner
from game import SnakeGame
from settings_designer import SettingsDesigner
from scores_widget import Scores
from game_files_init import create_files
from achievements_widget import Achievements
from PyQt6 import QtCore, QtWidgets


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.fill_level_choose_box()

        self.playButton.clicked.connect(self.open_snake_game)
        self.exitButton.clicked.connect(self.close)
        self.levelDesignerButton.clicked.connect(self.open_designer)
        self.settingsDesignerButton.clicked.connect(self.open_settings_designer)
        self.levelChoose.currentTextChanged.connect(self.on_levelchoose_changed)
        self.scoresButton.clicked.connect(self.open_scores)
        self.achievementsButton.clicked.connect(self.open_achievements)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(250, 400)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 252, 351))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.playButton = QtWidgets.QPushButton(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playButton.sizePolicy().hasHeightForWidth())
        self.playButton.setSizePolicy(sizePolicy)
        self.playButton.setMinimumSize(QtCore.QSize(250, 100))
        self.playButton.setObjectName("playButton")
        self.verticalLayout.addWidget(self.playButton)
        spacerItem = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.levelChooseLabel = QtWidgets.QLabel(parent=self.layoutWidget)
        self.levelChooseLabel.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.levelChooseLabel.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.levelChooseLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.levelChooseLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.levelChooseLabel.setObjectName("levelChooseLabel")
        self.verticalLayout.addWidget(self.levelChooseLabel)
        self.levelChoose = QtWidgets.QComboBox(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.levelChoose.sizePolicy().hasHeightForWidth())
        self.levelChoose.setSizePolicy(sizePolicy)
        self.levelChoose.setMinimumSize(QtCore.QSize(250, 25))
        self.levelChoose.setObjectName("levelChoose")
        self.verticalLayout.addWidget(self.levelChoose)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.scoresButton = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.scoresButton.setObjectName("scoresButton")
        self.verticalLayout.addWidget(self.scoresButton)
        self.achievementsButton = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.achievementsButton.setObjectName("achievementsButton")
        self.verticalLayout.addWidget(self.achievementsButton)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.levelDesignerButton = QtWidgets.QPushButton(parent=self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.levelDesignerButton.sizePolicy().hasHeightForWidth())
        self.levelDesignerButton.setSizePolicy(sizePolicy)
        self.levelDesignerButton.setMinimumSize(QtCore.QSize(250, 25))
        self.levelDesignerButton.setObjectName("levelDesignerButton")
        self.verticalLayout.addWidget(self.levelDesignerButton)
        self.settingsDesignerButton = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.settingsDesignerButton.setObjectName("settingsDesignerButton")
        self.verticalLayout.addWidget(self.settingsDesignerButton)
        self.exitButton = QtWidgets.QPushButton(parent=self.layoutWidget)
        self.exitButton.setObjectName("exitButton")
        self.verticalLayout.addWidget(self.exitButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 250, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.playButton.setText(_translate("MainWindow", "Играть"))
        self.levelChooseLabel.setText(_translate("MainWindow", "Выбор уровня"))
        self.scoresButton.setText(_translate("MainWindow", "Результаты"))
        self.achievementsButton.setText(_translate("MainWindow", "Достижения"))
        self.levelDesignerButton.setText(_translate("MainWindow", "Редактор уровней"))
        self.settingsDesignerButton.setText(_translate("MainWindow", "Редактор сложности"))
        self.exitButton.setText(_translate("MainWindow", "Выход"))

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

    def open_achievements(self):
        self.achievements = Achievements()
        self.achievements.show()
        self.achievements.activateWindow()


if __name__ == '__main__':
    create_files()

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
