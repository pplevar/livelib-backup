from lxml import html
from tqdm import tqdm
import math

from Helpers.book import Book
from Helpers.livelib_parser import slash_add, href_i, is_last_page, is_redirecting_page, handle_xpath, error_handler, \
    date_parser
from Helpers.page_loader import download_page
from Helpers.logger_config import get_logger
from Helpers.exceptions import NetworkError

logger = get_logger(__name__)


class BookLoader:
    def __init__(self, app_context):
        self.ac = app_context

    def get_books(self, status):
        """
        Get list of books with specified status.

        Args:
            status: Book status ('read', 'reading', 'wish')

        Returns:
            List of Book objects
        """
        books = []
        href = slash_add(self.ac.user_href, status)
        page_idx = 1

        # Create progress bar
        pbar = tqdm(
            desc=f'Scraping {status} books',
            unit='page',
            total=self.ac.page_count if self.ac.page_count != math.inf else None
        )

        while page_idx <= self.ac.page_count:
            self.ac.wait_for_delay()

            # If connection error occurs, move to next page
            try:
                page = html.fromstring(download_page(href_i(href, page_idx), self.ac.driver))
            except Exception as e:
                logger.error(f'Failed to download page {page_idx} for status "{status}": {e}')
                pbar.update(1)
                continue
            finally:
                page_idx += 1
                pbar.update(1)

            if is_last_page(page) or is_redirecting_page(page):
                break

            last_date = None
            for div_book_html in page.xpath('.//div[@id="booklist"]/div'):
                date = handle_xpath(div_book_html, './/h2/text()')
                if date is not None:
                    date = date_parser(date)
                    if status == 'read' and date is not None:
                        last_date = date
                else:
                    book = self.book_parser(div_book_html, last_date, status)
                    if book is not None:
                        books.append(book)

            # Update progress bar with current book count
            pbar.set_postfix({'books': len(books)})

        pbar.close()
        return books

    def book_parser(self, book_html, date, status):
        """
        Parse HTML node containing book data.

        Args:
            book_html: HTML node with book data
            date: Reading completion date (string or None)
            status: Book status ('read', 'reading', 'wish')

        Returns:
            Book object or None if parsing fails
        """
        book_data = handle_xpath(book_html, './/div/div/div[@class="brow-data"]/div')
        if book_data is None:
            return error_handler('book_data', book_html)

        book_name = handle_xpath(book_data, './/a[contains(@class, "brow-book-name")]')
        link = self.try_get_book_link(book_name.get("href"))  # Link is in href attribute
        if link is None:
            return error_handler('link', book_html)
        name = None if book_name is None else book_name.text

        author = book_data.xpath('.//a[contains(@class, "brow-book-author")]/text()')
        if len(author):
            author = ', '.join(author)  # Join multiple authors with commas

        rating = None
        if status == 'read':
            rating = handle_xpath(book_data, './/div[@class="brow-ratings"]/span/span/span/text()')

        return Book(link, status, name, author, rating, date)

    @staticmethod
    def try_get_book_link(link):
        """
        Validate book link URL.

        Args:
            link: URL to validate

        Returns:
            Link if valid (contains '/book/' or '/work/'), None otherwise
        """
        if "/book/" in link or "/work/" in link:
            return link
        return None
