"""
Unit tests for AppContext class
"""
import pytest
import math
import time
from Modules.AppContext import AppContext


class TestAppContext:
    """Tests for AppContext dataclass"""

    def test_appcontext_initialization_defaults(self):
        """Test default AppContext initialization"""
        context = AppContext()
        assert context.user_href is None
        assert context.status is None
        assert context.driver is None
        assert context.skip is None
        assert context.book_file is None
        assert context.quote_file is None
        assert context.page_count == math.inf
        assert context.quote_count == math.inf
        assert context.max_delay == 15
        assert context.min_delay == 5

    def test_appcontext_initialization_with_values(self):
        """Test AppContext initialization with custom values"""
        context = AppContext(
            user_href='https://www.livelib.ru/reader/testuser',
            status='read',
            book_file='books.csv',
            quote_file='quotes.csv',
            max_delay=30,
            min_delay=10
        )
        assert context.user_href == 'https://www.livelib.ru/reader/testuser'
        assert context.status == 'read'
        assert context.book_file == 'books.csv'
        assert context.quote_file == 'quotes.csv'
        assert context.max_delay == 30
        assert context.min_delay == 10

    def test_appcontext_modification(self):
        """Test modifying AppContext attributes"""
        context = AppContext()
        context.user_href = 'https://example.com'
        context.page_count = 5
        assert context.user_href == 'https://example.com'
        assert context.page_count == 5


class TestWaitForDelay:
    """Tests for wait_for_delay method"""

    def test_wait_for_delay_no_delay(self):
        """Test wait with max_delay = -1 uses min_delay"""
        context = AppContext(min_delay=0, max_delay=-1)
        start = time.time()
        context.wait_for_delay()
        duration = time.time() - start
        assert duration < 0.1

    def test_wait_for_delay_max_less_than_min(self):
        """Test wait when max_delay < min_delay uses max_delay"""
        context = AppContext(min_delay=10, max_delay=1)
        start = time.time()
        context.wait_for_delay()
        duration = time.time() - start
        assert duration >= 1
        assert duration < 2

    def test_wait_for_delay_normal_range(self):
        """Test wait with normal delay range"""
        context = AppContext(min_delay=1, max_delay=2)
        start = time.time()
        context.wait_for_delay()
        duration = time.time() - start
        assert duration >= 1
        assert duration < 3

    def test_wait_for_delay_zero_delays(self):
        """Test wait with zero delays"""
        context = AppContext(min_delay=0, max_delay=0)
        start = time.time()
        context.wait_for_delay()
        duration = time.time() - start
        assert duration < 0.1

    def test_wait_for_delay_same_min_max(self):
        """Test wait when min_delay equals max_delay"""
        context = AppContext(min_delay=1, max_delay=1)
        start = time.time()
        context.wait_for_delay()
        duration = time.time() - start
        assert duration >= 1
        assert duration < 2

    @pytest.mark.slow
    def test_wait_for_delay_multiple_calls(self):
        """Test multiple wait_for_delay calls"""
        context = AppContext(min_delay=0, max_delay=1)
        for _ in range(3):
            start = time.time()
            context.wait_for_delay()
            duration = time.time() - start
            assert duration >= 0
            assert duration < 2
