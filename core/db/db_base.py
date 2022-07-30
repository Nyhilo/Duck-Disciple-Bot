import sqlite3
from typing import List, Dict
from core.log import log


class Database():
    def __init__(self, database_name: str) -> None:
        self.database_name = database_name

    def _table_exists(self, table: str) -> None:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.execute(
            f'''
            SELECT count(name)
            FROM sqlite_master
            WHERE type='table' AND name='{table}'
            ''')

        conn.close()

        return cursor.fetchone()[0] == 1

    def idempotent_add_table(self, column_definitions: str, table: str) -> None:
        conn = sqlite3.connect(self.database_name)

        if self._table_exists(conn, table):
            return

        conn.execute(f'CREATE TABLE {table} ({column_definitions})')

        conn.commit()
        conn.close()

        log.info(f'Created sqlite3 table {table} in {self.database_name}')

    def get(self, query: str, params: List[str]) -> List[Dict[str, object]]:
        conn = sqlite3.connect(self.database_name)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(query, params)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def modify(self, query: str, params: List[str]) -> int:
        conn = sqlite3.connect(self.database_name)
        cursor = conn.execute(query, params)

        conn.commit()
        conn.close()

        return cursor.lastrowid
