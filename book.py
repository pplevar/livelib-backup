# Taken mostly from https://github.com/KonH/LivelibExport

class Book:
    def __init__(self, link, rating=None, date=None, status='', author=None, name=None):
        self.link = link
        self.rating = rating
        self.id = link[link.rfind("/") + 1:]
        self.full_link = 'https://www.livelib.ru' + link
        self.date = date
        self.status = status
        self.author = author
        self.name = name
        self.ISBN = None

    def __str__(self):
        return 'id="%s", link="%s", rating="%s", date="%s", name="%s", author="%s"' % \
               (self.id, self.link, self.rating, self.date, self.name, self.author)

    def add_isbn(self, isbn):
        self.ISBN = isbn

    def add_name(self, name):
        self.name = name

    def add_author(self, author):
        self.author = author
