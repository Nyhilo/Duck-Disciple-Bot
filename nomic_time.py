from datetime import datetime
from config import PHASES_BY_DAY, PHASE_CYCLE, PHASE_START


def get_current_utc_string():
    utc = datetime.utcnow()

    time = utc.strftime("%H:%M")
    weekday = utc.strftime("%A")
    phase = PHASES_BY_DAY[weekday]
    nextPhase = PHASE_CYCLE[phase]
    nextDay = PHASE_START[nextPhase]

    return (f'It is **{time}** on **{weekday}**, UTC\n'
            f'That means it is the **{phase}**\n'
            f'The *{nextPhase}* starts on *{nextDay}*')
