import requests
import json

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List


@dataclass
class Location:
    location_id: int
    location_name: str

    epoch_timestamp: int
    location_visitors: int


    def get_finnish_datetime(self) -> datetime:
        utc_datetime = datetime.fromtimestamp(self.epoch_timestamp)

        finnish_time_offset = timedelta(hours=2)  # Finland (EET: UTC+2)

        finnish_datetime = utc_datetime + finnish_time_offset

        return finnish_datetime

    def get_formatted_finnish_time(self) -> str:
        """
        Converts the epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.
        Format: 'DD-MM-YYYY HH:MM:SS EET'
        """
        return self.get_finnish_datetime().strftime("%d-%m-%Y %H:%M:%S EET")

    def get_finnish_date(self) -> str:
        return self.get_finnish_datetime().strftime("%d-%m-%Y")
    
    def get_finnish_time(self) -> str:
        return self.get_finnish_datetime().strftime("%H:%M:%S")
    
    def get_finnish_day(self) -> str:
        return self.get_finnish_datetime().strftime("%A")


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

    parsed_data = json.loads(response.text)
    entries_by_location = parsed_data["entriesByLocation"]

    for entry in entries_by_location:
        location = Location(
            location_id=entry["locationId"],
            location_name=entry["locationName"],
            location_visitors=entry["personEntries"],
            epoch_timestamp=epoch
        )
        locations.append(location)

    return locations


def epoch_to_finnish_time(epoch):
    """
    Converts the given epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.
    Format: 'DD-MM-YYYY HH:MM:SS EET'
    """

    utc_datetime = datetime.fromtimestamp(epoch)

    finnish_time_offset = timedelta(hours=2)  # Finland (EET: UTC+2)

    finnish_datetime = utc_datetime + finnish_time_offset

    formatted_finnish_time = finnish_datetime.strftime("%d-%m-%Y %H:%M:%S EET")

    return formatted_finnish_time


def main():
    hmtl = get_data()
    locations = parse_locations_data(hmtl)

    print()
    print(locations)
    print("Locaatiot:  ")
    for location in locations:
        print(location)
        print(location.get_finnish_datetime())
        print(location.get_finnish_date())
        print(location.get_finnish_time())
        print(location.get_finnish_day())
    
    print()

    tuple1 = (1, "Toripoliisi", 1711190925, 55)
    location1 = Location(*tuple1)

    print(location1.get_formatted_finnish_time())
    print(location1.get_finnish_day())
    breakpoint1 = 2
    print(epoch_to_finnish_time(1711160020))



if __name__ == "__main__":
    main()
