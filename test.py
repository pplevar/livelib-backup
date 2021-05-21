import re
from collections import defaultdict
from lxml import html
from lxml import etree
from book import Book, print_header
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


def handle_xpath(html_node, request, i=0):
    tmp = html_node.xpath(request)
    return tmp[i] if len(tmp) else None


def mybookparser(book_html, date, status):
    book_data = handle_xpath(book_html, './/div/div/div[@class="brow-data"]/div')
    book_name = handle_xpath(book_data, './/a[contains(@class, "brow-book-name")]')
    link = try_get_book_link(book_name.get("href"))
    name = None if book_name is None else book_name.text
    author = handle_xpath(book_data, './/a[@class="brow-book-author"]/text()')
    rating = None
    if status == 'read':
        rating = handle_xpath(book_data, './/div[@class="brow-ratings"]/span/span/span/text()')
    return None if link is None else Book(link, status, name, author, rating, date)


def slash_add(left, right):
    return left + '/' + right


# book = Book('read', 'https://www.livelib.ru/book/1003017165-znak-edinoroga-rodzher-zhelyazny',
#             'Знак Единорога',
#             'Роджер Желязны',
#             '4',
#             None)
# print(print_header())
# print(book)
# print(book.to_list())

ll_href = 'https://www.livelib.ru/reader'
user = 'vzhukov00'
user_href = slash_add(ll_href, user)
for status in ('read', 'reading', 'wish'):
    href = slash_add(user_href, status)
    page_idx = 1
    page = html.fromstring(download_page(href_i(href, page_idx)))
    while not is_last_page(page):
        last_date = None
        for div_book_html in page.xpath('.//div[@id="booklist"]/div'):
            date = handle_xpath(div_book_html, './/h2/text()')
            if status == 'read' and date is not None:
                date = mydateparser(date)
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
href = slash_add(user_href, 'quotes')
page_idx = 1
page = html.fromstring(download_page(href_i(href, page_idx)))
while not is_last_page(page):
    for quote_html in page.xpath('.//article'):
        quote = parse_quote(quote_html)
        print("None" if quote is None else quote)
    page_idx += 1
    wait_for_delay(5, 30)
    page = html.fromstring(download_page(href_i(href, page_idx)))

