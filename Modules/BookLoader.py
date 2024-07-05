from lxml import html

from Helpers.book import Book
from Helpers.livelib_parser import slash_add, href_i, is_last_page, is_redirecting_page, handle_xpath, error_handler, \
    date_parser
from Helpers.page_loader import download_page


class BookLoader:
    def __init__(self, app_context):
        self.ac = app_context

    def get_books(self, status):
        """
        Возвращает список книг (классов Book)
        :param status: string - статус книг
        :return: list - список классов Book
        """
        books = []
        href = slash_add(self.ac.user_href, status)
        page_idx = 1

        while page_idx <= self.ac.page_count:
            self.ac.wait_for_delay()

            # если происходит какая-то ошибка с подключением, переходим к следующей странице
            try:
                page = html.fromstring(download_page(href_i(href, page_idx), self.ac.driver))
            except Exception:
                continue
            finally:
                page_idx += 1

            if is_last_page(page) or is_redirecting_page(page):
                break

            last_date = None
            for div_book_html in page.xpath('.//div[@id="booklist"]/div'):
                date = handle_xpath(div_book_html, './/h2/text()')
                if date is not None:
                    date = date_parser(date)
                    if status == 'read' and date is not None:
                        last_date = date
                else:
                    book = self.book_parser(div_book_html, last_date, status)
                    if book is not None:
                        books.append(book)

        return books

    def book_parser(self, book_html, date, status):
        """
        Парсит html-узел с книгой
        :param book_html: html-узел с книгой
        :param date: string or None - дата прочтения
        :param status: string - статус книги
        :return: Book or None
        """
        book_data = handle_xpath(book_html, './/div/div/div[@class="brow-data"]/div')
        if book_data is None:
            return error_handler('book_data', book_html)

        book_name = handle_xpath(book_data, './/a[contains(@class, "brow-book-name")]')
        link = self.try_get_book_link(book_name.get("href"))  # в аргументах лежит ссылка
        if link is None:
            return error_handler('link', book_html)
        name = None if book_name is None else book_name.text

        author = book_data.xpath('.//a[contains(@class, "brow-book-author")]/text()')
        if len(author):
            author = ', '.join(author)  # в случае нескольких авторов нужно добавить запятые

        rating = None
        if status == 'read':
            rating = handle_xpath(book_data, './/div[@class="brow-ratings"]/span/span/span/text()')

        return Book(link, status, name, author, rating, date)

    @staticmethod
    def try_get_book_link(link):
        """
        Проверяет валидность ссылки на книгу
        :param link: string - ссылка
        :return: string or None
        """
        if "/book/" in link or "/work/" in link:
            return link
        return None
