from collections import OrderedDict
from typing import List
from discord import Message, PartialEmoji, Embed
from datetime import datetime, timedelta

from config.config import REACTION_TRACKING_EXPIRY_DAYS, MAX_EMBED_TITLE_LENGTH, \
    DOUBLE_CLICK_DETECTION_SECONDS, DOUBLE_CLICK_MIDNIGHT_BUFFER_SECONDS

from core import nomic_time, language
from core.utils import MemoizeCache
from core.db import reactions_db as db
from core.db.models import reaction_models as model

locale = language.Locale('core.reaction_tracking')

DOUBLE_CLICK_EXCEPTION_TD = timedelta(seconds=DOUBLE_CLICK_MIDNIGHT_BUFFER_SECONDS)


def create_channel_tracking_relationship(trackingChannelId: int, channelId: int,
                                         trackingChannelName: str, channelName: str) -> str:
    '''
    Create a new tracker for the provided channel, attached to the current trackingChannel.

    :param trackingChannelId: Id of the channel in which the command was run
    :param channelId: Id of the channel we are going to be tracking messages in
    :return: Response message to client
    '''
    trackers = db.get_trackers()

    # Check if there is already a tracker with this channel relationship
    exists = [t for t in trackers if t.channelId == channelId and t.trackingChannelId == trackingChannelId]

    if any(exists):
        return locale.get_string('trackerAlreadyExists',
                                 trackingChannelName=trackingChannelName, channelName=channelName)

    newTracker = model.ReactionTracker(
        channelId,
        trackingChannelId,
        model.ReactionType.All,
        None,
        nomic_time.utc_now()
    )

    db.save_tracker(newTracker)

    return locale.get_string('trackerCreated',
                             trackingChannelName=trackingChannelName, channelName=channelName)


def remove_channel_tracking_relationship(trackingChannelId: int, channelId: int,
                                         trackingChannelName: str, channelName: str) -> str:
    '''
    Deactivate a tracking channel relationship between the two given channels.

    :param trackingChannelId: Id of the channel in which the command was run
    :param channelId: Id of the channel we are tracking messages in
    :return: Response message to client
    '''
    trackingChannels = db.get_trackers_by_tracking_channel_id(trackingChannelId)

    trackedChannels = [tracker for tracker in trackingChannels if tracker.channelId == channelId]

    if len(trackedChannels) == 0:
        return locale.get_string('trackerNotExist',
                                 trackingChannelName=trackingChannelName, channelName=channelName)

    for tracker in trackedChannels:
        tracker.active = False
        db.save_tracker(tracker)

    return locale.get_string('trackerRemoved',
                             trackingChannelName=trackingChannelName, channelName=channelName)


def get_channel_trackers(channelId: int) -> List[model.ReactionTracker]:
    return db.get_trackers_by_channel_id(channelId)


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
    trackers = db.get_trackers_by_channel_id(channelId)

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


# Tracking Log #
async def update_tracking_channels(cache: MemoizeCache, message: Message):
    # Get the tracking channels linked to the updating messageId
    messageId = message.id
    reactionMessages = get_messages(messageId)
    trackingChannelIds = [m.trackingChannelId for m in reactionMessages]
    trackingMessages = get_tracking_messages(messageId)

    # for each tracking channel, ensure that a tracking message exists in it
    for channelId in trackingChannelIds:
        if not any([m for m in trackingMessages if m.trackingChannelId == channelId]):
            await send_new_tracking_message(cache, channelId, message)


    for trackingMessage in trackingMessages:
        await update_tracking_message(cache, trackingMessage, message)


async def send_new_tracking_message(cache: MemoizeCache, trackingChannelId: int, message: Message):
    # Get the message we are tracking
    trackingChannel = await cache.get_channel(trackingChannelId)

    # Generate a tracking message for each tracking channel that is tracking the target message
    embed = get_reaction_log(message)

    trackingMessage = await trackingChannel.send(embed=embed)

    create_tracking_message(message.id, trackingMessage.id, trackingChannel.id)


async def update_tracking_message(cache: MemoizeCache,
                                  trackingMessage: model.ReactionTrackingMessage,
                                  message: Message):
    # Get the message object we need to update
    trackingChannel = await cache.get_channel(trackingMessage.trackingChannelId)
    trackingMessage = await cache.get_message(trackingChannel, trackingMessage.trackingMessageId)

    embed = get_reaction_log(message)

    await trackingMessage.edit(embed=embed)


def get_tracking_messages(messageId: int) -> List[model.ReactionTrackingMessage]:
    return db.get_tracking_messages(messageId)


def get_messages(messageId: int) -> List[model.ReactionMessage]:
    return db.get_messages(messageId)


def create_tracking_message(messageId, trackingMessageId, trackingChannelId) -> None:
    trackingMessage = model.ReactionTrackingMessage(messageId, trackingMessageId, trackingChannelId)
    db.save_tracking_message(trackingMessage)


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
