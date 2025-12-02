"""Tests for file handler strategy pattern."""

import pytest
import pandas as pd
from pathlib import Path
from Helpers.file_handlers import (
    FileHandler,
    CSVHandler,
    ExcelHandler,
    FileHandlerFactory
)
from Helpers.constants import CSV_SEPARATOR


class TestCSVHandler:
    """Test CSV file handler."""

    def test_read_existing_csv(self, tmp_path):
        """Test reading an existing CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(f"Name{CSV_SEPARATOR}Author\nBook1{CSV_SEPARATOR}Author1\n")

        handler = CSVHandler()
        df = handler.read(str(csv_file))

        assert len(df) == 1
        assert df.iloc[0]['Name'] == 'Book1'
        assert df.iloc[0]['Author'] == 'Author1'

    def test_read_nonexistent_csv_returns_empty_dataframe(self, tmp_path):
        """Test reading nonexistent CSV returns empty DataFrame."""
        handler = CSVHandler()
        df = handler.read(str(tmp_path / "nonexistent.csv"))

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_write_csv(self, tmp_path):
        """Test writing CSV file."""
        csv_file = tmp_path / "output.csv"
        handler = CSVHandler()

        df = pd.DataFrame({
            'Name': ['Book1', 'Book2'],
            'Author': ['Author1', 'Author2']
        })
        handler.write(df, str(csv_file))

        assert csv_file.exists()
        content = csv_file.read_text()
        assert CSV_SEPARATOR in content
        assert 'Book1' in content
        assert 'Author1' in content

    def test_format_text_removes_tabs(self):
        """Test that format_text removes tabs."""
        handler = CSVHandler()
        text = "Text\twith\ttabs"
        result = handler.format_text(text)

        assert '\t' not in result
        assert result == "Text with tabs"

    def test_format_text_removes_newlines(self):
        """Test that format_text removes newlines."""
        handler = CSVHandler()
        text = "Text\nwith\nnewlines"
        result = handler.format_text(text)

        assert '\n' not in result
        assert result == "Text with newlines"

    def test_format_text_removes_both_tabs_and_newlines(self):
        """Test that format_text removes both tabs and newlines."""
        handler = CSVHandler()
        text = "Text\twith\ttabs\nand\nnewlines"
        result = handler.format_text(text)

        assert '\t' not in result
        assert '\n' not in result
        assert result == "Text with tabs and newlines"

    def test_write_preserves_data_integrity(self, tmp_path):
        """Test that write and read preserve data integrity."""
        csv_file = tmp_path / "test.csv"
        handler = CSVHandler()

        original_df = pd.DataFrame({
            'Name': ['Book1', 'Book2', 'Book3'],
            'Author': ['Author1', 'Author2', 'Author3'],
            'Rating': ['5', '4', '3']
        })

        handler.write(original_df, str(csv_file))
        read_df = handler.read(str(csv_file))

        # Compare values, not dtypes (CSV doesn't preserve types perfectly)
        assert len(original_df) == len(read_df)
        assert list(original_df.columns) == list(read_df.columns)
        for col in original_df.columns:
            assert list(original_df[col].astype(str)) == list(read_df[col].astype(str))


class TestExcelHandler:
    """Test Excel file handler."""

    def test_read_existing_excel(self, tmp_path):
        """Test reading an existing Excel file."""
        excel_file = tmp_path / "test.xlsx"

        df = pd.DataFrame({
            'Name': ['Book1'],
            'Author': ['Author1']
        })
        df.to_excel(excel_file, index=False)

        handler = ExcelHandler()
        read_df = handler.read(str(excel_file))

        assert len(read_df) == 1
        assert read_df.iloc[0]['Name'] == 'Book1'
        assert read_df.iloc[0]['Author'] == 'Author1'

    def test_read_nonexistent_excel_returns_empty_dataframe(self, tmp_path):
        """Test reading nonexistent Excel returns empty DataFrame."""
        handler = ExcelHandler()
        df = handler.read(str(tmp_path / "nonexistent.xlsx"))

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_write_excel(self, tmp_path):
        """Test writing Excel file."""
        excel_file = tmp_path / "output.xlsx"
        handler = ExcelHandler()

        df = pd.DataFrame({
            'Name': ['Book1', 'Book2'],
            'Author': ['Author1', 'Author2']
        })
        handler.write(df, str(excel_file))

        assert excel_file.exists()
        assert excel_file.suffix == '.xlsx'

    def test_format_text_preserves_formatting(self):
        """Test that format_text preserves all formatting for Excel."""
        handler = ExcelHandler()
        text = "Text\twith\ttabs\nand\nnewlines"
        result = handler.format_text(text)

        assert result == text

    def test_format_text_preserves_special_chars(self):
        """Test that format_text preserves special characters."""
        handler = ExcelHandler()
        text = "Special chars: @#$%^&*()"
        result = handler.format_text(text)

        assert result == text

    def test_write_preserves_data_integrity(self, tmp_path):
        """Test that write and read preserve data integrity."""
        excel_file = tmp_path / "test.xlsx"
        handler = ExcelHandler()

        original_df = pd.DataFrame({
            'Name': ['Book1', 'Book2', 'Book3'],
            'Author': ['Author1', 'Author2', 'Author3'],
            'Rating': ['5', '4', '3']
        })

        handler.write(original_df, str(excel_file))
        read_df = handler.read(str(excel_file))

        # Compare values, not dtypes (Excel may infer types)
        assert len(original_df) == len(read_df)
        assert list(original_df.columns) == list(read_df.columns)
        for col in original_df.columns:
            assert list(original_df[col].astype(str)) == list(read_df[col].astype(str))

    def test_write_preserves_multiline_text(self, tmp_path):
        """Test that Excel preserves multiline text."""
        excel_file = tmp_path / "test.xlsx"
        handler = ExcelHandler()

        original_df = pd.DataFrame({
            'Text': ['Line1\nLine2\nLine3']
        })

        handler.write(original_df, str(excel_file))
        read_df = handler.read(str(excel_file))

        assert '\n' in read_df.iloc[0]['Text']


class TestFileHandlerFactory:
    """Test file handler factory."""

    def test_get_csv_handler(self):
        """Test getting CSV handler."""
        handler = FileHandlerFactory.get_handler("file.csv")
        assert isinstance(handler, CSVHandler)

    def test_get_excel_handler(self):
        """Test getting Excel handler."""
        handler = FileHandlerFactory.get_handler("file.xlsx")
        assert isinstance(handler, ExcelHandler)

    def test_get_handler_with_path(self):
        """Test getting handler with full path."""
        handler = FileHandlerFactory.get_handler("/path/to/file.csv")
        assert isinstance(handler, CSVHandler)

    def test_unsupported_extension_raises_error(self):
        """Test that unsupported extension raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported file format: txt"):
            FileHandlerFactory.get_handler("file.txt")

    def test_no_extension_raises_error(self):
        """Test that file with no extension raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            FileHandlerFactory.get_handler("file")

    def test_case_sensitive_extension(self):
        """Test that extension matching is case-sensitive."""
        with pytest.raises(ValueError, match="Unsupported file format: CSV"):
            FileHandlerFactory.get_handler("file.CSV")

    def test_supports_csv_extension(self):
        """Test that CSV extension is supported."""
        assert FileHandlerFactory.supports_extension("csv")
        assert FileHandlerFactory.supports_extension(".csv")

    def test_supports_xlsx_extension(self):
        """Test that XLSX extension is supported."""
        assert FileHandlerFactory.supports_extension("xlsx")
        assert FileHandlerFactory.supports_extension(".xlsx")

    def test_does_not_support_txt_extension(self):
        """Test that TXT extension is not supported."""
        assert not FileHandlerFactory.supports_extension("txt")
        assert not FileHandlerFactory.supports_extension(".txt")

    def test_supports_extension_strips_leading_dot(self):
        """Test that leading dot is handled correctly."""
        assert FileHandlerFactory.supports_extension(".csv")
        assert FileHandlerFactory.supports_extension("csv")
