from datetime import datetime, timedelta, timezone
import pytz


def epoch_to_finnish_time(epoch):
    """
    Converts the given epoch timestamp to Finnish time zone (EET: UTC+2) and returns it in a formatted string.
    Format: 'DD-MM-YYYY HH:MM:SS EET'
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


def time_to_epoch(time: str) -> int | None:
    try:
        time_obj = datetime.strptime(time, "%d-%m-%Y %H:%M:%S")

        # Finland (EET: UTC+2)
        finnish_time_offset = timedelta(hours=2)

        # Convert Finnish time to UTC
        utc_time_obj = time_obj - finnish_time_offset

        epoch_time = int(utc_time_obj.timestamp())

        return epoch_time
    except (ValueError, OSError):
        return None


def main():

    edge_cases2 = [
        "12-02-2023 12:00:00",
        "29-02-2024 12:00:00",  # Leap year, February 29th
        "31-04-2024 12:00:00",  # April with 31 days
        "32-12-2024 12:00:00",  # Day exceeds maximum days in a month
        "12-00-2024 12:00:00",  # Month is 00, invalid
        "12-13-2024 12:00:00",  # Month exceeds maximum value
        "12-12-0000 12:00:00",  # Year 0000
        "02-01-1970 4:00:00",  # Year 0999
        "02-01-1970 1:59:59",  # Year 0999
        "12-12-9999 12:00:00",  # Year 9999
        "12-12-2024 25:00:00",  # Hour exceeds 24
        "12-12-2024 12:60:00",  # Minute exceeds 59
        "12-12-2024 12:00:60",  # Second exceeds 59
        "12-12-2024 12:00:00",  # Valid time string
        "01-01-1969 00:00:00",  # Before Unix epoch
        "27-03-2022 03:00:00",  # Start of DST in Finland
        "30-10-2022 04:00:00",  # End of DST in Finland
        "27-03-2022 02:00:00",  # Transition from standard time to DST
        "30-10-2022 03:00:00",  # Transition from DST to standard time
        "invalid_format",  # Invalid time string format
    ]

    print(epoch_to_finnish_time((253402300796)))
    fin_time = None
    for case in edge_cases2:
        print(f"Testing with time string: {case}")
        epoch_time = time_to_epoch(case)
        if epoch_time is not None:
            print(f"Epoch time: {epoch_time}")
            if epoch_time is not None:
                fin_time = epoch_to_finnish_time(epoch_time)
            else:
                fin_time = None

            print(f"epoch ({epoch_time} is: {fin_time})")
        print()

    print(epoch_to_finnish_time(1711485419))


if __name__ == "__main__":
    main()
