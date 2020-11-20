from functionality.functions import *
from misc.settings import *
from misc.variables import *

from tkinter import *


class AdditionalGUILane:
    def __init__(self, detection_object):
        self.object = detection_object
    #     self.drawROISlider()
    #
    # def drawROISlider(self):
    #     self.object.roi_sliders_frame = LabelFrame(self.object.window, text=roi_sliders_title, width=roi_coords_width)
    #     self.object.roi_sliders_frame.grid(row=2, column=1, ipadx=roi_coords_inner_padding_x,
    #                                        ipady=roi_coords_inner_padding_y, pady=(roi_coords_top_padding,
    #                                                                                roi_coords_bottom_padding))
    #     self.object.roi_sliders_frame.pack_propagate(0)
    #
    #     self.object.roi_slider_x1_label = Label(self.object.roi_sliders_frame, text=roi_slider_x1_title)
    #     self.object.roi_slider_x1 = Scale(self.object.roi_sliders_frame, from_=0, to=self.object.video.width,
    #                                       orient=slider_default_orientation, tick_interval=roi_slider_tick_interval)
    #     self.object.roi_slider_x1.set(0)
    #     self.object.roi_slider_x1_label.grid(row=1, column=0, padx=roi_coords_label_padding_x,
    #                                          pady=roi_coords_label_padding_y)
    #     self.object.roi_slider_x1.grid(row=1, column=1)
