# src/models/direction.py
from enum import Enum

class Direction(Enum):
    """Направление движения автомобиля"""
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"

    def opposite(self) -> 'Direction':
        """Получить противоположное направление"""
        return Direction.RIGHT_TO_LEFT if self == Direction.LEFT_TO_RIGHT else Direction.LEFT_TO_RIGHT
