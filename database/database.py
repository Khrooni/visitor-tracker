import sqlite3

database_name: str = "myLocationDB.db"



# connection = sqlite3.connect(":memory:")
connection = sqlite3.connect(database_name)

cursor = connection.cursor()

# Create a Table
cursor.execute(
    """CREATE TABLE fun_oulu_ritaharju (
                epoch_timestamp INTEGER PRIMARY KEY NOT NULL,
                location_name TEXT,
                person_entries INTEGER,
                day_of_the_week TEXT
    )"""
)

connection.commit()

connection.close()
