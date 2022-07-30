import sqlite3
from typing import List, Dict
from core.log import log


class Database():
    def __init__(self, database_name: str) -> None:
        self.database_name = database_name

    def _table_exists(self, table: str) -> None:
        """
        Checks if a given table exists in the object database.

        :param table: The name of the table.
        """
        conn = sqlite3.connect(self.database_name)
        cursor = conn.execute(
            f'''
            SELECT count(name)
            FROM sqlite_master
            WHERE type='table' AND name='{table}'
            ''')

        exists = cursor.fetchone()[0] == 1

        conn.close()

        return exists

    def idempotent_add_table(self, column_defs: str, table: str) -> None:
        """Checks if the provided table exists, and adds it to the database with
        the given table definition if it doesn't. Column definitions should be in
        the following format:
            '''
            <property 1>    <type>  <other keywords...>,
            <property 2>    <type>  <other keywords...>,
            etc.
            '''

        :param column_defs: A formatted string of column definitions
        :param table:       Name of the table to be created (case-sensitive)
        """
        if self._table_exists(table):
            return

        conn = sqlite3.connect(self.database_name)

        conn.execute(f'CREATE TABLE {table} ({column_defs})')

        conn.commit()
        conn.close()

        log.info(f'Created sqlite3 table {table} in {self.database_name}')

    def get(self, query: str, params: List[str]) -> List[Dict[str, object]]:
        """
        Opens a connection to the object database and gets some rows from it
        for the given query. Takes parameters for sql-injection safety.

        :param query:  The full string query to execute. Parameters in the query
                        should look like ':this'.
        :param params: A list of parameters to substitute into the query.
        :return:       Returns a list of dictionaries representing the values
                        returned by the query. Dictionary keys map to column
                        names.
        """
        conn = sqlite3.connect(self.database_name)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(query, params)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def modify(self, query: str, params: List[str]) -> int:
        """
        Takes an INSERT or UPDATE type query, and confirms the operation by
        returning the last row id modified. Takes parameters for sql-injection
        safety.

        :param query:  The full string query to execute. Parameters in the query
                        should look like ':this'. Should be an INSERT or UPDATE
                        command.
        :param params: A list of parameters to substitute into the query.
        :return:       The row number of the last row modified.
        """
        conn = sqlite3.connect(self.database_name)
        cursor = conn.execute(query, params)

        conn.commit()
        conn.close()

        return cursor.lastrowid
