"""
Book loader module with improved error handling and type safety.
"""
import logging
from typing import List, Optional
from lxml import html

from Helpers.book import Book
from Helpers.livelib_parser import (
    slash_add, href_i, is_last_page, is_redirecting_page,
    handle_xpath, error_handler, date_parser
)
from Helpers.page_loader import download_page
from Helpers.config import BackupConfig

logger = logging.getLogger(__name__)


class BookLoader:
    """Loads books from LiveLib user profile."""
    
    def __init__(self, config: BackupConfig, driver=None):
        """
        Initialize BookLoader.
        
        Args:
            config: Backup configuration
            driver: Optional Selenium WebDriver instance
        """
        self.config = config
        self.driver = driver
        self.user_href = config.get_user_href()
    
    def get_books(self, status: str) -> List[Book]:
        """
        Fetch all books with given status.
        
        Args:
            status: Book status ('read', 'reading', 'wish')
            
        Returns:
            List of Book objects
        """
        if status not in ('read', 'reading', 'wish'):
            raise ValueError(f"Invalid status: {status}. Must be 'read', 'reading', or 'wish'")
        
        books: List[Book] = []
        href = slash_add(self.user_href, status)
        page_idx = 1
        max_pages = self.config.read_count if status == 'read' else float('inf')
        
        logger.info('Fetching books with status "%s"...', status)
        
        while page_idx <= max_pages:
            self._wait_for_delay()
            
            try:
                page_url = href_i(href, page_idx)
                page_content = download_page(page_url, self.driver)
                
                if page_content is None:
                    logger.warning('Failed to download page %d, skipping...', page_idx)
                    page_idx += 1
                    continue
                
                page = html.fromstring(page_content)
                
            except Exception as e:
                logger.error('Error processing page %d: %s', page_idx, e)
                page_idx += 1
                continue
            finally:
                page_idx += 1
            
            if is_last_page(page) or is_redirecting_page(page):
                logger.info('Reached last page or error page at page %d', page_idx - 1)
                break
            
            last_date: Optional[str] = None
            book_elements = page.xpath('.//div[@id="booklist"]/div')
            
            for div_book_html in book_elements:
                date_element = handle_xpath(div_book_html, './/h2/text()')
                
                if date_element is not None:
                    parsed_date = date_parser(date_element)
                    if status == 'read' and parsed_date is not None:
                        last_date = parsed_date
                else:
                    book = self._parse_book(div_book_html, last_date, status)
                    if book is not None:
                        books.append(book)
        
        logger.info('Found %d books with status "%s"', len(books), status)
        return books
    
    def _parse_book(self, book_html: html.HtmlElement, date: Optional[str], status: str) -> Optional[Book]:
        """
        Parse a single book from HTML element.
        
        Args:
            book_html: HTML element containing book data
            date: Reading date (if available)
            status: Book status
            
        Returns:
            Book object or None if parsing fails
        """
        book_data = handle_xpath(book_html, './/div/div/div[@class="brow-data"]/div')
        if book_data is None:
            return error_handler('book_data', book_html)
        
        book_name_element = handle_xpath(book_data, './/a[contains(@class, "brow-book-name")]')
        if book_name_element is None:
            return error_handler('book_name', book_html)
        
        raw_link = book_name_element.get("href")
        link = self._validate_book_link(raw_link)
        if link is None:
            return error_handler('link', book_html)
        
        name = book_name_element.text
        
        author_elements = book_data.xpath('.//a[contains(@class, "brow-book-author")]/text()')
        author = ', '.join(author_elements) if author_elements else None
        
        rating = None
        if status == 'read':
            rating_element = handle_xpath(book_data, './/div[@class="brow-ratings"]/span/span/span/text()')
            rating = rating_element if rating_element else None
        
        try:
            return Book(
                link=link,
                status=status,
                name=name,
                author=author,
                rating=rating,
                date=date
            )
        except ValueError as e:
            logger.error('Invalid book data: %s', e)
            return None
    
    @staticmethod
    def _validate_book_link(link: Optional[str]) -> Optional[str]:
        """
        Validate book link format.
        
        Args:
            link: Raw link from HTML
            
        Returns:
            Validated link or None
        """
        if not link:
            return None
        if "/book/" in link or "/work/" in link:
            return link
        return None
    
    def _wait_for_delay(self) -> None:
        """Wait for configured delay between requests."""
        import time
        import random
        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        time.sleep(delay)
