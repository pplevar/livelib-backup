# Taken mostly from https://github.com/KonH/LivelibExport

import time
import random
from urllib import request


def download_page(link):
    print('Start download page from "%s"' % link)
    with request.urlopen(link) as data:
        content = data.read()
        print('Page downloaded.')
        return content


def wait_for_delay(min_delay, max_delay=-1):
    delay = random.randint(min_delay, max_delay) if max_delay >= 0 else min_delay
    print("Waiting %s sec..." % delay)
    time.sleep(delay)


# Page loader to download book pages to cache_books
class PageLoader:
    def __init__(self, cache, min_delay, max_delay):
        self.cache = cache
        self.min_delay = min_delay
        self.max_delay = max_delay

    def try_download_book_page(self, book):
        print('Downloading book with id = "%s" from "%s"' % (book.id, book.full_link))
        if self.cache.is_cached(book.id):
            print('Already in cache_books, skipping.')
            return False
        else:
            page = download_page(book.full_link)
            self.cache.save(book.id, page)
            return True

    def download(self, books):
        count = 1
        total = len(books)
        for book in books:
            print('%s/%s' % (count, total))
            count += 1
            if self.try_download_book_page(book) and count != total:
                wait_for_delay(self.min_delay, self.max_delay)
