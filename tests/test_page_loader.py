"""
Tests for Helpers/page_loader.py
"""
from unittest.mock import Mock, patch

import pytest

from Helpers.page_loader import download_page


class TestDownloadPageRequests:
    def test_uses_requests_when_no_driver(self):
        mock_response = Mock()
        mock_response.content = b'<html>ok</html>'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch('Helpers.page_loader.requests.get', return_value=mock_response) as mock_get:
            result = download_page('https://example.com/page')

        mock_get.assert_called_once_with('https://example.com/page')
        assert result == b'<html>ok</html>'

    def test_raises_on_requests_error(self):
        with patch('Helpers.page_loader.requests.get', side_effect=Exception('network error')):
            with pytest.raises(Exception, match='network error'):
                download_page('https://example.com/page')


class TestDownloadPageSelenium:
    def test_uses_selenium_when_driver_given(self, mock_selenium_driver):
        with patch('Helpers.page_loader.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = True
            result = download_page('https://example.com/page', driver=mock_selenium_driver)

        mock_selenium_driver.get.assert_called_once_with('https://example.com/page')
        assert result == mock_selenium_driver.page_source

    def test_returns_none_when_element_never_appears(self, mock_selenium_driver):
        with patch('Helpers.page_loader.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.side_effect = Exception('timed out')
            result = download_page('https://example.com/page', driver=mock_selenium_driver)

        assert result is None
