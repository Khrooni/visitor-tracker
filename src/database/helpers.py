import re
import string
from typing import List
from datetime import datetime, timedelta
import utils

import pytz
import math



def calculate_averages(sums: list[int], counts: list[int]) -> list[float]:
    if len(sums) != len(counts):
        raise ValueError("The lengths of 'sums' and 'counts' lists must be the same.")

    averages = [sum_val / count_val if count_val != 0 else 0.0 for sum_val, count_val in zip(sums, counts)]

    return averages


def get_timestamps(start: int, end: int, interval: int) -> List[int]:
    """Return all timestamps of intervals that fit into start and end"""

    timestamps = []

    duration = end - start
    loops = math.floor(duration / interval)

    for i in range(loops):
        timestamps.append(start + i * interval)

    return timestamps

def are_ints(*args):
    """True if all given arguments were of type int. False otherwise."""
    for arg in args:
        if not isinstance(arg, int):
            return False
    return True


def calculate_days(
    start: int, end: int, weekday: str, tzinfo=pytz.timezone("Europe/Helsinki")
) -> List[tuple[int, int]]:
    """Calculates the start day (inclusive) and end day (exclusive)"""
    weekdays: List[tuple[int, int]] = []

    lower_limit = utils.lower_limit(start, weekday)  # Beginning of first weekday
    upper_limit = utils.upper_limit(end, weekday)  # End of last weekday

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


def get_unique_epochs(all_epochs: List[int]) -> List[str]:
    """
    Returns a list
    """
    # dates = [datetime.fromtimestamp(epoch).strftime("%d-%m-%Y") for epoch in all_epochs]
    dates = [utils.get_finnish_date(epoch) for epoch in all_epochs]

    unique_dates = []
    seen_dates = set()
    for date in dates:
        if date not in seen_dates:
            unique_dates.append(date)
            seen_dates.add(date)

    return unique_dates


def valid_table_name(table_name: str) -> bool:
    """
    Checks that table_name only uses ascii-letters, underscores,
    numbers or "äÄöÖåÅ"-letters.

    A-Za-z0-9_äÄöÖåÅ
    """
    string.ascii_letters
    if re.match("^[A-Za-z0-9_äÄöÖåÅ]+$", table_name):
        return True
    else:
        return False


# def main():
#     test = "dsa231sadsad23321____31312321ädadäåqwertyuiopåäölkjhgfdsazxcvbnm"
#     test2 = "----;;;;2131321DELETE"
#     print(valid_table_name(test))
#     print(valid_table_name(test2))
#     print(valid_table_name(""))
#     print(valid_table_name("das-"))
#     print(valid_table_name("löä"))
#     print(valid_table_name(";"))
#     print(valid_table_name("+"))
#     print(valid_table_name("-"))


# if __name__ == "__main__":
#     main()
