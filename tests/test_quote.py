"""
Unit tests for Quote class
"""
import pytest
from Helpers.quote import Quote
from Helpers.book import Book


class TestQuote:
    """Tests for Quote class"""

    def test_quote_initialization_with_book(self):
        """Test creating quote with a book object"""
        book = Book(
            link='https://www.livelib.ru/book/123',
            status='read',
            name='Test Book',
            author='Test Author'
        )
        quote = Quote(
            link='https://www.livelib.ru/quote/456',
            text='This is a test quote.',
            book=book
        )
        assert quote.link == 'https://www.livelib.ru/quote/456'
        assert quote.text == 'This is a test quote.'
        assert quote.book == book
        assert quote.book.name == 'Test Book'

    def test_quote_requires_link(self):
        """Test that a missing link is rejected"""
        book = Book(link='https://www.livelib.ru/book/123', status='read')
        with pytest.raises(ValueError, match='Invalid quote link'):
            Quote(link=None, text='Text', book=book)

    def test_quote_requires_absolute_url(self):
        """Test that a relative link (no scheme) is rejected"""
        book = Book(link='https://www.livelib.ru/book/123', status='read')
        with pytest.raises(ValueError, match='Invalid quote link'):
            Quote(link='/quote/456', text='Text', book=book)

    def test_quote_requires_quote_in_link(self):
        """Test that a link without /quote/ is rejected"""
        book = Book(link='https://www.livelib.ru/book/123', status='read')
        with pytest.raises(ValueError, match='Invalid quote link'):
            Quote(link='https://www.livelib.ru/book/456', text='Text', book=book)

    def test_quote_requires_non_empty_text(self):
        """Test that empty text is rejected"""
        book = Book(link='https://www.livelib.ru/book/123', status='read')
        with pytest.raises(ValueError, match='cannot be empty'):
            Quote(link='https://www.livelib.ru/quote/456', text='', book=book)

    def test_quote_requires_non_blank_text(self):
        """Test that whitespace-only text is rejected"""
        book = Book(link='https://www.livelib.ru/book/123', status='read')
        with pytest.raises(ValueError, match='cannot be empty'):
            Quote(link='https://www.livelib.ru/quote/456', text='   ', book=book)

    def test_quote_requires_book_instance(self):
        """Test that book must be a Book instance"""
        with pytest.raises(ValueError, match='must be a Book instance'):
            Quote(link='https://www.livelib.ru/quote/456', text='Text', book='not a book')

    def test_quote_str_representation(self):
        """Test string representation of quote"""
        book = Book(
            link='https://www.livelib.ru/book/111',
            status='read',
            name='Novel',
            author='Writer'
        )
        quote = Quote(
            link='https://www.livelib.ru/quote/222',
            text='Interesting quote text',
            book=book
        )
        expected = (
            'Novel\tWriter\tInteresting quote text\t'
            'https://www.livelib.ru/book/111\thttps://www.livelib.ru/quote/222'
        )
        assert str(quote) == expected

    def test_quote_str_representation_with_missing_book_fields(self):
        """Test string representation falls back to empty strings for missing book fields"""
        book = Book(link='https://www.livelib.ru/book/111', status='read')
        quote = Quote(link='https://www.livelib.ru/quote/222', text='Text', book=book)
        expected = '\t\tText\thttps://www.livelib.ru/book/111\thttps://www.livelib.ru/quote/222'
        assert str(quote) == expected

    def test_quote_equality_same_link(self):
        """Test that quotes with same link are equal"""
        book = Book(link='https://www.livelib.ru/book/1', status='read')
        quote1 = Quote(link='https://www.livelib.ru/quote/111', text='Text A', book=book)
        quote2 = Quote(link='https://www.livelib.ru/quote/111', text='Text B', book=book)
        assert quote1 == quote2

    def test_quote_equality_different_link(self):
        """Test that quotes with different links are not equal"""
        book = Book(link='https://www.livelib.ru/book/1', status='read')
        quote1 = Quote(link='https://www.livelib.ru/quote/111', text='Text', book=book)
        quote2 = Quote(link='https://www.livelib.ru/quote/222', text='Text', book=book)
        assert quote1 != quote2

    def test_quote_not_equal_to_non_quote(self):
        """Test that a Quote never equals a non-Quote object"""
        book = Book(link='https://www.livelib.ru/book/1', status='read')
        quote = Quote(link='https://www.livelib.ru/quote/111', text='Text', book=book)
        assert quote != 'https://www.livelib.ru/quote/111'

    def test_quote_hash_based_on_link(self):
        """Test that quotes with the same link hash the same"""
        book = Book(link='https://www.livelib.ru/book/1', status='read')
        quote1 = Quote(link='https://www.livelib.ru/quote/111', text='Text A', book=book)
        quote2 = Quote(link='https://www.livelib.ru/quote/111', text='Text B', book=book)
        assert hash(quote1) == hash(quote2)
        assert len({quote1, quote2}) == 1
