import sqlite3
import contextlib
from typing import List
import re
import math

from .helpers import (
    are_ints,
    get_unique_epochs,
    calculate_days,
    calculate_timestamps,
    calculate_averages,
)
from retrieve_data import Location

import time


DB_NAME = "visitorTrackingDB.db"
DB_DIRECTORY = "src/database/"
DB_FILE_PATH = DB_DIRECTORY + DB_NAME

MODES = {
    "avg": "AVG",
    "max": "MAX",
    "min": "MIN",
    "sum": "SUM",
    "count": "COUNT",
}


class SQLiteDBManager:
    def __init__(self, dbpath=DB_FILE_PATH):
        self.dbpath = dbpath
        self.conn = sqlite3.connect(dbpath)

        sql_create_visitor_activity_table = """CREATE TABLE IF NOT EXISTS visitor_activity(
            location_id INTEGER NOT NULL,
            epoch_timestamp INTEGER NOT NULL,
            location_visitors INTEGER NOT NULL,
            PRIMARY KEY (location_id, epoch_timestamp)
            )"""

        sql_create_locations_table = """CREATE TABLE IF NOT EXISTS locations(
            location_id INTEGER PRIMARY KEY NOT NULL,
            location_name TEXT NOT NULL)"""

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(sql_create_locations_table)
            cursor.execute(sql_create_visitor_activity_table)
            self.conn.commit()

    def _close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Closes db connection"""
        self._close()

    def add_data(
        self,
        location_id: int,
        location_name: str,
        epoch_timestamp: int,
        location_visitors: int,
    ) -> bool:
        try:
            self.add_location(location_id, location_name)
        except sqlite3.DatabaseError as e:
            print(e)
            return False

        success = self.add_visitor_activity(
            location_id, epoch_timestamp, location_visitors
        )

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

    def add_visitor_activity(
        self, location_id: int, epoch_timestamp: int, location_visitors: int
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

    def add_many_visitor(self, visitor_activity: List[tuple[int, int, int]]):

        pstmt_add_visitors = "INSERT INTO visitor_activity VALUES (?, ?, ?)"

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.executemany(pstmt_add_visitors, visitor_activity)
            self.conn.commit()

    def add_many_location(self, locations: List[tuple[int, str]]):

        pstmt_add_locations = "INSERT INTO locations VALUES (?, ?)"

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.executemany(pstmt_add_locations, locations)
            self.conn.commit()

    def get_activity_between(
        self, location_id: int, start: int, end: int
    ) -> List[tuple]:
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
            WHERE (location_id = ?) AND (? <= epoch_timestamp AND epoch_timestamp < ?)
            ORDER BY epoch_timestamp
            """

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt_get_between, (location_id, start, end))
            activity_list = cursor.fetchall()

        return activity_list

    def get_mode_activity_between(
        self, location_id: int, start: int, end: int, mode: str
    ) -> tuple | None:
        """
        Retrieve activity records from the 'visitor_activity' table within a specified time range for a given location.

        Parameters:
            location_id (int): The ID of the location..
            start (int): The start time (inclusive) of the time range in epoch format.
            end (int): The end time (exclusive) of the time range in epoch format.
            mode (str): avg, max, min or sum.

        Returns:
            List[Tuple]: A list of tuples representing the retrieved activity records.
                        Each tuple contains two elements: epoch timestamp and number of location visitors.

        If either the 'start' or 'end' parameters are negative or if any of the int parameters are not of type 'int',
        None is returned.
        """

        if not are_ints(location_id, start, end) or (start < 0 or end < 0):
            return None

        pstmt: str = f"""SELECT {MODES.get(mode.lower())}(location_visitors) 
            FROM visitor_activity
            WHERE (location_id = ?) AND (? <= epoch_timestamp AND epoch_timestamp < ?)
            """

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt, (location_id, start, end))
            result = cursor.fetchone()

        return (start, result[0])

    def get_mode_activity_between_peridiocally(
        self, location_id: int, start: int, end: int, mode: str, interval: int
    ) -> List[tuple]:
        """
        Retrieve activity records from the 'visitor_activity' table within a specified time range for a given location.

        Parameters:
            location_id (int): The ID of the location..
            start (int): The start time (inclusive) of the time range in epoch format.
            end (int): The end time (exclusive) of the time range in epoch format.
            interval (int): The duration of each interval in seconds. Average visitors will be calculated
                                within each interval.

        Returns:
            List[Tuple]: A list of tuples representing the retrieved activity records.
                        Each tuple contains two elements: epoch timestamp (interval start time) and average visitors during inteval.

        If either the 'start' or 'end' parameters are negative or if any of the parameters are not of type 'int',
        an empty list is returned.
        """
        activity_list: List[tuple] = []

        if not are_ints(location_id, start, end, interval) or (
            start < 0 or end < 0 or interval < 0
        ):
            return activity_list

        duration = end - start
        loops = math.floor(duration / interval)

        for i in range(loops):
            activity = self.get_mode_activity_between(
                location_id,
                (start + i * interval),
                (start + (i + 1) * interval),
                MODES.get(mode.lower()),
            )
            activity_list.append(activity)

        return activity_list

    def get_average_visitors(
        self, location_id: int, weekday: str
    ) -> tuple[list[int], list[int]]:
        epochs = []

        total_sums = []
        total_counts = []

        interval = 60 * 60

        all_days = self._get_days(location_id, weekday)

        for day in all_days:
            start = day[0]
            end = day[1]

            if not self._has_data(location_id, start, end):
                continue

            new_sums = self.get_data_by_mode(location_id, start, end, "sum", interval)
            new_counts = self.get_data_by_mode(
                location_id,
                start,
                end,
                "count",
                interval,
            )

            if not total_sums or not epochs:
                epochs = calculate_timestamps(start, end, interval)

                total_counts.extend(new_counts)
                total_sums = [
                    0 if not are_ints(visitor_sum) else visitor_sum
                    for visitor_sum in new_sums
                ]
            else:
                # total counts += new counts
                total_counts = [
                    total_count + new_count
                    for total_count, new_count in zip(total_counts, new_counts)
                ]

                # total sums += visitor sum (if visitor sum is a integer)
                total_sums = [
                    current_sum + visitor_sum if are_ints(visitor_sum) else current_sum
                    for current_sum, visitor_sum in zip(total_sums, new_sums)
                ]

        averages = calculate_averages(total_sums, total_counts)

        return averages, epochs

    def get_single_by_mode(
        self, location_id: int, start: int, end: int, mode: str
    ) -> int | None:

        if not are_ints(location_id, start, end):
            raise TypeError(
                "Arguments 'location_id', 'start', and 'end' must be integers."
            )
        if start < 0 or end < 0:
            raise ValueError("Start and end values must be non-negative.")

        pstmt: str = f"""SELECT {MODES.get(mode.lower())}(location_visitors) 
            FROM visitor_activity
            WHERE (location_id = ?) AND (? <= epoch_timestamp AND epoch_timestamp < ?)
            """

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt, (location_id, start, end))
            result = cursor.fetchone()

        return result[0]

    def get_data_by_mode(
        self, location_id: int, start: int, end: int, mode: str, interval: int
    ) -> List[int]:

        activity_list: List[int] = []

        if not are_ints(location_id, start, end):
            raise TypeError(
                "Arguments 'location_id', 'start', and 'end' must be integers."
            )
        if start < 0 or end < 0 or interval < 0:
            raise ValueError("Start and end values must be non-negative.")

        duration = end - start
        loops = math.floor(duration / interval)

        for i in range(loops):
            start_time = start + i * interval
            activity = self.get_single_by_mode(
                location_id,
                start_time,
                (start + (i + 1) * interval),
                MODES.get(mode.lower()),
            )
            activity_list.append(activity)

        return activity_list

    def _get_days(self, location_id: int, weekday: str) -> List[tuple[int, int]]:
        """
        Calculates upper (start of first target weekday) and lower limit (end of last tar)

        """
        pstmt_first: str = (
            "SELECT epoch_timestamp FROM visitor_activity WHERE (location_id = ?)"
        )
        pstmt_last: str = (
            "SELECT epoch_timestamp FROM visitor_activity WHERE (location_id = ?) ORDER BY epoch_timestamp DESC"
        )

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt_first, (location_id,))
            first_timestamp = cursor.fetchone()
            cursor.execute(pstmt_last, (location_id,))
            last_timestamp = cursor.fetchone()

        if first_timestamp and last_timestamp:
            first_timestamp = first_timestamp[0]
            last_timestamp = last_timestamp[0]
        else:
            return []

        return calculate_days(first_timestamp, last_timestamp, weekday)

    def _has_data(self, location_id: int, start_epoch: int, end_epoch: int) -> bool:
        """
        Checks if visitor_activity table has data, with given location id, between
        given start (inclusive) and end (exclusive) epochs.

        Returns: True if there is any data, False otherwise.
        """

        pstmt = """SELECT rowid
            FROM visitor_activity
            WHERE (location_id = ?) AND (? <= epoch_timestamp AND epoch_timestamp < ?)
            """

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt, (location_id, start_epoch, end_epoch))
            result = cursor.fetchone()

        if result is not None:
            return True
        else:
            return False

    def get_locations(self) -> List[tuple[int, str]]:
        return self.get_all("locations")

    def get_unique_dates(self, location_id: int) -> List[int]:
        unique_epochs = []

        if not are_ints(location_id):
            return unique_epochs

        all_epochs = []

        pstmt_get_between: str = """SELECT epoch_timestamp
            FROM visitor_activity
            WHERE (location_id = ?)
            ORDER BY epoch_timestamp
            """

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt_get_between, (location_id,))
            all_epochs_tuple = cursor.fetchall()
            for row in all_epochs_tuple:
                if len(row) > 0:
                    all_epochs.append(row[0])

        unique_epochs = get_unique_epochs(all_epochs)

        return unique_epochs

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

        stmt_get_all = f"SELECT * FROM {table_name} ORDER BY rowid"

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(stmt_get_all)
            all_list = cursor.fetchall()

        return all_list

    def _table_has(self, location_id: int) -> bool:
        """
        Checks if a location with the given location_id exists in the 'locations' table.
        """
        pstmt_check_table: str = "SELECT * FROM locations WHERE location_id = ?"

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt_check_table, (location_id,))
            result = cursor.fetchone()
            return result is not None

    def _table_exists(self, table_name: str) -> bool:
        """
        True if table exists. False if table doesn't exist or given table name didn't pass SQL Injection check.
        (Doesn't follow regex '^[A-Za-z0-9_äÄöÖåÅ]+$')
        """

        if not self._valid_table_name(table_name):
            return False

        stmt = (
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(stmt)
            result = cursor.fetchone()

        if result is not None:
            return True
        else:
            return False

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
