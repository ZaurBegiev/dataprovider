from datetime import datetime
import logging
import requests
import time

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)

MAIN = 'https://en.wikipedia.org'
RECENT_CHANGES_PAGE_URL = 'https://en.wikipedia.org/wiki/Special:RecentChanges'
CACHE_SIZE_THRESHOLD = 500


def refresh_recent_changes():
    recent_changes_page = requests.get(RECENT_CHANGES_PAGE_URL).text
    recent_changes_soup = BeautifulSoup(recent_changes_page, "html.parser")
    recent_changes = recent_changes_soup.find_all('li', {'class': 'mw-changeslist-line'})
    return recent_changes


def get_url_suffix(change):
    return change.find('a', {'class': 'mw-changeslist-diff'}).get('href')


def extract_diff_id(url_suffix):
    first_split = url_suffix.split('&')
    second_split = [_.split('=') for _ in first_split]
    split_to_dict = {key: value for key, value in second_split}
    return int(split_to_dict['diff'])


def parse_change_url(change):
    if not change.get('data-mw-logaction'):
        url_suffix = get_url_suffix(change)
    else:
        return

    ts = change.get('data-mw-ts')
    result_message = {
        'timestamp': datetime.strptime(ts, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
        'url_suffix': url_suffix,
        'diff_id': extract_diff_id(url_suffix),
    }
    return result_message


def run():
    cache = set()

    while True:
        time.sleep(2)
        recent_changes = refresh_recent_changes()
        for change in recent_changes:
            try:
                if change:
                    message = parse_change_url(change)
                    if message:
                        diff_id = message['diff_id']
                        if diff_id in cache:
                            pass
                        else:
                            cache.add(message['diff_id'])
                            logging.info(message)
            except AttributeError:
                pass
        if len(cache) > CACHE_SIZE_THRESHOLD:
            cache = set(list(sorted(cache))[len(cache) - CACHE_SIZE_THRESHOLD:])
            logging.info('Obsolete cache cleared')


if __name__ == '__main__':
    run()
