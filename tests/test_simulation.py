# tests/test_simulation.py
import unittest
from src.simulation.multi_threaded import run_multi_threaded_simulation
from src.models.direction import Direction

class TestSimulation(unittest.TestCase):

    def test_multi_threaded_simulation(self):
        """Тест многопоточной симуляции"""
        num_cars = 5
        result = run_multi_threaded_simulation(num_cars)
        
        self.assertIn('execution_time', result)
        self.assertIn('result', result)
        
        stats = result['result']
        self.assertEqual(stats['num_cars'], num_cars)
        self.assertEqual(stats['successful_crosses'], num_cars)
        self.assertGreater(stats['avg_crossing_time'], 0)

    def test_priority_direction_simulation(self):
        """Тест симуляции с приоритетным направлением"""
        num_cars = 10
        priority_direction = Direction.LEFT_TO_RIGHT
        
        result = run_multi_threaded_simulation(
            num_cars,
            priority_direction=priority_direction
        )
        
        stats = result['result']
        self.assertEqual(stats['priority_direction'], priority_direction.value)
        self.assertEqual(stats['successful_crosses'], num_cars)

    def test_performance_comparison(self):
        """Тест сравнения производительности между реализациями"""
        num_cars = 20
        
        multi_result = run_multi_threaded_simulation(num_cars)
        
        self.assertEqual(multi_result['result']['successful_crosses'], num_cars)
        
        self.assertIsNotNone(multi_result['execution_time'])