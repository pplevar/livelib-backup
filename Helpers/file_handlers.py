"""File format handlers using Strategy pattern for CSV and Excel operations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
import pandas as pd
from .constants import CSV_SEPARATOR


class FileHandler(ABC):
    """Abstract base class for file format handlers."""

    @abstractmethod
    def read(self, filepath: str) -> pd.DataFrame:
        """
        Read data from file.

        Args:
            filepath: Path to file

        Returns:
            DataFrame containing file data
        """
        pass

    @abstractmethod
    def write(self, df: pd.DataFrame, filepath: str) -> None:
        """
        Write data to file.

        Args:
            df: DataFrame to write
            filepath: Path to output file
        """
        pass

    @abstractmethod
    def format_text(self, text: str) -> str:
        """
        Format text for this file type.

        Args:
            text: Text to format

        Returns:
            Formatted text suitable for file type
        """
        pass


class CSVHandler(FileHandler):
    """Handler for CSV files with tab separator."""

    def read(self, filepath: str) -> pd.DataFrame:
        """
        Read CSV file with tab separator.

        Args:
            filepath: Path to CSV file

        Returns:
            DataFrame with file contents, or empty DataFrame if file doesn't exist
        """
        if not Path(filepath).exists():
            return pd.DataFrame()
        return pd.read_csv(filepath, sep=CSV_SEPARATOR)

    def write(self, df: pd.DataFrame, filepath: str) -> None:
        """
        Write DataFrame to CSV file with tab separator.

        Args:
            df: DataFrame to write
            filepath: Output file path
        """
        df.to_csv(filepath, sep=CSV_SEPARATOR, index=False)

    def format_text(self, text: str) -> str:
        """
        Format text for CSV by removing tabs and newlines.

        Args:
            text: Text to format

        Returns:
            Text with tabs and newlines replaced by spaces
        """
        return text.replace('\t', ' ').replace('\n', ' ')


class ExcelHandler(FileHandler):
    """Handler for Excel (.xlsx) files."""

    def read(self, filepath: str) -> pd.DataFrame:
        """
        Read Excel file.

        Args:
            filepath: Path to Excel file

        Returns:
            DataFrame with file contents, or empty DataFrame if file doesn't exist
        """
        if not Path(filepath).exists():
            return pd.DataFrame()
        return pd.read_excel(filepath)

    def write(self, df: pd.DataFrame, filepath: str) -> None:
        """
        Write DataFrame to Excel file.

        Args:
            df: DataFrame to write
            filepath: Output file path
        """
        df.to_excel(filepath, index=False)

    def format_text(self, text: str) -> str:
        """
        Format text for Excel (preserves formatting).

        Args:
            text: Text to format

        Returns:
            Original text (Excel preserves formatting)
        """
        return text


class FileHandlerFactory:
    """Factory for creating appropriate file handlers based on file extension."""

    _handlers = {
        'csv': CSVHandler,
        'xlsx': ExcelHandler,
    }

    @classmethod
    def get_handler(cls, filepath: str) -> FileHandler:
        """
        Get appropriate file handler for given file path.

        Args:
            filepath: Path to file (extension used to determine handler)

        Returns:
            FileHandler instance for the file type

        Raises:
            ValueError: If file extension is not supported
        """
        ext = Path(filepath).suffix[1:]  # Remove leading dot
        handler_class = cls._handlers.get(ext)
        if not handler_class:
            raise ValueError(f'Unsupported file format: {ext}. Supported: {", ".join(cls._handlers.keys())}')
        return handler_class()

    @classmethod
    def supports_extension(cls, extension: str) -> bool:
        """
        Check if extension is supported.

        Args:
            extension: File extension (with or without dot)

        Returns:
            True if extension is supported
        """
        ext = extension.lstrip('.')
        return ext in cls._handlers
