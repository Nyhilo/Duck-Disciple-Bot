from enum import IntEnum
from datetime import datetime


class ReactionType(IntEnum):
    All = 1
    Limited = 2


class ReactionTracker():
    def __init__(
            self,
            channelId: int,
            trackingChannelId: int,
            type: int,
            validReactions: str,
            created: int,
            id: int = -1,
            active: int = True) -> None:
        '''Raw values taken from db table types'''

        self.id = id
        self.channelId = channelId
        self.trackingChannelId = trackingChannelId
        self.type = ReactionType(type)
        self.validReactions = validReactions.split(',')
        self.created = datetime.fromtimestamp(created)
        self.active = active == 1


class ReactionMessage():
    def __init__(
            self,
            trackingChannelId: int,
            messageId: int,
            created: int,
            id: int = -1,
            active: int = True) -> None:
        '''Raw values taken from db table types'''

        self.id = id
        self.trackingChannelId = trackingChannelId
        self.messageId = messageId
        self.created = datetime.fromtimestamp(created)
        self.active = bool(active)


class Action(IntEnum):
    Add = 1
    Remove = 1


class Reaction():
    def __init__(
            self,
            messageId: int,
            reaction: str,
            action: int,
            userId: int,
            userName: str,
            created: int,
            id: int = -1) -> None:
        '''Raw values taken from db table types'''

        self.id = id
        self.messageId = messageId
        self.reaction = reaction
        self.action = Action(action)
        self.userId = userId
        self.userName = userName
        self.created = datetime.fromtimestamp(created)
