# Third Party Modules ##
import numpy as np
import time
from tkinter import messagebox

# Local Modules ##
from misc.settings import *
from misc.variables import *


global prev_coordinates, rest_start_time
rest_start_time = None
prev_coordinates = []


def moving(prevbbox):
    std = np.std(prevbbox, axis=0)  # along columns standard deviation
    px1std, py1std, px2std, py2std = int(std[0]), int(std[1]), int(std[2]), int(std[3])

    # if any std deviation > moving_std_deviation_threshold, then object is moving
    if px1std >= moving_std_deviation_threshold or px2std >= moving_std_deviation_threshold or py1std >= \
            moving_std_deviation_threshold or py2std >= moving_std_deviation_threshold:
        return True
    return False


def checkViolation(detection_object):
    global prev_coordinates, rest_start_time

    # first of all our prev_coordinate is list.
    if type(prev_coordinates) is list:
        prev_coordinates.append([detection_object.detector_tracker.tracked_x1, detection_object.detector_tracker.tracked_y1,
                                 detection_object.detector_tracker.tracked_x2,
                                 detection_object.detector_tracker.tracked_y2])

    # it's then converted into numpy array
    prev_coordinates = np.array(prev_coordinates)

    # put current tracked coordinates into curr_bbox
    curr_bbox = np.array([[detection_object.detector_tracker.tracked_x1, detection_object.detector_tracker.tracked_y1,
                           detection_object.detector_tracker.tracked_x2, detection_object.detector_tracker.tracked_y2]])

    # also, put into the previous element array, now rows are 11 in number
    prev_coordinates = np.append(prev_coordinates, curr_bbox, axis=0)  # axis = 0 specifies horizontal placement

    # so, now delete the first row to make number of rows back to 10
    if prev_coordinates.shape[0] >= 10:
        prev_coordinates = np.delete(prev_coordinates, 0, 0)  # delete the first one co-ordinates to make size
    # limited to 10 elements.

    # if object is not moving then
    if not moving(prev_coordinates):
        print(moving_not_message)

        # save current time in curr_time
        curr_time = time.time()
        print(curr_time)

        # first time non-moving object is detected, the time is logged.
        if rest_start_time is None:
            rest_start_time = time.time()
        print(rest_start_time)

        # how much time_elapsed from the time object first started to be in rest.
        time_elapsed = curr_time - rest_start_time
        print(time_elapsed)

        # if time_elapsed >= n seconds and image of violation hasn't been written then caall self.violation
        if time_elapsed >= parking_violation_report_time and not detection_object.violation_img_written:
            violation(detection_object)
    else:
        print(moving_message)
        rest_start_time = None  # if bounding box moved, then reset the rest_start_time


def violation(detection_object):
    messagebox.showwarning(violation_warning_box_title, violation_warning_box_message)

    # save violator vehicle #
    # TODO: Violation Log for Parking
    # commented the down one because it doesn't yield proper outputs.
    # cropped_vehicle_frame = detection_object.roi.frame[
    #                         detection_object.detector_tracker.tracked_y1:detection_object.detector_tracker.tracked_y2,
    #                         detection_object.detector_tracker.tracked_x1:detection_object.detector_tracker.tracked_x2]
    cv2.imwrite(parking_violation_save_directory + violation_save_name_prefix + str(int(time.time())) + parking_violation_save_extension,
                detection_object.roi.frame)
    detection_object.violation_img_written = True
    detection_object.violation_log.append(time.time())
