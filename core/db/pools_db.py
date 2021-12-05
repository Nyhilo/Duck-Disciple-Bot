import sqlite3
from core.log import log
from config.config import SQLITE3_DB_NAME, DB_TABLE_POOLS_NAME, DB_TABLE_POOL_ENTRIES_NAME
from core.db.models.pool_models import Pool, Entry


# Database definitions
def _table_exists(conn, table):
    cursor = conn.execute(f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table}' ''')

    return cursor.fetchone()[0] == 1


def _create_table_pools(db):
    '''
    Notes on database architecture:

    ServerId - The ID of the guild in which the table was instantiated.
               An ID of 0 indicates that the table is globally available.
               An ID of -1 indicates that the table is hidden
    CreatorId - The ID of the user that created the table
    Name - The user readable name of the table
    '''

    table = DB_TABLE_POOLS_NAME
    conn = sqlite3.connect(db)

    if _table_exists(conn, table):
        conn.close()
        return

    conn.execute(
        f'''
        CREATE TABLE {table}
        (
            Id          INTEGER PRIMARY KEY     AUTOINCREMENT,
            ServerId    INT     NOT NULL,
            CreatorId   INT     NOT NULL,
            Name        TEXT    NOT NULL,
            Active      INT     NOT NULL    DEFAULT 1
        )
        '''
    )

    conn.commit()
    conn.close()

    log.info(f'Created sqlite3 table {table} in {db}')

    return


def _create_table_pool_entries(db):
    '''
    This has a many-to-one relationship with the 'Pools' table.
    '''

    table = DB_TABLE_POOL_ENTRIES_NAME
    conn = sqlite3.connect(db)

    if _table_exists(conn, table):
        conn.close()
        return

    conn.execute(
        f'''
        CREATE TABLE {table}
        (
            Id              INTEGER PRIMARY KEY     AUTOINCREMENT,
            ParentPoolId    INT     NOT NULL,
            Description     TEXT    NOT NULL,
            Amount          INT     NOT NULL    DEFAULT 1,
            Active          INT     NOT NULL    DEFAULT 1
        )
        '''
    )

    conn.commit()
    conn.close()

    log.info(f'Created sqlite3 table {table} in {db}')

    return


# Repository Methods
def get_all_pools(serverId):
    results = db_get(
        f'''
        SELECT Id, ServerId, CreatorId, Name, Active
        FROM {DB_TABLE_POOLS_NAME}
        WHERE Active = 1 AND ServerId = :serverId OR ServerId = 0
        ''', [serverId]
    )

    pools = []
    for r in results:
        pool = Pool(r['Id'], r['Name'], r['ServerId'], r['CreatorId'], None)
        pool.entries = get_entries(r['Id'], pool)
        pools.append(pool)

    return pools


def get_pool(poolName):
    results = db_get(
        f'''
        SELECT Id, ServerId, CreatorId, Name, Active
        FROM {DB_TABLE_POOLS_NAME}
        WHERE Active = 1 AND Name = :poolName
        ''', [poolName]
    )

    r = results[0] if len(results) > 0 else None
    pool = Pool(r['Id'], r['Name'], r['ServerId'], r['CreatorId'], None) if r else None

    if pool:
        pool.entries = get_entries(r['Id'], pool)

    return pool


def get_entries(poolId, parentPool=None):
    results = db_get(
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


def add_pool(serverId, creatorId, poolName):
    return db_modify(
        f'''
        INSERT INTO {DB_TABLE_POOLS_NAME}
        (ServerId, CreatorId, Name)
        Values (:serverId, :creatorId, :poolName)
        ''', [serverId, creatorId, poolName]
    )


def add_entry(poolId, description, amount):
    return db_modify(
        f'''
        INSERT INTO {DB_TABLE_POOL_ENTRIES_NAME}
        (ParentPoolId, Description, Amount)
        Values (:poolId, :description, :amount)
        ''', [poolId, description, amount]
    )


def update_entry(entryId, amount):
    return db_modify(
        f'''
        UPDATE {DB_TABLE_POOL_ENTRIES_NAME}
        SET Amount = :amount
        WHERE Id = :entryId
        ''', [amount, entryId]
    )


def unset_pool(poolId):
    return db_modify(
        f'''
        UPDATE {DB_TABLE_POOLS_NAME}
        SET Active = 0
        WHERE Id = :poolId
        ''', [poolId]
    )


def unset_entry(entryId):
    return db_modify(
        f'''
        UPDATE {DB_TABLE_POOL_ENTRIES_NAME}
        SET Active = 0
        WHERE Id = :entryId
        ''', [entryId]
    )


# Database Access
def db_get(query, params, db=SQLITE3_DB_NAME):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    cursor = conn.execute(query, params)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def db_modify(query, params, db=SQLITE3_DB_NAME):
    conn = sqlite3.connect(db)
    cursor = conn.execute(query, params)

    conn.commit()
    conn.close()

    return cursor.lastrowid


# Maintenance Methods
def set_table():
    _create_table_pools(SQLITE3_DB_NAME)
    _create_table_pool_entries(SQLITE3_DB_NAME)
