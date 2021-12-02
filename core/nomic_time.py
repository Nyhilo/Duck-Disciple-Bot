from datetime import datetime, timedelta, timezone
import time
import calendar
import dateutil.parser

from config.config import PHASES_BY_DAY, _phase_two, PHASE_CYCLE, PHASE_START, PHASE_START_DATE
import core.utils as utils


def get_current_utc_string():
    # Okay there's a lot going on here
    # Get some base reference values
    now = utc_now()
    today = _midnightify(now)
    _startYear, _startMonth, _startDay = PHASE_START_DATE
    phaseCountStart = datetime(_startYear, _startMonth, _startDay, tzinfo=timezone.utc)

    # Get string representations of the current time and day
    time = now.strftime('%H:%M')
    weekday = now.strftime('%A')

    # Figure out what phase it is
    _phase = PHASES_BY_DAY[weekday]
    _nextPhase = PHASE_CYCLE[_phase]

    # I don't remember why these -1s and +1s work, but the do so... ¯\_(ツ)_/¯
    weeksSinceStart = ((now - phaseCountStart).days // 7) + 1
    phasesSinceStart = weeksSinceStart * 2 + (0 if _phase == _phase_two else -1)
    phase = 'Phase ' + utils.roman_numeralize(phasesSinceStart)
    nextPhase = 'Phase ' + utils.roman_numeralize(phasesSinceStart + 1)
    nextDay = PHASE_START[_nextPhase]

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
    # return datetime(month=11, day=14, year=2021, hour=23, minute=59, second=1).replace(tzinfo=timezone.utc)

    return datetime.utcnow().replace(tzinfo=timezone.utc)


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


def get_timespan_from_timestamp(timestamp, now=None):
    if not now:
        now = utc_now()

    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc) - now.replace(tzinfo=timezone.utc)


def _midnightify(date):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def get_datestring_timestamp(datestring):
    if datestring is None or datestring == "" or datestring.lower() == 'now':
        return unix_now()

    return get_timestamp(dateutil.parser.parse(datestring))
