"""
Unit tests for Quote class
"""
import pytest
from Helpers.quote import Quote, handle_none, add_livelib
from Helpers.book import Book


class TestQuoteHelpers:
    """Tests for Quote helper functions"""

    def test_handle_none_with_none(self):
        """Test that None returns empty string"""
        assert handle_none(None) == ''

    def test_handle_none_with_value(self):
        """Test that value is returned as-is"""
        assert handle_none('text') == 'text'

    def test_add_livelib_relative(self):
        """Test adding domain to relative path"""
        assert add_livelib('/quote/123') == 'https://www.livelib.ru/quote/123'

    def test_add_livelib_absolute(self):
        """Test that absolute URL is not modified"""
        url = 'https://www.livelib.ru/quote/456'
        assert add_livelib(url) == url


class TestQuote:
    """Tests for Quote class"""

    def test_quote_initialization_with_book(self):
        """Test creating quote with book object"""
        book = Book(
            link='/book/123',
            name='Test Book',
            author='Test Author'
        )
        quote = Quote(
            link='/quote/456',
            text='This is a test quote.',
            book=book
        )
        assert quote.link == 'https://www.livelib.ru/quote/456'
        assert quote.text == 'This is a test quote.'
        assert quote.book == book
        assert quote.book.name == 'Test Book'

    def test_quote_initialization_without_book(self):
        """Test creating quote without book object"""
        quote = Quote(
            link='/quote/789',
            text='Quote without book'
        )
        assert quote.link == 'https://www.livelib.ru/quote/789'
        assert quote.text == 'Quote without book'
        assert isinstance(quote.book, Book)
        assert quote.book.name == ''

    def test_quote_initialization_with_none_values(self):
        """Test that None values are handled correctly"""
        quote = Quote(link=None, text=None)
        assert quote.link == 'https://www.livelib.ru'
        assert quote.text == ''

    def test_quote_str_representation(self):
        """Test string representation of quote"""
        book = Book(
            link='/book/111',
            name='Novel',
            author='Writer'
        )
        quote = Quote(
            link='/quote/222',
            text='Interesting quote text',
            book=book
        )
        expected = 'Novel\tWriter\tInteresting quote text\thttps://www.livelib.ru/book/111\thttps://www.livelib.ru/quote/222'
        assert str(quote) == expected

    def test_quote_equality_same_link(self):
        """Test that quotes with same link are equal"""
        quote1 = Quote(link='/quote/111', text='Text A')
        quote2 = Quote(link='/quote/111', text='Text B')
        assert quote1 == quote2

    def test_quote_equality_different_link(self):
        """Test that quotes with different links are not equal"""
        quote1 = Quote(link='/quote/111', text='Text')
        quote2 = Quote(link='/quote/222', text='Text')
        assert quote1 != quote2

    def test_quote_inequality(self):
        """Test inequality operator"""
        quote1 = Quote(link='/quote/111', text='Text')
        quote2 = Quote(link='/quote/222', text='Text')
        assert quote1 != quote2
        assert not (quote1 != quote1)

    def test_quote_to_list(self):
        """Test converting quote to list"""
        book = Book(link='/book/333', name='Book', author='Author')
        quote = Quote(
            link='/quote/444',
            text='Quote text',
            book=book
        )
        result = list(quote.to_list())
        assert len(result) == 3
        assert 'Quote text' in [str(item) for item in result]

    def test_quote_add_book(self):
        """Test adding book to quote"""
        quote = Quote(link='/quote/555', text='Text')
        new_book = Book(
            link='/book/666',
            name='New Book',
            author='New Author'
        )
        quote.add_book(new_book)
        assert quote.book == new_book
        assert quote.book.name == 'New Book'

    def test_quote_full_url_link(self):
        """Test quote initialized with full URL"""
        quote = Quote(
            link='https://www.livelib.ru/quote/777',
            text='Full URL quote'
        )
        assert quote.link == 'https://www.livelib.ru/quote/777'

    def test_quote_with_empty_book(self):
        """Test quote with default empty book"""
        quote = Quote(link='/quote/888', text='Text')
        assert quote.book.link == 'https://www.livelib.ru'
        assert quote.book.name == ''
        assert quote.book.author == ''
