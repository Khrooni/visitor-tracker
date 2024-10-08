import datetime
import ntpath
import os
from pathlib import Path
import threading
import time
import webbrowser

from tkinter import filedialog, messagebox
from typing import Any

import customtkinter as ctk
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
import numpy as np
from PIL import Image
import requests

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

import constants
import database
import retrieve_data.retrieve_data as rd
from settings.settings import Settings
import utils
from utils import DropdownAndLabel, InfoButton, MyPopup, CustomDateEntry

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

        # Create menubar
        self.menu = MyMenuBar(self)

        # Create Frame for pages (otherwise pages overlap menubar)
        container = ctk.CTkFrame(self)
        container.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # Create pages
        self.pages: dict[str, GraphPage | DatabasePage] = {}
        self.pages["graph"] = GraphPage(container)
        self.pages["database"] = DatabasePage(container)

        # Place pages in Frame
        self.pages.get("graph").place(x=0, y=0, relwidth=1, relheight=1)
        self.pages.get("database").place(x=0, y=0, relwidth=1, relheight=1)

        # Bring graph page on top
        self.lift_page("graph")

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

    def lift_page(self, page_name: str):
        """
        Lift the page responding to the given page_name.

        :param page_name: dictionary key for the pages dictionary
        :type page_name: str
        :raises ValueError: If dictionary didn't have a key matching the page_name.
        """
        page = self.pages.get(page_name)

        if not page:
            raise ValueError("Invalid page_name. Given page_name not in the dictionary")

        page.lift()


class GraphPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)

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

        for color in constants.GRAPH_COLORS:
            self.all_graphs.append(Graph(master=self.main_frame, element_color=color))

        # Sidebar
        self.sidebar = GraphSidebar(self)
        self.sidebar.pack(fill=ctk.Y, side=ctk.LEFT)
        self.main_frame.pack(
            fill=ctk.BOTH, expand=True, side=ctk.LEFT, padx=10, pady=10
        )

    def set_ylims(
        self, lower_ylim: float | None, upper_ylim: float | None, graph_amount: int
    ):
        """Set the y-axis limits for a specified number of graphs.

        :param float | None lower_ylim: The lower limit for the y-axis.
        :param float | None upper_ylim: The upper limit for the y-axis.
        :param int graph_amount: The number of graphs to update.
        """
        for graph_num in range(graph_amount):
            self.all_graphs[graph_num].ax.set_ylim(lower_ylim, upper_ylim)

    def redraw_graphs(self, graph_amount: int):
        """Redraw the specified number of graphs on their canvases.

        :param int graph_amount: The number of graphs to redraw.
        """
        for graph_num in range(graph_amount):
            self.all_graphs[graph_num].canvas.draw()
            self.all_graphs[graph_num].is_drawn = True

    def draw_all_graphs(self):
        """Rearrange graphs and draw all graphs on screen."""
        if self.graph_amount != self.active_graph_amount:
            self._arrange_graphs()

        for graph_num in range(self.graph_amount):
            self.all_graphs[graph_num].draw_graph(self.graph_amount)

        if app_settings.ymode == "Auto Limit":
            self.set_ylims(*self._get_ylim(), self.graph_amount)
            self.redraw_graphs(self.graph_amount)

        self.active_graph_amount = self.graph_amount

    def draw_single_graph(self, graph_num: int):
        """Draw a specific graph based on the provided graph number.

        Note: redraws other graphs if ymode is set to "Auto Limit" and the limit
        needs be changed according to auto limit logic.

        :param graph_num: The index of the graph to be drawn. Must be less than `graph_amount`.
        :type graph_num: int
        """
        if self.graph_amount != self.active_graph_amount:
            self._arrange_graphs()

        if self.graph_amount >= (graph_num + 1):
            self.all_graphs[graph_num].draw_graph(self.graph_amount)

        if app_settings.ymode == "Auto Limit":
            self.set_ylims(*self._get_ylim(), self.graph_amount)
            self.redraw_graphs(self.graph_amount)

        self.active_graph_amount = self.graph_amount

    def _get_auto_ylim(self) -> tuple[float, float]:
        """Calculate auto ylim from all graphs on screen.

        :return: (lower_ylim, upper_ylim)
        :rtype: tuple[float, float]
        """
        upper_ylim = None
        margin = 0.05

        for graph_num in range(self.graph_amount):
            if self.all_graphs[graph_num].y_values:
                temp_upper = max(self.all_graphs[graph_num].y_values)

                if upper_ylim:
                    if temp_upper and temp_upper > upper_ylim:
                        upper_ylim = temp_upper
                else:
                    upper_ylim = temp_upper

        if upper_ylim:
            upper_ylim = upper_ylim * (margin + 1)

        return (app_settings.ylim[0], upper_ylim)

    def _get_ylim(self) -> tuple[float, float]:
        """
        :return: ymode appropriate y-limit. (lower_ylim, upper_ylim)
        :rtype: tuple[float, float]
        """
        if app_settings.ymode == "Auto Limit":
            ylim = self._get_auto_ylim()
        elif app_settings.ymode == "Select Limit":
            ylim = app_settings.ylim
        elif app_settings.ymode == "No Limit":
            ylim = app_settings.get_default_ylim()

        return ylim

    def _arrange_graphs(self):
        """Rearrange graphs depending on `graph_amount`."""
        if self.label:
            self.label.destroy()
            self.label = None

        if self.graph_amount == 1:
            for graph in self.all_graphs:
                graph.grid_forget()

            self.all_graphs[0].pack(
                side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=10
            )
            for graph in self.all_graphs[1:]:
                graph.pack_forget()

        elif self.graph_amount == 2:
            for graph in self.all_graphs:
                graph.grid_forget()

            self.all_graphs[0].pack(
                side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=(10, 0)
            )
            self.all_graphs[1].pack(
                side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=10, pady=(0, 10)
            )
            for graph in self.all_graphs[2:]:
                graph.pack_forget()

        elif self.graph_amount == 4:
            for graph in self.all_graphs:
                graph.pack_forget()

            self.main_frame.columnconfigure((0, 1), weight=1)
            self.main_frame.rowconfigure((0, 1), weight=1)
            self.all_graphs[0].grid(
                sticky="nsew", row=0, column=0, padx=(10, 0), pady=(10, 0)
            )
            self.all_graphs[1].grid(
                sticky="nsew", row=0, column=1, padx=(0, 10), pady=(10, 0)
            )
            self.all_graphs[2].grid(
                sticky="nsew", row=1, column=0, padx=(10, 0), pady=(0, 10)
            )
            self.all_graphs[3].grid(
                sticky="nsew", row=1, column=1, padx=(0, 10), pady=(0, 10)
            )

    def get_drawn_graphs(self) -> list[int]:
        """Return list of indexes of graphs that have been drawn."""
        drawn_graphs: list[int] = []
        for i, graph in enumerate(self.all_graphs):
            if graph.is_drawn:
                drawn_graphs.append(i + 1)

        return drawn_graphs

    def get_fig(self, graph_num: int) -> Figure:
        """Retrieve the Figure object for a specified graph.

        :param graph_num: graph's index
        :type graph_num: int
        """
        return self.all_graphs[graph_num].fig


class DatabasePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.main_frame = DatabaseMainFrame(self)
        self.main_frame.pack(
            fill=ctk.BOTH, expand=True, side=ctk.RIGHT, padx=10, pady=10
        )

        self.sidebar = DatabaseSidebar(self, self.main_frame)
        self.sidebar.pack(fill=ctk.Y, side=ctk.LEFT)


class GraphSidebar(ctk.CTkFrame):
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

    def update_all(self):
        """
        Updates calendar and locations of every graph tab. Retrieves the necessary data
        from the database for the update.

        Call whenever updating calendar/locations is necessary. (e.g. database is changed to
        a different database or the database gets new locations)
        """
        locations, location_name, unique_dates = self._get_locations_dates()
        for graph_tab in self.graph_tabs:
            graph_tab.update_cal(unique_dates)
            graph_tab.update_loc(locations, location_name)

    def _get_locations_dates(self) -> tuple[dict[str, int], str, list[str]]:
        """Get all locations from the database. The first location from the database
        is used as the selected location (location_name). The selected location is used to get
        unique dates that have visitor data.

        :return: tuple[all_locations, location_name, unique_dates]
        :rtype: tuple[dict[str, int], str, list[str]]
        """
        locations = constants.NO_LOCATIONS
        default_location = constants.DEFAULT_LOCATION
        unique_dates = []

        with database.SQLiteDBManager(app_settings.db_path) as db_handle:
            locations_dict = db_handle.get_locations_dict()

            if locations_dict:
                locations = locations_dict
                default_location = next(iter(locations_dict.keys()))

            unique_dates = db_handle.get_unique_dates(locations.get(default_location))

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
        """Enable 'Plot Graph'-button in all GraphTabs in graph amount"""
        for i in range(graph_amount - 1):
            # i + 1 (first tab button is never disabled)
            self.graph_tabs[i + 1].plot_graph_button.configure(state=ctk.NORMAL)


