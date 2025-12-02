from typing import Optional
import logging
import math
from dataclasses import dataclass, field
import time
import random


@dataclass
class AppContext:
    """Application context holding configuration and state for the scraper."""

    user_href: Optional[str] = None
    status: Optional[str] = None
    driver: Optional[object] = None
    skip: Optional[str] = None
    book_file: Optional[str] = None
    quote_file: Optional[str] = None
    page_count: int = math.inf
    quote_count: int = math.inf
    max_delay: int = 15
    min_delay: int = 5
    rewrite_all: bool = False

    def wait_for_delay(self) -> None:
        """
        Pause program execution for random duration.

        Prevents bot detection by mimicking human browsing patterns
        with random delays between requests.
        """
        if self.max_delay == -1:
            delay = self.min_delay
        elif self.max_delay < self.min_delay:
            delay = self.max_delay
        else:
            delay = random.randint(self.min_delay, self.max_delay)
        logging.debug(f"Waiting {delay} sec...")
        time.sleep(delay)
