# Third Party Modules ##
from tkinter import *
import tkinter.font as tkFont

# Local Modules ##
from misc.settings import *

# Problem Creating Modules ##
from PIL import Image, ImageTk

global thumbnail


class ConfirmDetect:
    """ This is a sub module for just code minimization purposes.
    - Further Extension for selecting options in future if time gives.
    - Shows content on confirm detect window.
    """
    def __init__(self, window, video):
        video_name_font = tkFont.Font(family=video_name_font_family, size=video_name_font_size,
                                      weight=video_name_font_weight)
        video_name_label = Label(window, text=video.name, font=video_name_font)
        video_name_label.grid(row=2, column=0)

        video_thumbnail_canvas = Canvas()
        video_thumbnail_canvas.grid(row=3, column=0)
        global thumbnail
        thumbnail = video.getThumbnail(non_tk=True)

        # scale down to 40% of original size.
        width = int(thumbnail.shape[1] * video_scale_percent / 100)
        height = int(thumbnail.shape[0] * video_scale_percent / 100)
        dim = (width, height)

        # resize image
        thumbnail = cv2.resize(thumbnail, dim, interpolation=cv2.INTER_AREA)
        thumbnail = ImageTk.PhotoImage(Image.fromarray(thumbnail))
        video_thumbnail_canvas.configure(width=width, height=height)
        video_thumbnail_canvas.create_image(0, 0, image=thumbnail, anchor=NW)
