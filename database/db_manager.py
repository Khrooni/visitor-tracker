import sqlite3
import contextlib
from typing import List
import re

from .helpers import are_ints


DB_NAME = "visitorTrackingDB.db"
DB_DIRECTORY = "database/"
DB_FILE_PATH = DB_DIRECTORY + DB_NAME


class SQLiteDBManager:
    def __init__(self, dbname=DB_FILE_PATH):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        # self.cur = self.conn.cursor()

        sql_create_locations_table: str = """CREATE TABLE IF NOT EXISTS locations(
                        location_id INTEGER PRIMARY KEY NOT NULL,
                        location_name TEXT NOT NULL)"""

        sql_create_visitor_activity_table: str = """CREATE TABLE IF NOT EXISTS visitor_activity(
                        location_id INTEGER NOT NULL,
                        epoch_timestamp INTEGER NOT NULL UNIQUE,
                        location_visitors INTEGER)"""

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(sql_create_locations_table)
            cursor.execute(sql_create_visitor_activity_table)
            self.conn.commit()

    def _close(self):
        if self.conn:  # but check to make sure it has not been called by client!
            self.conn.close()
            self.conn = None

    def __del__(self):
        self._close()

    def add_data(self, 
        location_id: int, location_name: str, epoch_timestamp: int, location_visitors: int
    ) -> bool:
        try:
            self.add_location(location_id, location_name)
        except sqlite3.DatabaseError:
            return False

        success = self.add_visitor_activity(location_id, epoch_timestamp, location_visitors)

        return success


    def add_location(self, location_id: int, location_name: str) -> bool:
        if self._table_has(location_id):
            return False

        pstmt_add_visitor_data: str = (
            "INSERT INTO locations(location_id, location_name) VALUES(?,?)"
        )
        
    
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt_add_visitor_data, (location_id, location_name))
            self.conn.commit()

        return True


    def add_visitor_activity(self,
        location_id: int, epoch_timestamp: int, location_visitors: int
    ) -> bool:
        pstmt_add_visitor_data: str = (
            "INSERT INTO visitor_activity(location_id, epoch_timestamp, location_visitors) VALUES(?,?,?)"
        )

        try:
            with contextlib.closing(self.conn.cursor()) as cursor:
                cursor.execute(
                    pstmt_add_visitor_data,
                    (location_id, epoch_timestamp, location_visitors),
                )
                self.conn.commit()
        except sqlite3.IntegrityError:
            return False

        return True


    def _table_has(self, location_id: int) -> bool:
        """
        Checks if a location with the given location_id exists in the 'locations' table.
        """
        pstmt_check_table: str = "SELECT * FROM locations WHERE location_id = ?"


        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt_check_table, (location_id,))
            result = cursor.fetchone()
            return result is not None


    def get_activity_between(self, location_id: int, start: int, end: int) -> List[tuple]:
        """
        Retrieve activity records from the 'visitor_activity' table within a specified time range for a given location.

        Parameters:
            location_id (int): The ID of the location..
            start (int): The start time (inclusive) of the time range in epoch format.
            end (int): The end time (exclusive) of the time range in epoch format.

        Returns:
            List[Tuple]: A list of tuples representing the retrieved activity records.
                        Each tuple contains two elements: epoch timestamp and number of location visitors.

        If either the 'start' or 'end' parameters are negative or if any of the parameters are not of type 'int',
        an empty list is returned.
        """
        activity_list: List[tuple] = []

        if not are_ints(location_id, start, end) or (start < 0 or end < 0):
            return activity_list

        pstmt_get_between: str = """SELECT epoch_timestamp, location_visitors 
            FROM visitor_activity
            WHERE (location_id = ?) AND (epoch_timestamp >= ? AND epoch_timestamp < ?)
            ORDER BY epoch_timestamp
            """

    
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt_get_between, (location_id, start, end))
            activity_list = cursor.fetchall()

        return activity_list


    def get_all(self, table_name: str) -> List[tuple]:
        """
        Retrieve all records from the specified table in the database.

        Returns:
            List[Tuple]: A list of tuples representing the retrieved records.
                        Each tuple corresponds to a single row in the table.

        If the provided table name is not valid according to typical database naming conventions
        or if the table does not exist in the database, an empty list is returned.

        """
        all_list: List[tuple] = []

        if not self._table_exists(table_name):
            return all_list

        stmt_get_all = f"SELECT * FROM {table_name}"


        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(stmt_get_all)
            all_list = cursor.fetchall()

        return all_list


    def _table_exists(self, table_name: str) -> bool:
        """
        True if table exists. False if table doesn't exist or given table name didn't pass SQL Injection check.
        (Doesn't follow regex '^[A-Za-z0-9_äÄöÖåÅ]+$')
        """

        if not self._valid_table_name(table_name):
            return False

        stmt = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"

    
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(stmt)
            result = cursor.fetchone()

            return result


    def _valid_table_name(self, table_name: str) -> bool:
        """
        Checks that table_name only uses ascii-letters, underscores,
        numbers or "äÄöÖåÅ"-letters.

        A-Za-z0-9_äÄöÖåÅ
        """
        if re.match("^[A-Za-z0-9_äÄöÖåÅ]+$", table_name):
            return True
        else:
            return False




def main():
    print()
    print("Start")
    # db_handle = SQLiteDBManager()
    # print("Database intialized...")
    # print()
    # db_handle.__del__()


    i = 2


if __name__ == "__main__":
    main()
