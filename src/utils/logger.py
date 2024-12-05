# src/utils/logger.py
import logging
from typing import Optional

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Создание и настройка логгера"""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger