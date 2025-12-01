"""
Unit tests for livelib_parser module
"""
import pytest
from lxml import etree
from Helpers.livelib_parser import (
    try_parse_month,
    is_last_page,
    is_redirecting_page,
    href_i,
    date_parser,
    handle_xpath,
    slash_add
)


class TestTryParseMonth:
    """Tests for try_parse_month function"""

    def test_parse_january(self):
        """Test parsing January in Russian"""
        assert try_parse_month('Январь') == '01'

    def test_parse_february(self):
        """Test parsing February in Russian"""
        assert try_parse_month('Февраль') == '02'

    def test_parse_march(self):
        """Test parsing March in Russian"""
        assert try_parse_month('Март') == '03'

    def test_parse_december(self):
        """Test parsing December in Russian"""
        assert try_parse_month('Декабрь') == '12'

    def test_parse_invalid_month(self):
        """Test parsing invalid month returns default"""
        assert try_parse_month('InvalidMonth') == '01'

    def test_parse_all_months(self):
        """Test parsing all months"""
        months = {
            'Январь': '01', 'Февраль': '02', 'Март': '03',
            'Апрель': '04', 'Май': '05', 'Июнь': '06',
            'Июль': '07', 'Август': '08', 'Сентябрь': '09',
            'Октябрь': '10', 'Ноябрь': '11', 'Декабрь': '12'
        }
        for month, expected in months.items():
            assert try_parse_month(month) == expected


class TestIsLastPage:
    """Tests for is_last_page function"""

    def test_is_last_page_true(self):
        """Test detecting last page with empty content"""
        html = '<html><div class="with-pad">Empty page</div></html>'
        page = etree.HTML(html)
        assert is_last_page(page) is True

    def test_is_last_page_false(self):
        """Test detecting non-last page"""
        html = '<html><div class="content">Some content</div></html>'
        page = etree.HTML(html)
        assert is_last_page(page) is False

    def test_is_last_page_empty(self):
        """Test empty page"""
        html = '<html></html>'
        page = etree.HTML(html)
        assert is_last_page(page) is False


class TestIsRedirectingPage:
    """Tests for is_redirecting_page function"""

    def test_is_redirecting_page_true(self, capsys):
        """Test detecting 404 redirect page"""
        html = '<html><div class="page-404">Not found</div></html>'
        page = etree.HTML(html)
        result = is_redirecting_page(page)
        assert result is True
        captured = capsys.readouterr()
        assert 'bot' in captured.out.lower()

    def test_is_redirecting_page_false(self):
        """Test detecting normal page"""
        html = '<html><div class="content">Normal page</div></html>'
        page = etree.HTML(html)
        assert is_redirecting_page(page) is False


class TestHrefI:
    """Tests for href_i function"""

    def test_href_i_first_page(self):
        """Test generating link for first page"""
        result = href_i('https://example.com/books', 1)
        assert result == 'https://example.com/books/~1'

    def test_href_i_tenth_page(self):
        """Test generating link for tenth page"""
        result = href_i('https://example.com/books', 10)
        assert result == 'https://example.com/books/~10'

    def test_href_i_zero_page(self):
        """Test generating link for page zero"""
        result = href_i('https://example.com/books', 0)
        assert result == 'https://example.com/books/~0'


class TestDateParser:
    """Tests for date_parser function"""

    def test_date_parser_valid_date(self):
        """Test parsing valid Russian date"""
        result = date_parser('Январь 2024 г.')
        assert result == '2024-01-01'

    def test_date_parser_february(self):
        """Test parsing February date"""
        result = date_parser('Февраль 2023 г.')
        assert result == '2023-02-01'

    def test_date_parser_december(self):
        """Test parsing December date"""
        result = date_parser('Декабрь 2022 г.')
        assert result == '2022-12-01'

    def test_date_parser_invalid_format(self):
        """Test parsing invalid date format"""
        result = date_parser('Invalid date')
        assert result is None

    def test_date_parser_partial_date(self):
        """Test parsing date without month name"""
        # The regex requires both month name and year
        # If only year is present, month defaults to '01' (January)
        result = date_parser('2024 г.')
        # Since there's no month name, try_parse_month returns default '01'
        assert result == '2024-01-01' or result is None

    def test_date_parser_empty_string(self):
        """Test parsing empty string"""
        result = date_parser('')
        assert result is None


class TestHandleXpath:
    """Tests for handle_xpath function"""

    def test_handle_xpath_found(self):
        """Test xpath when element is found"""
        html = '<html><div class="test">Content</div></html>'
        node = etree.HTML(html)
        result = handle_xpath(node, '//div[@class="test"]')
        assert result is not None
        assert result.text == 'Content'

    def test_handle_xpath_not_found(self):
        """Test xpath when element is not found"""
        html = '<html><div class="other">Content</div></html>'
        node = etree.HTML(html)
        result = handle_xpath(node, '//div[@class="test"]')
        assert result is None

    def test_handle_xpath_with_index(self):
        """Test xpath with specific index"""
        html = '<html><div>First</div><div>Second</div><div>Third</div></html>'
        node = etree.HTML(html)
        result = handle_xpath(node, '//div', i=1)
        assert result.text == 'Second'

    def test_handle_xpath_index_out_of_range(self):
        """Test xpath with index out of range"""
        html = '<html><div>Only one</div></html>'
        node = etree.HTML(html)
        result = handle_xpath(node, '//div', i=5)
        assert result is None

    def test_handle_xpath_none_node(self):
        """Test xpath with None node"""
        result = handle_xpath(None, '//div')
        assert result is None

    def test_handle_xpath_multiple_elements(self):
        """Test xpath returning multiple elements"""
        html = '<html><p>1</p><p>2</p><p>3</p></html>'
        node = etree.HTML(html)
        result = handle_xpath(node, '//p', i=0)
        assert result.text == '1'
        result = handle_xpath(node, '//p', i=2)
        assert result.text == '3'


class TestSlashAdd:
    """Tests for slash_add function"""

    def test_slash_add_basic(self):
        """Test basic slash_add functionality"""
        result = slash_add('https://example.com', 'path')
        assert result == 'https://example.com/path'

    def test_slash_add_multiple_parts(self):
        """Test slash_add with multiple calls"""
        result = slash_add('https://example.com', 'user')
        assert result == 'https://example.com/user'
        result = slash_add(result, 'profile')
        assert result == 'https://example.com/user/profile'

    def test_slash_add_empty_right(self):
        """Test slash_add with empty right part"""
        result = slash_add('https://example.com', '')
        assert result == 'https://example.com/'

    def test_slash_add_empty_left(self):
        """Test slash_add with empty left part"""
        result = slash_add('', 'path')
        assert result == '/path'
