from datetime import datetime, timedelta
import db
import nomic_time
from log import log
from config import PREFIX, SERVER_ADMIN_IDS


def set_new_reminder(userId: str, messageId: int, createdAt: datetime, remindAfter: timedelta, remindMsg: str):
    '''CreatedAt and remindAfter should be a UTC timestamp in seconds'''

    rowId = db.add_reminder(userId, messageId, createdAt.seconds, remindAfter.seconds, remindMsg)

    if rowId:
        return(f'I\'ll remind you about the following message after <t:{remindAfter}>\n'
               f'{remindMsg}')

    else:
        return 'An error occured trying to set this reminder :(. Some kind of reminder database issue.'


def check_for_triggered_reminders():
    '''
    Returns a list of dictionaries [{RowId, MessageId, ReplyMessage}]
    '''
    reminders = db.get_reminders('WHERE Active = 1')

    if reminders:
        return [
            {'RowId': d['RowId'], 'MessageId': d['MessageId'], 'ReplyMessage': d['ReplyMessage']}
            for d in reminders
        ]


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

    reminders = db.get_reminders(f'WHERE RowId = {rowId}')
    if len(reminders) == 0:
        return 'No reminder found with id {rowId}.'

    if requesterId == reminders[0] or requesterId in SERVER_ADMIN_IDS:
        if db.update_reminder(rowId):
            return f'You will no longer be reminded of reminder number {rowId}.'
        else:
            return 'An error occured trying to delete this reminder. Oof.'
    else:
        return 'Only an admin or the person who created a reminder can delete it.'


def parse_remind_message(msg):
    # Parse the timestamp as <integer> <minutes|hours|days|weeks|months>
    parts = msg.split(' ')
    if len(parts) < 3:
        return (None, f'Incorrect syntax for reminder. See `{PREFIX}help remind` for more details.')

    try:
        number = int(parts[0])
    except ValueError:
        return (None, 'Please enter an integer number of time units.')

    timeUnit = parts[1]
    remindMsg = ' '.join(parts[2:])

    span = nomic_time.parse_timespan_by_units(number, timeUnit)

    return (span, remindMsg)
