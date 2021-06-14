import os


def save_books(books, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        if os.path.getsize(file_path) == 0:
            file.write('Name\tAuthor\tStatus\tMy Rating\tDate\tLink\n')
        for book in books:
            file.write(str(book) + '\n')


def save_quotes(quotes, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        if os.path.getsize(file_path) == 0:
            file.write('Name\tAuthor\tQuote text\tBook link\tQuote link\n')
        for quote in quotes:
            file.write(str(quote) + '\n')