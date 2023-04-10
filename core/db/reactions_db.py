from typing import List
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
    Type                - Enum 1 or 2. Maps to "All" for all reactions or
                           "Limited" for only the reactions in ValidReactions
    ValidReactions      - Comma-separated list of pre-formatted reactions
                            i.e.: '<:thumb:customId>,<:thumb2:customId2>'
    '''

    db.idempotent_add_table(
        '''
        Id                  INT     PRIMARY KEY     AUTOINCREMENT,
        ChannelId           INT     NOT NULL,
        TrackingChannelId   INT     NOT NULL,
        Type                INT     NOT NULL,
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
        Id                  INT     PRIMARY KEY     AUTOINCREMENT,
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
        Id          INT     PRIMARY KEY     AUTOINCREMENT,
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
def get_trackers() -> List[ReactionTracker]:
    results = db.get(
        f'''
        SELECT Id, ChannelId, TrackingChannelId, Type, ValidReactions, Created, Active
        FROM {DB_TABLE_REACTION_TRACKING_NAME}
        WHERE Active = 1
        '''
    )

    trackers = [
        ReactionTracker(r['ChannelId'],
                        r['TrackingChannelId'],
                        r['Type'],
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
        (ChannelId, TrackingChannelId, Type, ValidReactions, Created, Active)
        VALUES (:channelId, :trackingChannelId, :type, :validReactions, :created, :active)
        ''', [
            tracker.channelId,
            tracker.trackingChannelId,
            tracker.type.value,
            ','.join(tracker.validReactions),
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
            Type = :type,
            ValidReactions = :validReactions,
            Created = :created,
            Active = :active
        WHERE Id = :id
        ''', [
            tracker.channelId,
            tracker.trackingChannelId,
            tracker.type.value,
            ','.join(tracker.validReactions),
            get_timestamp(tracker.created),
            1 if tracker.active else 0,
            tracker.id
        ]
    )


# Reaction Messages #


# Reactions #
