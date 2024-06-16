import database

class Settings():
    def __init__(self):
        # KORJAA! Move default settings later to their own config file

        # Default settings
        self.default_db_path = database.DB_FILE_PATH
        self.default_ylim = (-0.0001, None)

        # Current settings
        self.db_path = database.DB_FILE_PATH
        self.ylim = (-0.0001, None)

    def set_path_to_default(self):
        self.db_path = self.default_db_path
