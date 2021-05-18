# Taken mostly from https://github.com/KonH/LivelibExport

from book import Book
from quote import Quote
from livelib_parser import Parser
from csv_writer import CsvWriter
from details_parser import DetailsParser
from cache_manager import CacheManager
from page_loader import PageLoader

# settings
input_file_names = [('read.html', 'read'), ('wish.html', 'wish')]
cache_dir_name = 'cache_books'
out_file_name = 'backup_books.csv'
min_delay = 90
max_delay = 120

parser = Parser()
for input_file_name, status in input_file_names:
    print('Load books from file: "%s"' % input_file_name)
    if parser.load_from_file(input_file_name) is False:
        exit(1)
    print('Books loaded.\n')

    print('Parse books from summary.')
    books = parser.parse_books(status)
    print('Books parsed: %s.\n' % len(books))

    print('Start download detailed book pages with status "%s".' % status)
    cache = CacheManager(cache_dir_name)
    loader = PageLoader(cache, min_delay, max_delay)
    loader.download(books)
    print('Detailed book pages downloaded.\n')

    print('Prepare books for export.')
    details_parser = DetailsParser(cache)
    ready_books = details_parser.parse(books)
    print('Books ready to export: %s.\n' % len(ready_books))

    writer = CsvWriter()
    writer.save_books(ready_books, out_file_name)
    print('Books saved to "%s"' % out_file_name)


# settings
input_file_name = 'quotes.html'
cache_dir_name = 'cache_quotes'
out_file_name = 'backup_quotes.csv'

print('Load quotes from file: "%s"' % input_file_name)
if parser.load_from_file(input_file_name) is False:
    exit(1)
print('Quotes loaded.\n')

print('Parse books from summary.')
quotes = parser.parse_quotes()
print('Quotes parsed: %s.\n' % len(quotes))

# print('Start download detailed quotes pages with status.')
# cache = CacheManager(cache_dir_name)
# loader = PageLoader(cache, min_delay, max_delay)
# loader.download(quotes)
# print('Detailed quote pages downloaded.\n')

# print('Prepare quotes for export.')
# details_parser = DetailsParser(cache)
# ready_quotes = details_parser.parse(quotes)
# print('Quotes ready to export: %s.\n' % len(ready_quotes))

writer = CsvWriter()
writer.save_quotes(quotes, out_file_name)
print('Quotes saved to "%s"' % out_file_name)
