from typing import Optional
import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Helpers.logger_config import get_logger
from Helpers.exceptions import NetworkError
from Helpers.retry import retry

logger = get_logger(__name__)


def download_page(link: str, driver: Optional[object] = None) -> str:
    """
    Download page content using either requests or Selenium.

    Args:
        link: URL to download
        driver: Optional Selenium WebDriver instance

    Returns:
        Page content as string

    Raises:
        NetworkError: If download fails
    """
    if driver:
        return __download_page_selenium(link, driver)
    else:
        return __download_page_requests(link)


@retry(max_attempts=3, delay=2.0, exceptions=(NetworkError, requests.RequestException))
def __download_page_requests(link: str) -> str:
    """
    Download page using requests library with automatic retry.

    Args:
        link: URL to download

    Returns:
        Page content as bytes

    Raises:
        NetworkError: If download fails after all retries
    """
    logger.debug(f'Downloading page: {link}')
    try:
        response = requests.get(link, timeout=30)
        response.raise_for_status()
        logger.debug(f'Successfully downloaded: {link}')
        return response.content
    except requests.RequestException as ex:
        logger.error(f'Failed to download page: {link}', exc_info=True)
        raise NetworkError(f'Download failed: {link}') from ex


def __download_page_selenium(link: str, driver: object) -> str:
    """
    Download page using Selenium WebDriver.

    Args:
        link: URL to download
        driver: Selenium WebDriver instance

    Returns:
        Page source as string

    Raises:
        NetworkError: If download fails
    """
    driver.get(link)
    try:
        from selenium.webdriver.common.by import By
        logger.info(f'Start downloading {link}')
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "main-body"))
            # EC.presence_of_element_located((By.CLASS_NAME, "page-content"))
        )
        return driver.page_source
    except Exception as e:
        logger.error(f'Selenium download failed for {link}: {e}')
        raise NetworkError(f'Selenium download failed: {link}') from e
