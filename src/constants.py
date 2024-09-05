import datetime
import pytz

WINDOW_START_SIZE = (1150, 600)
WINDOW_MIN_SIZE = (1000, 550)
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
MAX_GRAPH_AMOUNT = 4

GRAPH_MODES = {
    "Visitors": "avg",
    "Most Visitors": "max",
    "Least Visitors": "min",
}
WEEKDAY_TIME_RANGE_GRAPH_MODES = {"Visitors": "avg"}
DEFAULT_GRAPH_MODE = "Visitors"


GRAPH_TYPES = ["Bar Graph", "Line Graph"]
DEFAULT_GRAPH_TYPE = "Bar Graph"

TIME_RANGE_GRAPH_TYPES = ["Line Graph"]
DEFAULT_TR_GRAPH_TYPE = "Line Graph"

DEFAULT_GRAPH_DATE = datetime.datetime.now().strftime("%d-%m-%Y")

DEFAULT_TIMEZONE = pytz.timezone("Europe/Helsinki")

TEXTBOX_WIDTH = 350


DATE_ENTRY_FONT_SMALLNESS = 7  # Smaller number -> Smaller font size
CALENDAR_FONT_SMALLNESS = 12  # Smaller number -> Smaller font size

TIME_MODES = ["Calendar", "Daily Average", "Time Range"]
DEFAULT_TIME_MODE = "Calendar"

LIGHT_GREY = "#333333"
DARK_GREY = "#2b2b2b"

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
DEFAULT_TIME_RANGE = "48 hours"

NO_LOCATIONS = {"No locations": 0}
DEFAULT_LOCATION = next(iter(NO_LOCATIONS.keys()))

RETRIEVAL_LOCATIONS = {"FUN Oulu Ritaharju": 1}
DEFAULT_RETRIEVAL_LOCATION = "FUN Oulu Ritaharju"

SQUARE_BLUE = "#697a96"
SQUARE_GREEN = "#809372"
SQUARE_RED = "#d45252"
SQUARE_YELLOW = "#fbc070"

GRAPH_COLORS = [SQUARE_BLUE, SQUARE_GREEN, SQUARE_RED, SQUARE_YELLOW]

BLUE = "#6c95d9"
GREEN = "#6be014"
RED = "#f01a1a"
YELLOW = "#dede47"

DARK_GREY_SETTINGS_BUTTON = "#302c2c"
DARK_BLUE_HOVER_COLOR = "#144870"

PAD = 8

YMODES = ["Auto Limit", "No Limit", "Select Limit"]

DB_FILETYPES = [("SQLite Database (*.db)", "*.db")]
DB_DEFAULTEXTENSION = DB_FILETYPES[0][1]
DB_INITIALDIR= "src/database"

IMG_FILETYPES = [("PNG (*.png)", "*.png"), ("JPEG (*.jpg)", "*.jpg")]
IMG_DEFAULTEXTENSION = IMG_FILETYPES[0][1]
