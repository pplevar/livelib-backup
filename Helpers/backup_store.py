"""
Unified backup store.

Owns the two things that used to be duplicated across the books and quotes
save paths: detecting whether a backup file is CSV or Excel, and merging
newly-scraped items into the existing file (updating a matching row in
place, appending anything new). Books and quotes each plug in a small
BackupAdapter describing their columns and how to turn a domain object into
a row.
"""
import logging
import os
from dataclasses import dataclass
from typing import Any, Callable, List

import pandas as pd

logger = logging.getLogger(__name__)

EXCEL_EXTENSIONS = ('xlsx', 'xls')


def detect_format(file_path: str) -> str:
    """Return 'excel' or 'csv' based on a file path's extension."""
    ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
    return 'excel' if ext in EXCEL_EXTENSIONS else 'csv'


@dataclass(frozen=True)
class BackupAdapter:
    """Describes how a domain object maps onto a backup file's rows."""

    columns: List[str]
    key_column: str
    key_of: Callable[[Any], str]
    to_row: Callable[[Any], dict]


BOOKS_ADAPTER = BackupAdapter(
    columns=['Name', 'Author', 'Status', 'My Rating', 'Date', 'Link'],
    key_column='Link',
    key_of=lambda book: book.link,
    to_row=lambda book: {
        'Name': book.name or '',
        'Author': book.author or '',
        'Status': book.status,
        'My Rating': book.rating or '',
        'Date': book.date or '',
        'Link': book.link,
    },
)

QUOTES_ADAPTER = BackupAdapter(
    columns=['Name', 'Author', 'Quote text', 'Book link', 'Quote link'],
    key_column='Quote link',
    key_of=lambda quote: quote.link,
    to_row=lambda quote: {
        'Name': quote.book.name or '',
        'Author': quote.book.author or '',
        'Quote text': quote.text,
        'Book link': quote.book.link,
        'Quote link': quote.link,
    },
)


class BackupStore:
    """Persists a list of domain objects to a single CSV/Excel backup file."""

    def __init__(self, adapter: BackupAdapter):
        self.adapter = adapter

    def save(self, items: List[Any], file_path: str, rewrite_all: bool = False) -> int:
        """
        Merge items into the backup file at file_path and save.

        Existing rows whose key matches an item are updated in place;
        everything else is appended. Returns the total row count after
        saving.
        """
        if rewrite_all and os.path.exists(file_path):
            os.remove(file_path)
            logger.info('Cleared existing backup file: %s', file_path)

        df = self._load(file_path)
        df = self._merge(df, items)
        self._write(df, file_path)
        return len(df)

    def _load(self, file_path: str) -> pd.DataFrame:
        columns = list(self.adapter.columns)
        if not os.path.exists(file_path):
            return pd.DataFrame(columns=columns)

        try:
            if detect_format(file_path) == 'excel':
                df = pd.read_excel(file_path, dtype=str, keep_default_na=False)
            else:
                df = pd.read_csv(file_path, sep='\t', dtype=str, keep_default_na=False)
            logger.info('Loaded %d existing records from %s', len(df), file_path)
            return df
        except Exception as e:
            logger.warning('Could not read existing backup file %s: %s. Starting fresh.', file_path, e)
            return pd.DataFrame(columns=columns)

    def _merge(self, df: pd.DataFrame, items: List[Any]) -> pd.DataFrame:
        key_column = self.adapter.key_column

        for item in items:
            key = self.adapter.key_of(item)
            row = self.adapter.to_row(item)

            existing_idx = df.index[df[key_column] == key] if key_column in df.columns else pd.Index([])
            if len(existing_idx) > 0:
                for column, value in row.items():
                    df.loc[existing_idx[0], column] = value
                logger.debug('Updated existing record: %s', key)
            else:
                new_row = pd.DataFrame([row])
                df = pd.concat([df, new_row], ignore_index=True)
                logger.debug('Added new record: %s', key)

        return df

    def _write(self, df: pd.DataFrame, file_path: str) -> None:
        if detect_format(file_path) == 'excel':
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, sep='\t', index=False)
