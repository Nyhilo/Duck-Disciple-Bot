from enum import IntEnum


class Reoccur(IntEnum):
    NONE = 0
    DAILY = 1
    BIDAILY = 2
    WEEKLY = 3
    FORNIGHTLY = 4
    MONTHLY = 5
    MONTHEND = 6
    YEARLY = 7
    YEAREND = 8
