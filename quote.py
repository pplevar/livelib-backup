from book import Book


class Quote:
    def __init__(self, link, text, book=None):
        self.link = link
        self.id = link[link.rfind("/") + 1:]
        self.full_link = 'https://www.livelib.ru' + link
        self.text = text
        self.book = book

    def __str__(self):
        return 'id="%s", link="%s", text="%s", book_id="%s"' % (self.id, self.link, self.text, self.book.id)

    def add_book(self, book):
        self.book = book
