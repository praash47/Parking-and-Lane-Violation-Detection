# System Modules ##
import datetime
import queue
import threading

# Local Modules ##
import yolo.object_tracker as obtk
from functionality.lane.lane_Processing import *
from functionality.lane.lane_Violation_Logic import *
from functionality.lane.vehicles import *
from functionality.roi import *
from functionality.video import *
from gui.additional_GUI_Lane import *
from gui.confirm_Detect import ConfirmDetect
from misc.settings import *
from misc.variables import *

global thumbnail  # tkinter bug for needing to declare global
global lock  # lock for passing through multiple threads, needs to be global to work
lock = threading.Lock()


class LaneViolation:
    def __init__(self, video_path):
        # show thumbnail and video, ask for confirmation [window] #
        self.detect_ask_window = Tk()
        self.detect_ask_window.title(option2 + " - " + app_title)

        # Video Initialization #
        self.video = Video(video_path)

        # OpenCV Initializations #
        self.frame_received = ''
        self.frame = None

        # Tkinter Initializations #
        self.window = None
        self.additional_gui = None
        self.video_canvas = None
        self.menu_bar = None

        # Pausing features initialization #
        self.pause_video = False
        self.pause_frame = None  # frame in which last time we paused.

        # Lanes and Tracker initialization #
        self.masked_frame = None
        self.tracker = obtk.DetectorTracker(self)
        self.lanes = Lanes(self)
        self.lane_line_received = None

        # ROI coordinates #
        self.roi = RegionOfInterest(self)

        self.road_roi_left = None
        self.road_roi_right = None

        # Vehicles Object initialization #
        self.vehicles = Vehicles(self)

        # Frame number counter #
        self.frame_count = 0

        # Violation Detection Initializations #
        self.violation_info = None  # violation_info consists of violations that occur in the current frame.
        self.violation_log = []  # violation log is collection of log batches (a batch is equal to one violation_info)
        self.violation_log_batch = None  # violation log batch is a batch made out of violation info, whose multiple
        # instances make violation_log
        self.violation_logged_ids = []  # ids which have already been placed in violation log
        self.violation_queue = queue.Queue()  # queue for threads for each log batch

        generateTopBottomBar(window=self.detect_ask_window, title=self.detect_ask_window.title(),
                             bottom_row=lane_window_bottom_row)
        generateSubtitleBar(window=self.detect_ask_window, title='Confirm Detect?')

        # confirm detect window is popped by this
        ConfirmDetect(window=self.detect_ask_window, video=self.video)

        detect_btn_font = tkFont.Font(family=detect_btn_font_family, size=detect_btn_font_size)
        detect_btn = Button(self.detect_ask_window, text="Detect", bg=detect_btn_color,
                            activebackground=detect_btn_active_color,
                            command=self.startDetectionWindow, font=detect_btn_font)
        detect_btn.grid(row=4, column=0, ipadx=load_video_inner_padding_x, ipady=load_video_inner_padding_y,
                        pady=load_video_outer_padding_y)

        self.startDetectionWindow()

        self.detect_ask_window.mainloop()

    def startDetectionWindow(self):
        """
        responsible for starting the detection window
        """
        self.detect_ask_window.destroy()
        self.detect_ask_window.quit()

        while not self.lane_line_received:
            # First, we specify three region of interests
            self.roiSpecification()

            # we apply hough transform and then:
            # 1. separate lane lines (placing top and bottom co-ordinate values of four lane lines)
            # 2. separate lane areas (placing the top left, right and bottom left & right for two lane areas)
            self.lanes.houghTransform()
            self.lane_line_received = self.lanes.separateLaneLines()
            self.lanes.separateLaneAreas()

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

        # Creation of Recent Violation Section and Violation Log Section
        self.additional_gui = AdditionalGUILane(self)

        # run detect and track in another thread, for optimum performance.
        # if it is threaded, it is expected that video processing will take in one frame of cpu and interactions with
        # GUI (eg. pressing button, clicking on menu bar) will run in next core for smooth performance.
        threading.Thread(target=self.detectAndTrack).start()

        self.frame_count += 1

        self.window.mainloop()

    def detectAndTrack(self):
        """
        our main looping function, called every 10 ms.
        """
        self.frame_received, self.frame = self.updateFrame()

        self.frame_count += 1

        if self.frame_received and not self.pause_frame:
            # Obtain a mask, for operation of YOLO and deep sort on that masked frame.
            self.maskRoad()
            self.lanes.showLaneLines()

            # Only start detection after n frames
            # reason: some of the previous frames data is required for lane violation detection.
            if self.frame_count > lane_violation_detection_start_after_n_frames:
                # Use yolo detection then, apply deep sort tracker in the frame
                self.tracker.yoloDetect()
                self.tracker.deepSortTrack()

                # Register the vehicle into the
                self.vehicles.register()

                # Retrieve the violation info in the current frame
                self.violation_info = self.checkViolation()

                # If in the current frame, if violation has occur then
                if self.violation_info['status']:
                    # Log that violation, put the batch thread in the queue and show in GUI that thread.
                    self.logViolation()
                    self.putInQueue()
                    self.showInGUI()

            # scale down the video for display on screen
            width = int(self.masked_frame.shape[1] * video_scale_percent / 100)
            height = int(self.masked_frame.shape[0] * video_scale_percent / 100)
            dim = (width, height)

            try:
                # resize image
                self.masked_frame = cv2.resize(self.masked_frame, dim, interpolation=cv2.INTER_AREA)
                self.video_canvas.configure(width=width, height=height)

            except:
                messagebox.showerror("Ended or Failed", "Your video ended or failed!")

            writeNewFrame(frame=self.masked_frame, detection_object=self)

        # call detectAndTrack after 10 ms.
        self.window.after(lane_window_update_time, self.detectAndTrack)

    def updateFrame(self):
        """
        This function fetches the next frame.

        :return:
        frame_received - boolean
        frame - numpy image frame
        """
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
        """
        select three region of interests, required for lane violation module
        """
        # select rectangular area
        dim = cv2.selectROI(roi_select_road_window_title, self.video.getThumbnail(non_tk=True))
        self.roi.x1, self.roi.y1, self.roi.x2, self.roi.y2 = int(dim[0]), int(dim[1]), int(dim[0] + dim[2]), \
                                                             int(dim[1] + dim[3])
        self.roi.getRoiCoords(have_roi=True)  # sometimes, we would want to draw this selected rectangular area into the
        # screen, it is for the very purpose.
        cv2.destroyWindow(roi_select_road_window_title)

        # crop the frame
        frame = self.video.getThumbnail(non_tk=True)[self.roi.y1:self.roi.y2, self.roi.x1:self.roi.x2]

        # select top left and top right of road.
        dim = cv2.selectROI(roi_select_road_top_left_right_title, frame)
        true_x = int(self.roi.x1 + dim[0])
        true_y = int(self.roi.y1 + dim[1])
        self.road_roi_left, self.road_roi_right = (true_x, true_y), (int(true_x + dim[2]), true_y)
        cv2.destroyWindow(roi_select_road_top_left_right_title)

        # draw line on frame, for selection ease of road roi top left and top right
        road_roi_drawn_frame = self.video.getThumbnail(non_tk=True)
        cv2.line(road_roi_drawn_frame, self.road_roi_left, self.road_roi_right, (0, 255, 0), 2)

        # hough crop range left and right select
        dim = cv2.selectROI("Select Lane Lines Area", road_roi_drawn_frame)
        # transformation of co-ordinates into larger cropped rectangular area co-ordinates.
        true_x = int(self.roi.x1 + dim[0])
        true_y = int(self.roi.y1 + dim[1])
        self.lanes.hough_crop_range_left, self.lanes.hough_crop_range_right = (true_x, true_y), \
                                                                              (int(true_x + dim[2]),
                                                                               int(true_y + dim[3]))

    def maskRoad(self):
        """
        masks out the road by using
        1. road roi left
        2. road roi right
        3. left lane area bottom left and right
        4. right lane area bottom left and right

        stores the mask in the self.masked_frame
        """
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
        """
        generates the menu-bar at the top of detection window.
        """
        # FILE MENU *
        file_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quitProgram)

    def quitProgram(self):
        """
        this function destroys the detection window.
        """
        self.window.destroy()
        self.window.quit()

    def checkViolation(self):
        """
        Looks for lane and retrogress violation.
        violation['status'] is True if violation occur.

        :return: violation dictionary
        """
        violation = {
            'status': False,
            'types': [],
            'ids': [],
            'class_names': [],
            'violation_bbox': []
        }
        # For each vehicle in vehicles in scene
        for vehicle_object in self.vehicles.vehicles_in_scene['objects']:
            # First, check location of the vehicle
            where_is_vehicle = checkVehicleLocation(self, vehicle_object)
            # If vehicle is overlapping lane lines
            if where_is_vehicle == "Overlapping Lane Lines":
                # Make status true and append it's details onto the violation dictionary
                violation['status'] = True
                violation['types'].append("Lane Cross")
                violation['ids'].append(vehicle_object.id)
                violation['class_names'].append(vehicle_object.class_name)
                violation['violation_bbox'].append(vehicle_object.curr_bbox)
            # If retrogress check function returns true, then retrogress is appended
            elif checkRetrogress(self, vehicle_object, where_is_vehicle):
                violation['status'] = True
                violation['types'].append("Retrogress")
                violation['ids'].append(vehicle_object.id)
                violation['class_names'].append(vehicle_object.class_name)
                violation['violation_bbox'].append(vehicle_object.curr_bbox)

        return violation

    def logViolation(self):
        """
        Creates a log batch and appends it to violation log.
        """
        self.violation_log_batch = {
            'ids': [],
            'class_names': [],
            'times': [],
            'types': [],
            'pictures': [],
            'video_proof_links': []
        }
        for i in range(len(self.violation_info['ids'])):
            # If that id is not in already violation performed ids; to prevent duplicates of violation
            if self.violation_info['ids'][i] not in self.violation_logged_ids:
                self.violation_log_batch['ids'].append(self.violation_info['ids'][i])
                self.violation_log_batch['class_names'].append(self.violation_info['class_names'][i])

                # Get current time
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")
                self.violation_log_batch['times'].append(current_time)
                self.violation_log_batch['types'].append(self.violation_info['types'][i])

                # Write picture to directory and also save it's saved path
                violator_picture = self.masked_frame[int(self.violation_info['violation_bbox'][i][1]):int(
                    self.violation_info['violation_bbox'][i][3]),
                                   int(self.violation_info['violation_bbox'][i][0]):int(
                                       self.violation_info['violation_bbox'][i][2])]
                save_path = lane_violation_img_save_directory + violation_save_name_prefix + \
                            str(self.violation_info['ids'][i]) + lane_violation_img_save_extension
                cv2.imwrite(save_path, violator_picture)
                self.violation_log_batch['pictures'].append(save_path)

                # Write video to directory and also save it's saved path
                start_frame = self.video.cap.get(cv2.CAP_PROP_POS_FRAMES)
                cap = cv2.VideoCapture(self.video.path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                video_save_path = lane_violation_vid_save_directory + violation_save_name_prefix + str(
                    self.violation_info['ids'][i]) + lane_violation_vid_save_extension
                fourcc = cv2.VideoWriter_fourcc(*'H264')
                out = cv2.VideoWriter(video_save_path, fourcc, 20.0,
                                      (self.masked_frame.shape[1], self.masked_frame.shape[0]))
                try:
                    n = 0
                    # write n frames
                    while n < n_output_violation_frames:
                        _, frame = cap.read()
                        out.write(frame)
                        n += 1
                except:
                    print("Not enough frames for video output")
                self.violation_log_batch['video_proof_links'].append(video_save_path)

                # Write the current id into logged ids
                self.violation_logged_ids.append(self.violation_info['ids'][i])
        # Appending the log batch into the violation log.
        self.violation_log.append(self.violation_log_batch)

    def showInGUI(self):
        """
        get thread from the queue one at a time and start it
        """
        current_thread = self.violation_queue.get()
        current_thread.start()

    def putInQueue(self):
        """
        puts each log batch thread into the queue and keep it in pending while one sets the lock and uses recent
        violation. pass lock with the log batch.
        """
        global lock
        t = threading.Thread(target=self.additional_gui.showViolationFrame, args=(self.violation_log_batch, lock,))
        self.violation_queue.put(t)
