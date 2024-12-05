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
    """
    def __init__(self, priority_direction: Optional[Direction] = None):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.current_direction: Optional[Direction] = None
        self.cars_on_bridge = 0
        self.priority_direction = priority_direction
        self.consecutive_cars = 0  # Счетчик машин в одном направлении
        self.MAX_CONSECUTIVE = 3   # Максимальное количество машин подряд
        
        # Используем deque для очередей
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

    def can_cross(self, car_id: int, direction: Direction) -> bool:
        """Проверяет, может ли машина проехать мост"""
        # Если мост пустой
        if self.cars_on_bridge == 0:
            # Проверяем приоритет только если есть машины в обоих направлениях
            if (self.priority_direction and 
                all(len(q) > 0 for q in self.waiting_queues.values())):
                return direction == self.priority_direction
            # Проверяем, что это первая машина в своей очереди
            return car_id == self.waiting_queues[direction][0]
            
        # Если мост занят
        if self.current_direction != direction:
            return False
            
        # Проверяем лимит последовательных машин
        if self.consecutive_cars >= self.MAX_CONSECUTIVE:
            opposite_queue = self.waiting_queues[direction.opposite()]
            return len(opposite_queue) == 0
            
        return car_id == self.waiting_queues[direction][0]

    def cross(self, car_id: int, direction: Direction, priority: bool = False) -> Tuple[float, float]:
        """Метод для проезда автомобиля через мост"""
        arrival_time = time.time()
        
        with self.lock:
            # Добавляем машину в конец очереди
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
            
            self.cars_on_bridge += 1
            self.waiting_times.append(wait_time)
            self.direction_stats[direction]['total_wait'] += wait_time
        
        # Симуляция проезда
        crossing_time = 1.0
        time.sleep(crossing_time)
        
        with self.lock:
            self.cars_on_bridge -= 1
            self.total_crossed += 1
            self.direction_stats[direction]['crossed'] += 1
            self.crossing_times.append(crossing_time)
            
            # Проверяем необходимость смены направления
            if self.consecutive_cars >= self.MAX_CONSECUTIVE:
                opposite_queue = self.waiting_queues[direction.opposite()]
                if len(opposite_queue) > 0:
                    self.current_direction = None
                    self.consecutive_cars = 0
            
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