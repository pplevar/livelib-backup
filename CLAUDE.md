# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Livelib-backup is a Python web scraper that backs up user data from the Russian book portal Livelib.ru. It extracts book lists (read, reading, wish-to-read) and user quotes into CSV/Excel files without requiring authentication.

## Running the Application

### Setup
```bash
# Install dependencies
pip3 install -r requirements.txt  # Linux/macOS
py -m pip install -r requirements.txt  # Windows
```

### Basic Usage
```bash
# Export all data for a user
python3 export.py username  # Linux/macOS
python export.py username  # Windows

# Get help on all options
python export.py --help
```

### Common Command Options
```bash
# Custom output files
python export.py username --books_backup custom_books.csv --quotes_backup custom_quotes.xlsx

# Control delay between requests (to avoid bot detection)
python export.py username --min_delay 30 --max_delay 60

# Limit pages processed
python export.py username --read_count 5 --quote_count 10

# Rewrite files completely (instead of incremental update)
python export.py username -R

# Skip books or quotes
python export.py username --skip quotes  # only process books
python export.py username --skip books   # only process quotes

# Use Selenium driver (for JavaScript-rendered content)
python export.py username --driver selenium
```

## Architecture

### Entry Point
- `export.py` - Main script that orchestrates the scraping workflow

### Core Components

**AppContext** (`Modules/AppContext.py`)
- Shared configuration and state dataclass
- Manages user URLs, file paths, page limits, and rate limiting
- `wait_for_delay()` implements random delays (5-15 seconds default) to avoid bot detection

**BookLoader** (`Modules/BookLoader.py`)
- Scrapes book data from user's reading lists (read/reading/wish statuses)
- Parses book metadata: title, author(s), rating, completion date, link
- Handles pagination and validates book links (`/book/` or `/work/` URLs)

**QuoteLoader** (`Modules/QuoteLoader.py`)
- Scrapes user quotes from books
- Handles truncated quotes by fetching full quote pages when needed
- Saves to CSV (tab-separated) or Excel format with pandas
- Manages incremental updates to avoid duplicate quotes

### Helper Modules (`Helpers/`)

**Data Models**
- `book.py` - Book class with equality based on link
- `quote.py` - Quote class containing text and associated Book object

**Parsing**
- `livelib_parser.py` - XPath utilities and HTML parsing helpers
- `page_loader.py` - Dual-mode page fetching (requests or Selenium)

**I/O**
- `csv_reader.py` - Reads existing books from CSV files
- `csv_writer.py` - Appends new books to CSV files
- `arguments.py` - CLI argument parsing with validation

### Data Flow

1. **Initialization**: Parse arguments → validate user URL → configure AppContext
2. **Books**: Iterate through statuses (read/reading/wish) → scrape pages → merge with existing CSV → save
3. **Quotes**: Scrape quote pages → fetch full text for truncated quotes → merge with existing data → save
4. **Rate Limiting**: Random delays between requests via `wait_for_delay()`
5. **Incremental Updates**: New items identified via `get_new_items()` comparing links

### Key Design Patterns

**Dual Driver Support**: The scraper supports two modes:
- `requests` (default): Fast, lightweight HTTP requests
- `selenium`: For JavaScript-rendered content, waits for DOM elements

**Incremental Backup**: By default, appends only new items to existing CSV/Excel files. Use `-R` flag to force complete rewrite.

**Link-based Deduplication**: Books and quotes use their URLs as unique identifiers for equality checks.

**Error Resilience**: Individual page failures don't stop the entire scrape; script continues to next page.

## File Format

**Books CSV** (tab-separated):
```
Name    Author    Status    Rating    Date    Link
```

**Quotes CSV/Excel**:
```
Name    Author    Quote text    Book link    Quote link
```

## Development Notes

- The scraper respects bot detection by implementing random delays; adjust carefully with `--min_delay` and `--max_delay`
- XPath parsing expects specific Livelib HTML structure; site changes may break scraping
- Pandas DataFrames used for quote management; CSV for books uses custom writer
- Custom exception hierarchy (`Helpers/exceptions.py`) for better error handling
- Logging is centralized through `Helpers/logger_config.py`
