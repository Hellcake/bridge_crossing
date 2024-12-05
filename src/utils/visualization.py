# src/utils/visualization.py
import matplotlib.pyplot as plt
from typing import Dict
import numpy as np

def plot_performance_comparison(single_stats: Dict, multi_stats: Dict, save_path: str = 'performance.png'):
    """Создание графика сравнения производительности"""
    plt.figure(figsize=(12, 8))
    
    # Время выполнения
    plt.subplot(2, 2, 1)
    times = [single_stats['execution_time'], multi_stats['execution_time']]
    plt.bar(['Single-threaded', 'Multi-threaded'], times)
    plt.title('Execution Time Comparison')
    plt.ylabel('Time (seconds)')
    
    # Среднее время ожидания
    plt.subplot(2, 2, 2)
    wait_times = [
        single_stats['result']['avg_waiting_time'],
        multi_stats['result']['avg_waiting_time']
    ]
    plt.bar(['Single-threaded', 'Multi-threaded'], wait_times)
    plt.title('Average Waiting Time')
    plt.ylabel('Time (seconds)')
    
    # Статистика по направлениям (многопоточная версия)
    plt.subplot(2, 2, 3)
    dir_stats = multi_stats['result']['direction_stats']
    directions = list(dir_stats.keys())
    crossed = [dir_stats[d]['total_crossed'] for d in directions]
    plt.bar(directions, crossed)
    plt.title('Cars Crossed by Direction\n(Multi-threaded)')
    plt.ylabel('Number of cars')
    
    # Распределение времени ожидания
    plt.subplot(2, 2, 4)
    if 'waiting_times' in multi_stats['result']:
        plt.hist(multi_stats['result']['waiting_times'], bins=20)
        plt.title('Waiting Time Distribution\n(Multi-threaded)')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Number of cars')
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def create_ascii_visualization(bridge_state: Dict) -> str:
    """Создание ASCII-визуализации текущего состояния моста"""
    left_queue = bridge_state['left_queue']
    right_queue = bridge_state['right_queue']
    cars_on_bridge = bridge_state['cars_on_bridge']
    direction = bridge_state['current_direction']
    
    # Создание визуализации
    max_queue = max(len(left_queue), len(right_queue))
    width = max_queue * 3 + 20
    
    visualization = []
    
    # Левая очередь
    left_line = ''.join(['🚗' for _ in range(len(left_queue))]).ljust(max_queue)
    
    # Мост
    bridge = '=' * 10
    if cars_on_bridge > 0:
        if direction == 'left_to_right':
            bridge = '=' * 4 + '🚗' + '=' * 5
        else:
            bridge = '=' * 5 + '🚗' + '=' * 4
    
    # Правая очередь
    right_line = ''.join(['🚗' for _ in range(len(right_queue))]).rjust(max_queue)
    
    # Сборка визуализации
    visualization.append('-' * width)
    visualization.append(f"{left_line} [{bridge}] {right_line}")
    visualization.append('-' * width)
    
    return '\n'.join(visualization)