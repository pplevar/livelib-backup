import re
from collections import defaultdict
from lxml import html
from lxml import etree
from book import Book
from quote import Quote
from urllib import request
from page_loader import download_page, wait_for_delay
from livelib_parser import *


def is_last_page(page):
    return bool(len(page.xpath('//div[@class="with-pad"]')))


def href_i(href, i):
    return href + '/~' + str(i)


def mydateparser(date):
    m = re.search('\d{4} г.', date)
    if m is not None:
        year = m.group(0).split(' ')[0]
        raw_month = date.split(' ')[0]
        month = try_parse_month(raw_month)
        return '%s-%s-01' % (year, month)
    return None


def mybookparser(book_html, date, status):
    book_data = book_html.xpath('.//div/div/div[@class="brow-data"]/div')[0]
    book_name = book_data.xpath('.//a[contains(@class, "brow-book-name")]')[0]
    link = try_get_book_link(book_name.get("href"))
    name = book_name.text
    author_tmp = book_data.xpath('.//a[@class="brow-book-author"]/text()')
    author = author_tmp[0] if len(author_tmp) else None
    rating = None
    if status == 'read':
        rating = book_data.xpath('.//div[@class="brow-ratings"]/span/span/span/text()')[0]
    return Book(link, rating, last_date, status, author, name)


href = 'https://www.livelib.ru/reader/levar/wish'
status = 'wish'
page_idx = 1
page = html.fromstring(download_page(href_i(href, page_idx)))
while not is_last_page(page):
    last_date = None
    for div_book_html in page.xpath('.//div[@id="booklist"]/div'):
        dates = div_book_html.xpath('.//h2/text()')
        if len(dates):
            date = mydateparser(dates[0])
            if date is not None:
                last_date = date
            print(last_date)
        else:
            book = mybookparser(div_book_html, last_date, status)
            print(book)
    page_idx += 1
    wait_for_delay(5, 30)
    page = html.fromstring(download_page(href_i(href, page_idx)))


print("\n\nQUOTES NOW\n")
href = 'https://www.livelib.ru/reader/vzhukov00/quotes'
page_idx = 1
page = html.fromstring(download_page(href_i(href, page_idx)))
while not is_last_page(page):
    for quote_html in page.xpath('.//article'):
        quote = parse_quote(quote_html)
        print("None" if quote is None else quote)
    page_idx += 1
    wait_for_delay(5, 30)
    page = html.fromstring(download_page(href_i(href, page_idx)))

