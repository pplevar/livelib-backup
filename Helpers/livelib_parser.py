from typing import Optional
import re
from collections import defaultdict
from lxml import etree
from Helpers.logger_config import get_logger

logger = get_logger(__name__)


def error_handler(where: str, raw: etree._Element) -> None:
    """
    Handle parsing errors for HTML pages.

    Args:
        where: Description of what failed to parse
        raw: HTML node that failed

    Returns:
        None
    """
    logger.error(f'Parsing error ({where} not parsed): {etree.tostring(raw)}')
    return None


def try_parse_month(raw_month: str) -> str:
    """
    Convert Russian month name to numeric format.

    Args:
        raw_month: Month name in Russian (e.g., 'Январь', 'Февраль')

    Returns:
        Month as two-digit string (01-12), defaults to '01' if not found
    """
    month_mapping = defaultdict(lambda: '01', {
        'Январь': '01',    # January
        'Февраль': '02',   # February
        'Март': '03',      # March
        'Апрель': '04',    # April
        'Май': '05',       # May
        'Июнь': '06',      # June
        'Июль': '07',      # July
        'Август': '08',    # August
        'Сентябрь': '09',  # September
        'Октябрь': '10',   # October
        'Ноябрь': '11',    # November
        'Декабрь': '12'    # December
    })
    return month_mapping[raw_month]


def is_last_page(page: etree._Element) -> bool:
    """
    Check if page is the last page (has empty list indicator).

    Args:
        page: HTML page element

    Returns:
        True if this is the last page
    """
    return bool(len(page.xpath('//div[@class="with-pad"]')))


def is_redirecting_page(page: etree._Element) -> bool:
    """
    Check if page is a redirect/404 page (bot detection).

    Args:
        page: HTML page element

    Returns:
        True if this is a redirect/error page
    """
    flag = bool(len(page.xpath('//div[@class="page-404"]')))
    if flag:
        logger.warning('Bot detection triggered - Livelib suspects automation')
        logger.warning('Reading stopped to avoid being blocked')
    return flag


def href_i(href: str, i: int) -> str:
    """
    Generate URL for i-th page of given type.

    Args:
        href: Base URL
        i: Page number

    Returns:
        URL for page i
    """
    return href + '/~' + str(i)


def date_parser(date: str) -> Optional[str]:
    """
    Convert date to YYYY-MM-DD format.

    Args:
        date: Date string in Russian format

    Returns:
        Date in YYYY-MM-DD format, or None if parsing fails
    """
    match = re.search(r'\d{4} г.', date)
    if match is not None:
        year = match.group(0).split(' ')[0]
        raw_month = date.split(' ')[0]
        month = try_parse_month(raw_month)
        return '%s-%s-01' % (year, month)
    return None


def handle_xpath(html_node: Optional[etree._Element], request: str, i: int = 0) -> Optional[etree._Element]:
    """
    XPath wrapper that returns i-th found node or None.

    Args:
        html_node: HTML node to search
        request: XPath query string
        i: Index of node to return (default: 0)

    Returns:
        Found HTML node or None if not found
    """
    if html_node is None:
        return None
    tmp = html_node.xpath(request)
    return tmp[i] if i < len(tmp) else None


def slash_add(left: str, right: str) -> str:
    """Join two URL parts with a slash."""
    return left + '/' + right
