import requests
import json

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List
import time


@dataclass
class Location:
    location_id: int
    location_name: str

    epoch_timestamp: int
    location_visitors: int

    def _get_finnish_datetime(self) -> datetime:
        utc_datetime = datetime.fromtimestamp(self.epoch_timestamp)

        finnish_time_offset = timedelta(hours=2)  # Finland (EET: UTC+2)

        finnish_datetime = utc_datetime + finnish_time_offset

        return finnish_datetime

    def get_formatted_finnish_time(self) -> str | None:
        """
        Converts the epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.
        Format: 'DD-MM-YYYY HH:MM:SS EET'

        Returns None if epoch timestamp was a value that couldn't be converted.
        """
        try:
            return self._get_finnish_datetime().strftime("%d-%m-%Y %H:%M:%S EET")
        except IOError:
            return None

    def get_finnish_date(self) -> str | None:
        """Returns None if epoch timestamp was a value that couldn't be converted."""
        try:
            return self._get_finnish_datetime().strftime("%d-%m-%Y")
        except IOError:
            return None

    def get_finnish_time(self) -> str | None:
        """Returns None if epoch timestamp was a value that couldn't be converted."""
        try:
            return self._get_finnish_datetime().strftime("%H:%M:%S")
        except IOError:
            return None

    def get_finnish_day(self) -> str | None:
        """Returns None if epoch timestamp was a value that couldn't be converted."""
        try:
            return self._get_finnish_datetime().strftime("%A")
        except IOError:
            return None


def _get_html() -> requests.models.Response:
    """
    Retrieves data from a specific URL and returns the response object.

    Returns:
        requests.models.Response: The response object containing the data retrieved from the URL.

    """
    url = "https://funouluritaharju.fi/?controller=ajax&getentriescount=1&locationId=1"

    response = requests.get(url)

    return response


def _parse_locations_data(response: requests.models.Response) -> List[Location]:
    """
    Parses location data from the response object and returns a list of Location objects.

    Parameters:
        response (requests.models.Response): The response object containing location data.

    Returns:
        List[Location]: A list of Location objects, each representing a location entry with parsed data.
    """
    locations = []

    date = response.headers.get("date")
    print(date)  # Korjaa
    time_object = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")

    epoch = int(time_object.timestamp())
    print(epoch)
    parsed_data = json.loads(response.text)
    entries_by_location = parsed_data["entriesByLocation"]

    for entry in entries_by_location:
        location = Location(
            location_id=entry["locationId"],
            location_name=entry["locationName"],
            location_visitors=entry["personEntries"],
            epoch_timestamp=epoch,
        )
        locations.append(location)

    return locations


def epoch_to_finnish_time(epoch):
    """
    Converts the given epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.
    Format: 'DD-MM-YYYY HH:MM:SS EET'

    Returns None if epoch was a value that couldn't be converted.
    """
    if epoch < 0:
        return None
    try:
        utc_datetime = datetime.fromtimestamp(epoch)

        finnish_time_offset = timedelta(hours=2)  # Finland (EET: UTC+2)

        finnish_datetime = utc_datetime + finnish_time_offset

        formatted_finnish_time = finnish_datetime.strftime("%d-%m-%Y %H:%M:%S EET")
    except IOError:
        return None

    return formatted_finnish_time


def get_data_periodically(duration: int, interval: int) -> List[Location]:
    """
    Retrives data from a specific URL for given 'duration' in given 'interval'.

    Parameters:
        duration (int): Duration of data retrival in seconds. (Must be greater than > 0)
        interval (int): Interval of data retrival in seconds. (Must be greater than > 0)

    Returns:
        List[Location]: A list of retrived Location objects
        or an empty list if duration or interval was < 1.
    """
    end_time = time.time() + duration
    location_data: List[Location] = []

    if duration < 1 or interval < 1:
        return location_data

    # Continue fetching data until the end time is reached
    while time.time() < end_time:
        function_start = time.perf_counter()
        hmtl = _get_html()
        locations = _parse_locations_data(hmtl)
        for location in locations:
            location_data.append(location)

        # Time it took took to execute data fetching
        function_time = time.perf_counter() - function_start

        # Wait for the specified interval before fetching data again
        time.sleep(float(interval) - function_time)

    return location_data


def main():
    # data = get_data_periodically(60, 10)
    print(epoch_to_finnish_time(100000))
    # for i, location in enumerate(data):
    #     print()
    #     print(f"Time (iteration {i+1}): {location.get_formatted_finnish_time()}")
    #     print(f"Visitors (iteration {i+1}): {location.location_visitors}")
    #     print()


if __name__ == "__main__":
    main()
