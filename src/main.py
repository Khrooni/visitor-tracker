import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from tkcalendar import DateEntry

import customtkinter as ctk
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import datetime
from typing import List, Tuple
import time
import threading

import database
import retrive_data
from retrive_data import Location
import utils

from dataclasses import dataclass


WINDOW_START_SIZE = (1100, 580)
WINDOW_MIN_SIZE = (850, 450)
SIDEBAR_WIDTH = 250
SIDEBAR_BUTTON_WIDTH = 140
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

GRAPH_MODES = [
    "Visitors",
    "Average Visitors",
    "Highest Visitors",
    "Lowest Visitors",
]
DEFAULT_GRAPH_MODE = "Visitors"

GRAPH_TYPES = ["Bar Graph", "Line Graph"]
DEFAULT_GRAPH_TYPE = "Bar Graph"
DEFAULT_GRAPH_DATE = datetime.datetime.now().strftime("%d-%m-%Y")

TEXTBOX_WIDTH = 350


class App(ctk.CTk):
    # graph_amount = 1
    # graph_mode = ["Visitors", "Visitors", "Visitors", "Visitors"]
    # graph_type = ["Bar Graph", "Bar Graph", "Bar Graph", "Bar Graph"]

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

        self.graph_amount = DEFAULT_GRAPH_AMOUNT
        self.fig = None
        self.graphs = [GraphSettings(graph_num=num) for num in range(4)]

        self.main_frame = MainFrameGraph(self)
        self.sidebar = SideBarGraph(
            self,
            self.main_frame,
            self.graphs,
            self.graph_amount,
            self.fig,
        )
        self.sidebar.pack(fill="y", side="left")
        self.main_frame.pack(fill="both", expand=True, side="left", padx=10, pady=10)
    

    def draw_all_graphs(self):
        print("Draw all graphs")

    def set_fig_and_ax(self):
        if self.graph_amount == 1:
            self.fig, axis = plt.subplots(
                1,
                1,
                figsize=(20, 20),
                layout="constrained",
                facecolor="#2b2b2b",
            )
            self.graphs[0].ax = axis
        elif self.graph_amount == 2:
            self.fig, axes = plt.subplots(
                2, 1, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
            )
            self.graphs[0].ax = axes[0]
            self.graphs[1].ax = axes[1]
        elif self.graph_amount == 4:
            self.fig, axes = plt.subplots(
                2,
                2,
                figsize=(20, 20),
                layout="constrained",
                facecolor="#2b2b2b",
            )
            self.graphs[0].ax = axes[0, 0]
            self.graphs[1].ax = axes[0, 1]
            self.graphs[2].ax = axes[1, 0]
            self.graphs[3].ax = axes[1, 1]


class GraphSettings:
    def __init__(
        self,
        graph_num: int,
        ax: plt.Axes = None,
        graph_date: str = DEFAULT_GRAPH_DATE,
        graph_mode: str = DEFAULT_GRAPH_MODE,
        graph_type: str = DEFAULT_GRAPH_TYPE,
        title: str = "Default title",
        x_values: List = [],
        y_values: List = [],
        x_label: str = "x label",
        y_label: str = "y label",
        element_color: str = "purple",
        bg_color: str = "white",
        edge_color: str = "grey",
        axis_colors: str = "white",
    ):
        self.ax = ax

        self.graph_date = graph_date
        self.graph_mode = graph_mode
        self.graph_type = graph_type
        self.title = title
        self.x_values = x_values
        self.y_values = y_values
        self.x_label = x_label
        self.y_label = y_label
        self.element_color = element_color
        self.bg_color = bg_color
        self.edge_color = edge_color
        self.axis_colors = axis_colors

    def _get_graph_data(self):
        search_start = utils.time_to_epoch(f"{self.graph_date} 00:00:00")
        search_end =  search_start + 24 * 60 * 60 # +24 hours

        try:
            db_handle = database.SQLiteDBManager()

            location_data = db_handle.get
            data = db_handle.get_avg_activity_between_peridiocally(1, search_start, search_end, 60 * 60)
        finally:
            db_handle.__del__()

        self.x_values, self.y_values = utils.convert_for_day_graph(data)

        date = utils.get_finnish_date(data[0][0])






    def draw_graph(self):
        if self.graph_type.lower() == "bar":
            self._bar_graph()
        elif self.graph_type.lower() == "line":

            self._line_graph()

    def _bar_graph(self):
        self._graph_settings(
            self.ax,
            title=self.title,
            xlabel=self.x_label,
            ylabel=self.y_label,
            colors=self.axis_colors,
            edge_color=self.edge_color,
        )
        self.ax.bar(self.x_values, self.y_values, color=self.color)

    def _line_graph(self, x, y, ax, title=None, xlabel=None, ylabel=None, color=None):
        self._graph_settings(
            ax,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            colors="white",
            edge_color="grey",
        )
        ax.plot(x, y, color=color, marker="o")

    def _graph_settings(
        self, ax, title=None, xlabel=None, ylabel=None, colors=None, edge_color=None
    ):
        ax.clear()
        ax.set_facecolor(colors)
        ax.set_title(title, color=colors)
        ax.set_xlabel(xlabel, color=colors)
        ax.set_ylabel(ylabel, color=colors)
        ax.yaxis.set_tick_params(color=colors, labelcolor=colors)
        ax.xaxis.set_tick_params(color=colors, labelcolor=colors)
        for spine in ax.axes.spines.values():
            spine.set_edgecolor(edge_color)
    
    def test_graph_date(self):
        print(self.graph_date)


