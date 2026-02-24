# Architecture Documentation

## Overview

**LiveLib Backup** is a Python utility that exports user data from the LiveLib.ru book portal. It scrapes publicly available user profile pages and saves the data to CSV files without requiring authentication.

**Version:** Current (pre-refactoring)  
**Last Updated:** 2026-02-24  
**Author:** Leonid Karavaev (@pplevar)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (CLI)                                │
│                    python export.py <username>                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      export.py (Main)                            │
│  • Argument parsing                                              │
│  • Orchestration                                                 │
│  • Global AppContext                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│     BookLoader           │    │     QuoteLoader          │
│  (Modules/BookLoader.py) │    │  (Modules/QuoteLoader.py)│
│  • Fetch books by status │    │  • Fetch quotes          │
│  • Parse book data       │    │  • Parse quote data      │
└──────────────────────────┘    └──────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Helpers (Shared Utilities)                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ page_loader.py  │  │ livelib_parser  │  │  arguments.py   │ │
│  │ • HTTP requests │  │ • HTML parsing  │  │ • CLI args      │ │
│  │ • Selenium      │  │ • XPath helpers │  │ • Validation    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ csv_reader.py   │  │ csv_writer.py   │  │  utils.py       │ │
│  │ • Read CSV      │  │ • Write CSV     │  │ • Helpers       │ │
│  │ • To models     │  │ • Append mode   │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Models (Helpers/)                       │
│  ┌─────────────────┐              ┌─────────────────┐           │
│  │ book.py (Book)  │              │ quote.py (Quote)│           │
│  │ • link, status  │              │ • link, text    │           │
│  │ • name, author  │              │ • book (Book)   │           │
│  │ • rating, date  │              │                 │           │
│  └─────────────────┘              └─────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LiveLib.ru (Web Scraping)                   │   │
│  │  • User profile pages                                    │   │
│  │  • Book lists (read, reading, wish)                      │   │
│  │  • Quotes                                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Output Files                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  backup_<username>_book.csv      (Books)                │   │
│  │  backup_<username>_quote.csv     (Quotes)               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Architecture

### 1. Entry Point: `export.py`

**Responsibility:** Main orchestration and CLI entry point

**Key Components:**
- Global `AppContext` instance (shared state)
- Argument parsing via `Helpers.arguments`
- Book and quote processing loops
- Logging configuration

**Flow:**
```python
1. Parse CLI arguments
2. Initialize AppContext (global state)
3. Validate user profile exists
4. If not skipping books:
   - Initialize BookLoader
   - Fetch books for each status (read, reading, wish)
   - Compare with existing CSV (incremental mode)
   - Save new books
5. If not skipping quotes:
   - Initialize QuoteLoader
   - Fetch all quotes
   - Save quotes (update or append)
```

**Issues:**
- ❌ Global mutable state (`app_context`)
- ❌ No type hints
- ❌ Mixed concerns (orchestration + configuration)
- ❌ Bare `except Exception` blocks

---

### 2. Configuration: `Modules/AppContext.py`

**Responsibility:** Shared application state and configuration

**Structure:**
```python
@dataclass
class AppContext:
    user_href: str = None           # User profile URL
    status: str = None              # Current book status
    driver: object = None           # Selenium WebDriver (optional)
    skip: str = None                # Skip flag (books/quotes)
    book_file: str = None           # Output books CSV path
    quote_file: str = None          # Output quotes CSV path
    page_count: int = math.inf      # Max book pages to fetch
    quote_count: int = math.inf     # Max quote pages to fetch
    max_delay: int = 15             # Max delay between requests
    min_delay: int = 5              # Min delay between requests
    
    def wait_for_delay(self) -> None:
        # Random delay to avoid bot detection
```

**Issues:**
- ❌ God object (holds everything)
- ❌ No validation of values
- ❌ Mixed configuration and runtime state
- ❌ Hard to test in isolation

---

### 3. Data Loaders

#### 3.1 `Modules/BookLoader.py`

