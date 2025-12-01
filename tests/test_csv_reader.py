"""
Unit tests for CSV reader module
"""
import pytest
import os
import tempfile
from Helpers.csv_reader import (
    read_csv,
    convert_csv_to_books,
    convert_csv_to_quotes,
    read_books_from_csv,
    read_quotes_from_csv
)
from Helpers.book import Book
from Helpers.quote import Quote


class TestReadCsv:
    """Tests for read_csv function"""

    def test_read_csv_nonexistent_file(self):
        """Test reading non-existent file returns empty list"""
        result = read_csv('/nonexistent/file.csv')
        assert result == []

    def test_read_csv_empty_file(self, temp_csv_file):
        """Test reading empty CSV file"""
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Header1\tHeader2\tHeader3\n')
        result = read_csv(temp_csv_file)
        assert result == []

    def test_read_csv_with_data(self, temp_csv_file):
        """Test reading CSV file with data"""
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Name\tAuthor\tStatus\n')
            f.write('Book1\tAuthor1\tread\n')
            f.write('Book2\tAuthor2\treading\n')
        result = read_csv(temp_csv_file)
        assert len(result) == 2
        assert result[0] == ['Book1', 'Author1', 'read']
        assert result[1] == ['Book2', 'Author2', 'reading']

    def test_read_csv_skip_header(self, temp_csv_file):
        """Test that header is skipped"""
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Col1\tCol2\n')
            f.write('data1\tdata2\n')
        result = read_csv(temp_csv_file)
        assert len(result) == 1
        assert 'Col1' not in result[0]

    def test_read_csv_utf8_encoding(self, temp_csv_file):
        """Test reading CSV with UTF-8 characters"""
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Name\tAuthor\n')
            f.write('Война и мир\tТолстой\n')
        result = read_csv(temp_csv_file)
        assert result[0] == ['Война и мир', 'Толстой']


class TestConvertCsvToBooks:
    """Tests for convert_csv_to_books function"""

    def test_convert_empty_list(self):
        """Test converting empty list"""
        result = convert_csv_to_books([])
        assert result == []

    def test_convert_single_book(self):
        """Test converting single book"""
        cache = [['Book Name', 'Author Name', 'read', '5', '01.01.2024', '/book/123']]
        result = convert_csv_to_books(cache)
        assert len(result) == 1
        assert isinstance(result[0], Book)
        assert result[0].name == 'Book Name'
        assert result[0].author == 'Author Name'
        assert result[0].status == 'read'
        assert result[0].rating == '5'
        assert result[0].date == '01.01.2024'
        assert '/book/123' in result[0].link

    def test_convert_multiple_books(self):
        """Test converting multiple books"""
        cache = [
            ['Book1', 'Author1', 'read', '5', '01.01.2024', '/book/111'],
            ['Book2', 'Author2', 'reading', '4', '15.02.2024', '/book/222'],
            ['Book3', 'Author3', 'wish', '', '', '/work/333']
        ]
        result = convert_csv_to_books(cache)
        assert len(result) == 3
        assert all(isinstance(book, Book) for book in result)
        assert result[0].name == 'Book1'
        assert result[1].status == 'reading'
        assert result[2].rating == ''


class TestConvertCsvToQuotes:
    """Tests for convert_csv_to_quotes function"""

    def test_convert_empty_list(self):
        """Test converting empty list"""
        result = convert_csv_to_quotes([])
        assert result == []

    def test_convert_single_quote(self):
        """Test converting single quote"""
        cache = [['Book Name', 'Author', 'Quote text here', '/book/123', '/quote/456']]
        result = convert_csv_to_quotes(cache)
        assert len(result) == 1
        assert isinstance(result[0], Quote)
        assert result[0].text == 'Quote text here'
        assert result[0].book.name == 'Book Name'
        assert result[0].book.author == 'Author'
        assert '/quote/456' in result[0].link

    def test_convert_multiple_quotes(self):
        """Test converting multiple quotes"""
        cache = [
            ['Book1', 'Author1', 'Quote1', '/book/111', '/quote/1'],
            ['Book2', 'Author2', 'Quote2', '/book/222', '/quote/2'],
            ['Book3', 'Author3', 'Quote3', '/book/333', '/quote/3']
        ]
        result = convert_csv_to_quotes(cache)
        assert len(result) == 3
        assert all(isinstance(quote, Quote) for quote in result)
        assert result[0].text == 'Quote1'
        assert result[1].book.name == 'Book2'
        assert '/quote/3' in result[2].link


class TestReadBooksFromCsv:
    """Tests for read_books_from_csv function"""

    def test_read_books_nonexistent_file(self):
        """Test reading books from non-existent file"""
        result = read_books_from_csv('/nonexistent/books.csv')
        assert result == []

    def test_read_books_valid_file(self, temp_csv_file):
        """Test reading books from valid CSV file"""
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Name\tAuthor\tStatus\tRating\tDate\tLink\n')
            f.write('Test Book\tTest Author\tread\t5\t01.01.2024\t/book/123\n')
        result = read_books_from_csv(temp_csv_file)
        assert len(result) == 1
        assert isinstance(result[0], Book)
        assert result[0].name == 'Test Book'

    def test_read_books_multiple_entries(self, temp_csv_file):
        """Test reading multiple books"""
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Name\tAuthor\tStatus\tRating\tDate\tLink\n')
            f.write('Book1\tAuthor1\tread\t5\t01.01.2024\t/book/1\n')
            f.write('Book2\tAuthor2\treading\t4\t15.02.2024\t/book/2\n')
            f.write('Book3\tAuthor3\twish\t\t\t/work/3\n')
        result = read_books_from_csv(temp_csv_file)
        assert len(result) == 3


class TestReadQuotesFromCsv:
    """Tests for read_quotes_from_csv function"""

    def test_read_quotes_nonexistent_file(self):
        """Test reading quotes from non-existent file"""
        result = read_quotes_from_csv('/nonexistent/quotes.csv')
        assert result == []

    def test_read_quotes_valid_file(self, temp_csv_file):
        """Test reading quotes from valid CSV file"""
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Name\tAuthor\tQuote\tBook Link\tQuote Link\n')
            f.write('Book\tAuthor\tQuote text\t/book/123\t/quote/456\n')
        result = read_quotes_from_csv(temp_csv_file)
        assert len(result) == 1
        assert isinstance(result[0], Quote)
        assert result[0].text == 'Quote text'
        assert result[0].book.name == 'Book'

    def test_read_quotes_multiple_entries(self, temp_csv_file):
        """Test reading multiple quotes"""
        with open(temp_csv_file, 'w', encoding='utf-8') as f:
            f.write('Name\tAuthor\tQuote\tBook Link\tQuote Link\n')
            f.write('Book1\tAuthor1\tQuote1\t/book/1\t/quote/1\n')
            f.write('Book2\tAuthor2\tQuote2\t/book/2\t/quote/2\n')
        result = read_quotes_from_csv(temp_csv_file)
        assert len(result) == 2
