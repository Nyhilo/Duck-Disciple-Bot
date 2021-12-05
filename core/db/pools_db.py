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
            ServerId    TEXT    NOT NULL,
            CreatorId   TEXT    NOT NULL,
            Name        INT     NOT NULL,
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
            ParentPoolId    TEXT    NOT NULL,
            Description     INT     NOT NULL,
            Amount          INT     NOT NULL    DEFAULT 1
        )
        '''
    )

    conn.commit()
    conn.close()

    log.info(f'Created sqlite3 table {table} in {db}')

    return


# Repository Methods
def get_all_pools(serverId, db=SQLITE3_DB_NAME, table=DB_TABLE_POOLS_NAME):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    cursor = conn.execute(
        f'''
        SELECT Id, ServerId, CreatorId, Name
        FROM {table}
        WHERE ServerId = :serverId OR ServerId = 0
        ''', [serverId]
    )

    rows = cursor.fetchall()
    conn.close()

    pools = []
    for d in [dict(row) for row in rows]:
        pool = Pool(d['Id'], d['Name'], d['ServerId'], d['CreatorId'], None)
        pool.entries = get_entries(d['Id'], pool)
        pools.append(pool)

    return pools


def get_pool(poolName, db=SQLITE3_DB_NAME, table=DB_TABLE_POOLS_NAME):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute(
        f'''
        SELECT Id, ServerId, CreatorId, Name
        FROM {table}
        WHERE Name = :poolName
        ''', [poolName]
    )

    rows = cursor.fetchall()
    conn.close()

    d = [dict(row) for row in rows][0]
    pool = Pool(d['Id'], d['Name'], d['ServerId'], d['CreatorId'], None)
    pool.entries = get_entries(d['Id'], pool)

    return pool


def get_entries(poolId, parentPool=None, db=SQLITE3_DB_NAME, table=DB_TABLE_POOL_ENTRIES_NAME):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    cursor = conn.execute(
        f'''
        SELECT Id, ParentPoolId, Description, Amount
        FROM {table}
        WHERE ParentPoolId = :poolId
        ''', [poolId]
    )

    rows = cursor.fetchall()
    conn.close()

    entries = []
    for d in [dict(row) for row in rows]:
        entries.append(Entry(d['Id'], parentPool, d['Amount'], d['Description']))

    return entries


def add_pool(serverId, creatorId, poolName, db=SQLITE3_DB_NAME, table=DB_TABLE_POOLS_NAME):
    conn = sqlite3.connect(db)
    cursor = conn.execute(
        f'''
        INSERT INTO {table}
        (ServerId, CreatorId, Name)
        Values (:serverId, :creatorId, :poolName)
        ''', [serverId, creatorId, poolName]
    )

    conn.commit()
    conn.close()

    return cursor.lastrowid


def add_entry(poolId, description, amount, db=SQLITE3_DB_NAME, table=DB_TABLE_POOL_ENTRIES_NAME):
    conn = sqlite3.connect(db)
    cursor = conn.execute(
        f'''
        INSERT INTO {table}
        (ParentPoolId, Description, Amount)
        Values (:poolId, :description, :amount)
        ''', [poolId, description, amount]
    )

    conn.commit()
    conn.close()

    return cursor.lastrowid


# Maintenance Methods
def set_table():
    _create_table_pools(SQLITE3_DB_NAME)
    _create_table_pool_entries(SQLITE3_DB_NAME)