class MainFrameGraph(ctk.CTkFrame):
    def __init__(self, parent: App, width=0, side="left", expand=False, fill=None):
        super().__init__(parent)
        self.pack_propagate(False)

        self.fig = None
        self.ax = None
        self.canvas = None
        # self.pack(fill="both", expand=True, side=side, padx=10, pady=10)

       

        self.label = ctk.CTkLabel(
            self,
            font=ctk.CTkFont(size=50, weight="bold"),
            text="No graphs plotted",
            width=TEXTBOX_WIDTH,
            height=50,
            fg_color="transparent",
            bg_color="transparent",
            corner_radius=10,
        )
        self.label.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        self.label.destroy()

        self.fig, self.ax = plt.subplots(
            1, 1, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
        )
        # fig.set_constrained_layout_pads()

        # fig, ax = plt.subplots(
        #     2, 1, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
        # )

        # canvas = FigureCanvasTkAgg(fig, master=self)
        # canvas.get_tk_widget().pack(padx=10, pady=10)

        # self.draw_amount_graphs(
        #     2,
        #     [x_values, x_values1],
        #     [y_values, y_values1],
        #     [ax[0], ax[1]],
        #     [time, time1],
        #     ["time1", "time2"],
        #     ["visitors1", "visitors2"],
        #     ["purple", "blue"],
        # )

        # fig, ax = plt.subplots(
        #     2, 2, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
        # )

        # self.draw_amount_graphs(
        #     4,
        #     [x_values, x_values, x_values, x_values],
        #     [y_values, y_values, y_values, y_values],
        #     [ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]],
        #     [time, time, time, time],
        #     ["time", "time", "time", "time4"],
        #     ["visitors1", "visitors2", "visitors3", "visitors4"],
        #     ["purple", "blue", "red", "green"],
        # )

        # canvas.draw()

        # self.draw_amount_graphs(
        #     4,
        #     [[1, 2, 3, 4], x_values, x_values, x_values],
        #     [[10, 20, 30, 40], y_values, y_values, y_values],
        #     [ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]],
        #     [time, time, time, time],
        #     ["time", "time", "time", "time4"],
        #     ["visitors1", "visitors2", "visitors3", "visitors4"],
        #     ["red", "blue", "green", "orange"],
        # )

        # canvas.draw()

        # fig, ax = plt.subplots(
        #     2, 1, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
        # )
        # canvas.figure = fig
        # # fig2.set_constrained_layout_pads()
        # # # canvas = FigureCanvasTkAgg(fig, master=self)
        # # # canvas.get_tk_widget().pack(padx=10, pady=10)

        # self.draw_amount_graphs(
        #     2,
        #     [x_values, x_values],
        #     [y_values, y_values],
        #     [ax[0], ax[1]],
        #     [time, time],
        #     ["time", "time2"],
        #     ["visitors1", "visitor2"],
        #     ["purple", "red"],
        # )

        # canvas.draw()

        # fig, ax = plt.subplots(
        #     1, 1, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
        # )
        # canvas.figure = fig
        # self.draw_amount_graphs(
        #     1,
        #     [x_values],
        #     [y_values],
        #     [ax],
        #     [time],
        #     ["time"],
        #     ["visitors1"],
        #     ["purple"],
        #     graph_type="line",
        # )

    def set_canvas(self, figure):
        self.canvas = FigureCanvasTkAgg(figure, master=self)
        self.canvas.get_tk_widget().pack(padx=10, pady=10)

    def draw_amount_graphs(
        self,
        amount: int,
        x_values: List[List],
        y_values: List[List],
        ax: List,
        titles: List[str | None],
        x_labels: List[str | None],
        y_labels: List[str | None],
        colors: List,
        graph_type: str = "bar",
    ):
        if graph_type.lower() == "bar":
            for i in range(amount):
                self._bar_graph(
                    x_values[i],
                    y_values[i],
                    ax[i],
                    titles[i],
                    x_labels[i],
                    y_labels[i],
                    colors[i],
                )
        elif graph_type.lower() == "line":
            for i in range(amount):
                self._line_graph(
                    x_values[i],
                    y_values[i],
                    ax[i],
                    titles[i],
                    x_labels[i],
                    y_labels[i],
                    colors[i],
                )

    def _bar_graph(self, x, y, ax, title=None, xlabel=None, ylabel=None, color=None):
        self._graph_settings(
            ax,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            colors="white",
            edge_color="grey",
        )
        ax.bar(x, y, color=color)

    def _line_graph(self, x, y, ax, title=None, xlabel=None, ylabel=None, color=None):
        self._graph_settings(
            ax,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            colors="white",
            edge_color="grey",
        )
        ax.plot(x, y, color=color, marker="o")

    def _graph_settings(
        self, ax, title=None, xlabel=None, ylabel=None, colors=None, edge_color=None
    ):
        ax.clear()
        ax.set_facecolor(colors)
        ax.set_title(title, color=colors)
        ax.set_xlabel(xlabel, color=colors)
        ax.set_ylabel(ylabel, color=colors)
        ax.yaxis.set_tick_params(color=colors, labelcolor=colors)
        ax.xaxis.set_tick_params(color=colors, labelcolor=colors)
        for spine in ax.axes.spines.values():
            spine.set_edgecolor(edge_color)


