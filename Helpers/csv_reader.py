import csv
import os
from .book import Book
from .quote import Quote


def read_csv(file_path):
    """
    Считывает csv таблицу в виде списка, в котором лежат списки из ячеек строки
    :param file_path: string - путь к таблице
    :return: list - список списков из ячеек таблицы
    """
    if not os.path.exists(file_path):  # если таблицы не существует, следует вернуть пустой лист
        return []
    with open(file_path, "r", encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader, None)  # skip the header
        return list(reader)


def convert_csv_to_books(cache):
    """
    Конвертирует список списков из ячеек таблицы в список классов Book
    :param cache: list - список списков из ячеек таблицы с книгами
    :return: list - список классов Book
    """
    return [Book(link, stat, name, auth, rate, date) for name, auth, stat, rate, date, link in cache]


def convert_csv_to_quotes(cache):
    """
    Конвертирует список списков из ячеек таблицы в список классов Quote
    :param cache: list - список списков из ячеек таблицы с цитатами
    :return: list - список классов Quote
    """
    return [Quote(link, text, Book(blink, '', name, auth)) for name, auth, text, blink, link in cache]


def read_books_from_csv(file_name):
    """
    Возвращает список уже обработанных книг (классов Book), считанных из таблицы по данному пути
    :param file_name: string - путь к таблице с книгами
    :return: list - список классов Book
    """
    return convert_csv_to_books(read_csv(file_name))


def read_quotes_from_csv(file_name):
    """
    Возвращает список уже обработанных цитат (классов Quote), считанных из таблицы по данному пути
    :param file_name: string - путь к таблице с цитатами
    :return: list - список классов Quote
    """
    return convert_csv_to_quotes(read_csv(file_name))
