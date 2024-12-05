# src/utils/input_reader.py
import csv
from typing import List, Tuple
from ..models.direction import Direction

class InputReader:
    @staticmethod
    def read_cars_data(filename: str) -> List[Tuple[float, int, Direction]]:
        """
        Читает данные о машинах из входного файла.
        Returns: List of (arrival_time, car_id, direction)
        """
        cars_data = []
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            next(reader, None)  # Пропускаем заголовок
            for row in reader:
                arrival_time = float(row[0])
                car_id = int(row[1])
                direction = Direction(row[2])
                cars_data.append((arrival_time, car_id, direction))
        return sorted(cars_data)  # Сортируем по времени прибытия