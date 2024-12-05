import random
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from src.models.direction import Direction
from src.models.bridge import Bridge
from src.simulation.scheduler import CarScheduler
from src.simulation.single_threaded import SingleThreadedBridge
from src.utils.logger import get_logger

logger = get_logger(__name__)

def generate_test_data(num_cars: int, time_span: float) -> List[Tuple[float, int, Direction]]:
    """
    Генерирует тестовые данные для симуляции
    
    Args:
        num_cars: Количество машин
        time_span: Временной интервал в секундах
    
    Returns:
        List of (arrival_time, car_id, direction)
    """
    cars_data = []
    for i in range(num_cars):
        arrival_time = random.uniform(0, time_span)
        direction = random.choice([Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT])
        cars_data.append((arrival_time, i, direction))
    return sorted(cars_data)  # Сортируем по времени прибытия

def run_comparison(cars_data: List[Tuple[float, int, Direction]]) -> Tuple[Dict, Dict]:
    """
    Запускает обе реализации и возвращает их статистику
    """
    # Многопоточная реализация
    multi_bridge = Bridge()
    scheduler = CarScheduler(cars_data, multi_bridge)
    scheduler.run()
    scheduler.wait_completion()
    multi_stats = multi_bridge.get_statistics()
    
    # Однопоточная реализация
    single_bridge = SingleThreadedBridge()
    single_stats = single_bridge.simulate(cars_data)
    return single_stats, multi_stats

def compare_implementations(test_cases: List[int], time_span: float = 10.0):
    """
    Сравнивает реализации для разных размеров входных данных
    
    Args:
        test_cases: Список количества машин для тестирования
        time_span: Временной интервал для генерации данных
    """
    results = {
        'single': {
            'avg_waiting': [],
            'max_waiting': [],
            'avg_crossing': [],
            'left_to_right_wait': [],
            'right_to_left_wait': []
        },
        'multi': {
            'avg_waiting': [],
            'max_waiting': [],
            'avg_crossing': [],
            'left_to_right_wait': [],
            'right_to_left_wait': []
        }
    }
    
    for num_cars in test_cases:
        logger.info(f"\nTesting with {num_cars} cars...")
        cars_data = generate_test_data(num_cars, time_span)
        single_stats, multi_stats = run_comparison(cars_data)
        
        # Собираем метрики для однопоточной реализации
        results['single']['avg_waiting'].append(single_stats['avg_waiting_time'])
        results['single']['max_waiting'].append(single_stats['max_waiting_time'])
        results['single']['avg_crossing'].append(single_stats['avg_crossing_time'])
        results['single']['left_to_right_wait'].append(
            single_stats['direction_stats']['left_to_right']['avg_waiting_time']
        )
        results['single']['right_to_left_wait'].append(
            single_stats['direction_stats']['right_to_left']['avg_waiting_time']
        )
        
        # Собираем метрики для многопоточной реализации
        results['multi']['avg_waiting'].append(multi_stats['avg_waiting_time'])
        results['multi']['max_waiting'].append(multi_stats['max_waiting_time'])
        results['multi']['avg_crossing'].append(multi_stats['avg_crossing_time'])
        results['multi']['left_to_right_wait'].append(
            multi_stats['direction_stats']['left_to_right']['avg_waiting_time']
        )
        results['multi']['right_to_left_wait'].append(
            multi_stats['direction_stats']['right_to_left']['avg_waiting_time']
        )
        
        # Выводим детальную статистику
        logger.info(f"\nResults for {num_cars} cars:")
        logger.info("\nSingle-threaded:")
        logger.info(f"Average waiting time: {single_stats['avg_waiting_time']:.2f} seconds")
        logger.info(f"Maximum waiting time: {single_stats['max_waiting_time']:.2f} seconds")
        logger.info(f"Left to right avg wait: {single_stats['direction_stats']['left_to_right']['avg_waiting_time']:.2f} seconds")
        logger.info(f"Right to left avg wait: {single_stats['direction_stats']['right_to_left']['avg_waiting_time']:.2f} seconds")
        
        logger.info("\nMulti-threaded:")
        logger.info(f"Average waiting time: {multi_stats['avg_waiting_time']:.2f} seconds")
        logger.info(f"Maximum waiting time: {multi_stats['max_waiting_time']:.2f} seconds")
        logger.info(f"Left to right avg wait: {multi_stats['direction_stats']['left_to_right']['avg_waiting_time']:.2f} seconds")
        logger.info(f"Right to left avg wait: {multi_stats['direction_stats']['right_to_left']['avg_waiting_time']:.2f} seconds")
        
    return results

def plot_results(test_cases: List[int], results: Dict):
    """
    Создает графики сравнения метрик симуляции
    """
    metrics = [
        ('avg_waiting', 'Average Waiting Time'),
        ('max_waiting', 'Maximum Waiting Time'),
        ('avg_crossing', 'Average Crossing Time'),
        ('left_to_right_wait', 'Left to Right Average Waiting Time'),
        ('right_to_left_wait', 'Right to Left Average Waiting Time')
    ]
    
    fig, axes = plt.subplots(3, 2, figsize=(15, 20))
    fig.suptitle('Bridge Simulation Metrics Comparison', fontsize=16)
    
    for idx, (metric, title) in enumerate(metrics):
        row = idx // 2
        col = idx % 2
        if row < 3:  # У нас 5 метрик, но 6 ячеек в сетке
            ax = axes[row, col]
            ax.plot(test_cases, results['single'][metric], 'b-', label='Single-threaded')
            ax.plot(test_cases, results['multi'][metric], 'r-', label='Multi-threaded')
            ax.set_xlabel('Number of cars')
            ax.set_ylabel('Time (seconds)')
            ax.set_title(title)
            ax.legend()
            ax.grid(True)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('simulation_comparison.png')
    plt.close()

def main():
    # Тестовые случаи: разное количество машин
    test_cases = [3, 5, 10, 20]
    time_span = 10.0  # Временной интервал в секундах
    
    logger.info("Starting simulation comparison...")
    results = compare_implementations(test_cases, time_span)
    
    # Создаем графики результатов
    plot_results(test_cases, results)
    logger.info("\nComparison completed. Results saved to 'simulation_comparison.png'")

if __name__ == "__main__":
    main()