from core import sha as shalib, utils
from config.config import PREFIX, MESSAGE_LIMIT

from core import language
locale = language.Locale('core.secret_keeping')


def format_secret_reply(message: str) -> str:
    filteredMessage = utils.trim_quotes(message)
    hash = shalib.get_sha_256(filteredMessage)
    reply = ''

    if '```' in filteredMessage:
        reply += locale.get_string('backticksDetected') + '\n\n'

    if _will_message_split_codeblock(reply, filteredMessage, hash):
        reply += locale.get_string('messageRealLong') + '\n\n'

    reply += locale.get_string('secretReply', hash=hash, prefix=PREFIX, msg=filteredMessage)

    return reply


def _will_message_split_codeblock(replyBlock: str, message: str, hash: str) -> bool:
    testMessage = replyBlock + locale.get_string('secretReply', hash=hash, prefix=PREFIX, msg=message)
    messageOverflowLimit = MESSAGE_LIMIT - len(testMessage)

    return len(message) >= messageOverflowLimit
