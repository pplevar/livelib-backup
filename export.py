from livelib_parser import get_books, get_quotes, slash_add
from csv_reader import read_books_from_csv, read_quotes_from_csv
from csv_writer import save_books, save_quotes


def get_new_items(old_data, new_data):
    items = []
    for new in new_data:
        if new not in old_data:
            items.append(new)
    return items


if __name__ == "__main__":

    ll_href = 'https://www.livelib.ru/reader'

    user = input('Type your username: ')
    print()

    user_href = slash_add(ll_href, user)
    book_file = 'backup_%s_book.csv' % user
    quote_file = 'backup_%s_quote.csv' % user
    print('Data from the page %s will be saved to files %s and %s' % (user_href, book_file, quote_file))
    print()

    books = []
    for status in ('read', 'reading', 'wish'):
        print('Started parsing the book pages with status "%s".' % status)
        books = books + get_books(user_href, status)
        print('The book pages with status "%s" were parsed.' % status)
        print()

    print('Started reading the books from %s.' % book_file)
    books_csv = read_books_from_csv(book_file)
    print('The books were read from %s.' % book_file)

    print('Started calculating the newly added books.')
    new_books = get_new_items(books_csv, books)
    print('The newly added books were calculated.')

    print('Started writing the newly added books to %s.' % book_file)
    save_books(new_books, book_file)
    print('The newly added books were written to %s.' % book_file)
    print()

    print('Started parsing the quote pages.')
    quotes = get_quotes(user_href)
    print('The quote pages were parsed.')
    print()

    print('Started reading the quotes from %s.' % quote_file)
    quotes_csv = read_quotes_from_csv(quote_file)
    print('The quotes were read from %s.' % quote_file)

    print('Started calculating the newly added quotes.')
    new_quotes = get_new_items(quotes_csv, quotes)
    print('The newly added quotes were calculated.')

    print('Started writing the newly added quotes to %s.' % book_file)
    save_quotes(new_quotes, quote_file)
    print('The newly added quotes were written to %s.' % book_file)
    print()
