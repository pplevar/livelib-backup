# Taken mostly from https://github.com/KonH/LivelibExport

import os
from book import Book
from quote import Quote


def str_or_empty(str):
    if str is None:
        return ''
    else:
        return str


def format_book(book):
    return "%s\t%s\t%s\t%s\t%s\t%s\n" % (book.full_link,
                                         book.status,
                                         str_or_empty(book.name),
                                         str_or_empty(book.ISBN),
                                         book.rating,
                                         book.date)


def format_quote(quote):
    return "%s\t%s\t%s\t%s\t%s\n" % (quote.full_link,
                                     quote.text,
                                     str_or_empty(quote.book if quote.book is None else quote.book.author),
                                     str_or_empty(quote.book if quote.book is None else quote.book.name),
                                     str_or_empty(quote.book if quote.book is None else quote.book.link))


# Write books content to csv file
class CsvWriter:
    def save_books(self, books, file_name):
        with open(file_name, 'a', encoding="utf-8") as file:
            if os.path.getsize(file_name) == 0:
                file.write('Link\tStatus\tTitle\tISBN\tMy Rating\tDate Added\n')
            for book in books:
                file.write(format_book(book))

    def save_quotes(self, quotes, file_name):
        with open(file_name, 'a', encoding="utf-8") as file:
            if os.path.getsize(file_name) == 0:
                file.write('Link\tText\tAuthor\tTitle\tBook link\n')
            for quote in quotes:
                file.write(format_quote(quote))
