from collections import OrderedDict
from typing import List
from discord import TextChannel, Message, User, PartialEmoji, Embed
from datetime import datetime, timedelta

from config.config import REACTION_TRACKING_EXPIRY_DAYS, MAX_CACHE_LENGTH, MAX_EMBED_TITLE_LENGTH, \
    DOUBLE_CLICK_DETECTION_SECONDS, DOUBLE_CLICK_MIDNIGHT_BUFFER_SECONDS

from core import nomic_time
from core.db import reactions_db as db
from core.db.models import reaction_models as model

DOUBLE_CLICK_EXCEPTION_TD = timedelta(seconds=DOUBLE_CLICK_MIDNIGHT_BUFFER_SECONDS)


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


# Tracking Log #

def get_reaction_log(message: Message) -> Embed:
    # Build the title
    firstLine = message.content.split('\n')[0]
    msgTrimmedFirstLine = firstLine[:MAX_EMBED_TITLE_LENGTH]

    if len(msgTrimmedFirstLine) < len(firstLine):
        msgTrimmedFirstLine = msgTrimmedFirstLine + '...'

    title = f'Log for "{msgTrimmedFirstLine}"'

    # Fetch formatted url
    url = message.jump_url

    # Get all the reactions for a the given message
    _reactions = db.get_reactions(message.id, 0)
    reactions = filter_reactions_by_frequency(_reactions)

    # Group reactions by day created
    dateGroups = OrderedDict()
    for reaction in reactions:
        datestring = reaction.created.strftime('%m-%d-%Y')

        if datestring not in dateGroups:
            dateGroups[datestring] = []

        dateGroups[datestring].append(reaction)

    msg = [url]

    for date, group in dateGroups.items():
        msg.append(f'**{date}**')

        for reaction in group:
            reaction: model.Reaction = reaction
            time = reaction.created.strftime('%H:%M:%S')
            event = '+' if reaction.action is model.Action.Add else '\u2212'    # \u2212 is a slightly wider '-'
            emoji = reaction.reaction
            user = reaction.userName

            line = f'`{time}` | {event} | {emoji} | {user}'
            msg.append(line)

        msg.append('')

    # Generate a unique color from the message id
    uniqueColor = message.id % (0xffffff + 1)

    return Embed(title=title, description='\n'.join(msg), color=uniqueColor)


def filter_reactions_by_frequency(reactions: List[model.Reaction]) -> List[model.Reaction]:
    # Split the list up keyed on by user id
    reactionsByUser = {}
    for reaction in reactions:
        if reaction.userId not in reactionsByUser:
            reactionsByUser[reaction.userId] = []

        reactionsByUser[reaction.userId].append(reaction)

    filteredReactionList = []

    # Iterate through user ids. Detect and remove doubleclicks
    for id, reactions in reactionsByUser.items():
        doubleClickedIndicies = set()
        for i, current in enumerate(reactions):
            if i == 0:
                continue

            # If this reaction happened soon after 00:00 utc, we want to preserve it
            if (current.created - DOUBLE_CLICK_EXCEPTION_TD).day != current.created.day:
                continue

            prevIndex = i - 1
            previous = reactions[prevIndex]

            # Two different reactions interacting will never constitute a double click
            if previous.reaction != current.reaction:
                continue

            # Detect if this reaction and the previous reaction constitute a double click
            # If they do, then they are marked to be removed from the tracking list
            diffSeconds = (current.created - previous.created).total_seconds()
            closeTimestamps = diffSeconds < DOUBLE_CLICK_DETECTION_SECONDS
            if closeTimestamps and current.action != previous.action:
                doubleClickedIndicies.add(i)
                doubleClickedIndicies.add(prevIndex)

        # Add values to rebuild unsplit list
        for i, reaction in enumerate(reactions):
            if i not in doubleClickedIndicies:
                filteredReactionList.append(reaction)

    # Splitting by user will have messed up the order of things
    filteredReactionList.sort(key=lambda r: r.created)

    return filteredReactionList


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
