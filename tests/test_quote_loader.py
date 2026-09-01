"""
Tests for Modules/QuoteLoader.py
"""
import os
from unittest.mock import patch

import pytest
from lxml import html

from Modules.QuoteLoader import QuoteLoader


QUOTE_ARTICLE = """
<article>
    <div class="lenta-card">
        <blockquote>Some wise words.</blockquote>
        <div class="lenta-card-book__wrapper">
            <a class="lenta-card__book-title" href="https://www.livelib.ru/book/123-test-book">Test Book</a>
            <p class="lenta-card__author-wrap"><a href="https://www.livelib.ru/author/1">Test Author</a></p>
        </div>
        <a href="https://www.livelib.ru/quote/111111">Quote link</a>
        <a href="https://www.livelib.ru/book/123-test-book">Book link</a>
    </div>
</article>
"""

QUOTE_ARTICLE_TRUNCATED = """
<article>
    <div class="lenta-card">
        <blockquote>Truncated text</blockquote>
        <a class="read-more__link" href="https://www.livelib.ru/quote/222222">Читать дальше...</a>
        <div class="lenta-card-book__wrapper">
            <a class="lenta-card__book-title" href="https://www.livelib.ru/book/456-other-book">Other Book</a>
            <p class="lenta-card__author-wrap"><a href="https://www.livelib.ru/author/2">Other Author</a></p>
        </div>
        <a href="https://www.livelib.ru/quote/222222">Quote link</a>
        <a href="https://www.livelib.ru/book/456-other-book">Book link</a>
    </div>
</article>
"""

QUOTE_LIST_PAGE = """
<html><body>
%s
%s
</body></html>
""" % (QUOTE_ARTICLE, QUOTE_ARTICLE_TRUNCATED)

QUOTE_DETAIL_PAGE = """
<html><body>
<article>
    <div id="lenta-card__text-quote-full"><p>The full untruncated quote text.</p></div>
</article>
</body></html>
"""

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


class TestValidateQuoteLink:
    def test_quote_link_is_valid(self):
        assert QuoteLoader._validate_quote_link('https://www.livelib.ru/quote/123') == 'https://www.livelib.ru/quote/123'

    def test_other_link_is_invalid(self):
        assert QuoteLoader._validate_quote_link('https://www.livelib.ru/book/123') is None

    def test_none_link_is_invalid(self):
        assert QuoteLoader._validate_quote_link(None) is None


class TestParseQuote:
    def test_parses_full_quote(self, backup_config):
        loader = QuoteLoader(backup_config)
        node = html.fromstring(QUOTE_ARTICLE)
        quote = loader._parse_quote(node)

        assert quote is not None
        assert quote.text == 'Some wise words.'
        assert quote.book.name == 'Test Book'
        assert quote.book.author == 'Test Author'
        assert quote.link == 'https://www.livelib.ru/quote/111111'

    def test_truncated_quote_marked_not_full(self, backup_config):
        loader = QuoteLoader(backup_config)
        node = html.fromstring(QUOTE_ARTICLE_TRUNCATED)
        quote = loader._parse_quote(node)

        assert quote is not None
        assert quote.text == '!!!NOT_FULL###'

    def test_missing_card_returns_none(self, backup_config):
        loader = QuoteLoader(backup_config)
        node = html.fromstring('<article><span>nothing</span></article>')
        quote = loader._parse_quote(node)

        assert quote is None


class TestExtractQuoteText:
    def test_reads_blockquote(self, backup_config):
        loader = QuoteLoader(backup_config)
        card = html.fromstring('<div><blockquote>Hello world</blockquote></div>')
        assert loader._extract_quote_text(card) == 'Hello world'

    def test_reads_full_text_paragraph(self, backup_config):
        loader = QuoteLoader(backup_config)
        card = html.fromstring(
            '<div><div id="lenta-card__text-quote-full"><p>Full text here</p></div></div>'
        )
        assert loader._extract_quote_text(card) == 'Full text here'

    def test_returns_none_when_nothing_found(self, backup_config):
        loader = QuoteLoader(backup_config)
        card = html.fromstring('<div><span>irrelevant</span></div>')
        assert loader._extract_quote_text(card) is None

    def test_returns_none_for_none_card(self, backup_config):
        loader = QuoteLoader(backup_config)
        assert loader._extract_quote_text(None) is None