**Responsibility:** Fetch and parse book data from LiveLib

**Key Methods:**
- `get_books(status)` - Fetch all books with given status
- `book_parser(book_html, date, status)` - Parse single book from HTML
- `try_get_book_link(link)` - Validate book link format

**Data Flow:**
```
User Profile URL → BookLoader → page_loader → HTML → parser → List[Book]
```

**Issues:**
- ❌ Depends on `AppContext` (tight coupling)
- ❌ Silent exception handling (skips pages on error)
- ❌ No retry logic for network failures
- ❌ No type hints

#### 3.2 `Modules/QuoteLoader.py`

**Responsibility:** Fetch and parse quote data from LiveLib

**Key Methods:**
- `get_quotes()` - Fetch all quotes
- `quote_parser(quote_html)` - Parse single quote from HTML
- `get_quote_text(card)` - Extract quote text (multiple fallback selectors)
- `save_quotes(new_quotes)` - Save to CSV or Excel (uses pandas)
- `format_quote_text(text)` - Clean text for CSV

**Special Handling:**
- Detects truncated quotes (`!!!NOT_FULL###` marker)
- Fetches full quote text from individual quote page if truncated
- Uses pandas for CSV/Excel operations (inconsistent with books)

**Issues:**
- ❌ Inconsistent data handling (pandas vs. manual CSV)
- ❌ Magic string for state (`!!!NOT_FULL###`)
- ❌ No type hints
- ❌ Tight coupling to `AppContext`

---

### 4. Helpers (Shared Utilities)

#### 4.1 `Helpers/page_loader.py`

**Responsibility:** Download web pages (requests or Selenium)

**Functions:**
- `download_page(link, driver)` - Main entry point
- `__download_page_requests(link)` - Fast, no JavaScript
- `__download_page_silenium(link, driver)` - Full browser (for JS-heavy pages)

**Issues:**
- ❌ Typo in function name (`__download_page_silenium`)
- ❌ No retry logic
- ❌ Inconsistent error handling (print vs. logger)
- ❌ No timeout configuration

#### 4.2 `Helpers/livelib_parser.py`

**Responsibility:** HTML parsing utilities

**Functions:**
- `error_handler(where, raw)` - Log parsing errors
- `try_parse_month(raw_month)` - Russian month → number
- `is_last_page(page)` - Check if no more results
- `is_redirecting_page(page)` - Detect bot detection page
- `href_i(href, i)` - Generate paginated URL
- `date_parser(date)` - Parse date to ISO format
- `handle_xpath(html_node, request, i)` - Safe XPath wrapper
- `slash_add(left, right)` - URL path joiner

**Issues:**
- ❌ No type hints
- ❌ `error_handler` returns `None` silently
- ❌ No structured error types

#### 4.3 `Helpers/arguments.py`

**Responsibility:** CLI argument parsing

**Arguments:**
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `user` | str | (required) | LiveLib username |
| `--min_delay` | int | 60 | Min delay (seconds) |
| `--max_delay` | int | 30 | Max delay (seconds) |
| `--books_backup` | file | None | Custom books CSV path |
| `--quotes_backup` | file | None | Custom quotes CSV path |
| `--read_count` | int | ∞ | Limit read book pages |
| `--quote_count` | int | ∞ | Limit quote pages |
| `--rewrite_all` | flag | False | Overwrite existing files |
| `--skip` | str | None | Skip books/quotes |
| `--driver` | str | None | requests/silenium |

**Issues:**
- ❌ No validation of argument combinations
- ❌ Default delays inverted (min=60, max=30)
- ❌ No type hints

#### 4.4 `Helpers/csv_reader.py`

**Responsibility:** Read CSV files into model objects

**Functions:**
- `read_csv(file_path)` - Raw CSV → list of lists
- `convert_csv_to_books(cache)` - Raw rows → List[Book]
- `convert_csv_to_quotes(cache)` - Raw rows → List[Quote]
- `read_books_from_csv(file_name)` - File → List[Book]
- `read_quotes_from_csv(file_name)` - File → List[Quote]

