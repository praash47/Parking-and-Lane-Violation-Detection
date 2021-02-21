from tkinter import messagebox

# Local Modules ##
from misc.settings import *


class Lanes:
    """
    Lanes module for managing lanes.
    """

    def __init__(self, detection_object):
        self.object = detection_object

        # Lane Lines Initializations #
        self.lanes_list = []
        self.left_lane_line1 = None
        self.left_lane_line2 = None
        self.right_lane_line1 = None
        self.right_lane_line2 = None

        # Hough Transform Initializations #
        self.hough_img = None
        self.hough_crop_range_left = None
        self.hough_crop_range_right = None

        # Lane Areas Initializations #
        self.left_lane_area = None
        self.right_lane_area = None

    def houghTransform(self):
        """
        Pre-processing required for hough transform, and canny edge detection
        """
        frame_width = int(self.object.video.width)
        frame_height = int(self.object.video.height)
        mid_x = int(frame_width / 2)

        # Calculation of relative crop ranges for Hough
        self.hough_crop_range_left = abs(self.hough_crop_range_left[0] - mid_x)
        self.hough_crop_range_right = abs(self.hough_crop_range_right[0] - mid_x)

        self.hough_img = self.object.video.getThumbnail(non_tk=True)
        # Cropping according to hough requirements
        hough_crop = self.hough_img[self.object.road_roi_left[1]: frame_height, mid_x - self.hough_crop_range_left:
                                                                                mid_x + self.hough_crop_range_right]

        # Pre-processing for Hough: Canny Edge Detection
        edges = cv2.Canny(hough_crop, canny_threshold1, canny_threshold2, apertureSize=canny_aperture_size)

        # The main Hough Transform call
        self.hough(edges, mid_x)

    def hough(self, edges, m):
        """
        The main hough transform

        :param edges: edges obtained from the canny edge detection
        :param m: midpoint of the frame
        """
        lines = cv2.HoughLinesP(edges, hough_rho, hough_theta, hough_threshold, minLineLength=hough_min_line_length,
                                maxLineGap=hough_max_line_gap)
        try:
            # Adjusting of the co-ordinates
            lines = self.adjustCoordinates(lines)
            for line in lines:
                # Changing from hough frame co-ordinates to large frame co-ordinate
                x1, y1, x2, y2 = line[0], line[1], line[2], line[3]
                rel_x1 = m - self.hough_crop_range_left + x1
                rel_x2 = m - self.hough_crop_range_left + x2
                rel_y1 = self.object.road_roi_left[1] + y1
                rel_y2 = self.object.road_roi_left[1] + y2
                # Append to the lanes list; rough list of lanes
                self.lanes_list.append([rel_x1, rel_y1, rel_x2, rel_y2])

        except TypeError:  # No any lines in specified location
            messagebox.showerror(title="Closing Program",
                                 message="Either you selected a video of non-matched format or hough is not able to "
                                         "detect "
                                         "any lines.")
            raise ValueError(
                "Either you selected a video of non-matched format or hough is not able to detect any lines.")

    @staticmethod
    def adjustCoordinates(lines):
        """
        The function adjust co-ordinates such that the bottom co-ordinates of the line are exchanged with top ones so
        as to maintain the consistency of top and bottom co-ordinates which is not maintained by raw Hough Transform

        :param lines: lines list
        :return: adjusted list of lines (ascending order)
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

    def separateLaneLines(self):
        """
        This function separate lane lines into self.left_lane_line1, left_lane_line2, right_lane_line1 &
        right_lane_line2
        """
        if len(self.lanes_list) >= 4:
            # If number of lines only greater than or equal to 4, then proceed.
            if len(self.lanes_list) > 4:
                # If greater than four, then pop.
                for index, lane in enumerate(self.lanes_list):
                    if lane[0] == lane[2]:
                        self.lanes_list.pop(index)
            # Keep the lanes in order
            lanes_order = [self.lanes_list[0][0], self.lanes_list[1][0], self.lanes_list[2][0], self.lanes_list[3][0]]
            # Sort in ascending order
            lanes_order.sort()
            # Assign to each lane_line variable.
            self.left_lane_line1 = self.getLaneLine(lanes_order.pop(0))
            self.left_lane_line2 = self.getLaneLine(lanes_order.pop(0))
            self.right_lane_line1 = self.getLaneLine(lanes_order.pop(0))
            self.right_lane_line2 = self.getLaneLine(lanes_order.pop(0))
            # Create dictionary format for lanes (easy readability)
            self.formatLaneLinesProperly()
            # Extend Lane Lines to the top of the frame and bottom of the frame
            self.extendLaneLines()
        else:
            # Case of Not Enough Lines by Hough
            messagebox.showwarning(title="Not Enough Lines By Hough",
                                   message="There is not enough lines by hough. Selecting ROI properly may work.")
            self.object.roiSpecification()
            self.houghTransform()
            self.separateLaneLines()

    def getLaneLine(self, x):
        """
        This function returns lane line one by one
        :param x: lanes_list
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

        for each line, it is extended, according to the property of the co-ordinates, the lines are either extended
        from the top or from the bottom.
        """
        lanes_list = [self.left_lane_line1, self.left_lane_line2, self.right_lane_line1, self.right_lane_line2]
        # top and bottom check and extension if short for each line.
        for lane in lanes_list:
            dy = abs(lane['bottomy'] - lane['topy'])
            dx = abs(lane['topx'] - lane['bottomx'])
            # Extending to the top
            if lane['topy'] > self.object.road_roi_left[1]:
                self.extendLaneLine(lane, dy, dx, self.object.road_roi_left[1])
            # Extending to the bottom
            if lane['bottomy'] < self.object.video.height:
                self.extendLaneLine(lane, dy, dx, self.object.video.height, up=False)

    @staticmethod
    def extendLaneLine(lane, dy, dx, upto, up=True):
        """
        Line extension to the top or bottom with the use of DDA for extension
        :param lane:
        :param dy: variation of y range of the lane
        :param dx: variation of x range of the lane
        :param upto: point upto which line to be extended
        :param up: True if we are extending to top, if bottom, False
        :return: void
        """
        # DDA
        if dy > dx:
            steps = dy
        else:
            steps = dx
        yinc = dy / steps
        xinc = dx / steps
        # If you want to the extend to the top, then assign x and y to the topy and topx
        if up:
            y = lane['topy']
            x = lane['topx']
        # If you want to the extend to the bottom, then assign x and y to the bottomx and bottomy
        else:
            y = lane['bottomy']
            x = lane['bottomx']
        while y != upto:
            if up:
                # Start extending to the top
                y -= yinc
                x -= xinc
            else:
                # Start extending to the bottom
                y += yinc
                x += xinc
        if up:
            # After reaching to the top, assign back to the top variables
            lane['topx'], lane['topy'] = int(round(x, 0)), int(round(y, 0))
        else:
            # After bottom, to the bottom variables.
            lane['bottomx'], lane['bottomy'] = int(round(x, 0)), int(round(y, 0))

    def formatLaneLinesProperly(self):
        """
        Formatting lanes line for readability one at a time.
        """
        self.left_lane_line1 = self.formatLaneLine(self.left_lane_line1)
        self.left_lane_line2 = self.formatLaneLine(self.left_lane_line2)
        self.right_lane_line1 = self.formatLaneLine(self.right_lane_line1)
        self.right_lane_line2 = self.formatLaneLine(self.right_lane_line2)

    @staticmethod
    def formatLaneLine(lane):
        """
        Separate co-ordinates using dictionary for readability.
        :param lane: the lane to be formatted on
        :return: dictionary of the formatted lane
        """
        return {'bottomx': lane[0], 'bottomy': lane[1], 'topx': lane[2], 'topy': lane[3]}

    def separateLaneAreas(self):
        """
        separate lane areas and assign to lane area variables
        """
        self.left_lane_area = self.separateLaneArea()
        self.right_lane_area = self.separateLaneArea(left=False)
        self.showLaneAreas()

    def separateLaneArea(self, left=True):
        """
        Separating Lane Areas on the basis of lane lines so detected and road top left, right
        and bottom of screen co-ordinates.

        :param left: It specifies lane is left lane or right lane
        :return: dictionary with tuples for top-left, top-right, bottom-left and bottom-right
        """
        # Assigning on the basis of left or right lane
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

    def showLaneLines(self):
        """
        Responsible for showing lane lines on masked frame.
        """
        lanes_list = [self.left_lane_line1, self.left_lane_line2, self.right_lane_line1, self.right_lane_line2]
        cv2.line(self.object.masked_frame, self.object.road_roi_left, self.object.road_roi_right,
                 lane_color, lane_thickness)
        for lane in lanes_list:
            cv2.line(self.object.masked_frame, (lane['topx'], lane['topy']), (lane['bottomx'], lane['bottomy']),
                     lane_color, lane_thickness)

    def showLaneAreas(self):
        """
        This function is responsible for showing separated lane areas. This is specially for testing purposes.
        It can be used anywhere to draw the lane areas on to the frame.

        - Uses polylines
        - Operates on hough_img for now.
        """
        # Make data ready for the polylines function.
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
