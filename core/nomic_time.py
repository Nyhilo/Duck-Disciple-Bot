import discord

from datetime import datetime, timedelta, timezone
import time
import calendar
from dateutil import parser
from dateutil.relativedelta import relativedelta
from math import ceil

from config.config import PHASE_START_DATE, PHASE_GROUPS
import core.utils as utils

_d = PHASE_START_DATE
START_DATE = datetime(year=_d[0], month=_d[1], day=_d[2], tzinfo=timezone.utc)


def get_current_utc_string():
    # Okay there's a lot going on here
    # Get some base reference values
    now = utc_now()

    # Get string representations of the current time and day
    time = now.strftime('%H:%M')
    weekday = now.strftime('%A')

    # Figure out what phase it is
    _phase = _get_phase(now)
    _nextPhase = _phase + 1

    # Get the names of the needed phases
    phase = _get_phase_name(_phase)
    nextPhase = _get_phase_name(_nextPhase)

    # Day of the week for the next phase's beginning
    nextDayDt = _get_date_from_phase(_nextPhase)
    nextDay = nextDayDt.strftime('%A')
    nextDayTimestamp = get_timestamp(nextDayDt)

    # Discord-formatted timestamp strings
    nextDayRelativeTimestampStr = f'<t:{nextDayTimestamp}:R>'
    nextDayTimestampStr = f'<t:{nextDayTimestamp}:F>'

    return (f'It is **{time}** on **{weekday}**, UTC\n'
            f'That means it is **{phase}**\n\n'
            f'*{nextPhase}* starts on *{nextDay}*, which is roughly '
            f'{nextDayRelativeTimestampStr}.\n'
            f'That is {nextDayTimestampStr} your time.')


#################################
# Phase Determination Functions #
#################################

def _get_phase(date: datetime) -> int:
    """
    Retrieve the current phase, given the value of utc_now()
    """
    # This is the total length in days after iterating through all the phases in
    # a "loop" or "group". i.e. [3, 2, 2] is a full week (7 days)
    phase_group_len = sum(PHASE_GROUPS)

    # This will how phase groups are divided
    num_phases_per_group = len(PHASE_GROUPS)

    # We want to know how long it's been since we started the cycle.
    days_since_beginning = (date - START_DATE).days

    # This "rounds down" the days to the most recent full phase group
    # for instance, (20 // 7) * 7 = 18
    phases_since = (days_since_beginning // phase_group_len) * num_phases_per_group

    # I don't know why this -1 works, but it fixes an inconsistent off-by-one error
    days_since = ((days_since_beginning // phase_group_len) * phase_group_len) - 1

    # Add phases to the running total until we get to today
    for group in PHASE_GROUPS:
        phases_since += 1
        days_since += group
        if days_since >= days_since_beginning:
            break

    return phases_since


def _get_date_from_phase(phase: int) -> str:
    """
    Get a datetime for the day that a given phase falls on

    :param phase: _description_
    :return: _description_
    """
    phases_per_group = len(PHASE_GROUPS)

    days_since = 0
    count = 0

    # Iterate through the phase lengths until we get to the start day of the phase
    while count < (phase-1):
        days_since += PHASE_GROUPS[count % phases_per_group]
        count += 1

    return START_DATE + relativedelta(days=days_since)


def _get_phase_name(phase: int) -> str:
    if phase < 1:
        minus = '-' if phase < 0 else ''
        phase_ = f'{minus}{utils.roman_numeralize(abs(phase))}'
        phase__ = f'-{utils.roman_numeralize(abs(phase - 1))}'
        return f'Phase {phase_}, (or is it Phase {phase__}?)'

    return 'Phase ' + utils.roman_numeralize(phase)


################################
# Scheduling Related Utilities #
################################

def get_formatted_date_string(timestamp: int = None) -> str:
    '''
    Gets a formatted datestring for the given timestamp. Returns the time string
     for the current time if no timestamp is given. Rounds down to the nearest
     10 minutes.

    :param timestamp: UTC timestamp, defaults to None
    :return: Formatted datetime string
    '''
    timestamp = timestamp if timestamp is not None else get_timestamp(utc_now())
    format = '%a %b %d, %H:%M UTC'

    msg = datetime.utcfromtimestamp(timestamp).strftime(format)

    # "round down" to the nearest 10 minutes if we happen to grab this at an odd time
    # NOTE: The index on this part may change if time format changes
    msg_ = list(msg)
    msg_[-5] = '0'
    msg = ''.join(msg_)

    return msg


def get_current_phase_string():
    '''
    Get the string for the current phase right now.
    '''
    if utc_now().day < 15:
        return 'Cycle 13 Starts Oct 16!'

    if utc_now().day < 16:
        return 'Cycle 13 Starts Soon!'

    # TODO: Actually calculate the loop here
    return 'First Loop, ' + _get_phase_name(_get_phase(utc_now()))


def get_minutes_to_next_phase() -> int:
    '''
    Get the number of integer minutes to the next phase. This is expected to be
     converted to an HH:MM format so something similar.
    '''
    current_phase = _get_phase(utc_now())
    next_phase_date = _get_date_from_phase(current_phase + 1)
    minutes = (next_phase_date - utc_now()).total_seconds() // 60

    return minutes


def get_next_time_to_phase_end_string():
    minutes = get_minutes_to_next_phase()
    if minutes <= 60:
        return f'Phase ends in {((minutes // 10) + 1) * 10} min'

    return f'Phase ends in {ceil(minutes/60)} hrs'


def seconds_to_next_10_minute_increment():
    '''
    See function name.
    '''
    now = utc_now()
    if now.minute % 10 == 0:
        return 0

    next_minute = ((now.minute // 10) + 1)*10
    return (next_minute * 60) - ((now.minute * 60) + now.second) + 1


def seconds_to_next_day():
    now = utc_now()

    # Adds 1 day, then replaces the clock time to bring us to 00:00 UTC
    tomorrow = now + relativedelta(days=1) + relativedelta(hour=0, minute=0, second=0)
    return (tomorrow - now).seconds


#####################
# General Utilities #
#####################

def utc_now():
    # for debugging
    # return datetime(month=10, day=21, year=2022, hour=0, minute=59, second=1).replace(tzinfo=timezone.utc)

    return discord.utils.utcnow()


def unix_now():
    '''Returns the current unix timestamp in seconds.'''
    return int(time.time())


def get_timestamp(date: datetime):
    return int(calendar.timegm(date.utctimetuple()))


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


######################
# Timstamp Utilities #
######################

def get_timespan_from_timestamp(timestamp, now=None):
    if not now:
        now = utc_now()

    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc) - now.replace(tzinfo=timezone.utc)


def get_datestring_timestamp(datestring):
    if datestring is None or datestring == "" or datestring.lower() == 'now':
        return unix_now()

    return get_timestamp(parser.parse(datestring))
