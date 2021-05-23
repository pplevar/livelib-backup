import re
import os
import csv
from lxml import html
from lxml import etree
from book import Book
from quote import Quote

from page_loader import download_page, wait_for_delay
from livelib_parser import error_handler, try_get_book_link, try_parse_month, try_get_quote_link


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
    if book_data is None:
        return error_handler('book_data', book_html)
    book_name = handle_xpath(book_data, './/a[contains(@class, "brow-book-name")]')
    link = try_get_book_link(book_name.get("href"))
    if link is None:
        return error_handler('link', book_html)
    name = None if book_name is None else book_name.text
    author = handle_xpath(book_data, './/a[@class="brow-book-author"]/text()')
    rating = None
    if status == 'read':
        rating = handle_xpath(book_data, './/div[@class="brow-ratings"]/span/span/span/text()')
    return None if link is None else Book(link, status, name, author, rating, date)


def myquoteparser(quote_html):
    card = handle_xpath(quote_html, './/div[@class="lenta-card"]')
    if card is None:
        return error_handler('card', quote_html)
    link = None
    link_book = None
    for href in card.xpath('.//a'):
        if link is None:
            link = try_get_quote_link(href.get('href'))
        if link_book is None:
            link_book = try_get_book_link(href.get('href'))
    text = handle_xpath(card, './/p/text()')
    book_card = handle_xpath(card, './/div[@class="lenta-card-book__wrapper"]')
    book_name = None if book_card is None else handle_xpath(book_card, './/a[@class="lenta-card__book-title"]/text()')
    book_author = None if book_card is None else handle_xpath(book_card, './/p[@class="lenta-card__author-wrap"]/a/text()')
    if link is not None and link_book is not None and text is not None:
        return Quote(link, text, Book(link_book, name=book_name, author=book_author))
    if link is None or link_book is None:
        return error_handler('link', quote_html)
    if text is None:
        return error_handler('text', quote_html)
    return None


def slash_add(left, right):
    return left + '/' + right


def get_books(user_href, status):
    books = []
    href = slash_add(user_href, status)
    page_idx = 1
    wait_for_delay(10, 30)
    page = html.fromstring(download_page(href_i(href, page_idx)))
    while not is_last_page(page):
        last_date = None
        for div_book_html in page.xpath('.//div[@id="booklist"]/div'):
            date = handle_xpath(div_book_html, './/h2/text()')
            if date is not None:
                date = mydateparser(date)
                if status == 'read' and date is not None:
                    last_date = date
            else:
                book = mybookparser(div_book_html, last_date, status)
                if book is not None:
                    books.append(book)
        page_idx += 1
        wait_for_delay(10, 30)
        page = html.fromstring(download_page(href_i(href, page_idx)))
    return books


def get_quotes(user_href):
    quotes = []
    href = slash_add(user_href, 'quotes')
    page_idx = 1
    wait_for_delay(10, 30)
    page = html.fromstring(download_page(href_i(href, page_idx)))
    while not is_last_page(page):
        for quote_html in page.xpath('.//article'):
            quote = myquoteparser(quote_html)
            if quote is not None:
                quotes.append(quote)
        page_idx += 1
        wait_for_delay(10, 30)
        page = html.fromstring(download_page(href_i(href, page_idx)))
    return quotes


def save_books(books, file_name):
    with open(file_name, 'a', encoding='utf-8') as file:
        if os.path.getsize(file_name) == 0:
            file.write('Name\tAuthor\tStatus\tMy Rating\tDate\tLink\n')
        for book in books:
            file.write(str(book) + '\n')


def save_quotes(quotes, file_name):
    with open(file_name, 'a', encoding='utf-8') as file:
        if os.path.getsize(file_name) == 0:
            file.write('Name\tAuthor\tQuote text\tBook link\tQuote link\n')
        for quote in quotes:
            file.write(str(quote) + '\n')


def read_cache(file_name):
    with open(file_name, "r", encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader, None)  # skip the header
        return list(reader)


def convert_cache_to_books(cache):
    return [Book(link, stat, name, auth, rate, date) for name, auth, stat, rate, date, link in cache]


def convert_cache_to_quotes(cache):
    return [Quote(link, text, Book(blink, '', name, auth)) for name, auth, text, blink, link in cache]


def get_new_items(old_data, new_data):
    items = []
    for new in new_data:
        if new not in old_data:
            items.append(new)
    return items


ll_href = 'https://www.livelib.ru/reader'
book_file = 'backup_book.csv'
quote_file = 'backup_quote.csv'

print('Type your username:', end=' ')
user = 'vzhukov00'
# user = input()
user_href = slash_add(ll_href, user)

books = []
for status in ('read', 'reading', 'wish'):
    books = books + get_books(user_href, status)

quotes = get_quotes(user_href)

book_cache = convert_cache_to_books(read_cache(book_file))
new_books = get_new_items(book_cache, books)

quote_cache = convert_cache_to_quotes(read_cache(quote_file))
new_quotes = get_new_items(quote_cache, quotes)

save_books(new_books, book_file)
save_quotes(new_quotes, quote_file)
