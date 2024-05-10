import sqlite3
import contextlib
from typing import List
import re
import math

from . import helpers


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

        if not helpers.are_ints(location_id, start, end) or (start < 0 or end < 0):
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

    def get_average_visitors(self, location_id: int, weekday: str) -> list[int]:
        """
        Calculates the average number of visitors and corresponding timestamps for a given location and weekday.
        Averages are calculated for every hour of the day (00, 01, ..., 23)

        Parameters:
        - location_id (int)
        - weekday (str): The weekday for which to calculate average visitors
            - e.g., ("mon", "tue", "wed", "thu", "fri", "sat", "sun").

        Returns:
        - list[int]: A list of average visitor counts for every hour.
        """

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

            missing_hour = None

            if new_sums.__len__() != 24:
                missing_hour = helpers.calculate_missing_or_extra_hour(
                    start, end, interval
                )
                new_sums = helpers.add_or_remove_extra_values(
                    new_sums, missing_hour, 0, 24
                )

            if new_counts.__len__() != 24:
                if not missing_hour:
                    missing_hour = helpers.calculate_missing_or_extra_hour(
                        start, end, interval
                    )
                new_counts = helpers.add_or_remove_extra_values(
                    new_counts, missing_hour, 0, 24
                )

            if not total_sums or not total_counts:
                total_counts.extend(new_counts)
                total_sums = [
                    0 if not helpers.are_ints(visitor_sum) else visitor_sum
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
                    (
                        current_sum + visitor_sum
                        if helpers.are_ints(visitor_sum)
                        else current_sum
                    )
                    for current_sum, visitor_sum in zip(total_sums, new_sums)
                ]

        averages = helpers.calculate_averages(total_sums, total_counts)

        return averages

    def get_data_by_mode(
        self, location_id: int, start: int, end: int, mode: str, interval: int
    ) -> list[int]:
        """
        Retrieve data at specified intervals between given start and end times,
        following the given mode.

        Parameters:
        - location_id (int): Identifier for the location to retrieve data from.
        - start (int): Start time in epoch format.
        - end (int): End time in epoch format.
        - mode (str): Data mode to follow for each interval
            - e.g., ("avg", "max", "min", "sum" or "count").
        - interval (int): Time interval in seconds for data retrieval.

        Returns:
        - list[int]: A list of data points corresponding to the given mode for each interval.

        Raises:
        - TypeError: If 'location_id', 'start', 'end' or 'interval' are not integers.
        - ValueError: If 'start', 'end', or 'interval' are negative.
        """
        activity_list: List[int] = []

        if not helpers.are_ints(location_id, start, end, interval):
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

    def get_single_by_mode(
        self, location_id: int, start: int, end: int, mode: str
    ) -> int | None:

        if not helpers.are_ints(location_id, start, end):
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

    def _get_days(self, location_id: int, weekday: str) -> List[tuple[int, int]]:
        """
        Calculates upper (start of first target weekday) and lower limit (end of last target)

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

        return helpers.calculate_days(first_timestamp, last_timestamp, weekday)

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
        
    def get_first_time(self, location_id: int) -> int | None:
        """
        Returns the first epoch timestamp in visitors table.
        """

        if not helpers.are_ints(location_id):
            raise TypeError(
                "Argument 'location_id' must be an integer."
            )
        
        pstmt = """SELECT epoch_timestamp 
        FROM visitor_activity 
        WHERE location_id = ? 
        ORDER BY ROWID ASC LIMIT 1"""

        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(pstmt, (location_id,))
            result = cursor.fetchone()
        
        if result:
            result = result[0]

        return result

    def get_locations_dict(self) -> dict[str:int]:
        locations = {}

        locations_data = self.get_all("locations")

        for location_id, location_name in locations_data:
            locations.update({location_name: location_id})

        return locations

    def get_locations(self) -> List[tuple[int, str]]:
        return self.get_all("locations")

    def get_unique_dates(self, location_id: int) -> List[int]:
        unique_epochs = []

        if not helpers.are_ints(location_id):
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

        unique_epochs = helpers.get_unique_epochs(all_epochs)

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
