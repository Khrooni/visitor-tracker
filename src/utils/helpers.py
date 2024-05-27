from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import time
import calendar
from typing import Callable, Any
import screeninfo


def get_monitor_from_coord(x: int, y: int) -> screeninfo.Monitor:
    monitors = screeninfo.get_monitors()

    for monitor in reversed(monitors):
        if (
            monitor.x <= x <= monitor.width + monitor.x
            and monitor.y <= y <= monitor.height + monitor.y
        ):
            return monitor
    return monitors[0]


def convert_for_day_graph(
    x_values: list[int], y_values: list[int | None]
) -> tuple[list[str], list[int]]:
    """
    Convert x_values (epoch timestamps) to hour string ('00', '01', ... ,'23') and
    convert y_values (visitor_amounts) that are None to int 0.
    """
    return epochs_to_format(x_values, "hour"), nones_to_zeros(y_values)


def top_of_the_hour(dt: datetime, tzinfo=pytz.timezone("Europe/Helsinki")) -> datetime:
    """
    Returns datetime object with start of closest previous hour.
    """
    return reset_dt_timezone(dt.replace(minute=0, second=0, microsecond=0), tzinfo)


def epochs_to_format(epochs: list[int], mode: str) -> list[str]:
    """
    Convert a list of epoch timestamps to formatted strings based on the given mode.

    Parameters:
    - epochs (list[int]): A list of epoch timestamps to be formatted.
    - mode (str): The mode specifying the desired formatting type.
                  Valid modes are 'hour', 'day', 'time', 'date', 'formatted_time'
                  and 'datetime'.

    Returns:
    - list[str]: A list of formatted strings corresponding to the epochs based on the selected mode.

    Raises:
    - ValueError: If an invalid mode is provided.
    """

    format_functions = {
        "hour": get_finnish_hour,
        "day": get_finnish_day,
        "time": get_finnish_time,
        "date": get_finnish_date,
        "formatted_time": get_formatted_finnish_time,
        "datetime": get_localized_datetime,
    }

    format_function: Callable[[int], str] = format_functions.get(mode)

    if format_function is None:
        raise ValueError(f"Invalid mode '{mode}'")

    formatted_list = [format_function(epoch) for epoch in epochs]

    return formatted_list


def day_epochs() -> list[int]:
    """
    Returns a list of epochs with values in interval 1 hour from
    December 12, 2024 00:00:00 GMT+02:00 to December 12, 2024 23:00:00 GMT+02:00.
    """

    epochs = []

    start_epoch = 1733954400  # Thursday, December 12, 2024 00:00:00 GMT+02:00

    hour = 60 * 60

    for i in range(24):
        epochs.append(start_epoch + (i * hour))

    return epochs


def nones_to_zeros(my_list: list[Any | None]) -> list[Any | int]:
    """Convert all None values to 0."""
    return [value if value is not None else 0 for value in my_list]


def datetime_to_utc(datetime_to: datetime) -> datetime:
    return datetime_to.astimezone(pytz.utc)


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


def get_finnish_time(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return get_localized_datetime(epoch_timestamp).strftime("%H:%M:%S")
    except IOError:
        return None


def get_finnish_date(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return get_localized_datetime(epoch_timestamp).strftime("%d-%m-%Y")
    except IOError:
        return None


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


def formatted_date_to_epoch(date: str, tzinfo=pytz.timezone("Europe/Helsinki")) -> int:
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
    Example: "Mon, 15 Apr 2024 18:04:29 GMT"

    Raises:
        ValueError: If the date string does not match the expected format.
    """
    return calendar.timegm(time.strptime(date, "%a, %d %b %Y %H:%M:%S %Z"))


def get_localized_datetime(
    epoch_timestamp: int, tzinfo=pytz.timezone("Europe/Helsinki")
) -> datetime:
    finnish_datetime = datetime.fromtimestamp(epoch_timestamp, tzinfo)

    return finnish_datetime


def next_time(
    epoch_timestamp: int, tzinfo=pytz.timezone("Europe/Helsinki"), days=0, weeks=0
) -> int:
    """
    Adds days/weeks to given epoch. Takes into account daylight saving time.

    Example: 31.3.2024 00:00:00 + day -> 1.4.2024 00:00:00
    (even though (31.3.2024 00:00:00 + 24 hours) = (1.4.2024 01:00:00)
    due to daylight saving time)

    Note: Doesn't work if the given epoch_timestamp is exactly by seconds
    the exact time when daylight saving time changes.
    """

    start_dt = get_localized_datetime(epoch_timestamp, tzinfo)
    next_dt = start_dt + timedelta(days=days, weeks=weeks)

    next_dt = reset_dt_timezone(next_dt, tzinfo)

    return datetime_to_epoch(next_dt)


def get_time_delta(time_str: str, direction="positive") -> relativedelta | None:
    """
    If direction positive -> value = abs(value). If direction negative ->
    value = -abs(value). Else keep original.
    """
    if time_str == "ALL":
        return None

    value, unit = time_str.split()
    value = int(value)

    if direction == "positive":
        value = abs(value)
    elif direction == "negative":
        value = -abs(value)

    if unit == "hours":
        return relativedelta(hours=value)
    elif unit == "days":
        return relativedelta(days=value)
    elif unit == "month" or unit == "months":
        return relativedelta(months=value)
    elif unit == "year":
        return relativedelta(years=value)
    else:
        raise ValueError("Invalid time unit")


def year_change(dt1: datetime, dt2: datetime) -> bool:
    return dt1.year != dt2.year


def reset_dt_timezone(
    dt: datetime, tzinfo=pytz.timezone("Europe/Helsinki")
) -> datetime:
    """
    Sets tzinfo to None and then sets it to given tzinfo.
    (Change timezone without converting time to new timezones time.)
    """
    return tzinfo.localize(dt.replace(tzinfo=None))


def datetime_to_epoch(datetime_to: datetime) -> int:
    return int(datetime_to.timestamp())


def main():
    date = "Mon, 15 Apr 2024 18:04:29 GMT"

    time_object2 = time.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")

    epoch2 = calendar.timegm(time_object2)
    epoch3 = gmt_to_epoch(date)

    print("My calculated epoch style 2: ", epoch2)
    print("My calculated epoch func   : ", epoch3)
    print("Right epoch:                 ", 1713204269)

    fin_date = "15-4-2024 21:04:29"
    fin_epoch = formatted_date_to_epoch(fin_date)
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
