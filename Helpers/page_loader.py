import time
import random
from urllib import request


def download_page(link):
    print('Start downloading "%s" ...' % link, end='\t')
    try:
        with request.urlopen(link) as data:
            content = data.read()
            print('Downloaded.')
            return content
    except Exception as ex:
        print('\nERROR: Some troubles with downloading:', ex)
        raise ex


def wait_for_delay(min_delay, max_delay=-1):
    if max_delay == -1:
        delay = min_delay
    elif max_delay < min_delay:
        delay = max_delay
    else:
        delay = random.randint(min_delay, max_delay)
    print("Waiting %s sec..." % delay)
    time.sleep(delay)