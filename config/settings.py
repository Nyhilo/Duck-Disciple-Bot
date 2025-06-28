from typing import List
from core.db import settings_db as db
from datetime import datetime, timezone


class Settings():
    def __init__(self):
        # Configure defaults for settings here
        if self.current_locale_key is None:
            self.current_locale_key = 'en-US'

        if self.current_cycle_start_date is None:
            self.current_cycle_start_date = datetime(2001, 1, 1)

        if self.current_cycle_phase_loop is None:
            self.current_cycle_phase_loop = [3, 4]

        if self.current_cycle_phase_names is None:
            self.current_cycle_phase_names = ['Phase I', 'Phase II']

    # Stores the value of the currently used locale
    @property
    def current_locale_key(self) -> str:
        return db.get_setting('current_locale_key')

    @current_locale_key.setter
    def current_locale_key(self, value):
        db.save_setting('current_locale_key', value)

    # A boolean toggle for whether Khronos should report on a running cycle
    @property
    def cycle_running(self) -> bool:
        val = db.get_setting('cycle_running')
        if val is None:
            return None

        return bool(int(val))

    @cycle_running.setter
    def cycle_running(self, value):
        db.save_setting('cycle_running', int(value))

    # The start date of the current cycle
    @property
    def current_cycle_start_date(self) -> datetime:
        val = db.get_setting('current_cycle_start_date')
        if val is None:
            return None
        return datetime.fromisoformat(val).replace(tzinfo=timezone.utc)

    @current_cycle_start_date.setter
    def current_cycle_start_date(self, value: datetime):
        db.save_setting('current_cycle_start_date', value.isoformat())

    # The cycle loop pattern
    @property
    def current_cycle_phase_loop(self) -> List[int]:
        val = db.get_setting('current_cycle_phase_loop')
        if val is None:
            return None
        return [int(v) for v in val.split(',')]

    @current_cycle_phase_loop.setter
    def current_cycle_phase_loop(self, value):
        db.save_setting('current_cycle_phase_loop', ','.join(str(v) for v in value))

    # The cycle phase names
    @property
    def current_cycle_phase_names(self) -> List[int]:
        val = db.get_setting('current_cycle_phase_names')
        if val is None:
            return None
        return [v for v in val.split(',')]

    @current_cycle_phase_names.setter
    def current_cycle_phase_names(self, value):
        db.save_setting('current_cycle_phase_names', ','.join(str(v) for v in value))


# Module-level constant for easy importing
settings = Settings()
