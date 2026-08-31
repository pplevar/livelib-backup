"""
Tests for Helpers/config.py
"""
import pytest

from Helpers.config import BackupConfig


class TestBackupConfigValidation:
    def test_valid_config(self):
        config = BackupConfig(username='testuser')
        assert config.username == 'testuser'
        assert config.validate() == []

    def test_rejects_empty_username(self):
        with pytest.raises(ValueError, match='Username is required'):
            BackupConfig(username='')

    def test_rejects_blank_username(self):
        with pytest.raises(ValueError, match='Username is required'):
            BackupConfig(username='   ')

    def test_rejects_min_delay_too_low(self):
        with pytest.raises(ValueError, match='min_delay too low'):
            BackupConfig(username='testuser', min_delay=0.1)

    def test_rejects_max_delay_below_min_delay(self):
        with pytest.raises(ValueError, match='max_delay must be >= min_delay'):
            BackupConfig(username='testuser', min_delay=5, max_delay=1)

    def test_rejects_invalid_driver_type(self):
        with pytest.raises(ValueError, match='driver_type must be'):
            BackupConfig(username='testuser', driver_type='silenium')

    def test_accepts_selenium_driver_type(self):
        config = BackupConfig(username='testuser', driver_type='selenium')
        assert config.driver_type == 'selenium'

    def test_rejects_read_count_below_one(self):
        with pytest.raises(ValueError, match='read_count must be >= 1'):
            BackupConfig(username='testuser', read_count=0)

    def test_rejects_quote_count_below_one(self):
        with pytest.raises(ValueError, match='quote_count must be >= 1'):
            BackupConfig(username='testuser', quote_count=0)

    def test_reports_multiple_errors(self):
        config = BackupConfig.__new__(BackupConfig)
        config.username = ''
        config.min_delay = 0.1
        config.max_delay = 0.05
        config.driver_type = 'bogus'
        config.read_count = 0
        config.quote_count = 0
        errors = config.validate()
        assert len(errors) == 6


class TestBackupConfigPaths:
    def test_default_books_file_path(self):
        config = BackupConfig(username='alice')
        assert config.get_books_file_path() == 'backup_alice_book.csv'

    def test_custom_books_file_path(self):
        config = BackupConfig(username='alice', books_file='my_books.csv')
        assert config.get_books_file_path() == 'my_books.csv'

    def test_default_quotes_file_path(self):
        config = BackupConfig(username='alice')
        assert config.get_quotes_file_path() == 'backup_alice_quote.csv'

    def test_custom_quotes_file_path(self):
        config = BackupConfig(username='alice', quotes_file='my_quotes.xlsx')
        assert config.get_quotes_file_path() == 'my_quotes.xlsx'

    def test_user_href(self):
        config = BackupConfig(username='alice')
        assert config.get_user_href() == 'https://www.livelib.ru/reader/alice'
