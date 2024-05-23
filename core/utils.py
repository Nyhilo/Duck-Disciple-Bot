from discord import Message, TextChannel, User
from random import choice

from config.config import GLOBAL_ADMIN_IDS, SERVER_ADMIN_IDS, CARDS, MAX_CACHE_LENGTH


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
        if id not in self.cachedChannels:

            # "Clear the cache" if it gets too big
            if len(self.cachedChannels) >= MAX_CACHE_LENGTH:
                self.cachedChannels = {}

            self.cachedChannels[id] = await self.bot.fetch_channel(id)

        return self.cachedChannels[id]

    async def get_message(self, channel: TextChannel, id: int) -> Message:
        if id not in self.cachedMessages:

            # "Clear the cache" if it gets too big
            if len(self.cachedMessages) >= MAX_CACHE_LENGTH:
                self.cachedMessages = {}

            self.cachedMessages[id] = await channel.fetch_message(id)

        return self.cachedMessages[id]

    async def get_user(self, id: int) -> User:
        if id not in self.cachedUsers:

            # "Clear the cache" if it gets too big
            if len(self.cachedUsers) >= MAX_CACHE_LENGTH:
                self.cachedUsers = {}

            self.cachedUsers[id] = await self.bot.fetch_user(id)

        return self.cachedUsers[id]


message_limit = 2000


# The following method was generated with ChatGPT-4o
# As the ownership of this code is unclear and up for debate, I do not suggest
# making use of it as per the MIT license that applies to the rest of this
# program. I intend to remove this method in the future and replace it with
# something more accountable. Forgive me.
def page_message(message: str, limit: int = message_limit) -> list:
    def split_codeblock(message, limit):
        result = []
        in_codeblock = False
        temp = ''
        for line in message.splitlines(keepends=True):
            if line.startswith('```'):
                if in_codeblock:
                    temp += line
                    in_codeblock = False
                    if len(temp) > limit:
                        result.extend(split_line(temp, limit))
                    else:
                        result.append(temp)
                    temp = ''
                else:
                    if temp:
                        if len(temp) > limit:
                            result.extend(split_line(temp, limit))
                        else:
                            result.append(temp)
                        temp = ''
                    in_codeblock = True
                    temp += line
            else:
                if in_codeblock:
                    temp += line
                else:
                    if len(temp + line) > limit:
                        if temp:
                            result.append(temp)
                        temp = line
                    else:
                        temp += line

        if temp:
            result.append(temp)

        return result

    def split_line(line, limit):
        result = []
        while len(line) > limit:
            split_pos = line.rfind(' ', 0, limit)
            if split_pos == -1:
                split_pos = limit
            result.append(line[:split_pos])
            line = line[split_pos:].lstrip()
        if line:
            result.append(line)
        return result

    if len(message) <= limit:
        return [message]

    chunks = split_codeblock(message, limit)
    result = []
    for chunk in chunks:
        if len(chunk) > limit:
            result.extend(split_line(chunk, limit))
        else:
            result.append(chunk)
    return result