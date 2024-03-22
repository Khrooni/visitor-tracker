import requests
import json
from datetime import datetime, timedelta
from dataclasses import dataclass

from typing import List


@dataclass
class Location:
    location_id: int
    location_name: str
    person_entries: int
    epoch_timestamp: int
    day_of_the_week: str

    def get_finnish_time(self):
        """
        Converts the epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.

        Returns:
            str: A string representing the given epoch timestamp converted to Finnish time
                in the format 'DD-MM-YYYY HH:MM:SS EET'.
        """
        utc_datetime = datetime.fromtimestamp(self.epoch_timestamp)

        finnish_time_offset = timedelta(hours=2)  # Finland (EET: UTC+2)

        finnish_datetime = utc_datetime + finnish_time_offset

        formatted_finnish_time = finnish_datetime.strftime("%d-%m-%Y %H:%M:%S EET")

        return formatted_finnish_time


def get_data() -> requests.models.Response:
    """
    Retrieves data from a specific URL and returns the response object.

    Returns:
        requests.models.Response: The response object containing the data retrieved from the URL.

    """
    url = "https://funouluritaharju.fi/?controller=ajax&getentriescount=1&locationId=1"

    response = requests.get(url)

    return response


def parse_locations_data(response: requests.models.Response) -> List[Location]:
    """
    Parses location data from the response object and returns a list of Location objects.

    Parameters:
        response (requests.models.Response): The response object containing location data.

    Returns:
        list: A list of Location objects, each representing a location entry with parsed data.
    """
    locations = []

    date = response.headers.get("date")
    time_object = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")

    epoch = int(time_object.timestamp())
    day_of_the_week = time_object.strftime("%A")

    parsed_data = json.loads(response.text)
    entries_by_location = parsed_data["entriesByLocation"]

    for entry in entries_by_location:
        location = Location(
            location_id=entry["locationId"],
            location_name=entry["locationName"],
            person_entries=entry["personEntries"],
            epoch_timestamp=epoch,
            day_of_the_week=day_of_the_week,
        )
        locations.append(location)

    return locations


def epoch_to_finnish_time(epoch):
    """
    Converts the given epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.

    Parameters:
        epoch (int): The epoch timestamp to be converted to Finnish time.

    Returns:
        str: A string representing the given epoch timestamp converted to Finnish time
             in the format 'DD-MM-YYYY HH:MM:SS EET'.
    """

    utc_datetime = datetime.fromtimestamp(epoch)

    finnish_time_offset = timedelta(hours=2)  # Finland (EET: UTC+2)

    finnish_datetime = utc_datetime + finnish_time_offset

    formatted_finnish_time = finnish_datetime.strftime("%d-%m-%Y %H:%M:%S EET")

    return formatted_finnish_time


if __name__ == "__main__":


    html = get_data()

    # locations: List[Location] = parse_locations_data(html)
    locations = parse_locations_data(html)

    print()


    epoch = 0

    for location in locations:
        if location.location_id == 1:
            epoch = location.epoch_timestamp
            break
    print("epoch: " + str(epoch))

    time2 = location.get_finnish_time()
    print("Finnish time from epoch (using class function): ", time2)

    time = epoch_to_finnish_time(location.epoch_timestamp)
    print("Back to Finnish time from epoch(using function): " + time)

    print("All locations: ")
    print(locations)