class SideBarGraph(ctk.CTkFrame):
    def __init__(
        self,
        parent: GraphPage,
        main_frame: MainFrameGraph,
        graphs: List[GraphSettings],
        graph_amount: int,
        fig,
        width=SIDEBAR_WIDTH,
    ):
        super().__init__(parent, width=width, corner_radius=0)
        self.parent = parent
        self.main_frame = main_frame
        self.graphs = graphs
        self.graph_amount = graph_amount
        self.fig = fig
        self.graph_mode = DEFAULT_GRAPH_AMOUNT
        self.graph_amount = DEFAULT_GRAPH_MODE
        self.graph_type = DEFAULT_GRAPH_TYPE

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
        self.logo_label.pack(side=tk.TOP, padx=10, pady=(20, 10))

        # "Plot All Graphs"-button
        self.plot_all_button = ctk.CTkButton(
            self, command=self.plot_all_button_event, text="Plot All Graphs"
        )
        self.plot_all_button.pack(side=tk.TOP, padx=10, pady=10)

        # Graph Amount label
        self.graph_amount_label = ctk.CTkLabel(self, text="Graph Amount:", anchor="w")
        self.graph_amount_label.pack(side=tk.TOP, padx=10, pady=(10, 0))
        # Graph Amount dropdown menu
        self.graph_amount_option_menu = ctk.CTkOptionMenu(
            self,
            values=list(GRAPH_AMOUNTS.keys()),
            command=self.change_graph_amount_event,
            variable=ctk.StringVar(value=DEFAULT_GRAPH_AMOUNT),
        )
        self.graph_amount_option_menu.pack(side=tk.TOP, padx=10, pady=(0, 10))

        # Create graph tabview
        self.tabview = ctk.CTkTabview(self, width=SIDEBAR_WIDTH)
        self.tabview.pack(side=tk.BOTTOM)
        self.graph1_tab = GraphTab(self.tabview, "Graph 1", self.parent, 1, self.unique_dates, self.graphs[0])
        self.graph2_tab = GraphTab(self.tabview, "Graph 2", self.parent, 2,self.unique_dates, self.graphs[1])
        self.graph3_tab = GraphTab(self.tabview, "Graph 3", self.parent, 3,self.unique_dates, self.graphs[2])
        self.graph4_tab = GraphTab(self.tabview, "Graph 4", self.parent, 4, self.unique_dates, self.graphs[3])

    def plot_all_button_event(self):
        print("PLOTTING bar...")
        # self.parent.set_fig_and_ax()
        self.parent.draw_all_graphs()
        # self.main_frame.set_figure_ax(self.graph_amount)

    def change_graph_amount_event(self, value):
        print("Amount")
        print("Amount: ", value)
        oikea = GRAPH_AMOUNTS.get(value)

        self.parent.graph_amount = oikea

    # def set_fig_and_ax(self, parent: App, amount: int):
    #     """ """
    #     if amount == 1:
    #         self.fig, ax = plt.subplots(
    #             1,
    #             1,
    #             figsize=(20, 20),
    #             layout="constrained",
    #             facecolor="#2b2b2b",
    #         )
    #         self.graphs[0].ax = ax
    #     elif amount == 2:
    #         self.fig, parent.ax = plt.subplots(
    #             2, 1, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
    #         )
    #     elif amount == 4:
    #         parent.fig, parent.ax = plt.subplots(
    #             2,
    #             2,
    #             figsize=(20, 20),
    #             layout="constrained",
    #             facecolor="#2b2b2b",
    #         )


