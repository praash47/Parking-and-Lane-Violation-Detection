"""
Utility functions required for the program
"""
# Third Party Modules ##
import tkinter.font as tkFont

from misc.settings import *
# Local Module Imports ##
from misc.variables import *

# Problem Creating Modules #
from PIL import ImageTk, Image

# We have to make this global otherwise this variable won't work.
global tkinter_readable_frame


def generateTopBottomBar(window=None, title=app_title, bottom_row=4, n_columns=1):  # bottom_row specifies
    """
    Generates a top bar with title text at the top of the window and bottom bar at the bottom of the window.

    :param window: Window in which to generate
    :param title: title of the top bar
    :param bottom_row: to generate bottom bar in designated row
    :param n_columns: to span the bar over multiple columns
    """

    # The bar that resides on top and bottom of each window
    top_font_style = tkFont.Font(family=top_font_family, size=top_font_size)
    bottom_font_style = tkFont.Font(family=bottom_font_family, size=bottom_font_size)

    # TOP BAR #
    window.app_title_label = Label(window, text=title, font=top_font_style, bg=theme_top_bottom_bar_color,
                                   fg=theme_top_bottom_bar_text_color, activebackground=theme_bg_color)
    window.app_title_label.grid(row=0, column=0, columnspan=n_columns, sticky=top_bottom_sticky_direction,
                                ipadx=top_bottom_inner_padding_x, ipady=top_bottom_inner_padding_y)

    # BOTTOM BAR #
    window.by_text_label = Label(window, text=by_text, font=bottom_font_style, bg=theme_top_bottom_bar_color,
                                 fg=theme_top_bottom_bar_text_color, activebackground=theme_bg_color)

    window.by_text_label.grid(row=bottom_row, column=0, columnspan=n_columns, sticky=top_bottom_sticky_direction,
                              ipadx=top_bottom_inner_padding_x, ipady=top_bottom_inner_padding_y)


def generateSubtitleBar(window="", title="", n_columns=1):
    """
    Generates a subtitle bar with title under the title bar

    :param window: window to generate the subtitle bar on
    :param title: title of the subtitle
    :param n_columns: to span the bar over multiple columns
    """
    # n_columns sames as top-bottom bar
    # The bar that resides below the top bar
    window.subtitle_label = Label(window, text=title, font=subtitle_font_size, bg=subtitle_bg_color,
                                  fg=subtitle_text_color, activebackground=theme_bg_color)
    window.subtitle_label.grid(row=1, column=0, columnspan=n_columns, sticky=subtitle_sticky_direction,
                               padx=subtitle_inner_pad_x, ipady=subtitle_inner_pad_y)


def writeNewFrame(frame, detection_object):
    """
    Writes opencv frame to the video canvas

    :param frame: opencv frame to write
    :param detection_object: Parking or Lane Violation object
    """
    # writes tkinter readable image into our canvas
    if frame is not None:
        # drawing canvas for placing video
        global tkinter_readable_frame
        tkinter_readable_frame = ImageTk.PhotoImage(Image.fromarray(frame))
        detection_object.video_canvas.create_image(0, 0, image=tkinter_readable_frame, anchor=NW)


# PARKING VIOLATION FUNCTIONS #
def isDesiredObject(objects):
    """
    :param objects: object to check
    :return: True only if the object passed is in our desired list
    """
    # filter only Truck, Bus, Motorbike and Car for YOLOv3 in Parking module.

    # Parking violation module is only able to work with one vehicle.
    if len(objects) == 1:
        if objects[0] in desired_objects:
            return True
    return False
