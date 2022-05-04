import time
import random
import requests

def download_page(link):
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


def wait_for_delay(min_delay, max_delay=-1):
    """
    Останавливает программу на некоторое число секунд. Нужна, чтобы сайт не распознал в нас бота
    :param min_delay: int - минимальное число секунд
    :param max_delay: int - максимальное число секунд
    """
    if max_delay == -1:
        delay = min_delay
    elif max_delay < min_delay:
        delay = max_delay
    else:
        delay = random.randint(min_delay, max_delay)
    print("Waiting %s sec..." % delay)
    time.sleep(delay)
