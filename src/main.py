import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry, Calendar

import customtkinter as ctk
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu

from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import datetime
from typing import List, Callable, Any
import time
import threading

import database
import database.helpers
import retrieve_data
from retrieve_data import Location
import utils


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
    "Average Visitors": "all_time_avg",
    "Highest Visitors": "max",
    "Lowest Visitors": "min",
}
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


class App(ctk.CTk):
    def __init__(self, title, size=WINDOW_START_SIZE, min_size=WINDOW_MIN_SIZE):
        super().__init__()
        self.title(title)
        positions = self._calculte_positions(size)
        self.geometry(f"{int(size[0])}x{size[1]}+{positions[0]}+{positions[1]}")
        self.minsize(min_size[0], min_size[1])

        ctk.set_appearance_mode("Dark")

        self.menu = Menu(self)

        self.graph_page = GraphPage(self)
        self.database_page = DatabasePage(self)

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)

        self.graph_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.database_page.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

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


class GraphPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.pack(side="top", fill="both", expand="true")

        self.all_graphs: List[Graph] = []
        self.graph_amount = DEFAULT_GRAPH_AMOUNT

        # Used to decide if graphs need to be rearranged
        self.active_graph_amount = None

        # main frame
        self.main_frame = ctk.CTkFrame(self)

        # Add temporary "No graphs plotted"-label
        self.label = ctk.CTkLabel(
            self.main_frame,
            font=ctk.CTkFont(size=50, weight="bold"),
            text="No graphs plotted",
            width=TEXTBOX_WIDTH,
            height=50,
            fg_color="transparent",
            bg_color="transparent",
            corner_radius=10,
        )
        self.label.place(relx=0.5, rely=0.45, anchor=ctk.CENTER)
        # self.label.destroy()

        self.graph1 = Graph(self.main_frame, element_color="red", padx=0, pady=0)
        self.graph2 = Graph(self.main_frame, element_color="green", padx=0, pady=0)
        self.graph3 = Graph(self.main_frame, element_color="blue", padx=0, pady=0)
        self.graph4 = Graph(self.main_frame, element_color="orange", padx=0, pady=0)

        self.all_graphs.append(self.graph1)
        self.all_graphs.append(self.graph2)
        self.all_graphs.append(self.graph3)
        self.all_graphs.append(self.graph4)

        # Sidebar
        self.sidebar = SideBarGraph(self)
        self.sidebar.pack(fill="y", side="left")
        self.main_frame.pack(fill="both", expand=True, side="left", padx=10, pady=10)

    def draw_all_graphs(self):
        if self.graph_amount != self.active_graph_amount:
            self._arrange_graphs()

        for graph_num in range(self.graph_amount):
            self.all_graphs[graph_num].draw_graph()

        self.active_graph_amount = self.graph_amount

    def draw_single_graph(self, graph_num: int):
        if self.graph_amount != self.active_graph_amount:
            self._arrange_graphs()

        self.all_graphs[graph_num].draw_graph()

        self.active_graph_amount = self.graph_amount

    def _arrange_graphs(self):
        self.label.destroy()

        if self.graph_amount == 1:
            self.graph1.grid_forget()
            self.graph2.grid_forget()
            self.graph3.grid_forget()
            self.graph4.grid_forget()

            self.graph1.pack(side=ctk.TOP, fill="both", expand=True, padx=10, pady=10)
            self.graph2.pack_forget()
            self.graph3.pack_forget()
            self.graph4.pack_forget()
        elif self.graph_amount == 2:
            self.graph1.grid_forget()
            self.graph2.grid_forget()
            self.graph3.grid_forget()
            self.graph4.grid_forget()

            self.graph1.pack(
                side=ctk.TOP, fill="both", expand=True, padx=10, pady=(10, 0)
            )
            self.graph2.pack(
                side=ctk.TOP, fill="both", expand=True, padx=10, pady=(0, 10)
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


class SideBarGraph(ctk.CTkFrame):
    def __init__(
        self,
        parent: GraphPage,
        width=SIDEBAR_WIDTH,
    ):
        super().__init__(parent, width=width, corner_radius=0)
        self.parent: GraphPage = parent

        self.unique_dates = []

        try:
            db_handle = database.SQLiteDBManager()
            self.unique_dates = db_handle.get_unique_dates(1)
        finally:
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
            width=SIDEBAR_BUTTON_WIDTH,
        )
        self.plot_all_button.pack(side=ctk.TOP, padx=10, pady=(5, 10))

        # Graph Amount dropdown menu and label
        self.graph_amount_menu = DropdownAndLabel(
            self,
            "Graph Amount:",
            list(GRAPH_AMOUNTS.keys()),
            self.change_graph_amount_event,
            DEFAULT_GRAPH_AMOUNT,
            SIDEBAR_BUTTON_WIDTH,
        )
        self.graph_amount_menu.pack(side=ctk.TOP, padx=10, pady=0)

        # Create graph tabview
        self.tabview = ctk.CTkTabview(self, width=SIDEBAR_WIDTH)
        self.tabview.pack(side=ctk.TOP, fill="y", expand=True, pady=(15, 10), padx=10)
        self.tabview._segmented_button.configure(font=ctk.CTkFont(size=15))
        self.tabview.pack_propagate(False)

        self.graph1_tab = GraphTab(
            self.tabview,
            "Graph 1",
            self.parent,
            0,
            self.unique_dates,
            self.parent.all_graphs[0],
        )
        self.graph2_tab = GraphTab(
            self.tabview,
            "Graph 2",
            self.parent,
            1,
            self.unique_dates,
            self.parent.all_graphs[1],
        )
        self.graph3_tab = GraphTab(
            self.tabview,
            "Graph 3",
            self.parent,
            2,
            self.unique_dates,
            self.parent.all_graphs[2],
        )
        self.graph4_tab = GraphTab(
            self.tabview,
            "Graph 4",
            self.parent,
            3,
            self.unique_dates,
            self.parent.all_graphs[3],
        )

    def plot_all_button_event(self):
        print("PLOTTING bars...")
        self.parent.draw_all_graphs()

        # self.main_frame.set_figure_ax(self.graph_amount)

    def change_graph_amount_event(self, value):
        print("Amount")
        print("Amount: ", value)
        oikea = GRAPH_AMOUNTS.get(value)

        self.parent.graph_amount = oikea


