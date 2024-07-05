import logging
import math
from dataclasses import dataclass
import time
import random


@dataclass
class AppContext:
    user_href: str = None
    status: str = None
    driver: object = None
    skip: str = None
    book_file: str = None
    quote_file: str = None
    page_count: int = math.inf
    quote_count: int = math.inf
    max_delay: int = 15
    min_delay: int = 5

    def wait_for_delay(self) -> None:
        """
        Останавливает программу на некоторое число секунд. Нужна, чтобы сайт не распознал в нас бота
        """
        if self.max_delay == -1:
            delay = self.min_delay
        elif self.max_delay < self.min_delay:
            delay = self.max_delay
        else:
            delay = random.randint(self.min_delay, self.max_delay)
        logging.debug(f"Waiting {delay} sec...")
        time.sleep(delay)
