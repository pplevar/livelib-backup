"""Retry decorator with exponential backoff for network operations."""

from functools import wraps
from typing import Callable, Tuple, Type
import time
import logging

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator for retrying operations with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exception types to catch and retry

    Returns:
        Decorated function with retry logic

    Example:
        @retry(max_attempts=3, delay=2.0, exceptions=(NetworkError, requests.RequestException))
        def download_page(url):
            return requests.get(url)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f'{func.__name__} failed after {max_attempts} attempts')
                        raise

                    logger.warning(
                        f'{func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}'
                    )
                    logger.info(f'Retrying in {current_delay:.1f}s...')
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator
