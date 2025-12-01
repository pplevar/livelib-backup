"""
Mock HTML responses for testing livelib scraper
"""


MOCK_BOOK_LIST_PAGE = """
<html>
<body>
    <div class="brow">
        <div class="brow-item">
            <a href="/book/123456-test-book" class="brow-book-name">Test Book Title</a>
        </div>
        <div class="brow-item">
            <a href="/author/1111-test-author" class="brow-book-author">Test Author</a>
        </div>
        <div class="brow-ratings">
            <span class="rating-value">5</span>
        </div>
        <div class="read-date">Январь 2024 г.</div>
    </div>
    <div class="brow">
        <div class="brow-item">
            <a href="/work/789012-another-book" class="brow-book-name">Another Book</a>
        </div>
        <div class="brow-item">
            <a href="/author/2222-another-author" class="brow-book-author">Another Author</a>
        </div>
        <div class="brow-ratings">
            <span class="rating-value">4</span>
        </div>
        <div class="read-date">Февраль 2024 г.</div>
    </div>
</body>
</html>
"""


MOCK_EMPTY_PAGE = """
<html>
<body>
    <div class="with-pad">
        <p>Страница пуста</p>
    </div>
</body>
</html>
"""


MOCK_404_PAGE = """
<html>
<body>
    <div class="page-404">
        <h1>404 - Страница не найдена</h1>
    </div>
</body>
</html>
"""


MOCK_QUOTE_LIST_PAGE = """
<html>
<body>
    <div class="quote-item">
        <div class="quote-text">
            This is a test quote from the book.
        </div>
        <a href="/quote/111111" class="quote-link">Quote link</a>
        <div class="quote-book">
            <a href="/book/123456" class="book-link">Test Book</a>
            <a href="/author/1111" class="author-link">Test Author</a>
        </div>
    </div>
    <div class="quote-item">
        <div class="quote-text">
            Another quote text here...
        </div>
        <a href="/quote/222222" class="quote-link">Quote link</a>
        <div class="quote-book">
            <a href="/book/789012" class="book-link">Another Book</a>
            <a href="/author/2222" class="author-link">Another Author</a>
        </div>
    </div>
</body>
</html>
"""


MOCK_QUOTE_DETAIL_PAGE = """
<html>
<body>
    <div class="quote-full-text">
        <p>This is the complete quote text that was truncated on the list page.
        It contains much more detail and context about the specific passage from the book.</p>
    </div>
    <div class="quote-meta">
        <a href="/book/123456-test-book">Test Book</a>
        <a href="/author/1111-test-author">Test Author</a>
    </div>
</body>
</html>
"""


MOCK_USER_PAGE = """
<html>
<body>
    <div class="user-profile">
        <h1>User Profile</h1>
        <div class="user-stats">
            <span class="books-read">150</span>
            <span class="books-reading">5</span>
            <span class="books-wish">200</span>
        </div>
    </div>
</body>
</html>
"""


MOCK_BOOK_DETAIL_PAGE = """
<html>
<body>
    <div class="book-detail">
        <h1 class="book-title">Detailed Book Title</h1>
        <div class="book-authors">
            <a href="/author/1111">Main Author</a>
            <a href="/author/2222">Co-Author</a>
        </div>
        <div class="book-rating">
            <span class="rating-value">4.5</span>
        </div>
        <div class="book-description">
            <p>This is a detailed description of the book.</p>
        </div>
    </div>
</body>
</html>
"""


def get_mock_html(page_type):
    """
    Get mock HTML for different page types

    Args:
        page_type: Type of page (book_list, quote_list, empty, 404, etc.)

    Returns:
        HTML string
    """
    pages = {
        'book_list': MOCK_BOOK_LIST_PAGE,
        'quote_list': MOCK_QUOTE_LIST_PAGE,
        'quote_detail': MOCK_QUOTE_DETAIL_PAGE,
        'empty': MOCK_EMPTY_PAGE,
        '404': MOCK_404_PAGE,
        'user': MOCK_USER_PAGE,
        'book_detail': MOCK_BOOK_DETAIL_PAGE
    }
    return pages.get(page_type, '<html><body></body></html>')
