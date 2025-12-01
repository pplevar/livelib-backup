# Test Suite for livelib-backup

Comprehensive test suite for the livelib-backup project covering unit tests, integration tests, and end-to-end workflows.

## Overview

This test suite ensures the reliability and correctness of the livelib-backup scraper through:
- Unit tests for individual components
- Integration tests for component interactions
- Mock HTML fixtures for realistic testing
- Coverage reporting

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures
├── test_book.py               # Unit tests for Book class
├── test_quote.py              # Unit tests for Quote class
├── test_app_context.py        # Unit tests for AppContext
├── test_livelib_parser.py     # Unit tests for HTML parsing utilities
├── test_csv_reader.py         # Unit tests for CSV reading
├── test_csv_writer.py         # Unit tests for CSV writing
├── test_export.py             # Unit tests for export.py functions
├── test_integration.py        # Integration tests for workflows
├── fixtures/
│   ├── __init__.py
│   └── mock_html.py           # Mock HTML responses
└── README.md                  # This file
```

## Running Tests

### Install Test Dependencies

First, ensure pytest and coverage tools are installed:

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_book.py -v

# Run specific test class
pytest tests/test_book.py::TestBook -v

# Run specific test
pytest tests/test_book.py::TestBook::test_book_equality_same_link -v
```

### Run Tests by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Categories

### Unit Tests

**Data Models** (`test_book.py`, `test_quote.py`)
- Book and Quote class initialization
- Equality and inequality operators
- String representation
- Helper functions (handle_none, add_livelib)
- URL normalization

**AppContext** (`test_app_context.py`)
- Initialization with defaults and custom values
- wait_for_delay functionality
- Delay calculation logic

**Parsing** (`test_livelib_parser.py`)
- Month name parsing (Russian to numeric)
- Date parsing and formatting
- XPath handling
- Page type detection (last page, 404)
- URL construction

**CSV I/O** (`test_csv_reader.py`, `test_csv_writer.py`)
- Reading books and quotes from CSV
- Writing books and quotes to CSV
- UTF-8 encoding handling
- Append vs. overwrite modes
- Header management

**Export Functions** (`test_export.py`)
- get_new_items deduplication
- Incremental backup logic

### Integration Tests

**Workflows** (`test_integration.py`)
- Complete book scraping workflow
- Complete quote scraping workflow
- Incremental backup updates
- Multi-status book handling
- Rewrite mode behavior
- Error handling
- Data consistency

## Fixtures

### Shared Fixtures (conftest.py)

- `app_context`: Pre-configured AppContext for testing
- `temp_csv_file`: Temporary CSV file (auto-cleanup)
- `temp_excel_file`: Temporary Excel file (auto-cleanup)
- `sample_book`: Single Book object
- `sample_books`: List of Book objects
- `sample_quote`: Single Quote object
- `sample_quotes`: List of Quote objects
- `mock_html_book_list`: Mock HTML for book listings
- `mock_html_quote_list`: Mock HTML for quote listings
- `mock_selenium_driver`: Mock Selenium WebDriver
- `mock_requests_response`: Mock requests.Response

### Mock HTML Fixtures (fixtures/mock_html.py)

Realistic HTML responses for testing:
- `MOCK_BOOK_LIST_PAGE`: Book listing page
- `MOCK_QUOTE_LIST_PAGE`: Quote listing page
- `MOCK_EMPTY_PAGE`: Empty/last page
- `MOCK_404_PAGE`: 404 error page
- `MOCK_QUOTE_DETAIL_PAGE`: Full quote detail
- `MOCK_USER_PAGE`: User profile page
- `MOCK_BOOK_DETAIL_PAGE`: Book detail page

## Coverage

The test suite provides comprehensive coverage:

- **Data Models**: ~100% coverage of Book and Quote classes
- **Helpers**: ~95% coverage of parser and I/O functions
- **Core Modules**: Integration test coverage for AppContext
- **Edge Cases**: Error handling, empty data, malformed input

View detailed coverage report:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # macOS
```

## Writing New Tests

### Test Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<Feature>`
- Test methods: `test_<specific_behavior>`

### Example Test

```python
def test_book_initialization_with_all_params(sample_book):
    """Test creating book with all parameters"""
    assert sample_book.name == 'Test Book'
    assert sample_book.author == 'Test Author'
    assert '/book/' in sample_book.link
```

### Using Fixtures

```python
def test_save_and_load_books(temp_csv_file, sample_books):
    """Test complete save/load cycle"""
    save_books(sample_books, temp_csv_file)
    loaded = read_books_from_csv(temp_csv_file)
    assert len(loaded) == len(sample_books)
```

## Continuous Integration

### Pre-commit Checks

Run these before committing:
```bash
# All tests must pass
pytest

# Check coverage
pytest --cov=. --cov-report=term-missing

# Ensure no warnings
pytest --strict-markers
```

### GitHub Actions (Example)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure you're running pytest from the project root
- Verify all dependencies are installed: `pip install -r requirements.txt`

**File Not Found Errors**
- Tests use temporary files; ensure proper cleanup
- Check that test fixtures are being used correctly

**Encoding Issues**
- All files use UTF-8 encoding
- Ensure your terminal supports UTF-8 for Russian text

**Selenium Tests**
- Mock drivers are used by default in tests
- Real Selenium tests would require ChromeDriver installation

## Best Practices

1. **Use fixtures**: Leverage conftest.py fixtures for common test data
2. **Clean up**: Use temporary files/directories with auto-cleanup
3. **Mock external calls**: Don't make real HTTP requests in tests
4. **Test edge cases**: Empty data, None values, malformed input
5. **Descriptive names**: Test names should explain what is being tested
6. **Assertions**: Include clear, specific assertions
7. **Isolation**: Tests should not depend on each other

## Future Enhancements

Potential test improvements:
- [ ] Performance/benchmark tests for large datasets
- [ ] Property-based testing with Hypothesis
- [ ] Selenium integration tests with real browser
- [ ] API mocking with responses library
- [ ] Parameterized tests for multiple scenarios
- [ ] Snapshot testing for HTML parsing
- [ ] Mutation testing for test quality

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
