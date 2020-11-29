# System Modules ##
import os

# Third Party Modules ##
import cv2
import numpy as np
from tkinter import *


# -----------------------------------------------
# GLOBAL SETTINGS
# -----------------------------------------------
# Misc #
current_directory = os.getcwd()
desired_objects = [
    "car",
    "motorbike",
    "bicycle",
    "bus",
    "truck",
    "train"
]

# Default #
theme_bg_color = "Blue"
default_font_family = "Lucida Grande"
default_btn_color = "#fadace"
default_btn_active_color = "#e94b3c"
default_sticky_direction = "NESW"
default_error_color = "Red"
default_success_color = "Green"
slider_default_orientation = HORIZONTAL

# Top Bottom Bar #
theme_top_bottom_bar_color = "Blue"
theme_top_bottom_bar_text_color = "White"
top_canvas_height = 200
top_bottom_sticky_direction = default_sticky_direction
top_bottom_inner_padding_x = 100
top_bottom_inner_padding_y = 20
top_font_family = default_font_family
bottom_font_family = default_font_family
top_font_size = 15
bottom_font_size = 10

# Subtitle Bar #
subtitle_bg_color = "#00BFFF"
subtitle_text_color = "white"
subtitle_inner_pad_x = 10
subtitle_inner_pad_y = subtitle_inner_pad_x
subtitle_sticky_direction = default_sticky_direction
subtitle_font_size = 5

# Main Menu Window #
option_color = default_btn_color
option_width = 30
option_inner_padding_x = 10
option_inner_padding_y = option_inner_padding_x
option_outer_padding_y = 10
option_btn_active_color = default_btn_active_color

# Load Video Window #
load_video_color = default_btn_color
load_video_active_color = default_btn_active_color
load_video_inner_padding_x = 30
load_video_inner_padding_y = option_inner_padding_x
load_video_outer_padding_y = 50
load_video_font_family = default_font_family
load_video_font_size = 20


# -----------------------------------------------
# VIDEO MODULE SETTINGS
# -----------------------------------------------
# Font #
video_name_font_family = default_font_family
video_name_font_size = 20
video_name_font_weight = "bold"

# Controls #
# buttons
video_controls_inner_padding_x = 10
video_controls_inner_padding_y = video_controls_inner_padding_x
video_controls_btn_color = default_btn_color
video_controls_btn_active_color = default_btn_active_color
video_controls_btn_font_family = default_font_family
video_controls_btn_font_size = 15
# icons
video_controls_pause_icon = current_directory + "\\" + "resources" + "\\" + "pause.png"  # 24x24 icon
video_controls_restart_icon = current_directory + "\\" + "resources" + "\\" + "restart.png"  # 24x24 icon
video_controls_play_icon = current_directory + "\\" + "resources" + "\\" + "play.png"  # 24x24 icon

# -----------------------------------------------
# CONFIRM DETECT MODULE SETTINGS
# -----------------------------------------------
# Detect Button
detect_btn_color = default_btn_color
detect_btn_active_color = default_btn_active_color
detect_btn_inner_padding_x = 20
detect_btn_inner_padding_y = option_inner_padding_x
detect_btn_outer_padding_y = 5
detect_btn_font_family = default_font_family
detect_btn_font_size = 15

# -----------------------------------------------
# YOLO MODULE SETTINGS
# -----------------------------------------------
# Initialization
parking_yolo_confidence_threshold = 0.35
parking_yolo_nms_threshold = 0.3
parking_yolo_coco_names = current_directory + "\\" + "yolo" + "\\" + "coco.names"
parking_yolo_config = current_directory + "\\" + "yolo" + "\\" + "yolov3.cfg"
parking_yolo_weights = current_directory + "\\" + "yolo" + "\\" + "yolov3.weights"

# DNN
parking_yolo_dnn_blob_scale_factor = 1/255
parking_yolo_dnn_blob_mean_sub_value = [0, 0, 0]
parking_yolo_dnn_blob_swap_RB = 1
parking_yolo_dnn_blob_crop = False
parking_yolo_dnn_blob_output_size = 320

