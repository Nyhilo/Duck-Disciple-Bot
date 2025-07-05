from enum import Enum


class Reoccur(Enum):
    NONE = 0
    DAILY = 1
    BIDAILY = 2
    WEEKLY = 3
    FORNIGHTLY = 4
    MONTHLY = 5
    MONTHEND = 6
    BIMONTHLY = 7
    SEMIYEARLY = 8
    YEARLY = 9
    YEAREND = 10
