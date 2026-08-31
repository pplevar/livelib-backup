"""
Unit tests for Book class
"""
import pytest
from Helpers.book import Book


class TestBook:
    """Tests for Book class"""

    def test_book_initialization_with_all_params(self):
        """Test creating book with all parameters"""
        book = Book(
            link='https://www.livelib.ru/book/123',
            status='read',
            name='Test Book',
            author='Test Author',
            rating='5',
            date='01.01.2024'
        )
        assert book.name == 'Test Book'
        assert book.author == 'Test Author'
        assert book.status == 'read'
        assert book.rating == '5'
        assert book.date == '01.01.2024'
        assert book.link == 'https://www.livelib.ru/book/123'

    def test_book_initialization_with_none_optional_values(self):
        """Test that optional fields default to None"""
        book = Book(link='https://www.livelib.ru/book/456', status='wish')
        assert book.name is None
        assert book.author is None
        assert book.rating is None
        assert book.date is None

    def test_book_requires_link(self):
        """Test that a missing link is rejected"""
        with pytest.raises(ValueError, match='Invalid book link'):
            Book(link=None, status='read')

    def test_book_requires_absolute_url(self):
        """Test that a relative link (no scheme) is rejected"""
        with pytest.raises(ValueError, match='Invalid book link'):
            Book(link='/book/123', status='read')

    def test_book_requires_book_or_work_in_link(self):
        """Test that a link without /book/ or /work/ is rejected"""
        with pytest.raises(ValueError, match='Invalid book link'):
            Book(link='https://www.livelib.ru/author/123', status='read')

    def test_book_accepts_work_link(self):
        """Test that a /work/ link is valid"""
        book = Book(link='https://www.livelib.ru/work/555', status='read')
        assert book.link == 'https://www.livelib.ru/work/555'

    def test_book_requires_valid_status(self):
        """Test that an invalid status is rejected"""
        with pytest.raises(ValueError, match="Invalid status"):
            Book(link='https://www.livelib.ru/book/123', status='unknown')

    @pytest.mark.parametrize('status', ['read', 'reading', 'wish'])
    def test_book_accepts_valid_statuses(self, status):
        book = Book(link='https://www.livelib.ru/book/123', status=status)
        assert book.status == status

    def test_book_str_representation(self):
        """Test string representation of book"""
        book = Book(
            link='https://www.livelib.ru/book/789',
            status='reading',
            name='Novel',
            author='Writer',
            rating='4',
            date='15.02.2024'
        )
        expected = 'Novel\tWriter\treading\t4\t15.02.2024\thttps://www.livelib.ru/book/789'
        assert str(book) == expected

    def test_book_str_representation_with_missing_fields(self):
        """Test string representation falls back to empty strings for missing fields"""
        book = Book(link='https://www.livelib.ru/book/789', status='wish')
        expected = '\t\twish\t\t\thttps://www.livelib.ru/book/789'
        assert str(book) == expected

    def test_book_equality_same_link(self):
        """Test that books with same link are equal"""
        book1 = Book(link='https://www.livelib.ru/book/111', status='read', name='Book A')
        book2 = Book(link='https://www.livelib.ru/book/111', status='wish', name='Book B')
        assert book1 == book2

    def test_book_equality_different_link(self):
        """Test that books with different links are not equal"""
        book1 = Book(link='https://www.livelib.ru/book/111', status='read')
        book2 = Book(link='https://www.livelib.ru/book/222', status='read')
        assert book1 != book2

    def test_book_not_equal_to_non_book(self):
        """Test that a Book never equals a non-Book object"""
        book = Book(link='https://www.livelib.ru/book/111', status='read')
        assert book != 'https://www.livelib.ru/book/111'

    def test_book_hash_based_on_link(self):
        """Test that books with the same link hash the same"""
        book1 = Book(link='https://www.livelib.ru/book/111', status='read')
        book2 = Book(link='https://www.livelib.ru/book/111', status='wish')
        assert hash(book1) == hash(book2)
        assert len({book1, book2}) == 1