class Graph(ctk.CTkFrame):
    def __init__(
        self, *args, master=None, element_color="red", padx=0, pady=0, **kwargs
    ):
        super().__init__(master, *args, **kwargs)
        self.pack_propagate(False)
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
        self.x_label: str = "x label"
        self.y_label: str = "y label"
        self.x_values: list = []
        self.y_values: list = []
        self.element_color: str = element_color
        self.facecolor: str = constants.LIGHT_GREY
        self.edge_color: str = "grey"
        self.axis_colors: str = "white"

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

    def draw_graph(self, graph_amount: int = 1, force_draw=False):
        """Retrieve graph values from the database, set axes values, plot graph
        and finally if app_settings.ymode isn't "Auto Limit" draw the graph on
        tkinter canvas.

        :param graph_amount: amount of graphs that will be drawn, defaults to 1.
            If graph amount is 4, only every other value is used for bar graph
        :type graph_amount: int, optional
        :param force_draw: force drawing the graph on tkinter canvas even if
            app_settings.ymode is "Auto Limit", defaults to False
        :type force_draw: bool, optional
        """
        self._update_graph_values()
        self._set_axes(graph_amount)

        # Plot graph
        if self.graph_type.lower() == "bar graph":
            width = np.diff(self.x_values).min() * 0.80

            self.ax.bar(
                self.x_values,
                self.y_values,
                color=self.element_color,
                align="center",
                width=width,
            )
            # self.ax.xaxis_date()
        elif self.graph_type.lower() == "line graph":
            self.ax.plot(
                self.x_values,
                self.y_values,
                color=self.element_color,
                linewidth=4,
            )

        # Set ylimits
        if app_settings.ymode == "Select Limit":
            self.ax.set_ylim(*app_settings.ylim)
        elif app_settings.ymode == "No Limit":
            self.ax.set_ylim(app_settings.ylim[0], None)
        elif app_settings.ymode == "Auto Limit":
            # Force drawing graphs even if auto limit ymode is set
            if force_draw:
                self.canvas.draw()
                self.is_drawn = True

            # The Graphs need the ylims of other graphs before drawing,
            # so the graphs will be drawn with redraw_graphs() later.
            return  # Stop graphs from being drawn twice.

        # Draw graph on tkinter canvas
        self.canvas.draw()
        self.is_drawn = True

    def _update_graph_values(self):
        """Update the graph values based on the current time mode and location.

        Retrieves data from the database and sets the title, x-label, y-label,
        x-values, and y-values for the graph.
        """
        with database.SQLiteDBManager(app_settings.db_path) as db_handle:
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
            elif self.time_mode == "Daily Average":
                visitors = db_handle.get_average_visitors(
                    self.locations.get(self.location_name),
                    constants.WEEKDAYS.get(self.weekday),
                )
                timestamps = utils.day_epochs()
            elif self.time_mode == "Time Range":
                time_r_interval = 60 * 60
                search_start, search_end = self._get_search_range()
                visitors = db_handle.get_data_by_mode(
                    self.locations.get(self.location_name),
                    search_start,
                    search_end,
                    constants.GRAPH_MODES.get(self.graph_mode),
                    time_r_interval,
                )
                timestamps = database.helpers.calculate_timestamps(
                    search_start, search_end, time_r_interval
                )

        self._set_title_and_labels(timestamps)
        self.x_values = utils.epochs_to_format(timestamps, "datetime")
        self.y_values = utils.nones_to_zeros(visitors)

    def _get_search_range(self) -> tuple[int, int]:
        search_start: int
        search_end: int

        if self.time_mode == "Calendar":
            search_start = utils.formatted_date_to_epoch(f"{self.graph_date} 00:00:00")
            search_end = utils.next_time(search_start, days=1)  # +1 day
        elif self.time_mode == "Time Range":
            search_end_dt = datetime.datetime.now()
            search_end = utils.datetime_to_epoch(search_end_dt)

            time_dif_td = utils.get_time_delta(self.time_range, "negative")
            if time_dif_td:
                search_start_dt = search_end_dt + time_dif_td
                search_start = utils.datetime_to_epoch(search_start_dt)
            else:
                search_start = self._get_all_search_start()

        # print("\nSearch start:", utils.get_formatted_finnish_time(search_start))
        # print("Search end:  ", utils.get_formatted_finnish_time(search_end))

        return search_start, search_end

    def get_first(self) -> datetime.datetime | None:
        """Get first epoch of chosen location from the database.

        :return: first epoch of chosen location as datetime Object
        :rtype: datetime.datetime | None
        """
        with database.SQLiteDBManager(app_settings.db_path) as db_handle:
            search_start = db_handle.get_first_time(
                self.locations.get(self.location_name)
            )

        if search_start:
            search_start = utils.get_localized_datetime(search_start)

        return search_start

    def _get_all_search_start(self) -> int | None:
        search_start_dt = self.get_first()

        if not search_start_dt:
            return search_start_dt

        search_start_dt = utils.top_of_the_hour(search_start_dt)

        return utils.datetime_to_epoch(search_start_dt)

    def _set_axes(self, graph_amount: int):
        """Clears previous axis values and then sets all axis values to the new ones.

        :param graph_amount: amount of graphs that will be drawn. Affects the
            interval of data to reduce graph label overlap
        :type graph_amount: int
        """
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

        if self.time_mode == "Time Range":

            locator = mdates.AutoDateLocator(tz=constants.DEFAULT_TIMEZONE)
            formatter = mdates.ConciseDateFormatter(
                locator, tz=constants.DEFAULT_TIMEZONE
            )

            # '%#d' only works with windows. '%-d' on linux
            formatter.formats = [
                "%y",  # ticks are mostly years
                "%b",  # ticks are mostly months
                "%a, %#d.",  # ticks are mostly days
                "%H:%M",  # hrs
                "%H:%M",  # min
                "%S.%f",  # secs
            ]

            formatter.zero_formats = [
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

    def _set_title_and_labels(self, timestamps: list[int]):
        """Set the title and axis labels for the graph based on the current
        time mode and timestamps.

        This method updates the graph's title, x-axis label, and y-axis label
        according to the current time mode.

        :param list[int] timestamps: A list of epoch timestamps.
        """
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
        elif self.time_mode == "Daily Average":
            self.title = f"{self.location_name}, {self.weekday}"
            self.x_label = "Hour"
            self.y_label = self.graph_mode
        elif self.time_mode == "Time Range":
            self.title = f"{self.location_name}"
            self.x_label = ""
            self.y_label = self.graph_mode

    def get_limits(
        self, datetimes: list[datetime.datetime]
    ) -> tuple[datetime.datetime, datetime.datetime]:
        """
        Calculate and return the lower and upper limits based on a list of datetime objects.

        The function computes the difference between the first two datetime objects in the list.
        It then uses this difference to calculate a lower limit by subtracting 0.75% of
        the difference from the first datetime, and an upper limit by adding 0.75% of
        the difference to the last datetime.

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
        for i, _ in enumerate(values):
            if (i % 2) == 1:
                values[i] = ""

        # for i in range(len(values)):
        #     if (i % 2) == 1:
        #         values[i] = ""

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
            maxdate=datetime.date.today(),
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
            "Day",
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
        mindate = self.graph.get_first()
        maxdate = datetime.date.today()
        if not mindate:
            mindate = maxdate
        self.cal.configure(mindate=mindate, maxdate=maxdate)
        self.cal.highlight_dates()

    def update_loc(self, locations: dict[str, int], location_name: str):
        """Update locations"""
        self.graph.locations = locations
        self.graph.location_name = location_name
        self.location_menu.set_menu_values(
            values=list(locations.keys()), default_value=location_name
        )

    def plot_single_graph_event(self):
        self.graph_page.draw_single_graph(self.graph_num)

    def open_calendar_event(self):
        self.cal.drop_down()

    def update_date(self, event):
        self.graph.graph_date = self.cal.get_date().strftime("%d-%m-%Y")

    def change_graph_type_event(self, value):
        self.graph.graph_type = value

    def change_graph_mode_event(self, value):
        self.graph.graph_mode = value

    def change_time_mode_event(self, value):
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
        elif value == "Daily Average":
            self.weekday_frame.lift()
            self.graph_mode_menu.set_menu_values(
                constants.WEEKDAY_TIME_RANGE_GRAPH_MODES, constants.DEFAULT_GRAPH_MODE
            )
            self.graph.graph_mode = constants.DEFAULT_GRAPH_MODE

            self.graph_type_menu.set_menu_values(
                constants.GRAPH_TYPES, constants.DEFAULT_GRAPH_TYPE
            )
            self.graph.graph_type = constants.DEFAULT_GRAPH_TYPE

        elif value == "Time Range":
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
        self.graph.weekday = value

    def change_time_range_event(self, value):
        self.graph.time_range = value

    def change_location_event(self, value):
        self.graph.location_name = value

        with database.SQLiteDBManager(app_settings.db_path) as db_handle:
            unique_dates = db_handle.get_unique_dates(
                self.graph.locations.get(self.graph.location_name)
            )
            self.update_cal(unique_dates)


class DatabaseMainFrame(ctk.CTkFrame):
    def __init__(self, parent: DatabasePage):
        super().__init__(parent)
        self.pack_propagate(False)
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


class DatabaseSidebar(ctk.CTkFrame):
    def __init__(
        self,
        parent: DatabasePage,
        main_frame: DatabaseMainFrame,
        width=constants.SIDEBAR_WIDTH,
    ):
        super().__init__(parent, width=width, corner_radius=0)
        self.pack_propagate(False)
        self.thread_id = 1  # Used for stopping data collection
        self.col_interval = constants.DEFAULT_COL_INTERVAL

        self.parent = parent
        self.main_frame = main_frame
        self.unique_dates = []

        with database.SQLiteDBManager(app_settings.db_path) as db_handle:
            self.unique_dates = db_handle.get_unique_dates(
                constants.RETRIEVAL_LOCATIONS.get(constants.DEFAULT_RETRIEVAL_LOCATION)
            )

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

        daemon_thread = threading.Thread(
            target=self._get_data_in_intervals,
            args=(constants.DATA_COL_INTERVALS.get(self.col_interval), self.thread_id),
        )
        daemon_thread.daemon = True
        daemon_thread.start()

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
            with database.SQLiteDBManager(app_settings.db_path) as db_handle:
                # Collect data until thread_id changes
                while thread_id == self.thread_id:
                    start_time = time.perf_counter()

                    data = rd.get_data()
                    location: rd.Location
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
        except requests.exceptions.ConnectionError as err:
            self.write_to_textbox(
                f"Data collection aborted. {type(err).__name__} occurred."
                + "\nInternet connection might have been lost.\n\n"
            )
            self.stop_collecting_data()  # Toggle data collection button off
        except Exception as err:
            self.write_to_textbox(
                f"Data collection aborted. {type(err).__name__} occurred."
                + "\nRestarting app might be necessary."
                + f"\nError info:\n{err}\n\n"
            )
            self.stop_collecting_data()  # Toggle data collection button off

    def _format_data(self, location_data: rd.Location):
        formatted_str = f"""
        \tLocation name: {location_data.location_name}
        \tTime: {utils.get_formatted_finnish_time(location_data.epoch_timestamp)}
        \tVisitor amount: {location_data.location_visitors}
        """
        return formatted_str


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
        help_button = self.add_cascade(
            "Help", postcommand=self.open_doc, text_color="white"
        )

        # Buttons in File
        file_dropdown = CustomDropdownMenu(master=parent, widget=file_button)
        # Save buttons
        file_dropdown.add_option("Save Figure", command=self.save_fig)
        file_dropdown.add_option("Save Single Graph", command=self.save_single_graph)
        file_dropdown.add_separator()
        # Import data / Create Backup buttons
        file_dropdown.add_option(option="Import Data", command=self.import_data)
        file_dropdown.add_option(option="Create Backup", command=self.create_backup)
        # file_dropdown.add_separator()
        # Change database button
        file_dropdown.add_option(option="Change Database", command=self.select_db)

        # Buttons in View
        view_dropdown = CustomDropdownMenu(master=parent, widget=view_button)
        view_dropdown.add_option(
            option="Graphs", command=lambda: parent.lift_page("graph")
        )
        view_dropdown.add_option(
            option="Database", command=lambda: parent.lift_page("database")
        )

    def open_doc(
        self,
        doc_url="https://github.com/Khrooni/visitor-tracker?tab=readme-ov-file#how-to-use---demo",
    ):
        """Open documentation"""
        webbrowser.open(doc_url, new=0, autoraise=True)

    def open_settings(self):
        SettingsPopup(self.parent, "Settings")

    def create_backup(self):
        backup_path = filedialog.asksaveasfilename(
            confirmoverwrite=True,
            defaultextension=constants.DB_DEFAULTEXTENSION,
            title="Save Backup",
            filetypes=constants.DB_FILETYPES,
        )

        if backup_path:
            if os.path.realpath(backup_path) != os.path.realpath(app_settings.db_path):
                with database.SQLiteDBManager(app_settings.db_path) as db_handle:
                    db_handle.create_backup(backup_path)
                    messagebox.showinfo("Info", "Backup created.")
            else:
                messagebox.showerror(
                    title="Error",
                    message="Choose a different name or a location for the backup.",
                )

    def import_data(self):
        import_path = filedialog.askopenfilename(
            defaultextension=constants.DB_DEFAULTEXTENSION,
            filetypes=constants.DB_FILETYPES,
            initialdir=constants.DB_INITIALDIR,
            title="Select database",
        )

        if import_path:
            if os.path.realpath(import_path) != os.path.realpath(app_settings.db_path):
                with database.SQLiteDBManager(import_path) as db_handle:
                    db_handle.import_data(app_settings.db_path)
                    self.parent.pages.get("graph").sidebar.update_all()
                    messagebox.showinfo("Info", "Data imported")
            else:
                messagebox.showerror(
                    title="Error",
                    message="Unable to import data from the same database. "
                    + "Choose a different database to import from.",
                )

    def select_db(self):
        new_filepath = filedialog.askopenfilename(
            defaultextension=constants.DB_DEFAULTEXTENSION,
            filetypes=constants.DB_FILETYPES,
            initialdir=constants.DB_INITIALDIR,
            title="Select database",
        )

        if new_filepath:
            new_filepath = os.path.relpath(new_filepath)
            old_filepath = os.path.relpath(app_settings.db_path)

            if messagebox.askokcancel(
                "Change database?",
                f"Do you wish to change currently used database ({old_filepath}) to "
                + f"selected database ({new_filepath})?",
            ):
                app_settings.db_path = new_filepath
                app_settings.update_all()
                self.parent.pages.get("graph").sidebar.update_all()

    def save_single_graph(self):
        drawn_graphs = self.parent.pages.get("graph").get_drawn_graphs()
        if drawn_graphs:
            SaveSinglePopup(self.parent, "Select graph", drawn_graphs)
        else:
            messagebox.showerror(
                "Error",
                "No graphs have been drawn yet. Draw a graph before attempting to save.",
            )

    def save_fig(self):
        drawn_graphs = self.parent.pages.get("graph").get_drawn_graphs()
        if drawn_graphs:

            file_path = filedialog.asksaveasfilename(
                confirmoverwrite=True,
                defaultextension=constants.IMG_DEFAULTEXTENSION,
                title="Save Figure",
                filetypes=constants.IMG_FILETYPES,
            )

            if file_path:
                images = []

                for i in range(self.parent.pages.get("graph").active_graph_amount):
                    canvas = self.parent.pages.get("graph").all_graphs[i].fig.canvas
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
        """Returns the size of the new image.

        If images has only 1 image the new image size is the size of the original image

        If images has 2 images
            the new width is image0 + image1 width
            the new height is the max(height) of the two images

        if images has 4 images
            the new width is max(image0, image2) + max(image1, image3) width
            the new height is max(image0, image1) + max(image2, image3) height

        :return: size of the new image. (width, height)
        :rtype: tuple[int, int]
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

        Valid resource names: background, bd, bg, borderwidth, class, colormap, container, cursor,
        height, highlightbackground, highlightcolor, highlightthickness, relief, takefocus, visual,
        width.
        """
        super().__init__(master=master, corner_radius=corner_radius, **kwargs)

    def add_title(
        self, text: str, font_size=15, font_weight="bold", padx=8, pady=8
    ) -> ctk.CTkLabel:
        label = ctk.CTkLabel(self, text=text, anchor="w", height=0)
        label.cget("font").configure(size=font_size, weight=font_weight)
        label.pack(side=ctk.TOP, anchor="w", padx=padx, pady=pady)

        return label

    def add_setting_button(
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
        label = ctk.CTkLabel(
            setting_frame, text=label_text, anchor="w", height=0, width=label_width
        )
        label.cget("font").configure(size=font_size)
        label.pack(side=ctk.LEFT, anchor="w", padx=(padx_inner, 0), pady=(0, pady))
        # Button
        button = ctk.CTkButton(
            setting_frame,
            text=button_text,
            command=command,
            font=label.cget("font"),
            fg_color=constants.DARK_GREY_SETTINGS_BUTTON,
            border_color="black",
            border_width=1,
            height=0,
            width=0,
            anchor="w",
            border_spacing=4,
            **kwargs,
        )
        # button._text_label.configure(wraplength=500)
        button.pack(
            side=ctk.LEFT,
            anchor="w",
            padx=(0, padx),
            pady=(0, pady),
            fill=fill,
            expand=True,
        )

        return setting_frame

    def add_settings_dropdown(
        self,
        label_text: str,
        values: list,
        default_value: str,
        command,
        font_size=12,
        label_width=125,
        pady=8,
        padx=8,
        padx_inner=20,
        fill="x",
        **kwargs,
    ):
        settings_dropdown = SettingsDropdown(
            self,
            label_text,
            values,
            default_value,
            command,
            font_size,
            label_width,
            pady,
            padx,
            padx_inner,
            fill,
            **kwargs,
        )
        settings_dropdown.pack(side=ctk.TOP, anchor="w", fill=ctk.X)

        return settings_dropdown


class SettingsDropdown(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        label_text: str,
        values: list,
        default_value: str,
        command,
        font_size=12,
        label_width=125,
        pady=8,
        padx=8,
        padx_inner=20,
        fill="x",
        **kwargs,
    ):
        # Frame
        super().__init__(parent, fg_color="transparent")

        # Label
        self.label = ctk.CTkLabel(
            self, text=label_text, anchor="w", height=0, width=label_width
        )
        self.label.cget("font").configure(size=font_size)
        self.label.pack(side=ctk.LEFT, anchor="w", padx=(padx_inner, 0), pady=(0, pady))
        # Dropdown
        border_frame = ctk.CTkFrame(
            self,
            width=0,
            height=0,
            corner_radius=0,
            border_color="black",
            border_width=1,
        )
        border_frame.pack(
            side=ctk.LEFT,
            anchor="w",
            padx=(0, padx),
            pady=(0, pady),
            fill=fill,
            expand=True,
        )
        self.variable: ctk.StringVar = ctk.StringVar(value=default_value)
        self.dropdown = ctk.CTkOptionMenu(
            border_frame,
            values=values,
            command=command,
            variable=self.variable,
            font=self.label.cget("font"),
            dropdown_font=self.label.cget("font"),
            fg_color=constants.DARK_GREY_SETTINGS_BUTTON,
            button_color=constants.DARK_GREY_SETTINGS_BUTTON,
            button_hover_color=constants.DARK_BLUE_HOVER_COLOR,
            corner_radius=0,
            **kwargs,
        )
        self.dropdown.pack(
            side=ctk.LEFT,
            anchor="w",
            padx=1,
            pady=1,
            fill="both",
            expand=True,
        )


class SaveSinglePopup(MyPopup):
    def __init__(
        self, parent: App, title: str, drawn_graphs: list[int], *args, **kwargs
    ):
        super().__init__(parent, title, *args, **kwargs)
        self.parent = parent
        self.chosen_graph = None

        # Open square image
        img_square = Image.open(Path(__file__).parent / "images/square1234.png")
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
            parent=drop_info_frame,
            popup_title="Info",
            popup_info_text="Only graphs that have been drawn will be available for saving."
            + "\n\nThis includes graphs that may not currently be visible on the screen "
            + "but have been previously drawn.",
        )
        info_button.pack(side=ctk.LEFT, anchor="se")

        # Pack bottom frame
        self.pack_bottom_frame()
        # Cancel button
        self.add_cancel_button()
        # OK button
        self.ok_button: ctk.CTkButton = self.add_bottom_button(
            text="OK", command=self._ok_event, state=ctk.DISABLED
        )

    def _choose_graph_event(self, value):
        self.chosen_graph = int(value) - 1
        self.ok_button.configure(state=ctk.NORMAL)

    def _ok_event(self):
        fig = self.parent.pages.get("graph").get_fig(self.chosen_graph)
        file_path = filedialog.asksaveasfilename(
            confirmoverwrite=True,
            defaultextension=constants.IMG_DEFAULTEXTENSION,
            title="Save Graph",
            filetypes=constants.IMG_FILETYPES,
        )

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
            geometry="400x400",
            minsize=(400, 400),
            maxsize=(600, 400),
            *args,
            **kwargs,
        )
        self.pack_propagate(True)
        self.parent = parent
        self.filepath = app_settings.db_path
        self.ylim: tuple[float, float] = app_settings.ylim
        self.ymode = app_settings.ymode

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
        self.db_path_frame = db_frame.add_setting_button(
            "Database file:", tail, self.select_db
        )
        db_frame.add_setting_button(
            "", "Use Default Database", self.default_db, fill=None
        )

        # Graphs
        graph_frame = SettingsFrame(self)
        graph_frame.pack(
            side=ctk.TOP, anchor="w", fill=ctk.BOTH, padx=pad, pady=(pad, 2 * pad)
        )
        graph_frame.add_title("Graphs")
        self.settings_dropdown = graph_frame.add_settings_dropdown(
            "Y-axis upper limit:",
            constants.YMODES,
            default_value=self.get_ylim_text(),
            command=self._select_ylim_event,
        )

        # Bottom frame
        self.pack_bottom_frame()
        self.add_cancel_button()
        self.add_bottom_button("OK", self._ok_event)
        self.add_bottom_button("Reset", self._reset_event)

    def _select_ylim_event(self, value):
        if value == "Auto Limit":
            self.ymode = value
        elif value == "No Limit":
            self.ymode = value
            self.ylim = (self.ylim[0], None)
        elif value == "Select Limit":
            self.settings_dropdown.variable.set(self.get_ylim_text())
            dialog = ctk.CTkInputDialog(
                text="Type in a number:", title="Choose upper limit"
            )
            selected_value = dialog.get_input()
            self.grab_set()
            try:
                if selected_value:
                    selected_value = float(selected_value)
                    self.settings_dropdown.variable.set(selected_value)
                    self.ymode = value
                    self.ylim = (self.ylim[0], selected_value)
            except ValueError:
                messagebox.showerror(
                    "Error", "No changes made. Please enter a valid number."
                )
                self.grab_set()

    def _ok_event(self):
        if self.filepath and self.filepath != os.path.relpath(app_settings.db_path):
            app_settings.db_path = self.filepath
            self.parent.pages.get("graph").sidebar.update_all()

        if self.ylim and (
            self.ylim != app_settings.ylim or self.ymode != app_settings.ymode
        ):
            app_settings.ylim = self.ylim
            app_settings.ymode = self.ymode

        app_settings.update_all()
        self.destroy()

    def _reset_event(self):
        if messagebox.askokcancel(
            "Reset settings?", "Do you really want to reset settings to default values?"
        ):
            self.ylim = app_settings.get_default_ylim()
            self.ymode = app_settings.get_default_ymode()
            self.filepath = app_settings.get_default_db_path()

            self.settings_dropdown.variable.set(self.get_ylim_text())

            _, tail = ntpath.split(self.filepath)
            self.db_path_frame.winfo_children()[1].configure(text=tail)

    def select_db(self):
        filepath = filedialog.askopenfilename(
            defaultextension=constants.DB_DEFAULTEXTENSION,
            filetypes=constants.DB_FILETYPES,
            initialdir=constants.DB_INITIALDIR,
            title="Select database",
        )

        if filepath:
            filepath = os.path.relpath(filepath)
            self.filepath = filepath

            _, tail = ntpath.split(filepath)

            self.db_path_frame.winfo_children()[1].configure(text=tail)

    def default_db(self):
        default_filepath = os.path.relpath(app_settings.get_default_db_path())

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

    def get_ylim_text(self) -> int | float | str:
        "Get text for button"
        if self.ymode == "Select Limit":
            return self.ylim[1]

        return self.ymode


def main():
    App("VisitorTracker")


if __name__ == "__main__":
    main()
