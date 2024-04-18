import re
import string
from typing import List
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
        start_day = utils.get_localized_datetime(lower_limit).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_day = (
            (start_day + timedelta(days=1))  # + 1 day
            .astimezone(tzinfo)  # + timedelta doesn't check if timezone changes
            .replace(hour=0, minute=0, second=0, microsecond=0)
        )
        weekdays.append(
            (utils.datetime_to_epoch(start_day), utils.datetime_to_epoch(end_day))
        )

        lower_limit = utils.datetime_to_epoch(
            (start_day + timedelta(weeks=1))  # + 1 week
            .astimezone(tzinfo)  # + timedelta doesn't check if timezone changes
            .replace(hour=0, minute=0, second=0, microsecond=0)
        )

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

    # Current weekday is the target weekday
    if days_to_add == 0:
        # Return current day but time set to 00:00:00.
        return fin_datetime.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).timestamp()

    # Calculate the weekday
    lower_limit = fin_datetime + timedelta(days=days_to_add)

    # Set time to 00:00:00
    lower_limit = lower_limit.replace(hour=0, minute=0, second=0, microsecond=0)

    return int(lower_limit.timestamp())


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

    return int(upper_limit_dt.timestamp())


def get_unique_epochs(all_epochs: List[int]) -> List[str]:
    """
    Returns a list
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
