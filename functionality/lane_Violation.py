# System Modules ##
import time
from datetime import datetime

# Third Party Modules ##
import cv2
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
import threading


global thumbnail


class LaneViolation:
    def __init__(self, video_path):
        # show thumbnail and video, ask for confirmation [window] #
        # self.detect_ask_window = Tk()
        # self.detect_ask_window.title(option2 + " - " + app_title)

        # Video Initialization #
        self.video = Video(video_path)

        # OpenCV Initializations #
        self.frame_received = ''
        self.frame = ''

        # Tkinter Initializations #
        self.window = ''
        self.additional_gui = None
        self.video_canvas = ''
        self.menu_bar = ''

        # Pausing features initialization #
        self.pause_video = False
        self.pause_frame = None  # frame in which last time we paused.

        # Lanes and Tracker initialization #
        self.masked_frame = None
        self.tracker = obtk.DetectorTracker(self)
        self.lanes = Lanes(self)

        # ROI coordinates #
        self.roi = RegionOfInterest(self)
        self.road_roi_left = (296, 250) # road roi
        self.road_roi_right = (910, 250) # road roi

        # Vehicles Object initialization #
        self.vehicles = Vehicles(self)

        # Frame number counter #
        self.frame_count = 0

        # Violation #
        self.violation_info = None
        self.violation_log = {
            'ids': [],
            'class_names': [],
            'times': [],
            'types': [],
            'pictures': [],
            'video_proof_links': []
        }
        self.startDetectionWindow()
        #
        # generateTopBottomBar(window=self.detect_ask_window, title=self.detect_ask_window.title(),
        #                      bottom_row=lane_window_bottom_row)
        # generateSubtitleBar(window=self.detect_ask_window, title='Confirm Detect?')
        #
        # # confirm detect window is popped by this
        # ConfirmDetect(window=self.detect_ask_window, video=self.video, option=option1)
        #
        # detect_btn_font = tkFont.Font(family=detect_btn_font_family, size=detect_btn_font_size)
        # detect_btn = Button(self.detect_ask_window, text="Detect", bg=detect_btn_color,
        #                     activebackground=detect_btn_active_color,
        #                     command=self.startDetectionWindow, font=detect_btn_font)
        # detect_btn.grid(row=4, column=0, ipadx=load_video_inner_padding_x, ipady=load_video_inner_padding_y,
        #                 pady=load_video_outer_padding_y)
        #
        # self.detect_ask_window.mainloop()

    def startDetectionWindow(self):
        # self.detect_ask_window.destroy()
        # self.detect_ask_window.quit()

        #self.roiSpecification()

        #self.lanes.houghTransform()
        #self.lanes.seperateLaneLines()
        #self.lanes.seperateLaneAreas()

        # our main detection window
        self.window = Tk()
        self.window.title(option2 + ' - ' + app_title)
        self.menu_bar = Menu(self.window)
        self.window.config(menu=self.menu_bar)
        self.window.resizable(0, 0)

        # create the video and it's controls
        self.video.createCanvasControls(detection_object=self)
        self.menuBar()

        generateTopBottomBar(window=self.window, title=app_title, bottom_row=lane_window_bottom_row, n_columns=3)
        generateSubtitleBar(window=self.window, title=option2, n_columns=3)
        self.additional_gui = AdditionalGUILane(self)

        self.detectAndTrack()

        self.window.mainloop()

    def detectAndTrack(self):
        # Our main looping function
        self.frame_received, self.frame = self.updateFrame()

        self.roi.draw()

        self.frame_count += 1

        if self.frame_received:
            self.maskRoad()

            # Only start detection after n frames
            if self.frame_count > lane_violation_detection_start_after_n_frames:
                self.tracker.yoloDetect()
                self.tracker.deepSortTrack()
                self.vehicles.register()
                self.violation_info = self.checkViolation()
                if self.violation_info['status']:
                    print("Violation!!")
                    print(self.violation_info)
                    self.logViolation()
                    print(self.violation_log)
                    self.showInGUI()

        lanes_list = [self.lanes.left_lane_line1, self.lanes.left_lane_line2, self.lanes.right_lane_line1,
                      self.lanes.right_lane_line2]
        cv2.line(self.masked_frame, self.road_roi_left, self.road_roi_right, lane_color, lane_thickness)
        for lane in lanes_list:
            cv2.line(self.masked_frame, (lane['topx'], lane['topy']), (lane['bottomx'], lane['bottomy']),
                     lane_color, lane_thickness)

        scale_percent = 60  # percent of original size
        width = int(self.masked_frame.shape[1] * scale_percent / 100)
        height = int(self.masked_frame.shape[0] * scale_percent / 100)
        dim = (width, height)

        try:
            # resize image
            self.masked_frame = cv2.resize(self.masked_frame, dim, interpolation=cv2.INTER_AREA)
            self.video_canvas.configure(width=width, height=height)

        except:
            messagebox.showerror("Ended or Failed", "Your video ended or failed!")

        writeNewFrame(frame=self.masked_frame, detection_object=self)

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

    def maskRoad(self):
        mask_vertices = np.array([[
            self.road_roi_left,
            self.road_roi_right,
            (self.lanes.right_lane_area['bottom_right'][0], self.lanes.right_lane_area['bottom_right'][1]),
            (self.lanes.left_lane_area['bottom_left'][0], self.lanes.left_lane_area['bottom_left'][1]),
        ]], np.int32)
        mask = np.zeros_like(self.frame)
        channel_count_in_mask = self.frame.shape[2]
        match_mask_color = (255,) * channel_count_in_mask
        cv2.fillPoly(mask, mask_vertices, match_mask_color)
        self.masked_frame = cv2.bitwise_and(self.frame, mask)

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
            'ids': [],
            'class_names': [],
            'violation_bbox': []
        }
        for vehicle_object in self.vehicles.vehicles_in_scene['objects']:
            print("checking for id " + str(vehicle_object.id))
            where_is_vehicle = checkVehicleLocation(self, vehicle_object)
            if where_is_vehicle == "Overlapping Lane Lines":
                violation['status'] = True
                violation['types'].append("Lane Cross")
                violation['ids'].append(vehicle_object.id)
                violation['class_names'].append(vehicle_object.class_name)
                violation['violation_bbox'].append(vehicle_object.curr_bbox)
            elif checkRetrogress(self, vehicle_object, where_is_vehicle):
                violation['status'] = True
                violation['types'].append("Retrogress")
                violation['ids'].append(vehicle_object.id)
                violation['class_names'].append(vehicle_object.class_name)
                violation['violation_bbox'].append(vehicle_object.curr_bbox)

        return violation

    def logViolation(self):
        for i in range(len(self.violation_info['ids'])):
            if self.violation_info['ids'][i] not in self.violation_log['ids']:
                self.violation_log['ids'].append(self.violation_info['ids'][i])
                self.violation_log['class_names'].append(self.violation_info['class_names'][i])

                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                self.violation_log['times'].append(current_time)
                self.violation_log['types'].append(self.violation_info['types'][i])

                violator_picture = self.masked_frame[int(self.violation_info['violation_bbox'][i][1]):int(self.violation_info['violation_bbox'][i][3]),
                                   int(self.violation_info['violation_bbox'][i][0]):int(self.violation_info['violation_bbox'][i][2])]
                save_path = lane_violation_img_save_directory + violation_save_name_prefix + str(
                    self.violation_info['ids'][i]) + lane_violation_img_save_extension
                cv2.imwrite(save_path, violator_picture)
                self.violation_log['pictures'].append(save_path)

                start_frame = self.video.cap.get(cv2.CAP_PROP_POS_FRAMES)
                cap = cv2.VideoCapture(self.video.path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                video_save_path = lane_violation_vid_save_directory + violation_save_name_prefix + str(
                    self.violation_info['ids'][i]) + lane_violation_vid_save_extension
                fourcc = cv2.VideoWriter_fourcc(*'H264')
                out = cv2.VideoWriter(video_save_path, fourcc, 20.0, (self.masked_frame.shape[1], self.masked_frame.shape[0]))
                try:
                    n = 0
                    while n < 10:
                        _, frame = cap.read()
                        out.write(frame)
                        n += 1
                except:
                    print("Not enough frames for video output")

                self.violation_log['video_proof_links'].append(video_save_path)

    def showInGUI(self):
        threading.Thread(self.additional_gui.showViolationFrame(self.violation_log)).start()
        threading.Thread(self.additional_gui.logUpdate(self.violation_log)).start()
