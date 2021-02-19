"""
Parking Violation Utility Logic
"""
# System Modules ##
import time
# Third Party Modules ##
from tkinter import messagebox

# Local Modules ##
from misc.settings import *
from misc.variables import *

global prev_coordinates, rest_start_time


def moving(prevbbox):
    """
    :param: prevbbox: Previous bounding boxes numpy 2D array
    :rtype: boolean
    :returns: True if according to previous bounding boxes, object is found to be moving
    """
    std = np.std(prevbbox, axis=0)  # compute standard deviation along columns
    px1std, py1std, px2std, py2std = int(std[0]), int(std[1]), int(std[2]), int(std[3])

    # if any column std deviation > moving_std_deviation_threshold, then object is moving
    if px1std >= moving_std_deviation_threshold or px2std >= moving_std_deviation_threshold or py1std >= \
            moving_std_deviation_threshold or py2std >= moving_std_deviation_threshold:
        return True
    return False


def checkViolation(detection_object):
    """
    This function basically sets a timer for some n seconds and if the object remains not moving for that n seconds,
    then it calls the violation function.

    Also, this function keeps track of previous 10 coordinates.
    """
    global prev_coordinates, rest_start_time

    # first of all our prev_coordinate is list.
    if type(prev_coordinates) is list:
        prev_coordinates.append([detection_object.detector_tracker.tracked_x1,
                                 detection_object.detector_tracker.tracked_y1,
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

        # save current time in curr_time
        curr_time = time.time()

        # first time non-moving object is detected, the time is logged.
        if rest_start_time is None:
            rest_start_time = time.time()

        # how much time_elapsed from the time object first started to be in rest.
        time_elapsed = curr_time - rest_start_time

        # if time_elapsed >= n seconds and image of violation hasn't been written then call self.violation
        if time_elapsed >= parking_violation_report_time and not detection_object.violation_img_written:
            violation(detection_object)
    else:
        rest_start_time = None  # if bounding box moved, then reset the rest_start_time


def violation(detection_object):
    """
    triggered when a violation occurs
    :param detection_object: parking violation object
    """
    # show warning
    messagebox.showwarning(violation_warning_box_title, violation_warning_box_message)

    # write violator image
    cv2.imwrite(parking_violation_save_directory + violation_save_name_prefix + str(int(time.time())) +
                parking_violation_save_extension, detection_object.roi.frame)
    detection_object.violation_img_written = True

    # Append in violation log: to be extended in the future
    detection_object.violation_log.append(time.time())
