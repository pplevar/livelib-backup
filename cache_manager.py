# Taken mostly from https://github.com/KonH/LivelibExport

import os
from os import path


# Operates with book pages cache_books
class CacheManager:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()

    def ensure_cache_dir(self):
        if not path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

    def get_path(self, id):
        return path.join(self.cache_dir, id + '.html')

    def is_cached(self, id):
        return path.exists(self.get_path(id))

    def save(self, id, content):
        file_name = self.get_path(id)
        with open(file_name, 'wb') as file:
            print('Save to cache_books: "%s"' % file_name)
            file.write(content)

    def load(self, id):
        file_name = self.get_path(id)
        try:
            with open(file_name, 'r', encoding="utf-8") as file:
                return file.read()
        except Exception as ex:
            print('load_book_content_from_cache("%s"): %s' % (file_name, ex))
            return None
