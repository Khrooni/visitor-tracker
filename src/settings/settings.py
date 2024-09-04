from configparser import ConfigParser

import database


class Settings:
    def __init__(self, config_path="src/settings/config.ini"):
        self.config_path = config_path
        self.config = ConfigParser()
        config_exists = self.config.read(self.config_path)

        if not config_exists:
            self._create_config()

        # Current settings
        self.db_path = self.config.get("main", "db_path")

        lower = self.config.get("main", "lower_ylim")
        upper = self.config.get("main", "upper_ylim")
        lower = None if lower == "None" else float(lower)
        upper = None if upper == "None" else float(upper)

        self.ylim = (lower, upper)
        self.ymode = self.config.get("main", "ymode")

    def _save(self, config_path):
        with open(config_path, "w", encoding="UTF-8") as f:
            self.config.write(f)

    def _create_config(self):
        """Create the config file for the first time."""
        self.config.add_section("default")
        self.config.set("default", "db_path", "src/database/visitorTrackingDB.db")
        self.config.set("default", "lower_ylim", str(-0.0001))
        self.config.set("default", "upper_ylim", str(None))
        self.config.set("default", "ymode", "Auto Limit")

        self.config.add_section("main")
        self.config.set("main", "db_path", "src/database/visitorTrackingDB.db")
        self.config.set("main", "lower_ylim", str(-0.0001))
        self.config.set("main", "upper_ylim", str(None))
        self.config.set("main", "ymode", "Auto Limit")

        self._save(self.config_path)

    def _set_db_path(self, db_path: str):
        self.config.set("main", "db_path", db_path)

    def _set_ylim(self, lower_ylim: float | None, upper_ylim: float | None):
        self.config.set("main", "lower_ylim", lower_ylim)
        self.config.set("main", "upper_ylim", upper_ylim)

    def _set_ymode(self, ymode: str):
        self.config.set("main", "ymode", ymode)

    def update_all(self):
        """Update config.ini to match set Settings class variables
        (db_path, ylim, ymode)"""
        self._set_db_path(self.db_path)
        self._set_ylim(str(self.ylim[0]), str(self.ylim[1]))
        self._set_ymode(self.ymode)

        self._save(self.config_path)

    def get_default_db_path(self):
        return self.config.get("default", "db_path")

    def get_default_ylim(self) -> tuple[float | None, float | None]:
        lower = self.config.get("default", "lower_ylim")
        upper = self.config.get("default", "upper_ylim")
        lower = None if lower == "None" else float(lower)
        upper = None if upper == "None" else float(upper)

        ylim = (lower, upper)
        return ylim

    def get_default_ymode(self):
        return self.config.get("default", "ymode")

    def set_to_defaults(self):
        """Set class variables (db_path, ylim, ymode) to default"""
        self.db_path = self.get_default_db_path()
        self.ylim = self.get_default_ylim()
        self.ymode = self.get_default_ymode()
