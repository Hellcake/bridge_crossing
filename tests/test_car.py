# tests/test_car.py
import unittest
import time
from src.models.car import Car
from src.models.bridge import Bridge
from src.models.direction import Direction

class TestCar(unittest.TestCase):
    def setUp(self):
        self.bridge = Bridge()

    def test_car_creation(self):
        """Тест создания машины"""
        car = Car(1, Direction.LEFT_TO_RIGHT, self.bridge)
        # tests/test_car.py (продолжение)
        self.assertEqual(car.car_id, 1)
        self.assertEqual(car.direction, Direction.LEFT_TO_RIGHT)
        self.assertFalse(car.crossed)
        self.assertIsNone(car.crossing_time)

    def test_car_crossing(self):
        """Тест проезда машины через мост"""
        car = Car(1, Direction.LEFT_TO_RIGHT, self.bridge)
        car.start()
        car.join()
        
        self.assertTrue(car.crossed)
        self.assertIsNotNone(car.crossing_time)
        self.assertGreater(car.crossing_time, 0)

    def test_multiple_cars_different_directions(self):
        """Тест проезда нескольких машин в разных направлениях"""
        cars = [
            Car(1, Direction.LEFT_TO_RIGHT, self.bridge),
            Car(2, Direction.RIGHT_TO_LEFT, self.bridge),
            Car(3, Direction.LEFT_TO_RIGHT, self.bridge)
        ]
        
        for car in cars:
            car.start()
        
        for car in cars:
            car.join()
            
        for car in cars:
            self.assertTrue(car.crossed)
            self.assertIsNotNone(car.crossing_time)

    def test_priority_car(self):
        """Тест приоритетного проезда"""
        bridge = Bridge(priority_direction=Direction.LEFT_TO_RIGHT)
        
        priority_car = Car(1, Direction.LEFT_TO_RIGHT, bridge, priority=True)
        regular_car = Car(2, Direction.RIGHT_TO_LEFT, bridge, priority=False)
        
        # Запускаем сначала обычную машину
        regular_car.start()
        time.sleep(0.1)  # Небольшая задержка
        priority_car.start()
        
        priority_car.join()
        regular_car.join()
        
        self.assertTrue(priority_car.crossed)
        self.assertTrue(regular_car.crossed)
