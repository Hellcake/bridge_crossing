# tests/test_bridge.py
import unittest
import threading
import time
from src.models.bridge import Bridge
from src.models.direction import Direction

class TestBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = Bridge()

    def test_single_car_crossing(self):
        """Тест проезда одной машины"""
        crossing_time = self.bridge.cross(1, Direction.LEFT_TO_RIGHT)
        
        self.assertGreater(crossing_time, 0)
        self.assertEqual(self.bridge.total_crossed, 1)
        self.assertEqual(self.bridge.cars_on_bridge, 0)

    def test_priority_direction(self):
        """Тест приоритетного направления"""
        bridge = Bridge(priority_direction=Direction.LEFT_TO_RIGHT)
        
        # Запускаем машины с разных направлений одновременно
        def right_to_left():
            bridge.cross(1, Direction.RIGHT_TO_LEFT)
            
        def left_to_right():
            bridge.cross(2, Direction.LEFT_TO_RIGHT)
        
        thread1 = threading.Thread(target=right_to_left)
        thread2 = threading.Thread(target=left_to_right)
        
        thread1.start()
        time.sleep(0.1)  # Небольшая задержка для гарантии порядка
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        stats = bridge.get_statistics()
        self.assertEqual(stats['total_crossed'], 2)

    def test_concurrent_same_direction(self):
        """Тест одновременного проезда машин в одном направлении"""
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=self.bridge.cross,
                args=(i, Direction.LEFT_TO_RIGHT)
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
            
        self.assertEqual(self.bridge.total_crossed, 5)