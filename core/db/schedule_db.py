from typing import List
from core.db.db_base import Database
from core.db.models.schedule_models import Schedule
from config.config import SQLITE3_DB_NAME, DB_TABLE_SCHEDULE_TASKS_NAME

db = Database(SQLITE3_DB_NAME)


def _create_table_schedule():
    '''
    Each Schedule in the Schedule table represents the time that a scheduled
    event should be triggered. DayOfThe* properties with higher specificity
    override properties with lower specificity.
    (i.e., DayOfTheWeek takes priority DayOfTheYear)

    Schedules that share the same ID will all be relevant triggers.
    For example, if you have two entries that share the same ID, and one entry
    has DayOfTheMonth set to 1 the other has DayOfTheMonth set to 15, the event
    will be triggered on the 1st and 15th.
    If a DayOfThe* property and the HourOfTheDay property are both defined, the
    latter will provide greater precision to the former.

    The LastActivated property of all events should be updated at the same time.
    When the Task Scheduler checks a particular event ID, it checks to see if
    the current timestamp has elapsed any of the expected NextActivations. When
    this happens, the task is triggered and the NextActivation property of the
    schedule is updated. If multiple schedules that share an id activate at
    once, the task is only triggered once, and all activations are updated.
    '''
    db.idempotent_add_table(
        '''
            ScheduleId      TEXT    NOT NULL,
            ScheduleName    TEXT    NOT NULL,
            ScheduleChannel TEXT,
            StartTimestamp  INT     NOT NULL,
            DayOfTheYear    INT,
            DayOfTheMonth   INT,
            DayOfTheWeek    INT,
            HourOfTheDay    INT,
            NextActivation  INT,
            Active          INT     NOT NULL    DEFAULT 1
        ''', DB_TABLE_SCHEDULE_TASKS_NAME
    )


def get_schedules(schedule_id=None) -> List[Schedule]:
    """
    Return a list of all active schedules, or active schedules with the given id

    :param schedule_id: The id for a list of schedules, defaults to None
    :return: A list of Schedule objects
    """
    results = None
    if schedule_id is None:
        results = db.get(
            f'''
            SELECT ScheduleId, ScheduleName, ScheduleChannel, StartTimestamp,
            DayOfTheYear, DayOfTheMonth, DayOfTheWeek, HourOfTheDay,
            NextActivation, Active
            FROM {DB_TABLE_SCHEDULE_TASKS_NAME}
            WHERE Active = 1
            '''
        )
    else:
        results = db.get(
            f'''
            SELECT ScheduleId, ScheduleName, ScheduleChannel, StartTimestamp,
            DayOfTheYear, DayOfTheMonth, DayOfTheWeek, HourOfTheDay,
            NextActivation, Active
            FROM {DB_TABLE_SCHEDULE_TASKS_NAME}
            WHERE Active = 1 AND ScheduleId = :schedule_id
            ''', [schedule_id]
        )

    schedules = []
    for r in results:
        schedules.append(Schedule(
            r['ScheduleId'],
            r['ScheduleName'],
            r['ScheduleChannel'],
            r['StartTimestamp'],
            r['DayOfTheYear'],
            r['DayOfTheMonth'],
            r['DayOfTheWeek'],
            r['HourOfTheDay'],
            r['NextActivation'],
            r['Active']
        ))

    return schedules


def add_schedule(schedule: Schedule) -> bool:
    """
    Add a schedule to the list of schedules. Not idempotent.

    :param schedule: The Schedule object to add to the database
    :return: A success value
    """
    return db.modify(
        f'''
        INSERT INTO {DB_TABLE_SCHEDULE_TASKS_NAME} (
            ScheduleId,
            ScheduleName,
            ScheduleChannel,
            StartTimestamp,
            DayOfTheYear,
            DayOfTheMonth,
            DayOfTheWeek,
            HourOfTheDay,
            NextActivation,
            Active
        )
        VALUES (
            :schedule_id,
            :schedule_name,
            :schedule_channel,
            :start_timestamp,
            :day_of_the_year,
            :day_of_the_month,
            :day_of_the_week,
            :hour_of_the_day,
            :next_activation,
            :active
        )
        ''', {
            'schedule_id': schedule.schedule_id,
            'schedule_name': schedule.schedule_name,
            'schedule_channel': schedule.schedule_channel,
            'start_timestamp': schedule.start_timestamp,
            'day_of_the_year': schedule.day_of_the_year,
            'day_of_the_month': schedule.day_of_the_month,
            'day_of_the_week': schedule.day_of_the_week,
            'hour_of_the_day': schedule.hour_of_the_day,
            'next_activation': schedule.next_activation,
            'active': schedule.active
        }
    )


# Maintenance Methods
def set_tables():
    _create_table_schedule()
