from enum import IntEnum
from datetime import datetime
from typing import Union

from core.nomic_time import get_datetime


class ReactionType(IntEnum):
    All = 1
    Limited = 2


class ReactionTracker():
    def __init__(
            self,
            channelId: int,
            trackingChannelId: int,
            reactionType: Union[int, ReactionType],
            validReactions: Union[str, list, None],
            created: Union[int, datetime],
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        '''Raw values taken from db table types'''

        self.id = id
        self.channelId = channelId
        self.trackingChannelId = trackingChannelId

        self.reactionType = reactionType if isinstance(reactionType, ReactionType) else ReactionType(reactionType)

        self.validReactions = None
        if validReactions is not None:
            self.validReactions = validReactions if isinstance(validReactions, list) else validReactions.split(',')

        self.created = created if isinstance(created, datetime) else get_datetime(created)

        self.active = bool(active)


class ReactionMessage():
    def __init__(
            self,
            trackingChannelId: int,
            messageId: int,
            created: Union[int, datetime],
            id: int = -1,
            active: Union[int, bool] = True) -> None:
        '''Raw values taken from db table types'''

        self.id = id
        self.trackingChannelId = trackingChannelId
        self.messageId = messageId

        self.created = created if isinstance(created, datetime) else get_datetime(created)

        self.active = bool(active)


class Action(IntEnum):
    Add = 1
    Remove = 2


class Reaction():
    def __init__(
            self,
            messageId: int,
            reaction: str,
            action: Union[int, Action],
            userId: int,
            userName: str,
            created: Union[int, datetime],
            id: int = -1) -> None:
        '''Raw values taken from db table types'''

        self.id = id
        self.messageId = messageId
        self.reaction = reaction

        self.action = action if isinstance(action, Action) else Action(action)

        self.userId = userId
        self.userName = userName

        self.created = created if isinstance(created, datetime) else get_datetime(created)
