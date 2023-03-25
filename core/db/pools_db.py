from typing import List
from core.db.db_base import Database
from core.db.models.pool_models import Pool, Entry
from config.config import SQLITE3_DB_NAME, DB_TABLE_POOLS_NAME, DB_TABLE_POOL_ENTRIES_NAME

db = Database(SQLITE3_DB_NAME)


def _create_table_pools():
    """
    Notes on database architecture:

    ServerId - The ID of the guild in which the table was instantiated.
               An ID of 0 indicates that the table is globally available.
               An ID of -1 indicates that the table is hidden
    CreatorId - The ID of the user that created the table
    Name - The user readable name of the table
    """

    db.idempotent_add_table(
        '''
        Id          INTEGER PRIMARY KEY     AUTOINCREMENT,
        ServerId    INT     NOT NULL,
        CreatorId   INT     NOT NULL,
        Name        TEXT    NOT NULL,
        Active      INT     NOT NULL    DEFAULT 1
        ''', DB_TABLE_POOLS_NAME
    )


def _create_table_pool_entries():
    """
    This has a many-to-one relationship with the 'Pools' table.
    """

    db.idempotent_add_table(
        '''
        Id              INTEGER PRIMARY KEY     AUTOINCREMENT,
        ParentPoolId    INT     NOT NULL,
        Description     TEXT    NOT NULL,
        Amount          INT     NOT NULL    DEFAULT 1,
        Active          INT     NOT NULL    DEFAULT 1
        ''', DB_TABLE_POOL_ENTRIES_NAME
    )

    return


# Repository Methods
def get_all_pools(serverId) -> List[Pool]:
    results = db.get(
        f'''
        SELECT Id, ServerId, CreatorId, Name, Active
        FROM {DB_TABLE_POOLS_NAME}
        WHERE Active = 1 AND (ServerId = :serverId OR ServerId = 0)
        ''', [serverId]
    )

    pools = []
    for r in results:
        pool = Pool(r['Id'], r['Name'], r['ServerId'], r['CreatorId'], None)
        pool.entries = get_entries(r['Id'], pool)
        pools.append(pool)

    return pools


def get_pool(serverId, poolName) -> List[Pool]:
    results = db.get(
        f'''
        SELECT Id, ServerId, CreatorId, Name, Active
        FROM {DB_TABLE_POOLS_NAME}
        WHERE Active = 1 AND (ServerId = :serverId OR ServerId = 0) AND Name = :poolName
        ''', [serverId, poolName]
    )

    r = results[0] if len(results) > 0 else None
    pool = Pool(r['Id'], r['Name'], r['ServerId'], r['CreatorId'], None) if r else None

    if pool:
        pool.entries = get_entries(r['Id'], pool)

    return pool


def get_entries(poolId, parentPool=None) -> List[Entry]:
    results = db.get(
        f'''
        SELECT Id, ParentPoolId, Description, Amount, Active
        FROM {DB_TABLE_POOL_ENTRIES_NAME}
        WHERE Active = 1 AND ParentPoolId = :poolId
        ''', [poolId]
    )

    entries = []
    for r in results:
        entries.append(Entry(r['Id'], parentPool, r['Amount'], r['Description']))

    return entries


def add_pool(serverId, creatorId, poolName) -> int:
    return db.modify(
        f'''
        INSERT INTO {DB_TABLE_POOLS_NAME}
        (ServerId, CreatorId, Name)
        Values (:serverId, :creatorId, :poolName)
        ''', [serverId, creatorId, poolName]
    )


def add_entry(poolId, description, amount) -> int:
    return db.modify(
        f'''
        INSERT INTO {DB_TABLE_POOL_ENTRIES_NAME}
        (ParentPoolId, Description, Amount)
        Values (:poolId, :description, :amount)
        ''', [poolId, description, amount]
    )


def update_entry(entryId, amount) -> int:
    return db.modify(
        f'''
        UPDATE {DB_TABLE_POOL_ENTRIES_NAME}
        SET Amount = :amount
        WHERE Id = :entryId
        ''', [amount, entryId]
    )


def unset_pool(poolId) -> int:
    return db.modify(
        f'''
        UPDATE {DB_TABLE_POOLS_NAME}
        SET Active = 0
        WHERE Id = :poolId
        ''', [poolId]
    )


def unset_entry(entryId) -> int:
    return db.modify(
        f'''
        UPDATE {DB_TABLE_POOL_ENTRIES_NAME}
        SET Active = 0
        WHERE Id = :entryId
        ''', [entryId]
    )


# Maintenance Methods
def set_tables():
    _create_table_pools()
    _create_table_pool_entries()
