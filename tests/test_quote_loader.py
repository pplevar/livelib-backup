"""
Tests for Modules/QuoteLoader.py
"""
import math
import os

from lxml import html
from unittest.mock import patch

from Modules.QuoteLoader import QuoteLoader


QUOTE_ARTICLE = """
<article>
    <div class="lenta-card">
        <blockquote>Some wise words.</blockquote>
        <div class="lenta-card-book__wrapper">
            <a class="lenta-card__book-title" href="/book/123-test-book">Test Book</a>
            <p class="lenta-card__author-wrap"><a href="/author/1">Test Author</a></p>
        </div>
        <a href="/quote/111111">Quote link</a>
        <a href="/book/123-test-book">Book link</a>
    </div>
</article>
"""

QUOTE_ARTICLE_TRUNCATED = """
<article>
    <div class="lenta-card">
        <blockquote>Truncated text</blockquote>
        <a class="read-more__link" href="/quote/222222">Читать дальше...</a>
        <div class="lenta-card-book__wrapper">
            <a class="lenta-card__book-title" href="/book/456-other-book">Other Book</a>
            <p class="lenta-card__author-wrap"><a href="/author/2">Other Author</a></p>
        </div>
        <a href="/quote/222222">Quote link</a>
        <a href="/book/456-other-book">Book link</a>
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


class TestTryGetQuoteLink:
    def test_quote_link_is_valid(self):
        assert QuoteLoader.try_get_quote_link('/quote/123') == '/quote/123'

    def test_other_link_is_invalid(self):
        assert QuoteLoader.try_get_quote_link('/book/123') is None


class TestQuoteParser:
    def test_parses_full_quote(self, app_context):
        loader = QuoteLoader(app_context)
        node = html.fromstring(QUOTE_ARTICLE)
        quote = loader.quote_parser(node)

        assert quote is not None
        assert quote.text == 'Some wise words.'
        assert quote.book.name == 'Test Book'
        assert quote.book.author == 'Test Author'
        assert '/quote/111111' in quote.link

    def test_truncated_quote_marked_not_full(self, app_context):
        loader = QuoteLoader(app_context)
        node = html.fromstring(QUOTE_ARTICLE_TRUNCATED)
        quote = loader.quote_parser(node)

        assert quote is not None
        assert quote.text == '!!!NOT_FULL###'

    def test_missing_card_returns_none(self, app_context):
        loader = QuoteLoader(app_context)
        node = html.fromstring('<article><span>nothing</span></article>')
        quote = loader.quote_parser(node)

        assert quote is None


class TestGetQuoteText:
    def test_reads_blockquote(self, app_context):
        loader = QuoteLoader(app_context)
        card = html.fromstring('<div><blockquote>Hello world</blockquote></div>')
        assert loader.get_quote_text(card) == 'Hello world'

    def test_reads_full_text_paragraph(self, app_context):
        loader = QuoteLoader(app_context)
        card = html.fromstring(
            '<div><div id="lenta-card__text-quote-full"><p>Full text here</p></div></div>'
        )
        assert loader.get_quote_text(card) == 'Full text here'

    def test_returns_none_when_nothing_found(self, app_context):
        loader = QuoteLoader(app_context)
        card = html.fromstring('<div><span>irrelevant</span></div>')
        assert loader.get_quote_text(card) is None


class TestFormatQuoteText:
    def test_csv_strips_tabs_and_newlines(self, app_context):
        app_context.quote_file = 'quotes.csv'
        loader = QuoteLoader(app_context)
        assert loader.format_quote_text('a\tb\nc') == 'a b c'

    def test_excel_keeps_text_unchanged(self, app_context):
        app_context.quote_file = 'quotes.xlsx'
        loader = QuoteLoader(app_context)
        assert loader.format_quote_text('a\tb\nc') == 'a\tb\nc'

    def test_none_text_returns_none(self, app_context):
        app_context.quote_file = 'quotes.csv'
        loader = QuoteLoader(app_context)
        assert loader.format_quote_text(None) is None


class TestGetQuotes:
    def test_get_quotes_parses_full_and_fetches_truncated(self, app_context):
        app_context.quote_count = 1
        loader = QuoteLoader(app_context)

        with patch(
            'Modules.QuoteLoader.download_page',
            side_effect=[QUOTE_LIST_PAGE, QUOTE_DETAIL_PAGE],
        ):
            quotes = loader.get_quotes()

        assert len(quotes) == 2
        full_quote = next(q for q in quotes if '111111' in q.link)
        truncated_quote = next(q for q in quotes if '222222' in q.link)
        assert full_quote.text == 'Some wise words.'
        assert truncated_quote.text == 'The full untruncated quote text.'

    def test_get_quotes_stops_on_empty_page(self, app_context):
        app_context.quote_count = math.inf
        loader = QuoteLoader(app_context)

        with patch('Modules.QuoteLoader.download_page', return_value=EMPTY_PAGE):
            quotes = loader.get_quotes()

        assert quotes == []

    def test_get_quotes_stops_on_redirect_page(self, app_context):
        app_context.quote_count = math.inf
        loader = QuoteLoader(app_context)

        with patch('Modules.QuoteLoader.download_page', return_value=REDIRECT_PAGE):
            quotes = loader.get_quotes()

        assert quotes == []

    def test_get_quotes_continues_when_detail_fetch_fails(self, app_context):
        app_context.quote_count = 1
        loader = QuoteLoader(app_context)

        with patch(
            'Modules.QuoteLoader.download_page',
            side_effect=[QUOTE_LIST_PAGE, Exception('boom')],
        ):
            quotes = loader.get_quotes()

        # the truncated quote is skipped because fetching its detail page failed
        assert len(quotes) == 1
        assert quotes[0].text == 'Some wise words.'


class TestSaveQuotes:
    def test_save_new_quotes_to_csv(self, app_context, temp_csv_file, sample_quote):
        os.remove(temp_csv_file)
        app_context.quote_file = temp_csv_file
        app_context.rewrite_all = False
        loader = QuoteLoader(app_context)

        loader.save_quotes([sample_quote])

        with open(temp_csv_file, encoding='utf-8') as f:
            content = f.read()
        assert sample_quote.link in content

    def test_rewrite_all_deletes_existing_file(self, app_context, temp_csv_file, sample_quote):
        app_context.quote_file = temp_csv_file
        app_context.rewrite_all = True
        loader = QuoteLoader(app_context)

        loader.save_quotes([sample_quote])

        assert os.path.exists(temp_csv_file)
        with open(temp_csv_file, encoding='utf-8') as f:
            content = f.read()
        assert sample_quote.link in content

    def test_updating_existing_quote_replaces_text(self, app_context, temp_csv_file, sample_quote):
        os.remove(temp_csv_file)
        app_context.quote_file = temp_csv_file
        app_context.rewrite_all = False
        loader = QuoteLoader(app_context)

        loader.save_quotes([sample_quote])
        sample_quote.text = 'Updated text'
        loader.save_quotes([sample_quote])

        with open(temp_csv_file, encoding='utf-8') as f:
            content = f.read()
        assert content.count(sample_quote.link) == 1
