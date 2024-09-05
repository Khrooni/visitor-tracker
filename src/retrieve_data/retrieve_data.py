from dataclasses import dataclass
import json
import time
from typing import List

import requests

import utils

@dataclass
class Location:
    location_id: int
    location_name: str
    epoch_timestamp: int
    location_visitors: int


def _get_html() -> requests.models.Response:
    """
    Retrieves data from a specific URL and returns the response object.

    Returns:
        requests.models.Response: The response object containing the data retrieved from the URL.

    """
    url = "https://funouluritaharju.fi/?controller=ajax&getentriescount=1&locationId=1"

    response = requests.get(url, timeout=10)

    return response


def _parse_locations_data(response: requests.models.Response) -> List[Location]:
    """
    Parses location data from the response object and returns a list of Location objects.

    Parameters:
        response (requests.models.Response): The response object containing location data.

    Returns:
        List[Location]: A list of Location objects, each representing a location entry
            with parsed data.
    """
    locations = []

    date = response.headers.get("date")
    # print(date)

    epoch = utils.gmt_to_epoch(date)
    # print(epoch)
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


def get_data() -> List[Location]:
    location_data: List[Location] = []
    hmtl = _get_html()
    locations = _parse_locations_data(hmtl)
    for location in locations:
        location_data.append(location)
    return location_data
