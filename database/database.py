import sqlite3
import contextlib
from typing import List
from psycopg2 import sql

from os import path
import random


DB_NAME = "visitorTrackingDB.db"
DB_DIRECTORY = "database/"
DB_FILE_PATH = DB_DIRECTORY + DB_NAME


def initialize_database():
    sql_create_locations_table: str = """CREATE TABLE IF NOT EXISTS locations(
                    location_id INTEGER PRIMARY KEY NOT NULL,
                    location_name TEXT NOT NULL)"""

    sql_create_visitor_activity_table: str = """CREATE TABLE IF NOT EXISTS visitor_activity(
                    location_id INTEGER NOT NULL,
                    epoch_timestamp INTEGER NOT NULL UNIQUE,
                    location_visitors INTEGER)"""

    with sqlite3.connect(DB_FILE_PATH) as conn:
        with contextlib.closing(conn.cursor()) as cursor:
            cursor.execute(sql_create_locations_table)
            cursor.execute(sql_create_visitor_activity_table)
        conn.commit()


def add_data(
    location_id: int, location_name: str, epoch_timestamp: int, location_visitors: int
) -> bool:

    add_location(location_id, location_name)
    add_visitor_activity(location_id, epoch_timestamp, location_visitors)

    return True


def add_location(location_id: int, location_name: str) -> bool:
    if table_has(location_id):
        return False

    pstmt_add_visitor_data: str = (
        "INSERT INTO locations(location_id, location_name) VALUES(?,?)"
    )

    with sqlite3.connect(DB_FILE_PATH) as conn:
        with contextlib.closing(conn.cursor()) as cursor:
            cursor.execute(pstmt_add_visitor_data, (location_id, location_name))
        conn.commit()

    return True


def add_visitor_activity(
    location_id: int, epoch_timestamp: int, location_visitors: int
) -> bool:
    pstmt_add_visitor_data: str = (
        "INSERT INTO visitor_activity(location_id, epoch_timestamp, location_visitors) VALUES(?,?,?)"
    )

    try: 
        with sqlite3.connect(DB_FILE_PATH) as conn:
            with contextlib.closing(conn.cursor()) as cursor:
                cursor.execute(
                    pstmt_add_visitor_data,
                    (location_id, epoch_timestamp, location_visitors),
                )
            conn.commit()
    except sqlite3.IntegrityError:
        return False

    return True


def add_to_table(
    epoch: int, location_name: str, person_entries: int, day_of_the_week: str
):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    sql_insert_query = (
        "INSERT INTO fun_oulu_ritaharju VALUES ("
        + str(epoch)
        + ",'"
        + location_name
        + "',"
        + str(person_entries)
        + ",'"
        + day_of_the_week
        + "')"
    )

    cursor.execute(sql_insert_query)
    conn.commit()
    conn.close()


def table_has(location_id: int) -> bool:
    """
    Checks if a location with the given location_id exists in the 'locations' table.
    """
    pstmt_check_table: str = "SELECT * FROM locations WHERE location_id = ?"

    with sqlite3.connect(DB_FILE_PATH) as conn:
        with contextlib.closing(conn.cursor()) as cursor:
            cursor.execute(pstmt_check_table, (location_id,))
            result = cursor.fetchone()
            return result is not None


def copy_old_to_new_db(data: List[tuple]):
    for item in data:
        loc_id, epoch, lkm = item
        if add_data(loc_id, "FUN Oulu Ritaharju", epoch, lkm):
            print("Added successfully")
        else:
            print()
            print("Failed to add")
            print()



    # sql_query_insert: str = (
    #     "INSERT INTO visitor_activity(location_id, epoch_timestamp, location_visitors) VALUES (?,?,?)"
    # )

    # with sqlite3.connect(DB_FILE_PATH) as conn:
    #     with contextlib.closing(conn.cursor()) as cursor:
    #         for item in data:
    #             cursor.execute(sql_query_insert, item)
    #             conn.commit()
        


def get_data_from_old() -> List[tuple]:
    data: List[tuple] = []
    all_fe = []
    sql_query_get_data: str = (
        "SELECT epoch_timestamp, person_entries FROM fun_oulu_ritaharju"
    )

    with sqlite3.connect(
        "C:/Users/kaspe/git-repo-clone/omat-projektit/headcount-graph-project/myLocationDB.db"
    ) as conn:
        with contextlib.closing(conn.cursor()) as cursor:
            cursor.execute(sql_query_get_data)
            all_fe = cursor.fetchall()

    for tuple_all in all_fe:
        smaller_tuple = tuple_all
        epoch_timestamp, person_entries = smaller_tuple
        tuple_with_loc_id = (1, epoch_timestamp, person_entries)
        data.append(tuple_with_loc_id)

    return data


def main():
    print()
    print("Start")
    initialize_database()
    print("Database intialized...")
    print()
    # add_data(1, "Koulu", random.randint(1, 10000000), 33)
    # add_data(2, "blah'); drop table locations; --", random.randint(1, 10000000), 22)
    # print(table_has(1))
    # print(table_has(2))
    old_data = get_data_from_old()
    print("Got data from old DB")
    copy_old_to_new_db(old_data)
    print("Copied data")

    # print(count_rows("fun_oulu_ritaharju"))

    # data = get_data_from_old()
    # copy_old_to_new_db(data)

    i = 2


if __name__ == "__main__":
    main()
