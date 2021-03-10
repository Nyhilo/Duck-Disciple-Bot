import requests
from bs4 import BeautifulSoup

from config import WIKI_SCRAPE_LOCATION
from log import log


def get_site_content():
    log.info(f'Getting wiki content from {WIKI_SCRAPE_LOCATION}')

    req = requests.get(WIKI_SCRAPE_LOCATION)

    if not req.status_code == 200:
        log.debug(f'Request returned status {req.status_code}')
        return None

    return BeautifulSoup(req.content, 'html.parser')


def parse_duck_row(table_row, headers):
    return {headers[i]: td.text.strip()
            for i, td
            in enumerate(table_row.find_all('td')) if i < len(headers)}


def get_ducks(include_unnamed=True):
    soup = get_site_content()
    table = soup.select('#Ducks')[0].find_parent().find_next_sibling('table')

    rows = table.find_all('tr')
    headers = rows[0]
    header_keys = [h.text.strip() for h in headers.find_all('th')]

    ducks = [parse_duck_row(r, header_keys) for r in rows[1:]]

    if not include_unnamed:
        ducks = [duck for duck in ducks if duck['Name'][0] != '-']

    return ducks


def get_player_duck(dice_roll, cached_ducks=None, include_unnamed=True):
    ducks = cached_ducks
    if not ducks:
        ducks = get_ducks(include_unnamed)

    duck = ducks[dice_roll-1]

    log.info(f'Rolled {dice_roll} and got {duck}')

    named_ducks = '' if include_unnamed else ' for named ducks'
    name = duck['Name']
    owner = duck['Owner']
    return f'Rolled a {dice_roll} on the Ducks table{named_ducks}:\n' + \
           f'Got the duck named `{name}` belonging to `{owner}`'


if __name__ == '__main__':
    soup = get_site_content()
