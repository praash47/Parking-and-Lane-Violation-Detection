from misc.settings import *

from tkinter import *
from PIL import Image, ImageTk
import tkinter.font as tkFont

global thumbnail


class ConfirmDetect:
    def __init__(self, window, video, option):
        video_name_font = tkFont.Font(family=video_name_font_family, size=video_name_font_size,
                                      weight=video_name_font_weight)
        video_name_label = Label(window, text=video.name, font=video_name_font)
        video_name_label.grid(row=2, column=0)

        video_thumbnail_canvas = Canvas(width=video.width, height=video.height)
        video_thumbnail_canvas.grid(row=3, column=0)
        global thumbnail
        thumbnail = video.getThumbnail()
        video_thumbnail_canvas.create_image(0, 0, image=thumbnail, anchor=NW)
