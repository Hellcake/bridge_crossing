import unittest
import tempfile
import os
from src.simulation.scheduler import CarScheduler
from src.models.bridge import Bridge
from src.models.direction import Direction
from src.utils.input_reader import InputReader
from src.simulation.single_threaded import SingleThreadedBridge

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Создаем временный файл для тестовых данных
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.close()
        
    def tearDown(self):
        # Удаляем временный файл после тестов
        os.unlink(self.test_file.name)

    def create_test_input(self, data):
        """Создает тестовый входной файл"""
        with open(self.test_file.name, 'w') as f:
            for arrival_time, car_id, direction in data:
                f.write(f"{arrival_time},{car_id},{direction.value}\n")

    def test_compare_implementations(self):
        """Сравнение многопоточной и однопоточной реализаций"""
        test_data = [
            (0, 1, Direction.LEFT_TO_RIGHT),
            (0, 2, Direction.RIGHT_TO_LEFT),
            (2, 3, Direction.LEFT_TO_RIGHT),
            (2, 4, Direction.RIGHT_TO_LEFT),
            (2, 5, Direction.RIGHT_TO_LEFT)
        ]
        
        # Создаем тестовый файл
        self.create_test_input(test_data)
        
        # Запускаем однопоточную версию
        single_bridge = SingleThreadedBridge()
        single_stats = single_bridge.simulate(test_data)
        
        # Запускаем многопоточную версию
        multi_bridge = Bridge()
        scheduler = CarScheduler(test_data, multi_bridge)
        scheduler.run()
        scheduler.wait_completion()
        multi_stats = multi_bridge.get_statistics()
        
        # Сравниваем результаты
        self.assertEqual(
            single_stats['total_crossed'],
            multi_stats['total_crossed'],
            "Количество проехавших машин должно быть одинаковым"
        )
        
        # Проверяем распределение по направлениям
        for direction in Direction:
            single_dir = single_stats['direction_stats'][direction.value]['total_crossed']
            multi_dir = multi_stats['direction_stats'][direction.value]['total_crossed']
            self.assertEqual(
                single_dir,
                multi_dir,
                f"Количество машин в направлении {direction.value} должно совпадать"
            )

    def test_full_simulation_cycle(self):
        """Тест полного цикла симуляции с чтением из файла"""
        test_data = [
            (0, 1, Direction.LEFT_TO_RIGHT),
            (0, 2, Direction.LEFT_TO_RIGHT),
            (0, 3, Direction.RIGHT_TO_LEFT),
            (2, 4, Direction.LEFT_TO_RIGHT),
            (2, 5, Direction.RIGHT_TO_LEFT),
            (4, 6, Direction.LEFT_TO_RIGHT)
        ]
        
        self.create_test_input(test_data)
        
        # Читаем данные из файла
        cars_data = InputReader.read_cars_data(self.test_file.name)
        
        # Запускаем обе реализации
        single_bridge = SingleThreadedBridge()
        single_stats = single_bridge.simulate(cars_data)
        
        multi_bridge = Bridge()
        scheduler = CarScheduler(cars_data, multi_bridge)
        scheduler.run()
        scheduler.wait_completion()
        multi_stats = multi_bridge.get_statistics()
        
        # Проверяем базовые метрики
        self.assertEqual(len(cars_data), single_stats['total_crossed'])
        self.assertEqual(len(cars_data), multi_stats['total_crossed'])
        
        # Проверяем корректность времени пересечения
        self.assertAlmostEqual(single_stats['avg_crossing_time'], 1.0, places=1)
        self.assertAlmostEqual(multi_stats['avg_crossing_time'], 1.0, places=1)
        
        # Проверяем разумность времени ожидания
        self.assertGreaterEqual(single_stats['avg_waiting_time'], 0.0)
        self.assertGreaterEqual(multi_stats['avg_waiting_time'], 0.0)
        
        # Проверяем, что все машины успешно пересекли мост
        for direction in Direction:
            dir_key = direction.value
            single_crossed = single_stats['direction_stats'][dir_key]['total_crossed']
            multi_crossed = multi_stats['direction_stats'][dir_key]['total_crossed']
            expected = len([car for car in cars_data if car[2] == direction])
            self.assertEqual(single_crossed, expected)
            self.assertEqual(multi_crossed, expected)

    def test_input_file_error_handling(self):
        """Тест обработки ошибок при чтении файла"""
        # Создаем файл с неправильным форматом
        with open(self.test_file.name, 'w') as f:
            f.write("invalid_data\n")
            f.write("0,1,invalid_direction\n")
        
        # Проверяем, что чтение некорректного файла обрабатывается правильно
        with self.assertRaises(Exception):
            cars_data = InputReader.read_cars_data(self.test_file.name)
            
    def test_concurrent_arrival_handling(self):
        """Тест обработки одновременного прибытия машин"""
        test_data = [
            (0, 1, Direction.LEFT_TO_RIGHT),
            (0, 2, Direction.LEFT_TO_RIGHT),
            (0, 3, Direction.RIGHT_TO_LEFT),
            (0, 4, Direction.RIGHT_TO_LEFT)
        ]
        
        # Запускаем обе реализации
        single_bridge = SingleThreadedBridge()
        single_stats = single_bridge.simulate(test_data)
        
        multi_bridge = Bridge()
        scheduler = CarScheduler(test_data, multi_bridge)
        scheduler.run()
        scheduler.wait_completion()
        multi_stats = multi_bridge.get_statistics()
        
        # Проверяем, что все машины проехали
        self.assertEqual(single_stats['total_crossed'], len(test_data))
        self.assertEqual(multi_stats['total_crossed'], len(test_data))
        
        # Проверяем, что среднее время ожидания разумное
        self.assertLess(single_stats['max_waiting_time'], len(test_data) * 2)
        self.assertLess(multi_stats['max_waiting_time'], len(test_data) * 2)

if __name__ == '__main__':
    unittest.main()