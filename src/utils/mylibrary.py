import datetime
from tkinter import messagebox
from typing import Callable, Any


import customtkinter as ctk
from PIL import Image
from tkcalendar import DateEntry

import utils

class CustomDateEntry(DateEntry):
    """Custom DateEntry widget

    :param master: widget master, defaults to None
    :param dates: list of unique dates following format "%d-%m-%Y", defaults to None
    :type dates: list[str] | None, optional
    :param showothermonthdays: whether to display the last days of the
        previous month and the first of the next month, defaults to False
    :type showothermonthdays: bool, optional

    - Note: showothermonthdays=False on default to avoid bug caused by highlighting
    dates outside current selected month.
    
    Bug origin:
    Creating a calevent for a date in the calendar changes the 'style' of date from
    ('normal'/'normal_om' or 'we'/'we_om') to 'tag_%s' (tag_name).
    - DateEntry -> Calendar -> Calendar._on_click()
    - tkcalendar.calendar_.py -> Calendar._on_click


    self._calendar.calevent_create(dt, "Has Data", tag) creates a calevent
    that changes style of the date

    Following check fails because style is always 'tag_%s' (tag_name)

    if style in ['normal_om.%s.TLabel' % self._style_prefixe,
    'we_om.%s.TLabel' % self._style_prefixe]:
        if label in self._calendar[0]:
            self._prev_month()
        else:
            self._next_month()

    This prevents the month from changing when a date outside of the currently
    shown month in the calendar is selected. Which means that the date will change
    but the month doesn't change with it.
    """

    def __init__(
        self, master=None, dates: list[str] | None = None, showothermonthdays=False, **kw
    ):

        if dates is None:
            dates = []
        super().__init__(master, showothermonthdays=showothermonthdays, **kw)
        self.dates = dates
        self.configure_size()
        self.bind("<Configure>", self.update_on_resize)  # Bind to the Configure event

    def drop_down(self):
        """
        Display or withdraw the drop-down calendar depending on its current state.

        Patched version of the DateEntry drop_down(). The patch stops calender
        from opening outside screen.
        """
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
            # - patch begin: Stop calendar from opening outside screen.
            current_screen_height = utils.get_monitor(x, y).height
            if y + self._top_cal.winfo_height() > current_screen_height - 70:
                y = self.winfo_rooty() - self._top_cal.winfo_height()
            # - patch end
            self._top_cal.geometry("+%i+%i" % (x, y))
            self._top_cal.deiconify()
            self._calendar.focus_set()
            self._calendar.selection_set(date)

    def configure_size(self, de_font_smallness=7, cal_font_smallness=12):
        """
        Configure DateEntry and Calendar font size.

        :param int de_font_smallness:
            DateEntry font reversed size. Increasing this value will decrease font size.
        :param int cal_font_smallness:
            Calendar font reversed size. Increasing this value will decrease font size.
        """
        # Calculate the font size based on the width of the widget
        width = self.winfo_width()
        font_size = int(width / de_font_smallness)
        cal_font_size = int(width / cal_font_smallness)

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
        """Removes all calevents and then adds all dates in 'dates' variable
        to the calendar as calevents"""
        self._calendar.calevent_remove("all")
        tag_name = "Data"
        for date in self.dates:
            dt = datetime.datetime.strptime(date, "%d-%m-%Y")
            self._calendar.calevent_create(dt, "Has Data", tag_name)

        self._calendar.tag_config(tag_name, background="#19a84c", foreground="white")

    def update_on_resize(self, event=None):
        """Handle the resize event for the widget."""
        self.configure_size()


class MyPopup(ctk.CTkToplevel):
    """
    Popup base class with functionality to add bottom frame with 
    """
    def __init__(
        self,
        parent,
        title: str,
        geometry="250x300",
        minsize=(250, 300),
        maxsize=(250, 300),
        **kwargs,
    ):
        super().__init__(parent, **kwargs)

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
        **kwargs,
    ) -> ctk.CTkButton:
        """
        Add bottom button to bottom frame

        If master is None self.bottom_frame is used.
        CTkButton **kwargs are usable
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
        **kwargs,
    ) -> ctk.CTkButton:
        """
        Add cancel button to a frame (bottom_frame if no master was given).
        The cancel button destroys the Popup.
        """
        return self.add_bottom_button(
            "Cancel",
            self._cancel_event,
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
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
        self.label.pack(side=ctk.TOP, padx=0, pady=(0, 2), fill=ctk.X)
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
        "Set menu values of the CTkOptionMenu"
        self.option_menu.configure(
            values=values, variable=ctk.StringVar(value=default_value)
        )

class InfoButton(ctk.CTkButton):
    def __init__(
        self,
        parent,
        *args,
        command=None,
        popup_title="Info",
        popup_info_text="Info text",
        **kwargs,
    ):
        """
        If command = None, popup_title and popup_info_text are used with messagebox.showinfo().
        """
        self.popup_title = popup_title
        self.popup_info_text = popup_info_text

        if not command:
            command = self.info_popup

        # Info image
        info_img = Image.open("src\\images\\information-button.png")
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

    def info_popup(self):
        messagebox.showinfo(self.popup_title, self.popup_info_text, master=self)
