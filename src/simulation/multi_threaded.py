# src/simulation/multi_threaded.py
from typing import List, Dict
from ..models.car import Car
from ..models.bridge import Bridge
from ..models.direction import Direction
from ..utils.performance import measure_time
from ..utils.logger import get_logger

logger = get_logger(__name__)

@measure_time
def run_multi_threaded_simulation(
    num_cars: int,
    priority_direction: Direction = None
) -> Dict:
    """
    Запуск многопоточной симуляции движения
    Returns: словарь с результатами симуляции
    """
    bridge = Bridge(priority_direction)
    cars: List[Car] = []
    
    # Создание машин
    for i in range(num_cars):
        direction = Direction.LEFT_TO_RIGHT if i % 2 == 0 else Direction.RIGHT_TO_LEFT
        priority = direction == priority_direction if priority_direction else False
        car = Car(i, direction, bridge, priority)
        cars.append(car)
    
    # Запуск всех потоков
    for car in cars:
        car.start()
    
    # Ожидание завершения всех потоков
    for car in cars:
        car.join()
    
    # Сбор статистики
    stats = bridge.get_statistics()
    stats.update({
        'num_cars': num_cars,
        'priority_direction': priority_direction.value if priority_direction else None,
        'successful_crosses': sum(1 for car in cars if car.crossed)
    })
    
    return stats