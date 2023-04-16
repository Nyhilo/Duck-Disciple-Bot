from discord import TextChannel, Message, User, PartialEmoji
from datetime import datetime

from config.config import REACTION_TRACKING_EXPIRY_DAYS, MAX_CACHE_LENGTH

from core import nomic_time
from core.db import reactions_db as db
from core.db.models import reaction_models as model


def create_channel_tracking_relationship(trackingChannelId: int, channelId: int) -> None:
    '''
    Create a new tracker for the provided channel, attached to the current trackingChannel.

    :param trackingChannelId: Id of the channel in which the command was run
    :param channelId: Id of the channel we are going to be tracking messages in
    :return: _description_
    '''
    trackers = db.get_trackers()

    # Check if there is already a tracker with this channel relationship
    exists = [t for t in trackers if t.channelId == channelId and t.trackingChannelId == trackingChannelId]

    newTracker = model.ReactionTracker(
        channelId,
        trackingChannelId,
        model.ReactionType.All,
        None,
        nomic_time.utc_now()
    )

    if any(exists):
        newTracker.id = exists[0].id

    db.save_tracker(newTracker)

    return 'Tracker created between the two channels.'


def add_reaction(channelId: int,
                 messageId: int,
                 messageCreated: datetime,
                 userId: int,
                 userName: str,
                 reaction: str) -> None:
    '''Save an "add reaction" event to the database'''
    return _add_reaction_event(channelId, messageId, messageCreated, userId, userName, reaction, False)


def remove_reaction(channelId: int,
                    messageId: int,
                    messageCreated: datetime,
                    userId: int,
                    userName: str,
                    reaction: str) -> None:
    '''Save a "remove reaction" event to the database'''
    return _add_reaction_event(channelId, messageId, messageCreated, userId, userName, reaction, True)


def _add_reaction_event(channelId: int,
                        messageId: int,
                        messageCreated: datetime,
                        userId: int,
                        userName: str,
                        reaction: str,
                        remove: bool) -> None:
    trackers = db.get_trackers(channelId)

    # If there are no trackers for that channel, then we're done here
    if not any(trackers):
        return

    # How far back we should look for new reactions
    createdBy = nomic_time.get_full_days_ago(REACTION_TRACKING_EXPIRY_DAYS)

    # Target message is older than the configured check time
    if messageCreated < createdBy:
        return

    # Ensure the message is logged the relevant amount of times for future parsing in the tracking channels
    # One message object for each tracking channel
    messages = db.get_messages(messageId)
    if len(messages) < len(trackers):
        # Create a new message for each tracker
        for tracker in trackers:
            newMessage = model.ReactionMessage(
                tracker.trackingChannelId,
                messageId,
                messageCreated
            )

            db.save_message(newMessage)

    reaction = model.Reaction(
        messageId,
        reaction,
        model.Action.Add if not remove else model.Action.Remove,
        userId,
        userName,
        nomic_time.utc_now()
    )

    db.save_reaction(reaction)



def get_message(channelId: int):
    db.get_messages(channelId)


# Utils #

def format_emoji(emoji: PartialEmoji) -> str:
    if emoji.id is None:
        return emoji.name

    a = 'a' if emoji.animated else ''
    return f'<{a}:{emoji.name}:{emoji.id}>'


class MemoizeCache():
    def __init__(self, bot) -> None:
        self.bot = bot
        self.cachedChannels = {}
        self.cachedMessages = {}
        self.cachedUsers = {}

    async def get_channel(self, id: int) -> TextChannel:
        if id not in self.cachedChannels:

            # "Clear the cache" if it gets too big
            if len(self.cachedChannels) >= MAX_CACHE_LENGTH:
                self.cachedChannels = {}

            self.cachedChannels[id] = await self.bot.fetch_channel(id)

        return self.cachedChannels[id]

    async def get_message(self, channel: TextChannel, id: int) -> Message:
        if id not in self.cachedMessages:

            # "Clear the cache" if it gets too big
            if len(self.cachedMessages) >= MAX_CACHE_LENGTH:
                self.cachedMessages = {}

            self.cachedMessages[id] = await channel.fetch_message(id)

        return self.cachedMessages[id]

    async def get_user(self, id: int) -> User:
        if id not in self.cachedUsers:

            # "Clear the cache" if it gets too big
            if len(self.cachedUsers) >= MAX_CACHE_LENGTH:
                self.cachedUsers = {}

            self.cachedUsers[id] = await self.bot.fetch_user(id)

        return self.cachedUsers[id]
