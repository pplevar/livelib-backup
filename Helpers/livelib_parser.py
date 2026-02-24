"""
LiveLib HTML parsing utilities with improved error handling.
"""
import re
import logging
from typing import Optional, List, Any
from collections import defaultdict
from lxml import etree, html

logger = logging.getLogger(__name__)


def error_handler(where: str, raw: html.HtmlElement) -> None:
    """
    Log parsing errors with context.
    
    Args:
        where: Description of what failed to parse
        raw: HTML element that failed to parse
    """
    try:
        html_snippet = etree.tostring(raw, encoding='unicode', method='html')[:200]
    except Exception:
        html_snippet = "<unable to serialize>"
    
    logger.error('Parsing error (%s not parsed): %s...', where, html_snippet)
    return None


def try_parse_month(raw_month: str) -> str:
    """
    Convert Russian month name to numeric format.
    
    Args:
        raw_month: Month name in Russian (e.g., 'Январь')
        
    Returns:
        Two-digit month string (e.g., '01')
    """
    month_map = defaultdict(lambda: '01', {
        'Январь': '01',
        'Февраль': '02',
        'Март': '03',
        'Апрель': '04',
        'Май': '05',
        'Июнь': '06',
        'Июль': '07',
        'Август': '08',
        'Сентябрь': '09',
        'Октябрь': '10',
        'Ноябрь': '11',
        'Декабрь': '12'
    })
    return month_map[raw_month]


def is_last_page(page: html.HtmlElement) -> bool:
    """
    Check if page is the last page (empty object list).
    
    Args:
        page: Parsed HTML page
        
    Returns:
        True if this is the last page
    """
    return bool(len(page.xpath('//div[@class="with-pad"]')))


def is_redirecting_page(page: html.HtmlElement) -> bool:
    """
    Check if page is a redirect/error page (bot detection).
    
    Args:
        page: Parsed HTML page
        
    Returns:
        True if this is an error/redirect page
    """
    flag = bool(len(page.xpath('//div[@class="page-404"]')))
    if flag:
        logger.error('LiveLib suspects bot activity. Reading stopped.')
    return flag


def href_i(href: str, i: int) -> str:
    """
    Generate URL for page number i.
    
    Args:
        href: Base URL
        i: Page number
        
    Returns:
        URL for specific page
    """
    return f"{href}/~{i}"


def date_parser(date: str) -> Optional[str]:
    """
    Parse date string to ISO format (YYYY-MM-DD).
    
    Args:
        date: Date string from LiveLib (e.g., 'Январь 2024 г.')
        
    Returns:
        ISO format date string or None if parsing fails
    """
    m = re.search(r'\d{4} г\.', date)
    if m is not None:
        year = m.group(0).split(' ')[0]
        raw_month = date.split(' ')[0]
        month = try_parse_month(raw_month)
        return f'{year}-{month}-01'
    return None


def handle_xpath(html_node: Optional[html.HtmlElement], request: str, i: int = 0) -> Optional[Any]:
    """
    Safe XPath wrapper with bounds checking.
    
    Args:
        html_node: HTML element to query
        request: XPath query string
        i: Index of result to return (default: 0)
        
    Returns:
        XPath result at index i, or None if not found
    """
    if html_node is None:
        return None
    
    tmp = html_node.xpath(request)
    return tmp[i] if i < len(tmp) else None


def slash_add(left: str, right: str) -> str:
    """
    Join two path segments with a slash.
    
    Args:
        left: Left path segment
        right: Right path segment
        
    Returns:
        Combined path with slash separator
    """
    return f"{left}/{right}"
