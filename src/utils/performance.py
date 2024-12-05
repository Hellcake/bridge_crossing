# src/utils/performance.py
import time
from typing import Callable, Any, Dict
from functools import wraps

def measure_time(func: Callable[..., Any]) -> Callable[..., Dict]:
    """Декоратор для измерения времени выполнения функции"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        return {
            'result': result,
            'execution_time': end_time - start_time
        }
    
    return wrapper