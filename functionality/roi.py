from misc.settings import *
from misc.variables import *
from functionality.functions import *

from threading import Timer
from tkinter import *
from tkinter import messagebox
import cv2


class RegionOfInterest:
    def __init__(self, detection_object):
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        self.object = detection_object
        self.frame = None

        self.confirm_box_served = False
        self.enter_loop = True
        self.have_roi = False

    def draw(self):
        # draw only if values are present, enter_loop is true and frame is present
        if self.x1 is not None and self.x2 is not None and self.y1 is not None and self.y2 is not \
                None and self.enter_loop and self.object.frame is not None and not self.have_roi:
            self.object.frame = cv2.rectangle(self.object.frame, (self.x1, self.y1), (self.x2, self.y2),
                                                  roi_rectangle_color, roi_rectangle_thickness)  # draw rectangle
            self.frame = self.object.frame[self.y1:self.y2, self.x1:self.x2]  # extract frame of size of roi

            # ASK CONFIRMATION #
            if not self.confirm_box_served:
                writeNewFrame(self.object.frame, self.object)
                self.enter_loop = messagebox.askyesno(roi_confirm_box_title, roi_confirm_box_message_first_half +
                                                      roi_coords_title + "? (" +
                                                      str(self.x1) + ", " + str(self.x2) + ") (" + str(self.y1)
                                                      + ", " + str(self.y2) + ")")

                if self.enter_loop:
                    self.confirm_box_served = True
                else:
                    self.enter_loop = False
                    self.confirm_box_served = False
        elif self.have_roi:
            self.object.frame = cv2.rectangle(self.object.frame, (self.x1, self.y1), (self.x2, self.y2),
                                              roi_rectangle_color, roi_rectangle_thickness)  # draw rectangle
            self.frame = self.object.frame[self.y1:self.y2, self.x1:self.x2]  # extract frame of size of roi

    def getRoiCoords(self, have_roi=False):
        if not have_roi:
            self.enter_loop = True
            x1 = self.object.roi_coords_x1.get()
            y1 = self.object.roi_coords_y1.get()
            x2 = self.object.roi_coords_x2.get()
            y2 = self.object.roi_coords_y2.get()

            # CO-ORDINATES VALIDATION #
            # if not empty input boxes
            if len(x1) != 0 and len(y1) != 0 and len(x2) != 0 and len(y2) != 0:
                x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)

                # clear all boxes after input
                self.object.roi_coords_x1.delete(0, 'end')
                self.object.roi_coords_y1.delete(0, 'end')
                self.object.roi_coords_x2.delete(0, 'end')
                self.object.roi_coords_y2.delete(0, 'end')

                # if initial coordinates > 0 and final less than video width, proceed
                if x1 >= 0 and y1 >= 0 and x2 <= self.object.video.width and y2 <= self.object.video.height:
                    # ignore a point drawing type coordinates or line drawing
                    # if x1 == x2 or y1 == y2, user is trying to draw a point or line
                    if x1 != x2 and y1 != y2:
                        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
                        parking_status_message = Label(self.object.roi_coords_frame, text=success, fg=default_success_color)  # success

                    else:
                        # print line or point error
                        parking_status_message = Label(self.object.roi_coords_frame, text=error_same_value, fg=default_error_color)
                        self.enter_loop = False
                else:
                    # print invalid coordinates
                    parking_status_message = Label(self.object.roi_coords_frame, text=error_invalid_value, fg=default_error_color)
                    self.enter_loop = False
            else:
                # print some or all empty values
                parking_status_message = Label(self.object.roi_coords_frame, text=error_no_value, fg=default_error_color)
                self.enter_loop = False
            parking_status_message.grid(row=3, column=0, padx=parking_status_message_padding_x, pady=parking_status_message_padding_y)

            # after 3 seconds, destroy the error or success message
            timer = Timer(roi_status_message_destroy_time, lambda: self.msgDestroy(parking_status_message))
            timer.start()
        else:
            self.have_roi = True


    def msgDestroy(self, msg):
        msg.destroy()
