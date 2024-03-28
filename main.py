import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

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
    graph_amount = '1'
    graph_mode = ["Visitors", "Visitors", "Visitors", "Visitors"]
    graph_type = ["Bar Graph", "Bar Graph", "Bar Graph", "Bar Graph"]

    def __init__(self, title, size=(1100, 580), min_size=(580, 400)):
        # def __init__(self, title, size=(1100, 580), min_size=(580, 400)):
        super().__init__()
        self.title(title)
        positions = self._calculte_positions(size)
        self.geometry(f"{int(size[0])}x{size[1]}+{positions[0]}+{positions[1]}")
        self.minsize(min_size[0], min_size[1])
        # self.attributes('-fullscreen', True)
        # self.iconbitmap('python.ico') # Choose app icon.

        # widgets
        # self.menu = Menu(self)
        ctk.set_appearance_mode("Light")
        self.configure(menu=Menu(self))

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = SideBar(self, 120)

        self.main_frame = MainFrame(self)

        # self.sub_menu = tk.Menu(tearoff=False)
        # self.sub_menu.pack()

        # self.menu_button = ttk.Menubutton(self, text= "Week days")
        # self.menu_button.pack()

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


class SideBar(ctk.CTkFrame):
    def __init__(self, parent: App, width):
        super().__init__(parent, width=width, corner_radius=0)
        # self.pack_propagate(False)  # Stop children from changing frame size
        # self.pack(side=side, expand=expand, fill=fill)
        # self.grid_propagate(False)
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(
            self, text="Graphs", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=10, pady=(20, 10))

        self.sidebar_button_1 = ctk.CTkButton(
            self, command=self.plot_bar_button_event, text="Plot Graph"
        )
        self.sidebar_button_1.grid(row=1, column=0, padx=10, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(
            self, command=self.sidebar_button_event, text="Open Calendar"
        )
        self.sidebar_button_2.grid(row=2, column=0, padx=10, pady=10)

        # self.sidebar_button_3 = ctk.CTkButton(self, command=self.sidebar_button_event)
        # self.sidebar_button_3.grid(row=3, column=0, padx=10, pady=10)




        # Graph amount label
        self.graph_amount_label = ctk.CTkLabel(self, text="Graph Amount:", anchor="w")
        self.graph_amount_label.grid(row=7, column=0, padx=10, pady=(20, 0))
        # Graph amount dropdown menu
        self.graph_amount_option_menu = ctk.CTkOptionMenu(
            self,
            values=["1", "2", "4"],
            command=self.change_graph_amount_event,
        )
        self.graph_amount_option_menu.grid(row=8, column=0, padx=10, pady=(10, 20))


        # Graph Mode label
        self.graph_mode_label = ctk.CTkLabel(self, text="Graph Mode:", anchor="w")
        self.graph_mode_label.grid(row=9, column=0, padx=10, pady=(20, 0))
        # Graph Mode dropdown menu
        self.graph_mode_option_menu = ctk.CTkOptionMenu(
            self,
            values=["Visitors", "Average Visitors", "Highest Visitors", "Lowest Visitors"],
            command=self.change_graph_mode_event,
        )
        self.graph_mode_option_menu.grid(row=10, column=0, padx=10, pady=(10, 20))

        # Graph Type label
        self.graph_type_label = ctk.CTkLabel(self, text="Graph Type:", anchor="w")
        self.graph_type_label.grid(row=11, column=0, padx=10, pady=(20, 0))
        # Graph Type dropdown menu
        self.graph_type_option_menu = ctk.CTkOptionMenu(
            self,
            values=["Bar Graph", "Line Graph"],
            command=self.change_graph_type_event,
        )
        self.graph_type_option_menu.grid(row=12, column=0, padx=10, pady=(10, 10))




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


class MainFrame(ctk.CTkFrame):
    def __init__(self, parent: App, width=0, side="left", expand=False, fill=None):
        super().__init__(parent)
        self.grid_propagate(False)  # Stop children from changing frame size
        self.grid(row=0, column=1, padx=10, pady=10, sticky="nesw")
        self.rowconfigure(0, weight=1)

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

        fig, ax = plt.subplots(2, 2, figsize=(20, 20), layout="constrained")
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
            bar_graph(
                x_values[i],
                y_values[i],
                ax[i],
                titles[i],
                x_labels[i],
                y_labels[i],
                colors[i],
            )

        # # for i in range(4):
        # #     for j in range(2)

        # # for index, (x_val, y_val, title, xlabel, ylabel, color) in enumerate(zip(x_values, y_values, titles, x_labels, y_labels, colors)):
        # #     bar_graph(x_val, y_val, ax[index // 2, index % 2], title, xlabel, ylabel, color)

        # bar_graph(
        #     x_values[0],
        #     y_values[0],
        #     ax[0],
        #     titles[0],
        #     x_labels[0],
        #     y_labels[0],
        #     colors[0],
        # )
        # bar_graph(
        #     x_values[1],
        #     y_values[1],
        #     ax[1],
        #     titles[1],
        #     x_labels[1],
        #     y_labels[1],
        #     colors[1],
        # )
        # bar_graph(
        #     x_values[2],
        #     y_values[2],
        #     ax[2],
        #     titles[2],
        #     x_labels[2],
        #     y_labels[2],
        #     colors[2],
        # )
        # bar_graph(
        #     x_values[3],
        #     y_values[3],
        #     ax[3],
        #     titles[3],
        #     x_labels[3],
        #     y_labels[3],
        #     colors[3],
        # )


class Menu(tk.Menu):
    def __init__(self, parent: App):
        super().__init__(parent)
        self.file_menu = FileMenu(self, tearoff=False)
        self.help_menu = HelpMenu(self, tearoff=False)


class FileMenu(tk.Menu):
    def __init__(self, parent: tk.Menu, tearoff):
        super().__init__(parent, tearoff=tearoff)
        parent.add_cascade(label="File", menu=self)
        self.add_command(label="Save", command=lambda: print("new"))


class HelpMenu(tk.Menu):
    def __init__(self, parent: tk.Menu, tearoff):
        super().__init__(parent, tearoff=tearoff)
        parent.add_cascade(label="Help", menu=self)
        self.add_command(label="How to", command=lambda: print("apua"))


# def motion_hover(event, annotation, ax, fig, bar):
#     annotation_visbility = annotation.get_visible()
#     if event.inaxes == ax:
#         is_contained, annotation_index = scatter.contains(event)
#         if is_contained:
#             data_point_location = scatter.get_offsets()[annotation_index['ind'][0]]
#             annotation.xy = data_point_location

#             text_label = '({0:.2f}, {0:.2f})'.format(data_point_location[0], data_point_location[1])
#             annotation.set_text(text_label)

#             annotation.get_bbox_patch().set_facecolor(cmap(norm(colors[annotation_index['ind'][0]])))
#             annotation.set_alpha(0.4)

#             annotation.set_visible(True)
#             fig.canvas.draw_idle()
#         else:
#             if annotation_visbility:
#                 annotation.set_visible(False)
#                 fig.canvas.draw_idle()


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


def bar_graph(x, y, ax, title=None, xlabel=None, ylabel=None, color=None):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.bar(x, y, color=color)


# def motion_hover(event, annotation):
#     annotation.get_visible()
#     if event.inaxes == ax:
#             is_contained, annotation_index = bar.contains(event)


def main():
    App("VisitorFlowTracker")


def main2():

    alku = time_to_epoch("23-3-2024 00:00:00")
    loppu = time_to_epoch("24-3-2024 00:00:00")
    print("alku: ", alku)
    print("loppu: ", loppu)

    try:
        db = database.SQLiteDBManager()
        # data = db.get_activity_between(1, alku, loppu)
        # data = db.get_avg_activity_between(1, alku, loppu)
        data2 = db.get_avg_activity_between_peridiocally(1, alku, loppu, 60 * 60)
    finally:
        db.__del__()

    print(epoch_to_time(1711223986))

    root = tk.Tk()
    fig, ax = plt.subplots()

    print("hei")
    root.title("VisitorFlowTracker")
    # root.title("VisitorTrendTracker")
    root.geometry("800x800")

    # Label
    title_label = ttk.Label(master=root, text="Paina tätä", font="Calibri 24")
    title_label.pack()

    frame = tk.Frame(root)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    frame.pack()
    # x, y = zip(*data2)

    x_values, y_values = zip(*data2)

    data = [(x_value, y_value) for x_value, y_value in data2]  # Extract x and y values

    # Extract x values and convert them to dates
    x_values = [get_finnish_hour(x) for x, _ in data]

    # Extract y values
    y_values = [int(round(y)) for _, y in data]

    bar = bar_graph(x_values, y_values, canvas, ax)

    annotation = ax.annotate(
        text="",
        xy=(0, 0),
        xytext=(15, 15),
        textcoords="offset points",
        bbox={"boxstyle": "round", "fc": "w"},
        arrowprops={"arrowstyle": "->"},
    )

    annotation.set_visible(False)

    fig.canvas.mpl_connect("motion_notify_event", motion_hover)

    # tk.Button(frame, text = "Bar graph", command=bar_graph(*zip(*data2), canvas, ax)).pack(pady=10)

    # input field

    # cal = DateEntry(root, width=12, year=2019, month=6, day=22,
    # background='darkblue', foreground='white', borderwidth=2)
    # cal.pack(padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
