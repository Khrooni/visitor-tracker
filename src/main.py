from tkcalendar import DateEntry

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
from PIL import Image, ImageTk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
import matplotlib.dates as mdates


from dateutil.rrule import rrule, YEARLY, MONTHLY, DAILY, HOURLY
from datetime import datetime, date
import numpy as np
import pytz
import threading
import time
from typing import Callable, Any
import ntpath
import os


import constants
import database
import database.helpers
import retrieve_data
from retrieve_data import Location
import utils
from settings import Settings


app_settings = Settings()


class App(ctk.CTk):
    def __init__(
        self,
        title,
        size=constants.WINDOW_START_SIZE,
        min_size=constants.WINDOW_MIN_SIZE,
    ):
        super().__init__()
        self.title(title)
        positions = self._calculate_positions(size)
        self.geometry(f"{int(size[0])}x{size[1]}+{positions[0]}+{positions[1]}")
        self.minsize(min_size[0], min_size[1])

        ctk.set_appearance_mode("Dark")

        # Create bad menubar
        self.menu = MyMenuBar(self)

        # Create pages
        self.graph_page = GraphPage(self)
        self.database_page = DatabasePage(self)

        # Create Frame for pages
        container = ctk.CTkFrame(self)
        container.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # Place pages in Frame
        self.graph_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.database_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        # Bring graph page on top
        self.show_graph_page()

        # run
        self.mainloop()

    def _calculate_positions(self, size: tuple):
        window_width = size[0]
        window_height = size[1]
        display_width = self.winfo_screenwidth()
        display_height = self.winfo_screenheight()

        left = int(display_width / 2 - window_width / 2)
        top = int(display_height / 2 - window_height / 2)
        return (left, top)

    def show_graph_page(self):
        self.graph_page.lift()

    def show_database_page(self):
        self.database_page.lift()

    def open_save_file_dialog(
        self,
        confirmoverwrite: bool | None = True,
        title="Save Image",
        filetypes=[("PNG (*.png)", "*.png"), ("JPEG (*.jpg)", "*.jpg")],
    ):
        """
        Open choose filename file dialog

        Parameters:
        ---
        confirmoverwrite (bool, None):
        title (str, optional): The title of the file dialog window. Defaults to "Save Image".
        filetypes (list of tuple, optional): Each tuple contains the file type description and the corresponding file extension.
                filetypes[0][1] used as defaultextension.

        Returns:
        ---
        str: The selected file path and filetype. (example: C:/Desktop/test.png)
        """
        if filetypes:
            defaultextension = filetypes[0][1]

        file_path_type = filedialog.asksaveasfilename(
            confirmoverwrite=confirmoverwrite,
            defaultextension=defaultextension,
            title=title,
            filetypes=filetypes,
        )

        return file_path_type

    def open_choose_file_dialog(
        self,
        title="Choose a file",
        filetypes=[
            ("SQLite Database (*.db)", "*.db"),
        ],
    ):
        if filetypes:
            defaultextension = filetypes[0][1]

        file_path_name = filedialog.askopenfilename(
            defaultextension=defaultextension,
            filetypes=filetypes,
            initialdir="src\database",
            title=title,
        )

        return file_path_name


class GraphPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.pack(side=ctk.TOP, fill=ctk.BOTH, expand="true")

        self.all_graphs: list[Graph] = []
        self.graph_amount = constants.DEFAULT_GRAPH_AMOUNT

        # Used to decide if graphs need to be rearranged
        self.active_graph_amount = None

        # main frame
        self.main_frame = ctk.CTkFrame(self)

        # Add temporary "No graphs plotted"-label
        self.label = ctk.CTkLabel(
            self.main_frame,
            font=ctk.CTkFont(size=50, weight="bold"),
            text="No graphs plotted",
            width=constants.TEXTBOX_WIDTH,
            height=50,
            fg_color="transparent",
            bg_color="transparent",
            corner_radius=10,
        )
        self.label.place(relx=0.5, rely=0.45, anchor=ctk.CENTER)
        # self.label.destroy()

        self.graph1 = Graph(self.main_frame, element_color=constants.BLUE)
        self.graph2 = Graph(self.main_frame, element_color=constants.GREEN)
        self.graph3 = Graph(self.main_frame, element_color=constants.RED)
        self.graph4 = Graph(self.main_frame, element_color=constants.YELLOW)

        self.all_graphs.append(self.graph1)
        self.all_graphs.append(self.graph2)
        self.all_graphs.append(self.graph3)
        self.all_graphs.append(self.graph4)

        # Sidebar
        self.sidebar = SideBarGraph(self)
        self.sidebar.pack(fill=ctk.Y, side=ctk.LEFT)
        self.main_frame.pack(
            fill=ctk.BOTH, expand=True, side=ctk.LEFT, padx=10, pady=10
        )

    def draw_all_graphs(self):
        if self.graph_amount != self.active_graph_amount:
            self._arrange_graphs()

        for graph_num in range(self.graph_amount):
            self.all_graphs[graph_num].draw_graph(self.graph_amount)

        self.active_graph_amount = self.graph_amount

    def draw_single_graph(self, graph_num: int):
        if self.graph_amount != self.active_graph_amount:
            self._arrange_graphs()

        if self.graph_amount >= (graph_num + 1):
            self.all_graphs[graph_num].draw_graph(self.graph_amount)

        self.active_graph_amount = self.graph_amount

    def _arrange_graphs(self):
        self.label.destroy()

        if self.graph_amount == 1:
            self.graph1.grid_forget()
            self.graph2.grid_forget()
            self.graph3.grid_forget()
            self.graph4.grid_forget()

            self.graph1.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=10)
            self.graph2.pack_forget()
            self.graph3.pack_forget()
            self.graph4.pack_forget()
        elif self.graph_amount == 2:
            self.graph1.grid_forget()
            self.graph2.grid_forget()
            self.graph3.grid_forget()
            self.graph4.grid_forget()

            self.graph1.pack(
                side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=(10, 0)
            )
            self.graph2.pack(
                side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=(0, 10)
            )
            self.graph3.pack_forget()
            self.graph4.pack_forget()
        elif self.graph_amount == 4:
            self.graph1.pack_forget()
            self.graph2.pack_forget()
            self.graph3.pack_forget()
            self.graph4.pack_forget()

            self.main_frame.columnconfigure((0, 1), weight=1)
            self.main_frame.rowconfigure((0, 1), weight=1)
            self.graph1.grid(sticky="nsew", row=0, column=0, padx=(10, 0), pady=(10, 0))
            self.graph2.grid(sticky="nsew", row=0, column=1, padx=(0, 10), pady=(10, 0))
            self.graph3.grid(sticky="nsew", row=1, column=0, padx=(10, 0), pady=(0, 10))
            self.graph4.grid(sticky="nsew", row=1, column=1, padx=(0, 10), pady=(0, 10))

    def get_drawn_graphs(self) -> list[int]:
        """Return list of numbers of graphs that have been drawn."""
        drawn_graphs: list[int] = []
        for i, graph in enumerate(self.all_graphs):
            if graph.is_drawn:
                drawn_graphs.append(i + 1)

        return drawn_graphs

    def get_fig(self, graph_num: int) -> Figure:
        """graph num = index of graph"""
        return self.all_graphs[graph_num].fig


