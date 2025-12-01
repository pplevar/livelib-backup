"""
Pytest configuration and shared fixtures for livelib-backup tests
"""
import pytest
import os
import tempfile
from unittest.mock import Mock
from Modules.AppContext import AppContext
from Helpers.book import Book
from Helpers.quote import Quote


@pytest.fixture
def app_context():
    """Create a basic AppContext for testing"""
    context = AppContext()
    context.user_href = "https://www.livelib.ru/reader/testuser"
    context.book_file = "test_books.csv"
    context.quote_file = "test_quotes.csv"
    context.min_delay = 0
    context.max_delay = 0
    return context


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    fd, path = tempfile.mkstemp(suffix='.csv')
    yield path
    os.close(fd)
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def temp_excel_file():
    """Create a temporary Excel file for testing"""
    fd, path = tempfile.mkstemp(suffix='.xlsx')
    yield path
    os.close(fd)
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def sample_book():
    """Create a sample Book object"""
    return Book(
        link="/book/123456",
        status="read",
        name="Test Book",
        author="Test Author",
        rating="5",
        date="01.01.2024"
    )


@pytest.fixture
def sample_books():
    """Create a list of sample Book objects"""
    return [
        Book(
            link="/book/123456",
            status="read",
            name="Book 1",
            author="Author 1",
            rating="5",
            date="01.01.2024"
        ),
        Book(
            link="/book/789012",
            status="reading",
            name="Book 2",
            author="Author 2",
            rating="4",
            date="15.02.2024"
        ),
        Book(
            link="/work/345678",
            status="wish",
            name="Book 3",
            author="Author 3",
            rating="",
            date=""
        )
    ]


@pytest.fixture
def sample_quote(sample_book):
    """Create a sample Quote object"""
    return Quote(
        link="/quote/999888",
        text="This is a test quote from the book.",
        book=sample_book
    )


@pytest.fixture
def sample_quotes(sample_books):
    """Create a list of sample Quote objects"""
    return [
        Quote(
            link="/quote/111111",
            text="First quote text",
            book=sample_books[0]
        ),
        Quote(
            link="/quote/222222",
            text="Second quote text",
            book=sample_books[1]
        ),
        Quote(
            link="/quote/333333",
            text="Third quote text",
            book=sample_books[2]
        )
    ]


@pytest.fixture
def mock_html_book_list():
    """Mock HTML for a book list page"""
    return """
    <html>
        <div class="brow">
            <a href="/book/123456" class="brow-book-name">Test Book</a>
            <a href="/author/1" class="brow-book-author">Test Author</a>
            <div class="brow-ratings">5</div>
            <div class="read-date">01 января 2024</div>
        </div>
        <div class="brow">
            <a href="/work/789012" class="brow-book-name">Another Book</a>
            <a href="/author/2" class="brow-book-author">Another Author</a>
            <div class="brow-ratings">4</div>
            <div class="read-date">15 февраля 2024</div>
        </div>
    </html>
    """


@pytest.fixture
def mock_html_quote_list():
    """Mock HTML for a quote list page"""
    return """
    <html>
        <div class="quote-item">
            <a href="/quote/111111" class="quote-link">View quote</a>
            <div class="quote-text">This is a test quote.</div>
            <a href="/book/123456" class="book-link">Test Book</a>
            <a href="/author/1" class="author-link">Test Author</a>
        </div>
        <div class="quote-item">
            <a href="/quote/222222" class="quote-link">View quote</a>
            <div class="quote-text">Another test quote...</div>
            <a href="/book/789012" class="book-link">Another Book</a>
            <a href="/author/2" class="author-link">Another Author</a>
        </div>
    </html>
    """


@pytest.fixture
def mock_selenium_driver():
    """Mock Selenium WebDriver for testing"""
    driver = Mock()
    driver.get = Mock()
    driver.quit = Mock()
    driver.page_source = "<html><body>Mock page</body></html>"
    return driver


@pytest.fixture
def mock_requests_response():
    """Mock requests.Response object"""
    response = Mock()
    response.status_code = 200
    response.text = "<html><body>Mock response</body></html>"
    response.content = b"<html><body>Mock response</body></html>"
    return response
