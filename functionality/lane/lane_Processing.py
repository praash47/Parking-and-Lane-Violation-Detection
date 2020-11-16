from misc.settings import *
from misc.variables import *

import numpy as np
import cv2
import math


class Lanes:
    def __init__(self, detection_object):
        self.object = detection_object
        self.lanes_list = []
        self.left_lane_line1 = None
        self.left_lane_line2 = None
        self.right_lane_line1 = None
        self.right_lane_line2 = None
        self.hough_img = None
        self.left_lane_area = None
        self.right_lane_area = None

    def houghTransform(self):
        frame_width = int(self.object.video.width)
        frame_height = int(self.object.video.height)
        mid_x = int(frame_width / 2)
        self.hough_img = self.object.video.getThumbnail(non_tk=True)
        hough_crop = self.hough_img[self.object.road_roi_left[1]: frame_height, mid_x - hough_crop_range_left: mid_x +
                                                                   hough_crop_range_right]
        edges = cv2.Canny(hough_crop, canny_threshold1, canny_threshold2, apertureSize=canny_aperture_size)
        self.hough(edges, mid_x)

    def hough(self, edges, m):
        lines = cv2.HoughLinesP(edges, hough_rho, hough_theta, hough_threshold, minLineLength=hough_min_line_length,
                                maxLineGap=hough_max_line_gap)
        lines = self.adjustCoordinates(lines)
        print(lines)
        for line in lines:
            x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
            rel_x1 = m - hough_crop_range_left + x1
            rel_x2 = m - hough_crop_range_left + x2
            rel_y1 = self.object.road_roi_left[1] + y1
            rel_y2 = self.object.road_roi_left[1] + y2
            self.lanes_list.append([rel_x1, rel_y1, rel_x2, rel_y2])
            cv2.line(self.hough_img, (rel_x1, rel_y1), (rel_x2, rel_y2), lane_color, lane_thickness)
        cv2.line(self.hough_img, self.object.road_roi_left, self.object.road_roi_right, lane_color, lane_thickness)
        cv2.imshow('hough before extension', self.hough_img)

    def adjustCoordinates(self, lines):
        adjusted = np.array([[0, 0, 0, 0]])
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if y2 > y1:
                tempx = line[0][0]
                tempy = line[0][1]
                line[0][0] = line[0][2]
                line[0][1] = line[0][3]
                line[0][2] = tempx
                line[0][3] = tempy
            line = [line[0][0], line[0][1], line[0][2], line[0][3]]
            adjusted = np.append(adjusted, [line], axis=0)
        adjusted = np.delete(adjusted, 0, 0)
        return adjusted

    def seperateLaneLines(self):
        if len(self.lanes_list) >= 4:
            if len(self.lanes_list) > 4:
                for index, lane in enumerate(self.lanes_list):
                    if lane[0] == lane[2]:
                        self.lanes_list.pop(index)
            lanes_order = [self.lanes_list[0][0], self.lanes_list[1][0], self.lanes_list[2][0], self.lanes_list[3][0]]
            lanes_order.sort()
            print(lanes_order)
            self.left_lane_line1 = self.getLaneLine(lanes_order.pop(0))
            self.left_lane_line2 = self.getLaneLine(lanes_order.pop(0))
            self.right_lane_line1 = self.getLaneLine(lanes_order.pop(0))
            self.right_lane_line2 = self.getLaneLine(lanes_order.pop(0))
            self.formatLaneLinesProperly()
            self.extendLaneLines()

            lanes_list = [self.left_lane_line1, self.left_lane_line2, self.right_lane_line1, self.right_lane_line2]
            print(self.left_lane_line1, self.left_lane_line2, self.right_lane_line1, self.right_lane_line2)
            for lane in lanes_list:
                cv2.line(self.hough_img, (lane['bottomx'], lane['bottomy']), (lane['topx'], lane['topy']),
                         lane_color, lane_thickness)
            cv2.imshow('hough after extension', self.hough_img)
        else:
            print("Not enough lines by hough.")

    def getLaneLine(self, x):
        found = None
        for index, lane in enumerate(self.lanes_list):
            if lane[0] == x:
                found = index
        return self.lanes_list.pop(found)

    def extendLaneLines(self):
        lanes_list = [self.left_lane_line1, self.left_lane_line2, self.right_lane_line1, self.right_lane_line2]
        # top and bottom check and extension if short.
        for lane in lanes_list:
            print(lane)
            dy = abs(lane['bottomy']-lane['topy'])
            dx = abs(lane['topx']-lane['bottomx'])
            if lane['topy'] > self.object.road_roi_left[1]:
                self.extendLaneLine(lane, dy, dx, self.object.road_roi_left[1])
            if lane['bottomy'] < self.object.video.height:
                self.extendLaneLine(lane, dy, dx, self.object.video.height, up=False)

    def extendLaneLine(self, lane, dy, dx, upto, up=True):
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
                print("up: ", x, y)
                y -= yinc
                x += xinc
            else:
                print("down: ", x, y)
                y += yinc
                x -= xinc
        if up:
            lane['topx'], lane['topy'] = int(x), int(y)
        else:
            lane['bottomx'], lane['bottomy'] = int(x), int(y)

    def formatLaneLinesProperly(self):
        self.left_lane_line1 = self.formatLaneLine(self.left_lane_line1)
        self.left_lane_line2 = self.formatLaneLine(self.left_lane_line2)
        self.right_lane_line1 = self.formatLaneLine(self.right_lane_line1)
        self.right_lane_line2 = self.formatLaneLine(self.right_lane_line2)

    def formatLaneLine(self, lane):
        return {'bottomx': lane[0], 'bottomy': lane[1], 'topx': lane[2], 'topy': lane[3]}

    def seperateLaneAreas(self):
        self.left_lane_area = self.seperateLaneArea()
        self.right_lane_area = self.seperateLaneArea(left=False)

    def seperateLaneArea(self, left=True):
        if left:
            top_left = self.object.road_roi_left
            top_right = (self.left_lane_line1['topx'], self.left_lane_line1['topy'])
            bottom_left = (self.object.video.height, 0)
            bottom_right = (self.left_lane_line1['bottomx'], self.left_lane_line1['bottomy'])
        else:
            top_left = (self.right_lane_line2['topx'], self.right_lane_line2['topy'])
            top_right = self.object.road_roi_right
            bottom_left = (self.right_lane_line2['bottomx'], self.right_lane_line2['bottomy'])
            bottom_right = (self.object.video.width, self.object.video.height)
        return {'top_left': top_left, 'top_right': top_right, 'bottom_left': bottom_left, 'bottom_right': bottom_right}

    def showLaneAreas(self):
        left_lane_pts = [
            [self.left_lane_area['top_left'], self.left_lane_area['top_right']],
            [self.left_lane_area['bottom_left'], self.left_lane_area['bottom_right']],
                         ]
        right_lane_pts = [
            [self.right_lane_area['top_right'], self.right_lane_area['top_right']],
            [self.right_lane_area['bottom_right'], self.right_lane_area['bottom_right']],
                         ]
        left_lane_pts.zreshape(-1, 1, 2)
        right_lane_pts.reshape(-1, 1, 2)
        self.object.frame = cv2.polylines(self.object.frame, [left_lane_pts], lane_area_polygon_join, left_lane_color)
        self.object.frame = cv2.polylines(self.object.frame, [right_lane_pts], lane_area_polygon_join, right_lane_color)
        self.object.frame = cv2.putText(self.object.frame, left_lane_text,
                                        (self.left_lane_area['top_left']+lane_text_padding,
                                         self.left_lane_area['top_right']+lane_text_padding),
                                        lane_text_font,
                                        lane_text_font_scale, left_lane_color, lane_text_thickness,
                                        lane_text_line_type)
        self.object.frame = cv2.putText(self.object.frame, right_lane_text,
                                        (self.right_lane_area['top_left']+lane_text_padding,
                                         self.right_lane_area['top_right']+lane_text_padding),
                                        lane_text_font,
                                        lane_text_font_scale, right_lane_color, lane_text_thickness,
                                        lane_text_line_type)

    def determineLane(self, vehicle_object):
        if vehicle_object.in_frame > 10:
            avg_prev_5_areas = sum(vehicle_object.prev_10_areas[-5:]) / 5
            avg_first_5_areas = sum(vehicle_object.prev_10_areas[:5]) / 5
            if vehicle_object.curr_bbox[2] in range(self.left_lane_line2['topx'] +
                                                    (vehicle_object.curr_bbox[2]-vehicle_object.curr_bbox[2]),
                                                    self.object.video.width):
                if avg_prev_5_areas < avg_first_5_areas:
                    return "likely retrogress"
                return "right"
            else:
                if avg_prev_5_areas > avg_first_5_areas:
                    return "likely retrogress"
                return "left"
        return None
