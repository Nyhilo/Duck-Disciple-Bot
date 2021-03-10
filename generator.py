import requests

import config
from log import log


def get_random_duck_name():
    req = requests.get(config.NAME_GENERATOR_URL)

    log.info(f'Getting duck name from {config.NAME_GENERATOR_URL}')

    if not req.status_code == 200:
        log.debug(f'Request returned status {req.status_code}')
        return None

    res = req.json()
    try:
        name = res['data']['name']
    except KeyError:
        log.debug('Request returned malformed data.')
        return None

    return name


if __name__ == '__main__':
    response = get_random_duck_name()
    print(response)
