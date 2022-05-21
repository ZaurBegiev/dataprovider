from datetime import datetime
import requests
import time

from bs4 import BeautifulSoup

MAIN = 'https://en.wikipedia.org'
RECENT_CHANGES_PAGE_URL = 'https://en.wikipedia.org/wiki/Special:RecentChanges'


def refresh_recent_changes():
    recent_changes_page = requests.get(RECENT_CHANGES_PAGE_URL).text
    recent_changes_soup = BeautifulSoup(recent_changes_page, "html.parser")
    recent_changes = recent_changes_soup.find_all('li', {'class': 'mw-changeslist-line'})
    return recent_changes


def get_url_suffix(change):
    return change.find('a', {'class': 'mw-changeslist-diff'}).get('href')


def parse_change_url(change):
    if not change.get('data-mw-logaction'):
        url_suffix = get_url_suffix(change)
    else:
        return

    ts = change.get('data-mw-ts')
    result_message = {
        'timestamp': datetime.strptime(ts, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
        'url_suffix': url_suffix
    }
    return result_message


def run():
    while True:
        print('-' * 100)
        time.sleep(2)
        recent_changes = refresh_recent_changes()
        for change in recent_changes:
            try:
                if change:
                    message = parse_change_url(change)
                    if message:
                        print(message)
            except AttributeError:
                pass


if __name__ == '__main__':
    run()
