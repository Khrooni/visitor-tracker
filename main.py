import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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


class App(tk.Tk):
    def __init__(self, title, size, min_size):
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(min_size[0],min_size[1])

        # widgets
        self.menu = Menu(self)

        self.configure(menu=self.menu)
        # run
        self.mainloop()

class Menu(tk.Menu):
    def __init__(self, parent: App):
        super().__init__(parent)
        self.file_menu = FileMenu(self,tearoff=False)


class FileMenu(tk.Menu):
    def __init__(self, parent: tk.Menu, tearoff):
        super().__init__(parent, tearoff=tearoff)
        parent.add_cascade(label = "File", menu=self)
        self.add_command(label = 'New', command = lambda: print("new"))
        
        
        

        



def bar_graph(x, y, canvas, ax):
    ax.clear()
    bar = plt.bar(x, y)
    canvas.draw()
    return bar


# def motion_hover(event, annotation):
#     annotation.get_visible()
#     if event.inaxes == ax:
#             is_contained, annotation_index = bar.contains(event)

def main():
    App("VisitorFlowTracker", (800,700), (600,600))
    
    # menu = tk.Menu(App)
    # file_menu = tk.Menu(menu)

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
