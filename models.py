from PyQt6.QtGui import QColor


class GameItem:
    body_color = QColor(255, 255, 255)
    edge_color = QColor(255, 255, 255)

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def get_coords(self) -> tuple:
        return self.x, self.y


class SnakeTile(GameItem):
    designer_name = 'Тело змеи'
    body_color = QColor(0, 128, 0)
    edge_color = QColor(0, 128, 0)

    def __init__(self, x: int = 0, y: int = 0) -> None:
        super().__init__(x, y)


class SnakeHead(SnakeTile):
    designer_name = 'Змея'
    body_color = QColor(0, 255, 0)
    edge_color = QColor(0, 255, 0)

    def __init__(self, x: int = 0, y: int = 0, direction: str = 'right') -> None:
        super().__init__(x, y)
        self.direction = direction


class Food(GameItem):
    designer_name = 'Еда'
    body_color = QColor(255, 0, 0)
    edge_color = QColor(128, 0, 0)

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y)


class Obstacle(GameItem):
    designer_name = 'Стена'
    body_color = QColor(128, 128, 128)
    edge_color = QColor(128, 128, 128)

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y)


# Объекты, которые будут доступны к работе в редакторе уровня
ITEMS_CLASSES = [Food, Obstacle, SnakeHead]
