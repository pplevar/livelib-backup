"""
Tests for export.main()
"""
import argparse
from unittest.mock import Mock, patch

import pytest
import requests

import export


def make_args(**overrides):
    defaults = dict(
        user='testuser',
        min_delay=0.5,
        max_delay=0.5,
        books_backup=None,
        quotes_backup=None,
        read_count=1,
        quote_count=1,
        rewrite_all=False,
        skip=None,
        driver=None,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


@pytest.fixture(autouse=True)
def no_real_sleep():
    with patch('time.sleep'):
        yield


class TestMainConfigErrors:
    def test_invalid_config_returns_1(self):
        with patch('export.get_arguments', return_value=make_args(user='', min_delay=0.5, max_delay=0.5)):
            assert export.main() == 1


class TestMainProfileCheckFailure:
    def test_unreachable_profile_returns_1(self):
        with patch('export.get_arguments', return_value=make_args()), \
             patch('requests.get', side_effect=requests.exceptions.RequestException('boom')):
            assert export.main() == 1


class TestMainHappyPath:
    def test_default_driver_none_does_not_fail_config(self):
        """Regression: CLI default of --driver=None must not be rejected by BackupConfig."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        with patch('export.get_arguments', return_value=make_args(driver=None)), \
             patch('requests.get', return_value=mock_response), \
             patch('export.BookLoader') as MockBookLoader, \
             patch('export.QuoteLoader') as MockQuoteLoader, \
             patch('export.read_books_from_csv', return_value=[]):
            MockBookLoader.return_value.get_books.return_value = []
            MockQuoteLoader.return_value.get_quotes.return_value = []
            result = export.main()

        assert result == 0

    def test_processes_books_and_quotes(self):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        mock_book_loader = Mock()
        mock_book_loader.get_books.return_value = []

        mock_quote_loader = Mock()
        mock_quote_loader.get_quotes.return_value = []

        with patch('export.get_arguments', return_value=make_args()), \
             patch('requests.get', return_value=mock_response), \
             patch('export.BookLoader', return_value=mock_book_loader) as MockBookLoader, \
             patch('export.QuoteLoader', return_value=mock_quote_loader) as MockQuoteLoader, \
             patch('export.read_books_from_csv', return_value=[]), \
             patch('export.save_books') as mock_save_books:
            result = export.main()

        assert result == 0
        assert mock_book_loader.get_books.call_count == 3  # read, reading, wish
        mock_quote_loader.get_quotes.assert_called_once()
        mock_save_books.assert_not_called()  # no books were found

    def test_skip_books(self):
        mock_quote_loader = Mock()
        mock_quote_loader.get_quotes.return_value = []
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        with patch('export.get_arguments', return_value=make_args(skip='books')), \
             patch('requests.get', return_value=mock_response), \
             patch('export.BookLoader') as MockBookLoader, \
             patch('export.QuoteLoader', return_value=mock_quote_loader):
            result = export.main()

        assert result == 0
        MockBookLoader.assert_not_called()

    def test_skip_quotes(self):
        mock_book_loader = Mock()
        mock_book_loader.get_books.return_value = []
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        with patch('export.get_arguments', return_value=make_args(skip='quotes')), \
             patch('requests.get', return_value=mock_response), \
             patch('export.BookLoader', return_value=mock_book_loader), \
             patch('export.QuoteLoader') as MockQuoteLoader, \
             patch('export.read_books_from_csv', return_value=[]):
            result = export.main()

        assert result == 0
        MockQuoteLoader.assert_not_called()

    def test_selenium_driver_init_failure_returns_1(self):
        with patch('export.get_arguments', return_value=make_args(driver='selenium')), \
             patch('selenium.webdriver.Chrome', side_effect=Exception('no chrome')):
            result = export.main()

        assert result == 1

    def test_unexpected_error_during_backup_returns_1(self):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        with patch('export.get_arguments', return_value=make_args()), \
             patch('requests.get', return_value=mock_response), \
             patch('export.BookLoader', side_effect=RuntimeError('kaboom')):
            result = export.main()

        assert result == 1
