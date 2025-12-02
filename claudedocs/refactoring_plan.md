# Livelib-Backup Refactoring Plan

**Generated**: 2025-12-02
**Focus**: Code Quality Improvements
**Project**: Livelib-Backup Web Scraper

---

## Executive Summary

This refactoring plan addresses code quality issues identified in the livelib-backup Python web scraper. The plan is organized by priority (Critical → Low) and focuses on improving maintainability, reducing technical debt, enforcing SOLID principles, and eliminating code smells.

**Key Metrics**:
- Total Python files analyzed: 15 (excluding tests and venv)
- Critical issues identified: 5
- High priority issues: 12
- Medium priority issues: 8
- Low priority issues: 6

---

## Table of Contents

1. [Critical Priority Issues](#1-critical-priority-issues)
2. [High Priority Issues](#2-high-priority-issues)
3. [Medium Priority Issues](#3-medium-priority-issues)
4. [Low Priority Issues](#4-low-priority-issues)
5. [Implementation Strategy](#5-implementation-strategy)
6. [Testing Requirements](#6-testing-requirements)

---

## 1. Critical Priority Issues

### 1.1 Swapped Min/Max Delay Default Values (BUG)

**Issue**: `arguments.py:21,26` - Default values for `--min_delay` (60) and `--max_delay` (30) are swapped.

**Why it matters**:
- Logic error causing incorrect delay behavior
- `wait_for_delay()` compensates with conditional check (AppContext.py:27-28)
- Confusing for users and developers
- Data integrity risk if delay logic fails

**Impact**: 🔴 High - Potential bot detection, incorrect rate limiting

**Affected files**:
- `Helpers/arguments.py`
- `Modules/AppContext.py`

**Proposed solution**:
```python
# arguments.py
arg_parser.add_argument('--min_delay',
                        type=int,
                        default=5,  # Changed from 60
                        help='minimum waiting time between two page loads (default: 5 seconds)')

arg_parser.add_argument('--max_delay',
                        type=int,
                        default=15,  # Changed from 30
                        help='maximum waiting time between two page loads (default: 15 seconds)')
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: Yes - users relying on current defaults will see different behavior

---

### 1.2 Global Module-Level AppContext Instance (ANTI-PATTERN)

**Issue**: `export.py:18` - Global mutable `app_context` instance violates dependency injection principles.

**Why it matters**:
- Violates Dependency Inversion Principle (SOLID)
- Makes testing difficult (shared state between tests)
- Hidden dependencies across modules
- Thread-unsafe for concurrent operations
- Circular import in `QuoteLoader.py:11` importing logger from export

**Impact**: 🔴 High - Testability, maintainability, extensibility

**Affected files**:
- `export.py`
- `Modules/QuoteLoader.py`
- `Modules/BookLoader.py`

**Proposed solution**:
```python
# Remove global app_context from export.py
# Pass app_context as parameter through dependency injection

def main():
    args = get_arguments()
    configure_logging()

    # Create context locally
    app_context = AppContext()

    # ... rest of logic

    if args.skip != 'books':
        bl = BookLoader(app_context)  # Already using DI
        # ...

    if args.skip != 'quotes':
        ql = QuoteLoader(app_context)  # Already using DI
        # ...
```

**Complexity**: Low
**Dependencies**: Fix circular import (1.3)
**Breaking changes**: No - internal refactoring only

---

### 1.3 Circular Import with Logger (ANTI-PATTERN)

**Issue**: `Modules/QuoteLoader.py:11`, `Helpers/livelib_parser.py:13`, `Helpers/page_loader.py:37` - Import logger from `export.py` creates circular dependency.

**Why it matters**:
- Fragile module coupling
- Import errors in certain execution contexts
- Violates Single Responsibility Principle
- Makes modules non-reusable outside of export.py

**Impact**: 🔴 High - Code organization, reusability

**Affected files**:
- `export.py`
- `Modules/QuoteLoader.py`
- `Helpers/livelib_parser.py`
- `Helpers/page_loader.py`

**Proposed solution**:
```python
# Create dedicated logging configuration module
# Helpers/logger_config.py
import logging

def get_logger(name):
    """Get configured logger instance"""
    return logging.getLogger(name)

def configure_logging(level=logging.INFO):
    """Configure logging format and level"""
    logging.basicConfig(
        format='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s',
        level=level
    )

# Usage in modules:
# from Helpers.logger_config import get_logger
# logger = get_logger(__name__)
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: No - internal refactoring only

---

### 1.4 Missing Error Handling in Critical Paths

**Issue**: Multiple locations with bare `except Exception` or inadequate error handling.

**Why it matters**:
- Silent failures hide bugs
- Poor user experience (unclear error messages)
- Difficult debugging
- Data loss potential

**Impact**: 🔴 High - Reliability, debugging, user experience

**Affected files**:
- `export.py:44` - Generic exception handling for user URL validation
- `Modules/BookLoader.py:29` - Silent continue on page download failure
- `Modules/QuoteLoader.py:33,49` - Generic exception with minimal context

**Proposed solution**:
```python
# Create custom exception hierarchy
# Helpers/exceptions.py
class LivelibError(Exception):
    """Base exception for livelib-backup"""
    pass

class NetworkError(LivelibError):
    """Network/connection related errors"""
    pass

class ParsingError(LivelibError):
    """HTML parsing errors"""
    pass

class UserNotFoundError(LivelibError):
    """User profile not found"""
    pass

# Usage in export.py:
try:
    response = requests.get(app_context.user_href)
    response.raise_for_status()
except requests.RequestException as ex:
    logger.error(f'Failed to access user profile: {app_context.user_href}')
    logger.error(f'Error: {ex}')
    logger.error('Please verify:')
    logger.error('  1. Username is correct')
    logger.error('  2. Internet connection is active')
    logger.error('  3. Livelib.ru is accessible')
    sys.exit(1)
```

**Complexity**: Medium
**Dependencies**: None
**Breaking changes**: No - internal improvement

---

### 1.5 Inconsistent Driver Typo: "silenium" vs "selenium"

**Issue**: Intentional typo `silenium` used throughout codebase instead of `selenium`.

**Why it matters**:
- Confusing for new developers
- Looks unprofessional
- Mentioned as intentional in CLAUDE.md but creates technical debt
- Could cause issues if Selenium library expectations change

**Impact**: 🟡 Medium-High - Code clarity, professionalism

**Affected files**:
- `export.py:36`
- `Helpers/arguments.py:59`
- `Helpers/page_loader.py:8,30`
- Documentation references

**Proposed solution**:
```python
# Option 1: Fix typo everywhere (recommended)
if args.driver == 'selenium':  # Changed from 'silenium'
    app_context.driver = webdriver.Chrome()

# Option 2: Keep backward compatibility
DRIVER_ALIASES = {
    'selenium': 'selenium',
    'silenium': 'selenium',  # Support old typo
    'requests': None
}
driver_type = DRIVER_ALIASES.get(args.driver, None)
```

**Complexity**: Low
**Dependencies**: Update documentation
**Breaking changes**: Yes - users using `--driver silenium` will need to update

---

## 2. High Priority Issues

### 2.1 Violation of Single Responsibility Principle - export.py

**Issue**: `export.py` handles too many responsibilities: CLI parsing, logging config, driver setup, orchestration, file I/O, URL validation.

**Why it matters**:
- Hard to test individual components
- Difficult to reuse logic
- Violates SRP (SOLID)
- Poor separation of concerns

**Impact**: 🟡 High - Maintainability, testability

**Affected files**:
- `export.py`

**Proposed solution**:
```python
# Refactor into focused modules:

# Modules/Orchestrator.py
class BackupOrchestrator:
    """Coordinates the backup workflow"""
    def __init__(self, context: AppContext):
        self.context = context

    def backup_books(self, statuses):
        """Orchestrate book backup process"""
        pass

    def backup_quotes(self):
        """Orchestrate quote backup process"""
        pass

# Modules/DriverFactory.py
class DriverFactory:
    """Creates appropriate page loader drivers"""
    @staticmethod
    def create_driver(driver_type: str):
        if driver_type == 'selenium':
            return webdriver.Chrome()
        return None

# export.py becomes thin CLI wrapper
def main():
    args = get_arguments()
    configure_logging()

    context = create_context(args)
    orchestrator = BackupOrchestrator(context)

    if args.skip != 'books':
        orchestrator.backup_books(['read', 'reading', 'wish'])

    if args.skip != 'quotes':
        orchestrator.backup_quotes()
```

**Complexity**: Medium
**Dependencies**: 1.2 (AppContext DI)
**Breaking changes**: No - internal refactoring

---

### 2.2 Missing Input Validation

**Issue**: User inputs not validated before use.

**Why it matters**:
- Security vulnerabilities (path traversal)
- Poor error messages for invalid inputs
- Runtime failures instead of early validation

**Impact**: 🟡 High - Security, UX

**Affected files**:
- `Helpers/arguments.py`
- `export.py`

**Proposed solution**:
```python
# Helpers/validators.py
import re
import os
from pathlib import Path

def validate_username(username: str) -> str:
    """Validate livelib username format"""
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")

    # Username should be alphanumeric, dash, underscore
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValueError(f"Invalid username format: {username}")

    return username.strip()

def validate_file_path(filepath: str, must_exist: bool = False) -> str:
    """Validate file path for security"""
    path = Path(filepath).resolve()

    # Prevent path traversal
    cwd = Path.cwd()
    if not str(path).startswith(str(cwd)):
        raise ValueError(f"File path must be within current directory: {filepath}")

    if must_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    return str(path)

def validate_delay(min_delay: int, max_delay: int) -> tuple[int, int]:
    """Validate delay range"""
    if min_delay < 0 or max_delay < 0:
        raise ValueError("Delays must be non-negative")

    if min_delay > max_delay:
        raise ValueError(f"min_delay ({min_delay}) cannot exceed max_delay ({max_delay})")

    return min_delay, max_delay

# Use in arguments.py:
args = arg_parser.parse_args()

# Validate inputs
args.user = validate_username(args.user)
args.min_delay, args.max_delay = validate_delay(args.min_delay, args.max_delay)

if args.books_backup:
    args.books_backup = validate_file_path(args.books_backup)
if args.quotes_backup:
    args.quotes_backup = validate_file_path(args.quotes_backup)
```

**Complexity**: Medium
**Dependencies**: None
**Breaking changes**: No - adds validation

---

### 2.3 Hardcoded Magic Strings and URLs

**Issue**: Magic strings scattered throughout code: URLs, XPath expressions, file extensions, status values.

**Why it matters**:
- DRY violation
- Hard to update consistently
- No single source of truth
- Testing difficulty

**Impact**: 🟡 High - Maintainability

**Affected files**:
- `export.py:39` - Base URL
- `Helpers/utils.py:16` - Domain URL (duplicate)
- `Modules/QuoteLoader.py:45,78,120,121,140` - File extensions, magic values
- `BookLoader.py:86` - URL patterns

**Proposed solution**:
```python
# Helpers/constants.py
"""Application constants and configuration"""

# URLs
LIVELIB_BASE_URL = 'https://www.livelib.ru'
LIVELIB_READER_PATH = '/reader'

# Book statuses
BOOK_STATUS_READ = 'read'
BOOK_STATUS_READING = 'reading'
BOOK_STATUS_WISH = 'wish'
BOOK_STATUSES = [BOOK_STATUS_READ, BOOK_STATUS_READING, BOOK_STATUS_WISH]

# URL patterns
BOOK_URL_PATTERNS = ['/book/', '/work/']
QUOTE_URL_PATTERN = '/quote/'

# File formats
FILE_EXT_CSV = 'csv'
FILE_EXT_XLSX = 'xlsx'
SUPPORTED_FILE_EXTENSIONS = [FILE_EXT_CSV, FILE_EXT_XLSX]

# Special markers
TRUNCATED_QUOTE_MARKER = '!!!NOT_FULL###'

# Default values
DEFAULT_MIN_DELAY = 5
DEFAULT_MAX_DELAY = 15
DEFAULT_WAIT_TIMEOUT = 60

# CSV/Excel columns
BOOK_COLUMNS = ['Name', 'Author', 'Status', 'My Rating', 'Date', 'Link']
QUOTE_COLUMNS = ['Name', 'Author', 'Quote text', 'Book link', 'Quote link']

# XPath expressions (if they become reusable)
class XPath:
    """Commonly used XPath expressions"""
    BOOKLIST = './/div[@id="booklist"]/div'
    BOOK_DATA = './/div/div/div[@class="brow-data"]/div'
    QUOTE_CARD = './/div[@class="lenta-card"]'
    # ... etc

# Usage:
from Helpers.constants import LIVELIB_BASE_URL, BOOK_STATUSES

for status in BOOK_STATUSES:
    books = bl.get_books(status)
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: No - internal refactoring

---

### 2.4 Inconsistent Error Reporting

**Issue**: Mix of `logger.error()`, `print()` statements, and inconsistent error formats.

**Why it matters**:
- Inconsistent UX
- Some errors bypass logging configuration
- Hard to filter/analyze logs
- No structured error handling

**Impact**: 🟡 High - UX, debugging

**Affected files**:
- `Helpers/page_loader.py:19,23,26` - Uses print() instead of logger
- `Helpers/livelib_parser.py:58-60` - Uses print() for bot detection
- Mixed logger.error() and print() throughout

**Proposed solution**:
```python
# Replace all print() with logger calls
# Helpers/page_loader.py
def __download_page_requests(link):
    logger.debug(f'Downloading page: {link}')
    try:
        with requests.get(link) as data:
            content = data.content
            logger.debug(f'Successfully downloaded: {link}')
            return content
    except Exception as ex:
        logger.error(f'Failed to download page: {link}', exc_info=True)
        raise NetworkError(f'Download failed: {link}') from ex

# Helpers/livelib_parser.py
def is_redirecting_page(page):
    flag = bool(len(page.xpath('//div[@class="page-404"]')))
    if flag:
        logger.warning('Bot detection triggered - Livelib suspects automation')
        logger.warning('Reading stopped to avoid being blocked')
    return flag
```

**Complexity**: Low
**Dependencies**: 1.3 (Logger refactoring)
**Breaking changes**: No - internal improvement

---

### 2.5 No Configuration File Support

**Issue**: All configuration via CLI arguments, no config file option.

**Why it matters**:
- Repetitive for regular users
- Can't save preset configurations
- Limited environment-specific settings
- No easy way to manage multiple user backups

**Impact**: 🟡 High - UX, usability

**Affected files**:
- `Helpers/arguments.py`
- `export.py`

**Proposed solution**:
```python
# Add support for config files (YAML/JSON)
# config.example.yaml
users:
  - username: user1
    books_backup: backups/user1_books.csv
    quotes_backup: backups/user1_quotes.xlsx

defaults:
  min_delay: 5
  max_delay: 15
  driver: requests

# Helpers/config_loader.py
import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class BackupConfig:
    username: str
    books_backup: str = None
    quotes_backup: str = None
    min_delay: int = 5
    max_delay: int = 15
    driver: str = 'requests'

    @classmethod
    def from_yaml(cls, filepath: str):
        """Load configuration from YAML file"""
        with open(filepath) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_args(cls, args):
        """Create from CLI arguments"""
        return cls(
            username=args.user,
            books_backup=args.books_backup,
            # ... map all args
        )

# arguments.py - add config file option
arg_parser.add_argument('-c', '--config',
                        type=str,
                        help='path to YAML configuration file')
```

**Complexity**: Medium
**Dependencies**: New dependency: PyYAML (optional)
**Breaking changes**: No - additive feature

---

### 2.6 Missing Type Hints

**Issue**: No type hints throughout codebase (except AppContext dataclass).

**Why it matters**:
- Reduced IDE support (autocomplete, refactoring)
- No static type checking
- Harder to understand function contracts
- Modern Python best practice

**Impact**: 🟡 High - Developer experience, maintainability

**Affected files**: All `.py` files

**Proposed solution**:
```python
# Add comprehensive type hints
# Helpers/book.py
from typing import Optional

class Book:
    def __init__(
        self,
        link: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
        author: Optional[str] = None,
        rating: Optional[str] = None,
        date: Optional[str] = None
    ) -> None:
        self.name: str = handle_none(name)
        self.author: str = handle_none(author)
        # ...

    def __str__(self) -> str:
        return '%s\t%s\t%s\t%s\t%s\t%s' % (...)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.link == other.link

    def to_list(self) -> list[str]:
        return list(self.__dict__.values())

# Helpers/livelib_parser.py
from lxml import etree
from typing import Optional

def error_handler(where: str, raw: etree._Element) -> None:
    """Handle parsing errors"""
    ...

def date_parser(date: str) -> Optional[str]:
    """Convert date to YYYY-MM-DD format"""
    ...

# Enable mypy checking
# Add to project root: mypy.ini
[mypy]
python_version = 3.13
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

**Complexity**: Medium
**Dependencies**: None (mypy optional for CI)
**Breaking changes**: No - additive improvement

---

### 2.7 Duplication in CSV/Excel Handling

**Issue**: `QuoteLoader.save_quotes()` duplicates logic for CSV vs Excel handling instead of using strategy pattern.

**Why it matters**:
- DRY violation
- Hard to add new formats
- Duplication across CSV reader/writer modules
- Violates Open/Closed Principle

**Impact**: 🟡 High - Extensibility, maintainability

**Affected files**:
- `Modules/QuoteLoader.py:112-146`
- `Helpers/csv_writer.py`
- `Helpers/csv_reader.py`

**Proposed solution**:
```python
# Create strategy pattern for file formats
# Helpers/file_handlers.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Protocol
from pathlib import Path

class FileHandler(ABC):
    """Abstract base for file format handlers"""

    @abstractmethod
    def read(self, filepath: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def write(self, df: pd.DataFrame, filepath: str) -> None:
        pass

    @abstractmethod
    def format_text(self, text: str) -> str:
        """Format text for this file type"""
        pass

class CSVHandler(FileHandler):
    SEPARATOR = '\t'

    def read(self, filepath: str) -> pd.DataFrame:
        if not Path(filepath).exists():
            return pd.DataFrame()
        return pd.read_csv(filepath, sep=self.SEPARATOR)

    def write(self, df: pd.DataFrame, filepath: str) -> None:
        df.to_csv(filepath, sep=self.SEPARATOR, index=False)

    def format_text(self, text: str) -> str:
        # Remove tabs and newlines for CSV
        return text.replace('\t', ' ').replace('\n', ' ')

class ExcelHandler(FileHandler):
    def read(self, filepath: str) -> pd.DataFrame:
        if not Path(filepath).exists():
            return pd.DataFrame()
        return pd.read_excel(filepath)

    def write(self, df: pd.DataFrame, filepath: str) -> None:
        df.to_excel(filepath, index=False)

    def format_text(self, text: str) -> str:
        # Excel preserves formatting
        return text

class FileHandlerFactory:
    """Factory for creating file handlers"""
    _handlers = {
        'csv': CSVHandler,
        'xlsx': ExcelHandler,
    }

    @classmethod
    def get_handler(cls, filepath: str) -> FileHandler:
        ext = Path(filepath).suffix[1:]  # Remove leading dot
        handler_class = cls._handlers.get(ext)
        if not handler_class:
            raise ValueError(f'Unsupported file format: {ext}')
        return handler_class()

# Usage in QuoteLoader:
def save_quotes(self, new_quotes):
    handler = FileHandlerFactory.get_handler(self.ac.quote_file)

    if self.ac.rewrite_all and Path(self.ac.quote_file).exists():
        Path(self.ac.quote_file).unlink()
        logger.info(f'Cleared existing file: {self.ac.quote_file}')

    quotes_df = handler.read(self.ac.quote_file)
    if quotes_df.empty:
        quotes_df = pd.DataFrame(columns=QUOTE_COLUMNS)

    for quote in new_quotes:
        if (quotes_df['Quote link'] == quote.link).any():
            quotes_df.loc[quotes_df['Quote link'] == quote.link, 'Quote text'] = quote.text
        else:
            quotes_df.loc[len(quotes_df)] = [
                quote.book.name,
                quote.book.author,
                handler.format_text(quote.text),
                quote.book.link,
                quote.link
            ]

    handler.write(quotes_df, self.ac.quote_file)
    logger.info(f'Quotes saved to {self.ac.quote_file}')
```

**Complexity**: Medium
**Dependencies**: 2.3 (Constants)
**Breaking changes**: No - internal refactoring

---

### 2.8 Weak Equality Implementation in Book/Quote

**Issue**: `Book.__eq__` and `Quote.__eq__` don't check type, violating Liskov Substitution Principle.

**Why it matters**:
- Incorrect behavior when comparing with non-Book/Quote objects
- Could cause bugs in collections (sets, dicts)
- Violates Python data model best practices

**Impact**: 🟡 Medium - Correctness

**Affected files**:
- `Helpers/book.py:16-20`
- `Helpers/quote.py:14-18`

**Proposed solution**:
```python
# Helpers/book.py
def __eq__(self, other: object) -> bool:
    if not isinstance(other, Book):
        return NotImplemented  # Let Python handle comparison
    return self.link == other.link

def __hash__(self) -> int:
    """Make Book hashable for use in sets/dicts"""
    return hash(self.link)

# Same for Quote class
def __eq__(self, other: object) -> bool:
    if not isinstance(other, Quote):
        return NotImplemented
    return self.link == other.link

def __hash__(self) -> int:
    return hash(self.link)
```

**Complexity**: Low
**Dependencies**: 2.6 (Type hints)
**Breaking changes**: No - fixes bug

---

### 2.9 No Retry Logic for Network Operations

**Issue**: Network failures immediately skip pages without retry.

**Why it matters**:
- Transient network issues cause data loss
- Poor resilience
- No exponential backoff
- Users may need to re-run entire process

**Impact**: 🟡 High - Reliability, UX

**Affected files**:
- `Modules/BookLoader.py:27-32`
- `Modules/QuoteLoader.py:31-36,47-51`
- `Helpers/page_loader.py`

**Proposed solution**:
```python
# Helpers/retry.py
from functools import wraps
import time
import logging
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retrying operations with exponential backoff"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f'{func.__name__} failed after {max_attempts} attempts')
                        raise

                    logger.warning(
                        f'{func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}'
                    )
                    logger.info(f'Retrying in {current_delay:.1f}s...')
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator

# Usage in page_loader.py
from Helpers.retry import retry
from Helpers.exceptions import NetworkError

@retry(max_attempts=3, delay=2.0, exceptions=(NetworkError, requests.RequestException))
def __download_page_requests(link: str) -> str:
    logger.debug(f'Downloading: {link}')
    try:
        response = requests.get(link, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.RequestException as ex:
        raise NetworkError(f'Failed to download {link}') from ex
```

**Complexity**: Medium
**Dependencies**: 1.4 (Custom exceptions)
**Breaking changes**: No - improves reliability

---

### 2.10 Missing Progress Indicators

**Issue**: No progress bars or completion estimates for long-running operations.

**Why it matters**:
- Poor UX for large backups
- Users don't know if script is working or stuck
- No ETA for completion
- Anxiety-inducing for multi-hour operations

**Impact**: 🟡 Medium - UX

**Affected files**:
- `Modules/BookLoader.py`
- `Modules/QuoteLoader.py`

**Proposed solution**:
```python
# Add tqdm for progress bars
# requirements.txt
# Add: tqdm==4.66.1

# Modules/BookLoader.py
from tqdm import tqdm

def get_books(self, status):
    books = []
    href = slash_add(self.ac.user_href, status)

    # Use tqdm for progress
    pbar = tqdm(
        desc=f'Scraping {status} books',
        unit='page',
        total=self.ac.page_count if self.ac.page_count != math.inf else None
    )

    page_idx = 1
    while page_idx <= self.ac.page_count:
        self.ac.wait_for_delay()

        try:
            page = html.fromstring(download_page(href_i(href, page_idx), self.ac.driver))
        except Exception:
            pbar.update(1)
            continue
        finally:
            page_idx += 1
            pbar.update(1)

        if is_last_page(page) or is_redirecting_page(page):
            break

        # ... process books
        pbar.set_postfix({'books': len(books)})

    pbar.close()
    return books
```

**Complexity**: Low
**Dependencies**: New dependency: tqdm
**Breaking changes**: No - additive feature

---

### 2.11 No Incremental Backup Verification

**Issue**: `get_new_items()` uses simple list comparison, no hash verification of existing items.

**Why it matters**:
- Can't detect corrupted existing data
- No verification that saved data matches scraped data
- Silent data corruption possible

**Impact**: 🟡 Medium - Data integrity

**Affected files**:
- `export.py:21-26`

**Proposed solution**:
```python
# Add data verification
# Helpers/verification.py
import hashlib
from typing import List, Tuple
from Helpers.book import Book

def verify_books(books: List[Book]) -> Tuple[int, List[Book]]:
    """Verify book data integrity and detect duplicates"""
    seen_links = set()
    valid_books = []
    duplicate_count = 0

    for book in books:
        if not book.link:
            logger.warning(f'Book missing link: {book.name}')
            continue

        if book.link in seen_links:
            duplicate_count += 1
            logger.debug(f'Duplicate book detected: {book.link}')
            continue

        seen_links.add(book.link)
        valid_books.append(book)

    return duplicate_count, valid_books

def compute_backup_hash(filepath: str) -> str:
    """Compute hash of backup file for integrity checking"""
    if not Path(filepath).exists():
        return ''

    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

# Save hash alongside backup
# backup_user_books.csv.sha256
```

**Complexity**: Medium
**Dependencies**: None
**Breaking changes**: No - additive feature

---

### 2.12 Missing Cleanup for Selenium Driver

**Issue**: Chrome WebDriver not properly closed on exit or error.

**Why it matters**:
- Resource leak (browser processes)
- Multiple zombie processes after errors
- System resource exhaustion on repeated runs

**Impact**: 🟡 High - Resource management

**Affected files**:
- `export.py:37`
- No cleanup anywhere

**Proposed solution**:
```python
# export.py - Use context manager
from contextlib import contextmanager

@contextmanager
def get_driver(driver_type: str):
    """Context manager for driver lifecycle"""
    driver = None
    try:
        if driver_type == 'selenium':
            driver = webdriver.Chrome()
        yield driver
    finally:
        if driver:
            logger.info('Closing browser driver')
            driver.quit()

# Usage:
def main():
    args = get_arguments()
    configure_logging()

    with get_driver(args.driver) as driver:
        app_context = AppContext()
        app_context.driver = driver

        # ... rest of logic

    # Driver automatically cleaned up
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: No - internal refactoring

---

## 3. Medium Priority Issues

### 3.1 Unclear Variable Naming

**Issue**: Inconsistent and unclear variable names.

**Why it matters**:
- Reduced code readability
- Harder for new contributors
- Cognitive overhead

**Impact**: 🟠 Medium - Readability

**Examples**:
- `export.py:18` - `app_context` vs `ac` inconsistency
- `livelib_parser.py:24` - `dict` shadows builtin
- `BookLoader.py:11` - `ac` abbreviation unclear
- `livelib_parser.py:79` - `m` for match result

**Proposed solution**:
```python
# Use descriptive names consistently
# Bad:
dict = defaultdict(...)
m = re.search(...)
ac = app_context

# Good:
month_mapping = defaultdict(...)
match = re.search(...)
context = app_context  # or just use app_context everywhere
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: No - internal refactoring

---

### 3.2 Russian Comments in Code

**Issue**: Mix of Russian and English comments/docstrings.

**Why it matters**:
- Inconsistent for international contributors
- Harder to maintain
- IDE/tool support may be limited

**Impact**: 🟠 Medium - Maintainability, collaboration

**Affected files**: All files with Russian docstrings

**Proposed solution**:
```python
# Translate all comments to English
# Before:
def wait_for_delay(self) -> None:
    """
    Останавливает программу на некоторое число секунд. Нужна, чтобы сайт не распознал в нас бота
    """

# After:
def wait_for_delay(self) -> None:
    """
    Pause program execution for random duration.
    Prevents bot detection by mimicking human browsing patterns.
    """
```

**Complexity**: Low (tedious)
**Dependencies**: None
**Breaking changes**: No - documentation only

---

### 3.3 No Data Classes for Configuration

**Issue**: Dictionary/argument passing instead of structured configuration objects.

**Why it matters**:
- Error-prone (typos in dict keys)
- No IDE autocomplete
- No type safety

**Impact**: 🟠 Medium - Developer experience

**Affected files**:
- Multiple modules passing primitive types

**Proposed solution**:
```python
# Use dataclasses for structured configuration
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ScraperConfig:
    """Configuration for scraping operations"""
    user_href: str
    min_delay: int = 5
    max_delay: int = 15
    driver_type: str = 'requests'
    skip: Optional[str] = None

@dataclass
class BackupConfig:
    """Configuration for backup file management"""
    book_file: str
    quote_file: str
    rewrite_all: bool = False

@dataclass
class LimitsConfig:
    """Configuration for processing limits"""
    page_count: int = math.inf
    quote_count: int = math.inf
    read_count: int = math.inf
```

**Complexity**: Medium
**Dependencies**: 2.6 (Type hints)
**Breaking changes**: No - internal refactoring

---

### 3.4 Inconsistent Return Types

**Issue**: Functions return different types based on conditions without clear documentation.

**Why it matters**:
- Confusing for users
- Type checking difficulties
- Potential runtime errors

**Impact**: 🟠 Medium - Type safety

**Examples**:
- `page_loader.py:6` - Returns `str or None` (old-style annotation)
- `livelib_parser.py:6` - Sometimes returns None, sometimes raises
- `BookLoader.py:51` - Can return Book or None

**Proposed solution**:
```python
# Use Optional type hints and be consistent
from typing import Optional

def download_page(link: str, driver: Optional[object] = None) -> str:
    """
    Download page content.

    Args:
        link: URL to download
        driver: Optional Selenium WebDriver

    Returns:
        Page content as string

    Raises:
        NetworkError: If download fails
    """
    # Always return str, raise on error (don't return None)

def book_parser(self, book_html, date: Optional[str], status: str) -> Optional[Book]:
    """
    Parse book from HTML node.

    Returns:
        Parsed Book object, or None if parsing fails
    """
```

**Complexity**: Low
**Dependencies**: 2.6 (Type hints)
**Breaking changes**: Potentially - if code relies on None returns

---

### 3.5 No Logging Levels Configuration

**Issue**: Everything logged at INFO level, no debug/verbose mode control.

**Why it matters**:
- Can't reduce verbosity for production
- Can't increase verbosity for debugging
- No control over log output

**Impact**: 🟠 Medium - Debugging, UX

**Affected files**:
- `export.py:30` - Hardcoded INFO level

**Proposed solution**:
```python
# Add verbosity control
# arguments.py
arg_parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='increase verbosity (-v for DEBUG, -vv for all)')

arg_parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='suppress all output except errors')

# export.py
def configure_logging(args) -> None:
    if args.quiet:
        level = logging.ERROR
    elif args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        format='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s',
        level=level
    )
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: No - additive feature

---

### 3.6 Missing Docstrings for Public Functions

**Issue**: Some functions lack docstrings, others have Russian-only docstrings.

**Why it matters**:
- Harder to generate documentation
- Reduced discoverability
- No IDE help text

**Impact**: 🟠 Medium - Documentation

**Affected files**: Multiple

**Proposed solution**:
```python
# Add comprehensive English docstrings in Google/NumPy style
def get_books(self, status: str) -> List[Book]:
    """
    Scrape books from user's library with specified status.

    Iterates through paginated book list, parsing each book's metadata
    and handling network errors gracefully.

    Args:
        status: Book status to filter ('read', 'reading', 'wish')

    Returns:
        List of Book objects with parsed metadata

    Raises:
        NetworkError: If unable to connect after retries
        ParsingError: If HTML structure is unexpected

    Example:
        >>> loader = BookLoader(context)
        >>> read_books = loader.get_books('read')
        >>> print(f'Found {len(read_books)} books')
    """
```

**Complexity**: Medium (tedious)
**Dependencies**: None
**Breaking changes**: No - documentation only

---

### 3.7 No Unit Tests for Parsers

**Issue**: Critical parsing logic (`livelib_parser.py`) has no unit tests.

**Why it matters**:
- Site changes will break silently
- No regression testing
- Refactoring is risky

**Impact**: 🟠 Medium - Quality assurance

**Affected files**:
- `Helpers/livelib_parser.py` - No tests found
- XPath expressions untested

**Proposed solution**:
```python
# tests/test_livelib_parser.py (needs expansion)
import pytest
from lxml import html
from Helpers.livelib_parser import (
    date_parser,
    try_parse_month,
    is_last_page,
    handle_xpath,
    slash_add
)

class TestDateParser:
    """Tests for date parsing functionality"""

    def test_parse_valid_date(self):
        assert date_parser('Январь 2024 г.') == '2024-01-01'
        assert date_parser('Декабрь 2023 г.') == '2023-12-01'

    def test_parse_invalid_date(self):
        assert date_parser('Invalid') is None
        assert date_parser('') is None

    @pytest.mark.parametrize('month,expected', [
        ('Январь', '01'),
        ('Февраль', '02'),
        ('Декабрь', '12'),
        ('Invalid', '01'),  # Default
    ])
    def test_month_parsing(self, month, expected):
        assert try_parse_month(month) == expected

class TestXPathHandling:
    """Tests for XPath utility functions"""

    def test_handle_xpath_found(self):
        html_str = '<div><span>Text</span></div>'
        node = html.fromstring(html_str)
        result = handle_xpath(node, './/span')
        assert result is not None
        assert result.text == 'Text'

    def test_handle_xpath_not_found(self):
        html_str = '<div></div>'
        node = html.fromstring(html_str)
        assert handle_xpath(node, './/span') is None
```

**Complexity**: Medium
**Dependencies**: Test fixtures with real HTML samples
**Breaking changes**: No - adds tests

---

### 3.8 Tight Coupling to Livelib HTML Structure

**Issue**: XPath expressions hardcoded throughout, no abstraction layer.

**Why it matters**:
- Site changes break entire app
- Hard to adapt to API changes
- No mocking capability for testing

**Impact**: 🟠 Medium - Maintainability, testability

**Affected files**:
- All parsers with XPath expressions

**Proposed solution**:
```python
# Create abstraction layer for selectors
# Helpers/selectors.py
from dataclasses import dataclass

@dataclass
class Selector:
    """XPath selector with metadata"""
    xpath: str
    description: str
    version: str = '1.0'  # Track when selector was last verified

class LivelibSelectors:
    """Centralized XPath selectors for Livelib.ru"""

    # Book list selectors
    BOOKLIST_CONTAINER = Selector(
        xpath='.//div[@id="booklist"]/div',
        description='Main container for book list items'
    )

    BOOK_DATA = Selector(
        xpath='.//div/div/div[@class="brow-data"]/div',
        description='Book metadata container'
    )

    BOOK_NAME = Selector(
        xpath='.//a[contains(@class, "brow-book-name")]',
        description='Book title link'
    )

    # Quote selectors
    QUOTE_CARD = Selector(
        xpath='.//div[@class="lenta-card"]',
        description='Quote card container'
    )

    # Page state selectors
    EMPTY_PAGE = Selector(
        xpath='//div[@class="with-pad"]',
        description='Empty page indicator'
    )

    ERROR_PAGE_404 = Selector(
        xpath='//div[@class="page-404"]',
        description='404/redirect page indicator'
    )

    @classmethod
    def get_all(cls) -> dict:
        """Get all selectors for validation/testing"""
        return {
            name: getattr(cls, name)
            for name in dir(cls)
            if isinstance(getattr(cls, name), Selector)
        }

# Usage in parsers:
from Helpers.selectors import LivelibSelectors

book_name = handle_xpath(book_data, LivelibSelectors.BOOK_NAME.xpath)
```

**Complexity**: Medium
**Dependencies**: 2.3 (Constants)
**Breaking changes**: No - internal refactoring

---

## 4. Low Priority Issues

### 4.1 Missing .gitignore Patterns

**Issue**: No comprehensive `.gitignore` for Python projects.

**Why it matters**:
- Risk of committing sensitive data
- Clutter in git status
- Larger repository size

**Impact**: 🟢 Low - Repository hygiene

**Proposed solution**:
```gitignore
# .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Project-specific
backup_*.csv
backup_*.xlsx
*.log
.DS_Store

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# MyPy
.mypy_cache/
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: No

---

### 4.2 No Pre-commit Hooks

**Issue**: No automated code quality checks before commits.

**Why it matters**:
- Inconsistent code style
- Manual linting required
- Quality issues slip through

**Impact**: 🟢 Low - Code quality automation

**Proposed solution**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

# Install: pip install pre-commit
# Setup: pre-commit install
```

**Complexity**: Low
**Dependencies**: New dev dependencies
**Breaking changes**: No

---

### 4.3 Inconsistent String Formatting

**Issue**: Mix of `%` formatting, `.format()`, and f-strings.

**Why it matters**:
- Inconsistent style
- Harder to maintain
- Modern f-strings more readable

**Impact**: 🟢 Low - Code style

**Examples**:
- `export.py:49` - `%` formatting
- `export.py:51` - f-string
- Mix throughout codebase

**Proposed solution**:
```python
# Standardize on f-strings (Python 3.6+)
# Before:
file = 'backup_%s_book.csv' % args.user
logger.info(f'Data from {url} will be saved to {file}')

# After:
file = f'backup_{args.user}_book.csv'
logger.info(f'Data from {url} will be saved to {file}')

# Use Black formatter to enforce consistency
```

**Complexity**: Low
**Dependencies**: Black formatter
**Breaking changes**: No - internal refactoring

---

### 4.4 No Makefile or Task Runner

**Issue**: No convenient commands for common tasks.

**Why it matters**:
- Harder for contributors
- No standardized workflow
- Manual command memorization

**Impact**: 🟢 Low - Developer experience

**Proposed solution**:
```makefile
# Makefile
.PHONY: help install test lint format clean run

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## Run tests
	pytest tests/ -v --cov=. --cov-report=html

lint:  ## Run linters
	flake8 Helpers/ Modules/ export.py
	mypy Helpers/ Modules/ export.py

format:  ## Format code
	black Helpers/ Modules/ export.py tests/
	isort Helpers/ Modules/ export.py tests/

clean:  ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/

run:  ## Run example backup (requires USER variable)
	python export.py $(USER)

# Usage:
# make install
# make test
# make run USER=someuser
```

**Complexity**: Low
**Dependencies**: None (make is standard)
**Breaking changes**: No

---

### 4.5 Missing Code of Conduct and Contributing Guide

**Issue**: No contribution guidelines for open source project.

**Why it matters**:
- Reduces contribution friction
- Sets expectations
- Professional project appearance

**Impact**: 🟢 Low - Open source readiness

**Proposed solution**:
```markdown
# CONTRIBUTING.md

## Development Setup

1. Clone repository
2. Install dependencies: `make install-dev`
3. Run tests: `make test`
4. Format code: `make format`

## Code Style

- Use Black for formatting (line length: 120)
- Use isort for import sorting
- Use flake8 for linting
- Add type hints to all functions
- Write docstrings in Google style

## Testing

- Write unit tests for all new functions
- Maintain >80% code coverage
- Use pytest fixtures for common setups

## Pull Requests

- Create feature branch from main
- Write descriptive commit messages
- Update tests and documentation
- Ensure all checks pass
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: No

---

### 4.6 Unused Methods in Book/Quote Classes

**Issue**: `add_name()`, `add_author()`, `add_book()` methods defined but unused.

**Why it matters**:
- Dead code
- Confusing API surface
- Maintenance burden

**Impact**: 🟢 Low - Code cleanliness

**Affected files**:
- `Helpers/book.py:25-29`
- `Helpers/quote.py:23-24`

**Proposed solution**:
```python
# Option 1: Remove if truly unused
# Search codebase: grep -r "add_name\|add_author\|add_book"
# If no usage found, delete methods

# Option 2: If needed for future extensibility, document
class Book:
    # ... existing code

    def add_name(self, name: str) -> None:
        """
        Update book name (used for enrichment from additional sources).

        Note: This method is reserved for future functionality.
        """
        self.name = name
```

**Complexity**: Low
**Dependencies**: None
**Breaking changes**: Yes if external code uses these methods

---

## 5. Implementation Strategy

### Phase 1: Critical Fixes (Week 1)
**Goal**: Fix bugs and critical design issues

1. **Day 1-2**: Fix swapped delay defaults (1.1)
2. **Day 2-3**: Refactor global AppContext and logger imports (1.2, 1.3)
3. **Day 4-5**: Improve error handling and create exception hierarchy (1.4)
4. **Day 5**: Decide on silenium typo fix approach (1.5)

**Success criteria**:
- All critical bugs resolved
- No circular imports
- Proper error messages for users
- Tests pass

---

### Phase 2: Architecture Improvements (Week 2-3)
**Goal**: Improve code structure and maintainability

1. **Week 2**:
   - Refactor export.py into focused modules (2.1)
   - Add input validation (2.2)
   - Create constants module (2.3)
   - Standardize logging (2.4)

2. **Week 3**:
   - Add type hints throughout (2.6)
   - Implement file handler strategy pattern (2.7)
   - Fix equality implementations (2.8)
   - Add Selenium cleanup (2.12)

**Success criteria**:
- Clear separation of concerns
- All public APIs type-hinted
- Mypy passes with strict mode
- No resource leaks

---

### Phase 3: Reliability Enhancements (Week 4)
**Goal**: Improve resilience and user experience

1. Add retry logic with exponential backoff (2.9)
2. Implement progress indicators (2.10)
3. Add data verification (2.11)
4. Create configuration file support (2.5)

**Success criteria**:
- Transient failures handled gracefully
- Users see progress updates
- Data integrity verified
- Config-based workflows supported

---

### Phase 4: Quality of Life (Week 5)
**Goal**: Developer experience and maintainability

1. Improve variable naming (3.1)
2. Translate Russian comments (3.2)
3. Add comprehensive docstrings (3.6)
4. Expand unit tests (3.7)
5. Create selector abstraction (3.8)

**Success criteria**:
- Code is self-documenting
- Test coverage >80%
- All comments in English
- Selectors centralized

---

### Phase 5: Polish (Week 6)
**Goal**: Professional finishing touches

1. Add pre-commit hooks (4.2)
2. Standardize string formatting (4.3)
3. Create Makefile (4.4)
4. Write contributing guide (4.5)
5. Clean up unused code (4.6)
6. Improve .gitignore (4.1)

**Success criteria**:
- Automated quality checks
- Easy contributor onboarding
- Professional project structure

---

## 6. Testing Requirements

### 6.1 Test Coverage Goals

**Target**: 80% overall coverage

**Critical paths** (require 100% coverage):
- `Helpers/livelib_parser.py` - All parsing functions
- `Helpers/book.py` - Book equality and string representation
- `Helpers/quote.py` - Quote equality and string representation
- `Modules/AppContext.py` - Delay logic
- `Helpers/arguments.py` - Validation functions

### 6.2 Test Categories

**Unit Tests**:
- All helper functions
- Data model methods
- Utility functions
- Validators

**Integration Tests**:
- BookLoader with mock HTML
- QuoteLoader with mock HTML
- File handler read/write cycles
- End-to-end backup workflow

**Regression Tests**:
- XPath selectors against real HTML samples
- Date parsing edge cases
- File format compatibility

### 6.3 Test Infrastructure

**Required**:
```python
# requirements-dev.txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-asyncio==0.21.1
black==23.12.1
isort==5.13.2
flake8==7.0.0
mypy==1.8.0
types-requests==2.31.0
pre-commit==3.6.0
```

**Test fixtures**:
```python
# tests/fixtures/html_samples.py
"""Real HTML samples from Livelib for regression testing"""

BOOK_LIST_PAGE = """
<!-- Actual HTML from livelib book list -->
"""

QUOTE_PAGE = """
<!-- Actual HTML from livelib quote page -->
"""

EMPTY_PAGE = """
<!-- HTML for last page detection -->
"""
```

### 6.4 Continuous Integration

**GitHub Actions workflow**:
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linters
        run: |
          black --check .
          isort --check-only .
          flake8 .
          mypy .

      - name: Run tests
        run: pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Summary

This refactoring plan addresses **31 identified issues** across 4 priority levels:

- **5 Critical** issues (bugs, anti-patterns, architectural flaws)
- **12 High Priority** issues (SOLID violations, missing features, quality gaps)
- **8 Medium Priority** issues (code clarity, documentation, coupling)
- **6 Low Priority** issues (tooling, polish, contributor experience)

**Estimated effort**: 6 weeks (1 developer, part-time)

**Key benefits after completion**:
- Elimination of all critical bugs
- SOLID-compliant architecture
- 80%+ test coverage
- Type-safe codebase
- Professional development workflow
- Easy contributor onboarding
- Resilient network operations
- Better user experience

**Breaking changes**:
- Delay default values (1.1)
- Silenium → Selenium rename (1.5) - optional
- Unused method removal (4.6) - if removed

**Backward compatibility**:
Most refactoring is internal. External API (CLI arguments, file formats) remains stable except where noted.
