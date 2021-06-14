from .book import Book


def handle_none(none):
    """
    Возвращет пустую строку, если объект является None, сам объект иначе
    :param none: any class - какой-то объект
    :return: param class or string
    """
    return '' if none is None else none


def add_livelib(link):
    """
    Добавляет доменное имя к ссылке, взятой из внутренностей HTML-кода, где доменное имя опускается
    :param link: string - ссылка, начинается с '/'
    :return: string - полноценная ссылка, к которой можно обращаться
    """
    ll = 'https://www.livelib.ru'
    return link if ll in link else ll + link


class Quote:
    def __init__(self, link, text, book=Book()):
        self.link = add_livelib(handle_none(link))
        self.text = handle_none(text)
        self.book = book

    def __str__(self):
        return '%s\t%s\t%s\t%s\t%s' % (self.book.name, self.book.author, self.text, self.book.link, self.link)

    def __eq__(self, other):
        return self.link == other.link

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_list(self):
        return self.__dict__.values()

    def add_book(self, book):
        self.book = book
