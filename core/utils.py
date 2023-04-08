from config.config import GLOBAL_ADMIN_IDS, SERVER_ADMIN_IDS, CARDS
from random import choice


def trim_quotes(string):
    # check if the string is surrounded by quotes
    if string[0] == '"' and string[-1] == '"':
        return string[1:-1]

    return string


def strip_command(message, command):
    if not message.startswith(command):
        return message

    return ' '.join(message.split(' ')[1:])


def is_admin(userId, serverId=None):
    if userId in GLOBAL_ADMIN_IDS:
        return True

    if not serverId or serverId not in SERVER_ADMIN_IDS:
        return False

    return userId in SERVER_ADMIN_IDS[serverId]


def roman_numeralize(num):
    '''Stolen and modified from w3resource.com'''
    if num == 0:
        return '0'

    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC",
           "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


def draw_random_card_sets(width, groups):
    out = ''
    for i in range(groups):
        cards = [choice(CARDS) for _ in range(width)]
        out += ''.join(cards) + ('\n' if i < groups else '')

    return out
