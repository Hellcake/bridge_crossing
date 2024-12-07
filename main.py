import argparse
import time
from typing import Optional
from src.models.direction import Direction
from src.models.bridge import Bridge
from src.utils.input_reader import InputReader
from src.utils.logger import get_logger

logger = get_logger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description='Bridge Crossing Simulation')
    parser.add_argument(
        '--input-file',
        type=str,
        default='input.txt',
        help='Input file with car arrival times'
    )
    parser.add_argument(
        '--priority-direction',
        choices=['left_to_right', 'right_to_left'],
        help='Priority direction for crossing'
    )
    parser.add_argument(
        '--mode',
        choices=['single', 'multi'],
        default='multi',
        help='Simulation mode: single-threaded or multi-threaded'
    )
    return parser.parse_args()

def simulate_traffic(input_file: str, mode: str, priority_direction: Optional[Direction] = None):
    cars_data = InputReader.read_cars_data(input_file)
    is_multithreaded = mode == 'multi'
    bridge = Bridge(priority_direction, is_multithreaded)
    return bridge.simulate(cars_data)


def print_statistics(stats: dict):
    """Вывод статистики симуляции"""
    logger.info("\nSimulation statistics:")
    logger.info(f"Total cars crossed: {stats['total_crossed']}")
    logger.info(f"Average crossing time: {stats['avg_crossing_time']:.2f} seconds")
    logger.info(f"Average waiting time: {stats['avg_waiting_time']:.2f} seconds")
    logger.info(f"Maximum waiting time: {stats['max_waiting_time']:.2f} seconds")
    
    for direction, dir_stats in stats['direction_stats'].items():
        logger.info(f"\nDirection {direction}:")
        logger.info(f"Cars crossed: {dir_stats['total_crossed']}")
        logger.info(f"Average waiting time: {dir_stats['avg_waiting_time']:.2f} seconds")

def main():
    args = parse_args()
    
    priority_direction = None
    if args.priority_direction:
        priority_direction = Direction[args.priority_direction.upper()]
    
    logger.info("Running simulation...")
    start_time = time.time()
    
    # Унифицированный запуск
    stats = simulate_traffic(args.input_file, args.mode, priority_direction)
        
    if not stats:
        logger.error("Simulation failed")
        return
    
    total_time = time.time() - start_time
    
    print_statistics(stats)
    logger.info(f"\nTotal simulation time: {total_time:.2f} seconds")


if __name__ == "__main__":
    main()