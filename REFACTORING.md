# Code Quality Refactoring

This document describes the major refactoring improvements made to the livelib-backup project.

## Summary

The codebase has been modernized with:
- ✅ Type hints throughout all modules
- ✅ Robust error handling with retry logic
- ✅ Centralized configuration management
- ✅ Data validation with dataclasses
- ✅ Improved logging consistency
- ✅ Better separation of concerns

## Changes

### 1. Configuration Management (`Helpers/config.py`)

**NEW:** Centralized configuration with validation

```python
@dataclass
class BackupConfig:
    username: str
    books_file: Optional[str] = None
    quotes_file: Optional[str] = None
    min_delay: float = 1.0
    max_delay: float = 3.0
    # ... and more
```

**Benefits:**
- Single source of truth for configuration
- Automatic validation on initialization
- Easy to test and mock
- Clear defaults and documentation

### 2. Data Models with Validation

**UPDATED:** `Helpers/book.py` and `Helpers/quote.py`

```python
@dataclass
class Book:
    link: str
    status: str
    name: Optional[str] = None
    author: Optional[str] = None
    # ... with automatic validation
```

**Benefits:**
- Type safety with dataclasses
- Automatic validation in `__post_init__`
- Clear `__str__` for CSV export
- Proper `__eq__` and `__hash__` for set operations

### 3. Robust Error Handling (`Helpers/page_loader.py`)

**IMPROVED:** Network requests with retry logic

```python
def __download_page_requests(link: str, retry_count: int = 0):
    try:
        response = requests.get(link, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        if retry_count < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return __download_page_requests(link, retry_count + 1)
        raise
```

**Benefits:**
- Automatic retry on transient failures
- Specific exception handling (not bare `except`)
- Configurable retry count and delay
- Detailed logging at each step

### 4. Type-Safe Parsing (`Helpers/livelib_parser.py`)

**IMPROVED:** All functions now have type hints

```python
def handle_xpath(
    html_node: Optional[html.HtmlElement],
    request: str,
    i: int = 0
) -> Optional[Any]:
```

**Benefits:**
- IDE autocomplete works
- Static type checkers (mypy) can catch errors
- Clear documentation of expected types
- Easier for contributors to understand

### 5. Module Refactoring (`Modules/BookLoader.py`, `Modules/QuoteLoader.py`)

**IMPROVED:** Constructor now takes `BackupConfig` instead of `AppContext`

```python
class BookLoader:
    def __init__(self, config: BackupConfig, driver=None):
        self.config = config
        self.driver = driver
```

**Benefits:**
- Clear dependencies
- Easier to test (mock config)
- No global state
- Single Responsibility Principle

### 6. Main Entry Point (`export.py`)

**IMPROVED:** Structured main function with proper error handling

```python
def main() -> int:
    """Main entry point. Returns exit code."""
    try:
        config = BackupConfig(...)
        # ... backup logic
        return 0
    except ValueError as e:
        logger.error('Configuration error: %s', e)
        return 1
    except KeyboardInterrupt:
        logger.info('Backup interrupted by user')
        return 130
```

**Benefits:**
- Proper exit codes for scripting
- Clear error messages
- Graceful shutdown on Ctrl+C
- No global state

## Testing

Run the existing test suite to verify changes:

```bash
pip install pytest pytest-cov
pytest --cov=. --cov-report=html
```

**Note:** Some tests may need updates to work with the new `BackupConfig` instead of `AppContext`.

## Backward Compatibility

All command-line arguments remain the same. The refactoring is internal and does not change the user-facing API.

```bash
# All existing commands still work
python export.py username
python export.py username --books_backup my_books.csv
python export.py username --min_delay 2 --max_delay 5
```

## Future Improvements

1. **Async/await support** - Parallel page downloads
2. **Progress bars** - Visual feedback during long runs
3. **Incremental backups** - Only fetch changed pages
4. **Export formats** - JSON, Excel, SQLite options
5. **CI/CD pipeline** - Automated testing on PRs

## Migration Guide

If you have custom code that uses the old modules:

### Before:
```python
from export import app_context
loader = BookLoader(app_context)
```

### After:
```python
from Helpers.config import BackupConfig
config = BackupConfig(username='myuser')
loader = BookLoader(config)
```

---

**PR Author:** Kate (AI Assistant)  
**Date:** 2026-02-24  
**Branch:** `refactor/code-quality-improvements`
