import re
import string


def are_ints(*args):
    """True if all given arguments were of type int. False otherwise."""
    for arg in args:
        if not isinstance(arg, int):
            return False
    return True


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


def main():
    test = "dsa231sadsad23321____31312321ädadäåqwertyuiopåäölkjhgfdsazxcvbnm"
    test2 = "----;;;;2131321DELETE"
    print(valid_table_name(test))
    print(valid_table_name(test2))
    print(valid_table_name(""))
    print(valid_table_name("das-"))
    print(valid_table_name("löä"))
    print(valid_table_name(";"))
    print(valid_table_name("+"))
    print(valid_table_name("-"))



if __name__ == "__main__":
    main()
