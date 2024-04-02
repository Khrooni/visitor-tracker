from datetime import datetime, timedelta
import pytz
from typing import List


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
    y_values =  [y if y is not None else 0 for y in y_values]

    return x_values, y_values


def _get_finnish_datetime(epoch_timestamp) -> datetime:
    utc_datetime = datetime.fromtimestamp(epoch_timestamp)
    utc_timezone = pytz.utc
    finnish_timezone = pytz.timezone('Europe/Helsinki')  # Finland timezone
    
    # Convert UTC time to Finnish time
    utc_aware = utc_timezone.localize(utc_datetime)
    finnish_datetime = utc_aware.astimezone(finnish_timezone)
    
    return finnish_datetime


def get_formatted_finnish_time(epoch_timestamp) -> str | None:
    """
    Converts the epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.
    Format: 'DD-MM-YYYY HH:MM:SS EET'

    Returns None if epoch timestamp was a value that couldn't be converted.
    """
    try:
        return _get_finnish_datetime(epoch_timestamp).strftime("%d-%m-%Y %H:%M:%S %Z")
    except IOError:
        return None


def get_finnish_date(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return _get_finnish_datetime(epoch_timestamp).strftime("%d-%m-%Y")
    except IOError:
        return None


def get_finnish_time(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return _get_finnish_datetime(epoch_timestamp).strftime("%H:%M:%S")
    except IOError:
        return None


def get_finnish_hour(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return _get_finnish_datetime(epoch_timestamp).strftime("%H")
    except IOError:
        return None


def get_finnish_day(epoch_timestamp) -> str | None:
    """Returns None if epoch timestamp was a value that couldn't be converted."""
    try:
        return _get_finnish_datetime(epoch_timestamp).strftime("%A")
    except IOError:
        return None


# def epoch_to_time(epoch, utc_offset_hours=2):
#     """
#     Convert the given epoch timestamp to Finnish time zone (EET: UTC+2) and return it in a formatted string.

#     Parameters:
#         epoch (int): Epoch timestamp (UTC epoch) to convert.
#         utc_offset_hours (int, optional): Offset from UTC in hours for the target time zone.
#         Defaults to 2, representing EET (Eastern European Time, UTC+2).

#     Returns:
#         str | None: Formatted string representing the time in Finnish time zone ('DD-MM-YYYY HH:MM:SS EET') if successful, otherwise None.
#     """
#     if epoch < 0:
#         return None
#     try:
#         # utc_datetime = datetime.fromtimestamp(epoch)

#         # finnish_time_offset = timedelta(hours=utc_offset_hours)  # Finland (EET: UTC+2)

#         # finnish_datetime = utc_datetime + finnish_time_offset
#         finnish_datetime = _get_finnish_datetime(epoch)

#         formatted_finnish_time = finnish_datetime.strftime("%d-%m-%Y %H:%M:%S EET")
#     except IOError:
#         return None

#     return formatted_finnish_time


def time_to_epoch(time: str, utc_offset_hours=None) -> int | None:
    """
    Convert the given time string in 'DD-MM-YYYY HH:MM:SS' format to epoch timestamp in UTC.

    Parameters:
        time (str): Time string in 'DD-MM-YYYY HH:MM:SS' format to convert.
        utc_offset_hours (int, optional): Offset from UTC in hours for the source time zone.
            If no offset is given utc_offset is Finnish offset (UTC+2/UTC+3 depending on daylight saving hours)
        Defaults to 2, representing EET (Eastern European Time, UTC+2).

    Returns:
        int | None: Epoch timestamp if conversion is successful, otherwise None.
    """
    try:
        if utc_offset_hours is None:
            utc_offset_hours = _finnish_utc_offset(time)
        time_obj = datetime.strptime(time, "%d-%m-%Y %H:%M:%S")

        # Finland (EET: UTC+2)
        finnish_time_offset = timedelta(hours=utc_offset_hours)

        # Convert Finnish time to UTC
        utc_time = time_obj - finnish_time_offset

        # finland_timezone = pytz.timezone('UTC')

        # # Parse the Finnish time string into a datetime object
        # finnish_time = datetime.strptime(time, "%d-%m-%Y %H:%M:%S")

        # # Localize the Finnish time to the Finland timezone
        # localized_time = finland_timezone.localize(finnish_time)

        # # Convert the localized time to UTC
        # utc_time = localized_time.astimezone(pytz.utc)


        epoch_time = int(utc_time.timestamp())

        return epoch_time
    except (ValueError, OSError):
        return None
    
def _finnish_utc_offset(finnish_time_str):
    # Define the timezone for Finland
    finland_timezone = pytz.timezone('Europe/Helsinki')

    # Parse the Finnish time string into a datetime object
    finnish_time = datetime.strptime(finnish_time_str, "%d-%m-%Y %H:%M:%S")

    # Localize the Finnish time to the Finland timezone
    localized_time = finland_timezone.localize(finnish_time)

    # Get UTC offset
    utc_offset = localized_time.utcoffset()

    
    offset_hours =  utc_offset.seconds // 3600

    return offset_hours


def main():
    epoch = time_to_epoch("24-3-2024 00:00:00")
    print(epoch)
    print("Päivänä: ",time_to_epoch("25-3-2024 00:00:00"))
    print("Plussana: ", epoch + 24*60*60)
    print(get_formatted_finnish_time(1711378397))



if __name__ == "__main__":
    main()
