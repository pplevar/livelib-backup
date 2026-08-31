"""
Tests for Helpers/arguments.py
"""
import argparse
import math
import sys

import pytest

from Helpers.arguments import get_arguments, table_file_type


class TestTableFileType:
    def test_accepts_csv(self):
        assert table_file_type('backup.csv') == 'backup.csv'

    def test_accepts_xlsx(self):
        assert table_file_type('backup.xlsx') == 'backup.xlsx'

    def test_rejects_other_extensions(self):
        with pytest.raises(argparse.ArgumentTypeError):
            table_file_type('backup.txt')

    def test_rejects_no_extension(self):
        with pytest.raises(argparse.ArgumentTypeError):
            table_file_type('backup')


class TestGetArguments:
    def _run(self, monkeypatch, argv):
        monkeypatch.setattr(sys, 'argv', ['export.py'] + argv)
        return get_arguments()

    def test_defaults(self, monkeypatch):
        args = self._run(monkeypatch, ['testuser'])

        assert args.user == 'testuser'
        assert args.min_delay == 60
        assert args.max_delay == 30
        assert args.books_backup is None
        assert args.quotes_backup is None
        assert args.read_count == math.inf
        assert args.quote_count == math.inf
        assert args.rewrite_all is False
        assert args.skip is None
        assert args.driver is None

    def test_requires_user(self, monkeypatch):
        monkeypatch.setattr(sys, 'argv', ['export.py'])
        with pytest.raises(SystemExit):
            get_arguments()

    def test_custom_delays(self, monkeypatch):
        args = self._run(monkeypatch, ['testuser', '--min_delay', '5', '--max_delay', '10'])
        assert args.min_delay == 5
        assert args.max_delay == 10

    def test_custom_backup_paths(self, monkeypatch):
        args = self._run(
            monkeypatch,
            ['testuser', '-b', 'books.csv', '-q', 'quotes.xlsx'],
        )
        assert args.books_backup == 'books.csv'
        assert args.quotes_backup == 'quotes.xlsx'

    def test_invalid_backup_path_exits(self, monkeypatch):
        monkeypatch.setattr(sys, 'argv', ['export.py', 'testuser', '-b', 'books.txt'])
        with pytest.raises(SystemExit):
            get_arguments()

    def test_rewrite_all_flag(self, monkeypatch):
        args = self._run(monkeypatch, ['testuser', '-R'])
        assert args.rewrite_all is True

    def test_skip_and_driver_options(self, monkeypatch):
        args = self._run(monkeypatch, ['testuser', '-s', 'quotes', '-d', 'silenium'])
        assert args.skip == 'quotes'
        assert args.driver == 'silenium'

    def test_read_and_quote_counts(self, monkeypatch):
        args = self._run(monkeypatch, ['testuser', '--read_count', '5', '--quote_count', '10'])
        assert args.read_count == 5
        assert args.quote_count == 10
