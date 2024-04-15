import re
import string
from typing import List
from datetime import datetime
import utils




def are_ints(*args):
    """True if all given arguments were of type int. False otherwise."""
    for arg in args:
        if not isinstance(arg, int):
            return False
    return True

def calculate_days(start: int, end: int, weekday:str):
    next_weekday = utils.next_weekday(start, weekday)
    previous_weekday = utils.previous_weekday(end, weekday)

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
