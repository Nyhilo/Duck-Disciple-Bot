import core.utils as utils
import core.db.schedule_db as db
from core.db.models.schedule_models import Schedule


def list_schedules(userId: int) -> str:
    """
    Return a formatted list of all available schedules.

    :param userId: Id of the user calling the command.
    :return: Formatted list of all available schedules.
    """
    if not utils.is_admin(userId):
        return None

    return _list_schedules()


def _list_schedules():
    schedules = db.get_schedules()

    sched_list = '\n'.join([
        (f'{s.schedule_id}\t{s.schedule_name}\t{s.start_timestamp}\t'
         f'{s.day_of_the_year}\t{s.day_of_the_month}\t{s.day_of_the_week}\t'
         f'{s.hour_of_the_day}') for s in schedules
    ])

    msg = (
        'Here are the current active schedules:\n'
        '```\n'
        'Id\tName\tTimestamp\tDay of Year\tDay of Month\tDay of Week\tHour of Day\n'
        f'{sched_list}\n'
        '```'
    )

    return msg


def add_schedule(userId: int, id: str, name: str, channel: str, start_timestamp: int,
                 day_of_year: int, day_of_month: int, day_of_week: int,
                 hour_of_day: int) -> str:

    if not utils.is_admin(userId):
        return None

    return _add_schedule(id, name, channel, start_timestamp, day_of_year,
                         day_of_month, day_of_week, hour_of_day)


def _add_schedule(id: str, name: str, channel: str, start_timestamp: int,
                  day_of_year: int, day_of_month: int, day_of_week: int,
                  hour_of_day: int) -> str:

    schedule = Schedule(id, name, channel, start_timestamp, day_of_year,
                        day_of_month, day_of_week, hour_of_day)

    db.add_schedule(schedule)
