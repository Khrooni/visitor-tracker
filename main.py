import retrive_data
import database
import time

if __name__ == "__main__":
    # print()
    # print("Start")
    # initialize_database()
    # print("Database intialized...")
    # print()



    day = "No day"
    epoch = 0
    location_id = 0
    location_name = "No name"
    person_entries = 0


    for i in range(1,181):
        print("iteration: " +str(i))

        html = retrive_data.get_data()
        locations= retrive_data.parse_locations_data(html)

        for location in locations:
            day = location.day_of_the_week
            epoch = location.epoch_timestamp
            location_id = location.location_id
            location_name = location.location_name
            person_entries = location.person_entries
        

        database.initialize_database()

        database.add_to_table(epoch, location_name, person_entries, day)
        print("added to table")
        time.sleep(60)



    # connection = sqlite3.connect(database_name)
    # cursor = connection.cursor()

    # cursor.execute("SELECT * FROM fun_oulu_ritaharju")

    # items = cursor.fetchall()
    # print(items)

    # for item in items:
    #     print(item)
