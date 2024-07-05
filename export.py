import logging

from selenium import webdriver

from Helpers.livelib_parser import slash_add
from Helpers.csv_reader import read_books_from_csv
from Helpers.csv_writer import save_books
from Helpers.arguments import get_arguments
import requests
import math
import os
import sys

from Modules.AppContext import AppContext
from Modules.BookLoader import BookLoader

logger = logging.getLogger(__name__)
app_context = AppContext()


def get_new_items(old_data, new_data):
    items = []
    for new in new_data:
        if new not in old_data and new not in items:
            items.append(new)
    return items


def configure_logging() -> None:
    logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s', level=logging.INFO)


if __name__ == "__main__":
    args = get_arguments()
    configure_logging()
    if args.driver == 'silenium':
        app_context.driver = webdriver.Chrome()

    ll_href = 'https://www.livelib.ru/reader'
    app_context.user_href = slash_add(ll_href, args.user)

    try:
        requests.get(app_context.user_href)
    except Exception as ex:
        logger.error(f'ERROR: Some troubles with downloading {app_context.user_href}:', ex)
        logger.error('Double-check your username')
        sys.exit(1)

    app_context.book_file = args.books_backup or 'backup_%s_book.csv' % args.user
    app_context.quote_file = args.quotes_backup or 'backup_%s_quote.csv' % args.user
    logger.info(f'Data from the page {app_context.user_href} will be saved to files {app_context.book_file} and '
                f'{app_context.quote_file}')
    app_context.rewrite_all = args.rewrite_all

    if args.skip != 'books':
        bl = BookLoader(app_context)
        books = []
        for status in ('read', 'reading', 'wish'):
            logger.info(f'Started parsing the book pages with status "{status}".')
            app_context.read_count = args.read_count if status == 'read' else math.inf
            books = books + bl.get_books(status)
            logger.info(f'The book pages with status "{status}" were parsed.')

        new_books = []
        if args.rewrite_all:
            new_books = books
            if os.path.exists(app_context.book_file):
                os.remove(app_context.book_file)
            logger.info(f'All books were deleted {app_context.book_file}.')
        else:
            logger.info(f'Started reading the books from {app_context.book_file}.')
            books_csv = read_books_from_csv(app_context.book_file)

            logger.info(f'Started calculating the newly added books.')
            new_books = get_new_items(books_csv, books)

        save_books(new_books, app_context.book_file)
        logger.info(f'The books were written to {app_context.book_file}.')

    if args.skip != 'quotes':
        logger.info('Started parsing the quote pages.')
        app_context.quote_count = args.quote_count or math.inf
        from Modules.QuoteLoader import QuoteLoader
        ql = QuoteLoader(app_context)
        quotes = ql.get_quotes()
        logger.info('The quote pages were parsed.')
        ql.save_quotes(quotes)
