# Third Party Modules ##
import numpy as np
import yolo.object_tracker as obtk

# Local Modules ##
from functionality.lane.vehicles import *
from functionality.lane.lane_Processing import *
from functionality.lane.lane_Violation_Logic import *
from functionality.video import *
from functionality.functions import *
from gui.additional_GUI_Lane import *
from gui.confirm_Detect import *
from functionality.roi import *
from misc.variables import *


global thumbnail


class LaneViolation:
    def __init__(self, video_path):
        # show thumbnail and video, ask for confirmation [window] #
        self.detect_ask_window = Tk()
        self.detect_ask_window.title(option2 + " - " + app_title)

        # Video Initialization #
        self.video = Video(video_path)

        # OpenCV Initializations #
        self.frame_received = ''
        self.frame = ''

        # Tkinter Initializations #
        self.window = ''
        self.additional_gui = ''
        self.video_canvas = ''
        self.menu_bar = ''

        # Pausing features initialization #
        self.pause_video = False
        self.pause_frame = None  # frame in which last time we paused.

        # Lanes and Tracker initialization #
        #self.tracker = obtk.DetectorTracker(self)
        self.lanes = Lanes(self)

        # ROI coordinates #
        self.roi = RegionOfInterest(self)
        self.road_roi_left = None # road roi
        self.road_roi_right = None # road roi

        # Vehicles Object initialization #
        self.vehicles = Vehicles(self)

        # Frame number counter #
        self.frame_count = 0

        generateTopBottomBar(window=self.detect_ask_window, title=self.detect_ask_window.title(),
                             bottom_row=lane_window_bottom_row)
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

    def startDetectionWindow(self):
        self.detect_ask_window.destroy()
        self.detect_ask_window.quit()

        self.roiSpecification()

        self.lanes.houghTransform()
        self.lanes.seperateLaneLines()
        self.lanes.seperateLaneAreas()

        # our main detection window
        self.window = Tk()
        self.window.title(option2 + ' - ' + app_title)
        self.menu_bar = Menu(self.window)
        self.window.config(menu=self.menu_bar)
        self.window.resizable(0, 0)

        # create the video and it's controls
        self.video.createCanvasControls(detection_object=self)
        self.menuBar()
        self.additional_gui = AdditionalGUILane(self)

        generateTopBottomBar(window=self.window, title=app_title, bottom_row=lane_window_bottom_row, n_columns=2)
        generateSubtitleBar(window=self.window, title=option2, n_columns=2)

        #self.detectAndTrack()

        self.frame_count += 1

        self.window.mainloop()

    def detectAndTrack(self):
        # Our main looping function
        self.frame_received, self.frame = self.updateFrame()

        self.roi.draw()

        if self.frame_received:
            self.tracker.yoloDetect()
            self.tracker.deepSortTrack()
            self.vehicles.register()

            # Only start detection after n fraes
            if self.frame_count > lane_violation_detection_start_after_n_frames:
                violation = self.checkViolation()
                if violation['occured']:
                    self.reportViolation()


        writeNewFrame(frame=self.frame, detection_object=self)

        self.window.after(lane_window_update_time, self.detectAndTrack)

    def updateFrame(self):
        # try to open the video
        if self.video.cap.isOpened():
            # if pause_frame has been set, then to continue from paused frame.
            if self.pause_frame is not None:
                self.video.cap.set(cv2.CAP_PROP_POS_FRAMES, self.pause_frame)
                self.pause_frame = None

            frame_received, frame = self.video.cap.read()

            # if video is paused
            if self.pause_video:
                self.pause_frame = self.video.cap.get(cv2.CAP_PROP_POS_FRAMES) - 1
                cv2.waitKey(-1)
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

    def roiSpecification(self):
        # select rectangular area
        dim = cv2.selectROI(roi_select_road_window_title, self.video.getThumbnail(non_tk=True))
        self.roi.x1, self.roi.y1, self.roi.x2, self.roi.y2 = dim[0], dim[1], dim[0] + dim[2], dim[1] + dim[3]
        self.roi.getRoiCoords(have_roi=True)
        cv2.destroyWindow(roi_select_road_window_title)

        # select top left and top right of road.
        dim = cv2.selectROI(roi_select_road_top_left_right_title,
                            self.video.getThumbnail(non_tk=True)[self.roi.y1:self.roi.y2, self.roi.x1:self.roi.x2])
        true_x = self.roi.x1 + dim[0]
        true_y = self.roi.y1 + dim[1]
        self.road_roi_left, self.road_roi_right = (true_x, true_y), (true_x + dim[2], true_y)
        cv2.destroyWindow(roi_select_road_top_left_right_title)



    def menuBar(self):
        # FILE MENU *
        file_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quitProgram)

    def quitProgram(self):
        self.window.destroy()
        self.window.quit()

    def checkViolation(self):
        """
        Looks for lane and retrogress violation.

        :return: violation dictionary
        """
        # TODO: to test
        violation = {
            'status': False,
            'types': [],
            'ids': []
        }
        for vehicle_object in self.vehicles.vehicles_in_scene['objects']:
            lane_cross, lane = laneCross(vehicle_object, self)
            if lane_cross:
                violation['occured'] = True
                violation['ids'].append(vehicle_object['id'])
                if lane == "likely retrogress":
                    if checkRetrogress(vehicle_object, self):
                        violation['types'].append("Retrogress")
                else:
                    violation['types'].append(lane.capitalize() + " Lane")
        return violation
