import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from tkcalendar import DateEntry

import customtkinter as ctk
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu

import datetime


import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from typing import List, Tuple

import database
from retrive_data import Location
from utils import (
    time_to_epoch,
    epoch_to_time,
    get_finnish_time,
    get_finnish_date,
    get_finnish_day,
    get_formatted_finnish_time,
    get_finnish_hour,
    convert_for_day_graph,
)


import math

# plt.rcParams["figure.figsize"] = (10, 4)



SIDEBAR_WIDTH = 175
SIDEBAR_BUTTON_WIDTH = 140
DEFAULT_COL_INTERVAL = "30 min"
data_col_intervals = {
    "30 sec": 30,
    "1 min": 60,
    "5 min": 5 * 60,
    "10 min": 10 * 60,
    "30 min": 30 * 60,
    "1 hour": 60 * 60,
}
graph_amounts = {"1":1, "2": 2, "4":4}
DEFAULT_GRAPH_AMOUNT = 1

graph_modes = [
        "Visitors",
        "Average Visitors",
        "Highest Visitors",
        "Lowest Visitors",
    ]
DEFAULT_GRAPH_MODE = "Visitors"

graph_types = ["Bar Graph", "Line Graph"]
DEFAULT_GRAPH_TYPE = "Bar Graph"

class App(ctk.CTk):
    graph_amount = "1"
    graph_mode = ["Visitors", "Visitors", "Visitors", "Visitors"]
    graph_type = ["Bar Graph", "Bar Graph", "Bar Graph", "Bar Graph"]

    def __init__(self, title, size=(1100, 580), min_size=(580, 450)):
        # def __init__(self, title, size=(1100, 580), min_size=(580, 400)):
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

        self.sidebar = SideBarGraph(self)
        self.main_frame = MainFrameGraph(self)


class DatabasePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.pack(side="top", fill="both", expand="true")

        self.sidebar = SideBarDatabase(self)
        self.main_frame = MainFrameDatabase(self)


class SideBarGraph(ctk.CTkFrame):
    def __init__(self, parent: App, width=SIDEBAR_WIDTH):
        super().__init__(parent, width=width, corner_radius=0)
        self.unique_dates = []

        try:
            db_handle = database.SQLiteDBManager()
            self.unique_dates = db_handle.get_unique_dates(1)
        finally:
            db_handle.__del__()

        self.pack_propagate(False)
        self.pack(fill="y", side="left")

        # Sidebar name text
        self.logo_label = ctk.CTkLabel(
            self, text="Graphs", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(side=tk.TOP, padx=10, pady=(20, 10))

        # Sidebar button 1
        self.sidebar_button_1 = ctk.CTkButton(
            self, command=self.plot_bar_button_event, text="Plot Graph"
        )
        self.sidebar_button_1.pack(side=tk.TOP, padx=10, pady=10)

        # Sidebar buton 2
        self.sidebar_button_2 = ctk.CTkButton(
            self, command=self.sidebar_button_event, text="Open Calendar"
        )
        self.sidebar_button_2.pack(side=tk.TOP, padx=10, pady=10)

        cal = CustomDateEntry(
            self,
            dates=self.unique_dates,
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
        cal.highlight_dates()
        cal.pack()


        # Graph Type dropdown menu
        self.graph_type_option_menu = ctk.CTkOptionMenu(
            self,
            values=graph_types,
            command=self.change_graph_type_event,
            variable=ctk.StringVar(value=DEFAULT_GRAPH_TYPE)
        )
        self.graph_type_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))
        # Graph Type label
        self.graph_type_label = ctk.CTkLabel(self, text="Graph Type:", anchor="w")
        self.graph_type_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

        # Graph Amount dropdown menu
        self.graph_amount_option_menu = ctk.CTkOptionMenu(
            self,
            values=list(graph_amounts.keys()),
            command=self.change_graph_amount_event,
            variable=ctk.StringVar(value=DEFAULT_GRAPH_AMOUNT)
        )
        self.graph_amount_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

        # Graph Amount label
        self.graph_amount_label = ctk.CTkLabel(self, text="Graph Amount:", anchor="w")
        self.graph_amount_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

        # Graph Mode dropdown menu
        self.graph_mode_option_menu = ctk.CTkOptionMenu(
            self,
            values=graph_modes,
            command=self.change_graph_mode_event,
            variable=ctk.StringVar(value=DEFAULT_GRAPH_MODE)

        )
        self.graph_mode_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))
        # Graph Mode label
        self.graph_mode_label = ctk.CTkLabel(self, text="Graph Mode:", anchor="w")
        self.graph_mode_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

    def sidebar_button_event(self):
        print("sidebar_button click")

    def plot_bar_button_event(self):
        print("PLOTTING bar...")

    def change_graph_type_event(self, value):
        print("appear")
        print("value: ", value)

    def change_graph_mode_event(self, value):
        print("scale")
        print("value: ", value)

    def change_graph_amount_event(self, value):
        print("Amount")
        print("Amount: ", value)