**Issues:**
- ❌ No error handling for malformed CSV
- ❌ No type hints
- ❌ Silent header skip (assumes format)

#### 4.5 `Helpers/csv_writer.py`

**Responsibility:** Write model objects to CSV

**Functions:**
- `save_books(books, file_path)` - Append books to CSV
- `save_quotes(quotes, file_path)` - Append quotes to CSV

**Format:**
- Tab-separated values (`\t`)
- Header row on first write
- UTF-8 encoding
- Append mode (incremental updates)

**Issues:**
- ❌ No atomic writes (partial writes on crash)
- ❌ No type hints
- ❌ Inconsistent with QuoteLoader (which uses pandas)

#### 4.6 Data Models

**`Helpers/book.py` - Book Model**
```python
class Book:
    def __init__(self, link, status, name=None, author=None, 
                 rating=None, date=None):
        self.link = link        # str: LiveLib book URL
        self.status = status    # str: read/reading/wish
        self.name = name        # str: Book title
        self.author = author    # str: Comma-separated authors
        self.rating = rating    # str: User rating (if read)
        self.date = date        # str: ISO date (YYYY-MM-DD)
```

**`Helpers/quote.py` - Quote Model**
```python
class Quote:
    def __init__(self, link, text, book):
        self.link = link        # str: LiveLib quote URL
        self.text = text        # str: Quote text
        self.book = book        # Book: Associated book
```

**Issues:**
- ❌ No validation in constructors
- ❌ No `__eq__` / `__hash__` (inefficient deduplication)
- ❌ No type hints
- ❌ No `__str__` documentation (implicit CSV format)

---

## Data Flow

### Book Export Flow

```
┌──────────────┐
│ CLI: username│
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. export.py validates user profile exists                   │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. BookLoader.get_books('read')                              │
│    For each page (until last page or read_count):            │
│      a. wait_for_delay()                                     │
│      b. download_page(url)                                   │
│      c. Parse HTML with lxml                                 │
│      d. Extract book elements via XPath                      │
│      e. book_parser() → Book object                          │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Repeat for 'reading' and 'wish' statuses                  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. Compare with existing CSV (if not rewrite_all)            │
│    read_books_from_csv() → existing_books                    │
│    get_new_items(existing, all_books) → new_books            │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. save_books(new_books, file_path)                          │
│    - Append mode                                             │
│    - Tab-separated                                           │
│    - Header if new file                                      │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. Output: backup_<username>_book.csv                        │
└──────────────────────────────────────────────────────────────┘
```

### Quote Export Flow

```
┌──────────────┐
│ CLI: username│
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 1. QuoteLoader.get_quotes()                                  │
│    For each page (until last page or quote_count):           │
│      a. wait_for_delay()                                     │
│      b. download_page(url)                                   │
│      c. Parse HTML with lxml                                 │
│      d. Extract quote elements via XPath                     │
│      e. quote_parser() → Quote object                        │
│      f. If truncated (read-more link):                       │
│         - Fetch individual quote page                        │
│         - Extract full text                                  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. save_quotes(quotes)                                       │
│    - Load existing (pandas)                                  │
│    - Update or append                                        │
│    - Save to CSV or Excel                                    │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Output: backup_<username>_quote.csv                       │
└──────────────────────────────────────────────────────────────┘
```

---

## External Dependencies

### Runtime Dependencies (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | Latest | HTTP requests (fast, no JS) |
| `lxml` | Latest | HTML parsing |
| `selenium` | Latest | Browser automation (JS-heavy pages) |
| `pandas` | Latest | CSV/Excel operations (quotes only) |

### Development Dependencies (`requirements-dev.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | Latest | Testing framework |
| `pytest-cov` | Latest | Coverage reporting |

### External Services

| Service | Purpose | Authentication |
|---------|---------|----------------|
| LiveLib.ru | Web scraping | None (public pages) |

