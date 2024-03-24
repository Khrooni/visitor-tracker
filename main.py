import time
import re


import retrive_data
import database





def main():
    # print()
    # print("Start")
    # initialize_database()
    # print("Database intialized...")
    # print()

    tuple_test = (1)

    print(retrive_data.epoch_to_finnish_time(1711128747))
    print(retrive_data.epoch_to_finnish_time(1711212166))

    # tuple_test.


    day = "No day"
    epoch = 0
    location_id = 0
    location_name = "No name"
    location_visitors = 0

    locationTest = retrive_data.Location(1, "nimi", 1000, 22)


    time.sleep(0)

    loca = "321321"
    start = 131
    end = -1

    
    if start < 0 or end < 0:
        print("liian pieni")

    if not isinstance(loca, int) or not isinstance(start, int) or not isinstance(end, int):
        print("ei int")
    else:
        print("int")

    # print(isinstance(12314, int))

    # print(retrive_data.epoch_to_finnish_time(1711200876))

    juup = 2
    # for i in range(1, 1441):
    #     print("iteration: " + str(i))

    #     html = retrive_data.get_data()
    #     locations = retrive_data.parse_locations_data(html)

    #     for location in locations:
    #         day = location.day_of_the_week
    #         epoch = location.epoch_timestamp
    #         location_id = location.location_id
    #         location_name = location.location_name
    #         location_visitors = location.location_visitors

    #     database.initialize_database()

    #     database.add_to_table(epoch, location_name, person_entries, day)
    #     print("added to table")
    #     time.sleep(60)



    # cursor.execute("SELECT * FROM fun_oulu_ritaharju")

    # items = cursor.fetchall()
    # print(items)

    # for item in items:
    #     print(item)


if __name__ == "__main__":
    main()
