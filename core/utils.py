from typing import Dict
from random import choice

from discord import Message, TextChannel, User

from config.config import GLOBAL_ADMIN_IDS, SERVER_ADMIN_IDS, CARDS, MESSAGE_LIMIT, LINE_SPLIT_LIMIT, \
                          MAX_CACHE_LENGTH, CACHE_EXPIRY_SECONDS
from core.nomic_time import utc_now


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


class MemoizeCache():
    def __init__(self, bot) -> None:
        self.bot = bot
        self.cachedChannels = {}
        self.cachedMessages = {}
        self.cachedUsers = {}

    async def get_channel(self, id: int) -> TextChannel:
        if self._is_data_stale(self.cachedChannels, id):
            response = await self.bot.fetch_channel(id)
            response.expires = utc_now() + CACHE_EXPIRY_SECONDS
            self.cachedChannels[id] = response

        return self.cachedChannels[id]

    async def get_message(self, channel: TextChannel, id: int) -> Message:
        if self._is_data_stale(self.cachedMessages, id):
            response = await channel.fetch_message(id)
            response.expires = utc_now() + CACHE_EXPIRY_SECONDS
            self.cachedMessages[id] = response

        return self.cachedMessages[id]

    async def get_user(self, id: int) -> User:
        if self._is_data_stale(self.cachedUsers, id):
            response = await self.bot.fetch_user(id)
            response.expires = utc_now() + CACHE_EXPIRY_SECONDS
            self.cachedUsers[id] = response

        return self.cachedUsers[id]

    async def _is_data_stale(self, cache: Dict[any], id: int) -> None:
        if len(cache) >= MAX_CACHE_LENGTH:
            cache = {}
            return True

        if id not in cache:
            return True

        if utc_now() > cache[id].expires:
            return True

        return False


def page_message(message: str, limit: int = MESSAGE_LIMIT, line_split_limit: int = LINE_SPLIT_LIMIT) -> list[str]:
    if len(message) <= limit:
        return [message]

    limit = limit - 6   # Buffer for codeblocks

    result = []
    buffer = ''

    while len(message) > 0 and message != '```':
        if len(message) < limit:
            if message.count('```') % 2 == 1:    # Search for unclosed codeblocks
                message += '```'

            result.append(message)
            break

        buffer = message[:limit]

        newline = buffer.rfind('\n')
        if newline != -1 and newline > (limit - line_split_limit):
            buffer = buffer[:newline]
            message = message[newline:].lstrip('\n')

            if buffer.count('```') % 2 == 1:    # Search for unclosed codeblocks
                buffer += '```'
                message = '```' + message

            result.append(buffer)
            continue

        space = buffer.rfind(' ')

        if space != -1 and space > (limit - line_split_limit):
            buffer = buffer[:space]
            message = message[space:].lstrip()

            if buffer.count('```') % 2 == 1:    # Search for unclosed codeblocks
                buffer += '```'
                message = '```' + message

            result.append(buffer)
            continue

        message = message[limit:]
        if buffer.count('```') % 2 == 1:    # Search for unclosed codeblocks
            buffer += '```'
            message = '```' + message

        result.append(buffer)

    return result
