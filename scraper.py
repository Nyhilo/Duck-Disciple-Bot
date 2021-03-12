import requests
from bs4 import BeautifulSoup

from config import WIKI_SCRAPE_LOCATION, BLANK_FIELD_PLACEHOLDER
from log import log


def get_site_content():
    log.info(f'Getting wiki content from {WIKI_SCRAPE_LOCATION}')

    req = requests.get(WIKI_SCRAPE_LOCATION)

    if not req.status_code == 200:
        log.debug(f'Request returned status {req.status_code}')
        return None

    return BeautifulSoup(req.content, 'html.parser')


def get_ducks_table(soup):
    return soup.select('#Ducks')[0].find_parent().find_next_sibling('table')


def parse_duck_row(table_row, headers):
    return {headers[i]: td.text.strip()
            for i, td
            in enumerate(table_row.find_all('td')) if i < len(headers)}


def get_ducks(include_unnamed=True):
    soup = get_site_content()
    table = get_ducks_table(soup)

    rows = table.find_all('tr')
    headers = rows[0]
    header_keys = [h.text.strip() for h in headers.find_all('th')]

    ducks = [parse_duck_row(r, header_keys) for r in rows[1:]]

    if not include_unnamed:
        ducks = [duck for duck in ducks
                 if 'Name' in duck
                    and duck['Name'][0] != BLANK_FIELD_PLACEHOLDER]

    return ducks


def get_player_duck(dice_roll, cached_ducks=None, include_unnamed=True):
    ducks = cached_ducks
    if not ducks:
        ducks = get_ducks(include_unnamed)

    duck = ducks[dice_roll-1]

    log.info(f'Rolled {dice_roll} and got {duck}')

    named_ducks = '' if include_unnamed else ' for named ducks'
    name = duck['Name'] if 'Name' in duck else ''
    owner = duck['Owner'] if 'Owner' in duck else ''

    return f'Rolled a {dice_roll} on the Ducks table{named_ducks}:\n' + \
           f'Got the duck named `{name}` belonging to `{owner}`'


def get_player_quacks():
    ducks = get_ducks(True)

    msg = ''

    # Aggregate the number of quacks owned by each player
    owners = {}
    flagged_owners = []
    for duck in ducks:
        owner = duck['Owner'] if 'Owner' in duck else None
        name = duck['Name'] if 'Name' in duck else 'an unnamed duck'

        if not owner or owner == BLANK_FIELD_PLACEHOLDER:
            continue

        try:
            quacks = int(duck['Quacks']) if 'Quacks' in duck else 0
        except ValueError:
            if owner not in flagged_owners:
                flagged_owners.append(owner)
                msg += (f'Whoops! {name} has a non-integer number of quacks! '
                        f'Gonna leave {owner} out of this one.\n')

        if owner in owners:
            owners[owner] += quacks
        else:
            owners[owner] = quacks

    # Build the return table
    headers = ('Player', 'Quacks')
    # Colum sizes are the max length of the header or the content
    owner_spacing = max(len(owner) for owner, quacks in owners.items())
    quacks_spacing = max(len(str(quacks)) for owner, quacks in owners.items())
    column_len = (max(owner_spacing, len(headers[0])) + 1,
                  max(quacks_spacing, len(headers[1])))

    if msg != '':
        msg += '\n'

    msg += '```\n'
    msg += headers[0].ljust(column_len[0]) + headers[1].rjust(column_len[1])
    msg += '\n' + '-' * (column_len[0] + column_len[1]) + '\n'

    sorted_owners = sorted(owners.items(), key=lambda i: i[1], reverse=True)
    for owner, quacks in sorted_owners:

        # `Player Name     Value`
        msg += owner.ljust(column_len[0]) + str(quacks).rjust(column_len[1])
        msg += '\n'

    msg += '```'

    return msg


if __name__ == '__main__':
    soup = get_site_content()
