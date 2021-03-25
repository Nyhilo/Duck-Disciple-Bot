from datetime import datetime

from config import VOTING_PERIOD_NAMES as PERIOD


def get_current_utc_string():
    utc = datetime.utcnow()

    time = utc.strftime("It is **%H:%m** on **%A**, UTC")
    day = utc.strftime("%A")
    voting_period = PERIOD[day]

    return f'{time}\nIt is currently **Voting Period {voting_period}**'
