# src/models/bridge.py
import threading
from collections import deque
from typing import Dict, List, Optional, Tuple
from .direction import Direction
from ..utils.logger import get_logger
from ..utils.time_manager import TimeManager

logger = get_logger(__name__)

class Bridge:
    """
    Унифицированная реализация моста для однопоточной и многопоточной симуляции.
    """
    def __init__(self, priority_direction: Optional[Direction] = None, is_multithreaded: bool = False):
        self.lock = threading.Lock() if is_multithreaded else None
        self.condition = threading.Condition(self.lock) if is_multithreaded else None
        self.current_direction: Optional[Direction] = None
        self.cars_on_bridge = 0
        self.current_car: Optional[int] = None
        self.priority_direction = priority_direction
        self.consecutive_cars = 0
        self.MAX_CONSECUTIVE = 3
        self.time_manager = TimeManager()
        self.last_change_time = self.time_manager.get_time()
        self.is_multithreaded = is_multithreaded

        # Очереди для машин
        self.waiting_queues: Dict[Direction, deque] = {
            Direction.LEFT_TO_RIGHT: deque(),
            Direction.RIGHT_TO_LEFT: deque()
        }

        # Статистика
        self.total_crossed = 0
        self.crossing_times: List[float] = []
        self.waiting_times: List[float] = []
        self.direction_stats: Dict[Direction, Dict] = {
            Direction.LEFT_TO_RIGHT: {'crossed': 0, 'total_wait': 0},
            Direction.RIGHT_TO_LEFT: {'crossed': 0, 'total_wait': 0}
        }

    def simulate(self, cars_data: List[Tuple[float, int, Direction]]) -> Dict:
        """Запуск симуляции"""
        current_time = 0.0  # Виртуальное время

        # Распределяем машины по очередям
        for arrival_time, car_id, direction in sorted(cars_data):
            self.waiting_queues[direction].append((arrival_time, car_id))

        # Обрабатываем машины
        while any(len(q) > 0 for q in self.waiting_queues.values()):
            direction, car_info = self._choose_next_car(current_time)
            if not direction or not car_info:
                break

            arrival_time, car_id = car_info
            self.waiting_queues[direction].popleft()

            # Переходим к времени прибытия машины
            current_time = max(current_time, arrival_time)

            # Симулируем проезд
            crossing_time, wait_time = self.cross(car_id, direction, current_time)
            current_time += crossing_time

        return self.get_statistics()

    def cross(self, car_id: int, direction: Direction, current_time: float) -> Tuple[float, float]:
        """Проезд машины через мост"""
        arrival_time = current_time

        if self.is_multithreaded:
            with self.lock:
                while not self._can_cross(car_id, direction):
                    self.condition.wait(timeout=0.1)
                    current_time = self.time_manager.get_time()  # Обновляем время
                # Рассчитываем время ожидания
                wait_time = max(0, self.last_change_time + 1.0 - arrival_time)
                self._update_state(car_id, direction, wait_time)
                self.condition.notify_all()
        else:
            while not self._can_cross(car_id, direction):
                current_time += 0.1  # Шаг времени для однопоточной симуляции
            # Рассчитываем время ожидания
            wait_time = max(0, self.last_change_time + 1.0 - arrival_time)
            self._update_state(car_id, direction, wait_time)

        # Возвращаем время пересечения и ожидания
        return 1.0, wait_time


    def _choose_next_car(self, current_time: float) -> Tuple[Optional[Direction], Optional[Tuple[float, int]]]:
        """Выбирает следующую машину для проезда"""
        earliest_time = float('inf')
        chosen_direction = None
        chosen_car = None

        # Если есть приоритетное направление и машины в обоих направлениях
        if self.priority_direction:
            if all(len(queue) > 0 for queue in self.waiting_queues.values()):
                direction_queue = self.waiting_queues[self.priority_direction]
                if len(direction_queue) > 0:
                    arrival_time, car_id = direction_queue[0]
                    return self.priority_direction, (arrival_time, car_id)

        # Если можно продолжить текущее направление
        if self.current_direction:
            queue = self.waiting_queues[self.current_direction]
            if len(queue) > 0 and self._can_cross(None, self.current_direction):
                arrival_time, car_id = queue[0]
                return self.current_direction, (arrival_time, car_id)

        # Проверяем все очереди, чтобы найти самую раннюю машину
        for direction, queue in self.waiting_queues.items():
            if len(queue) > 0:
                arrival_time, car_id = queue[0]
                if arrival_time < earliest_time:
                    earliest_time = arrival_time
                    chosen_direction = direction
                    chosen_car = (arrival_time, car_id)

        return chosen_direction, chosen_car


    def _can_cross(self, car_id: int, direction: Direction) -> bool:
        """Проверяет возможность проезда машины"""
        # Если мост пуст или направление совпадает с текущим
        if self.cars_on_bridge == 0:
            return True

        # Если мост занят и направление совпадает
        if self.current_direction == direction:
            # Проверяем, не превышено ли количество машин подряд
            if self.consecutive_cars < self.MAX_CONSECUTIVE:
                return True

            # Если превышено, проверить противоположную очередь
            if len(self.waiting_queues[direction.opposite()]) == 0:
                return True

        # Если мост занят машиной из другого направления
        return False


    def _update_state(self, car_id: int, direction: Direction, wait_time: float):
        """Обновление состояния моста"""
        self.cars_on_bridge = 1
        self.current_car = car_id
        self.last_change_time = self.time_manager.get_time()
        self.total_crossed += 1
        self.crossing_times.append(1.0)
        self.waiting_times.append(wait_time)
        self.direction_stats[direction]['crossed'] += 1
        self.direction_stats[direction]['total_wait'] += wait_time

    def get_statistics(self) -> Dict:
        """Получение статистики"""
        stats = {
            'total_crossed': self.total_crossed,
            'avg_crossing_time': sum(self.crossing_times) / len(self.crossing_times) if self.crossing_times else 0,
            'avg_waiting_time': sum(self.waiting_times) / len(self.waiting_times) if self.waiting_times else 0,
            'max_waiting_time': max(self.waiting_times) if self.waiting_times else 0,
            'direction_stats': {}
        }
        for direction, dir_stats in self.direction_stats.items():
            avg_wait = dir_stats['total_wait'] / dir_stats['crossed'] if dir_stats['crossed'] > 0 else 0
            stats['direction_stats'][direction.value] = {
                'total_crossed': dir_stats['crossed'],
                'avg_waiting_time': avg_wait
            }
        return stats
