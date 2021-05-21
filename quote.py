from book import Book


def handle_none(none):
    return '' if none is None else none


class Quote:
    def __init__(self, link, text, book=Book()):
        self.link = 'https://www.livelib.ru' + handle_none(link)
        self.text = handle_none(text)
        self.book = book

    def __str__(self):
        return '%s\t%s\t%s\t%s\t%s' % (self.book.name, self.book.author, self.text, self.book.link, self.link)

    def add_book(self, book):
        self.book = book
