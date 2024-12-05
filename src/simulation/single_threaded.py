from typing import List, Tuple, Dict, Optional
from ..models.direction import Direction
from ..utils.logger import get_logger
from collections import deque

logger = get_logger(__name__)

class SingleThreadedBridge:
    """Однопоточная реализация моста"""
    def __init__(self, priority_direction: Optional[Direction] = None):
        self.current_direction: Optional[Direction] = None
        self.consecutive_cars = 0
        self.MAX_CONSECUTIVE = 3
        self.priority_direction = priority_direction
        
        # Очереди для машин с указанием времени прибытия
        self.queues = {
            Direction.LEFT_TO_RIGHT: deque(),
            Direction.RIGHT_TO_LEFT: deque()
        }
        
        # Статистика
        self.total_crossed = 0
        self.crossing_times: List[float] = []
        self.waiting_times: List[float] = []
        self.direction_stats = {
            Direction.LEFT_TO_RIGHT: {'crossed': 0, 'total_wait': 0},
            Direction.RIGHT_TO_LEFT: {'crossed': 0, 'total_wait': 0}
        }

    def can_switch_direction(self, new_direction: Direction) -> bool:
        """Проверяет возможность смены направления движения"""
        if self.current_direction is None:
            return True
            
        if self.current_direction == new_direction:
            if self.consecutive_cars >= self.MAX_CONSECUTIVE:
                return len(self.queues[new_direction.opposite()]) == 0
            return True
            
        return False

    def choose_next_car(self, current_time: float) -> Tuple[Optional[Direction], Optional[Tuple[float, int]]]:
        """Выбирает следующую машину для проезда"""
        # Если есть приоритетное направление и машины в обоих направлениях
        if (self.priority_direction and 
            all(len(q) > 0 for q in self.queues.values())):
            return self.priority_direction, self.queues[self.priority_direction][0]
            
        # Если можно продолжить текущее направление
        if (self.current_direction and 
            len(self.queues[self.current_direction]) > 0 and
            self.can_switch_direction(self.current_direction)):
            return self.current_direction, self.queues[self.current_direction][0]
            
        # Проверяем очереди с учетом времени прибытия
        earliest_time = float('inf')
        chosen_direction = None
        chosen_car = None

        for direction in Direction:
            if len(self.queues[direction]) > 0:
                arrival_time, car_id = self.queues[direction][0]
                if arrival_time < earliest_time:
                    earliest_time = arrival_time
                    chosen_direction = direction
                    chosen_car = (arrival_time, car_id)

        return chosen_direction, chosen_car

    def simulate(self, cars_data: List[Tuple[float, int, Direction]]) -> Dict:
        """Запуск симуляции"""
        current_time = 0.0  # Текущее время симуляции
        
        # Распределяем машины по очередям
        for arrival_time, car_id, direction in sorted(cars_data):
            logger.info(f"Car {car_id} approaching bridge from {direction.value}")
            self.queues[direction].append((arrival_time, car_id))
        
        # Обрабатываем машины
        while any(len(q) > 0 for q in self.queues.values()):
            direction, car_info = self.choose_next_car(current_time)
            if not direction or not car_info:
                break
                
            arrival_time, car_id = car_info
            self.queues[direction].popleft()
            
            # Переходим к времени прибытия машины, если оно больше текущего
            if arrival_time > current_time:
                current_time = arrival_time
            
            # Обновляем состояние моста
            if self.current_direction != direction:
                self.current_direction = direction
                self.consecutive_cars = 1
            else:
                self.consecutive_cars += 1
            
            # Симулируем проезд
            crossing_time = 1.0
            wait_time = max(0.0, current_time - arrival_time)
            current_time += crossing_time
            
            # Обновляем статистику
            self.total_crossed += 1
            self.crossing_times.append(crossing_time)
            self.waiting_times.append(wait_time)
            self.direction_stats[direction]['crossed'] += 1
            self.direction_stats[direction]['total_wait'] += wait_time
            
            logger.info(
                f"Car {car_id} has crossed the bridge. "
                f"Direction: {direction.value}, "
                f"Crossing time: {crossing_time:.2f}s, "
                f"Waiting time: {wait_time:.2f}s"
            )
            
            # После MAX_CONSECUTIVE машин меняем направление
            if self.consecutive_cars >= self.MAX_CONSECUTIVE:
                if len(self.queues[direction.opposite()]) > 0:
                    self.current_direction = None
                    self.consecutive_cars = 0
        
        return self.get_statistics()

    def get_statistics(self) -> Dict:
        """Получение статистики"""
        stats = {
            'total_crossed': self.total_crossed,
            'avg_crossing_time': sum(self.crossing_times) / len(self.crossing_times) 
                if self.crossing_times else 0,
            'avg_waiting_time': sum(self.waiting_times) / len(self.waiting_times) 
                if self.waiting_times else 0,
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