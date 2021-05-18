# Taken mostly from https://github.com/KonH/LivelibExport

import re
from collections import defaultdict
from lxml import html
from lxml import etree
from book import Book
from quote import Quote


def get_rating_from_class(rating_class):
    try:
        if rating_class[0] == 'r':
            return int(rating_class[1:2])
        return None
    except Exception as ex:
        print('get_rating_from_class("%s"): %s' % (rating_class, ex))
        return None


def try_get_book_link(link):
    if "/book/" in link:
        return link
    return None


def parse_book(row, last_date, status):
    link = None
    rating = None

    for cell in row.iter():
        if rating is None:
            spans = cell.xpath('.//span')
            if len(spans) == 2:
                rating_class = spans[1].get('class')
                rating = get_rating_from_class(rating_class)
        if link is None:
            hrefs = cell.xpath('.//a')
            if len(hrefs):
                link = try_get_book_link(hrefs[0].get('href'))

    if link is not None and (rating is not None or status != 'read'):
        return Book(link, rating, last_date, status)
    if link is not None and status == 'read':
        print('Parsing error (rating not parsed):')
        print(etree.tostring(row))
        print()
    if rating is not None:
        print('Parsing error (link not parsed):')
        print(etree.tostring(row))
        print()
    return None


def try_get_quote_link(link):
    if "/quote/" in link:
        return link
    return None


def parse_quote(row):
    cards = row.xpath('.//div[@class="lenta-card"]')
    card = cards[0] if len(cards) else None
    hrefs = card.xpath('.//a')
    link = None
    link_book = None
    for href in hrefs:
        if link is None:
            link = try_get_quote_link(href.get('href'))
        if link_book is None:
            link_book = try_get_book_link(href.get('href'))
    texts = card.xpath('.//p/text()')
    text = texts[0] if len(texts) else None
    if link is not None and link_book is not None and text is not None:
        return Quote(link, text, Book(link_book))
    if link is None or link_book is None:
        print('Parsing error (link not parsed):')
        print(etree.tostring(row))
        print()
    if text is None:
        print('Parsing error (text not parsed):')
        print(etree.tostring(row))
        print()
    return None


def try_parse_month(raw_month):
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


def try_parse_date(row):
    headers = row.xpath('.//td/h2')
    for header in headers:
        raw_text = header.text
        if raw_text is not None:
            m = re.search('\d{4} г.', raw_text)
            if m is not None:
                year = m.group(0).split(' ')[0]
                raw_month = raw_text.split(' ')[0]
                month = try_parse_month(raw_month)
                return '%s-%s-01' % (year, month)
    return None


# Parser - parse some list in html format
class Parser:
    def __init__(self):
        self.content = None

    def load_from_file(self, file_name):
        try:
            with open(file_name, 'r', encoding="utf-8") as file:
                self.content = file.read()
                return True
        except Exception as ex:
            print('load_from_file("%s"): %s' % (file_name, ex))
            self.content = None
            return False

    def parse_books(self, status):
        books = []
        books_html = html.fromstring(self.content)
        rows = books_html.xpath('//tr')
        last_date = None

        i = 0                                                   # tmp

        for row in rows:
            result = parse_book(row, last_date, status)
            if result is not None:
                books.append(result)
            else:
                date = try_parse_date(row)
                if date is not None:
                    last_date = date

            if i == 15:                                         # tmp
                break                                           # tmp
            i += 1                                              # tmp

        return books

    def parse_quotes(self):
        quotes = []
        quotes_html = html.fromstring(self.content)
        rows = quotes_html.xpath('.//article')

        i = 0                                                   # tmp

        for row in rows:
            result = parse_quote(row)
            if result is not None:
                quotes.append(result)

            if i == 3:                                          # tmp
                break                                           # tmp
            i += 1                                              # tmp

        return quotes