class Graph(ctk.CTkFrame):
    def __init__(
        self, master=None, element_color="red", padx=10, pady=10, *args, **kwargs
    ):
        super().__init__(master, *args, **kwargs)
        self.graph_date: str = DEFAULT_GRAPH_DATE
        self.graph_mode: str = DEFAULT_GRAPH_MODE
        self.graph_type: str = DEFAULT_GRAPH_TYPE
        self.time_mode: str = DEFAULT_TIME_MODE
        self.weekday: str = DEFAULT_WEEKDAY
        self.time_range: str = DEFAULT_TIME_RANGE
        self.title: str = "Default title"
        self.x_values: List = []
        self.y_values: List = []
        self.x_label: str = "x label"
        self.y_label: str = "y label"
        self.element_color: str = element_color
        self.facecolor: str = "#333333"
        self.edge_color: str = "grey"
        self.axis_colors: str = "white"

        self.pack_propagate(False)
        self.fig = Figure(
            figsize=(20, 20), facecolor=self.facecolor, layout="constrained"
        )
        self.ax = self.fig.add_subplot()
        self.line: Line2D = None

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=padx, pady=pady)
        # self.canvas.get_tk_widget().configure()

    def draw_graph(self):
        self._get_graph_data()
        self._graph_settings()
        if self.graph_type.lower() == "bar graph":
            self.ax.bar(self.x_values, self.y_values, color=self.element_color)
        elif self.graph_type.lower() == "line graph":
            # if self.line is None:
            #     self.line = self.ax.plot(self.x_values, self.y_values)
            # else:
            #     self.line.set_data(self.x_values, self.y_values)

            self.line = self.ax.plot(
                self.x_values, self.y_values, color=self.element_color, marker="o"
            )

        self.canvas.draw()

    def _get_graph_data(self):
        search_start = utils.formatted_date_to_epoch(f"{self.graph_date} 00:00:00")
        search_end = search_start + 24 * 60 * 60  # +24 hours

        try:
            db_handle = database.SQLiteDBManager()

            visitors = db_handle.get_data_by_mode(
                1, search_start, search_end, GRAPH_MODES.get(self.graph_mode), 60 * 60
            )
            timestamps = database.helpers.calculate_timestamps(
                search_start, search_end, 60 * 60
            )

        finally:
            db_handle.__del__()

        self.x_values, self.y_values = utils.convert_for_day_graph(timestamps, visitors)

        # Korjaa! Lisää check, että oikean tyyppistä dataa.
        # for time_stamp in data[0]:
        for time_stamp in timestamps:
            if time_stamp is not None:
                found_date = time_stamp
                break
        date = utils.get_finnish_date(found_date)
        day = utils.get_finnish_day(found_date)
        location_name = "FUN Oulu Ritaharju"  # Korjaa! Hae itse.
        self.title = f"{location_name}, {day}, {date}"
        self.x_label = "Hour"
        self.y_label = self.graph_mode

    def _graph_settings(self):
        self.ax.clear()
        self.ax.set_facecolor(self.axis_colors)
        self.ax.set_title(self.title, color=self.axis_colors)
        self.ax.set_xlabel(self.x_label, color=self.axis_colors)
        self.ax.set_ylabel(self.y_label, color=self.axis_colors)
        self.ax.yaxis.set_tick_params(
            color=self.axis_colors, labelcolor=self.axis_colors
        )
        self.ax.xaxis.set_tick_params(
            color=self.axis_colors, labelcolor=self.axis_colors
        )
        for spine in self.ax.axes.spines.values():
            spine.set_edgecolor(self.edge_color)


