"""
Tests for Modules/BookLoader.py
"""
from unittest.mock import patch

import pytest
from lxml import html

from Helpers.book import Book
from Modules.BookLoader import BookLoader


BOOK_ROW = """
<div>
    <div>
        <div>
            <div class="brow-data">
                <div>
                    <a href="https://www.livelib.ru/book/123456-test-book" class="brow-book-name">Test Book</a>
                    <a href="https://www.livelib.ru/author/1-author" class="brow-book-author">Author One</a>
                    <a href="https://www.livelib.ru/author/2-author" class="brow-book-author">Author Two</a>
                    <div class="brow-ratings"><span><span><span>5</span></span></span></div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

BOOK_ROW_2 = BOOK_ROW.replace('123456', '999999')

BOOKLIST_PAGE = """
<html><body>
<div id="booklist">
    <div><h2>Январь 2024 г.</h2></div>
    %s
    %s
</div>
</body></html>
""" % (BOOK_ROW, BOOK_ROW_2)

EMPTY_PAGE = """
<html><body><div class="with-pad"><p>Страница пуста</p></div></body></html>
"""

REDIRECT_PAGE = """
<html><body><div class="page-404"><h1>404</h1></div></body></html>
"""


@pytest.fixture(autouse=True)
def no_real_delay():
    with patch('time.sleep'):
        yield


class TestValidateBookLink:
    def test_book_link_is_valid(self):
        assert BookLoader._validate_book_link('https://www.livelib.ru/book/123') == 'https://www.livelib.ru/book/123'

    def test_work_link_is_valid(self):
        assert BookLoader._validate_book_link('https://www.livelib.ru/work/123') == 'https://www.livelib.ru/work/123'

    def test_other_link_is_invalid(self):
        assert BookLoader._validate_book_link('https://www.livelib.ru/author/123') is None

    def test_none_link_is_invalid(self):
        assert BookLoader._validate_book_link(None) is None


class TestParseBook:
    def test_parses_full_book_row(self, backup_config):
        loader = BookLoader(backup_config)
        node = html.fromstring(BOOK_ROW)
        book = loader._parse_book(node, '2024-01-01', 'read')

        assert book is not None
        assert book.name == 'Test Book'
        assert book.author == 'Author One, Author Two'
        assert book.rating == '5'
        assert book.date == '2024-01-01'
        assert book.link == 'https://www.livelib.ru/book/123456-test-book'

    def test_no_rating_for_non_read_status(self, backup_config):
        loader = BookLoader(backup_config)
        node = html.fromstring(BOOK_ROW)
        book = loader._parse_book(node, None, 'wish')

        assert book is not None
        assert book.rating is None

    def test_missing_book_data_returns_none(self, backup_config):
        loader = BookLoader(backup_config)
        node = html.fromstring('<div><span>nothing here</span></div>')
        book = loader._parse_book(node, None, 'read')

        assert book is None

    def test_invalid_link_returns_none(self, backup_config):
        loader = BookLoader(backup_config)
        bad_row = BOOK_ROW.replace(
            'https://www.livelib.ru/book/123456-test-book',
            'https://www.livelib.ru/author/123456',
        )
        node = html.fromstring(bad_row)
        book = loader._parse_book(node, None, 'read')

        assert book is None


class TestGetBooks:
    def test_rejects_invalid_status(self, backup_config):
        loader = BookLoader(backup_config)
        with pytest.raises(ValueError, match='Invalid status'):
            loader.get_books('finished')

    def test_get_books_parses_all_rows(self, backup_config):
        loader = BookLoader(backup_config)

        with patch('Modules.BookLoader.download_page', return_value=BOOKLIST_PAGE):
            books = loader.get_books('read', 1)

        assert len(books) == 2
        assert all(b.date == '2024-01-01' for b in books)

    def test_get_books_stops_on_empty_page(self, backup_config):
        loader = BookLoader(backup_config)

        with patch('Modules.BookLoader.download_page', return_value=EMPTY_PAGE):
            books = loader.get_books('read')

        assert books == []

    def test_get_books_stops_on_redirect_page(self, backup_config):
        loader = BookLoader(backup_config)

        with patch('Modules.BookLoader.download_page', return_value=REDIRECT_PAGE):
            books = loader.get_books('read')

        assert books == []

    def test_get_books_respects_read_count_limit(self, backup_config):
        loader = BookLoader(backup_config)

        with patch('Modules.BookLoader.download_page', return_value=BOOKLIST_PAGE) as mock_download:
            loader.get_books('read', 2)

        assert mock_download.call_count == 2

    def test_get_books_ignores_read_count_for_other_statuses(self, backup_config):
        loader = BookLoader(backup_config)

        with patch(
            'Modules.BookLoader.download_page',
            side_effect=[BOOKLIST_PAGE, EMPTY_PAGE],
        ) as mock_download:
            loader.get_books('wish', 1)

        assert mock_download.call_count == 2

    def test_get_books_skips_page_on_download_failure(self, backup_config):
        loader = BookLoader(backup_config)

        with patch(
            'Modules.BookLoader.download_page',
            side_effect=[None, EMPTY_PAGE],
        ) as mock_download:
            books = loader.get_books('read', 2)

        assert books == []
        assert mock_download.call_count == 2

    def test_get_books_continues_after_download_error(self, backup_config):
        loader = BookLoader(backup_config)

        with patch(
            'Modules.BookLoader.download_page',
            side_effect=[Exception('boom'), EMPTY_PAGE],
        ) as mock_download:
            books = loader.get_books('read', 2)

        assert books == []
        assert mock_download.call_count == 2


class TestSaveBooks:
    def test_save_new_books_to_csv(self, backup_config, temp_csv_file, sample_book):
        import os
        os.remove(temp_csv_file)
        backup_config.books_file = temp_csv_file
        loader = BookLoader(backup_config)

        loader.save_books([sample_book])

        with open(temp_csv_file, encoding='utf-8') as f:
            content = f.read()
        assert sample_book.link in content

    def test_updating_existing_book_replaces_status(self, backup_config, temp_csv_file, sample_book):
        import os
        os.remove(temp_csv_file)
        backup_config.books_file = temp_csv_file
        loader = BookLoader(backup_config)

        loader.save_books([sample_book])
        sample_book.status = 'wish'
        loader.save_books([sample_book])

        import pandas as pd
        df = pd.read_csv(temp_csv_file, sep='\t')
        assert len(df) == 1
        assert df.iloc[0]['Status'] == 'wish'

    def test_rewrite_all_clears_existing_file(self, backup_config, temp_csv_file):
        old_book = Book(link='https://www.livelib.ru/book/1', status='read', name='Old')
        new_book = Book(link='https://www.livelib.ru/book/2', status='read', name='New')
        backup_config.books_file = temp_csv_file

        loader = BookLoader(backup_config)
        loader.save_books([old_book])

        backup_config.rewrite_all = True
        loader.save_books([new_book])

        import pandas as pd
        df = pd.read_csv(temp_csv_file, sep='\t')
        assert list(df['Link']) == [new_book.link]
