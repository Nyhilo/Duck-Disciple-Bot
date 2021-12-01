from datetime import datetime, timedelta
import re

import db
import nomic_time
from log import log
from config import PREFIX
import utils


def set_new_reminder(userId: str,
                     messageId: int,
                     channelId: int,
                     createdAt: datetime,
                     remindAfter: timedelta,
                     remindMsg: str):
    '''CreatedAt and remindAfter should be a UTC timestamp in seconds'''

    _createdAt = nomic_time.get_timestamp(createdAt)
    _remindAfter = nomic_time.get_timestamp(createdAt + remindAfter)

    rowId = db.add_reminder(userId, messageId, channelId, _createdAt, _remindAfter, remindMsg)

    if rowId:
        return(f'I\'ll remind you about this at about <t:{_remindAfter}>.\n'
               f'Use `{PREFIX}forget {rowId}` to delete this reminder.\n')

    else:
        return 'An error occured trying to set this reminder :(. Some kind of reminder database issue.'


def check_for_triggered_reminders():
    '''
    Returns a list of dictionaries [{RowId, MessageId, ReplyMessage}]
    '''
    reminders = db.get_reminders(f'WHERE Active = 1 AND RemindAfter <= {nomic_time.unix_now()}')

    return reminders


def get_reminder(rowId):
    try:
        # Also accounts for sql injection attempts
        rowId = int(rowId)
    except ValueError:
        log.exception(f'User gave a bad rowId to delete: "{rowId}"')
        return 'That is not a valid reminder Id. Please send the integer Id of a reminder that has been made before'

    _reminders = db.get_reminders(f'WHERE RowId = {rowId}')
    if len(_reminders) == 0:
        return 'No reminder found with id {rowId}.'

    reminder = _reminders[0]
    remindAfter = reminder['RemindAfter']
    remindMsg = reminder['RemindMsg']

    return (f"Reminder set to trigger <t:{remindAfter}:R>\n"
            f"> {remindMsg}")


def unset_reminder(rowId, requesterId=None, serverId=None, overrideId=False):
    '''Either requesterId or overrideId must be set.'''
    try:
        # Also accounts for sql injection attempts
        rowId = int(rowId)
    except ValueError:
        log.exception(f'User gave a bad rowId to delete: "{rowId}"')
        return 'That is not a valid reminder Id. Please send the integer Id of a reminder that has been made before'

    reminders = db.get_reminders(f'WHERE rowid = {rowId}')
    if len(reminders) == 0:
        return 'No reminder found with id {rowId}.'

    if reminders[0]['Active'] == 0:
        return f'Reminder {rowId} is old and wasn\'t going to trigger anyway'

    if overrideId or str(requesterId) == reminders[0]['UserId'] or utils.is_admin(requesterId, serverId):
        if db.unset_reminder(rowId):
            return f'You will no longer be reminded of reminder number {rowId}.'
        else:
            return 'An error occured trying to delete this reminder. Oof.'
    else:
        return 'Only an admin or the person who created a reminder can delete it.'


def parse_remind_message(_msg, createdAt=None):
    msg = _msg
    span = None
    timestamp = None

    # Check if we were just given a timestamp
    criteria = r'^\s*<?t?:?(\d{10})'
    if re.match(criteria, _msg):
        try:
            timestamp = int(re.match(criteria, _msg).group(1))
            span = nomic_time.get_timespan_from_timestamp(timestamp, createdAt)
            parts = _msg.split(' ')
            msg = ' '.join(parts[1:])
        except Exception:
            timestamp = None

    # Check if we have an arbitrary date format on our hands
    if timestamp is None and ';' in _msg:
        parts = _msg.split(';')
        datestring, msg = parts[0], ';'.join(parts[1:])
        try:
            timestamp = int(nomic_time.get_datestring_timestamp(datestring))
            span = nomic_time.get_timespan_from_timestamp(timestamp, createdAt)
        except Exception:
            timestamp = None

    # If we still don't have a timestamp, parse it by relative time
    if timestamp is None:
        # Parse the timestamp as <integer> <minutes|hours|days|weeks|months>
        parts = msg.split(' ')

        # The time unit might have a newline after it instead of a space.
        # i.e ['1', 'second\nThis\nmessage', 'here'] should be ['1', 'second', 'This\message', 'here']
        if len(parts) > 1 and '\n' in parts[1]:
            # subparts = ['second', 'This', 'message]
            subparts = parts[1].split('\n')
            # 'second', 'This\nmessage'
            timepart, firstWord = subparts[0], '\n'.join(subparts[1:])
            # parts = ['1', 'second', 'here']
            parts[1] = timepart
            # ['1', 'second', 'This\message', 'here']
            parts.insert(2, firstWord)

        if len(parts) < 2:
            return (None, ('Incorrect syntax for reminder or I couldn\'t understand your date format. '
                           'See `{PREFIX}help remind` for more details.'))

        try:
            number = float(parts[0])
        except ValueError:
            return (None, ('Couldn\'t understand your time format. '
                           'You might have an extra comma in there confusing things. '
                           f'See `{PREFIX}help remind` for more details.'))

        timeUnit = parts[1]
        span = nomic_time.parse_timespan_by_units(number, timeUnit)

        msg = None if len(parts) < 2 else ' '.join(parts[2:])

    if not span:
        return (None, f'Incorrect syntax for reminder. See `{PREFIX}help remind` for more details.')

    if span.total_seconds() < 1:
        return (None, 'Please give a time that is in the future (remember that times are in UTC).')

    return (span, msg)


def can_quick_remind(span: timedelta):
    return span.total_seconds() < 60 * 10
