# Third Party Modules ##
import numpy as np
import cv2
import math
from tkinter import messagebox

# Local Modules ##
from misc.settings import *
from misc.variables import *


class Lanes:
    """
    Lanes module for managing lanes.
    """
    def __init__(self, detection_object):
        self.object = detection_object
        self.lanes_list = []
        self.left_lane_line1 = None
        self.left_lane_line2 = None
        self.right_lane_line1 = None
        self.right_lane_line2 = None
        # self.left_lane_line1 = {
        #     'bottomx': 600,
        #     'bottomy': 720,
        #     'topx': 603,
        #     'topy': 250
        # }
        # self.left_lane_line2 = {
        #     'bottomx': 616,
        #     'bottomy': 720,
        #     'topx': 609,
        #     'topy': 250
        # }
        # self.right_lane_line1 = {
        #     'bottomx': 651,
        #     'bottomy': 720,
        #     'topx': 624,
        #     'topy': 250
        # }
        # self.right_lane_line2 = {
        #     'bottomx': 667,
        #     'bottomy': 720,
        #     'topx': 630,
        #     'topy': 250
        # }
        self.hough_img = None
        self.hough_crop_range_left = None
        self.hough_crop_range_right = None
        self.left_lane_area = None
        self.right_lane_area = None
        # self.left_lane_area = {
        #     'top_left': [296, 250],
        #     'top_right': [603, 250],
        #     'bottom_left': [0, 720],
        #     'bottom_right': [600, 720]
        # }
        # self.right_lane_area = {
        #     'top_left': [630, 250],
        #     'top_right': [910, 250],
        #     'bottom_left': [667,720],
        #     'bottom_right': [1280, 720]
        # }

    def houghTransform(self):
        # Pre-processing for hough transform
        frame_width = int(self.object.video.width)
        frame_height = int(self.object.video.height)
        mid_x = int(frame_width / 2)

        self.hough_crop_range_left = abs(self.hough_crop_range_left[0] - mid_x)
        self.hough_crop_range_right = abs(self.hough_crop_range_right[0] - mid_x)

        self.hough_img = self.object.video.getThumbnail(non_tk=True)
        hough_crop = self.hough_img[self.object.road_roi_left[1]: frame_height, mid_x - self.hough_crop_range_left: mid_x +
                                                                   self.hough_crop_range_right]
        edges = cv2.Canny(hough_crop, canny_threshold1, canny_threshold2, apertureSize=canny_aperture_size)
        ("crop", hough_crop)
        self.hough(edges, mid_x)

    def hough(self, edges, m):
        # the main hough transform
        lines = cv2.HoughLinesP(edges, hough_rho, hough_theta, hough_threshold, minLineLength=hough_min_line_length,
                                maxLineGap=hough_max_line_gap)
        try:
            lines = self.adjustCoordinates(lines)
            for line in lines:
                x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
                rel_x1 = m - self.hough_crop_range_left + x1
                rel_x2 = m - self.hough_crop_range_left + x2
                rel_y1 = self.object.road_roi_left[1] + y1
                rel_y2 = self.object.road_roi_left[1] + y2
                self.lanes_list.append([rel_x1, rel_y1, rel_x2, rel_y2])

        except TypeError:  # No any lines in specified location
            messagebox.showerror(title="Closing Program",
                                 message="Either you selected a video of non-matched format or hough is not able to detect"
                                 "any lines.")
            raise ValueError("Either you selected a video of non-matched format or hough is not able to detect any lines.")



    def adjustCoordinates(self, lines):
        """
        This function adjusts the co-ordinates so that it matches format.

        Bottom x, Bottom y, Top x, Top y

        :param lines:
        :return: list of lines
        """
        adjusted = np.array([[0, 0, 0, 0]])
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if y2 > y1:
                tempx = line[0][0]
                tempy = line[0][1]
                line[0][0] = int(line[0][2])
                line[0][1] = int(line[0][3])
                line[0][2] = int(tempx)
                line[0][3] = int(tempy)
            line = [line[0][0], line[0][1], line[0][2], line[0][3]]
            adjusted = np.append(adjusted, [line], axis=0)
        adjusted = np.delete(adjusted, 0, 0)
        return adjusted

    def seperateLaneLines(self):
        """
        This function adjusts the co-ordinates so that it matches format.

        Bottom x, Bottom y, Top x, Top y

        :param lines:
        :return: void
        """
        if len(self.lanes_list) >= 4:
            if len(self.lanes_list) > 4:
                for index, lane in enumerate(self.lanes_list):
                    if lane[0] == lane[2]:
                        self.lanes_list.pop(index)
            lanes_order = [self.lanes_list[0][0], self.lanes_list[1][0], self.lanes_list[2][0], self.lanes_list[3][0]]
            lanes_order.sort()
            self.left_lane_line1 = self.getLaneLine(lanes_order.pop(0))
            self.left_lane_line2 = self.getLaneLine(lanes_order.pop(0))
            self.right_lane_line1 = self.getLaneLine(lanes_order.pop(0))
            self.right_lane_line2 = self.getLaneLine(lanes_order.pop(0))
            self.formatLaneLinesProperly()
            self.extendLaneLines()

            lanes_list = [self.left_lane_line1, self.left_lane_line2, self.right_lane_line1, self.right_lane_line2]
            cv2.line(self.hough_img, self.object.road_roi_left, self.object.road_roi_right, lane_color, lane_thickness)
            for lane in lanes_list:
                cv2.line(self.hough_img, (lane['topx'], lane['topy']), (lane['bottomx'], lane['bottomy']),
                         lane_color, lane_thickness)
            ('hough after extension', self.hough_img)
        else:
            messagebox.showwarning(title="Not Enough Lines By Hough",
                                   message="There is not enough lines by hough. Selecting ROI properly may work.")
            self.object.roiSpecification()
            self.houghTransform()
            self.seperateLaneLines()

    def getLaneLine(self, x):
        """
        This function returns lane line one by one
        :param x:
        :return: lane line
        """
        found = None
        for index, lane in enumerate(self.lanes_list):
            if lane[0] == x:
                found = index
        return self.lanes_list.pop(found)

    def extendLaneLines(self):
        """
        The lane extension required for extending lines to top of screen and bottom of screen
        :return: void
        """
        lanes_list = [self.left_lane_line1, self.left_lane_line2, self.right_lane_line1, self.right_lane_line2]
        # top and bottom check and extension if short for each line.
        for lane in lanes_list:
            dy = abs(lane['bottomy']-lane['topy'])
            dx = abs(lane['topx']-lane['bottomx'])
            # see if line is not properly extended, then extend
            if lane['topy'] > self.object.road_roi_left[1]:
                self.extendLaneLine(lane, dy, dx, self.object.road_roi_left[1])
            if lane['bottomy'] < self.object.video.height:
                self.extendLaneLine(lane, dy, dx, self.object.video.height, up=False)

    def extendLaneLine(self, lane, dy, dx, upto, up=True):
        """
        Use of DDA for extension
        :param lane:
        :param dy: variation of y range of the lane
        :param dx: variation of x range of the lane
        :param upto:
        :param up: True if we are extending to top, if bottom, False
        :return:
        """
        if dy > dx:
            steps = dy
        else:
            steps = dx
        yinc = dy / steps
        xinc = dx / steps
        if up:
            y = lane['topy']
            x = lane['topx']
        else:
            y = lane['bottomy']
            x = lane['bottomx']
        while y != upto:
            if up:
                y -= yinc
                x -= xinc
            else:
                y += yinc
                x += xinc
        if up:
            lane['topx'], lane['topy'] = int(round(x, 0)), int(round(y, 0))
        else:
            lane['bottomx'], lane['bottomy'] = int(round(x, 0)), int(round(y, 0))

    def formatLaneLinesProperly(self):
        # Formatting lanes line for readability ##
        self.left_lane_line1 = self.formatLaneLine(self.left_lane_line1)
        self.left_lane_line2 = self.formatLaneLine(self.left_lane_line2)
        self.right_lane_line1 = self.formatLaneLine(self.right_lane_line1)
        self.right_lane_line2 = self.formatLaneLine(self.right_lane_line2)

    def formatLaneLine(self, lane):
        # Seperate co-ordinates using dictionary for readability ##
        return {'bottomx': lane[0], 'bottomy': lane[1], 'topx': lane[2], 'topy': lane[3]}

    def seperateLaneAreas(self):
        self.left_lane_area = self.seperateLaneArea()
        self.right_lane_area = self.seperateLaneArea(left=False)
        self.showLaneAreas()

    def seperateLaneArea(self, left=True):
        """
        Seperating Lane Areas on the basis of lane lines so detected and road top left, right
        and bottom of screen co-ordinates.

        :param left: It specifies lane is left lane or right lane
        :return: dictionary with tuples for top-left, top-right, bottom-left and bottom-right
        """
        if left:
            top_left = [self.object.road_roi_left[0], self.object.road_roi_left[1]]
            top_right = [self.left_lane_line1['topx'], self.left_lane_line1['topy']]
            bottom_left = [0, int(self.object.video.height)]
            bottom_right = [self.left_lane_line1['bottomx'], self.left_lane_line1['bottomy']]
        else:
            top_left = [self.right_lane_line2['topx'], self.right_lane_line2['topy']]
            top_right = [self.object.road_roi_right[0], self.object.road_roi_right[1]]
            bottom_left = [self.right_lane_line2['bottomx'], self.right_lane_line2['bottomy']]
            bottom_right = [int(self.object.video.width), int(self.object.video.height)]
        return {'top_left': top_left, 'top_right': top_right, 'bottom_left': bottom_left, 'bottom_right': bottom_right}

    def showLaneAreas(self):
        # TODO: To test
        # This function is responsible for showing seperated lane areas ##
        left_lane_pts = np.array([
            self.left_lane_area['top_left'], self.left_lane_area['top_right'],
            self.left_lane_area['bottom_right'], self.left_lane_area['bottom_left']],
                         np.int32)
        right_lane_pts = np.array([
            self.right_lane_area['top_left'], self.right_lane_area['top_right'],
            self.right_lane_area['bottom_right'], self.right_lane_area['bottom_left']],
                         np.int32)
        left_lane_pts = left_lane_pts.reshape((-1, 1, 2))
        right_lane_pts = right_lane_pts.reshape((-1, 1, 2))
        self.hough_img = cv2.polylines(self.hough_img, [left_lane_pts], lane_area_polygon_join, left_lane_color)
        self.hough_img = cv2.polylines(self.hough_img, [right_lane_pts], lane_area_polygon_join, right_lane_color)
        # self.hough_img = cv2.putText(self.hough_img, left_lane_text,
        #                                 (self.left_lane_area['top_left']+lane_text_padding,
        #                                  self.left_lane_area['top_right']+lane_text_padding),
        #                                 lane_text_font,
        #                                 lane_text_font_scale, left_lane_color, lane_text_thickness,
        #                                 lane_text_line_type)
        ("after lanes area seperation", self.hough_img)
