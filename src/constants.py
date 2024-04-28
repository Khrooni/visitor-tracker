import datetime

WINDOW_START_SIZE = (1100, 600)
WINDOW_MIN_SIZE = (850, 550)
SIDEBAR_WIDTH = 300
SIDEBAR_BUTTON_WIDTH = 170
DEFAULT_COL_INTERVAL = "30 min"
DATA_COL_INTERVALS = {
    "30 sec": 30,
    "1 min": 60,
    "5 min": 5 * 60,
    "10 min": 10 * 60,
    "30 min": 30 * 60,
    "1 hour": 60 * 60,
}
GRAPH_AMOUNTS = {"1": 1, "2": 2, "4": 4}
DEFAULT_GRAPH_AMOUNT = 1

GRAPH_MODES = {
    "Visitors": "avg",
    "Highest Visitors": "max",
    "Lowest Visitors": "min",
}
WEEKDAY_TIME_RANGE_GRAPH_MODES = {"Visitors": "avg"}
DEFAULT_GRAPH_MODE = "Visitors"

GRAPH_TYPES = ["Bar Graph", "Line Graph"]
DEFAULT_GRAPH_TYPE = "Bar Graph"
DEFAULT_GRAPH_DATE = datetime.datetime.now().strftime("%d-%m-%Y")

TEXTBOX_WIDTH = 350


DATE_ENTRY_FONT_SMALLNESS = 7  # Smaller number -> Smaller font size
CALENDAR_FONT_SMALLNESS = 12  # Smaller number -> Smaller font size

TIME_MODES = ["Calendar", "Days of the week", "Time range"]
DEFAULT_TIME_MODE = "Calendar"

DARK_GREY = "#2b2b2b"
LIGHT_GREY = "#333333"

WEEKDAYS = {
    "Monday": "mon",
    "Tuesday": "tue",
    "Wednesday": "wed",
    "Thursday": "thu",
    "Friday": "fri",
    "Saturday": "sat",
    "Sunday": "sun",
}

DEFAULT_WEEKDAY = "Monday"

TIME_RANGES = ["48 hours", "7 days", "1 month", "3 months", "6 months", "1 year", "ALL"]
DEFAULT_TIME_RANGE = "1 month"

NO_LOCATIONS = {"No locations": 0}
DEFAULT_LOCATION = next(iter(NO_LOCATIONS.keys()))

RETRIEVAL_LOCATIONS = {"FUN Oulu Ritaharju": 1}
DEFAULT_RETRIEVAL_LOCATION = "FUN Oulu Ritaharju"
