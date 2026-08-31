"""
Tests for Helpers/page_loader.py
"""
from unittest.mock import Mock, patch

import pytest
import requests

from Helpers.page_loader import download_page


@pytest.fixture(autouse=True)
def no_real_sleep():
    with patch('time.sleep'):
        yield


class TestDownloadPageRequests:
    def test_uses_requests_when_no_driver(self):
        mock_response = Mock()
        mock_response.content = b'<html>ok</html>'
        mock_response.raise_for_status = Mock()

        with patch('Helpers.page_loader.requests.get', return_value=mock_response) as mock_get:
            result = download_page('https://example.com/page')

        mock_get.assert_called_once_with('https://example.com/page', timeout=30)
        assert result == b'<html>ok</html>'

    def test_retries_on_timeout_then_succeeds(self):
        mock_response = Mock()
        mock_response.content = b'<html>ok</html>'
        mock_response.raise_for_status = Mock()

        with patch(
            'Helpers.page_loader.requests.get',
            side_effect=[requests.exceptions.Timeout('slow'), mock_response],
        ) as mock_get:
            result = download_page('https://example.com/page')

        assert mock_get.call_count == 2
        assert result == b'<html>ok</html>'

    def test_raises_after_max_retries_on_timeout(self):
        with patch(
            'Helpers.page_loader.requests.get',
            side_effect=requests.exceptions.Timeout('slow'),
        ) as mock_get:
            with pytest.raises(requests.exceptions.Timeout):
                download_page('https://example.com/page')

        assert mock_get.call_count == 4  # initial attempt + 3 retries

    def test_raises_after_max_retries_on_request_exception(self):
        with patch(
            'Helpers.page_loader.requests.get',
            side_effect=requests.exceptions.ConnectionError('down'),
        ):
            with pytest.raises(requests.exceptions.ConnectionError):
                download_page('https://example.com/page')

    def test_raises_immediately_on_unexpected_error(self):
        with patch('Helpers.page_loader.requests.get', side_effect=ValueError('boom')) as mock_get:
            with pytest.raises(ValueError):
                download_page('https://example.com/page')

        assert mock_get.call_count == 1


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
