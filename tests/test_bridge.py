import unittest
from src.models.bridge import Bridge
from src.models.direction import Direction
from src.models.car import Car
import threading
import time
import src.utils.logger as logger

class TestBridge(unittest.TestCase):
    def setUp(self):
        """Подготовка для каждого теста"""
        self.bridge = Bridge()
        
    def test_single_car_crossing(self):
        """Тест проезда одной машины"""
        car = Car(1, Direction.LEFT_TO_RIGHT, self.bridge)
        car.start()
        car.join()
        
        self.assertTrue(car.crossed)
        self.assertEqual(self.bridge.total_crossed, 1)
        self.assertEqual(self.bridge.cars_on_bridge, 0)
        self.assertGreaterEqual(car.crossing_time, 1.0)
        
    def test_opposite_direction_blocking(self):
        """Тест блокировки встречного движения"""
        car1 = Car(1, Direction.LEFT_TO_RIGHT, self.bridge)
        car2 = Car(2, Direction.RIGHT_TO_LEFT, self.bridge)
        
        car1.start()
        time.sleep(0.1)  # Даем первой машине начать движение
        car2.start()
        
        car1.join()
        car2.join()
        
        self.assertTrue(car1.crossed)
        self.assertTrue(car2.crossed)
        self.assertGreater(car2.waiting_time, 0)

    def test_max_consecutive_cars(self):
        """Тест ограничения последовательных машин в одном направлении"""
        # Создаем MAX_CONSECUTIVE + 1 машин в одном направлении
        cars_same_dir = [Car(i, Direction.LEFT_TO_RIGHT, self.bridge) 
                        for i in range(self.bridge.MAX_CONSECUTIVE + 1)]
        # И одну машину в противоположном направлении
        opposite_car = Car(len(cars_same_dir), Direction.RIGHT_TO_LEFT, self.bridge)
        
        # Запускаем все машины
        for car in cars_same_dir:
            car.start()
        opposite_car.start()
        
        # Ждем завершения
        for car in cars_same_dir:
            car.join()
        opposite_car.join()
        
        # Проверяем, что все машины проехали
        self.assertEqual(self.bridge.total_crossed, len(cars_same_dir) + 1)
        
        # Проверяем, что после MAX_CONSECUTIVE машин была пропущена встречная
        consecutive_cars = list(cars_same_dir[:self.bridge.MAX_CONSECUTIVE])
        last_consecutive = max(car.crossing_time + car.waiting_time 
                             for car in consecutive_cars)
        opposite_start = opposite_car.waiting_time
        last_same_dir_start = cars_same_dir[-1].waiting_time
        
        # Встречная машина должна была поехать раньше последней машины
        # в том же направлении
        self.assertLess(opposite_start, last_same_dir_start)

    def test_priority_direction(self):
        """Тест приоритетного направления"""
        bridge = Bridge(priority_direction=Direction.LEFT_TO_RIGHT)
        
        # Создаем условие для синхронизации запуска
        start_condition = threading.Event()
        
        class SynchronizedCar(threading.Thread):
            def __init__(self, car_id, direction, bridge, start_condition):
                super().__init__()
                self.car_id = car_id
                self.direction = direction
                self.bridge = bridge
                self.start_condition = start_condition
                self.crossed = False
                self.crossing_time = None
                self.waiting_time = None
            
            def run(self):
                # Ждем сигнала для начала
                self.start_condition.wait()
                arrival_time = time.time()
                
                try:
                    crossing_time, waiting_time = self.bridge.cross(self.car_id, self.direction)
                    self.crossed = True
                    self.crossing_time = crossing_time
                    self.waiting_time = waiting_time
                except Exception as e:
                    logger.error(f"Error during bridge crossing: {e}", exc_info=True)
        
        # Создаем машины с синхронизированным стартом
        cars = [
            SynchronizedCar(1, Direction.LEFT_TO_RIGHT, bridge, start_condition),
            SynchronizedCar(2, Direction.RIGHT_TO_LEFT, bridge, start_condition)
        ]
        
        # Запускаем потоки (они будут ждать сигнала)
        for car in cars:
            car.start()
            
        time.sleep(0.1)  # Даем время потокам начать ожидание
        
        # Даем сигнал для одновременного старта
        start_condition.set()
        
        # Ждем завершения
        for car in cars:
            car.join()
        
        # Приоритетная машина должна была ждать меньше
        priority_car = cars[0]  # LEFT_TO_RIGHT
        non_priority_car = cars[1]  # RIGHT_TO_LEFT
        
        self.assertTrue(priority_car.crossed)
        self.assertTrue(non_priority_car.crossed)
        self.assertLess(priority_car.waiting_time, non_priority_car.waiting_time)

    def test_fair_scheduling(self):
        """Тест справедливого распределения очереди"""
        num_cars = 10
        cars = []
        
        # Создаем машины попеременно в разных направлениях
        for i in range(num_cars):
            direction = Direction.LEFT_TO_RIGHT if i % 2 == 0 else Direction.RIGHT_TO_LEFT
            cars.append(Car(i, direction, self.bridge))
        
        # Запускаем все машины одновременно
        for car in cars:
            car.start()
            
        for car in cars:
            car.join()
        
        # Проверяем статистику
        stats = self.bridge.get_statistics()
        left_to_right = stats['direction_stats'][Direction.LEFT_TO_RIGHT.value]
        right_to_left = stats['direction_stats'][Direction.RIGHT_TO_LEFT.value]
        
        # Количество машин должно быть примерно одинаковым
        self.assertAlmostEqual(
            left_to_right['total_crossed'],
            right_to_left['total_crossed'],
            delta=1
        )
        
        # Среднее время ожидания не должно сильно отличаться
        self.assertLess(
            abs(left_to_right['avg_waiting_time'] - right_to_left['avg_waiting_time']),
            2.0
        )

if __name__ == '__main__':
    unittest.main()