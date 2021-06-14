import csv
import os
from .book import Book
from .quote import Quote


def read_csv(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader, None)  # skip the header
        return list(reader)


def convert_csv_to_books(cache):
    return [Book(link, stat, name, auth, rate, date) for name, auth, stat, rate, date, link in cache]


def convert_csv_to_quotes(cache):
    return [Quote(link, text, Book(blink, '', name, auth)) for name, auth, text, blink, link in cache]


def read_books_from_csv(file_name):
    return convert_csv_to_books(read_csv(file_name))


def read_quotes_from_csv(file_name):
    return convert_csv_to_quotes(read_csv(file_name))