class SideBarDatabase(ctk.CTkFrame):
    def __init__(self, parent: App, width=SIDEBAR_WIDTH):
        super().__init__(parent, width=width, corner_radius=0)
        self.unique_dates = []

        try:
            db_handle = database.SQLiteDBManager()
            self.unique_dates = db_handle.get_unique_dates(1)
        finally:
            db_handle.__del__()

        self.pack_propagate(False)
        self.pack(fill="y", side="left")

        # Sidebar name text
        self.logo_label = ctk.CTkLabel(
            self, text="Database", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(side=tk.TOP, padx=10, pady=(20, 10))

        button_frame = ctk.CTkFrame(self, height=80, fg_color="transparent")
        button_frame.pack(fill="y", expand=False)

        # self.start_button_frame = ctk.CTkFrame(self, height=80, fg_color="transparent")
        # self.start_button_frame.pack(fill="y", expand=False)
        # Sidebar buton 2
        self.start_button = ctk.CTkButton(
            self,
            width=SIDEBAR_BUTTON_WIDTH,
            command=self.collect_data,
            text="Start data collection",
        )
        self.start_button.place(
            in_=button_frame,
            relx=0.5,
            rely=0.5,
            anchor=tk.CENTER,
        )

        # self.stop_button_frame = ctk.CTkFrame(self, height=80, fg_color="transparent")
        # self.stop_button_frame.pack(fill="y", expand=False)
        # Sidebar buton 2
        self.stop_button = ctk.CTkButton(
            self,
            # padx=0,
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

        self.start_button.lift()

        # Sidebar button 1
        self.sidebar_button_3 = ctk.CTkButton(
            self, command=self.plot_bar_button_event, text="Database stuff"
        )
        self.sidebar_button_3.pack(side=tk.TOP, padx=10, pady=10)

        # Graph Type dropdown menu
        self.graph_type_option_menu = ctk.CTkOptionMenu(
            self,
            values=list(data_col_intervals.keys()),
            command=self.change_graph_type_event,
            variable=ctk.StringVar(value=DEFAULT_COL_INTERVAL),
        )
        self.graph_type_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 5))

        # Graph Type label
        self.graph_type_label = ctk.CTkLabel(
            self, text="Data Collection Interval:", anchor="w"
        )
        self.graph_type_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 0))

        # # Graph Amount dropdown menu
        # self.graph_amount_option_menu = ctk.CTkOptionMenu(
        #     self,
        #     values=["1", "2", "4"],
        #     command=self.change_graph_amount_event,
        # )
        # self.graph_amount_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))
        # # Graph Amount label
        # self.graph_amount_label = ctk.CTkLabel(self, text="Graph Amount:", anchor="w")
        # self.graph_amount_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

        # # Graph Mode dropdown menu
        # self.graph_mode_option_menu = ctk.CTkOptionMenu(
        #     self,
        #     values=[
        #         "Visitors",
        #         "Average Visitors",
        #         "Highest Visitors",
        #         "Lowest Visitors",
        #     ],
        #     command=self.change_graph_mode_event,
        # )
        # self.graph_mode_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))
        # # Graph Mode label
        # self.graph_mode_label = ctk.CTkLabel(self, text="Graph Mode:", anchor="w")
        # self.graph_mode_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

    def collect_data(self):
        print("collecting data")
        self.stop_button.lift()

    def stop_collecting_data(self):
        print("Data collection stopped")
        self.start_button.lift()

    def sidebar_button_event(self):
        print("sidebar_button click")

    def plot_bar_button_event(self):
        print("PLOTTING bar...")

    def change_graph_type_event(self, value):
        print("appear")
        print("value: ", value)

    def change_graph_mode_event(self, value):
        print("scale")
        print("value: ", value)

    def change_graph_amount_event(self, value):
        print("Amount")
        print("Amount: ", value)


