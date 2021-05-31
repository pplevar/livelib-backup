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
        print('\nSome troubles with downloading:', ex)
        raise ex


def wait_for_delay(min_delay, max_delay=-1):
    delay = random.randint(min_delay, max_delay) if max_delay >= 0 else min_delay
    print("Waiting %s sec..." % delay)
    time.sleep(delay)