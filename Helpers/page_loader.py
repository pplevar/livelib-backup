"""
Page loading module with robust error handling and retry logic.
Supports both requests and Selenium drivers.
"""
import logging
from typing import Optional
import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2.0  # seconds


def download_page(link: str, driver=None) -> Optional[str]:
    """
    Download a web page using either requests or Selenium.
    
    Args:
        link: URL to download
        driver: Optional Selenium WebDriver instance
        
    Returns:
        Page content as string, or None on failure
        
    Raises:
        requests.exceptions.RequestException: On persistent network failures
    """
    if driver:
        return __download_page_selenium(link, driver)
    else:
        return __download_page_requests(link)


def __download_page_requests(link: str, retry_count: int = 0) -> Optional[str]:
    """
    Download a page using requests library with retry logic.
    
    Args:
        link: URL to download
        retry_count: Current retry attempt number
        
    Returns:
        Page content as string, or None on failure
        
    Raises:
        requests.exceptions.RequestException: After max retries exceeded
    """
    try:
        logger.info('Downloading "%s"...', link)
        response = requests.get(link, timeout=30)
        response.raise_for_status()
        logger.info('Downloaded "%s" successfully.', link)
        return response.content
    except requests.exceptions.Timeout as e:
        logger.warning('Timeout downloading "%s": %s', link, e)
        if retry_count < MAX_RETRIES:
            import time
            time.sleep(RETRY_DELAY)
            return __download_page_requests(link, retry_count + 1)
        raise
    except requests.exceptions.RequestException as e:
        logger.error('Network error downloading "%s": %s', link, e)
        if retry_count < MAX_RETRIES:
            import time
            time.sleep(RETRY_DELAY)
            return __download_page_requests(link, retry_count + 1)
        raise
    except Exception as e:
        logger.error('Unexpected error downloading "%s": %s', link, e)
        raise


def __download_page_selenium(link: str, driver) -> Optional[str]:
    """
    Download a page using Selenium WebDriver.
    
    Args:
        link: URL to download
        driver: Selenium WebDriver instance
        
    Returns:
        Page content as string, or None on failure
    """
    try:
        logger.info('Downloading "%s" via Selenium...', link)
        driver.get(link)
        
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "main-body"))
        )
        
        logger.info('Downloaded "%s" successfully via Selenium.', link)
        return driver.page_source
    except Exception as e:
        logger.error('Selenium error downloading "%s": %s', link, e)
        return None