class CustomDateEntry(DateEntry):
    def __init__(self, master=None, dates: List[str] = [], **kw):
        super().__init__(master, **kw)
        self.dates = dates

    def highlight_dates(self):
        for date in self.dates:
            dt = datetime.datetime.strptime(date, "%d-%m-%Y")
            self._calendar.calevent_create(dt, date, date)
            self._calendar.tag_config(date, background="#454545", foreground="white")


class MainFrameGraph(ctk.CTkFrame):
    def __init__(self, parent: App, width=0, side="left", expand=False, fill=None):
        super().__init__(parent)

        self.pack_propagate(False)
        self.pack(fill="both", expand=True, side=side, padx=10, pady=10)

        alku = time_to_epoch("27-3-2024 00:00:00")
        # print(alku)
        loppu = time_to_epoch("28-3-2024 00:00:00")
        # print(loppu)

        try:
            db = database.SQLiteDBManager()
            # data = db.get_activity_between(1, alku, loppu)
            # data = db.get_avg_activity_between(1, alku, loppu)
            data2 = db.get_avg_activity_between_peridiocally(1, alku, loppu, 60 * 60)
        finally:
            db.__del__()

        x_values, y_values = convert_for_day_graph(data2)

        time = get_formatted_finnish_time(data2[0][0])

        fig, ax = plt.subplots(
            2, 2, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
        )
        fig.set_constrained_layout_pads()
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack(padx=10, pady=10)

        self.draw_amount_graphs(
            4,
            [x_values, x_values, x_values, x_values],
            [y_values, y_values, y_values, y_values],
            [ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]],
            [time, time, time, time],
            ["time", "time", "time", "time4"],
            ["visitors1", "visitors2", "visitors3", "visitors4"],
            ["purple", "blue", "red", "green"],
        )

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


class MainFrameDatabase(ctk.CTkFrame):
    def __init__(self, parent: App, width=0, side="left", expand=False, fill=None):
        super().__init__(parent)

        self.pack_propagate(False)
        self.pack(fill="both", expand=True, side=side, padx=10, pady=10)

        alku = time_to_epoch("27-3-2024 00:00:00")
        # print(alku)
        loppu = time_to_epoch("28-3-2024 00:00:00")
        # print(loppu)


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
        # Choose databse submenu
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


def bar_graph2(x, y, ax, title=None, xlabel=None, ylabel=None):
    color = "purple"

    # ax.clear()
    bar_figure = plt.bar(x, y, color=color)
    # bar_figure
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # ax.bar(x,y)
    return bar_figure


def main():
    App("VisitorFlowTracker")

    # alku = time_to_epoch("27-3-2024 00:00:00")
    # print(alku)
    # loppu = time_to_epoch("28-3-2024 00:00:00")
    # print(loppu)

    # ctk.set_appearance_mode("Dark")
    # # ctk.set_default_color_theme("green")

    # root = ctk.CTk()
    # root.geometry("550x400")

    # frame = ctk.CTkFrame(root)
    # frame.pack(fill="both", padx=10, pady=10, expand=True)

    # # style = ttk.Style(root)
    # # style.theme_use("default")

    # cal = Calendar(frame, selectmode='day', locale='en_US', disabledforeground='red',
    #             cursor="hand2", background=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
    #             selectbackground=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])
    # cal.pack(fill="both", expand=True, padx=10, pady=10)

    # root.mainloop()


if __name__ == "__main__":
    main()
