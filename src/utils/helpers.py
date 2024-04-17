from datetime import datetime, timedelta
import pytz
import time
import calendar
from typing import List
import database


def copy_db(old_db_path: str, new_db_path: str) -> bool:
    """
    Meant for 1 time use. Timezone errors in epochs. (epochs are -2h or -3h behind -> +2h/+3h)

    Raises: sqlite3.IntegrityError if adding a value to locations/visitor_activity
        failed due to locations/visitor_activity already having the primary key value
        that was attempted to add.
    """
    db_handle = None

    try:
        db_handle = database.SQLiteDBManager(dbpath=old_db_path)
        all_locations = db_handle.get_all("locations")
        all_activity = db_handle.get_all("visitor_activity")
    finally:
        if db_handle:
            db_handle.__del__()

    all_activity = edit_epochs_bad(all_activity)

    db_handle = None

    try:
        db_handle = database.SQLiteDBManager(dbpath=new_db_path)
        db_handle.add_many_location(all_locations)
        db_handle.add_many_visitor(all_activity)
    except Exception as e:
        print(e)
    finally:
        if db_handle:
            db_handle.__del__()

    return True


def edit_epochs_bad(activity: List[tuple[int, int, int]]) -> List[tuple[int, int, int]]:
    epoch_2 = 2 * 60 * 60
    epoch_3 = 3 * 60 * 60

    edited_activity = []

    for tuple_ in activity:
        if tuple_[1] <= 1711839599:  # a second before timezone changes from +2h to +3h.
            edited_tuple = (tuple_[0], tuple_[1] + epoch_2, tuple_[2])
        else:
            edited_tuple = (tuple_[0], tuple_[1] + epoch_3, tuple_[2])
        edited_activity.append(edited_tuple)
    return edited_activity


def lower_limit(start: int, weekday: str) -> int:
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
    fin_datetime = get_localized_datetime(start)

    current_weekday = fin_datetime.weekday()
    target_weekday = weekdays[weekday.lower()]

    days_to_add = (target_weekday - current_weekday) % 7

    # Current weekday is the target weekday
    if days_to_add == 0:
        # Return current day but time set to 00:00:00.
        return fin_datetime.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    # Calculate the weekday
    lower_limit = fin_datetime + timedelta(days=days_to_add)

    # Set time to 00:00:00
    lower_limit = lower_limit.replace(hour=0, minute=0, second=0, microsecond=0)

    return int(lower_limit.timestamp())


