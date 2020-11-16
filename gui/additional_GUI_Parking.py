from functionality.functions import *

from tkinter import *


class AdditionalGUIParking:
    def __init__(self, parking_object):
        self.object = parking_object
        self.roiCoordsFrame()

    def roiCoordsFrame(self):
        self.object.roi_coords_frame = LabelFrame(self.object.window, text=roi_coords_title,
                                                  width=roi_coords_width)
        self.object.roi_coords_frame.grid(row=2, column=1, ipadx=roi_coords_inner_padding_x,
                                          ipady=roi_coords_inner_padding_y, pady=(roi_coords_top_padding, roi_coords_bottom_padding))
        self.object.roi_coords_frame.pack_propagate(0)

        video_size_label_text = video_size_label_title + str(int(self.object.video.width)) + 'x' + str(
            int(self.object.video.height))
        self.object.video_size_label = Label(self.object.roi_coords_frame, text=video_size_label_text)
        self.object.video_size_label.grid(row=0, column=1, padx=roi_coords_btn_padding_x)

        self.object.roi_coords_x1_label = Label(self.object.roi_coords_frame, text=roi_coords_x1_title)
        self.object.roi_coords_x1 = Entry(self.object.roi_coords_frame, width=roi_coords_x1_width)
        self.object.roi_coords_x1_label.grid(row=1, column=0, padx=roi_coords_label_padding_x,
                                             pady=roi_coords_label_padding_y)
        self.object.roi_coords_x1.grid(row=1, column=1)

        self.object.roi_coords_y1_label = Label(self.object.roi_coords_frame, text=roi_coords_y1_title)
        self.object.roi_coords_y1_label.grid(row=1, column=2, padx=roi_coords_label_padding_x,
                                             pady=roi_coords_label_padding_y)
        self.object.roi_coords_y1 = Entry(self.object.roi_coords_frame, width=roi_coords_y1_width)
        self.object.roi_coords_y1.grid(row=1, column=3)

        self.object.roi_coords_x2_label = Label(self.object.roi_coords_frame, text=roi_coords_x2_title)
        self.object.roi_coords_x2_label.grid(row=2, column=0, padx=roi_coords_label_padding_x,
                                             pady=roi_coords_label_padding_y)
        self.object.roi_coords_x2 = Entry(self.object.roi_coords_frame, width=roi_coords_x2_width)
        self.object.roi_coords_x2.grid(row=2, column=1)

        self.object.roi_coords_y2_label = Label(self.object.roi_coords_frame, text=roi_coords_y2_title)
        self.object.roi_coords_y2_label.grid(row=2, column=2, padx=roi_coords_label_padding_x,
                                             pady=roi_coords_label_padding_y)
        self.object.roi_coords_y2 = Entry(self.object.roi_coords_frame, width=roi_coords_y2_width)
        self.object.roi_coords_y2.grid(row=2, column=3)

        self.object.roi_coords_btn = Button(self.object.roi_coords_frame, text=roi_coords_btn_title,
                                            bg=roi_coords_btn_color,
                                            activebackground=roi_coords_btn_active_color,
                                            command=self.object.roi.getRoiCoords)
        self.object.roi_coords_btn.grid(row=4, column=0, padx=roi_coords_btn_padding_x)

    def showResetButton(self):
        self.object.reset_violation_btn = Button(self.object.window, text=reset_violation_btn_title,
                                                 bg=reset_violation_btn_color,
                                                 activebackground=reset_violation_btn_active_color,
                                                 command=self.object.reset)
        self.object.reset_violation_btn.grid(row=3, column=1, sticky=reset_violation_btn_sticky)