**Rate Limiting:**
- Configurable delay between requests (default: 5-15 seconds random)
- Bot detection risk if delays too short
- 404 page indicates potential ban

---

## Testing Architecture

### Test Structure

```
tests/
├── fixtures/
│   ├── __init__.py
│   └── mock_html.py          # Mock HTML for unit tests
├── __init__.py
├── test_app_context.py       # AppContext tests
├── test_book.py              # Book model tests
├── test_csv_reader.py        # CSV reading tests
├── test_csv_writer.py        # CSV writing tests
├── test_export.py            # Main entry point tests
├── test_integration.py       # End-to-end tests
├── test_livelib_parser.py    # Parser utility tests
├── test_quote.py             # Quote model tests
└── README.md                 # Testing guide
```

### Test Coverage

| Metric | Value |
|--------|-------|
| Total Tests | 119 |
| Pass Rate | 100% |
| Overall Coverage | ~50% |
| Core Models | 100% |
| I/O Operations | 100% |

### Test Types

1. **Unit Tests** - Individual functions/classes
2. **Integration Tests** - Full workflow (mock HTTP)
3. **Fixture-based** - Mock HTML responses

---

## Known Issues & Technical Debt

### Critical Issues

1. **Inconsistent Error Handling**
   - Bare `except Exception` in loaders
   - Silent failures (pages skipped without notification)
   - Mixed logging (print vs. logger)

2. **Global State**
   - `app_context` is global mutable state
   - Hard to test in isolation
   - Thread-unsafe

3. **No Retry Logic**
   - Network failures cause data loss
   - No exponential backoff
   - No circuit breaker

### Medium Priority

4. **Type Safety**
   - No type hints anywhere
   - IDE autocomplete doesn't work
   - Runtime errors only

5. **Data Validation**
   - No validation in model constructors
   - Invalid data can be saved to CSV
   - No schema enforcement

6. **Inconsistent Data Handling**
   - Books: manual CSV append
   - Quotes: pandas DataFrame
   - Different error handling paths

### Low Priority

7. **Code Style**
   - Typos (`silenium` vs `selenium`)
   - Russian comments (fine, but inconsistent)
   - Magic strings (`!!!NOT_FULL###`)

8. **Performance**
   - Sequential page downloads
   - No async/await
   - No connection pooling

---

## Future Architecture (Post-Refactoring)

### Proposed Changes

1. **Configuration Management**
   - New `BackupConfig` dataclass
   - Validation on initialization
   - No global state

2. **Type Safety**
   - Type hints throughout
   - Static type checking (mypy)
   - Better IDE support

3. **Error Handling**
   - Specific exception types
   - Retry logic with backoff
   - User notifications on failures

4. **Data Validation**
   - Model validation in `__post_init__`
   - URL format validation
   - Status enum instead of strings

5. **Testing**
   - Update tests for new config
   - Increase coverage to 80%+
   - Add property-based testing

### Migration Path

1. Create `BackupConfig` (backward compatible)
2. Add type hints (non-breaking)
3. Improve error handling (transparent)
4. Refactor loaders (requires test updates)
5. Deprecate `AppContext` (gradual migration)

---

## Glossary

| Term | Definition |
|------|------------|
| **AppContext** | Global application state object (being deprecated) |
| **BookLoader** | Module for fetching/parsing book data |
| **QuoteLoader** | Module for fetching/parsing quote data |
| **LiveLib.ru** | Russian book social network (target service) |
| **Incremental Mode** | Only save new/changed items (default) |
| **Rewrite Mode** | Overwrite entire CSV (`-R` flag) |

---

## References

- [README.md](README.md) - User documentation
- [TEST_SUITE_SUMMARY.md](TEST_SUITE_SUMMARY.md) - Test coverage details
- [tests/README.md](tests/README.md) - Testing guide
- [GitHub Repository](https://github.com/pplevar/livelib-backup)

---

**Document Status:** Draft  
**Next Review:** After refactoring PR merge  
**Maintainer:** @pplevar
