"""
Quote loader module with improved error handling and type safety.
"""
import logging
import os
from typing import List, Optional
from lxml import html

from Helpers import page_loader
from Helpers.csv_writer import save_quotes as write_quotes
from Helpers.livelib_parser import slash_add, handle_xpath, error_handler
from Helpers.quote import Quote
from Helpers.book import Book
from Helpers.config import BackupConfig
from Modules.Paginator import Paginator

logger = logging.getLogger(__name__)


class QuoteLoader:
    """Loads quotes from LiveLib user profile."""
    
    def __init__(self, config: BackupConfig, driver=None):
        """
        Initialize QuoteLoader.
        
        Args:
            config: Backup configuration
            driver: Optional Selenium WebDriver instance
        """
        self.config = config
        self.driver = driver
        self.user_href = config.get_user_href()
    
    def get_quotes(self, quote_count: Optional[float] = None) -> List[Quote]:
        """
        Fetch all quotes from user profile.

        Args:
            quote_count: Max number of quote pages to fetch.

        Returns:
            List of Quote objects
        """
        quotes: List[Quote] = []
        href = slash_add(self.user_href, 'quotes')

        logger.info('Fetching quotes...')

        paginator = Paginator(self.config, self.driver)
        for page in paginator.pages(href, quote_count):
            quote_elements = page.xpath('.//article')

            for quote_html in quote_elements:
                quote = self._parse_quote(quote_html)

                if quote is not None and quote not in quotes:
                    # Handle truncated quotes
                    if quote.text == '!!!NOT_FULL###':
                        logger.info('Quote truncated, fetching full text...')
                        paginator.wait_for_delay()

                        try:
                            quote_page_content = page_loader.download_page(quote.link, self.driver)
                            if quote_page_content:
                                quote_page = html.fromstring(quote_page_content)
                                full_text = self._extract_quote_text(handle_xpath(quote_page, './/article'))
                                if full_text:
                                    quote.text = full_text
                        except Exception as e:
                            logger.error('Error fetching full quote text: %s', e)
                            continue

                    quotes.append(quote)

        logger.info('Found %d quotes', len(quotes))
        return quotes
    
    def _parse_quote(self, quote_html: html.HtmlElement) -> Optional[Quote]:
        """
        Parse a single quote from HTML element.
        
        Args:
            quote_html: HTML element containing quote data
            
        Returns:
            Quote object or None if parsing fails
        """
        card = handle_xpath(quote_html, './/div[@class="lenta-card"]')
        if card is None:
            return error_handler('card', quote_html)
        
        # Extract links
        quote_link: Optional[str] = None
        book_link: Optional[str] = None
        
        for href_element in card.xpath('.//a'):
            href = href_element.get('href')
            if quote_link is None:
                quote_link = self._validate_quote_link(href)
            if book_link is None:
                book_link = BookLoader._validate_book_link(href)
        
        # Extract text
        text = self._extract_quote_text(card)
        
        # Check if quote is truncated
        if card.xpath('.//a[@class="read-more__link"]'):
            text = '!!!NOT_FULL###'
        
        # Extract book info
        book_card = handle_xpath(card, './/div[@class="lenta-card-book__wrapper"]')
        book_name = handle_xpath(book_card, './/a[@class="lenta-card__book-title"]/text()')
        book_author = handle_xpath(book_card, './/p[@class="lenta-card__author-wrap"]/a/text()')
        
        # Validate and create Quote
        if quote_link is None or book_link is None:
            return error_handler('link', quote_html)
        
        if text is None:
            return error_handler('text', quote_html)
        
        try:
            book = Book(link=book_link, status='read', name=book_name, author=book_author)
            return Quote(link=quote_link, text=text, book=book)
        except ValueError as e:
            logger.error('Invalid quote data: %s', e)
            return None
    
    def _extract_quote_text(self, card: Optional[html.HtmlElement]) -> Optional[str]:
        """
        Extract quote text from HTML element.
        
        Args:
            card: HTML element containing quote
            
        Returns:
            Quote text or None
        """
        if card is None:
            return None
        
        # Try multiple selectors
        selectors = [
            './/blockquote',
            './/div[@id="lenta-card__text-quote-full"]/p',
            './/div[@id="lenta-card__text-quote-full"]/div',
            './/p'
        ]
        
        for selector in selectors:
            item = handle_xpath(card, selector)
            if item is not None:
                text = item.text_content()
                return self._format_quote_text(text)
        
        return None
    
    def _format_quote_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean and format quote text for CSV export.
        
        Args:
            text: Raw quote text
            
        Returns:
            Formatted text or None
        """
        if text is None:
            return None
        
        # Clean whitespace and newlines for CSV compatibility
        cleaned = text.replace('\t', ' ').replace('\n', ' ').strip()
        return cleaned if cleaned else None
    
    def save_quotes(self, new_quotes: List[Quote]) -> None:
        """
        Save quotes to file (CSV or Excel), updating existing quotes in place.

        Args:
            new_quotes: List of quotes to save
        """
        file_path = self.config.get_quotes_file_path()

        if self.config.rewrite_all and os.path.exists(file_path):
            os.remove(file_path)
            logger.info('Cleared existing quotes file: %s', file_path)

        try:
            write_quotes(new_quotes, file_path)
            logger.info('Saved %d quotes to %s', len(new_quotes), file_path)
        except Exception as e:
            logger.error('Failed to save quotes: %s', e)
            raise

    @staticmethod
    def _validate_quote_link(link: Optional[str]) -> Optional[str]:
        """
        Validate quote link format.
        
        Args:
            link: Raw link from HTML
            
        Returns:
            Validated link or None
        """
        if not link:
            return None
        if "/quote/" in link:
            return link
        return None


# Import BookLoader for link validation (circular import workaround)
from Modules.BookLoader import BookLoader
