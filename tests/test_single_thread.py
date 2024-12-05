import unittest
from src.simulation.single_threaded import SingleThreadedBridge
from src.models.direction import Direction

class TestSingleThreadedBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = SingleThreadedBridge()

    def test_basic_simulation(self):
        """Тест базового сценария"""
        cars_data = [
            (0, 1, Direction.LEFT_TO_RIGHT),
            (0, 2, Direction.RIGHT_TO_LEFT),
            (2, 3, Direction.LEFT_TO_RIGHT)
        ]
        
        stats = self.bridge.simulate(cars_data)
        
        self.assertEqual(stats['total_crossed'], 3)
        self.assertEqual(stats['avg_crossing_time'], 1.0)
        self.assertGreaterEqual(stats['avg_waiting_time'], 0.0)

    def test_consecutive_cars_limit(self):
        """Тест ограничения последовательных машин"""
        # Создаем MAX_CONSECUTIVE + 1 машин в одном направлении
        # и одну машину в противоположном
        cars_data = (
            [(0, i, Direction.LEFT_TO_RIGHT) for i in range(self.bridge.MAX_CONSECUTIVE + 1)] +
            [(0, self.bridge.MAX_CONSECUTIVE + 1, Direction.RIGHT_TO_LEFT)]
        )
        
        stats = self.bridge.simulate(cars_data)
        
        # После MAX_CONSECUTIVE машин должна проехать встречная
        direction_stats = stats['direction_stats'][Direction.RIGHT_TO_LEFT.value]
        self.assertEqual(direction_stats['total_crossed'], 1)
        
        # Время ожидания встречной машины не должно быть слишком большим
        self.assertLessEqual(direction_stats['avg_waiting_time'], 
                           self.bridge.MAX_CONSECUTIVE + 1)

    def test_arrival_order(self):
        """Тест соблюдения порядка прибытия"""
        cars_data = [
            (0, 1, Direction.LEFT_TO_RIGHT),  # Первая группа
            (0, 2, Direction.LEFT_TO_RIGHT),
            (2, 3, Direction.RIGHT_TO_LEFT),  # Вторая группа
            (2, 4, Direction.RIGHT_TO_LEFT),
        ]
        
        self.bridge = SingleThreadedBridge()
        stats = self.bridge.simulate(cars_data)
        
        self.assertEqual(stats['total_crossed'], 4)
        # Проверяем, что среднее время ожидания разумное
        self.assertLess(stats['avg_waiting_time'], 3.0)

    def test_priority_direction(self):
        """Тест приоритетного направления"""
        bridge = SingleThreadedBridge(priority_direction=Direction.LEFT_TO_RIGHT)
        cars_data = [
            (0, 1, Direction.RIGHT_TO_LEFT),
            (0, 2, Direction.LEFT_TO_RIGHT),
            (0, 3, Direction.RIGHT_TO_LEFT),
        ]
        
        stats = bridge.simulate(cars_data)
        
        # Машины в приоритетном направлении должны ждать меньше
        left_stats = stats['direction_stats'][Direction.LEFT_TO_RIGHT.value]
        right_stats = stats['direction_stats'][Direction.RIGHT_TO_LEFT.value]
        self.assertLess(left_stats['avg_waiting_time'], 
                       right_stats['avg_waiting_time'])

    def test_groups_arrival(self):
        """Тест обработки групп машин, прибывающих одновременно"""
        cars_data = [
            # Первая группа
            (0, 1, Direction.LEFT_TO_RIGHT),
            (0, 2, Direction.LEFT_TO_RIGHT),
            (0, 3, Direction.RIGHT_TO_LEFT),
            # Вторая группа
            (5, 4, Direction.LEFT_TO_RIGHT),
            (5, 5, Direction.RIGHT_TO_LEFT),
            (5, 6, Direction.RIGHT_TO_LEFT),
        ]
        
        stats = self.bridge.simulate(cars_data)
        
        self.assertEqual(stats['total_crossed'], 6)
        # Проверяем максимальное время ожидания
        self.assertLess(stats['max_waiting_time'], 
                       len(cars_data) * 1.1)  # Не больше чем время проезда всех машин

    def test_empty_input(self):
        """Тест пустых входных данных"""
        stats = self.bridge.simulate([])
        
        self.assertEqual(stats['total_crossed'], 0)
        self.assertEqual(stats['avg_crossing_time'], 0)
        self.assertEqual(stats['avg_waiting_time'], 0)
        self.assertEqual(stats['max_waiting_time'], 0)

if __name__ == '__main__':
    unittest.main()