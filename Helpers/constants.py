"""Application constants and configuration values."""

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
DEFAULT_PAGE_COUNT = float('inf')
DEFAULT_QUOTE_COUNT = float('inf')
DEFAULT_READ_COUNT = float('inf')

# CSV/Excel columns
BOOK_COLUMNS = ['Name', 'Author', 'Status', 'My Rating', 'Date', 'Link']
QUOTE_COLUMNS = ['Name', 'Author', 'Quote text', 'Book link', 'Quote link']

# Driver types
DRIVER_REQUESTS = 'requests'
DRIVER_SELENIUM = 'selenium'
SUPPORTED_DRIVERS = [DRIVER_REQUESTS, DRIVER_SELENIUM]

# CSV separator
CSV_SEPARATOR = '\t'
