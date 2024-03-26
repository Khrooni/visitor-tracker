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

    tuple_test = 1

    print(retrive_data.epoch_to_finnish_time(1711467662))

    day = "No day"
    epoch = 0
    location_id = 0
    location_name = "No name"
    location_visitors = 0

    locationTest = retrive_data.Location(1, "nimi", 1000, 22)

    juup = 2


if __name__ == "__main__":
    main()
