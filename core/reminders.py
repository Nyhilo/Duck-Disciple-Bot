from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re

from core.log import log
from core.db import reminders_db as db
from core import nomic_time, utils, language
from core.enums import Reoccur
from config.config import PREFIX, QUICK_REMIND_SECONDS_THRESHOLD

locale = language.Locale('core.reminders')


def set_new_reminder(userId: str,
                     messageId: int,
                     channelId: int,
                     createdAt: datetime,
                     remindAfter: timedelta,
                     remindMsg: str,
                     reoccur: Reoccur):
    '''CreatedAt and remindAfter should be a UTC timestamp in seconds'''

    _createdAt = nomic_time.get_timestamp(createdAt)
    _remindAfter = nomic_time.get_timestamp(createdAt + remindAfter)

    _originalRemindAfter = _remindAfter if reoccur != Reoccur.NONE else None

    rowId = db.add_reminder(userId, messageId, channelId,
                            _createdAt, _remindAfter, remindMsg, reoccur, _originalRemindAfter)

    _remindAfterFormatted = f'<t:{_remindAfter}>'

    if rowId:
        if reoccur is None or reoccur == Reoccur.NONE:
            return (locale.get_string('reminderSetShort',
                                      timestamp=_remindAfterFormatted, prefix=PREFIX, rowId=rowId))
        else:
            r_type = {
                1: 'Daily',
                2: 'Bi-Daily',
                3: 'Weekly',
                4: 'Fornightly',
                5: 'Monthly',
                6: 'Month-end',
                7: 'Yearly',
                8: 'Year-end'
            }[reoccur]
            return locale.get_string('reoccurSetShort',
                                     remindAfter=_remindAfterFormatted,
                                     remindReoccur=r_type,
                                     prefix=PREFIX,
                                     rowId=rowId)

    else:
        return locale.get_string('reminderError')


def check_for_triggered_reminders():
    '''
    Returns a list of dictionaries [{RowId, MessageId, ReplyMessage}]
    '''
    reminders = db.get_reminders(
        f'WHERE Active = 1 AND RemindAfter <= {nomic_time.unix_now()}')

    return reminders


def refresh_reoccuring_reminder(reminder):
    '''Sets a new timestamp on the reminder depending on the reoccur value'''
    rowId = reminder['rowid']
    originalTime = nomic_time.get_datetime(reminder['OriginalTimestamp'])
    reoccur = Reoccur(reminder['Reoccur'])

    nextDatetime = _get_reoccurrence_datetime(reoccur, originalTime, nomic_time.utc_now())
    db.update_remindAfter(rowId, nomic_time.get_timestamp(nextDatetime))


def _get_reoccurrence_datetime(reoccur, originalTime, now):
    match reoccur:
        case Reoccur.DAILY:
            delta = now - originalTime
            interval = timedelta(days=1)
            intervals_passed = (delta.total_seconds() // interval.total_seconds()) + 1
            next_occurrence = originalTime + interval * intervals_passed

            return next_occurrence

        case Reoccur.BIDAILY:
            delta = now - originalTime
            interval = timedelta(days=2)
            intervals_passed = (delta.total_seconds() // interval.total_seconds()) + 1
            next_occurrence = originalTime + interval * intervals_passed

            return next_occurrence

        case Reoccur.WEEKLY:
            delta = now - originalTime
            interval = timedelta(days=7)
            intervals_passed = (delta.total_seconds() // interval.total_seconds()) + 1
            next_occurrence = originalTime + interval * intervals_passed

            return next_occurrence

        case Reoccur.FORNIGHTLY:
            delta = now - originalTime
            interval = timedelta(days=14)
            intervals_passed = (delta.total_seconds() // interval.total_seconds()) + 1
            next_occurrence = originalTime + interval * intervals_passed

            return next_occurrence

        case Reoccur.MONTHLY:
            newTime = originalTime.replace(month=1, year=now.year)
            monthCounter = 1
            while newTime <= now:
                newTime = originalTime + relativedelta(months=monthCounter)
                monthCounter += 1

            return newTime

        case Reoccur.MONTHEND:
            newTime = originalTime.replace(day=31, month=1, year=now.year)
            print(newTime)
            monthCounter = 1
            year = now.year
            while newTime <= now:
                if monthCounter == 13:
                    monthCounter = 1
                    year += 1
                    originalTime.replace(year=now.year)
                print(monthCounter)
                newTime = originalTime + relativedelta(month=monthCounter)
                print(newTime)
                monthCounter += 1

            return newTime

        case Reoccur.YEARLY:
            newTime = originalTime.replace(year=now.year)

            if newTime <= now:
                newTime = originalTime.replace(year=now.year+1)

            return newTime

        case Reoccur.YEAREND:
            if now.month == 12 and now.day == 31:
                return originalTime.replace(year=now.year+1, month=12, day=31)

            return originalTime.replace(year=now.year, month=12, day=31)


def get_reminder(rowId):
    try:
        # Also accounts for sql injection attempts
        rowId = int(rowId)
    except ValueError:
        log.exception(f'User gave a bad rowId to delete: "{rowId}"')
        return locale.get_string('idInvalidError')

    _reminders = db.get_reminders(f'WHERE RowId = {rowId}')
    if len(_reminders) == 0:
        return locale.get_string('noReminderIdError', rowId=rowId)

    reminder = _reminders[0]
    remindAfter = f'<t:{reminder["RemindAfter"]}:R>'
    remindMsg = reminder['RemindMsg']

    remindReoccur = ''
    reoccurence = Reoccur(reminder['Reoccur'])
    if reoccurence != 0:
        remindReoccur = f', and to reoccur {reoccurence.name.lower()}'

    return locale.get_string('reminderSetLong',
                             remindAfter=remindAfter,
                             remindReoccur=remindReoccur,
                             remindMsg=remindMsg)


def unset_reminder(rowId, requesterId=None, serverId=None, overrideId=False):
    '''Either requesterId or overrideId must be set.'''
    try:
        # Also accounts for sql injection attempts
        rowId = int(rowId)
    except ValueError:
        log.exception(f'User gave a bad rowId to delete: "{rowId}"')
        return locale.get_string('idInvalidError')

    reminders = db.get_reminders(f'WHERE rowid = {rowId}')
    if len(reminders) == 0:
        return locale.get_string('noReminderIdError', rowId=rowId)

    if reminders[0]['Active'] == 0:
        return locale.get_string('reminderExpired', rowId=rowId)

    if overrideId or str(requesterId) == reminders[0]['UserId'] or utils.is_admin(requesterId, serverId):
        if db.unset_reminder(rowId):
            return locale.get_string('deleteSuccess', rowId=rowId)
        else:
            return locale.get_string('deleteError')
    else:
        return locale.get_string('deleteUnauthorized')


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
            return (None, locale.get_string('incorrectSyntax1', prefix=PREFIX))

        try:
            number = float(parts[0])
        except ValueError:
            return (None, locale.get_string('incorrectSyntax2', prefix=PREFIX))

        timeUnit = parts[1]
        span = nomic_time.parse_timespan_by_units(number, timeUnit)

        msg = None if len(parts) < 2 else ' '.join(parts[2:])

    if not span:
        return (None, locale.get_string('incorrectSyntaxGeneric', prefix=PREFIX))

    if span.total_seconds() < 1:
        return (None, locale.get_string('attemptedTimeTravelError'))

    return (span, msg)


def can_quick_remind(span: timedelta):
    return span.total_seconds() < QUICK_REMIND_SECONDS_THRESHOLD
