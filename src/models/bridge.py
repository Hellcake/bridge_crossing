# src/models/bridge.py
import threading
import time
from collections import deque
from typing import Dict, List, Optional, Tuple
from .direction import Direction
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Bridge:
    """
    Класс, представляющий мост с односторонним движением.
    На мосту одновременно может находиться только одна машина.
    """
    def __init__(self, priority_direction: Optional[Direction] = None):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.current_direction: Optional[Direction] = None
        self.cars_on_bridge = 0
        self.current_car: Optional[int] = None
        self.priority_direction = priority_direction
        self.consecutive_cars = 0
        self.MAX_CONSECUTIVE = 3
        self.last_change_time = time.time()
        
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

    def should_change_direction(self, current_time: float) -> bool:
        """Определяет, нужно ли менять направление движения"""
        if self.current_direction is None:
            return True
            
        # Если достигнут лимит последовательных машин
        if self.consecutive_cars >= self.MAX_CONSECUTIVE:
            opposite_queue = self.waiting_queues[self.current_direction.opposite()]
            return len(opposite_queue) > 0
            
        return False

    def can_cross(self, car_id: int, direction: Direction) -> bool:
        """Проверяет, может ли машина проехать мост"""
        # Если на мосту уже есть машина
        if self.cars_on_bridge > 0:
            return False
            
        # Проверяем, что это первая машина в своей очереди
        if not self.waiting_queues[direction] or self.waiting_queues[direction][0] != car_id:
            return False

        # Проверяем необходимость смены направления
        current_time = time.time()
        if self.should_change_direction(current_time):
            # Если есть машины в противоположном направлении
            opposite_direction = direction.opposite()
            if len(self.waiting_queues[opposite_direction]) > 0:
                if direction == self.current_direction:
                    return False

        # Проверяем приоритет
        if self.priority_direction:
            # Если есть машины в обоих направлениях
            if all(len(q) > 0 for q in self.waiting_queues.values()):
                if direction != self.priority_direction:
                    # Неприоритетное направление может ехать только если:
                    # 1. В приоритетном направлении достигнут лимит последовательных машин
                    # 2. Нет активного направления (новый цикл)
                    if (self.current_direction != self.priority_direction or
                        self.consecutive_cars < self.MAX_CONSECUTIVE):
                        return False

        return True

    def cross(self, car_id: int, direction: Direction) -> Tuple[float, float]:
        """Метод для проезда автомобиля через мост"""
        arrival_time = time.time()
        
        with self.lock:
            # Добавляем машину в очередь
            self.waiting_queues[direction].append(car_id)
            
            # Ждем возможности проезда
            while not self.can_cross(car_id, direction):
                self.condition.wait()
            
            # Удаляем машину из очереди
            self.waiting_queues[direction].popleft()
            wait_time = time.time() - arrival_time
            
            # Обновляем состояние моста
            if self.current_direction == direction:
                self.consecutive_cars += 1
            else:
                self.current_direction = direction
                self.consecutive_cars = 1
                self.last_change_time = time.time()
            
            self.cars_on_bridge = 1
            self.current_car = car_id
            self.waiting_times.append(wait_time)
            self.direction_stats[direction]['total_wait'] += wait_time
        
        # Симуляция проезда
        crossing_time = 1.0
        time.sleep(crossing_time)
        
        with self.lock:
            self.cars_on_bridge = 0
            self.current_car = None
            self.total_crossed += 1
            self.direction_stats[direction]['crossed'] += 1
            self.crossing_times.append(crossing_time)
            
            # Уведомляем ожидающие машины
            self.condition.notify_all()
        
        return crossing_time, wait_time

    def get_statistics(self) -> Dict:
        """Получение статистики работы моста"""
        stats = {
            'total_crossed': self.total_crossed,
            'avg_crossing_time': sum(self.crossing_times) / len(self.crossing_times) if self.crossing_times else 0,
            'avg_waiting_time': sum(self.waiting_times) / len(self.waiting_times) if self.waiting_times else 0,
            'max_waiting_time': max(self.waiting_times) if self.waiting_times else 0,
            'direction_stats': {}
        }
        
        for direction, dir_stats in self.direction_stats.items():
            if dir_stats['crossed'] > 0:
                avg_wait = dir_stats['total_wait'] / dir_stats['crossed']
            else:
                avg_wait = 0
                
            stats['direction_stats'][direction.value] = {
                'total_crossed': dir_stats['crossed'],
                'avg_waiting_time': avg_wait
            }
        
        return stats