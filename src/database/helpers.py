import re
import string
from typing import List, Any
from datetime import datetime, timedelta
import utils

import pytz
import math


def calculate_days(
    start: int, end: int, weekday: str, tzinfo=pytz.timezone("Europe/Helsinki")
) -> List[tuple[int, int]]:
    """Calculates the start day (inclusive) and end day (exclusive)"""
    weekdays: List[tuple[int, int]] = []

    lower_limit = _lower_limit(start, weekday)  # Beginning of first weekday
    upper_limit = _upper_limit(end, weekday)  # End of last weekday

    while True:
        start_day = utils.get_localized_datetime(lower_limit, tzinfo).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_day = utils.reset_dt_timezone(start_day, tzinfo)

        # +1 day and time to 00:00:00
        end_day = (start_day + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_day = utils.reset_dt_timezone(end_day, tzinfo)

        weekdays.append(
            (utils.datetime_to_epoch(start_day), utils.datetime_to_epoch(end_day))
        )

        lower_limit = utils.reset_dt_timezone(start_day + timedelta(weeks=1), tzinfo)
        lower_limit = utils.datetime_to_epoch(lower_limit)

        if lower_limit > upper_limit:
            break

    return weekdays


def calculate_averages(sums: list[int], counts: list[int]) -> list[float]:
    if len(sums) != len(counts):
        raise ValueError("The lengths of 'sums' and 'counts' lists must be the same.")

    averages = [
        sum_val / count_val if count_val != 0 else 0.0
        for sum_val, count_val in zip(sums, counts)
    ]

    return averages


def calculate_timestamps(start: int, end: int, interval: int) -> List[int]:
    """Returns a list with all timestamps of intervals that fit into start and end"""

    timestamps = []

    duration = end - start
    loops = math.floor(duration / interval)

    for i in range(loops):
        timestamps.append(start + i * interval)

    return timestamps


def _lower_limit(start: int, weekday: str) -> int:
    """
    Finds the next closest day (can be the given start day) to given start time
    that matches with the given target weekday.

    Parameters:
    - start (int): Starting time for search as epoch timestamp in seconds.
    - weekday (str): Target weekday abbreviation ("mon", "tue", "wed", "thu", "fri", "sat", "sun").

    Returns:
    - int: Closest target weekday as epoch timestamp in seconds. Time of the day will always be set to 00:00:00.

    """
    weekdays = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    fin_datetime = utils.get_localized_datetime(start)

    current_weekday = fin_datetime.weekday()
    target_weekday = weekdays[weekday.lower()]

    days_to_add = (target_weekday - current_weekday) % 7

    # Calculate the weekday
    lower_limit_dt = fin_datetime + timedelta(days=days_to_add)

    # Set time to 00:00:00
    lower_limit_dt = lower_limit_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    # Reset timezone in case of daylight saving time changes
    lower_limit_dt = utils.reset_dt_timezone(lower_limit_dt)

    return int(lower_limit_dt.timestamp())


def _upper_limit(end: int, weekday: str) -> int:
    """
    Finds the previous closest day (+1 day) to given end time
    that matches with the given target weekday.

    Parameters:
    - end (int): Ending time for search as epoch timestamp in seconds.
    - weekday (str): Target weekday abbreviation ("mon", "tue", "wed", "thu", "fri", "sat", "sun").

    Returns:
    - int: Closest target weekday(+1 day) as epoch timestamp in seconds. Time of the day will always be set to 00:00:00.
        Example: If target weekday is Tuesday returns previous Wednesday at 00:00:00. (mon -> tue, tue -> wed, ...)
    """

    weekdays = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

    fin_datetime = utils.get_localized_datetime(end)

    current_weekday = fin_datetime.weekday()
    target_weekday = weekdays[weekday.lower()]

    days_to_subtract = (current_weekday - target_weekday) % 7

    # Current weekday is the target weekday
    if days_to_subtract == 0:
        # +1 day
        fin_datetime = fin_datetime + timedelta(days=1)
        # Return the day, time set to 00:00:00.

        return int(
            fin_datetime.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        )

    # Calculate the datetime of the previous occurrence of the target weekday
    upper_limit_dt = fin_datetime - timedelta(days=days_to_subtract)

    # Set time to 00:00:00
    upper_limit_dt = upper_limit_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    # +1 day
    upper_limit_dt = upper_limit_dt + timedelta(days=1)

    # Reset timezone in case of daylight saving time changes
    upper_limit_dt = utils.reset_dt_timezone(upper_limit_dt)

    return int(upper_limit_dt.timestamp())


def add_or_remove_extra_values(
    value_list: list, value_index: int, added_value: Any | list = 0, expected_list_size = 24
) -> list:
    """
    Add/remove values to/from specific index(es) in a given list. Values are added/removed
    to/from the given index and indexes after it, for as many indexes as the difference
    between the size of the given list and expected_list_size.

    Parameters:
    - value_list (list): Given list.
    - value_index (int): The specific index where adding/removing the value(s) should start from.
    - expected_list_size (int): Expected size of the returned list.
    - added_value (Any | list):
        - If 'added_value' is not a list, the value will be added/removed to/from the chosen index(es).
        - If 'added_value' is a list, its element(s) will be added/removed sequentially to/from the chosen index(es),
            repeating as needed to fill/reduce the size gap.

    Raises:
    - IndexError: If added_value is a list that didn't have enough elements to add. (added_value list
        should have as many elements as there are values to be added to the new list)
    """
    new_list = value_list

    if value_list.__len__() < expected_list_size:
        new_list = _add_values(value_list, value_index, expected_list_size, added_value)
    elif value_list.__len__() > 24:
        new_list = _remove_values(value_list, value_index, expected_list_size)

    return new_list


def _add_values(
    value_list: list, value_index: int, expected_list_size: int, added_value: Any | list
) -> list:
    """
    Add values to specific index(es) in a given list. Values are added to the given index
    and indexes after it, for as many indexes as the difference between the size of the given
    list and expected_list_size.

    Parameters:
    - value_list (list): Given list.
    - value_index (int): The specific index where adding the value(s) should start from.
    - expected_list_size (int): Expected size of the returned list.
    - added_value (Any | list):
        - If 'added_value' is not a list, the value will be added to the chosen index(es).
        - If 'added_value' is a list, its element(s) will be added sequentially to the chosen index(es),
            repeating as needed to fill the size gap.

    Raises:
    - ValueError: If the size of 'value_list' is greater than 'expected_list_size'.
    - IndexError: If added_value is a list that didn't have enough elements to add. (added_value list
        should have as many elements as there are values to be added to the new list)
    """
    value_list_size = value_list.__len__()

    if value_list_size > expected_list_size:
        raise ValueError(
            "Expected_list_size should be greater than the size of value_list."
        )

    new_list = []

    for i in range(value_list_size):
        if i == value_index:

            for j in range(expected_list_size - value_list_size):
                if isinstance(added_value, list):
                    new_list.append(added_value[j])
                else:
                    new_list.append(added_value)

        new_list.append(value_list[i])

    return new_list


def _remove_values(value_list: list, value_index: int, expected_list_size: int) -> list:

    value_list_size = value_list.__len__()

    if value_list_size < expected_list_size:
        raise ValueError("Expected_list_size should be less than the size of value_list.")

    new_list = []

    i = 0
    while i < value_list_size:
        if i == value_index:
            # Don't add value(s) in given index
            i += value_list_size - expected_list_size
            continue

        new_list.append(value_list[i])
        i += 1

    return new_list


def calculate_missing_or_extra_hour(
    start: int, end: int, interval: int, tzinfo=pytz.timezone("Europe/Helsinki")
) -> int:
    hour_counter = 0

    duration = end - start
    loops = math.floor(duration / interval)

    for i in range(loops):
        start_time = start + i * interval
        end_time = start + (i + 1) * interval

        start_dt = utils.get_localized_datetime(start_time, tzinfo)
        end_dt = utils.get_localized_datetime(end_time, tzinfo)

        start_tzinfo = start_dt.dst()
        end_tzinfo = end_dt.dst()

        if start_tzinfo != end_tzinfo:
            break

        hour_counter += 1
        
    return hour_counter


def get_unique_epochs(all_epochs: List[int]) -> List[str]:
    """
    Returns a list of unique epochs as format "%d-%m-%Y".
    """
    dates = [utils.get_finnish_date(epoch) for epoch in all_epochs]

    unique_dates = []
    seen_dates = set()
    for date in dates:
        if date not in seen_dates:
            unique_dates.append(date)
            seen_dates.add(date)

    return unique_dates


def are_ints(*args):
    """True if all given arguments were of type int. False otherwise."""
    for arg in args:
        if not isinstance(arg, int):
            return False
    return True
