from core.reminders import _get_reoccurrence_datetime
from core.enums import Reoccur
from datetime import datetime, timezone


def test_daily():
    reoccur = Reoccur.DAILY

    originalTime = datetime(year=2025, month=1, day=1, hour=5, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=3, hour=5, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=2, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=4, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=4, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=4, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime


def test_bidaily():
    reoccur = Reoccur.BIDAILY

    originalTime = datetime(year=2025, month=1, day=1, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=5, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=5, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=2, hour=5, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=4, hour=5, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=5, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime


def test_weekly():
    reoccur = Reoccur.WEEKLY

    originalTime = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=10, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=10, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=11, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=17, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime


def test_fornightly():
    reoccur = Reoccur.FORNIGHTLY

    originalTime = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=17, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=17, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=18, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=31, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime



def test_monthly():
    reoccur = Reoccur.MONTHLY

    originalTime = datetime(year=2025, month=1, day=3, hour=2, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=2, day=3, hour=2, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=3, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=2, day=3, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=31, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=2, day=28, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=3, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=3, day=31, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=4, day=30, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=3, day=31, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=3, day=31, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=4, day=30, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2024, month=1, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2024, month=1, day=31, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2024, month=2, day=29, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=31, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=4, day=30, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=5, day=31, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2024, month=12, day=3, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=1, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2024, month=12, day=3, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=4, day=1, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=4, day=3, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime


def test_monthend():
    reoccur = Reoccur.MONTHEND

    originalTime = datetime(year=2025, month=1, day=2, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=1, day=31, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=2, day=2, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=2, day=3, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=2, day=28, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=31, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=2, day=28, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=31, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=31, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=2, day=28, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=2, day=1, hour=4, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=2, day=2, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=2, day=28, hour=4, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=2, day=28, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=3, day=31, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=3, day=30, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=3, day=31, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=1, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=4, day=30, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=5, day=31, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime


def test_yearly():
    reoccur = Reoccur.YEARLY

    originalTime = datetime(year=2025, month=1, day=1, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=1, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2026, month=1, day=1, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2023, month=2, day=28, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2024, month=2, day=29, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=2, day=28, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=12, day=31, hour=23, minute=59, second=58, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=12, day=31, hour=23, minute=59, second=59, tzinfo=timezone.utc)
    expectedTime = datetime(year=2026, month=12, day=31, hour=23, minute=59, second=58, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime


def test_yearend():
    reoccur = Reoccur.YEAREND

    originalTime = datetime(year=2025, month=1, day=1, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=1, day=1, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2025, month=12, day=31, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=12, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=12, day=31, hour=4, tzinfo=timezone.utc)
    expectedTime = datetime(year=2026, month=12, day=31, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime

    originalTime = datetime(year=2025, month=12, day=31, hour=3, tzinfo=timezone.utc)
    now          = datetime(year=2025, month=12, day=31, hour=3, tzinfo=timezone.utc)
    expectedTime = datetime(year=2026, month=12, day=31, hour=3, tzinfo=timezone.utc)
    newTime = _get_reoccurrence_datetime(reoccur, originalTime, now)

    assert newTime == expectedTime
