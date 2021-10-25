from datetime import datetime, timedelta
import db
import nomic_time
from log import log
from config import PREFIX, SERVER_ADMIN_IDS


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
        log.error(f'User gave a bad rowId to delete: "{rowId}"')
        return 'That is not a valid reminder Id. Please send the integer Id of a reminder that has been made before'

    _reminders = db.get_reminders(f'WHERE RowId = {rowId}')
    if len(_reminders) == 0:
        return 'No reminder found with id {rowId}.'

    reminder = _reminders[0]
    remindAfter = reminder['RemindAfter']
    remindMsg = reminder['RemindMsg']

    return (f"Reminder set to trigger <t:{remindAfter}:R>\n"
            f"> {remindMsg}")


def unset_reminder(rowId, requesterId=None, overrideId=False):
    '''Either requesterId or overrideId must be set.'''
    try:
        # Also accounts for sql injection attempts
        rowId = int(rowId)
    except ValueError:
        log.error(f'User gave a bad rowId to delete: "{rowId}"')
        return 'That is not a valid reminder Id. Please send the integer Id of a reminder that has been made before'

    reminders = db.get_reminders(f'WHERE rowid = {rowId}')
    if len(reminders) == 0:
        return 'No reminder found with id {rowId}.'

    if reminders[0]['Active'] == 0:
        return f'Reminder {rowId} is old and wasn\'t going to trigger anyway'

    if overrideId or str(requesterId) == reminders[0]['UserId'] or requesterId in SERVER_ADMIN_IDS:
        if db.unset_reminder(rowId):
            return f'You will no longer be reminded of reminder number {rowId}.'
        else:
            return 'An error occured trying to delete this reminder. Oof.'
    else:
        return 'Only an admin or the person who created a reminder can delete it.'


def parse_remind_message(msg):
    # Parse the timestamp as <integer> <minutes|hours|days|weeks|months>
    parts = msg.split(' ')
    if len(parts) < 2:
        return (None, f'Incorrect syntax for reminder. See `{PREFIX}help remind` for more details.')

    try:
        number = int(parts[0])
    except ValueError:
        return (None, 'Please enter an integer number of time units.')

    timeUnit = parts[1]
    remindMsg = None if len(parts) < 2 else ' '.join(parts[2:])

    span = nomic_time.parse_timespan_by_units(number, timeUnit)

    if not span:
        return (None, 'Please specify a time in the form of `<number> <second(s)|minute(s)|hour(s)|day(s)|week(s)>.`')

    return (span, remindMsg)


def can_quick_remind(span: timedelta):
    return span.total_seconds() < 60 * 10