class TestFormatQuoteText:
    def test_strips_tabs_and_newlines(self, backup_config):
        loader = QuoteLoader(backup_config)
        assert loader._format_quote_text('a\tb\nc') == 'a b c'

    def test_strips_surrounding_whitespace(self, backup_config):
        loader = QuoteLoader(backup_config)
        assert loader._format_quote_text('  hello  ') == 'hello'

    def test_none_text_returns_none(self, backup_config):
        loader = QuoteLoader(backup_config)
        assert loader._format_quote_text(None) is None

    def test_blank_text_returns_none(self, backup_config):
        loader = QuoteLoader(backup_config)
        assert loader._format_quote_text('   \t\n  ') is None


class TestGetQuotes:
    def test_get_quotes_parses_full_and_fetches_truncated(self, backup_config):
        loader = QuoteLoader(backup_config)

        with patch(
            'Helpers.page_loader.download_page',
            side_effect=[QUOTE_LIST_PAGE, QUOTE_DETAIL_PAGE],
        ):
            quotes = loader.get_quotes(1)

        assert len(quotes) == 2
        full_quote = next(q for q in quotes if '111111' in q.link)
        truncated_quote = next(q for q in quotes if '222222' in q.link)
        assert full_quote.text == 'Some wise words.'
        assert truncated_quote.text == 'The full untruncated quote text.'

    def test_get_quotes_stops_on_empty_page(self, backup_config):
        loader = QuoteLoader(backup_config)

        with patch('Helpers.page_loader.download_page', return_value=EMPTY_PAGE):
            quotes = loader.get_quotes()

        assert quotes == []

    def test_get_quotes_stops_on_redirect_page(self, backup_config):
        loader = QuoteLoader(backup_config)

        with patch('Helpers.page_loader.download_page', return_value=REDIRECT_PAGE):
            quotes = loader.get_quotes()

        assert quotes == []

    def test_get_quotes_keeps_truncated_text_when_detail_fetch_fails(self, backup_config):
        loader = QuoteLoader(backup_config)

        with patch(
            'Helpers.page_loader.download_page',
            side_effect=[QUOTE_LIST_PAGE, None],
        ):
            quotes = loader.get_quotes(1)

        truncated_quote = next(q for q in quotes if '222222' in q.link)
        assert truncated_quote.text == '!!!NOT_FULL###'

    def test_get_quotes_skips_quote_when_detail_fetch_raises(self, backup_config):
        loader = QuoteLoader(backup_config)

        with patch(
            'Helpers.page_loader.download_page',
            side_effect=[QUOTE_LIST_PAGE, Exception('boom')],
        ):
            quotes = loader.get_quotes(1)

        assert len(quotes) == 1
        assert quotes[0].text == 'Some wise words.'


class TestSaveQuotes:
    def test_save_new_quotes_to_csv(self, backup_config, temp_csv_file, sample_quote):
        os.remove(temp_csv_file)
        backup_config.quotes_file = temp_csv_file
        loader = QuoteLoader(backup_config)

        loader.save_quotes([sample_quote])

        with open(temp_csv_file, encoding='utf-8') as f:
            content = f.read()
        assert sample_quote.link in content

    def test_rewrite_all_deletes_existing_file(self, backup_config, temp_csv_file, sample_quote):
        backup_config.quotes_file = temp_csv_file
        backup_config.rewrite_all = True
        loader = QuoteLoader(backup_config)

        loader.save_quotes([sample_quote])

        assert os.path.exists(temp_csv_file)
        with open(temp_csv_file, encoding='utf-8') as f:
            content = f.read()
        assert sample_quote.link in content

    def test_updating_existing_quote_replaces_text(self, backup_config, temp_csv_file, sample_quote):
        os.remove(temp_csv_file)
        backup_config.quotes_file = temp_csv_file
        loader = QuoteLoader(backup_config)

        loader.save_quotes([sample_quote])
        sample_quote.text = 'Updated text'
        loader.save_quotes([sample_quote])

        with open(temp_csv_file, encoding='utf-8') as f:
            content = f.read()
        assert content.count(sample_quote.link) == 1
        assert 'Updated text' in content
