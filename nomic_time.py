from datetime import datetime, timedelta
import time
import calendar
import dateutil.parser
from config import PHASES_BY_DAY, PHASE_CYCLE, PHASE_START


def get_current_utc_string():
    now = utc_now()
    today = _midnightify(now)
    tomorrow = today + timedelta(days=1)

    time = now.strftime("%H:%M")
    weekday = now.strftime("%A")
    phase = PHASES_BY_DAY[weekday]
    nextPhase = PHASE_CYCLE[phase]
    nextDay = PHASE_START[nextPhase]

    if nextDay == tomorrow.strftime("%A"):
        secondstilmidnight = (tomorrow - now).seconds
        hours = secondstilmidnight // 3600
        minutes = (secondstilmidnight % 3600) // 60
        nextDay = f"*{nextDay}* (in *{hours} hours* and *{minutes} minutes*)"
    else:
        nextDay = f'*{nextDay}*'

    return (f'It is **{time}** on **{weekday}**, UTC\n')


def utc_now():
    # for debugging
    # return datetime(month=6, day=23, year=2021, hour=22, minute=13, second=6)

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


def get_timespan_from_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp) - utc_now()


def _midnightify(date):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def get_datestring_timestamp(datestring):
    if datestring is None or datestring == "" or datestring.lower() == 'now':
        return unix_now()

    return get_timestamp(dateutil.parser.parse(datestring))
