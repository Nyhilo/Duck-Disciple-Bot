from typing import List, Union
from core.db.db_base import Database
from config.config import SQLITE3_DB_NAME
from config.config import DB_TABLE_REACTION_TRACKING_NAME, DB_TABLE_REACTION_MESSAGES_NAME, DB_TABLE_REACTIONS_NAME

from core.db.models.reaction_models import ReactionTracker, ReactionMessage, Reaction
from core.nomic_time import get_timestamp

db = Database(SQLITE3_DB_NAME)


# Initialization Methods #
def _create_table_reaction_tracking():
    '''
    Notes on database architecture:

    ChannelID           - Id of the channel we'll be looking at to find
                           messages to track
    TrackingChannelId   - Id of the channel that contains the tracking log
    ReactionType        - Enum 1 or 2. Maps to "All" for all reactions or
                           "Limited" for only the reactions in ValidReactions
    ValidReactions      - Comma-separated list of pre-formatted reactions
                            i.e.: '<:thumb:customId>,<:thumb2:customId2>'
    '''

    db.idempotent_add_table(
        '''
        Id                  INTEGER PRIMARY KEY     AUTOINCREMENT,
        ChannelId           INT     NOT NULL,
        TrackingChannelId   INT     NOT NULL,
        ReactionType        INT     NOT NULL,
        ValidReactions      TEXT,
        Created             INT     NOT NULL,
        Active              INT     NOT NULL    DEFAULT 1
        ''', DB_TABLE_REACTION_TRACKING_NAME
    )


def _create_table_reaction_messages():
    '''
    Notes on database architecture:

    TrackingChannelId   - Foreign key for the channel that this message will
                           be tracked in
    MessageId           - Id of the message being tracked
    '''

    db.idempotent_add_table(
        '''
        Id                  INTEGER PRIMARY KEY     AUTOINCREMENT,
        TrackingChannelId   INT     NOT NULL,
        MessageId           INT     NOT NULL,
        Created             INT     NOT NULL,
        Active              INT     NOT NULL    DEFAULT 1
        ''', DB_TABLE_REACTION_MESSAGES_NAME
    )


def _create_table_reactions():
    '''
    Notes on database architecture:

    MessageId   - Foreign key for the message this reaction belongs to
    Reaction    - Formatted reaction. i.e.: '<:thumbup:customId>'
    Action      - Enum 1 or 2. Maps to "Add" and "Remove"
    UserId      - User Id who added or removed the reaction
    UserName    - Human-readable name for public logging (i.e. 'Joe')
    '''

    db.idempotent_add_table(
        '''
        Id          INTEGER PRIMARY KEY     AUTOINCREMENT,
        MessageId   INT     NOT NULL,
        Reaction    TEXT    NOT NULL,
        Action      INT     NOT NULL,
        UserId      INT     NOT NULL,
        UserName    TEXT    NOT NULL,
        Created     INT     NOT NULL
        ''', DB_TABLE_REACTIONS_NAME
    )


def set_tables():
    _create_table_reaction_tracking()
    _create_table_reaction_messages()
    _create_table_reactions()


# Reaction Tracking #
def get_trackers(channelId: int = None) -> List[ReactionTracker]:
    '''
    Get a list of existing active trackers.

    :param channelId: Optional channelId to limit how many trackers are returned, defaults to None
    :return: A list of the relevant ReactionTrackers
    '''
    results = None
    if channelId is None:
        results = db.get(
            f'''
            SELECT Id, ChannelId, TrackingChannelId, ReactionType, ValidReactions, Created, Active
            FROM {DB_TABLE_REACTION_TRACKING_NAME}
            WHERE Active = 1
            '''
        )
    else:
        results = db.get(
            f'''
            SELECT Id, ChannelId, TrackingChannelId, ReactionType, ValidReactions, Created, Active
            FROM {DB_TABLE_REACTION_TRACKING_NAME}
            WHERE Active = 1 AND ChannelId = :channelId
            ''', [channelId]
        )

    trackers = [
        ReactionTracker(r['ChannelId'],
                        r['TrackingChannelId'],
                        r['ReactionType'],
                        r['ValidReactions'],
                        r['Created'],
                        r['Id'],
                        r['Active'])
        for r in results
    ]

    return trackers


def save_tracker(tracker: ReactionTracker) -> bool:
    '''Inserts or updates the provided tracker'''

    # Check if a tracker with the given id already exists
    results = db.get(
        f'''
        SELECT Id
        FROM {DB_TABLE_REACTION_TRACKING_NAME}
        WHERE Id = :id
        ''', [tracker.id]
    )

    if len(results) > 0:
        return _update_tracker(tracker)

    return _add_tracker(tracker)


def _add_tracker(tracker: ReactionTracker) -> bool:
    return db.modify(
        f'''
        INSERT INTO {DB_TABLE_REACTION_TRACKING_NAME}
        (ChannelId, TrackingChannelId, ReactionType, ValidReactions, Created, Active)
        VALUES (:channelId, :trackingChannelId, :reactionType, :validReactions, :created, :active)
        ''', [
            tracker.channelId,
            tracker.trackingChannelId,
            tracker.reactionType.value,
            None if tracker.validReactions is None else ','.join(tracker.validReactions),
            get_timestamp(tracker.created),
            1 if tracker.active else 0
        ]
    )


