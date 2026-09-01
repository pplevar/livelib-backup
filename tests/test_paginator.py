"""
Tests for Modules/Paginator.py
"""
from unittest.mock import patch

import pytest

from Modules.Paginator import Paginator


LISTING_PAGE = "<html><body><div id='items'><div>item</div></div></body></html>"

EMPTY_PAGE = """
<html><body><div class="with-pad"><p>Страница пуста</p></div></body></html>
"""

REDIRECT_PAGE = """
<html><body><div class="page-404"><h1>404</h1></div></body></html>
"""


@pytest.fixture(autouse=True)
def no_real_delay():
    with patch('time.sleep'):
        yield


class TestPaginatorPages:
    def test_yields_pages_until_empty_page(self, backup_config):
        paginator = Paginator(backup_config)

        with patch(
            'Helpers.page_loader.download_page',
            side_effect=[LISTING_PAGE, LISTING_PAGE, EMPTY_PAGE],
        ) as mock_download:
            pages = list(paginator.pages('https://example.com/href'))

        assert len(pages) == 2
        assert mock_download.call_count == 3

    def test_stops_on_redirect_page(self, backup_config):
        paginator = Paginator(backup_config)

        with patch('Helpers.page_loader.download_page', return_value=REDIRECT_PAGE):
            pages = list(paginator.pages('https://example.com/href'))

        assert pages == []

    def test_respects_max_pages_limit(self, backup_config):
        paginator = Paginator(backup_config)

        with patch(
            'Helpers.page_loader.download_page', return_value=LISTING_PAGE
        ) as mock_download:
            pages = list(paginator.pages('https://example.com/href', max_pages=2))

        assert len(pages) == 2
        assert mock_download.call_count == 2

    def test_unlimited_when_max_pages_none(self, backup_config):
        paginator = Paginator(backup_config)

        with patch(
            'Helpers.page_loader.download_page',
            side_effect=[LISTING_PAGE, LISTING_PAGE, LISTING_PAGE, EMPTY_PAGE],
        ) as mock_download:
            pages = list(paginator.pages('https://example.com/href'))

        assert len(pages) == 3
        assert mock_download.call_count == 4

    def test_skips_page_on_download_failure(self, backup_config):
        paginator = Paginator(backup_config)

        with patch(
            'Helpers.page_loader.download_page',
            side_effect=[None, EMPTY_PAGE],
        ) as mock_download:
            pages = list(paginator.pages('https://example.com/href', max_pages=2))

        assert pages == []
        assert mock_download.call_count == 2

    def test_continues_after_download_error(self, backup_config):
        paginator = Paginator(backup_config)

        with patch(
            'Helpers.page_loader.download_page',
            side_effect=[Exception('boom'), EMPTY_PAGE],
        ) as mock_download:
            pages = list(paginator.pages('https://example.com/href', max_pages=2))

        assert pages == []
        assert mock_download.call_count == 2

    def test_requests_expected_page_urls(self, backup_config):
        paginator = Paginator(backup_config)

        with patch(
            'Helpers.page_loader.download_page',
            side_effect=[LISTING_PAGE, EMPTY_PAGE],
        ) as mock_download:
            list(paginator.pages('https://example.com/href'))

        called_urls = [call.args[0] for call in mock_download.call_args_list]
        assert called_urls == [
            'https://example.com/href/~1',
            'https://example.com/href/~2',
        ]
