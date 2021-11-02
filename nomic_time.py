from datetime import datetime, timedelta
import time
import calendar
from config import PHASES_BY_DAY, PHASE_CYCLE, PHASE_START


def get_current_utc_string():
    now = utc_now()
    today = _midnightify(now)

    time = now.strftime('%H:%M')
    weekday = now.strftime('%A')
    phase = PHASES_BY_DAY[weekday]
    nextPhase = PHASE_CYCLE[phase]
    nextDay = PHASE_START[nextPhase]
    nextDayTimestampStr = ''
    nextDayRelativeTimestampStr = ''

    for _daysTil in range(8):
        nextDayDatetime = (today + timedelta(days=_daysTil))
        nextDayTimestamp = get_timestamp(nextDayDatetime)
        if nextDayDatetime.strftime('%A') == nextDay:
            nextDayRelativeTimestampStr = f'<t:{nextDayTimestamp}:R>'
            nextDayTimestampStr = f'<t:{nextDayTimestamp}:F>'
            break

    return (f'It is **{time}** on **{weekday}**, UTC\n'
            f'That means it is **{phase}**\n\n'
            f'**{nextPhase}** starts on **{nextDay}**, which is roughly {nextDayRelativeTimestampStr}.\n'
            f'That is {nextDayTimestampStr} your time.')


def utc_now():
    # for debugging
    # return datetime(month=11, day=3, year=2021, hour=15, minute=41, second=6)

    return datetime.utcnow()


def unix_now():
    '''Returns the current unix timestamp in seconds.'''
    return int(time.time())


def get_timestamp(date: datetime):
    return int(calendar.timegm(date.utctimetuple()))


def _now():
    return datetime.now()


def parse_timespan_by_units(number, unit):
    if unit.lower().startswith('sec'):
        return timedelta(seconds=number)

    if unit.lower().startswith('min'):
        return timedelta(minutes=number)

    if unit.lower().startswith('hour'):
        return timedelta(hours=number)

    if unit.lower().startswith('day'):
        return timedelta(days=number)

    if unit.lower().startswith('week'):
        return timedelta(weeks=number)

    return None


def _midnightify(date):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)
