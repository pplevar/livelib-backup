import re
from collections import defaultdict
from lxml import html
from lxml import etree
from .book import Book
from .quote import Quote
from .page_loader import download_page, wait_for_delay


def error_handler(where, raw):
    """
    Обработчик ошибки при парсинге html страницы
    :param where: string - что не распарсилось
    :param raw: html-узел
    :return: None
    """
    print('ERROR: Parsing error (%s not parsed):' % where)
    print(etree.tostring(raw))
    print()
    return None


def try_get_book_link(link):
    """
    Проверяет валидность ссылки на книгу
    :param link: string - ссылка
    :return: string or None
    """
    if "/book/" in link or "/work/" in link:
        return link
    return None


def try_get_quote_link(link):
    """
    Проверяет валидность ссылки на цитату
    :param link: string - ссылка
    :return: string or None
    """
    if "/quote/" in link:
        return link
    return None


def try_parse_month(raw_month):
    """
    Возвращает месяц в нужном виде
    :param raw_month: string - месяц в текстовом виде
    :return: string - месяц в цифровом виде
    """
    dict = defaultdict(lambda: '01', {
        'Январь': '01',
        'Февраль': '02',
        'Март': '03',
        'Апрель': '04',
        'Май': '05',
        'Июнь': '06',
        'Июль': '07',
        'Август': '08',
        'Сентябрь': '09',
        'Октябрь': '10',
        'Ноябрь': '11',
        'Декабрь': '12'
    })
    return dict[raw_month]


def is_last_page(page):
    """
    Проверяет, что на странице уже пустой список объектов (она последняя)
    :param page: страница
    :return: bool
    """
    return bool(len(page.xpath('//div[@class="with-pad"]')))


def is_redirecting_page(page):
    """
    Проверяет, что страница является перенаправляющей
    :param page: страница
    :return: bool
    """
    flag = bool(len(page.xpath('//div[@class="page-404"]')))
    if flag:
        print('ERROR: Oops! Livelib suspects that you are a bot! Reading stopped.')
        print()
    return flag


def href_i(href, i):
    """
    Возвращает ссылку на i-ую страницу данного типа
    :param href: string - ссылка на страницу
    :param i: int - номер страницы
    :return: string - нужная ссылка
    """
    return href + '/~' + str(i)


def date_parser(date):
    """
    Конвертирует дату в нужный формат
    :param date: string
    :return: string or None
    """
    m = re.search('\d{4} г.', date)
    if m is not None:
        year = m.group(0).split(' ')[0]
        raw_month = date.split(' ')[0]
        month = try_parse_month(raw_month)
        return '%s-%s-01' % (year, month)
    return None


def handle_xpath(html_node, request, i=0):
    """
    Обертка над xpath. Возвращает i-ый найденный узел. Если он не нашелся, то возвращается None
    :param html_node: html-узел
    :param request: string - xpath запрос
    :param i: int - индекс (по дефолту 0)
    :return: нужный html-узел или None
    """
    if html_node is None:
        return None
    tmp = html_node.xpath(request)
    return tmp[i] if i < len(tmp) else None


def format_quote_text(text):
    """
    Обработка текста цитаты (удаление табов, переходов на новую строку)
    :param text: string or None
    :return: string or None
    """
    return None if text is None else text.replace('\t', ' ').replace('\n', ' ')


def book_parser(book_html, date, status):
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
    link = try_get_book_link(book_name.get("href"))  # в аргументах лежит ссылка
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


def get_quote_text(card):
    """
    Считываем текст цитаты
    :param card: html-узел с цитатой
    :return: string or None
    """
    item = handle_xpath(card, './/blockquote')
    if item is None:
        item = handle_xpath(card, './/p')
    return None if item is None else format_quote_text(item.text_content())


def quote_parser(quote_html):
    """
    Парсит html-узел с цитатой
    :param quote_html: html-узел с читатой
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
            link = try_get_quote_link(href.get('href'))
        if link_book is None:
            link_book = try_get_book_link(href.get('href'))

    text = get_quote_text(card)
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


def slash_add(left, right):
    return left + '/' + right


def get_books(user_href, status, min_delay=30, max_delay=60):
    """
    Возвращает список книг (классов Book)
    :param user_href: string - ссылка на пользователя
    :param status: string - статус книг
    :param min_delay: int - минимальное время задержки между запросами (по дефолту 30)
    :param max_delay: int - максимальное время задержки между запросами (по дефолту 60)
    :return: list - список классов Book
    """
    books = []
    href = slash_add(user_href, status)
    page_idx = 1
    page = None

    while True:
        wait_for_delay(min_delay, max_delay)

        # если происходит какая-то ошибка с подключением, переходим к следующей странице
        try:
            page = html.fromstring(download_page(href_i(href, page_idx)))
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
                book = book_parser(div_book_html, last_date, status)
                if book is not None:
                    books.append(book)

    return books


def get_quotes(user_href, min_delay=30, max_delay=60):
    """
    Возвращает список цитат (классов Quote)
    :param user_href: string - ссылка на пользователя
    :param min_delay: int - минимальное время задержки между запросами (по дефолту 30)
    :param max_delay: int - максимальное время задержки между запросами (по дефолту 60)
    :return: list - список классов Quote
    """
    quotes = []
    href = slash_add(user_href, 'quotes')
    page_idx = 1
    page = None

    while True:
        wait_for_delay(min_delay, max_delay)

        # если происходит какая-то ошибка с подключением, переходим к следующей странице
        try:
            page = html.fromstring(download_page(href_i(href, page_idx)))
        except Exception:
            continue
        finally:
            page_idx += 1

        if is_last_page(page) or is_redirecting_page(page):
            break

        for quote_html in page.xpath('.//article'):
            quote = quote_parser(quote_html)
            if quote is not None and quote not in quotes:
                if quote.text == '!!!NOT_FULL###':  # обрабатываем случай, когда показан не весь текст цитаты
                    wait_for_delay(min_delay, max_delay)
                    try:  # просматриваем страницу цитаты, в случае ошибки переходим к следующей цитате
                        quote_page = html.fromstring(download_page(quote.link))
                    except Exception:
                        continue
                    quote.text = get_quote_text(handle_xpath(quote_page, './/article'))
                quotes.append(quote)

    return quotes
