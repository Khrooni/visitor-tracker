import sqlite3


database_name = "myLocationDB.db"


def initialize_database():
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS fun_oulu_ritaharju (
                    epoch_timestamp INTEGER PRIMARY KEY NOT NULL,
                    location_name TEXT,
                    person_entries INTEGER,
                    day_of_the_week TEXT
        )"""
    )
    connection.commit()
    connection.close()


def add_to_table(
    epoch: int, location_name: str, person_entries: int, day_of_the_week: str
):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

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
    connection.commit()
    connection.close()


# connection = sqlite3.connect(":memory:")

if __name__ == "__main__":
    print()
    print("Start")
    initialize_database()
    print("Database intialized...")
    print()

    joo = retrive_data.get_data()

    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM fun_oulu_ritaharju")

    items = cursor.fetchall()
    print(items)

    for item in items:
        print(item)