def upper_limit(end: int, weekday: str) -> int:
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


    fin_datetime = get_localized_datetime(end)

    current_weekday = fin_datetime.weekday()
    target_weekday = weekdays[weekday.lower()]

    days_to_subtract = (current_weekday - target_weekday) % 7

    # Current weekday is the target weekday
    if days_to_subtract == 0:
        # +1 day
        fin_datetime = fin_datetime  + timedelta(days=1)
        # Return the day, time set to 00:00:00.
        return int(fin_datetime.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

    # Calculate the datetime of the previous occurrence of the target weekday
    upper_limit_dt = fin_datetime - timedelta(days=days_to_subtract)

    # Set time to 00:00:00
    upper_limit_dt = upper_limit_dt.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # +1 day
    upper_limit_dt = upper_limit_dt + timedelta(days=1)

    return int(upper_limit_dt.timestamp())


def datetime_to_utc(datetime_to: datetime) -> datetime:
    return datetime_to.astimezone(pytz.utc)


def convert_for_day_graph(data: List[tuple[int, int]]) -> tuple[List[int], List[int]]:
    """
    Convert a list of tuples representing data points for a day graph. If

    Parameters:
        data (List[Tuple[int, int]]): A list of tuples where each tuple contains two integers representing
                                       x (epoch_timestamp) and y (visitor activity) values.

    Returns:
        Tuple[List[int], List[int]]: A tuple containing two lists:
                                      - The first list contains converted x values (hour).
                                      - The second list contains y values (visitor activity).
    """
    x_values, y_values = zip(*data)

    # Extract x values and convert them to dates
    x_values = [get_finnish_hour(x) for x in x_values]

    # Extract y values and round them if they are not None.
    # If a value is None, set the value to 0.
    # y_values =  [int(round(y)) if y is not None else 0 for y in y_values]
    y_values = [y if y is not None else 0 for y in y_values]

    return x_values, y_values


def get_formatted_finnish_time(epoch_timestamp) -> str | None:
    """
    Converts the epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.
    Format: 'DD-MM-YYYY HH:MM:SS EET'

    Returns None if epoch timestamp was a value that couldn't be converted.
    """
    try:
        return get_localized_datetime(epoch_timestamp).strftime("%d-%m-%Y %H:%M:%S %Z")
    except IOError:
        return None


def get_finnish_date(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return get_localized_datetime(epoch_timestamp).strftime("%d-%m-%Y")
    except IOError:
        return None


def get_finnish_time(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return get_localized_datetime(epoch_timestamp).strftime("%H:%M:%S")
    except IOError:
        return None


def get_finnish_hour(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return get_localized_datetime(epoch_timestamp).strftime("%H")
    except IOError:
        return None


def get_finnish_day(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return get_localized_datetime(epoch_timestamp).strftime("%A")
    except IOError:
        return None


def time_to_epoch(date: str, tzinfo=pytz.timezone("Europe/Helsinki")) -> int:
    """
    Convert the given date string in 'DD-MM-YYYY HH:MM:SS' format to epoch timestamp.

    Parameters:
        date (str): date string in 'DD-MM-YYYY HH:MM:SS' format to convert.
        tzinfo (pytz.timezone, optional): Time zone to localize the time string.
            If not provided, defaults to 'Europe/Helsinki' time zone (UTC+2/UTC+3).

    Returns:
        int: Epoch timestamp corresponding to the input date.

    Raises:
        ValueError: If the date string does not match the expected format.
    """

    time_obj = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")

    time_obj = tzinfo.localize(time_obj)

    epoch_time = int(time_obj.timestamp())

    return epoch_time


def gmt_to_epoch(date: str) -> int:
    """
    Convert a GMT formatted date string to epoch timestamp.
    Date should follow format: "%a, %d %b %Y %H:%M:%S %Z"

    Parameters:
        date (str): A string representing the date in GMT format.
                    Example: "Mon, 15 Apr 2024 18:04:29 GMT"

    Returns:
        int: Epoch timestamp corresponding to the input date.

    Raises:
        ValueError: If the date string does not match the expected format.

    """
    return calendar.timegm(time.strptime(date, "%a, %d %b %Y %H:%M:%S %Z"))


def get_localized_datetime(
    epoch_timestamp: int, tzinfo=pytz.timezone("Europe/Helsinki")
) -> datetime:
    finnish_datetime = datetime.fromtimestamp(epoch_timestamp, tzinfo)

    return finnish_datetime

def datetime_to_epoch(datetime_to: datetime) -> int:
    return int(datetime_to.timestamp())


def main():
    # epoch = time_to_epoch("24-3-2024 00:00:00")

    date = "Mon, 15 Apr 2024 18:04:29 GMT"

    time_object2 = time.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")

    epoch2 = calendar.timegm(time_object2)
    epoch3 = gmt_to_epoch(date)

    print("My calculated epoch style 2: ", epoch2)
    print("My calculated epoch func   : ", epoch3)
    print("Right epoch:                 ", 1713204269)

    fin_date = "15-4-2024 21:04:29"
    fin_epoch = time_to_epoch(fin_date)
    my_fin_date = get_finnish_date(fin_epoch)
    my_fin_day = get_finnish_day(fin_epoch)
    my_fin_hour = get_finnish_hour(fin_epoch)
    my_fin_time = get_finnish_time(fin_epoch)

    print("Date:          ", fin_date)
    print("Fin epoch:     ", fin_epoch)
    print("Actual epoch:  ", 1713204269)
    print("Fin date:      ", my_fin_date)
    print("Fin day:       ", my_fin_day)
    print("Fin hour:      ", my_fin_hour)
    print("Fin time:      ", my_fin_time)

    test = get_localized_datetime(fin_epoch)
    print(test)


if __name__ == "__main__":
    main()