# Bounding Box
parking_yolo_bbox_color = (255, 255, 0)
parking_yolo_bbox_thickness = 1
parking_yolo_bbox_font = cv2.FONT_HERSHEY_SIMPLEX
parking_yolo_bbox_font_scale = 0.6

# -----------------------------------------------
# PARKING WINDOW SETTINGS
# -----------------------------------------------
# Misc
parking_window_bottom_row = 5

# Main
parking_window_update_time = 10
parking_after_motion_check_seconds = 3
moving_std_deviation_threshold = 1
parking_violation_report_time = 3
parking_violation_save_directory = "violations/parking/"
parking_violation_save_extension = ".jpg"

# | ROI |
# | MODULE |
# Frame
roi_coords_top_padding = 10
roi_coords_bottom_padding = roi_coords_top_padding
roi_coords_inner_padding_x = 10
roi_coords_inner_padding_y = roi_coords_inner_padding_x
roi_coords_width = 150
roi_coords_height = 100
roi_coords_label_padding_x = 10
roi_coords_label_padding_y = roi_coords_label_padding_x
# input boxes
roi_coords_x1_width = 4
roi_coords_y1_width = roi_coords_x1_width
roi_coords_x2_width = roi_coords_x1_width
roi_coords_y2_width = roi_coords_x1_width
# submit button
roi_coords_btn_color = default_btn_color
roi_coords_btn_active_color = default_btn_active_color
roi_coords_btn_padding_x = 10

# Rectangle
roi_rectangle_color = (255, 0, 255)
roi_rectangle_thickness = 2

# Misc
roi_status_message_destroy_time = 3

# Status Message
parking_status_message_padding_x = 10
parking_status_message_padding_y = parking_status_message_padding_x

# | DETECTION TRACKING |
# | MODULE |
# Detector
# blur
detector_blur_size = 0
detector_blur_output_size = (5, 5)
# threshold
detector_threshold_output_size = 20
detector_threshold_thresh = 255
# dilate
detector_dilate_iterations = 3

# Tracker
tracker_rectangle_color = (255, 0, 0)
tracker_rectangle_thickness = 2

# Reset
reset_violation_btn_color = default_btn_color
reset_violation_btn_active_color = default_btn_active_color
reset_violation_btn_sticky = "EW"


# -----------------------------------------------
# LANE WINDOW SETTINGS
# -----------------------------------------------
# Misc
lane_window_bottom_row = 5

# Main
lane_window_update_time = 10
lane_violation_detection_start_after_n_frames = 2

# | YOLO DEEPSORT |
# | MODULE |
# YOLO
lane_yolo_model_to_use = 'yolov4'

lane_yolo_max_cosine_distance = 0.4
lane_yolo_nn_budget = None
lane_yolo_nms_max_overlap = 1.0
lane_yolo_model_filename = 'yolo/model_data/mars-small128.pb'

# | LANE PROCESSING |
# | MODULE |
# Hough Transform
hough_crop_range_left = 110
hough_crop_range_right = 0
canny_threshold1 = 50
canny_threshold2 = 150
canny_aperture_size = 3

hough_rho = 1
hough_theta = np.pi/180
hough_threshold = 100
hough_min_line_length = 100
hough_max_line_gap = 10

lane_color = (0, 255, 0)
lane_thickness = 1
lane_text_font = cv2.FONT_HERSHEY_SIMPLEX
lane_text_line_type = cv2.LINE_AA
lane_text_font_scale = 2
lane_text_thickness = 1
lane_text_padding = 10

# Lane Seperation Area Showing
lane_area_polygon_join = True
left_lane_color = (255, 0, 255)
right_lane_color = (255, 0, 255)

# Lane Violation Setttings
lane_recent_violation_sleep_time = 3
lane_violation_img_save_directory = "violations/lane/images/"
lane_violation_img_save_extension = ".jpg"

lane_violation_vid_save_directory = "violations/lane/videos/"
lane_violation_vid_save_extension = ".mp4"