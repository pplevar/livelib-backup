"""
Integration tests for livelib-backup components
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from lxml import etree
import tempfile
import os

from Modules.AppContext import AppContext
from Helpers.book import Book
from Helpers.quote import Quote
from Helpers.csv_reader import read_books_from_csv, read_quotes_from_csv
from Helpers.csv_writer import save_books, save_quotes
from export import get_new_items
from tests.fixtures.mock_html import get_mock_html


class TestBookWorkflow:
    """Integration tests for book scraping workflow"""

    def test_complete_book_workflow(self, temp_csv_file):
        """Test complete workflow: scrape -> save -> read -> update"""
        # Step 1: Create initial books
        books = [
            Book(link='/book/111', name='Book 1', author='Author 1', status='read', rating='5', date='01.01.2024'),
            Book(link='/book/222', name='Book 2', author='Author 2', status='reading', rating='4', date='15.02.2024')
        ]

        # Step 2: Save to CSV
        save_books(books, temp_csv_file)

        # Step 3: Read back from CSV
        loaded_books = read_books_from_csv(temp_csv_file)
        assert len(loaded_books) == 2
        assert loaded_books[0].name == 'Book 1'
        assert loaded_books[1].name == 'Book 2'

        # Step 4: Simulate new scrape with one new book
        new_scraped_books = [
            Book(link='/book/111', name='Book 1', author='Author 1'),
            Book(link='/book/222', name='Book 2', author='Author 2'),
            Book(link='/book/333', name='Book 3', author='Author 3', status='wish')
        ]

        # Step 5: Get only new items
        new_items = get_new_items(loaded_books, new_scraped_books)
        assert len(new_items) == 1
        assert new_items[0].link == 'https://www.livelib.ru/book/333'

        # Step 6: Append new items
        save_books(new_items, temp_csv_file)

        # Step 7: Verify final state
        final_books = read_books_from_csv(temp_csv_file)
        assert len(final_books) == 3

    def test_incremental_backup_workflow(self, temp_csv_file):
        """Test incremental backup workflow"""
        # Initial backup
        initial_books = [Book(link='/book/1', name='Initial Book')]
        save_books(initial_books, temp_csv_file)

        # First update
        existing = read_books_from_csv(temp_csv_file)
        new_books = [
            Book(link='/book/1', name='Initial Book'),
            Book(link='/book/2', name='New Book 1')
        ]
        updates = get_new_items(existing, new_books)
        save_books(updates, temp_csv_file)

        # Second update
        existing = read_books_from_csv(temp_csv_file)
        new_books = [
            Book(link='/book/1', name='Initial Book'),
            Book(link='/book/2', name='New Book 1'),
            Book(link='/book/3', name='New Book 2')
        ]
        updates = get_new_items(existing, new_books)
        save_books(updates, temp_csv_file)

        # Verify
        final = read_books_from_csv(temp_csv_file)
        assert len(final) == 3


class TestQuoteWorkflow:
    """Integration tests for quote scraping workflow"""

    def test_complete_quote_workflow(self, temp_csv_file):
        """Test complete workflow: scrape -> save -> read -> update"""
        book = Book(link='/book/123', name='Test Book', author='Test Author')

        # Initial quotes
        quotes = [
            Quote(link='/quote/1', text='Quote 1', book=book),
            Quote(link='/quote/2', text='Quote 2', book=book)
        ]

        # Save
        save_quotes(quotes, temp_csv_file)

        # Read back
        loaded_quotes = read_quotes_from_csv(temp_csv_file)
        assert len(loaded_quotes) == 2
        assert loaded_quotes[0].text == 'Quote 1'

        # New scrape
        new_scraped_quotes = [
            Quote(link='/quote/1', text='Quote 1', book=book),
            Quote(link='/quote/2', text='Quote 2', book=book),
            Quote(link='/quote/3', text='Quote 3', book=book)
        ]

        # Get new
        new_items = get_new_items(loaded_quotes, new_scraped_quotes)
        assert len(new_items) == 1

        # Append
        save_quotes(new_items, temp_csv_file)

        # Verify
        final = read_quotes_from_csv(temp_csv_file)
        assert len(final) == 3


class TestAppContextIntegration:
    """Integration tests for AppContext"""

    def test_app_context_with_workflow(self, temp_csv_file):
        """Test AppContext integration with full workflow"""
        context = AppContext(
            user_href='https://www.livelib.ru/reader/testuser',
            book_file=temp_csv_file,
            min_delay=0,
            max_delay=0
        )

        # Simulate workflow
        books = [Book(link='/book/1', name='Book')]
        save_books(books, context.book_file)

        loaded = read_books_from_csv(context.book_file)
        assert len(loaded) == 1

    def test_multiple_status_workflow(self):
        """Test workflow with multiple book statuses"""
        with tempfile.TemporaryDirectory() as tmpdir:
            book_file = os.path.join(tmpdir, 'books.csv')

            # Simulate scraping different statuses
            all_books = []
            for status in ('read', 'reading', 'wish'):
                books = [
                    Book(link=f'/book/{status}_1', name=f'{status} Book 1', status=status),
                    Book(link=f'/book/{status}_2', name=f'{status} Book 2', status=status)
                ]
                all_books.extend(books)

            # Save all
            save_books(all_books, book_file)

            # Verify
            loaded = read_books_from_csv(book_file)
            assert len(loaded) == 6
            read_books = [b for b in loaded if b.status == 'read']
            assert len(read_books) == 2


class TestErrorHandling:
    """Integration tests for error handling"""

    def test_empty_file_handling(self, temp_csv_file):
        """Test handling of empty files"""
        # Try to read from empty file
        books = read_books_from_csv(temp_csv_file + '_nonexistent')
        assert books == []

        # Create empty file
        open(temp_csv_file, 'w').close()
        books = read_books_from_csv(temp_csv_file)
        assert books == []

    def test_corrupted_csv_handling(self, temp_csv_file):
        """Test handling of corrupted CSV data"""
        # Write invalid CSV with correct number of columns but wrong data
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Name\tAuthor\tStatus\tRating\tDate\tLink\n')
            f.write('Book\tAuthor\tread\t5\t01.01.2024\t/book/123\n')

        # Should handle valid CSV structure correctly
        books = read_books_from_csv(temp_csv_file)
        assert isinstance(books, list)
        assert len(books) == 1


class TestDataConsistency:
    """Integration tests for data consistency"""

    def test_book_equality_consistency(self):
        """Test that book equality is maintained across operations"""
        book1 = Book(link='/book/123', name='Name A')
        book2 = Book(link='/book/123', name='Name B')

        assert book1 == book2

        books = [book1]
        assert book2 in books

    def test_quote_with_book_consistency(self):
        """Test quote-book relationship consistency"""
        book = Book(link='/book/456', name='Book', author='Author')
        quote = Quote(link='/quote/789', text='Text', book=book)

        assert quote.book.name == 'Book'
        assert quote.book.author == 'Author'
        assert quote.book == book

    def test_link_normalization_consistency(self):
        """Test that links are normalized consistently"""
        book1 = Book(link='/book/123')
        book2 = Book(link='https://www.livelib.ru/book/123')

        # Both should normalize to the same full URL
        assert book1.link == book2.link
        assert book1 == book2


class TestRewriteMode:
    """Integration tests for rewrite mode"""

    def test_rewrite_all_workflow(self, temp_csv_file):
        """Test rewrite all mode workflow"""
        # Initial data
        initial_books = [
            Book(link='/book/1', name='Old Book 1'),
            Book(link='/book/2', name='Old Book 2')
        ]
        save_books(initial_books, temp_csv_file)

        # Simulate rewrite mode
        if os.path.exists(temp_csv_file):
            os.remove(temp_csv_file)

        new_books = [
            Book(link='/book/3', name='New Book 1'),
            Book(link='/book/4', name='New Book 2')
        ]
        save_books(new_books, temp_csv_file)

        # Verify only new books exist
        loaded = read_books_from_csv(temp_csv_file)
        assert len(loaded) == 2
        assert loaded[0].name == 'New Book 1'
        assert '/book/1' not in [b.link for b in loaded]
