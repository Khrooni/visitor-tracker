import database

class Settings():
    def __init__(self):
        # KORJAA! Move default settings later to their own config file

        # Default settings
        self.default_db_name = database.DB_NAME
        self.default_db_directory = database.DB_DIRECTORY
        self.default_ylim = (-0.0001, None)

        # Current settings
        self.db_name = database.DB_NAME
        self.db_directory = database.DB_DIRECTORY
        self.ylim = (-0.0001, None)

    def get_db_path(self) -> str:
        return self.db_directory + self.db_name

