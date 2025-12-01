"""
Unit tests for CSV writer module
"""
import pytest
import os
from Helpers.csv_writer import save_books, save_quotes
from Helpers.book import Book
from Helpers.quote import Quote


class TestSaveBooks:
    """Tests for save_books function"""

    def test_save_books_empty_list(self, temp_csv_file):
        """Test saving empty book list writes header"""
        save_books([], temp_csv_file)
        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # Empty list still writes header if file was empty
        assert 'Name\tAuthor\tStatus\tMy Rating\tDate\tLink' in content

    def test_save_books_new_file(self, temp_csv_file):
        """Test saving books to new file with header"""
        books = [
            Book(link='/book/123', status='read', name='Book1', author='Author1', rating='5', date='01.01.2024')
        ]
        save_books(books, temp_csv_file)
        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert 'Name\tAuthor\tStatus\tMy Rating\tDate\tLink' in lines[0]
        assert 'Book1\tAuthor1\tread\t5\t01.01.2024' in lines[1]

    def test_save_books_append_mode(self, temp_csv_file):
        """Test appending books to existing file"""
        books1 = [Book(link='/book/111', name='First', author='Author1')]
        books2 = [Book(link='/book/222', name='Second', author='Author2')]

        save_books(books1, temp_csv_file)
        save_books(books2, temp_csv_file)

        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == 3
        assert 'First' in lines[1]
        assert 'Second' in lines[2]

    def test_save_books_multiple_books(self, temp_csv_file):
        """Test saving multiple books at once"""
        books = [
            Book(link='/book/1', name='Book1', author='Author1'),
            Book(link='/book/2', name='Book2', author='Author2'),
            Book(link='/book/3', name='Book3', author='Author3')
        ]
        save_books(books, temp_csv_file)
        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == 4

    def test_save_books_utf8_encoding(self, temp_csv_file):
        """Test saving books with UTF-8 characters"""
        books = [
            Book(link='/book/999', name='Война и мир', author='Толстой')
        ]
        save_books(books, temp_csv_file)
        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'Война и мир' in content
        assert 'Толстой' in content


class TestSaveQuotes:
    """Tests for save_quotes function"""

    def test_save_quotes_empty_list(self, temp_csv_file):
        """Test saving empty quote list writes header"""
        save_quotes([], temp_csv_file)
        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # Empty list still writes header if file was empty
        assert 'Name\tAuthor\tQuote text\tBook link\tQuote link' in content

    def test_save_quotes_new_file(self, temp_csv_file):
        """Test saving quotes to new file with header"""
        book = Book(link='/book/123', name='Book', author='Author')
        quotes = [Quote(link='/quote/456', text='Quote text', book=book)]

        save_quotes(quotes, temp_csv_file)

        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert 'Name\tAuthor\tQuote text\tBook link\tQuote link' in lines[0]
        assert 'Book\tAuthor\tQuote text' in lines[1]

    def test_save_quotes_append_mode(self, temp_csv_file):
        """Test appending quotes to existing file"""
        book1 = Book(link='/book/111', name='Book1', author='Author1')
        book2 = Book(link='/book/222', name='Book2', author='Author2')

        quotes1 = [Quote(link='/quote/1', text='First quote', book=book1)]
        quotes2 = [Quote(link='/quote/2', text='Second quote', book=book2)]

        save_quotes(quotes1, temp_csv_file)
        save_quotes(quotes2, temp_csv_file)

        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == 3
        assert 'First quote' in lines[1]
        assert 'Second quote' in lines[2]

    def test_save_quotes_multiple_quotes(self, temp_csv_file):
        """Test saving multiple quotes at once"""
        book = Book(link='/book/123', name='Book', author='Author')
        quotes = [
            Quote(link='/quote/1', text='Quote1', book=book),
            Quote(link='/quote/2', text='Quote2', book=book),
            Quote(link='/quote/3', text='Quote3', book=book)
        ]
        save_quotes(quotes, temp_csv_file)
        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == 4

    def test_save_quotes_utf8_encoding(self, temp_csv_file):
        """Test saving quotes with UTF-8 characters"""
        book = Book(link='/book/999', name='Книга', author='Автор')
        quotes = [Quote(link='/quote/888', text='Русская цитата', book=book)]

        save_quotes(quotes, temp_csv_file)

        with open(temp_csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'Русская цитата' in content
        assert 'Книга' in content
