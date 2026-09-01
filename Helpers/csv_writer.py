from Helpers.backup_store import BackupStore, BOOKS_ADAPTER, QUOTES_ADAPTER


def save_books(books, file_path):
    """
    Сохраняет книги из списка в таблицу, обновляя уже существующие записи
    :param books: list - список книг (классов Book)
    :param file_path: string - путь к таблице
    """
    BackupStore(BOOKS_ADAPTER).save(books, file_path)


def save_quotes(quotes, file_path):
    """
    Сохраняет цитаты из списка в таблицу, обновляя уже существующие записи
    :param quotes: list - список цитат (классов Quote)
    :param file_path: string - путь к таблице
    """
    BackupStore(QUOTES_ADAPTER).save(quotes, file_path)
