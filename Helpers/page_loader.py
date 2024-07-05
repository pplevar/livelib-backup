import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_page(link, driver=None) -> str or None:
    if driver:
        return __download_page_silenium(link, driver)
    else:
        return __download_page_requests(link)


def __download_page_requests(link):
    """
    Скачивает страницу
    :param link: string - ссылка на страницу
    :return: string? - тело страницы
    """
    print('Start downloading "%s" ...' % link, end='\t')
    try:
        with requests.get(link)as data:
            content = data.content
            print('Downloaded.')
            return content
    except Exception as ex:
        print('\nERROR: Some troubles with downloading:', ex)
        raise ex


def __download_page_silenium(link, driver) -> str or None:
    """
    Скачивает страницу
    :param link: string - ссылка на страницу
    :param driver: obj - драйвер силениума
    :return: string? - тело страницы
    """
    from export import logger

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
        logger.error(f'Some error erupted during selenium processing: {e}')
        return None
