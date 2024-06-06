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
        positions = self._calculte_positions(size)
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

    def _calculte_positions(self, size: tuple):
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

    def open_file_dialog(
        self,
        confirmoverwrite: bool | None = True,
        title="Save Image",
        filetypes=[("PNG (*.png)", "*.png"), ("JPEG (*.jpg)", "*.jpg")],
    ):
        """
        Open a file dialog.

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
        """Return list of graph numbres of graphs that have been drawn."""
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
        self.parent: GraphPage = parent

        self.unique_dates = []
        self.locations = {"No locations": 0}
        self.default_location = next(iter(self.locations.keys()))

        db_handle = None
        try:
            db_handle = database.SQLiteDBManager(app_settings.get_db_path())

            locations_dict = db_handle.get_locations_dict()

            if locations_dict:
                self.locations = locations_dict
                self.default_location = next(iter(locations_dict.keys()))

            self.unique_dates = db_handle.get_unique_dates(
                self.locations.get(self.default_location)
            )
        finally:
            if db_handle:
                db_handle.__del__()

        self.pack_propagate(False)

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
        print("width:", self.parent.winfo_screenwidth())
        print("PLOTTING bars...")
        self.parent.draw_all_graphs()

    def change_graph_amount_event(self, value):
        print("Amount: ", value)
        new_amount = constants.GRAPH_AMOUNTS.get(value)

        if new_amount > self.parent.graph_amount:
            self.enable_tab_buttons(new_amount)
        elif new_amount < self.parent.graph_amount:
            self.disable_tab_buttons(new_amount)

        self.parent.graph_amount = new_amount

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
            db_handle = database.SQLiteDBManager(app_settings.get_db_path())
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
            db_handle = database.SQLiteDBManager(app_settings.get_db_path())
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
            db_handle = database.SQLiteDBManager(app_settings.get_db_path())
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
                "(f_y) %y",  # ticks are mostly years
                "(f_m) %b",  # ticks are mostly months
                "(f_d) %a, %#d.",  # ticks are mostly days
                "(f_h) %H:%M",  # hrs
                "(f_m) %H:%M",  # min
                "(f_s) %S.%f",  # secs
            ]

            formatter.zero_formats = [
                "(zf_y)",
                "(zf_m) %b %Y",
                "(zf_d) %b '%y",
                "(zf_h) %a, %#d. %b",  # '%#d' only works with windows. '%-d' on linux
                "(zf_m) %H:%M",
                "(zf_s) %H:%M",
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
        unique_dates: list[int],
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
        print("Set Calendar minumum date")
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
            db_handle = database.SQLiteDBManager(app_settings.get_db_path())
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
            db_handle = database.SQLiteDBManager(app_settings.get_db_path())

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
        tag_name = "Data"
        for date in self.dates:
            dt = datetime.strptime(date, "%d-%m-%Y")
            self._calendar.calevent_create(dt, "Has Data", tag_name)

        self._calendar.tag_config(tag_name, background="#19a84c", foreground="white")

    def update_on_resize(self, event):
        self.configure_size()


class MenuTk(tk.Menu):
    def __init__(self, parent: App, **kwargs):
        super().__init__(parent, **kwargs)

        # create a menu
        file_menu = tk.Menu(self)

        # add a menu item to the menu
        file_menu.add_command(label="Exit", command=lambda: print("Exit"))

        # add the File menu to the menubar
        self.add_cascade(label="File", menu=file_menu)


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

        # Buttons in file
        file_dropdown = CustomDropdownMenu(master=parent, widget=file_button)
        file_dropdown.add_option("Save Figure", command=self.save_fig)
        file_dropdown.add_option("Save Single Graph", command=self.save_single_graph)
        file_dropdown.add_separator()
        # Choose database submenu
        sub_menu = file_dropdown.add_submenu("Choose Database")
        sub_menu.add_option(option="Default database")
        sub_menu.add_option(option="Choose database path")

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
        help_dropdown.add_option(option="something", command=lambda: print("something"))

    def open_settings(self):
        settings_popup = ctk.CTkToplevel(self)
        settings_popup.geometry("250x300")
        settings_popup.minsize(400, 300)
        # settings_popup.maxsize(250, 300)
        settings_popup.title("Settings")
        settings_popup.grab_set()

        innder_width = 125

        pady = 8
        padx_outer = 8
        padx_inner = (padx_outer + 10, 5)

        # Settings label
        label = ctk.CTkLabel(
            settings_popup,
            text="Settings",
            anchor="w",
            padx=5,
            pady=10,
            bg_color=constants.LIGHT_GREY,
        )
        label.cget("font").configure(size=20, weight="bold")
        label.pack(side=ctk.TOP, anchor="w", fill=ctk.BOTH, padx=padx_outer, pady=pady)


        # Database frame
        db_frame = ctk.CTkFrame(settings_popup, corner_radius=0)
        db_frame.pack(
            side=ctk.TOP, anchor="w", fill=ctk.BOTH, padx=padx_outer, pady=pady
        )
        # Database label
        db_label = ctk.CTkLabel(db_frame, text="Database", anchor="w")
        db_label.cget("font").configure(size=15, weight="bold")
        db_label.pack(side=ctk.TOP, anchor="sw", padx=8, pady=0)
        # Path label
        path_label = ctk.CTkLabel(
            db_frame, text="Database path:", anchor="w", height=0, width=innder_width
        )
        path_label.cget("font").configure(size=12)
        path_label.pack(
            side=ctk.LEFT, anchor="sw", padx=padx_inner, pady=(0, padx_outer)
        )
        # Path button
        path_button = ctk.CTkButton(
            db_frame,
            text=app_settings.get_db_path(),
            font=path_label.cget("font"),
            fg_color=constants.DARK_GREY_SETTINGS_BUTTON,
            border_color="black",
            border_width=1,
            height=0,
            anchor="w",
            command=self.select_db
        )
        path_button.pack(
            side=ctk.LEFT,
            anchor="sw",
            padx=padx_outer,
            pady=(0, padx_outer),
            fill=ctk.X,
            expand=True,
        )

        # Graphs Frame
        graphs_frame = ctk.CTkFrame(settings_popup, corner_radius=0)
        graphs_frame.pack(
            side=ctk.TOP, anchor="w", fill=ctk.BOTH, padx=padx_outer, pady=pady
        )
        # Database label
        graphs_label = ctk.CTkLabel(graphs_frame, text="Graphs", anchor="w")
        graphs_label.cget("font").configure(size=15, weight="bold")
        graphs_label.pack(side=ctk.TOP, anchor="sw", padx=8, pady=0)
        # y-axis limits label
        y_axis_label = ctk.CTkLabel(
            graphs_frame, text="y-axis limits:", anchor="w", height=0, width=innder_width
        )
        y_axis_label.cget("font").configure(size=12)
        y_axis_label.pack(
            side=ctk.LEFT, anchor="sw", padx=padx_inner, pady=(0, padx_outer)
        )
        # y-axis limits button
        y_axis_button = ctk.CTkButton(
            graphs_frame,
            text=app_settings.ylim,
            font=path_label.cget("font"),
            fg_color=constants.DARK_GREY_SETTINGS_BUTTON,
            border_color="black",
            border_width=1,
            height=0,
            anchor="w",
            command=self.select_ylim
        )
        y_axis_button.pack(
            side=ctk.LEFT,
            anchor="sw",
            padx=padx_outer,
            pady=(0, padx_outer),
            fill=ctk.X,
            expand=True,
        )

    def select_db(self):
        print("Select db")
    
    def select_ylim(self):
        print("Select ylim")

    def save_single_graph(self):
        drawn_graphs = self.parent.graph_page.get_drawn_graphs()
        if drawn_graphs:
            SaveSinglePopup(self.parent, drawn_graphs)
        else:
            messagebox.showerror(
                "Error",
                "No graphs have been drawn yet. Draw a graph before attempting to save.",
            )

    def save_fig(self):
        print("Save fig")
        drawn_graphs = self.parent.graph_page.get_drawn_graphs()
        if drawn_graphs:

            file_path = self.parent.open_file_dialog(title="Save Figure")
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


class SaveSinglePopup(ctk.CTkToplevel):
    def __init__(self, parent: App, drawn_graphs: list[int], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.chosen_graph = None

        self.geometry("250x300")
        self.minsize(250, 300)
        self.maxsize(250, 300)
        self.title("Select graph")
        self.grab_set()

        # Open Image
        img_square = Image.open("src\images\square1234.png")
        img_square_ctk = ctk.CTkImage(
            light_image=img_square, dark_image=img_square, size=(150, 150)
        )
        # Add Image
        img_square_label = ctk.CTkLabel(self, text="", image=img_square_ctk)
        img_square_label.pack(side=ctk.TOP)

        # Dropdown and info Frame
        drop_info_frame = ctk.CTkFrame(
            self, bg_color="transparent", fg_color="transparent"
        )
        drop_info_frame.pack(side=ctk.TOP)

        # Choose graph Dropdown and Label
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

        # Info Image
        info_img = Image.open("src\images\information-button.png")
        info_img_ctk = ctk.CTkImage(
            light_image=info_img, dark_image=info_img, size=(15, 15)
        )

        # Info button
        info_button = ctk.CTkButton(
            drop_info_frame,
            image=info_img_ctk,
            width=1,
            height=1,
            corner_radius=50,
            hover_color="#afafaf",
            text="",
            fg_color="white",
            bg_color="transparent",
            command=self._info_event,
            round_height_to_even_numbers=False,
            round_width_to_even_numbers=False,
        )
        info_button.pack(side=ctk.LEFT, anchor="se")

        # Frame for Cancel and OK buttons
        buttons_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        buttons_frame.pack(side=ctk.BOTTOM, fill=ctk.X)
        buttons_frame.pack_propagate(False)
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            width=80,
            height=5,
            corner_radius=0,
            border_width=0.5,
            text="Cancel",
            command=self._cancel_event,
        )
        cancel_button.pack(side=ctk.RIGHT, padx=(10, 15))
        # OK button
        self.ok_button = ctk.CTkButton(
            buttons_frame,
            width=80,
            height=5,
            corner_radius=0,
            border_width=0.5,
            text="OK",
            state=ctk.DISABLED,
            command=self._ok_event,
        )
        self.ok_button.pack(side=ctk.RIGHT)

    def _choose_graph_event(self, value):
        print("Choose graph event:", value)
        self.chosen_graph = int(value) - 1
        self.ok_button.configure(state=ctk.NORMAL)

    def _cancel_event(self):
        self.destroy()

    def _ok_event(self):
        fig = self.parent.graph_page.get_fig(self.chosen_graph)
        file_path = self.parent.open_file_dialog(title="Save Graph")
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


def main():
    App("VisitorFlowTracker")


if __name__ == "__main__":
    main()
