from datetime import datetime, timedelta
from config import PHASES_BY_DAY, PHASE_CYCLE, PHASE_START


def get_current_utc_string():
    now = _now()
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

    return (f'It is **{time}** on **{weekday}**, UTC\n'
            f'That means it is the **{phase}**\n'
            f'The *{nextPhase}* starts on {nextDay}')


def _now():
    # for debugging
    # return datetime(month=6, day=23, year=2021, hour=22, minute=13, second=6)

    return datetime.utcnow()


def _midnightify(date):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)
