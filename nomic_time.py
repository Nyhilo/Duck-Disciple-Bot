from datetime import datetime


def get_current_utc_string():
    utc = datetime.utcnow()

    time = utc.strftime("It is **%H:%M** on **%A**, UTC")

    return f'{time}'