def _update_tracker(tracker: ReactionTracker) -> bool:
    return db.modify(
        f'''
        UPDATE {DB_TABLE_REACTION_TRACKING_NAME}
        SET ChannelId = :channelId,
            TrackingChannelId = :trackingChannelId,
            ReactionType = :reactionType,
            ValidReactions = :validReactions,
            Created = :created,
            Active = :active
        WHERE Id = :id
        ''', [
            tracker.channelId,
            tracker.trackingChannelId,
            tracker.reactionType.value,
            ','.join(tracker.validReactions),
            get_timestamp(tracker.created),
            1 if tracker.active else 0,
            tracker.id
        ]
    )


# Reaction Messages #
def get_messages(messageId: int) -> List[ReactionMessage]:
    '''Get a current active trackers'''

    results = db.get(
        f'''
        SELECT Id, TrackingChannelId, MessageId, Created, Active
        FROM {DB_TABLE_REACTION_MESSAGES_NAME}
        WHERE Active = 1 AND MessageId = :messageId
        ''', [messageId]
    )

    messages = [
        ReactionMessage(r['TrackingChannelId'],
                        r['MessageId'],
                        r['Created'],
                        r['Id'],
                        r['Active'])
        for r in results
    ]

    return messages


def save_message(tracker: ReactionMessage) -> bool:
    '''Inserts or updates the provided tracker'''

    # Check if a tracker with the given id already exists
    results = db.get(
        f'''
        SELECT Id
        FROM {DB_TABLE_REACTION_MESSAGES_NAME}
        WHERE Id = :id
        ''', [tracker.id]
    )

    if len(results) > 0:
        return _update_message(tracker)

    return _add_message(tracker)


def _add_message(tracker: ReactionMessage) -> bool:
    return db.modify(
        f'''
        INSERT INTO {DB_TABLE_REACTION_MESSAGES_NAME}
        (TrackingChannelId, MessageId, Created, Active)
        VALUES (:trackingChannelId, :messageId, :created, :active)
        ''', [
            tracker.trackingChannelId,
            tracker.messageId,
            get_timestamp(tracker.created),
            1 if tracker.active else 0
        ]
    )


def _update_message(tracker: ReactionMessage) -> bool:
    return db.modify(
        f'''
        UPDATE {DB_TABLE_REACTION_MESSAGES_NAME}
        SET TrackingChannelId = :trackingChannelId,
            MessageId = :messageId,
            Created = :created,
            Active = :active
        WHERE Id = :id
        ''', [
            tracker.trackingChannelId,
            tracker.messageId,
            get_timestamp(tracker.created),
            1 if tracker.active else 0,
            tracker.id
        ]
    )


# Reactions #
def get_reactions(messageId: int, timestampSince: int) -> List[Reaction]:
    '''Get a current active trackers'''

    results = db.get(
        f'''
        SELECT Id, MessageId, Reaction, Action, UserId, UserName, Created
        FROM {DB_TABLE_REACTIONS_NAME}
        WHERE MessageId = :messageId AND created > :timestampSince
        ''', [messageId, timestampSince]
    )

    trackers = [
        Reaction(r['MessageId'],
                 r['Reaction'],
                 r['Action'],
                 r['UserId'],
                 r['UserName'],
                 r['Created'],
                 r['Id'])
        for r in results
    ]

    return trackers


def save_reaction(tracker: Reaction) -> bool:
    '''Inserts or updates the provided tracker'''

    # Check if a tracker with the given id already exists
    results = db.get(
        f'''
        SELECT Id
        FROM {DB_TABLE_REACTIONS_NAME}
        WHERE Id = :id
        ''', [tracker.id]
    )

    if len(results) > 0:
        return _update_reaction(tracker)

    return _add_reaction(tracker)


def _add_reaction(tracker: Reaction) -> bool:
    return db.modify(
        f'''
        INSERT INTO {DB_TABLE_REACTIONS_NAME}
        (MessageId, Reaction, Action, UserId, UserName, Created)
        VALUES (:messageId, :reaction, :action, :userId, :userName, :created)
        ''', [
            tracker.messageId,
            tracker.reaction,
            tracker.action.value,
            tracker.userId,
            tracker.userName,
            get_timestamp(tracker.created)
        ]
    )


def _update_reaction(tracker: Reaction) -> bool:
    return db.modify(
        f'''
        UPDATE {DB_TABLE_REACTIONS_NAME}
        SET MessageId = :messageId,
            Reaction = :reaction,
            Action = :action,
            UserId = :userId,
            UserName = :userName,
            Created = :created
        WHERE Id = :id
        ''', [
            tracker.messageId,
            tracker.reaction,
            tracker.action.value,
            tracker.userId,
            tracker.userName,
            get_timestamp(tracker.created),
            tracker.id
        ]
    )
