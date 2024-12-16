import json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QApplication, QMainWindow, QTableWidgetItem, QInputDialog


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

        try:
            with open('options.json', 'r', encoding='utf-8') as f:
                existing_options = json.load(f)

            for i, option in enumerate(existing_options):
                if option.get("name") == items["name"]:
                    # Настройка с таким именем уже существует, спрашиваем пользователя
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

            else:
                existing_options.append(items)

            with open('options.json', 'w', encoding='utf-8') as f:
                json.dump(existing_options, f, indent=4, ensure_ascii=False)

            self.statusBar().showMessage(f"Настройки сохранены как {items['name']}")

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка чтения файла options.json: {e}")
        except Exception as e:  # Общий обработчик ошибок
            QMessageBox.warning(self, "Ошибка", str(e))

    def load_option(self):
        option_name, ok = QInputDialog.getText(self, "Загрузка настроек", "Имя настройки:")

        if not (option_name and ok):
            return

        self.load_and_display_options(option_name)
