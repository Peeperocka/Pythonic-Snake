import csv
import json
import math

from PyQt6.QtCore import Qt, QRect
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QPainter, QBrush, QPen
from PyQt6.QtWidgets import QMessageBox, QMainWindow, QInputDialog
from models import *


class LevelDesigner(QMainWindow):
    def __init__(self) -> None:
        """Инициализирует окно редактора уровней."""
        super().__init__()
        self.setupUi(self)

        self.init_difficulty_box()
        self.update_field_size()
        self.set_window_size()

        self.loadButton.clicked.connect(self.load_level)
        self.saveButton.clicked.connect(self.save_level)

        # Список доступных инструментов, отсортированный по имени в дизайнере
        self.tools = sorted(ITEMS_CLASSES, key=lambda x: x.designer_name)
        # Связь между кнопками, выпадающими списками и выбранными инструментами
        self.item_widgets = [
            {"button": self.firstItemButton, "combobox": self.firstItemBox},
            {"button": self.secondItemButton, "combobox": self.secondItemBox},
            {"button": self.thirdItemButton, "combobox": self.thirdItemBox}
        ]

        # Настройка виджетов инструментов
        for index, item_widget in enumerate(self.item_widgets):
            button = item_widget["button"]
            combobox = item_widget["combobox"]

            # Добавление всех инструментов в выпадающий список
            for tool in self.tools:
                combobox.addItem(tool.designer_name)

            # Установка выбранного инструмента по умолчанию
            selected_tool = self.tools[index % len(self.tools)]
            combobox.setCurrentText(selected_tool.designer_name)
            button.setText(selected_tool.designer_name)
            item_widget["selected_tool"] = selected_tool  # Сохранение ссылки на выбранный инструмент

            # Подключение слотов для обработки событий
            combobox.currentIndexChanged.connect(self.change_comboboxes_items)
            button.clicked.connect(self.tool_button_clicked)

        # Установка инструмента по умолчанию
        self.selected_tool = self.tools[0]

    def setupUi(self, LevelDesigner):
        LevelDesigner.setObjectName("LevelDesigner")
        LevelDesigner.resize(800, 967)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LevelDesigner.sizePolicy().hasHeightForWidth())
        LevelDesigner.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=LevelDesigner)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.MainLayout = QtWidgets.QHBoxLayout()
        self.MainLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
        self.MainLayout.setSpacing(0)
        self.MainLayout.setObjectName("MainLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.firstItemButton = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.firstItemButton.sizePolicy().hasHeightForWidth())
        self.firstItemButton.setSizePolicy(sizePolicy)
        self.firstItemButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.firstItemButton.setObjectName("firstItemButton")
        self.horizontalLayout_2.addWidget(self.firstItemButton)
        self.firstItemBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.firstItemBox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.firstItemBox.sizePolicy().hasHeightForWidth())
        self.firstItemBox.setSizePolicy(sizePolicy)
        self.firstItemBox.setMinimumSize(QtCore.QSize(300, 20))
        self.firstItemBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.firstItemBox.setObjectName("firstItemBox")
        self.horizontalLayout_2.addWidget(self.firstItemBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.secondItemButton = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.secondItemButton.sizePolicy().hasHeightForWidth())
        self.secondItemButton.setSizePolicy(sizePolicy)
        self.secondItemButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.secondItemButton.setObjectName("secondItemButton")
        self.horizontalLayout_3.addWidget(self.secondItemButton)
        self.secondItemBox = QtWidgets.QComboBox(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.secondItemBox.sizePolicy().hasHeightForWidth())
        self.secondItemBox.setSizePolicy(sizePolicy)
        self.secondItemBox.setMinimumSize(QtCore.QSize(300, 20))
        self.secondItemBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.secondItemBox.setObjectName("secondItemBox")
        self.horizontalLayout_3.addWidget(self.secondItemBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.thirdItemButton = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thirdItemButton.sizePolicy().hasHeightForWidth())
        self.thirdItemButton.setSizePolicy(sizePolicy)
        self.thirdItemButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.thirdItemButton.setObjectName("thirdItemButton")
        self.horizontalLayout_4.addWidget(self.thirdItemButton)
        self.thirdItemBox = QtWidgets.QComboBox(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.thirdItemBox.sizePolicy().hasHeightForWidth())
        self.thirdItemBox.setSizePolicy(sizePolicy)
        self.thirdItemBox.setMinimumSize(QtCore.QSize(300, 20))
        self.thirdItemBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.thirdItemBox.setObjectName("thirdItemBox")
        self.horizontalLayout_4.addWidget(self.thirdItemBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSpacing(10)
        self.formLayout.setObjectName("formLayout")
        self.difficultyLabel = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.difficultyLabel.sizePolicy().hasHeightForWidth())
        self.difficultyLabel.setSizePolicy(sizePolicy)
        self.difficultyLabel.setObjectName("difficultyLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.difficultyLabel)
        self.difficultyBox = QtWidgets.QComboBox(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.difficultyBox.sizePolicy().hasHeightForWidth())
        self.difficultyBox.setSizePolicy(sizePolicy)
        self.difficultyBox.setObjectName("difficultyBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.difficultyBox)
        self.verticalLayout_3.addLayout(self.formLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        spacerItem2 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.MainLayout.addLayout(self.horizontalLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.loadButton.setObjectName("loadButton")
        self.verticalLayout.addWidget(self.loadButton)
        self.saveButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.saveButton.setObjectName("saveButton")
        self.verticalLayout.addWidget(self.saveButton)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.MainLayout.addLayout(self.verticalLayout)
        self.verticalLayout_4.addLayout(self.MainLayout)
        spacerItem4 = QtWidgets.QSpacerItem(40, 800, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_4.addItem(spacerItem4)
        LevelDesigner.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=LevelDesigner)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        LevelDesigner.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=LevelDesigner)
        self.statusbar.setObjectName("statusbar")
        LevelDesigner.setStatusBar(self.statusbar)

        self.retranslateUi(LevelDesigner)
        QtCore.QMetaObject.connectSlotsByName(LevelDesigner)

    def retranslateUi(self, LevelDesigner):
        _translate = QtCore.QCoreApplication.translate
        LevelDesigner.setWindowTitle(_translate("LevelDesigner", "Редактор Уровня"))
        self.firstItemButton.setText(_translate("LevelDesigner", " Предмет 1"))
        self.secondItemButton.setText(_translate("LevelDesigner", "Предмет 2"))
        self.thirdItemButton.setText(_translate("LevelDesigner", "Предмет 3"))
        self.difficultyLabel.setText(_translate("LevelDesigner", "Cложность"))
        self.loadButton.setText(_translate("LevelDesigner", "Загрузить"))
        self.saveButton.setText(_translate("LevelDesigner", "Сохранить"))

    def init_difficulty_box(self):
        """Загружает параметры сложности из файла options.json."""
        with open('options.json', 'r', encoding='utf-8') as f:
            options = json.load(f)
            difficulty_options_names = [option["name"] for option in options]

        self.difficultyBox.addItems(difficulty_options_names)
        self.difficultyBox.currentIndexChanged.connect(self.update_field_size)

    def change_comboboxes_items(self):
        """Обновляет выбранный инструмент после изменения в выпадающем списке."""
        sender_combobox = self.sender()
        for item_widget in self.item_widgets:
            if item_widget["combobox"] == sender_combobox:
                selected_tool_name = sender_combobox.currentText()
                item_widget["selected_tool"] = next(
                    (tool for tool in self.tools if tool.designer_name == selected_tool_name), None)
                item_widget["button"].setText(selected_tool_name)
                break

    def tool_button_clicked(self):
        """Обновляет выбранный инструмент после нажатия на кнопку."""
        sender_button = self.sender()
        for item_widget in self.item_widgets:
            if item_widget["button"] == sender_button:
                self.selected_tool = item_widget["selected_tool"]
                break

    def update_field_size(self):
        """Обновляет размер игрового поля в соответствии с выбранной сложностью."""
        try:
            with open('options.json', 'r', encoding='utf-8') as f:
                options = json.load(f)
                # Находим параметр сложности по имени из выпадающего списка
                difficulty_option = next(
                    (option for option in options if option["name"] == self.difficultyBox.currentText()), None)
                if difficulty_option:
                    self.field_size = difficulty_option["grid_size"]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки настроек: {e}")
            return

        self.init_field()
        self.pen_width = math.ceil(self.tile_size / 7)
        self.update()

    def init_field(self):
        """Инициализирует игровое поле нулями."""
        self.field = [[0] * self.field_size for _ in range(self.field_size)]
        self.set_window_size()

    def set_window_size(self):
        """Устанавливает размер окна в зависимости от размера поля."""
        self.tile_size = 800 // self.field_size
        ideal_size = self.field_size * self.tile_size + 1
        self.setFixedSize(ideal_size, ideal_size + 115)

    def mousePressEvent(self, event):
        """Обрабатывает нажатие мыши для размещения/удаления объектов."""
        super().mousePressEvent(event)
        row = int(event.position().x() // self.tile_size)
        col = int((event.position().y() - 100) // self.tile_size)

        if 0 <= row < self.field_size and 0 <= col < self.field_size:
            if event.button() == Qt.RightButton:
                self.field[row][col] = 0  # Удаление объекта правой кнопкой мыши
            else:
                self.field[row][col] = self.selected_tool  # Размещение объекта левой кнопкой мыши
            self.update()

    def paintEvent(self, event):
        """Перерисовывает игровое поле."""
        qp = QPainter(self)
        for i in range(self.field_size):
            for j in range(self.field_size):
                # Рисуем рамку ячейки
                qp.setPen(QPen(QColor(255, 0, 0), 0))
                qp.setBrush(QBrush(QColor(0, 0, 0, 0)))
                qp.drawRect(QRect(i * self.tile_size, j * self.tile_size + 100, self.tile_size, self.tile_size))

                # Рисуем объект, если он есть
                if self.field[i][j]:
                    qp.setBrush(QBrush(self.field[i][j].body_color))
                    qp.setPen(QPen(self.field[i][j].edge_color, self.pen_width))
                    qp.drawRect(QRect(int(i * self.tile_size + self.pen_width / 2),
                                      int(j * self.tile_size + 100 + self.pen_width / 2),
                                      int(self.tile_size - self.pen_width),
                                      int(self.tile_size - self.pen_width)))

    def load_level(self):
        """Загружает данные уровня из CSV файла."""
        levelname, ok = QInputDialog.getText(self, "Загрузка файла", "Название уровня:")
        if not ok or not levelname:
            return

        with open('levels.csv', 'r', encoding='utf-8') as levels_file:
            levels = csv.reader(levels_file)
            next(levels)  # Skip header row

            try:
                for level in levels:
                    if level[0] == levelname:
                        level_options = level[1]
                        level_items = json.loads(level[2])
                        break
                else:
                    QMessageBox.warning(self, "Ошибка", f"Уровня '{levelname}' не существует.")
                    return
            except (json.JSONDecodeError, IndexError) as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка чтения файла: {e}")
                return

        # Создаем словарь для быстрого доступа к классам по имени
        classes_names = {cls.designer_name: cls for cls in ITEMS_CLASSES}

        self.difficultyBox.setCurrentText(level_options)
        self.init_field()

        for item_data in level_items:
            try:
                self.field[int(item_data['x'])][int(item_data['y'])] = classes_names[item_data['class']]
            except (KeyError, IndexError) as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при загрузке данных уровня: {e}")
                return

        self.update()
        self.statusBar().showMessage(f"Уровень '{levelname}' загружен.")

    def save_level(self):
        """Сохраняет текущий уровень в CSV файл."""
        levelname, ok = QInputDialog.getText(self, "Сохранение файла", "Название уровня:")
        if not ok or not levelname:
            return

        level_items = []
        has_snake = False

        for row in range(self.field_size):
            for col in range(self.field_size):
                if self.field[row][col]:
                    level_items.append({
                        'x': row,
                        'y': col,
                        'class': self.field[row][col].designer_name
                    })
                    if isinstance(self.field[row][col], SnakeHead):
                        if has_snake:
                            QMessageBox.warning(self, "Ошибка", "Уровень может содержать только одну змею.")
                            return
                        has_snake = True

        if not has_snake:
            QMessageBox.warning(self, "Ошибка", "Уровень должен содержать змею.")
            return

        with open('levels.csv', 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            level_exists = False

            for i, row in enumerate(rows):
                if row['name'] == levelname:
                    level_exists = True
                    reply = QMessageBox.question(
                        self, "Перезапись уровня",
                        f"Уровень '{levelname}' уже существует. Перезаписать?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        rows[i] = {'name': levelname, 'option_name': self.difficultyBox.currentText(),
                                   'items': json.dumps(level_items, ensure_ascii=False)}
                        break
                    else:
                        return

        if not level_exists:
            rows.append({'name': levelname, 'option_name': self.difficultyBox.currentText(),
                         'items': json.dumps(level_items, ensure_ascii=False)})

        with open('levels.csv', 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['name', 'option_name', 'items']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        self.statusBar().showMessage(f"Уровень '{levelname}' сохранен.")
