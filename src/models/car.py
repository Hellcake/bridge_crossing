# src/models/car.py
import threading
from typing import Optional
from .direction import Direction
from .bridge import Bridge
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Car(threading.Thread):
    """Представляет автомобиль как отдельный поток (для многопоточной симуляции)"""
    
    def __init__(self, car_id: int, direction: Direction, bridge: Bridge):
        super().__init__(name=f"Car-{car_id}-{direction.value}")
        self.car_id = car_id
        self.direction = direction
        self.bridge = bridge
        self.crossed = False
        self.crossing_time: Optional[float] = None
        self.waiting_time: Optional[float] = None

    def run(self):
        """
        Запуск машины. Вызывается при использовании в многопоточном режиме.
        """
        try:
            # Получаем текущее время
            current_time = self.bridge.time_manager.get_time()

            # Пытаемся пересечь мост
            crossing_time, waiting_time = self.bridge.cross(self.car_id, self.direction, current_time)
            self.crossed = True
            self.crossing_time = crossing_time
            self.waiting_time = waiting_time

            # Логируем результаты
            logger.info(
                f"Car {self.car_id} has crossed the bridge. "
                f"Direction: {self.direction.value}, "
                f"Crossing time: {crossing_time:.2f}s, "
                f"Waiting time: {waiting_time:.2f}s"
            )
        except Exception as e:
            logger.error(f"Error during bridge crossing for Car {self.car_id}: {e}", exc_info=True)
