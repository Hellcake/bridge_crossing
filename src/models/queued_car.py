from dataclasses import dataclass
from .direction import Direction

@dataclass
class QueuedCar:
    """Представляет машину в очереди на мост"""
    car_id: int
    arrival_time: float
    direction: Direction