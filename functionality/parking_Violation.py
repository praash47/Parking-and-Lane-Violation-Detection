# Local Modules ##
from functionality.parking.detector_Tracking import *
from functionality.parking.parking_Violation_Logic import *
from functionality.parking.yolo import *
from functionality.roi import *
from functionality.video import *
from gui.additional_GUI_Parking import *
from gui.confirm_Detect import *
from misc.settings import *
from misc.variables import *


# this is a tkinter bug that tkinter images must be global.
global thumbnail


class ParkingViolation:
    def __init__(self, video_path, start_frame=None):
        # CONFIRMATION WINDOW #
        # show thumbnail and video, ask for confirmation [window] #
        self.detect_ask_window = Tk()
        self.detect_ask_window.title(option1 + " - " + app_title)

        # Video, YOLO and Region of Interest Initialization #
        self.video = Video(video_path)
        self.yolo = YOLO(self)  # YOLO object is a YOLOv3 algorithm
        self.roi = RegionOfInterest(self)

        # Motion Detector and Tracker Initialization #
        self.detector_tracker = DetectorTracker(self)

        # OpenCV Initializations #
        self.frame_received = ''
        self.frame = ''

        # Tkinter Initializations #
        self.window = ''
        self.additional_gui = ''
        self.video_canvas = ''
        self.menu_bar = ''
        self.option_menu = ''

        # Pausing features initialization #
        self.pause_video = False
        self.pause_frame = start_frame  # frame in which last time we paused.

        # Violation Features #
        self.violation_img_written = False
        self.violation_log = []
        self.reset_violation_btn = None
        self.new_object = None

        if not start_frame:
            generateTopBottomBar(window=self.detect_ask_window, title=self.detect_ask_window.title(),
                                 bottom_row=parking_window_bottom_row)
            generateSubtitleBar(window=self.detect_ask_window, title='Confirm Detect?')

            # confirm detect window is popped by this
            ConfirmDetect(window=self.detect_ask_window, video=self.video, option=option1)

            detect_btn_font = tkFont.Font(family=detect_btn_font_family, size=detect_btn_font_size)
            detect_btn = Button(self.detect_ask_window, text="Detect", bg=detect_btn_color,
                                activebackground=detect_btn_active_color,
                                command=self.startDetectionWindow, font=detect_btn_font)
            detect_btn.grid(row=4, column=0, ipadx=load_video_inner_padding_x, ipady=load_video_inner_padding_y,
                            pady=load_video_outer_padding_y)

            self.detect_ask_window.mainloop()

        else:
            self.startDetectionWindow()

    def startDetectionWindow(self):
        self.detect_ask_window.destroy()
        self.detect_ask_window.quit()

        # our main detection window
        self.window = Tk()
        self.window.title(option1 + ' - ' + app_title)
        self.menu_bar = Menu(self.window)
        self.window.config(menu=self.menu_bar)
        self.window.resizable(0, 0)

        # create the video and it's controls
        self.video.createCanvasControls(detection_object=self)
        self.menuBar()
        self.additional_gui = AdditionalGUIParking(self)  # Additional region of interest enter box

        generateTopBottomBar(window=self.window, title=app_title, bottom_row=parking_window_bottom_row,
                             n_columns=2)
        generateSubtitleBar(window=self.window, title=option1, n_columns=2)

        self.detectAndTrack()

        self.window.mainloop()

    def detectAndTrack(self):
        # Our main looping function
        self.frame_received, self.frame = self.updateFrame()

        self.roi.draw()

        # if cropped frame is already received via roi, proceed
        if self.roi.frame is not None and self.roi.enter_loop:
            # if motion is detected in frame then
            if self.detector_tracker.motion_detected_time and not self.detector_tracker.disable_motion_detector:
                # take the current time
                curr_time = time.time()

                # and if the time exceeds n seconds then, activate the yolo detector once
                if (curr_time - self.detector_tracker.motion_detected_time) > parking_after_motion_check_seconds:
                    self.yolo.disabled = False
                    self.yolo.detector()
                    self.checkIfObjectPresentAndAct()

            # if object is present in first yolo call, disable yolo then, start tracking right away.
            if self.roi.frame is not None and not self.yolo.disabled:
                self.yolo.detector()
                self.checkIfObjectPresentAndAct()

            # if motion detector is not disabled;
            elif not self.detector_tracker.disable_motion_detector:
                motion_detected, moving_object_count = self.detector_tracker.motionDetector()

                # if motion detected then save the time
                if motion_detected and moving_object_count > 0 and not self.detector_tracker.motion_detected_time:
                    self.detector_tracker.motion_detected_time = time.time()
            else:
                # else just track the object
                self.detector_tracker.trackObject()

        # if tracking co-ordinates are set then check for violation
        if self.detector_tracker.tracked_x1 and self.detector_tracker.tracked_y1 and self.detector_tracker.tracked_x2 and \
                self.detector_tracker.tracked_y2:
            checkViolation(self)

        # After violation occurs show reset button.
        if len(self.violation_log) > 0 and not self.reset_violation_btn:
            self.additional_gui.showResetButton()

        writeNewFrame(frame=self.frame, detection_object=self)

        self.window.after(parking_window_update_time, self.detectAndTrack)

    def updateFrame(self):
        # try to open the video
        if self.video.cap.isOpened():
            # if pause_frame has been set, then to continue from paused frame.
            if self.pause_frame is not None:
                self.video.cap.set(cv2.CAP_PROP_POS_FRAMES, self.pause_frame)
                self.pause_frame = None  # empty the pause frame again after reading

            frame_received, frame = self.video.cap.read()

            # if video is paused
            if self.pause_video:
                self.pause_frame = self.video.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1  # capture the paused frame
                cv2.waitKey(-1)  # cv2 pause function
                return None, None

            # frame is properly received and video is not paused
            elif frame_received and not self.pause_video:
                return frame_received, frame

            # frame is not received from video
            else:
                return frame_received, None

        else:
            # video is not opened
            return None, None

    def checkIfObjectPresentAndAct(self):
        # if a bounding box is detected then start tracking object
        if self.yolo.bounding_box and isDesiredObject(self.yolo.class_names):
            self.startTracking()

        # no object is seen ,then stop tracking
        else:
            self.stopTracking()

    def startTracking(self):
        # disable yolo and start tracker
        self.detector_tracker.trackObject()
        self.detector_tracker.disable_motion_detector = True
        self.yolo.disabled = True
        self.yolo.bounding_box = []

    def stopTracking(self):
        # reset the last motion detected time and disable yolo.
        self.detector_tracker.motion_detected_time = None
        self.yolo.disabled = True

    def menuBar(self):
        # FILE MENU *
        file_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label=file_menu_title, menu=file_menu)
        file_menu.add_command(label=file_menu_exit_option_title, command=self.quitProgram)

        # OPTIONS MENU *
        self.option_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label=option_menu_title, menu=self.option_menu)
        self.option_menu.add_command(label=disable_yolo_option, command=self.yolo.disable)

    def reset(self):  # NOT WORKING #
        # TODO: Fix reset button
        self.reset_violation_btn.destroy()
        self.window.destroy()
        self.window.quit()

        self.new_object = 'Yes'

    def quitProgram(self):
        self.window.destroy()
        self.window.quit()