class GraphTab:
    def __init__(
        self,
        parent: ctk.CTkTabview,
        tab_name: str,
        graph_page: GraphPage,
        graph_num: int,
        unique_dates: List[int],
        graph: Graph,
    ):
        parent.add(tab_name)
        self.handle = parent.tab(tab_name)

        self.graph_page = graph_page
        self.graph_num = graph_num
        self.graph = graph

        # create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.handle)
        self.scrollable_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        # "Plot graph"-button
        self.plot_graph_button = ctk.CTkButton(
            self.scrollable_frame,
            command=self.plot_graph_event,
            text="Plot Graph",
            width=SIDEBAR_BUTTON_WIDTH,
        )
        self.plot_graph_button.pack(side=ctk.TOP, padx=10, pady=(10, 10))

        self.time_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=LIGHT_GREY,
            border_width=1,
            border_color=LIGHT_GREY,
        )
        self.time_frame.pack(side=ctk.TOP)

        # Time Mode dropdown menu and label
        self.time_mode_menu = DropdownAndLabel(
            self.time_frame,
            "Time Mode:",
            TIME_MODES,
            self.change_time_mode_event,
            DEFAULT_TIME_MODE,
            SIDEBAR_BUTTON_WIDTH,
        )
        self.time_mode_menu.pack(side=ctk.TOP, padx=10, pady=(5, 10))

        # Frame for different time modes
        self.time_mode_frame = ctk.CTkFrame(
            self.time_frame,
            width=SIDEBAR_BUTTON_WIDTH + 10,
            height=90,
            fg_color=DARK_GREY,
        )
        self.time_mode_frame.pack(side=ctk.TOP, expand=True, pady=(0,5))
        self.time_mode_frame.pack_propagate(False)

        # Calendar frame
        self.calendar_frame = ctk.CTkFrame(
            self.time_mode_frame, fg_color="transparent"
        )
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
            width=SIDEBAR_BUTTON_WIDTH,
        )
        self.open_calendar_button.pack(side=ctk.TOP, pady=10)
        # Create constructive frame for Calendar
        self.cal_frame = ctk.CTkFrame(
            self.calendar_frame,
            width=SIDEBAR_BUTTON_WIDTH,
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
            width=SIDEBAR_BUTTON_WIDTH,
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
        )
        self.cal.highlight_dates()
        self.cal.bind("<<DateEntrySelected>>", self.update_date)  # Update calendar date
        self.cal.bind("<Key>", lambda e: "break")  # Disable writing in calendar
        self.cal.bind("<Control-c>", lambda e: None)  # Enable Ctrl + c
        self.cal.pack(side=ctk.TOP, fill="both", expand=True)

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
            list(WEEKDAYS.keys()),
            self.change_weekday_event,
            DEFAULT_WEEKDAY,
            SIDEBAR_BUTTON_WIDTH,
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
            "From now to:",
            TIME_RANGES,
            self.change_weekday_event,
            DEFAULT_TIME_RANGE,
            SIDEBAR_BUTTON_WIDTH,
        )
        self.time_range_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

        # Lift calendar frame to top
        self.calendar_frame.lift()

        # Graph Mode dropdown menu and label
        self.graph_mode_menu = DropdownAndLabel(
            self.scrollable_frame,
            "Graph Mode:",
            list(GRAPH_MODES.keys()),
            self.change_graph_mode_event,
            DEFAULT_GRAPH_MODE,
            SIDEBAR_BUTTON_WIDTH,
        )
        self.graph_mode_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

        # Graph Type dropdown menu and label
        self.graph_type_menu = DropdownAndLabel(
            self.scrollable_frame,
            "Graph Type:",
            GRAPH_TYPES,
            self.change_graph_type_event,
            DEFAULT_GRAPH_TYPE,
            SIDEBAR_BUTTON_WIDTH,
        )
        self.graph_type_menu.pack(side=ctk.TOP, padx=10, pady=(10, 10))

    def plot_graph_event(self):
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
        elif value == "Days of the week":
            self.weekday_frame.lift()
        elif value == "Time range":
            self.time_range_frame.lift()
            
        self.graph.time_mode = value

    def change_weekday_event(self, value):
        print("Set weekday to: ", value)
        self.graph.weekday = value

    def change_time_range_event(self, value):
        print("Set time range to: ", value)
        self.graph.time_range = value

    def test(self, event):
        pass


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


class DatabasePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)

        self.pack(side="top", fill="both", expand="true")

        self.main_frame = MainFrameDatabase(self)
        self.sidebar = SideBarDatabase(self, self.main_frame)


class MainFrameDatabase(ctk.CTkFrame):
    def __init__(
        self, parent: DatabasePage, width=0, side=ctk.RIGHT, expand=False, fill=None
    ):
        super().__init__(parent)
        self.col_interval = DEFAULT_COL_INTERVAL
        self.col_active = False

        # create frame for textbox label and textbox
        self.textbox_frame = ctk.CTkFrame(parent, width=TEXTBOX_WIDTH)
        self.textbox_frame.pack(side=ctk.RIGHT, fill=ctk.Y, padx=(0, 10), pady=10)
        self.textbox_frame.pack_propagate(False)
        # create textbox label
        self.textbox_label = ctk.CTkLabel(
            self.textbox_frame,
            font=ctk.CTkFont(size=15, weight="bold"),
            text="Database events",
            width=TEXTBOX_WIDTH,
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

        self.pack_propagate(False)
        self.pack(fill="both", expand=True, side=side, padx=10, pady=10)

        # Active Settings Label
        self.info_label = ctk.CTkLabel(
            self,
            font=ctk.CTkFont(size=20, weight="bold"),
            text="Active Settings",
            width=TEXTBOX_WIDTH,
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
            fg_color="#2b2b2b",
            padx=10,
            pady=20,
        )
        self.interval_label.pack(side=ctk.TOP, pady=(10, 10))

        # self.test_button = ctk.CTkButton(
        #     self,
        #     fg_color="#74bc50",
        #     hover_color="#83bab1",
        #     width=SIDEBAR_BUTTON_WIDTH,
        #     command=self.test_update,
        #     text="Start data collection",
        # )
        # self.test_button.pack(side="left")

    # def test_update(self):
    #     print("PARENT: ", self.parent.collection_interval)
    #     print("COLLECTING: ", self.parent.data_collection_active)

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
        self, parent: DatabasePage, main_frame: MainFrameDatabase, width=SIDEBAR_WIDTH
    ):
        super().__init__(parent, width=width, corner_radius=0)
        self.thread_id = 1  # Used for stopping data collection
        self.col_interval = DEFAULT_COL_INTERVAL

        self.parent = parent
        self.main_frame = main_frame
        self.unique_dates = []

        try:
            db_handle = database.SQLiteDBManager()
            self.unique_dates = db_handle.get_unique_dates(1)
        finally:
            db_handle.__del__()

        self.pack(fill="y", side="left")
        self.pack_propagate(False)

        # Sidebar label
        self.logo_label = ctk.CTkLabel(
            self, text="Database", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(side=ctk.TOP, padx=10, pady=(20, 0))

        # Button frame for start/stop data collection
        button_frame = ctk.CTkFrame(self, height=80, fg_color="transparent")
        button_frame.pack(fill="y", expand=False)
        # Start data collection Button
        self.start_button = ctk.CTkButton(
            self,
            fg_color="#74bc50",
            hover_color="green",
            width=SIDEBAR_BUTTON_WIDTH,
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
            width=SIDEBAR_BUTTON_WIDTH,
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
            values=list(DATA_COL_INTERVALS.keys()),
            command=self.change_interval_event,
            variable=ctk.StringVar(value=DEFAULT_COL_INTERVAL),
            width=SIDEBAR_BUTTON_WIDTH,
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
            args=(DATA_COL_INTERVALS.get(self.col_interval), self.thread_id),
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
            db_handle = database.SQLiteDBManager()

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
    def __init__(self, master=None, dates: List[str] = None, **kw):
        if dates is None:
            dates = []
        super().__init__(master, **kw)
        self.dates = dates
        self.configure_size()
        self.bind("<Configure>", self.update_on_resize)  # Bind to the Configure event

    def configure_size(self):
        # Calculate the font size based on the width of the widget
        width = self.winfo_width()
        font_size = int(width / DATE_ENTRY_FONT_SMALLNESS)
        cal_font_size = int(width / CALENDAR_FONT_SMALLNESS)

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
        for date in self.dates:
            dt = datetime.datetime.strptime(date, "%d-%m-%Y")
            self._calendar.calevent_create(dt, date, date)
            self._calendar.tag_config(date, background="#19a84c", foreground="white")

    def update_on_resize(self, event):
        self.configure_size()


class Menu(CTkMenuBar):
    def __init__(self, parent: App):
        super().__init__(parent, bg_color="#484848")
        self.file_button = self.add_cascade("File", text_color="white")
        self.view_button = self.add_cascade("View", text_color="white")
        self.help_button = self.add_cascade("Help", text_color="white")

        # Buttons inside file
        self.file_dropdown = CustomDropdownMenu(master=parent, widget=self.file_button)
        self.file_dropdown.add_option(
            option="Save Graph", command=lambda: print("save graph")
        )
        self.file_dropdown.add_separator()
        # Choose database submenu
        sub_menu = self.file_dropdown.add_submenu("Choose Database")
        sub_menu.add_option(option="Default database")
        sub_menu.add_option(option="Choose database path")

        # Buttons inside View
        self.view_dropdown = CustomDropdownMenu(master=parent, widget=self.view_button)
        self.view_dropdown.add_option(
            option="Graphs", command=lambda: parent.show_graph_page()
        )
        self.view_dropdown.add_option(
            option="Database", command=lambda: parent.show_database_page()
        )

        # Buttons inside Help
        self.view_dropdown = CustomDropdownMenu(master=parent, widget=self.help_button)
        self.view_dropdown.add_option(
            option="How to use", command=lambda: print("How to use")
        )
        self.view_dropdown.add_option(
            option="something", command=lambda: print("something")
        )


def main():
    App("VisitorFlowTracker")


if __name__ == "__main__":
    main()
