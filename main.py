import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from tkcalendar import DateEntry

import customtkinter as ctk
from CTkMenuBar import CTkMenuBar, CustomDropdownMenu

import datetime


import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from typing import List

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
)


import math

plt.rcParams["figure.figsize"] = (10, 4)


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

        self.sidebar = SideBarGraph(self)

        # self.main_frame = MainFrameGraph(self)

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


class SideBarGraph(ctk.CTkFrame):
    def __init__(self, parent: App, width=175):
        super().__init__(parent, width=width, corner_radius=0)
        # self.pack_propagate(False)
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

        # self.frame = ctk.CTkFrame(self)
        # self.frame.pack(fill="both", padx=10, pady=10, expand=True)

        cal = CustomDateEntry(
            self,
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

        # cal = Calendar(
        #     self.frame,
        #     selectmode="day",
        #     locale="en_US",
        #     disabledforeground="red",
        #     cursor="hand2",
        #     background=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
        #     selectbackground=ctk.ThemeManager.theme["CTkButton"]["fg_color"][1],
        # )
        cal.pack()
        

        # highlighted_dates = ['2024-03-15', '2024-03-20', '2024-03-25']

        # # Extract year, month, and day from the highlighted dates
        # highlighted_dates = [tuple(map(int, date.split('-'))) for date in highlighted_dates]

        # # Highlight the dates in the DateEntry widget
        # cal.calevent_remove(all=True)  # Clear existing highlights
        # for date in highlighted_dates:
        #     cal.calevent_create(date, 'Highlighted Date', 'Highlight')

        # Graph Type dropdown menu
        self.graph_type_option_menu = ctk.CTkOptionMenu(
            self,
            values=["Bar Graph", "Line Graph"],
            command=self.change_graph_type_event,
        )
        self.graph_type_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))
        # Graph Type label
        self.graph_type_label = ctk.CTkLabel(self, text="Graph Type:", anchor="w")
        self.graph_type_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

        # Graph Amount dropdown menu
        self.graph_amount_option_menu = ctk.CTkOptionMenu(
            self,
            values=["1", "2", "4"],
            command=self.change_graph_amount_event,
        )
        self.graph_amount_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))
        # Graph Amount label
        self.graph_amount_label = ctk.CTkLabel(self, text="Graph Amount:", anchor="w")
        self.graph_amount_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))

        # Graph Mode dropdown menu
        self.graph_mode_option_menu = ctk.CTkOptionMenu(
            self,
            values=[
                "Visitors",
                "Average Visitors",
                "Highest Visitors",
                "Lowest Visitors",
            ],
            command=self.change_graph_mode_event,
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


class CustomDateEntry(DateEntry):
    def __init__(self, master=None, dates: List[str] = [], **kw):
        super().__init__(master, **kw)
        self.dates = dates

    def highlight_dates(self):
        for date in self.dates:
            dt = datetime.datetime.strptime(date, "%d-%m-%Y")
            id = self._calendar.calevent_create(dt, date, date)
            self._calendar.tag_config(date, background="#454545", foreground="white")


class MainFrameGraph(ctk.CTkFrame):
    def __init__(self, parent: App, width=0, side="left", expand=False, fill=None):
        super().__init__(parent)

        self.pack_propagate(False)
        self.pack(fill="both", expand=True, side=side, padx=10, pady=10)

        alku = time_to_epoch("27-3-2024 00:00:00")
        loppu = time_to_epoch("28-3-2024 00:00:00")

        try:
            db = database.SQLiteDBManager()
            # data = db.get_activity_between(1, alku, loppu)
            # data = db.get_avg_activity_between(1, alku, loppu)
            data2 = db.get_avg_activity_between_peridiocally(1, alku, loppu, 60 * 60)
        finally:
            db.__del__()

        x_values, y_values = zip(*data2)

        data = [
            (x_value, y_value) for x_value, y_value in data2
        ]  # Extract x and y values

        # Extract x values and convert them to dates
        x_values = [get_finnish_hour(x) for x, _ in data]

        # Extract y values
        y_values = [int(round(y)) for _, y in data]

        # figure = plt.Figure(figsize=(10,10), dpi=100)
        # figure_plot= figure.add_subplot(1, 1, 1)
        # figure_plot= figure.add_subplot(2, 2, 1)

        # fig, ax = plt.subplots(2, 1, figsize=(10,4))

        time = get_formatted_finnish_time(data[0][0])

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

        canvas.draw()

        self.draw_amount_graphs(
            4,
            [[1, 2, 3, 4], x_values, x_values, x_values],
            [[10, 20, 30, 40], y_values, y_values, y_values],
            [ax[0, 0], ax[0, 1], ax[1, 0], ax[1, 1]],
            [time, time, time, time],
            ["time", "time", "time", "time4"],
            ["visitors1", "visitors2", "visitors3", "visitors4"],
            ["red", "blue", "green", "orange"],
        )

        canvas.draw()

        fig, ax = plt.subplots(
            2, 1, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
        )
        canvas.figure = fig
        # fig2.set_constrained_layout_pads()
        # # canvas = FigureCanvasTkAgg(fig, master=self)
        # # canvas.get_tk_widget().pack(padx=10, pady=10)

        self.draw_amount_graphs(
            2,
            [x_values, x_values],
            [y_values, y_values],
            [ax[0], ax[1]],
            [time, time],
            ["time", "time2"],
            ["visitors1", "visitor2"],
            ["purple", "red"],
        )

        canvas.draw()

        fig, ax = plt.subplots(
            1, 1, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b"
        )
        canvas.figure = fig
        self.draw_amount_graphs(
            1,
            [x_values],
            [y_values],
            [ax],
            [time],
            ["time"],
            ["visitors1"],
            ["purple"],
            graph_type="line",
        )

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
        self.view_dropdown.add_option(option="Graphs", command=lambda: print("Graphs"))
        self.view_dropdown.add_option(
            option="Database", command=lambda: print("Databse")
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
