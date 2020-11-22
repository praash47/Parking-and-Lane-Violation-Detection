# A SPECIFIC detector and tracker for parking
# YOLO version: 3
# Tracker: MOSSE

# Third Party Modules ##
import cv2

# Local Modules ##
from misc.settings import *



class DetectorTracker:
    def __init__(self, detection_object):
        self.object = detection_object

        # MOTION DETECTOR #
        self.motion_detector_frame1 = None
        self.motion_detector_frame2 = None
        self.motion_detected_time = None
        self.disable_motion_detector = False

        # TRACKING #
        self.tracker = cv2.TrackerMOSSE_create()
        self.tracker_initialized = False
        self.tracked_x1 = None
        self.tracked_x2 = None
        self.tracked_y1 = None
        self.tracked_y2 = None

    def motionDetector(self):
        # Checks whether motion is detected in the frame or not. #
        if self.motion_detector_frame1 is None and self.motion_detector_frame2 is None:
            self.motion_detector_frame1 = self.object.roi.frame
        elif self.motion_detector_frame2 is None:
            self.motion_detector_frame2 = self.object.roi.frame
        else:
            # apply frame difference to check if motion is detected #

            frame_difference = cv2.absdiff(self.motion_detector_frame1, self.motion_detector_frame2)
            grayed_difference = cv2.cvtColor(frame_difference, cv2.COLOR_BGR2GRAY)
            blurred_difference = cv2.GaussianBlur(grayed_difference, detector_blur_output_size, detector_blur_size)

            threshold_received, threshold_frame = cv2.threshold(blurred_difference, detector_threshold_output_size,
                                                                detector_threshold_thresh, cv2.THRESH_BINARY)
            dilated_frame = cv2.dilate(threshold_frame, None, iterations=detector_dilate_iterations)
            contours, hierarchy = cv2.findContours(dilated_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            moving_object_count = 0
            # contours are the list of moving objects in frame.
            for contour in contours:
                moving_object_count += 1

            self.motion_detector_frame1 = self.motion_detector_frame2
            self.motion_detector_frame2 = None

            self.object.yolo.disabled = True

            if moving_object_count > 0:
                return True, moving_object_count
        return False, 0

    def trackObject(self):
        if not self.tracker_initialized:
            # initialization of the tracker
            if self.object.yolo.bounding_box:
                bounding_box = self.object.yolo.bounding_box[0]
                x1 = bounding_box[0]
                y1 = bounding_box[1]
                x2 = x1 + bounding_box[2]
                y2 = y1 + bounding_box[3]
                self.tracker.init(self.object.roi.frame, (x1, y1, x2, y2))
                self.object.yolo.disabled = True
                self.tracker_initialized = True

        else:
            # update the tracked bounding box of the object
            (track_successful, object_track_box) = self.tracker.update(self.object.roi.frame)

            if track_successful:
                (tracked_x, tracked_y, tracked_w, tracked_h) = [int(param) for param in object_track_box]
                self.tracked_x1 = tracked_x
                self.tracked_y1 = tracked_y
                self.tracked_x2 = tracked_x + tracked_w
                self.tracked_y2 = tracked_y + tracked_h
                cv2.rectangle(self.object.roi.frame, (tracked_x, tracked_y), (self.tracked_x2, self.tracked_y2),
                              tracker_rectangle_color, tracker_rectangle_thickness)
