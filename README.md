# Утилита для сохранения профилей книжного портала Livelib.ru

## Описание

Сохраняет список книг (прочитанные, желаемые и проч.), а также список цитат указанного пользователя в виде csv таблицы.

Не требует авторизации.

Следущие данные сохраняются в двух плоских csv таблицах с разделителем '/t':
- Книги:
    - Наименование
    - Автор(ы)
    - Статус (прочитал/читаю/хочу прочитать...)
    - Моя оценка (при наличии)
    - Дата прочтения (при наличии)
    - Ссылка на книгу
    
- Цитаты:
    - Наименования книги
    - Автор(ы)
    - Цитата
    - Ссылка на книгу
    - Ссылка на цитату

При повторном запуске обновляет уже имеющиеся таблицы.

## Запуск

Необходимо установить зависимости:
```
pip3 install -r requirements.txt  # for Linux
py -m pip install -r requirements.txt  # for Windows
```

После чего можно запускать скрипт `export.py`, где `username` — это ваше имя пользователя, которое вы берете из ссылки на ваш личный кабинет вида https://www.livelib.ru/reader/username
```
python3 export.py username  # for Linux
python export.py username  # for Windows
```

## Дополнительная информация об аргументах

Чтобы не лезть сюда, всегда можно вызвать:
```
python export.py --help
```

Если вы хотите по-своему назвать csv файлы, используйте `--books_backup` и/или `--quote_backup`.

Если вы хотите поменять время ожидания между запросами к сайту livelib.ru, используйте `--min_delay` и `--max_delay`.
Но будьте аккуратны! Если интервалы будут слишком маленькими, сайт может подумать, что вы бот, что повлечет за собой блокировку.

Если вы хотите, чтобы скрипт обработал только первые `N` страниц в прочитанных книгах, используйте `--read_count N`.

Если вы хотите, чтобы скрипт обработал только первые `N` страниц в цитатах, используйте `--quote_count N`.

Если вы хотите полностью перезаписать таблицы, например, если вы удалили несколько книг из прочитанных, используйте `-R`.

## Завершение скрипта

Скрипт сам автоматически завершается.

Если вы хотите досрочно завершить программу, нажмите `Ctrl+C` в терминале. 
Если вы сделали это до записи в файл, то ничего не изменится.

Например, если скрипт обработал 4 страницы прочитанных книг и не перешел к желаемым, а вы завершили процесс, то в таблице ничего не изменится.

## Testing

The project includes a comprehensive test suite with 119 tests covering unit tests, integration tests, and workflows.

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html
```

For detailed testing information, see:
- [Test Suite README](tests/README.md) - Complete testing guide
- [Test Suite Summary](TEST_SUITE_SUMMARY.md) - Coverage and metrics

### Test Coverage

- **119 passing tests** (100% pass rate)
- **50% code coverage** overall
- **100% coverage** on core data models and I/O operations
- **Integration tests** for complete workflows
