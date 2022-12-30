from core.db.db_base import Database
from config.config import SQLITE3_DB_NAME, DB_TABLE_SETTINGS_NAME

db = Database(SQLITE3_DB_NAME)


def _create_table_settings():
    """
    Notes on database architecture:
    This whole table is a simple key-value dictionary with upsert capability.

    Name - The key of the dynamic setting stored
    Value - The value of the dynamic setting stored
    """

    db.idempotent_add_table(
        '''
        Name    TEXT    NOT NULL,
        Value   TEXT
        ''', DB_TABLE_SETTINGS_NAME
    )


def set_tables():
    _create_table_settings()


def get_setting(name:str) -> str:
    """Gets the value of a given setting key"""

    results = db.get(
        f'''
        SELECT Value
        FROM {DB_TABLE_SETTINGS_NAME}
        WHERE Name = :name
        ''', [name]
    )

    r = results[0] if len(results) > 0 else None

    return r['Value']


def save_setting(name:str, value:str) -> bool:
    """Inserts or updates the setting value"""

    # Check if a setting with the given name already exists
    results = db.get(
        f'''
        SELECT Value
        FROM {DB_TABLE_SETTINGS_NAME}
        WHERE Name = :name
        ''', [name]
    )

    if len(results) > 0:
        print('updating...')
        return _update_setting(name, value)

    return _insert_setting(name, value)


def _insert_setting(name:str, value:str) -> bool:
    return db.modify(
        f'''
        INSERT INTO {DB_TABLE_SETTINGS_NAME}
        (Name, Value)
        Values (:name, :value)
        ''', [name, value]
    )


def _update_setting(name:str, value:str) -> bool:
    return db.modify(
        f'''
        UPDATE {DB_TABLE_SETTINGS_NAME}
        SET Value = :value
        WHERE Name = :name
        ''', [name, value]
    )
