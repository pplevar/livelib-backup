import os

from lxml import html
import pandas as pd

from Helpers.book import Book
from Helpers.livelib_parser import slash_add, href_i, is_last_page, is_redirecting_page, handle_xpath, error_handler
from Helpers.page_loader import download_page
from Helpers.quote import Quote
from Modules.BookLoader import BookLoader
from export import logger


class QuoteLoader:
    def __init__(self, app_context):
        self.ac = app_context

    def get_quotes(self):
        """
        Возвращает список цитат (классов Quote)
        :return: list - список классов Quote
        """
        quotes = []
        href = slash_add(self.ac.user_href, 'quotes')
        page_idx = 1

        while page_idx <= self.ac.quote_count:
            self.ac.wait_for_delay()

            # если происходит какая-то ошибка с подключением, переходим к следующей странице
            try:
                page = html.fromstring(download_page(href_i(href, page_idx), self.ac.driver))
            except Exception as e:
                logger.error(f'Some error was erupted: {e}')
                continue
            finally:
                page_idx += 1

            if is_last_page(page) or is_redirecting_page(page):
                break

            for quote_html in page.xpath('.//article'):
                quote = self.quote_parser(quote_html)
                if quote is not None and quote not in quotes:
                    if quote.text == '!!!NOT_FULL###':  # обрабатываем случай, когда показан не весь текст цитаты
                        self.ac.wait_for_delay()
                        try:  # просматриваем страницу цитаты, в случае ошибки переходим к следующей цитате
                            quote_page = html.fromstring(download_page(quote.link, self.ac.driver))
                        except Exception as e:
                            logger.error(f'Some error was erupted: {e}')
                            continue
                        quote.text = self.get_quote_text(handle_xpath(quote_page, './/article'))
                    quotes.append(quote)

        return quotes

    def quote_parser(self, quote_html):
        """
        Парсит html-узел с цитатой
        :param quote_html: html-узел с цитатой
        :return: Quote or None
        """
        card = handle_xpath(quote_html, './/div[@class="lenta-card"]')
        if card is None:
            return error_handler('card', quote_html)

        # Просматриваем все ссылки пока не найдем те, что нам подойдут
        link = None
        link_book = None
        for href in card.xpath('.//a'):
            if link is None:
                link = self.try_get_quote_link(href.get('href'))
            if link_book is None:
                link_book = BookLoader.try_get_book_link(href.get('href'))

        text = self.get_quote_text(card)
        # Если мы нашли "Читать дальше...", нужно дать об этом знать и обработать во внешней функции
        if len(card.xpath('.//a[@class="read-more__link"]')):
            text = '!!!NOT_FULL###'

        book_card = handle_xpath(card, './/div[@class="lenta-card-book__wrapper"]')
        book_name = handle_xpath(book_card, './/a[@class="lenta-card__book-title"]/text()')
        book_author = handle_xpath(book_card, './/p[@class="lenta-card__author-wrap"]/a/text()')

        if link is not None and link_book is not None and text is not None:
            return Quote(link, text, Book(link_book, name=book_name, author=book_author))
        if link is None or link_book is None:
            return error_handler('link', quote_html)
        if text is None:
            return error_handler('text', quote_html)
        return None

    def get_quote_text(self, card):
        """
        Считываем текст цитаты
        :param card: html-узел с цитатой
        :return: string or None
        """

        item = handle_xpath(card, './/blockquote')
        if item is None:
            item = handle_xpath(card, './/div[@id="lenta-card__text-quote-full"]/p')
        if item is None:
            item = handle_xpath(card, './/div[@id="lenta-card__text-quote-full"]/div')
        if item is None:
            item = handle_xpath(card, './/p')

        quote_text = None if item is None else self.format_quote_text(item.text_content())
        logger.info(f"\tQuote Processed: {quote_text}")
        return quote_text

    def save_quotes(self, new_quotes):
        file_ext = self.ac.quote_file.split('.')[-1]

        if self.ac.rewrite_all:
            if os.path.exists(self.ac.quote_file):
                os.remove(self.ac.quote_file)
            logger.info(f'All quotes were deleted from {self.ac.quote_file}.')

        quotes_df = pd.DataFrame(columns=['Name', 'Author', 'Quote text', 'Book link', 'Quote link'])
        if file_ext in ['csv']:
            if os.path.exists(self.ac.quote_file):
                quotes_df = pd.read_csv(self.ac.quote_file, sep='\t')
        else:
            if os.path.exists(self.ac.quote_file):
                quotes_df = pd.read_excel(self.ac.quote_file)

        for nc in new_quotes:
            if quotes_df[quotes_df['Quote link'] == nc.link].shape[0] > 0:
                quotes_df.loc[quotes_df['Quote link'] == nc.link, 'text'] = nc.text
            else:
                quotes_df.loc[len(quotes_df.index)] = [
                    nc.book.name,
                    nc.book.author,
                    nc.text,
                    nc.book.link,
                    nc.link
                ]

        if file_ext in ['csv']:
            quotes_df.to_csv(self.ac.quote_file, sep='\t')
        else:
            quotes_df.to_excel(self.ac.quote_file)

        logger.info(f'The quotes were written to {self.ac.quote_file}.')

    def format_quote_text(self, text):
        """
        Обработка текста цитаты (удаление табов, переходов на новую строку)
        :param text: string or None
        :return: string or None
        """
        if self.ac.quote_file.split('.')[-1] == 'csv':
            return None if text is None else text.replace('\t', ' ').replace('\n', ' ')
        else:
            return text

    @staticmethod
    def try_get_quote_link(link):
        """
        Проверяет валидность ссылки на цитату
        :param link: string - ссылка
        :return: string or None
        """
        if "/quote/" in link:
            return link
        return None
