# Taken mostly from https://github.com/KonH/LivelibExport

from book import Book
from read_parser import ReadParser
from csv_writer import CsvWriter
from details_parser import DetailsParser
from cache_manager import CacheManager
from page_loader import PageLoader

# settings
input_file_names = [('read.html', 'read'), ('wish.html', 'wish')]
cache_dir_name = 'cache'
out_file_name = 'out.csv'
min_delay = 90
max_delay = 120

for input_file_name, status in input_file_names:
    print('Load books from file: "%s"' % input_file_name)
    read_parser = ReadParser()
    if read_parser.load_from_file(input_file_name) is False:
        exit(1)
    print('Books loaded.\n')

    print('Parse books from summary.')
    books = read_parser.parse_books(status)
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
    writer.save(ready_books, out_file_name)
    print('Books saved to "%s"' % out_file_name)
