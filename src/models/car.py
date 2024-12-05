# src/models/car.py
import threading
import time
from typing import Optional
from .direction import Direction
from .bridge import Bridge
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Car(threading.Thread):
    """Представляет автомобиль как отдельный поток"""
    
    def __init__(self, car_id: int, direction: Direction, bridge: Bridge):
        super().__init__(name=f"Car-{car_id}-{direction.value}")
        self.car_id = car_id
        self.direction = direction
        self.bridge = bridge
        self.crossed = False
        self.crossing_time: Optional[float] = None
        self.waiting_time: Optional[float] = None

    def run(self):
        try:
            # Попытка проезда через мост
            crossing_time, waiting_time = self.bridge.cross(self.car_id, self.direction)
            
            # Обновляем статистику
            self.crossed = True
            self.crossing_time = crossing_time
            self.waiting_time = waiting_time
            
            logger.info(f"Car {self.car_id} has crossed the bridge. "
                       f"Crossing time: {crossing_time:.2f}s, "
                       f"Waiting time: {waiting_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error during bridge crossing: {e}", exc_info=True)