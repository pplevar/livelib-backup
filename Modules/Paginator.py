"""
Shared pagination loop for LiveLib listing pages.
"""
import logging
import random
import time
from typing import Iterator, Optional

from lxml import html

from Helpers import page_loader
from Helpers.config import BackupConfig
from Helpers.livelib_parser import href_i, is_last_page, is_redirecting_page

logger = logging.getLogger(__name__)


class Paginator:
    """
    Fetches successive listing pages, owning the delay, stop-condition, and
    error-handling policy shared by BookLoader and QuoteLoader.
    """

    def __init__(self, config: BackupConfig, driver=None):
        """
        Initialize Paginator.

        Args:
            config: Backup configuration (used for request delay)
            driver: Optional Selenium WebDriver instance
        """
        self.config = config
        self.driver = driver

    def pages(self, href: str, max_pages: Optional[float] = None) -> Iterator[html.HtmlElement]:
        """
        Yield parsed HTML pages for a listing starting at page 1.

        Stops once a page reports it is the last page, a redirect/error page
        is encountered, or `max_pages` pages have been fetched. Download
        failures and parsing errors are logged and skipped without stopping
        pagination.

        Args:
            href: Base URL for the listing (without the page-number suffix)
            max_pages: Max number of pages to fetch, or None for unlimited

        Yields:
            Parsed HTML page
        """
        page_idx = 1
        limit = max_pages if max_pages is not None else float('inf')

        while page_idx <= limit:
            self.wait_for_delay()

            try:
                page_url = href_i(href, page_idx)
                page_content = page_loader.download_page(page_url, self.driver)

                if page_content is None:
                    logger.warning('Failed to download page %d, skipping...', page_idx)
                    continue

                page = html.fromstring(page_content)

            except Exception as e:
                logger.error('Error processing page %d: %s', page_idx, e)
                continue
            finally:
                page_idx += 1

            if is_last_page(page) or is_redirecting_page(page):
                logger.info('Reached last page or error page at page %d', page_idx - 1)
                break

            yield page

    def wait_for_delay(self) -> None:
        """Wait for configured delay between requests."""
        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        time.sleep(delay)
