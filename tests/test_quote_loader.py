"""Tests for QuoteLoader module."""

import pytest
from unittest.mock import Mock, MagicMock
from Modules.QuoteLoader import QuoteLoader
from Modules.AppContext import AppContext


class TestQuoteLoaderHelperMethods:
    """Test helper methods of QuoteLoader."""

    @pytest.fixture
    def quote_loader_csv(self, tmp_path):
        """Create QuoteLoader instance with CSV file."""
        ac = AppContext()
        ac.quote_file = str(tmp_path / "quotes.csv")
        return QuoteLoader(ac)

    @pytest.fixture
    def quote_loader_excel(self, tmp_path):
        """Create QuoteLoader instance with Excel file."""
        ac = AppContext()
        ac.quote_file = str(tmp_path / "quotes.xlsx")
        return QuoteLoader(ac)

    def test_try_get_quote_link_valid(self):
        """Test that valid quote link is returned."""
        link = "https://www.livelib.ru/quote/123456"
        result = QuoteLoader.try_get_quote_link(link)
        assert result == link

    def test_try_get_quote_link_with_additional_path(self):
        """Test quote link with additional path segments."""
        link = "https://www.livelib.ru/quote/123456/extra"
        result = QuoteLoader.try_get_quote_link(link)
        assert result == link

    def test_try_get_quote_link_invalid_book_link(self):
        """Test that book link returns None."""
        link = "https://www.livelib.ru/book/123456"
        result = QuoteLoader.try_get_quote_link(link)
        assert result is None

    def test_try_get_quote_link_invalid_author_link(self):
        """Test that author link returns None."""
        link = "https://www.livelib.ru/author/123456"
        result = QuoteLoader.try_get_quote_link(link)
        assert result is None

    def test_try_get_quote_link_empty_string(self):
        """Test that empty string returns None."""
        result = QuoteLoader.try_get_quote_link("")
        assert result is None

    def test_try_get_quote_link_none(self):
        """Test that None input raises TypeError (as it should)."""
        with pytest.raises(TypeError):
            QuoteLoader.try_get_quote_link(None)

    def test_format_quote_text_csv_removes_tabs(self, quote_loader_csv):
        """Test that CSV format removes tabs from quote text."""
        text = "Quote\twith\ttabs"
        result = quote_loader_csv.format_quote_text(text)
        assert '\t' not in result
        assert result == "Quote with tabs"

    def test_format_quote_text_csv_removes_newlines(self, quote_loader_csv):
        """Test that CSV format removes newlines from quote text."""
        text = "Quote\nwith\nnewlines"
        result = quote_loader_csv.format_quote_text(text)
        assert '\n' not in result
        assert result == "Quote with newlines"

    def test_format_quote_text_csv_removes_both(self, quote_loader_csv):
        """Test that CSV format removes both tabs and newlines."""
        text = "Quote\twith\ttabs\nand\nnewlines"
        result = quote_loader_csv.format_quote_text(text)
        assert '\t' not in result
        assert '\n' not in result
        assert result == "Quote with tabs and newlines"

    def test_format_quote_text_csv_handles_none(self, quote_loader_csv):
        """Test that CSV format handles None input."""
        result = quote_loader_csv.format_quote_text(None)
        assert result is None

    def test_format_quote_text_excel_preserves_tabs(self, quote_loader_excel):
        """Test that Excel format preserves tabs."""
        text = "Quote\twith\ttabs"
        result = quote_loader_excel.format_quote_text(text)
        assert result == text

    def test_format_quote_text_excel_preserves_newlines(self, quote_loader_excel):
        """Test that Excel format preserves newlines."""
        text = "Quote\nwith\nnewlines"
        result = quote_loader_excel.format_quote_text(text)
        assert result == text

    def test_format_quote_text_excel_handles_none(self, quote_loader_excel):
        """Test that Excel format handles None input."""
        result = quote_loader_excel.format_quote_text(None)
        assert result is None

    def test_get_quote_text_from_blockquote(self, quote_loader_csv):
        """Test extracting quote text from blockquote element."""
        from lxml import html

        html_content = '<div><blockquote>This is a quote</blockquote></div>'
        element = html.fromstring(html_content)

        result = quote_loader_csv.get_quote_text(element)
        assert result == "This is a quote"

    def test_get_quote_text_handles_tabs_in_csv(self, quote_loader_csv):
        """Test that tabs are removed from quote text in CSV mode."""
        from lxml import html

        html_content = '<div><blockquote>Quote\twith\ttabs</blockquote></div>'
        element = html.fromstring(html_content)

        result = quote_loader_csv.get_quote_text(element)
        assert '\t' not in result
        assert result == "Quote with tabs"

    def test_get_quote_text_preserves_tabs_in_excel(self, quote_loader_excel):
        """Test that tabs are preserved in Excel mode."""
        from lxml import html

        html_content = '<div><blockquote>Quote\twith\ttabs</blockquote></div>'
        element = html.fromstring(html_content)

        result = quote_loader_excel.get_quote_text(element)
        assert result == "Quote\twith\ttabs"
