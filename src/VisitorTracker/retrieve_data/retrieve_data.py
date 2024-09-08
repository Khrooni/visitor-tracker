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


def _get_html(url: str | None = None) -> requests.models.Response:
    """Fetches the response object from the given URL.

    :param url: The URL to request. Defaults to a preset URL if None. Preset URL:
        "https://funouluritaharju.fi/?controller=ajax&getentriescount=1&locationId=1"
    :type url: str | None, optional
    :return: The response object.
    :rtype: requests.models.Response
    """
    if not url:
        url = "https://funouluritaharju.fi/?controller=ajax&getentriescount=1&locationId=1"

    response = requests.get(url, timeout=10)

    return response


def _parse_locations_data(response: requests.models.Response) -> List[Location]:
    """Parses location data from the response object and returns a list
    of Location objects.

    :param response: The response object containing location data.
    :type response: requests.models.Response
    :return: A list of Location objects, each representing a location entry
        with parsed data.
    :rtype: List[Location]
    """
    locations = []

    date = response.headers.get("date")
    epoch = utils.gmt_to_epoch(date)

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
    """Retrieves data from a specific URL for given 'duration' in given 'interval'.

    :param duration: Duration of data retrieval in seconds. (Must be greater than > 0)
    :type duration: int
    :param interval: Interval of data retrieval in seconds. (Must be greater than > 0)
    :type interval: int
    :return: A list of retrieved Location objects or an empty list if
        duration or interval was < 1.
    :rtype: List[Location]
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
