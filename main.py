import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from CTkMenuBar import CTkMenuBar, CustomDropdownMenu

import pandas as pd

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
)
from utils import *


from tkcalendar import DateEntry

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
        # self.attributes('-fullscreen', True)
        # self.iconbitmap('python.ico') # Choose app icon.

        # widgets

        ctk.set_appearance_mode("Dark")

        self.menu = Menu(self)

        self.sidebar = SideBarGraph(self)
        self.main_frame = MainFrameGraph(self)

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

        # Graph Type dropdown menu
        self.graph_type_option_menu = ctk.CTkOptionMenu(
            self,
            values=["Bar Graph", "Line Graph"],
            command=self.change_graph_type_event,
        )
        self.graph_type_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))
        # Graph Type label
        self.graph_type_label = ctk.CTkLabel(self, text="Graph Type:", anchor="w")
        self.graph_type_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 0))

        # Graph Amount dropdown menu
        self.graph_amount_option_menu = ctk.CTkOptionMenu(
            self,
            values=["1", "2", "4"],
            command=self.change_graph_amount_event,
        )
        self.graph_amount_option_menu.pack(side=tk.BOTTOM, padx=10, pady=(10, 10))
        # Graph Amount label
        self.graph_amount_label = ctk.CTkLabel(self, text="Graph Amount:", anchor="w")
        self.graph_amount_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 0))

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
        self.graph_mode_label.pack(side=tk.BOTTOM, padx=10, pady=(10, 0))

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

        fig, ax = plt.subplots(2, 2, figsize=(20, 20), layout="constrained", facecolor="#2b2b2b")
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

        fig, ax = plt.subplots(1,1, figsize=(20,20), layout="constrained", facecolor="#2b2b2b")

        

        # annot = ax[0,0].annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
        #             bbox=dict(boxstyle="round", fc="black", ec="b", lw=2),
        #             arrowprops=dict(arrowstyle="->"))
        # annot.set_visible(False)

        # canvas.mpl_connect("motion_notify_event", lambda event: self.hover(self))

        # fig, ax = plt.subplots(2, 2, figsize=(20,20), layout="constrained")
        # fig.set_constrained_layout_pads()
        # canvas = FigureCanvasTkAgg(fig, master=self)
        # canvas.get_tk_widget().pack()

        # canvas.draw()

        # bar_graph(x_values,y_values,ax[0,1],f"{time}  0,1","xlabel 0,1", "ylabel 0,1", 'purple')
        # bar_graph(x_values,y_values,ax[0,0],f"{time}  0,0","xlabel 0,0", "ylabel 0,0", 'blue')
        # bar_graph(x_values,y_values,ax[1,1],f"{time}  1,1","xlabel 1,1", "ylabel 1,1", 'red')
        # bar_graph(x_values,y_values,ax[1,0],f"{time}  1,0","xlabel 1,0", "ylabel 1,0", 'green')

        # bar_figure
        # ax[0,0].set_title("Test")
        # ax[0,0].set_xlabel("x test")
        # ax[0,0].set_ylabel("y test")
        # ax[0,0].bar(x_values,y_values)

        # canvas.draw()

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
    ):
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

    def _bar_graph(self, x, y, ax, title=None, xlabel=None, ylabel=None, color=None):
        ax.set_facecolor("white")
        ax.set_title(title, color="white")
        ax.set_xlabel(xlabel, color="white")
        ax.set_ylabel(ylabel, color="white")
        ax.yaxis.set_tick_params(color="white", labelcolor="white")
        ax.xaxis.set_tick_params(color="white", labelcolor="white")
        for spine in ax.axes.spines.values():
            spine.set_edgecolor("grey")
        ax.bar(x, y, color=color)


class Menu(CTkMenuBar):
    def __init__(self, parent: App):
        super().__init__(parent, bg_color="#484848")
        self.file_button = self.add_cascade("File", text_color="white")
        self.view_button = self.add_cascade("View")
        self.help_button = self.add_cascade("Help")

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


if __name__ == "__main__":
    main()
