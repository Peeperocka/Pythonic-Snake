import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QApplication, QMainWindow, QTableWidgetItem, QInputDialog
from PyQt6 import QtCore, QtWidgets


class SettingsDesigner(QMainWindow):
    def __init__(self) -> None:
        """Инициализирует окно настроек."""
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(400, 350)
        self.load_and_display_options()  # Загрузка и отображение базовых настроек при запуске
        self.saveButton.clicked.connect(self.save_option)
        self.loadButton.clicked.connect(self.load_option)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(402, 368)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(260, 0, 141, 321))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loadButton = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.loadButton.setObjectName("loadButton")
        self.verticalLayout.addWidget(self.loadButton)
        self.saveButton = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.saveButton.setObjectName("saveButton")
        self.verticalLayout.addWidget(self.saveButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.tableWidget = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 261, 321))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 402, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Редактор Настроек Игры"))
        self.loadButton.setText(_translate("MainWindow", "Загрузить"))
        self.saveButton.setText(_translate("MainWindow", "Сохранить"))

    def load_and_display_options(self, option_name="Базовые настройки"):
        """Загружает и отображает настройки из файла options.json."""
        try:
            with open('options.json', 'r', encoding='utf-8') as f:
                options = json.load(f)
        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "Файл options.json не найден.")
            QApplication.quit()
            return  # Добавлено для предотвращения дальнейшего выполнения после ошибки

        # Поиск настроек по имени
        for option in options:
            if option["name"] == option_name:
                selected_option = option
                break
        else:  # Выполняется, если цикл for завершился без break (настройки не найдены)
            QMessageBox.warning(self, "Ошибка",
                                f"Не найдена настройка с названием '{option_name}'.")
            return

        # Отображение настроек в таблице
        self.tableWidget.setRowCount(len(selected_option))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Переменная", "Значение"])

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)

        # Заполнение таблицы
        for row, (key, value) in enumerate(selected_option.items()):
            item_key = QTableWidgetItem(str(key))
            item_value = QTableWidgetItem(str(value))

            # Запрет редактирования поля option_id
            if key == "option_id":
                item_value.setFlags(item_value.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.tableWidget.setItem(row, 0, item_key)
            item_key.setFlags(item_key.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Запрет редактирования ключей
            self.tableWidget.setItem(row, 1, item_value)

    def get_tablewidget_items(self):
        """Извлекает данные из таблицы в словарь."""
        data = {}
        for row in range(self.tableWidget.rowCount()):
            key_item = self.tableWidget.item(row, 0)
            value_item = self.tableWidget.item(row, 1)

            if key_item is not None and value_item is not None:
                key = key_item.text()
                value = value_item.text()

                # Преобразование типов данных
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ["true", "false"]:
                    value = value.lower() == "true"

                data[key] = value
        return data

    def save_option(self):
        """Сохраняет настройки в файл options.json."""
        items = self.get_tablewidget_items()

        # Валидация данных
        try:
            for key, value in items.items():
                if key == "name":
                    if not isinstance(value, str):
                        raise ValueError("Имя должно быть строкой.")
                elif key == "grid_size":
                    if not isinstance(value, int) or value <= 0 or not (9 < value < 61):
                        raise ValueError("Размер уровня должен быть положительным целым числом от 10 до 60.")
                elif key == "updates_per_second":
                    if not isinstance(value, int) or value <= 0 or not (1 < value < 31):
                        raise ValueError("Updates per second должно быть положительным целым числом от 2 до 30.")
                elif key == "is_surrounded_by_walls":
                    if not isinstance(value, bool):
                        raise ValueError("is_surrounded_by_walls должно быть True/False.")

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка настроек", str(e))
            return

        try:
            with open('options.json', 'r', encoding='utf-8') as f:
                existing_options = json.load(f)

            # Поиск существующей настройки с тем же именем
            for i, option in enumerate(existing_options):
                if option.get("name") == items["name"]:
                    # Запрос на перезапись
                    reply = QMessageBox.question(
                        self, "Перезапись настройки",
                        f"Настройка с именем '{items['name']}' уже существует. Перезаписать?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        existing_options[i] = items
                        break
                    else:
                        return

            else:  # Если настройка с таким именем не найдена
                existing_options.append(items)

            with open('options.json', 'w', encoding='utf-8') as f:
                json.dump(existing_options, f, indent=4, ensure_ascii=False)

            self.statusBar().showMessage(f"Настройки сохранены как {items['name']}")

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка чтения файла options.json: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def load_option(self):
        """Загружает и отображает настройки по имени."""
        option_name, ok = QInputDialog.getText(self, "Загрузка настроек", "Имя настройки:")
        if not (option_name and ok):
            return
        self.load_and_display_options(option_name)
