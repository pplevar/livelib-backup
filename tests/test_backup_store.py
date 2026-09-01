"""
Unit tests for Helpers/backup_store.py
"""
import pandas as pd
import pytest

from Helpers.backup_store import BackupStore, BOOKS_ADAPTER, QUOTES_ADAPTER, detect_format
from Helpers.book import Book
from Helpers.quote import Quote


class TestDetectFormat:
    def test_csv_extension(self):
        assert detect_format('backup.csv') == 'csv'

    def test_xlsx_extension(self):
        assert detect_format('backup.xlsx') == 'excel'

    def test_xls_extension(self):
        assert detect_format('backup.xls') == 'excel'

    def test_no_extension_defaults_to_csv(self):
        assert detect_format('backup') == 'csv'

    def test_case_insensitive(self):
        assert detect_format('backup.XLSX') == 'excel'


class TestBackupStoreBooks:
    def test_new_file_gets_all_books(self, temp_csv_file, sample_books):
        import os
        os.remove(temp_csv_file)

        store = BackupStore(BOOKS_ADAPTER)
        total = store.save(sample_books, temp_csv_file)

        assert total == len(sample_books)
        df = pd.read_csv(temp_csv_file, sep='\t')
        assert set(df['Link']) == {b.link for b in sample_books}

    def test_updating_existing_book_updates_status_in_place(self, temp_csv_file):
        import os
        os.remove(temp_csv_file)

        book = Book(link='https://www.livelib.ru/book/1', status='reading', name='A Book')
        store = BackupStore(BOOKS_ADAPTER)
        store.save([book], temp_csv_file)

        book.status = 'read'
        total = store.save([book], temp_csv_file)

        df = pd.read_csv(temp_csv_file, sep='\t')
        assert total == 1
        assert len(df) == 1
        assert df.iloc[0]['Status'] == 'read'

    def test_rewrite_all_clears_previous_rows(self, temp_csv_file):
        import os
        os.remove(temp_csv_file)

        old_book = Book(link='https://www.livelib.ru/book/1', status='read', name='Old')
        new_book = Book(link='https://www.livelib.ru/book/2', status='read', name='New')

        store = BackupStore(BOOKS_ADAPTER)
        store.save([old_book], temp_csv_file)
        store.save([new_book], temp_csv_file, rewrite_all=True)

        df = pd.read_csv(temp_csv_file, sep='\t')
        assert list(df['Link']) == [new_book.link]


class TestBackupStoreQuotes:
    def test_updating_existing_quote_replaces_text(self, temp_csv_file, sample_quote):
        import os
        os.remove(temp_csv_file)

        store = BackupStore(QUOTES_ADAPTER)
        store.save([sample_quote], temp_csv_file)

        sample_quote.text = 'Updated text'
        store.save([sample_quote], temp_csv_file)

        df = pd.read_csv(temp_csv_file, sep='\t')
        assert len(df) == 1
        assert df.iloc[0]['Quote text'] == 'Updated text'


class TestBackupStoreExcel:
    def test_saves_and_reloads_excel_format(self, temp_excel_file, sample_quote):
        store = BackupStore(QUOTES_ADAPTER)
        store.save([sample_quote], temp_excel_file)

        df = pd.read_excel(temp_excel_file)
        assert len(df) == 1
        assert df.iloc[0]['Quote link'] == sample_quote.link

        sample_quote.text = 'Excel updated text'
        store.save([sample_quote], temp_excel_file)

        df = pd.read_excel(temp_excel_file)
        assert len(df) == 1
        assert df.iloc[0]['Quote text'] == 'Excel updated text'
