# src/simulation/scheduler.py
import threading
import time
from typing import List, Tuple
from ..models.car import Car
from ..models.bridge import Bridge
from ..models.direction import Direction
from ..utils.logger import get_logger

logger = get_logger(__name__)

class CarScheduler:
    """Управляет появлением машин и их движением"""
    
    def __init__(self, cars_data: List[Tuple[float, int, Direction]], bridge: Bridge):
        self.cars_data = sorted(cars_data)
        self.bridge = bridge
        self.cars: List[Car] = []
        self.active_cars: List[threading.Thread] = []

    def run(self):
        """Запускает машины в заданные моменты времени"""
        simulation_start = time.time()
        last_arrival = 0

        for arrival_time, car_id, direction in self.cars_data:
            # Ждем до следующего времени прибытия
            wait_time = arrival_time - last_arrival
            if wait_time > 0:
                time.sleep(wait_time)
            last_arrival = arrival_time
            
            # Создаем и запускаем машину
            car = Car(car_id, direction, self.bridge)
            logger.info(f"Car {car_id} approaching bridge from {direction.value}")
            car.start()
            self.cars.append(car)

    def wait_completion(self, timeout: float = 60.0) -> bool:
        """Ожидает завершения проезда всех машин"""
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            # Проверяем все ли машины проехали
            if all(not car.is_alive() for car in self.cars):
                return True
            time.sleep(0.1)
        
        return False

    def get_completed_cars(self) -> int:
        """Возвращает количество машин, успешно проехавших мост"""
        return sum(1 for car in self.cars if car.crossed)