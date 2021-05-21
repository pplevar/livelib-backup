# Taken mostly from https://github.com/KonH/LivelibExport

def print_header():
    return '\t'.join(vars(Book()).keys())


def handle_none(none):
    return '' if none is None else none


class Book:
    def __init__(self, link=None, status=None, name=None, author=None, rating=None, date=None):
        self.name = handle_none(name)
        self.author = handle_none(author)
        self.status = handle_none(status)
        self.rating = handle_none(rating)
        self.date = handle_none(date)
        self.link = 'https://www.livelib.ru' + handle_none(link)

    def __str__(self):
        return '%s\t%s\t%s\t%s\t%s\t%s' % (self.name, self.author, self.status, self.rating, self.date, self.link)

    def to_list(self):
        return self.__dict__.values()

    def add_name(self, name):
        self.name = name

    def add_author(self, author):
        self.author = author
