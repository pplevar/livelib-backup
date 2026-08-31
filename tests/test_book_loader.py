"""
Tests for Modules/BookLoader.py
"""
import math
from unittest.mock import patch

from lxml import html

from Modules.BookLoader import BookLoader


BOOK_ROW = """
<div>
    <div>
        <div>
            <div class="brow-data">
                <div>
                    <a href="/book/123456-test-book" class="brow-book-name">Test Book</a>
                    <a href="/author/1-author" class="brow-book-author">Author One</a>
                    <a href="/author/2-author" class="brow-book-author">Author Two</a>
                    <div class="brow-ratings"><span><span><span>5</span></span></span></div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

BOOKLIST_PAGE = """
<html><body>
<div id="booklist">
    <div><h2>Январь 2024 г.</h2></div>
    %s
    %s
</div>
</body></html>
""" % (BOOK_ROW, BOOK_ROW.replace('123456', '999999'))

EMPTY_PAGE = """
<html><body><div class="with-pad"><p>Страница пуста</p></div></body></html>
"""

REDIRECT_PAGE = """
<html><body><div class="page-404"><h1>404</h1></div></body></html>
"""


class TestTryGetBookLink:
    def test_book_link_is_valid(self):
        assert BookLoader.try_get_book_link('/book/123') == '/book/123'

    def test_work_link_is_valid(self):
        assert BookLoader.try_get_book_link('/work/123') == '/work/123'

    def test_other_link_is_invalid(self):
        assert BookLoader.try_get_book_link('/author/123') is None


class TestBookParser:
    def test_parses_full_book_row(self, app_context):
        loader = BookLoader(app_context)
        node = html.fromstring(BOOK_ROW)
        book = loader.book_parser(node, '2024-01-01', 'read')

        assert book is not None
        assert book.name == 'Test Book'
        assert book.author == 'Author One, Author Two'
        assert book.rating == '5'
        assert book.date == '2024-01-01'
        assert '/book/123456-test-book' in book.link

    def test_no_rating_for_non_read_status(self, app_context):
        loader = BookLoader(app_context)
        node = html.fromstring(BOOK_ROW)
        book = loader.book_parser(node, None, 'wish')

        assert book is not None
        assert book.rating == ''

    def test_missing_book_data_returns_none(self, app_context):
        loader = BookLoader(app_context)
        node = html.fromstring('<div><span>nothing here</span></div>')
        book = loader.book_parser(node, None, 'read')

        assert book is None

    def test_invalid_link_returns_none(self, app_context):
        loader = BookLoader(app_context)
        bad_row = BOOK_ROW.replace('/book/123456-test-book', '/author/123456')
        node = html.fromstring(bad_row)
        book = loader.book_parser(node, None, 'read')

        assert book is None


class TestGetBooks:
    def test_get_books_parses_all_rows(self, app_context):
        app_context.page_count = 1
        loader = BookLoader(app_context)

        with patch('Modules.BookLoader.download_page', return_value=BOOKLIST_PAGE):
            books = loader.get_books('read')

        assert len(books) == 2
        assert all(b.date == '2024-01-01' for b in books)

    def test_get_books_stops_on_empty_page(self, app_context):
        app_context.page_count = math.inf
        loader = BookLoader(app_context)

        with patch('Modules.BookLoader.download_page', return_value=EMPTY_PAGE):
            books = loader.get_books('read')

        assert books == []

    def test_get_books_stops_on_redirect_page(self, app_context):
        app_context.page_count = math.inf
        loader = BookLoader(app_context)

        with patch('Modules.BookLoader.download_page', return_value=REDIRECT_PAGE):
            books = loader.get_books('read')

        assert books == []

    def test_get_books_respects_page_count_limit(self, app_context):
        app_context.page_count = 2
        loader = BookLoader(app_context)

        with patch('Modules.BookLoader.download_page', return_value=BOOKLIST_PAGE) as mock_download:
            loader.get_books('read')

        assert mock_download.call_count == 2

    def test_get_books_continues_after_download_error(self, app_context):
        app_context.page_count = 2
        loader = BookLoader(app_context)

        with patch(
            'Modules.BookLoader.download_page',
            side_effect=[Exception('boom'), EMPTY_PAGE],
        ) as mock_download:
            books = loader.get_books('read')

        assert books == []
        assert mock_download.call_count == 2
