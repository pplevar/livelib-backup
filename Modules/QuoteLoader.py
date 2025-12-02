import os
import math

from lxml import html
import pandas as pd
from tqdm import tqdm

from Helpers.book import Book
from Helpers.livelib_parser import slash_add, href_i, is_last_page, is_redirecting_page, handle_xpath, error_handler
from Helpers.page_loader import download_page
from Helpers.quote import Quote
from Helpers.logger_config import get_logger
from Helpers.exceptions import NetworkError
from Modules.BookLoader import BookLoader

logger = get_logger(__name__)


class QuoteLoader:
    def __init__(self, app_context):
        self.ac = app_context

    def get_quotes(self):
        """
        Get list of quotes.

        Returns:
            List of Quote objects
        """
        quotes = []
        href = slash_add(self.ac.user_href, 'quotes')
        page_idx = 1

        # Create progress bar
        pbar = tqdm(
            desc='Scraping quotes',
            unit='page',
            total=self.ac.quote_count if self.ac.quote_count != math.inf else None
        )

        while page_idx <= self.ac.quote_count:
            self.ac.wait_for_delay()

            # If connection error occurs, move to next page
            try:
                page = html.fromstring(download_page(href_i(href, page_idx), self.ac.driver))
            except Exception as e:
                logger.error(f'Failed to download quote page {page_idx}: {e}')
                pbar.update(1)
                continue
            finally:
                page_idx += 1
                pbar.update(1)

            if is_last_page(page) or is_redirecting_page(page):
                break

            for quote_html in page.xpath('.//article'):
                quote = self.quote_parser(quote_html)
                if quote is not None and quote not in quotes:
                    if quote.text == '!!!NOT_FULL###':  # Handle case when full quote text is not shown
                        self.ac.wait_for_delay()
                        try:  # View quote page, if error occurs move to next quote
                            quote_page = html.fromstring(download_page(quote.link, self.ac.driver))
                        except Exception as e:
                            logger.error(f'Failed to download full quote text from {quote.link}: {e}')
                            continue
                        quote.text = self.get_quote_text(handle_xpath(quote_page, './/article'))
                    quotes.append(quote)

            # Update progress bar with current quote count
            pbar.set_postfix({'quotes': len(quotes)})

        pbar.close()
        return quotes

    def quote_parser(self, quote_html):
        """
        Parse HTML node containing quote data.

        Args:
            quote_html: HTML node with quote data

        Returns:
            Quote object or None if parsing fails
        """
        card = handle_xpath(quote_html, './/div[@class="lenta-card"]')
        if card is None:
            return error_handler('card', quote_html)

        # Search through all links until we find the ones we need
        link = None
        link_book = None
        for href in card.xpath('.//a'):
            if link is None:
                link = self.try_get_quote_link(href.get('href'))
            if link_book is None:
                link_book = BookLoader.try_get_book_link(href.get('href'))

        text = self.get_quote_text(card)
        # If we found "Read more...", mark for processing in outer function
        if len(card.xpath('.//a[@class="read-more__link"]')):
            text = '!!!NOT_FULL###'

        book_card = handle_xpath(card, './/div[@class="lenta-card-book__wrapper"]')
        book_name = handle_xpath(book_card, './/a[@class="lenta-card__book-title"]/text()')
        book_author = handle_xpath(book_card, './/p[@class="lenta-card__author-wrap"]/a/text()')

        if link is not None and link_book is not None and text is not None:
            return Quote(link, text, Book(link_book, name=book_name, author=book_author))
        if link is None or link_book is None:
            return error_handler('link', quote_html)
        if text is None:
            return error_handler('text', quote_html)
        return None

    def get_quote_text(self, card):
        """
        Extract quote text from HTML node.

        Args:
            card: HTML node with quote data

        Returns:
            Quote text as string or None if not found
        """
        item = handle_xpath(card, './/blockquote')
        if item is None:
            item = handle_xpath(card, './/div[@id="lenta-card__text-quote-full"]/p')
        if item is None:
            item = handle_xpath(card, './/div[@id="lenta-card__text-quote-full"]/div')
        if item is None:
            item = handle_xpath(card, './/p')

        quote_text = None if item is None else self.format_quote_text(item.text_content())
        logger.info(f"\tQuote Processed: {quote_text}")
        return quote_text

    def save_quotes(self, new_quotes):
        file_ext = self.ac.quote_file.split('.')[-1]

        if self.ac.rewrite_all:
            if os.path.exists(self.ac.quote_file):
                os.remove(self.ac.quote_file)
            logger.info(f'All quotes were deleted from {self.ac.quote_file}.')

        quotes_df = pd.DataFrame(columns=['Name', 'Author', 'Quote text', 'Book link', 'Quote link'])
        if file_ext in ['csv']:
            if os.path.exists(self.ac.quote_file):
                quotes_df = pd.read_csv(self.ac.quote_file, sep='\t')
        else:
            if os.path.exists(self.ac.quote_file):
                quotes_df = pd.read_excel(self.ac.quote_file)

        for nc in new_quotes:
            if quotes_df[quotes_df['Quote link'] == nc.link].shape[0] > 0:
                quotes_df.loc[quotes_df['Quote link'] == nc.link, 'text'] = nc.text
            else:
                quotes_df.loc[len(quotes_df.index)] = [
                    nc.book.name,
                    nc.book.author,
                    nc.text,
                    nc.book.link,
                    nc.link
                ]

        if file_ext in ['csv']:
            quotes_df.to_csv(self.ac.quote_file, sep='\t')
        else:
            quotes_df.to_excel(self.ac.quote_file)

        logger.info(f'The quotes were written to {self.ac.quote_file}.')

    def format_quote_text(self, text):
        """
        Process quote text (remove tabs and newlines for CSV format).

        Args:
            text: Quote text to format (string or None)

        Returns:
            Formatted text or None
        """
        if self.ac.quote_file.split('.')[-1] == 'csv':
            return None if text is None else text.replace('\t', ' ').replace('\n', ' ')
        else:
            return text

    @staticmethod
    def try_get_quote_link(link):
        """
        Validate quote link URL.

        Args:
            link: URL to validate

        Returns:
            Link if valid (contains '/quote/'), None otherwise
        """
        if "/quote/" in link:
            return link
        return None