class SideBarGraph(ctk.CTkFrame):
    def __init__(
        self,
        parent: GraphPage,
        width=constants.SIDEBAR_WIDTH,
    ):
        super().__init__(parent, width=width, corner_radius=0)
        self.pack_propagate(False)
        self.parent: GraphPage = parent

        self.locations, self.default_location, self.unique_dates = (
            self._get_locations_dates()
        )

        # Sidebar "Graphs"-label
        self.logo_label = ctk.CTkLabel(
            self, text="Graphs", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(side=ctk.TOP, padx=10, pady=(20, 10))

        # "Plot All Graphs"-button
        self.plot_all_button = ctk.CTkButton(
            self,
            command=self.plot_all_button_event,
            text="Plot All Graphs",
            width=constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.plot_all_button.pack(side=ctk.TOP, padx=10, pady=(5, 10))

        # Graph Amount dropdown menu and label
        self.graph_amount_menu = DropdownAndLabel(
            self,
            "Graph Amount:",
            list(constants.GRAPH_AMOUNTS.keys()),
            self.change_graph_amount_event,
            constants.DEFAULT_GRAPH_AMOUNT,
            constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.graph_amount_menu.pack(side=ctk.TOP, padx=10, pady=0)

        # Create graph tabview
        self.tabview = ctk.CTkTabview(self, width=constants.SIDEBAR_WIDTH)
        self.tabview.pack(side=ctk.TOP, fill=ctk.Y, expand=True, pady=(15, 10), padx=10)
        self.tabview._segmented_button.configure(font=ctk.CTkFont(size=15))
        self.tabview.pack_propagate(False)

        self.graph_tabs: list[GraphTab] = []

        # Create 4 graph tabs
        for i in range(4):
            graph_name = f"Graph {i+1}"
            self.graph_tabs.append(
                GraphTab(
                    self.tabview,
                    graph_name,
                    self.parent,
                    i,
                    self.unique_dates,
                    self.parent.all_graphs[i],
                    self.locations,
                    self.default_location,
                )
            )

        self.disable_tab_buttons(constants.DEFAULT_GRAPH_AMOUNT)

    def plot_all_button_event(self):
        self.parent.draw_all_graphs()

    def change_graph_amount_event(self, value):
        new_amount = constants.GRAPH_AMOUNTS.get(value)

        if new_amount > self.parent.graph_amount:
            self.enable_tab_buttons(new_amount)
        elif new_amount < self.parent.graph_amount:
            self.disable_tab_buttons(new_amount)

        self.parent.graph_amount = new_amount

    def update_cals(self, dates: list[str]):
        for graph_tab in self.graph_tabs:
            graph_tab.update_cal(dates)

    def update_locations(self, locations: dict[str, int], location_name: str):
        for graph_tab in self.graph_tabs:
            graph_tab.graph.locations = locations
            graph_tab.graph.location_name = location_name

    def update_all(self):
        locations, location_name, unique_dates = self._get_locations_dates()
        self.update_locations(locations, location_name)
        self.update_cals(unique_dates)

    def _get_locations_dates(self) -> tuple[dict[str, int], str, list[str]]:
        """
        Get all locations from the database. The first location from the database
        is used as the selected location (location_name). The selected location is used to get
        unique dates that have visitor data.

        Returns
        ---
        tuple[all_locations, location_name, unique_dates]
        """
        locations = constants.NO_LOCATIONS
        default_location = constants.DEFAULT_LOCATION
        unique_dates = []

        db_handle = None
        try:
            db_handle = database.SQLiteDBManager(app_settings.db_path)

            locations_dict = db_handle.get_locations_dict()

            if locations_dict:
                locations = locations_dict
                default_location = next(iter(locations_dict.keys()))

            unique_dates = db_handle.get_unique_dates(locations.get(default_location))
        finally:
            if db_handle:
                db_handle.__del__()

        return locations, default_location, unique_dates

    def disable_tab_buttons(self, graph_amount: int):
        """Disable 'Plot Graph'-button in all GraphTabs that exceed graph amount"""
        max_tabs = 4
        disable_amount = max_tabs - graph_amount

        for i in range(disable_amount):
            self.graph_tabs[(max_tabs - 1) - i].plot_graph_button.configure(
                state=ctk.DISABLED
            )

    def enable_tab_buttons(self, graph_amount: int):
        for i in range(graph_amount - 1):
            # i + 1 (first tab button is never disabled)
            self.graph_tabs[i + 1].plot_graph_button.configure(state=ctk.NORMAL)


class Graph(ctk.CTkFrame):
    def __init__(
        self, master=None, element_color="red", padx=0, pady=0, *args, **kwargs
    ):
        super().__init__(master, *args, **kwargs)
        self.time_mode: str = constants.DEFAULT_TIME_MODE
        self.locations: dict = constants.NO_LOCATIONS
        self.location_name: str = constants.DEFAULT_LOCATION

        self.graph_mode: str = constants.DEFAULT_GRAPH_MODE
        self.graph_type: str = constants.DEFAULT_GRAPH_TYPE

        self.graph_date: str = constants.DEFAULT_GRAPH_DATE
        self.weekday: str = constants.DEFAULT_WEEKDAY
        self.time_range: str = constants.DEFAULT_TIME_RANGE

        self.is_drawn = False
        self.title: str = "Default title"
        self.x_values: list = []
        self.y_values: list = []
        self.x_label: str = "x label"
        self.y_label: str = "y label"
        self.element_color: str = element_color
        self.facecolor: str = constants.LIGHT_GREY
        self.edge_color: str = "grey"
        self.axis_colors: str = "white"

        self.pack_propagate(False)
        self.fig = Figure(
            figsize=(20, 20),
            facecolor=self.facecolor,
            layout="constrained",
        )
        self.ax = self.fig.add_subplot()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=padx, pady=pady)

        # Hide annoying white lines caused by canvas background by changing canvas bg color
        # to match surrounding color. (These lines seem to only show up with certain fig sizes)
        self.canvas.get_tk_widget().configure(background=constants.LIGHT_GREY)

    def draw_graph(self, graph_amount: int = 1):
        """If graph amount 4 only every other value is used for bar graph"""
        self._get_graph_data()
        self._set_graph_settings(graph_amount)

        if self.graph_type.lower() == "bar graph":

            width = np.diff(self.x_values).min() * 0.80

            self.ax.bar(
                self.x_values,
                self.y_values,
                color=self.element_color,
                align="center",
                width=width,
            )
            self.ax.xaxis_date()

        elif self.graph_type.lower() == "line graph":
            self.ax.plot(
                self.x_values,
                self.y_values,
                color=self.element_color,
                # marker=".",
            )
            self.ax.set_ylim(-0.0001, None)

        self.canvas.draw()
        self.is_drawn = True

    def _get_graph_data(self) -> bool:
        try:
            db_handle = database.SQLiteDBManager(app_settings.db_path)
            if self.time_mode == "Calendar":
                search_start, search_end = self._get_search_range()
                visitors = db_handle.get_data_by_mode(
                    self.locations.get(self.location_name),
                    search_start,
                    search_end,
                    constants.GRAPH_MODES.get(self.graph_mode),
                    60 * 60,
                )
                timestamps = database.helpers.calculate_timestamps(
                    search_start, search_end, 60 * 60
                )
            elif self.time_mode == "Days of the week":
                visitors = db_handle.get_average_visitors(
                    self.locations.get(self.location_name),
                    constants.WEEKDAYS.get(self.weekday),
                )

                # Korjaa! Voisi varmaan suoraan hakea tunnit eikä hakea epocheja,
                # jotka muutetaan tunneiksi convert_for_day_graphilla
                timestamps = utils.day_epochs()

            elif self.time_mode == "Time range":
                time_r_interval = 60 * 60
                search_start, search_end = self._get_search_range()
                visitors = db_handle.get_data_by_mode(
                    self.locations.get(self.location_name),
                    search_start,
                    search_end,
                    constants.GRAPH_MODES.get(self.graph_mode),
                    60 * 60,
                )
                timestamps = database.helpers.calculate_timestamps(
                    search_start, search_end, 60 * 60
                )
        finally:
            db_handle.__del__()

        self._set_title_labels(timestamps)

        self.x_values = utils.epochs_to_format(timestamps, "datetime")
        self.y_values = utils.nones_to_zeros(visitors)

    def _get_search_range(self) -> tuple[int, int]:
        search_start: int
        search_end: int

        print("Mode:", self.time_mode)
        if self.time_mode == "Calendar":
            search_start = utils.formatted_date_to_epoch(f"{self.graph_date} 00:00:00")
            search_end = utils.next_time(search_start, days=1)  # +1 day
        elif self.time_mode == "Time range":
            print("Time range:", self.time_range)

            search_end_dt = utils.top_of_the_hour(datetime.now())
            search_end = utils.datetime_to_epoch(search_end_dt)

            time_dif_td = utils.get_time_delta(self.time_range, "negative")
            if time_dif_td:
                search_start_dt = search_end_dt + time_dif_td
                search_start = utils.datetime_to_epoch(search_start_dt)

                print(search_start_dt)
            else:
                search_start = self._get_all_search_start()

            print(search_end_dt)
        else:
            print("SHOULD NOT GET HERE!")

        print("Search start:", utils.get_formatted_finnish_time(search_start))
        print("Search end:  ", utils.get_formatted_finnish_time(search_end))

        return search_start, search_end

    def _get_all_search_start(self) -> int | None:
        try:
            db_handle = database.SQLiteDBManager(app_settings.db_path)
            search_start = db_handle.get_first_time(
                self.locations.get(self.location_name)
            )
        finally:
            db_handle.__del__()

        search_start_dt = utils.top_of_the_hour(
            utils.get_localized_datetime(search_start)
        )

        return utils.datetime_to_epoch(search_start_dt)

    def get_first(self) -> datetime | None:
        try:
            db_handle = database.SQLiteDBManager(app_settings.db_path)
            search_start = db_handle.get_first_time(
                self.locations.get(self.location_name)
            )
        finally:
            db_handle.__del__()

        if search_start:
            search_start = utils.get_localized_datetime(search_start)

        return search_start

    def _set_graph_settings(self, graph_amount: int):
        self.ax.clear()
        self.ax.set_facecolor(self.axis_colors)
        self.ax.set_title(self.title, color=self.axis_colors)
        self.ax.set_xlabel(self.x_label, color=self.axis_colors)
        self.ax.set_ylabel(self.y_label, color=self.axis_colors)
        self.ax.yaxis.set_tick_params(
            color=self.axis_colors, labelcolor=self.axis_colors
        )
        self.ax.xaxis.set_tick_params(
            which=ctk.BOTH,
            color=self.axis_colors,
            labelcolor=self.axis_colors,
        )

        for spine in self.ax.axes.spines.values():
            spine.set_edgecolor(self.edge_color)

        if self.time_mode == "Time range":

            locator = mdates.AutoDateLocator(tz=constants.DEFAULT_TIMEZONE)
            formatter = mdates.ConciseDateFormatter(
                locator, tz=constants.DEFAULT_TIMEZONE
            )

            # alku_dt = datetime(2024, 3)
            # for i in range(8):
            #     jep = locator.get_locator(alku_dt, datetime(2024, 4+i))
            #     print("locator:", jep)
            #     print("\n")

            # locator.intervald[DAILY] = [1,2,3,7, 14, 21, 30]
            # # locator.intervald[MONTHLY] = [6]

            # '%#d' only works with windows. '%-d' on linux
            formatter.formats = [
                # "(f_y) %y",  # ticks are mostly years
                # "(f_m) %b",  # ticks are mostly months
                # "(f_d) %a, %#d.",  # ticks are mostly days
                # "(f_h) %H:%M",  # hrs
                # "(f_m) %H:%M",  # min
                # "(f_s) %S.%f",  # secs
                "%y",  # ticks are mostly years
                "%b",  # ticks are mostly months
                "%a, %#d.",  # ticks are mostly days
                "%H:%M",  # hrs
                "%H:%M",  # min
                "%S.%f",  # secs
            ]

            formatter.zero_formats = [
                # "(zf_y)",
                # "(zf_m) %b %Y",
                # "(zf_d) %b '%y",
                # "(zf_h) %a, %#d.",  # '%#d' only works with windows. '%-d' on linux
                # "(zf_m) %H:%M",
                # "(zf_s) %H:%M",
                "",
                "%b %Y",
                "%b '%y",
                "%a, %#d.",  # '%#d' only works with windows. '%-d' on linux
                "%H:%M",
                "%H:%M",
            ]

            formatter.offset_formats = [
                "%Y",
                "%Y",
                "%b %Y",
                "%d %b %Y",
                "%d %b %Y",
                "%d %b %Y %H:%M",
            ]

            self.ax.xaxis.set_major_locator(locator)
            self.ax.xaxis.set_major_formatter(formatter)
        else:
            interval = 1

            # x-values go over each other if 4 graphs on screen. Figures are too small.
            if graph_amount == 4:
                interval = 2

            locator = mdates.HourLocator(
                byhour=range(24), interval=interval, tz=constants.DEFAULT_TIMEZONE
            )
            # '%#H' only works on windows
            formatter = mdates.DateFormatter("%#H", tz=constants.DEFAULT_TIMEZONE)

            self.ax.xaxis.set_major_locator(locator)
            self.ax.xaxis.set_major_formatter(formatter)

            lower_limit, upper_limit = self.get_limits(self.x_values)
            self.ax.set_xlim(lower_limit, upper_limit)

    def _set_title_labels(self, timestamps: list[int]):
        if self.time_mode == "Calendar":
            # Korjaa! Lisää check, että oikean tyyppistä dataa.
            # for time_stamp in data[0]:
            for time_stamp in timestamps:
                if time_stamp is not None:
                    found_date = time_stamp
                    break
            date = utils.get_finnish_date(found_date)
            day = utils.get_finnish_day(found_date)

            self.title = f"{self.location_name}, {day}, {date}"
            self.x_label = "Hour"
            self.y_label = self.graph_mode
        elif self.time_mode == "Days of the week":
            self.title = f"{self.location_name}, {self.weekday}"
            self.x_label = "Hour"
            self.y_label = self.graph_mode

        elif self.time_mode == "Time range":
            self.title = f"{self.location_name}"
            self.x_label = ""
            self.y_label = self.graph_mode

    def get_limits(self, datetimes: list[datetime]) -> tuple[datetime, datetime]:
        """
        Calculate and return the lower and upper limits based on a list of datetime objects.

        The function computes the difference between the first two datetime objects in the list.
        It then uses this difference to calculate a lower limit by subtracting 0.75% of the difference
        from the first datetime, and an upper limit by adding 0.75% of the difference to the last datetime.

        Parameters:
        ---
        datetimes : list[datetime]
            A list of datetime objects. The list must contain at least two elements.
            The datetime should be in chronological order, starting from the earliest
            to the latest.

        Returns:
        ---
        tuple[datetime, datetime]
            A tuple containing the calculated lower and upper limits as datetime objects.

        Raises:
        ---
        ValueError
            If the list contains fewer than two datetime objects.
        """
        if len(datetimes) >= 2:
            difference = (
                datetimes[1] - datetimes[0]
                if datetimes[0] < datetimes[1]
                else datetimes[0] - datetimes[1]
            )
        else:
            raise ValueError("The list must contain at least two datetime objects")

        lower_lim = datetimes[0] - (difference * 0.75)
        upper_lim = datetimes[-1] + (difference * 0.75)

        return lower_lim, upper_lim

    def reduce_values(self, values: list[Any | str]) -> list[Any | str]:
        """Change every other value in a list to empty string ''."""
        for i in range(len(values)):
            if (i % 2) == 1:
                values[i] = ""

        return values


class GraphTab:
    def __init__(
        self,
        parent: ctk.CTkTabview,
        tab_name: str,
        graph_page: GraphPage,
        graph_num: int,
        unique_dates: list[str],
        graph: Graph,
        locations: dict[str, int],
        default_location: str,
    ):
        parent.add(tab_name)
        self.handle = parent.tab(tab_name)

        self.graph_page = graph_page
        self.graph_num = graph_num
        self.graph: Graph = graph
        self.graph.locations = locations
        self.graph.location_name = default_location

        # create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.handle)
        self.scrollable_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # "Plot graph"-button
        self.plot_graph_button = ctk.CTkButton(
            self.scrollable_frame,
            command=self.plot_single_graph_event,
            text="Plot Graph",
            width=constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.plot_graph_button.pack(side=ctk.TOP, padx=10, pady=(10, 10))

        self.time_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=constants.LIGHT_GREY,
            border_width=1,
            border_color=constants.LIGHT_GREY,
        )
        self.time_frame.pack(side=ctk.TOP)

        # Time Mode dropdown menu and label
        self.time_mode_menu = DropdownAndLabel(
            self.time_frame,
            "Time Mode:",
            constants.TIME_MODES,
            self.change_time_mode_event,
            constants.DEFAULT_TIME_MODE,
            constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.time_mode_menu.pack(side=ctk.TOP, padx=10, pady=(5, 10))

        # Frame for different time modes
        self.time_mode_frame = ctk.CTkFrame(
            self.time_frame,
            width=constants.SIDEBAR_BUTTON_WIDTH + 10,
            height=90,
            fg_color=constants.DARK_GREY,
        )
        self.time_mode_frame.pack(side=ctk.TOP, expand=True, pady=(0, 5))
        self.time_mode_frame.pack_propagate(False)

        # Calendar frame
        self.calendar_frame = ctk.CTkFrame(self.time_mode_frame, fg_color="transparent")
        self.calendar_frame.place(
            in_=self.time_mode_frame,
            relx=0.5,
            rely=0.5,
            anchor=ctk.CENTER,
        )
        # "Open Calendar"-button
        self.open_calendar_button = ctk.CTkButton(
            self.calendar_frame,
            command=self.open_calendar_event,
            text="Open Calendar",
            width=constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.open_calendar_button.pack(side=ctk.TOP, pady=10)
        # Create constructive frame for Calendar
        self.cal_frame = ctk.CTkFrame(
            self.calendar_frame,
            width=constants.SIDEBAR_BUTTON_WIDTH,
            height=30,
        )
        self.cal_frame.pack(side=ctk.TOP, pady=(0, 10))
        self.cal_frame.pack_propagate(False)

        # Create Calendar
        self.cal = CustomDateEntry(
            self.cal_frame,
            dates=unique_dates,
            date_pattern="dd-mm-yyyy",
            justify="center",
            width=constants.SIDEBAR_BUTTON_WIDTH,
            bg="#1E6FBA",
            fg="yellow",
            disabledbackground="#1E6FBA",
            highlightbackground="black",
            highlightcolor="red",
            highlightthickness=1,
            bd=0,
            selectmode="day",
            locale="en_US",
            disabledforeground="red",
            cursor="hand2",
            background=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
            selectbackground=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1],
            mindate=self.graph.get_first(),
            maxdate=date.today(),
        )
        self.cal.highlight_dates()
        self.cal.bind("<<DateEntrySelected>>", self.update_date)  # Update calendar date
        self.cal.bind("<Key>", lambda e: "break")  # Disable writing in calendar
        self.cal.bind("<Control-c>", lambda e: None)  # Enable Ctrl + c
        self.cal.bind("<Control-a>", lambda e: None)  # Enable Ctrl + a
        self.cal.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # Weekday frame
        self.weekday_frame = ctk.CTkFrame(
            self.time_mode_frame,
            fg_color="transparent",
            # border_color=DARK_GREY,
            # border_width=2,
            # width=SIDEBAR_BUTTON_WIDTH,
        )
        self.weekday_frame.place(
            in_=self.time_mode_frame,
            relx=0.5,
            rely=0.5,
            anchor=ctk.CENTER,
        )
        # Weekday dropdown menu and label
        self.weekday_menu = DropdownAndLabel(
            self.weekday_frame,
            "Weekday",
            list(constants.WEEKDAYS.keys()),
            self.change_weekday_event,
            constants.DEFAULT_WEEKDAY,
            constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.weekday_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

        # Time range frame
        self.time_range_frame = ctk.CTkFrame(
            self.time_mode_frame,
            fg_color="transparent",
            # border_color=DARK_GREY,
            # border_width=2,
            # width=SIDEBAR_BUTTON_WIDTH,
        )
        self.time_range_frame.place(
            in_=self.time_mode_frame,
            relx=0.5,
            rely=0.5,
            anchor=ctk.CENTER,
        )
        # Time range dropdown menu and label
        self.time_range_menu = DropdownAndLabel(
            self.time_range_frame,
            # "From now to:",
            "Last:",
            constants.TIME_RANGES,
            self.change_time_range_event,
            constants.DEFAULT_TIME_RANGE,
            constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.time_range_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

        # Lift calendar frame to top
        self.calendar_frame.lift()

        # Graph Mode dropdown menu and label
        self.graph_mode_menu = DropdownAndLabel(
            self.scrollable_frame,
            "Graph Mode:",
            list(constants.GRAPH_MODES.keys()),
            self.change_graph_mode_event,
            constants.DEFAULT_GRAPH_MODE,
            constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.graph_mode_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

        # Graph Type dropdown menu and label
        self.graph_type_menu = DropdownAndLabel(
            self.scrollable_frame,
            "Graph Type:",
            constants.GRAPH_TYPES,
            self.change_graph_type_event,
            constants.DEFAULT_GRAPH_TYPE,
            constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.graph_type_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

        # Location dropdown menu and label
        self.location_menu = DropdownAndLabel(
            self.scrollable_frame,
            "Location:",
            list(self.graph.locations.keys()),
            self.change_location_event,
            self.graph.location_name,
            constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.location_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

    def update_cal(self, dates: list[str]):
        """Removes old highlighted dates from the calendar and highlights dates in the
        given dates list."""
        self.cal.dates = dates
        self.cal.configure(mindate=self.graph.get_first(), maxdate=date.today())
        self.cal.highlight_dates()

    def plot_single_graph_event(self):
        print("plot single graph")
        self.graph_page.draw_single_graph(self.graph_num)

        # if self.graph_page.graph_amount >= self.graph.graph_num:
        #     if self.graph_page.fig is None:
        #         self.graph_page.set_fig_and_ax()
        #     self.graph.draw_graph()

    def open_calendar_event(self):
        self.cal.drop_down()

    def update_date(self, event):
        self.graph.graph_date = self.cal.get_date().strftime("%d-%m-%Y")
        print("Selected Date: ", self.cal.get_date())

    def change_graph_type_event(self, value):
        print("Set graph type to: ", value)
        self.graph.graph_type = value

    def change_graph_mode_event(self, value):
        print("Set graph value to: ", value)
        # oikea = GRAPH_MODES.get(value)
        self.graph.graph_mode = value

    def change_time_mode_event(self, value):
        print("Set time mode to: ", value)
        if value == "Calendar":
            self.calendar_frame.lift()
            self.graph_mode_menu.set_menu_values(
                constants.GRAPH_MODES, constants.DEFAULT_GRAPH_MODE
            )
            self.graph.graph_mode = constants.DEFAULT_GRAPH_MODE

            self.graph_type_menu.set_menu_values(
                constants.GRAPH_TYPES, constants.DEFAULT_GRAPH_TYPE
            )
            self.graph.graph_type = constants.DEFAULT_GRAPH_TYPE
        elif value == "Days of the week":
            self.weekday_frame.lift()
            self.graph_mode_menu.set_menu_values(
                constants.WEEKDAY_TIME_RANGE_GRAPH_MODES, constants.DEFAULT_GRAPH_MODE
            )
            self.graph.graph_mode = constants.DEFAULT_GRAPH_MODE

            self.graph_type_menu.set_menu_values(
                constants.GRAPH_TYPES, constants.DEFAULT_GRAPH_TYPE
            )
            self.graph.graph_type = constants.DEFAULT_GRAPH_TYPE

        elif value == "Time range":
            self.time_range_frame.lift()

            self.graph_mode_menu.set_menu_values(
                constants.WEEKDAY_TIME_RANGE_GRAPH_MODES, constants.DEFAULT_GRAPH_MODE
            )
            self.graph.graph_mode = constants.DEFAULT_GRAPH_MODE

            self.graph_type_menu.set_menu_values(
                constants.TIME_RANGE_GRAPH_TYPES, constants.DEFAULT_TR_GRAPH_TYPE
            )
            self.graph.graph_type = constants.DEFAULT_TR_GRAPH_TYPE

        self.graph.time_mode = value

    def change_weekday_event(self, value):
        print("Set weekday to: ", value)
        self.graph.weekday = value

    def change_time_range_event(self, value):
        print("Set time range to: ", value)
        self.graph.time_range = value

    def change_location_event(self, value):
        print("Set location to:", value)
        self.graph.location_name = value
        print("Set Calendar minimum date")
        # Change Calendar mindate to match selected location
        self.cal.configure(mindate=self.graph.get_first())


class DropdownAndLabel(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        label: str,
        values: list,
        command: Callable[[str], Any],
        default_value: str,
        menu_width: int,
        fg_color: str = "transparent",
    ):
        super().__init__(parent, corner_radius=0, fg_color=fg_color)

        # Graph label
        self.label = ctk.CTkLabel(self, text=label, anchor="w")
        self.label.pack(side=ctk.TOP, padx=0, pady=(0, 5))
        # Graph dropdown menu
        self.option_menu = ctk.CTkOptionMenu(
            self,
            values=values,
            command=command,
            variable=ctk.StringVar(value=default_value),
            width=menu_width,
        )
        self.option_menu.pack(side=ctk.TOP, padx=0, pady=0)

    def set_menu_values(self, values: list[str], default_value: str):
        self.option_menu.configure(
            values=values, variable=ctk.StringVar(value=default_value)
        )


class DatabasePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)

        self.pack(side=ctk.TOP, fill=ctk.BOTH, expand="true")

        self.main_frame = MainFrameDatabase(self)
        self.sidebar = SideBarDatabase(self, self.main_frame)


class MainFrameDatabase(ctk.CTkFrame):
    def __init__(
        self, parent: DatabasePage, width=0, side=ctk.RIGHT, expand=False, fill=None
    ):
        super().__init__(parent)
        self.col_interval = constants.DEFAULT_COL_INTERVAL
        self.col_active = False

        # create frame for textbox label and textbox
        self.textbox_frame = ctk.CTkFrame(parent, width=constants.TEXTBOX_WIDTH)
        self.textbox_frame.pack(side=ctk.RIGHT, fill=ctk.Y, padx=(0, 10), pady=10)
        self.textbox_frame.pack_propagate(False)
        # create textbox label
        self.textbox_label = ctk.CTkLabel(
            self.textbox_frame,
            font=ctk.CTkFont(size=15, weight="bold"),
            text="Database events",
            width=constants.TEXTBOX_WIDTH,
            height=20,
            fg_color="transparent",
            bg_color="transparent",
            corner_radius=10,
        )
        self.textbox_label.pack(
            side=ctk.TOP,
            padx=10,
            pady=(10, 0),
        )
        # create textbox (read only)
        self.textbox = ctk.CTkTextbox(self.textbox_frame)
        self.textbox.pack(
            side=ctk.TOP,
            fill=ctk.BOTH,
            expand=True,
            padx=10,
            pady=10,
        )
        self.textbox.bind("<Key>", lambda e: "break")
        self.textbox.bind("<Control-c>", lambda e: None)  # Enable Ctrl + c
        self.textbox.bind("<Control-a>", lambda e: None)  # Enable Ctrl + a

        self.pack_propagate(False)
        self.pack(fill=ctk.BOTH, expand=True, side=side, padx=10, pady=10)

        # Active Settings Label
        self.info_label = ctk.CTkLabel(
            self,
            font=ctk.CTkFont(size=20, weight="bold"),
            text="Active Settings",
            width=constants.TEXTBOX_WIDTH,
            height=20,
            fg_color="transparent",
            bg_color="transparent",
            corner_radius=10,
        )
        self.info_label.pack(side=ctk.TOP, pady=10)

        # collection Checkbox
        self.collection_checkbox = ctk.CTkCheckBox(
            master=self,
            text="Active Data Collection",
            text_color="white",
            text_color_disabled="white",
            hover=False,
            fg_color="green",
            border_color="red",
        )
        self.collection_checkbox.configure(state=ctk.DISABLED)
        self.collection_checkbox.pack(side=ctk.TOP, pady=(50, 0))

        self.interval_label = ctk.CTkLabel(
            self,
            text=f"Active Data Collection Interval: {self.col_interval}",
            corner_radius=10,
            fg_color=constants.DARK_GREY,
            padx=10,
            pady=20,
        )
        self.interval_label.pack(side=ctk.TOP, pady=(10, 10))

    def write_to_textbox(self, text: str):
        self.textbox.insert("0.0", text)

    def toggle_collection(self):
        self.col_active = not self.col_active
        self.collection_checkbox.configure(state=ctk.NORMAL)
        self.collection_checkbox.toggle()
        self.collection_checkbox.configure(state=ctk.DISABLED)

    def change_interval(self, interval: str):
        self.col_interval = interval
        self.write_to_textbox(f"Interval changed to {interval}\n\n")

    def change_interval_label(self, interval: str):
        self.interval_label.configure(
            text=f"Active Data Collection Interval: {interval}"
        )


class SideBarDatabase(ctk.CTkFrame):
    def __init__(
        self,
        parent: DatabasePage,
        main_frame: MainFrameDatabase,
        width=constants.SIDEBAR_WIDTH,
    ):
        super().__init__(parent, width=width, corner_radius=0)
        self.thread_id = 1  # Used for stopping data collection
        self.col_interval = constants.DEFAULT_COL_INTERVAL

        self.parent = parent
        self.main_frame = main_frame
        self.unique_dates = []

        try:
            db_handle = database.SQLiteDBManager(app_settings.db_path)
            self.unique_dates = db_handle.get_unique_dates(
                constants.RETRIEVAL_LOCATIONS.get(constants.DEFAULT_RETRIEVAL_LOCATION)
            )
        finally:
            db_handle.__del__()

        self.pack(fill=ctk.Y, side=ctk.LEFT)
        self.pack_propagate(False)

        # Sidebar label
        self.logo_label = ctk.CTkLabel(
            self, text="Database", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(side=ctk.TOP, padx=10, pady=(20, 0))

        # Button frame for start/stop data collection
        button_frame = ctk.CTkFrame(self, height=80, fg_color="transparent")
        button_frame.pack(fill=ctk.Y, expand=False)
        # Start data collection Button
        self.start_button = ctk.CTkButton(
            self,
            fg_color="#74bc50",
            hover_color="green",
            width=constants.SIDEBAR_BUTTON_WIDTH,
            command=self.start_collecting_data,
            text="Start data collection",
        )
        self.start_button.place(
            in_=button_frame,
            relx=0.5,
            rely=0.5,
            anchor=ctk.CENTER,
        )
        # Stop data collection Button
        self.stop_button = ctk.CTkButton(
            self,
            fg_color="#fe0101",
            hover_color="#ed6464",
            width=constants.SIDEBAR_BUTTON_WIDTH,
            command=self.stop_collecting_data,
            text="Stop data collection",
        )
        self.stop_button.place(
            in_=button_frame,
            relx=0.5,
            rely=0.5,
            anchor=ctk.CENTER,
        )
        # Start data collection button on top
        self.start_button.lift()

        # Interval dropdown menu label
        self.interval_label = ctk.CTkLabel(
            self, text="Data Collection Interval:", anchor="w"
        )
        self.interval_label.pack(side=ctk.TOP, padx=10, pady=(10, 0))
        # Interval dropdown menu
        self.interval_option_menu = ctk.CTkOptionMenu(
            self,
            values=list(constants.DATA_COL_INTERVALS.keys()),
            command=self.change_interval_event,
            variable=ctk.StringVar(value=constants.DEFAULT_COL_INTERVAL),
            width=constants.SIDEBAR_BUTTON_WIDTH,
        )
        self.interval_option_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

    def write_to_textbox(self, text: str):
        self.main_frame.write_to_textbox(text)

    def start_collecting_data(self):
        self.stop_button.lift()
        self.main_frame.toggle_collection()
        self.main_frame.change_interval_label(self.col_interval)
        self.write_to_textbox("Data Collection Started!\n\n")

        deamon_thread = threading.Thread(
            target=self._get_data_in_intervals,
            args=(constants.DATA_COL_INTERVALS.get(self.col_interval), self.thread_id),
        )
        deamon_thread.daemon = True
        deamon_thread.start()

    def stop_collecting_data(self):
        self.start_button.lift()
        self.thread_id += 1  # Stop data collection
        self.main_frame.toggle_collection()
        self.write_to_textbox("Data Collection Stopped!\n\n")

    def change_interval_event(self, value):
        self.col_interval = value  # Set sidebar interval
        self.main_frame.change_interval(value)  # Set main_frame interval

    def _get_data_in_intervals(self, interval: int, thread_id: int):
        try:
            db_handle = database.SQLiteDBManager(app_settings.db_path)

            # Collect data until theard_id changes
            while thread_id == self.thread_id:
                start_time = time.perf_counter()

                data = retrieve_data.get_data()
                location: Location
                for location in data:
                    added = db_handle.add_data(
                        location.location_id,
                        location.location_name,
                        location.epoch_timestamp,
                        location.location_visitors,
                    )
                    if not added:
                        self.write_to_textbox(
                            f"Unable to add data to the database. A record with the "
                            f"same timestamp already exists. "
                            f"Discarded data: \n{self._format_data(location)}\n\n"
                        )
                    else:
                        self.write_to_textbox(
                            f"Added to the database: {self._format_data(location)}\n\n"
                        )

                func_time = time.perf_counter() - start_time
                sleep_time = max(0, (interval - func_time))
                time.sleep(sleep_time)  # Sleep for remaining time
        except Exception as e:
            self.write_to_textbox(
                f"Data collection aborted. Restarting app might be necessary. Database error: {e}\n\n"
            )
            self.stop_collecting_data()  # Toggle data collection button off
        finally:
            db_handle.__del__()

        # return

    def _format_data(self, location_data: Location):
        formatted_str = f"""
        \tLocation name: {location_data.location_name}
        \tTime: {utils.get_formatted_finnish_time(location_data.epoch_timestamp)}
        \tVisitor amount: {location_data.location_visitors}
        """

        return formatted_str


class CustomDateEntry(DateEntry):
    """
    Note: showothermonthdays=False on default to avoid bug caused by highlighting
    dates outside current selected month. Creating a calevent for a date in the calendar
    changes the 'style' of date from ('normal'/'normal_om' or 'we'/'we_om') to 'tag_%s' (tag_name).
    - DateEntry -> Calendar -> Calendar._on_click()
    - tkcalendar.calendar_.py -> Calendar._on_click


        self._calendar.calevent_create(dt, "Has Data", tag) creates a calevent that changes style of the date

        Following check fails because style is always 'tag_%s' (tag_name)

        if style in ['normal_om.%s.TLabel' % self._style_prefixe, 'we_om.%s.TLabel' % self._style_prefixe]:
            if label in self._calendar[0]:
                self._prev_month()
            else:
                self._next_month()
    """

    def __init__(
        self, master=None, dates: list[str] = None, showothermonthdays=False, **kw
    ):
        if dates is None:
            dates = []
        super().__init__(master, showothermonthdays=showothermonthdays, **kw)
        self.dates = dates
        self.configure_size()
        self.bind("<Configure>", self.update_on_resize)  # Bind to the Configure event

    def drop_down(self):
        """Display or withdraw the drop-down calendar depending on its current state."""
        if self._calendar.winfo_ismapped():
            self._top_cal.withdraw()
        else:
            self._validate_date()
            date = self.parse_date(self.get())
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            if self.winfo_toplevel().attributes("-topmost"):
                self._top_cal.attributes("-topmost", True)
            else:
                self._top_cal.attributes("-topmost", False)
            # - patch begin: Stop calendar from opeing outside screen.
            current_screen_height = utils.get_monitor_from_coord(x, y).height
            if y + self._top_cal.winfo_height() > current_screen_height - 70:
                y = self.winfo_rooty() - self._top_cal.winfo_height()
            # - patch end
            self._top_cal.geometry("+%i+%i" % (x, y))
            self._top_cal.deiconify()
            self._calendar.focus_set()
            self._calendar.selection_set(date)

    def configure_size(self):
        # Calculate the font size based on the width of the widget
        width = self.winfo_width()
        font_size = int(width / constants.DATE_ENTRY_FONT_SMALLNESS)
        cal_font_size = int(width / constants.CALENDAR_FONT_SMALLNESS)

        # Create a font object with the calculated size
        self.custom_font = ctk.CTkFont(
            family="Helvetica", size=font_size, weight="bold"
        )
        self.custom_cal_font = ctk.CTkFont(
            family="Helvetica", size=cal_font_size, weight="bold"
        )

        # Update the font configuration for the widget
        self.configure(font=self.custom_font)
        self._calendar.configure(font=self.custom_cal_font)

    def highlight_dates(self):
        self._calendar.calevent_remove("all")
        tag_name = "Data"
        for date in self.dates:
            dt = datetime.strptime(date, "%d-%m-%Y")
            self._calendar.calevent_create(dt, "Has Data", tag_name)

        self._calendar.tag_config(tag_name, background="#19a84c", foreground="white")

    def update_on_resize(self, event):
        self.configure_size()


class MyMenuBar(CTkMenuBar):
    def __init__(self, parent: App, *args, **kwargs):
        super().__init__(parent, bg_color="#484848", *args, **kwargs)
        self.parent = parent

        # Menubar buttons
        file_button = self.add_cascade("File", text_color="white")
        view_button = self.add_cascade("View", text_color="white")
        self.add_cascade(
            "Settings", self.open_settings, text_color="white", cursor="hand2"
        )
        help_button = self.add_cascade("Help", text_color="white")

        # Buttons in File
        file_dropdown = CustomDropdownMenu(master=parent, widget=file_button)
        # Save buttons
        file_dropdown.add_option("Save Figure", command=self.save_fig)
        file_dropdown.add_option("Save Single Graph", command=self.save_single_graph)
        file_dropdown.add_separator()
        # Choose database submenu
        # sub_menu = file_dropdown.add_submenu("Choose Database")
        file_dropdown.add_option(option="Use default database", command=self.use_default_db)
        file_dropdown.add_option(option="Choose database", command=self.select_db)

        # Buttons in View
        view_dropdown = CustomDropdownMenu(master=parent, widget=view_button)
        view_dropdown.add_option(
            option="Graphs", command=lambda: parent.show_graph_page()
        )
        view_dropdown.add_option(
            option="Database", command=lambda: parent.show_database_page()
        )

        # Buttons in Help
        help_dropdown = CustomDropdownMenu(master=parent, widget=help_button)
        help_dropdown.add_option(
            option="How to use", command=lambda: print("How to use")
        )
        help_dropdown.add_option(option="something", command=self._something_temp)

    def open_settings(self):
        SettingsPopup(self.parent, "Settings")
    
    def use_default_db(self):
        default_filepath = os.path.relpath(app_settings.default_db_path)

        if app_settings.db_path:
            old_filepath = os.path.relpath(app_settings.db_path)

        if old_filepath == default_filepath:
            messagebox.showinfo(
                "Info", "The default database is already in use."
            )
        else:
            if messagebox.askokcancel("Use default database?", f"Do you wish to change currently used database ({old_filepath}) to default database ({default_filepath})?"):
                app_settings.db_path = default_filepath
                self.parent.graph_page.sidebar.update_all()



    def select_db(self):
        new_filepath = self.parent.open_choose_file_dialog("Select database")

        if new_filepath:
            new_filepath = os.path.relpath(new_filepath)
            old_filepath = os.path.relpath(app_settings.db_path)

            if messagebox.askokcancel("Change database?", f"Do you wish to change currently used database ({old_filepath}) to selected database ({new_filepath})?"):
                app_settings.db_path = new_filepath
                self.parent.graph_page.sidebar.update_all() 




    def default_db(self):
        default_filepath = os.path.relpath(app_settings.default_db_path)

        if self.filepath:
            rel_path = os.path.relpath(self.filepath)

        if rel_path == default_filepath:
            messagebox.showinfo(
                "Info", "No changes made. The default database is already selected."
            )
        else:
            _, tail = ntpath.split(default_filepath)
            self.db_path_frame.winfo_children()[1].configure(text=tail)
            self.filepath = default_filepath

    def save_single_graph(self):
        drawn_graphs = self.parent.graph_page.get_drawn_graphs()
        if drawn_graphs:
            SaveSinglePopup(self.parent, "Select graph", drawn_graphs)
        else:
            messagebox.showerror(
                "Error",
                "No graphs have been drawn yet. Draw a graph before attempting to save.",
            )

    def save_fig(self):
        print("Save fig")
        drawn_graphs = self.parent.graph_page.get_drawn_graphs()
        if drawn_graphs:

            file_path = self.parent.open_save_file_dialog(title="Save Figure")
            if file_path:
                images = []

                for i in range(self.parent.graph_page.active_graph_amount):
                    canvas = self.parent.graph_page.all_graphs[i].fig.canvas
                    images.append(
                        Image.frombytes(
                            "RGB", canvas.get_width_height(), canvas.tostring_rgb()
                        )
                    )

                width, height = self._new_fig_size(images)

                new_im = self._combine_images(images, width, height)
                new_im.save(file_path)
        else:
            messagebox.showerror(
                "Error",
                "No graphs have been drawn yet. Draw a graph before attempting to save.",
            )

    def _new_fig_size(self, images: list[Image.Image]) -> tuple[int, int]:
        """
        Returns the size of the new image.


        If images has only 1 image the new image size is the size of the original image

        If images has 2 images
            the new width is image0 + image1 width
            the new height is the max(height) of the two images

        if images has 4 images
            the new width is max(image0, image2) + max(image1, image3) width
            the new height is max(image0, image1) + max(image2, image3) height

        returns
        ---
        width, height
        """
        width = 0
        height = 0
        if len(images) == 1:
            return images[0].size
        if len(images) == 2:
            for img in images:
                height += img.height
            width = max([img.width for img in images])

        if len(images) == 4:
            width += max(images[0].width, images[2].width)
            width += max(images[1].width, images[3].width)

            height += max(images[0].height, images[1].height)
            height += max(images[2].height, images[3].height)

        return width, height

    def _combine_images(
        self, images: list[Image.Image], width: int, height: int
    ) -> Image.Image:
        new_im = Image.new("RGB", (width, height))

        x_offset = 0
        y_offset = 0
        for i, im in enumerate(images):
            new_im.paste(im, (x_offset, y_offset))
            x_offset += im.size[0]
            if (i == 1 and len(images) == 4) or (i == 0 and len(images) == 2):
                x_offset = 0
                y_offset += im.size[1]

        return new_im

    def _something_temp(self):
        print("something")


class SettingsFrame(ctk.CTkFrame):
    def __init__(
        self,
        master,
        corner_radius: int | str | None = 0,
        **kwargs,
    ):
        """
        **kwargs
        ---
        width: int = 200,
        height: int = 200,
        border_width: int | str | None = None,
        bg_color: str | Tuple[str, str] = "transparent",
        fg_color: str | Tuple[str, str] | None = None,
        border_color: str | Tuple[str, str] | None = None,
        background_corner_colors: Tuple[str | Tuple[str, str]] | None = None,
        overwrite_preferred_drawing_method: str | None = None,

        ---
        Construct a frame widget with the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, class, colormap, container, cursor, height,
        highlightbackground, highlightcolor, highlightthickness, relief, takefocus, visual, width.
        """
        super().__init__(master=master, corner_radius=corner_radius, **kwargs)

    def add_title(
        self, text: str, font_size=15, font_weight="bold", padx=8, pady=8
    ) -> ctk.CTkLabel:
        label = ctk.CTkLabel(self, text=text, anchor="w", height=0)
        label.cget("font").configure(size=font_size, weight=font_weight)
        label.pack(side=ctk.TOP, anchor="w", padx=padx, pady=pady)

        return label

    def add_setting(
        self,
        label_text: str,
        button_text: str,
        command,
        font_size=12,
        label_width=125,
        pady=8,
        padx=8,
        padx_inner=20,
        fill="x",
        **kwargs,
    ) -> ctk.CTkFrame:
        """
        Frame with a label. kwargs go to CTkButton
        """
        # Frame
        setting_frame = ctk.CTkFrame(self, fg_color="transparent")
        setting_frame.pack(side=ctk.TOP, anchor="w", fill=ctk.X)
        # Label
        self.label = ctk.CTkLabel(
            setting_frame, text=label_text, anchor="w", height=0, width=label_width
        )
        self.label.cget("font").configure(size=font_size)
        self.label.pack(side=ctk.LEFT, anchor="w", padx=(padx_inner, 0), pady=(0, pady))
        # Button
        self.button = ctk.CTkButton(
            setting_frame,
            text=button_text,
            command=command,
            font=self.label.cget("font"),
            fg_color=constants.DARK_GREY_SETTINGS_BUTTON,
            border_color="black",
            border_width=1,
            height=0,
            width=0,
            anchor="w",
            border_spacing=4,
            **kwargs,
        )
        # self.button._text_label.configure(wraplength=500)
        self.button.pack(
            side=ctk.LEFT,
            anchor="w",
            padx=(0, padx),
            pady=(0, pady),
            fill=fill,
            expand=True,
        )

        return setting_frame



class InfoButton(ctk.CTkButton):
    def __init__(
        self,
        parent,
        command=None,
        popup_title="Info",
        popup_info_text="Info text",
        *args,
        **kwargs,
    ):
        """
        If command = None, popup_title and popup_info_text are used with messagebox.showinfo().
        """
        if not command:
            command = lambda: self.info_popup(popup_title, popup_info_text)

        # Info image
        info_img = Image.open("src\images\information-button.png")
        info_img_ctk = ctk.CTkImage(
            light_image=info_img, dark_image=info_img, size=(15, 15)
        )

        super().__init__(
            parent,
            image=info_img_ctk,
            width=1,
            height=1,
            corner_radius=50,
            hover_color="#afafaf",
            text="",
            fg_color="white",
            bg_color="transparent",
            command=command,
            round_height_to_even_numbers=False,
            round_width_to_even_numbers=False,
            *args,
            **kwargs,
        )

    def info_popup(self, title="Info", info_text="Info text"):
        messagebox.showinfo(title, info_text, master=self)


class MyPopup(ctk.CTkToplevel):
    def __init__(
        self,
        parent: App,
        title: str,
        geometry="250x300",
        minsize=(250, 300),
        maxsize=(250, 300),
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)

        self.geometry(geometry)
        if minsize:
            self.minsize(minsize[0], minsize[1])
        if maxsize:
            self.maxsize(maxsize[0], maxsize[1])
        self.title(title)
        self.grab_set()

        self.bottom_frame = ctk.CTkFrame(self, height=50, corner_radius=0)

    def add_bottom_button(
        self,
        text: str,
        command,
        master: ctk.CTkFrame | None = None,
        width=80,
        height=5,
        corner_radius=0,
        border_width=0.5,
        *args,
        **kwargs,
    ) -> ctk.CTkButton:
        """
        If master is None self.bottom_frame is used.
        CTkButton *args/**kwargs are usable
        """
        if not master:
            master = self.bottom_frame

        padx = (5, 5)
        if not master.winfo_children():
            # More right padding for first button
            padx = (5, 15)

        button = ctk.CTkButton(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            text=text,
            command=command,
            *args,
            **kwargs,
        )
        button.pack(side=ctk.RIGHT, padx=padx)

        return button

    def _cancel_event(self):
        self.destroy()

    def add_cancel_button(
        self,
        master: ctk.CTkFrame | None = None,
        width=80,
        height=5,
        corner_radius=0,
        border_width=0.5,
        *args,
        **kwargs,
    ) -> ctk.CTkButton:
        return self.add_bottom_button(
            "Cancel",
            self._cancel_event,
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            *args,
            **kwargs,
        )

    def pack_bottom_frame(self) -> ctk.CTkFrame:
        """
        Returns bottom_frame

        pack: side=bottom, fill=both and pack_propagate=False
        """
        self.bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.X)
        self.bottom_frame.pack_propagate(False)

        return self.bottom_frame


class SaveSinglePopup(MyPopup):
    def __init__(
        self, parent: App, title: str, drawn_graphs: list[int], *args, **kwargs
    ):
        super().__init__(parent, title, *args, **kwargs)
        self.parent = parent
        self.chosen_graph = None

        # Open square image
        img_square = Image.open("src\images\square1234.png")
        img_square_ctk = ctk.CTkImage(
            light_image=img_square, dark_image=img_square, size=(150, 150)
        )
        # Label + add square image to label
        img_square_label = ctk.CTkLabel(self, text="", image=img_square_ctk)
        img_square_label.pack(side=ctk.TOP)

        # Dropdown and info frame
        drop_info_frame = ctk.CTkFrame(
            self, bg_color="transparent", fg_color="transparent"
        )
        drop_info_frame.pack(side=ctk.TOP)

        # Choose graph dropdown and label
        drawn_graphs = [str(i) for i in drawn_graphs]
        choose_graph_menu = DropdownAndLabel(
            drop_info_frame,
            "Choose which graph to save:",
            drawn_graphs,
            self._choose_graph_event,
            "Graph number",
            menu_width=150,
        )
        choose_graph_menu.pack(side=ctk.LEFT, padx=10, pady=0, anchor="center")

        info_button = InfoButton(
            drop_info_frame,
            popup_title="Info",
            popup_info_text="Only graphs that have been drawn will be available for saving."
            + "\n\nThis includes graphs that may not currently be visible on the screen "
            + "but have been previously drawn.",
        )
        info_button.pack(side=ctk.LEFT, anchor="se")

        # Pack bottom frame
        bottom_frame = self.pack_bottom_frame()

        # Cancel button
        cancel_button = self.add_cancel_button()

        # OK button
        self.ok_button: ctk.CTkButton = self.add_bottom_button(
            text="OK", command=self._ok_event, state=ctk.DISABLED
        )

    def _choose_graph_event(self, value):
        print("Choose graph event:", value)
        self.chosen_graph = int(value) - 1
        self.ok_button.configure(state=ctk.NORMAL)

    def _cancel_event(self):
        self.destroy()

    def _ok_event(self):
        fig = self.parent.graph_page.get_fig(self.chosen_graph)
        file_path = self.parent.open_save_file_dialog(title="Save Graph")
        if file_path:
            fig.savefig(fname=file_path)
            self.destroy()

    def _info_event(self):
        messagebox.showinfo(
            "Info",
            "Only graphs that have been drawn will be available for saving."
            + "\n\nThis includes graphs that may not currently be visible on the screen "
            + "but have been previously drawn.",
            master=self,
        )


class SettingsPopup(MyPopup):
    def __init__(self, parent: App, title: str, *args, **kwargs):
        super().__init__(
            parent,
            title,
            geometry="400x300",
            minsize=(400, 300),
            maxsize=(600, 400),
            *args,
            **kwargs,
        )
        self.parent = parent
        self.filepath = app_settings.db_path
        self.ylim = app_settings.ylim

        pad = 8

        # Settings label
        label = ctk.CTkLabel(
            self,
            text="Settings",
            anchor="w",
            padx=5,
            pady=10,
            bg_color=constants.LIGHT_GREY,
        )
        label.cget("font").configure(size=20, weight="bold")
        label.pack(side=ctk.TOP, anchor="w", fill=ctk.BOTH, padx=pad, pady=pad)

        # Database
        db_frame = SettingsFrame(self)
        db_frame.pack(side=ctk.TOP, anchor="w", fill=ctk.BOTH, padx=pad, pady=pad)

        db_frame.add_title("Database")
        _, tail = ntpath.split(app_settings.db_path)
        self.db_path_frame = db_frame.add_setting(
            "Database file:", tail, self.select_db
        )
        db_frame.add_setting("", "Select Default Database", self.default_db, fill=None)

        # Graphs
        graph_frame = SettingsFrame(self)
        graph_frame.pack(side=ctk.TOP, anchor="w", fill=ctk.BOTH, padx=pad, pady=pad)

        graph_frame.add_title("Graphs")
        self.ylims_frame = graph_frame.add_setting("y-axis limits:", app_settings.ylim, self.select_ylim)

        # Bottom frame
        self.pack_bottom_frame()
        self.add_cancel_button()
        self.add_bottom_button("OK", self._ok_event)
        self.add_bottom_button("Reset", self._reset_event)

    def _ok_event(self):
        if self.filepath and self.filepath != os.path.relpath(app_settings.db_path):
            app_settings.db_path = self.filepath
            self.parent.graph_page.sidebar.update_all()

        if self.ylim:
            app_settings.ylim = self.ylim

        self.destroy()

    def _reset_event(self):
        if messagebox.askokcancel("Reset settings?", "Do you really want to reset settings to default values?"):
            self.filepath = app_settings.default_db_path
            self.ylim = app_settings.default_ylim

            _, tail = ntpath.split(self.filepath)
            self.db_path_frame.winfo_children()[1].configure(text=tail)

            self.ylims_frame.winfo_children()[1].configure(text=self.ylim)


    def select_db(self):
        filepath = self.parent.open_choose_file_dialog("Select database")

        if filepath:
            filepath = os.path.relpath(filepath)
            self.filepath = filepath

            _, tail = ntpath.split(filepath)

            self.db_path_frame.winfo_children()[1].configure(text=tail)

    def default_db(self):
        default_filepath = os.path.relpath(app_settings.default_db_path)

        if self.filepath:
            rel_path = os.path.relpath(self.filepath)

        if rel_path == default_filepath:
            messagebox.showinfo(
                "Info", "No changes made. The default database is already selected."
            )
        else:
            _, tail = ntpath.split(default_filepath)
            self.db_path_frame.winfo_children()[1].configure(text=tail)
            self.filepath = default_filepath

    def select_ylim(self):
        print("Select ylim")


class SelectDBPopup(MyPopup):
    def __init__(self, parent: App, title: str, *args, **kwargs):
        super().__init__(
            parent,
            title,
            geometry="400x300",
            minsize=(400, 300),
            # maxsize=(250, 300),
            *args,
            **kwargs,
        )
        self.parent = parent
        self.db_name = None
        self.db_directory = None

        # Settings label
        label = ctk.CTkLabel(
            self,
            text="Choose database",
            anchor="w",
            padx=5,
            pady=10,
            bg_color=constants.LIGHT_GREY,
        )
        label.cget("font").configure(size=20, weight="bold")
        label.pack(
            side=ctk.TOP,
            anchor="w",
            fill=ctk.BOTH,
            padx=constants.PAD,
            pady=constants.PAD,
        )

        self.pack_bottom_frame()
        self.add_cancel_button()
        self.add_bottom_button("OK", self._ok_event)

    def _select_db_event(self):
        filepath = self.parent.open_choose_file_dialog("Select database")

    def _default_db_event(self):
        print("default db event")

    def _ok_event(self):
        print("OK event")


def main():
    App("VisitorFlowTracker")


if __name__ == "__main__":
    main()
