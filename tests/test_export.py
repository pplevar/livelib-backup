"""
Unit tests for export.py functions
"""
import pytest
from export import get_new_items
from Helpers.book import Book
from Helpers.quote import Quote


class TestGetNewItems:
    """Tests for get_new_items function"""

    def test_get_new_items_empty_lists(self):
        """Test with both lists empty"""
        result = get_new_items([], [])
        assert result == []

    def test_get_new_items_all_new(self):
        """Test when all items in new_data are new"""
        old_data = []
        new_data = [
            Book(link='/book/1', name='Book1'),
            Book(link='/book/2', name='Book2')
        ]
        result = get_new_items(old_data, new_data)
        assert len(result) == 2
        assert all(item in result for item in new_data)

    def test_get_new_items_no_new(self):
        """Test when no new items exist"""
        data = [
            Book(link='/book/1', name='Book1'),
            Book(link='/book/2', name='Book2')
        ]
        result = get_new_items(data, data)
        assert result == []

    def test_get_new_items_some_new(self):
        """Test with mix of old and new items"""
        old_data = [
            Book(link='/book/1', name='Old Book')
        ]
        new_data = [
            Book(link='/book/1', name='Old Book'),
            Book(link='/book/2', name='New Book')
        ]
        result = get_new_items(old_data, new_data)
        assert len(result) == 1
        assert result[0].link == 'https://www.livelib.ru/book/2'

    def test_get_new_items_duplicates_removed(self):
        """Test that duplicates in new_data are removed"""
        old_data = []
        new_data = [
            Book(link='/book/1', name='Book1'),
            Book(link='/book/1', name='Book1'),
            Book(link='/book/2', name='Book2')
        ]
        result = get_new_items(old_data, new_data)
        assert len(result) == 2

    def test_get_new_items_with_quotes(self):
        """Test get_new_items with Quote objects"""
        book = Book(link='/book/123')
        old_data = [
            Quote(link='/quote/1', text='Old quote', book=book)
        ]
        new_data = [
            Quote(link='/quote/1', text='Old quote', book=book),
            Quote(link='/quote/2', text='New quote', book=book)
        ]
        result = get_new_items(old_data, new_data)
        assert len(result) == 1
        assert result[0].link == 'https://www.livelib.ru/quote/2'

    def test_get_new_items_order_preserved(self):
        """Test that order of new items is preserved"""
        old_data = []
        new_data = [
            Book(link='/book/3', name='Third'),
            Book(link='/book/1', name='First'),
            Book(link='/book/2', name='Second')
        ]
        result = get_new_items(old_data, new_data)
        assert result[0].name == 'Third'
        assert result[1].name == 'First'
        assert result[2].name == 'Second'

    def test_get_new_items_equality_based_on_link(self):
        """Test that equality is based on link, not other attributes"""
        old_data = [
            Book(link='/book/1', name='Original Name', author='Author A')
        ]
        new_data = [
            Book(link='/book/1', name='Different Name', author='Author B')
        ]
        result = get_new_items(old_data, new_data)
        assert result == []
