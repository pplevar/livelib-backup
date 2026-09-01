#!/usr/bin/env python3
"""
LiveLib Backup - Export user books and quotes from LiveLib.ru

Saves book lists (read, reading, wish) and quotes to CSV files.
No authorization required.

Usage:
    python export.py username [--books_backup FILE] [--quotes_backup FILE]
    python export.py --help
"""
import logging
import sys
import math
from typing import List

from Helpers.config import BackupConfig
from Helpers.arguments import get_arguments
from Modules.BookLoader import BookLoader
from Modules.QuoteLoader import QuoteLoader

# Configure logging
logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        format='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s',
        level=logging.INFO
    )


def get_new_items(old_data: List, new_data: List) -> List:
    """
    Find items in new_data that are not in old_data.
    
    Args:
        old_data: Existing items
        new_data: Newly fetched items
        
    Returns:
        List of new items
    """
    items = []
    for new in new_data:
        if new not in old_data and new not in items:
            items.append(new)
    return items


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = get_arguments()
    configure_logging()
    
    # Create configuration from arguments
    try:
        config = BackupConfig(
            username=args.user,
            books_file=args.books_backup,
            quotes_file=args.quotes_backup,
            min_delay=args.min_delay,
            max_delay=args.max_delay,
            read_count=args.read_count,
            quote_count=args.quote_count,
            rewrite_all=args.rewrite_all,
            driver_type=args.driver or 'requests',
            skip_books=args.skip == 'books',
            skip_quotes=args.skip == 'quotes'
        )
    except ValueError as e:
        logger.error('Configuration error: %s', e)
        return 1
    
    logger.info('LiveLib Backup starting...')
    logger.info('User: %s', config.username)
    logger.info('Books file: %s', config.get_books_file_path())
    logger.info('Quotes file: %s', config.get_quotes_file_path())
    
    # Initialize Selenium driver if requested
    driver = None
    if config.driver_type == 'selenium':
        try:
            from selenium import webdriver
            driver = webdriver.Chrome()
            logger.info('Selenium Chrome driver initialized')
        except Exception as e:
            logger.error('Failed to initialize Selenium driver: %s', e)
            return 1
    
    try:
        # Verify user profile exists
        import requests
        user_href = config.get_user_href()
        try:
            response = requests.get(user_href, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error('Cannot access user profile %s: %s', user_href, e)
            logger.error('Please check your username')
            return 1
        
        # Process books
        if not config.skip_books:
            logger.info('=== Processing Books ===')
            book_loader = BookLoader(config, driver)
            all_books: List = []
            
            for status in ('read', 'reading', 'wish'):
                logger.info('Fetching books with status: %s', status)
                books = book_loader.get_books(status, config.read_count)
                all_books.extend(books)
                logger.info('Found %d books with status "%s"', len(books), status)
            
            # Save books (BookLoader merges new/updated books into the existing backup)
            if all_books:
                book_loader.save_books(all_books)
            else:
                logger.info('No books to save')
        
        # Process quotes
        if not config.skip_quotes:
            logger.info('=== Processing Quotes ===')
            quote_loader = QuoteLoader(config, driver)
            quotes = quote_loader.get_quotes(config.quote_count)
            logger.info('Found %d quotes', len(quotes))
            
            if quotes:
                quote_loader.save_quotes(quotes)
                logger.info('Saved %d quotes to %s', len(quotes), config.get_quotes_file_path())
            else:
                logger.info('No quotes to save')
        
        logger.info('=== Backup Complete ===')
        return 0
        
    except KeyboardInterrupt:
        logger.info('Backup interrupted by user (Ctrl+C)')
        logger.info('No data was saved if interruption occurred before write')
        return 130
    except Exception as e:
        logger.exception('Unexpected error during backup: %s', e)
        return 1
    finally:
        # Clean up Selenium driver
        if driver is not None:
            try:
                driver.quit()
                logger.info('Selenium driver closed')
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())
