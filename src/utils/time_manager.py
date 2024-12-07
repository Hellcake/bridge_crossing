# src/utils/time_manager.py
import threading

class TimeManager:
    """Управляет виртуальным временем для симуляции"""
    def __init__(self):
        self.current_time = 0.0
        self.lock = threading.Lock()

    def advance_time(self, delta: float):
        """Увеличить виртуальное время"""
        with self.lock:
            self.current_time += delta

    def get_time(self) -> float:
        """Получить текущее виртуальное время"""
        with self.lock:
            return self.current_time
