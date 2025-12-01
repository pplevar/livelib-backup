"""
Unit tests for Book class
"""
import pytest
from Helpers.book import Book
from Helpers.utils import handle_none, add_livelib


class TestHandleNone:
    """Tests for handle_none helper function"""

    def test_handle_none_with_none(self):
        """Test that None returns empty string"""
        assert handle_none(None) == ''

    def test_handle_none_with_string(self):
        """Test that string is returned as-is"""
        assert handle_none('test') == 'test'

    def test_handle_none_with_number(self):
        """Test that numbers are returned as-is"""
        assert handle_none(42) == 42
        assert handle_none(3.14) == 3.14

    def test_handle_none_with_empty_string(self):
        """Test that empty string is returned as-is"""
        assert handle_none('') == ''


class TestAddLivelib:
    """Tests for add_livelib helper function"""

    def test_add_livelib_relative_path(self):
        """Test adding domain to relative path"""
        result = add_livelib('/book/123')
        assert result == 'https://www.livelib.ru/book/123'

    def test_add_livelib_full_url(self):
        """Test that full URL is not modified"""
        url = 'https://www.livelib.ru/book/456'
        assert add_livelib(url) == url

    def test_add_livelib_empty_string(self):
        """Test handling empty string"""
        result = add_livelib('')
        assert result == 'https://www.livelib.ru'


class TestBook:
    """Tests for Book class"""

    def test_book_initialization_with_all_params(self):
        """Test creating book with all parameters"""
        book = Book(
            link='/book/123',
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

    def test_book_initialization_with_none_values(self):
        """Test that None values are converted to empty strings"""
        book = Book(link='/book/456')
        assert book.name == ''
        assert book.author == ''
        assert book.status == ''
        assert book.rating == ''
        assert book.date == ''

    def test_book_initialization_no_params(self):
        """Test creating book with no parameters"""
        book = Book()
        assert book.name == ''
        assert book.author == ''
        assert book.link == 'https://www.livelib.ru'

    def test_book_str_representation(self):
        """Test string representation of book"""
        book = Book(
            link='/book/789',
            status='reading',
            name='Novel',
            author='Writer',
            rating='4',
            date='15.02.2024'
        )
        expected = 'Novel\tWriter\treading\t4\t15.02.2024\thttps://www.livelib.ru/book/789'
        assert str(book) == expected

    def test_book_equality_same_link(self):
        """Test that books with same link are equal"""
        book1 = Book(link='/book/111', name='Book A')
        book2 = Book(link='/book/111', name='Book B')
        assert book1 == book2

    def test_book_equality_different_link(self):
        """Test that books with different links are not equal"""
        book1 = Book(link='/book/111')
        book2 = Book(link='/book/222')
        assert book1 != book2

    def test_book_inequality(self):
        """Test inequality operator"""
        book1 = Book(link='/book/111')
        book2 = Book(link='/book/222')
        assert book1 != book2
        assert not (book1 != book1)

    def test_book_to_list(self):
        """Test converting book to list"""
        book = Book(
            link='/book/999',
            status='wish',
            name='Future Read',
            author='Someone',
            rating='',
            date=''
        )
        result = list(book.to_list())
        assert len(result) == 6
        assert 'Future Read' in result
        assert 'Someone' in result
        assert 'wish' in result

    def test_book_add_name(self):
        """Test adding name to book"""
        book = Book(link='/book/123')
        book.add_name('New Name')
        assert book.name == 'New Name'

    def test_book_add_author(self):
        """Test adding author to book"""
        book = Book(link='/book/123')
        book.add_author('New Author')
        assert book.author == 'New Author'

    def test_book_work_link(self):
        """Test book with /work/ link instead of /book/"""
        book = Book(link='/work/555')
        assert book.link == 'https://www.livelib.ru/work/555'

    def test_book_full_url_link(self):
        """Test book initialized with full URL"""
        book = Book(link='https://www.livelib.ru/book/777')
        assert book.link == 'https://www.livelib.ru/book/777'
