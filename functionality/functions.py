# Third Party Modules ##
from tkinter import *
import tkinter.font as tkFont
from PIL import ImageTk, Image

# Local Module Imports ##
from misc.variables import *
from misc.settings import *

# We have to make this global otherwise this variable won't work.
global tkinter_readable_frame


def generateTopBottomBar(window=None, title=app_title, bottom_row=4, n_columns=1):  # bottom_row specifies
    # where the Bottom Bar lies. (required for tkinter), n_columns allows us to add multiple columns in
    # middle section of our program.

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


def generateSubtitleBar(window="", title="", n_columns=1):  # n_columns sames as top-bottom bar
    # The bar that resides below the top bar
    window.subtitle_label = Label(window, text=title, font=subtitle_font_size, bg=subtitle_bg_color,
                                  fg=subtitle_text_color, activebackground=theme_bg_color)
    window.subtitle_label.grid(row=1, column=0, columnspan=n_columns, sticky=subtitle_sticky_direction,
                               padx=subtitle_inner_pad_x, ipady=subtitle_inner_pad_y)


def writeNewFrame(frame, detection_object):
    # writes tkinter readable image into our canvas
    if frame is not None:
        # drawing canvas for placing video
        global tkinter_readable_frame
        tkinter_readable_frame = ImageTk.PhotoImage(Image.fromarray(frame))
        detection_object.video_canvas.create_image(0, 0, image=tkinter_readable_frame, anchor=NW)


# PARKING VIOLATION FUNCTIONS #
def isDesiredObject(objects):
    # filter only Truck, Bus, Motorbike and Car for YOLOv3 in Parking module.

    # this condition is specially for one object structure of parking violation
    if len(objects) == 1:
        if objects[0] in desired_objects:
            return True
    return False