class GraphTab:
    def __init__(self, parent: ctk.CTkTabview, tab_name: str, graph_page: GraphPage, graph_num: int, unique_dates: List[int], graph: GraphSettings):
        parent.add(tab_name)
        self.handle = parent.tab(tab_name)
        self.graph_page = graph_page
        self.graph = graph

        # "Plot graph"-button
        self.plot_graph_button = ctk.CTkButton(
            self.handle,
            command=self.plot_graph_event,
            text="Plot Graph",
        )
        self.open_calendar_button.pack(side=tk.TOP, padx=10, pady=(10,20))

        # "Open Calendar"-button
        self.open_calendar_button = ctk.CTkButton(
            self.handle,
            command=self.open_calendar_event,
            text="Open Calendar",
        )
        self.open_calendar_button.pack(side=tk.TOP, padx=10, pady=10)
        # Create Calendar
        sel = tk.StringVar()
        self.cal = CustomDateEntry(
            self.handle,
            dates=unique_dates,
            date_pattern="dd-mm-yyyy",
            font="Helvetica 20 bold",
            justify="center",
            width=12,
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
        self.cal.bind("<Key>", lambda e: "break")  # Disable writing in calendar
        self.cal.pack(side=tk.TOP)

        # Graph Mode label
        self.graph_mode_label = ctk.CTkLabel(
            self.handle, text="Graph Mode:", anchor="w"
        )
        self.graph_mode_label.pack(side=tk.TOP, padx=10, pady=(10, 10))
        # Graph Mode dropdown menu
        self.graph_mode_option_menu = ctk.CTkOptionMenu(
            self.handle,
            values=GRAPH_MODES,
            command=self.change_graph_mode_event,
            variable=ctk.StringVar(value=DEFAULT_GRAPH_MODE),
        )
        self.graph_mode_option_menu.pack(side=tk.TOP, padx=10, pady=(0, 10))

        # Graph Type label
        self.graph_type_label = ctk.CTkLabel(
            self.handle, text="Graph Type:", anchor="w"
        )
        self.graph_type_label.pack(side=tk.TOP, padx=10, pady=(10, 10))
        # Graph Type dropdown menu
        self.graph_type_option_menu = ctk.CTkOptionMenu(
            self.handle,
            values=GRAPH_TYPES,
            command=self.change_graph_type_event,
            variable=ctk.StringVar(value=DEFAULT_GRAPH_TYPE),
        )
        self.graph_type_option_menu.pack(side=tk.TOP, padx=10, pady=(0, 10))

    def plot_graph_event(self):
        print("plot single graph")
        self.graph_page.set_fig_and_ax()
        self.graph.draw_graph()

    def open_calendar_event(self):
        self.cal.drop_down()
        self.graph.test_graph_date()

    def change_graph_type_event(self, value):
        print("Set graph type to: ", value)
        self.graph.graph_type = value

    def change_graph_mode_event(self, value):
        print("Set graph value to: ", value)
        self.graph.graph_mode = value


class DatabasePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        # self.collection_interval = DEFAULT_COL_INTERVAL  # Changed from sidebar.
        # self.data_collection_active = False
        # self.textbox: ctk.CTkTextbox = None

        self.pack(side="top", fill="both", expand="true")

        self.main_frame = MainFrameDatabase(self)
        self.sidebar = SideBarDatabase(self, self.main_frame)

    def collect_data(self):
        pass

    def write_to_textbox(self, text: str):
        print("writing")
        self.textbox.insert("0.0", text)


class MainFrameDatabase(ctk.CTkFrame):
    def __init__(
        self, parent: DatabasePage, width=0, side=tk.RIGHT, expand=False, fill=None
    ):
        super().__init__(parent)
        self.col_interval = DEFAULT_COL_INTERVAL
        self.col_active = False

        # create frame for textbox label and textbox
        self.textbox_frame = ctk.CTkFrame(parent, width=TEXTBOX_WIDTH)
        self.textbox_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
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
            side=tk.TOP,
            padx=10,
            pady=(10, 0),
        )
        # create textbox (read only)
        self.textbox = ctk.CTkTextbox(self.textbox_frame)
        self.textbox.pack(
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10,
        )
        self.textbox.bind("<Key>", lambda e: "break")

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
        self.info_label.pack(side=tk.TOP, pady=10)

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
        self.collection_checkbox.configure(state=tk.DISABLED)
        self.collection_checkbox.pack(side=tk.TOP, pady=(50, 0))

        self.interval_label = ctk.CTkLabel(
            self,
            text=f"Active Data Collection Interval: {self.col_interval}",
            corner_radius=10,
            fg_color="#2b2b2b",
            padx=10,
            pady=20,
        )
        self.interval_label.pack(side=tk.TOP, pady=(10, 10))

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
        self.collection_checkbox.configure(state=tk.NORMAL)
        self.collection_checkbox.toggle()
        self.collection_checkbox.configure(state=tk.DISABLED)

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
        self.logo_label.pack(side=tk.TOP, padx=10, pady=(20, 0))

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
            anchor=tk.CENTER,
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
            anchor=tk.CENTER,
        )
        # Start data collection button on top
        self.start_button.lift()

        # Interval dropdown menu label
        self.interval_label = ctk.CTkLabel(
            self, text="Data Collection Interval:", anchor="w"
        )
        self.interval_label.pack(side=tk.TOP, padx=10, pady=(10, 0))
        # Interval dropdown menu
        self.interval_option_menu = ctk.CTkOptionMenu(
            self,
            values=list(DATA_COL_INTERVALS.keys()),
            command=self.change_interval_event,
            variable=ctk.StringVar(value=DEFAULT_COL_INTERVAL),
        )
        self.interval_option_menu.pack(side=tk.TOP, padx=10, pady=(10, 10))

    def write_to_textbox(self, text: str):
        self.main_frame.write_to_textbox(text)

    def start_collecting_data(self):
        self.stop_button.lift()
        self.main_frame.toggle_collection()
        self.main_frame.change_interval_label(self.col_interval)
        self.write_to_textbox("Data Collection Started!\n\n")

        threading.Thread(
            target=self._get_data_in_intervals,
            args=(DATA_COL_INTERVALS.get(self.col_interval), self.thread_id),
        ).start()

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

                data = retrive_data.get_data()
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
                            f"Added to the database: \n{self._format_data(location)}\n\n"
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

        return

    def _format_data(self, location_data: Location):
        formatted_str = f"""Location name: {location_data.location_name}
                        \nTime: {location_data.get_formatted_finnish_time()}
                        \nVisitor amount: {location_data.location_visitors}"""

        return formatted_str


class CustomDateEntry(DateEntry):
    def __init__(self, master=None, dates: List[str] = [], **kw):
        super().__init__(master, **kw)
        self.dates = dates

    def highlight_dates(self):
        for date in self.dates:
            dt = datetime.datetime.strptime(date, "%d-%m-%Y")
            self._calendar.calevent_create(dt, date, date)
            # self._calendar.tag_config(date, background="#09ff08", foreground="white")
            self._calendar.tag_config(date, background="#19a84c", foreground="white")


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
