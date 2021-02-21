import cv2


def checkVehicleLocation(lane_areas, vehicle):
    """
    Returns the location of vehicle by checking the bounding box and comparing with the lane areas.
    :param lane_areas: separated lane areas
    :param vehicle: vehicle object to check of
    :return: string of its location
    """
    # If vehicle's bounding box within right lane area
    if int(vehicle.curr_bbox[0]) in range(lane_areas.lanes.right_lane_area['top_left'][0] - 2,
                                          lane_areas.lanes.right_lane_area['top_right'][0]) \
            and int(vehicle.curr_bbox[2]) in range(lane_areas.lanes.right_lane_area['bottom_left'][0] - 2,
                                                   lane_areas.lanes.right_lane_area['bottom_right'][0]):
        return "Right Lane"

    # If vehicle's bounding box within left lane area
    elif int(vehicle.curr_bbox[0]) in range(lane_areas.lanes.left_lane_area['top_left'][0],
                                            lane_areas.lanes.left_lane_area['top_right'][0] + 2) \
            and int(vehicle.curr_bbox[2]) in range(lane_areas.lanes.left_lane_area['bottom_left'][0],
                                                   lane_areas.lanes.left_lane_area['bottom_right'][0] + 2):
        print(vehicle.curr_bbox[0], lane_areas.lanes.left_lane_area['top_left'][0],lane_areas.lanes.left_lane_area['top_right'][0] + 2)
        print(vehicle.curr_bbox[2], lane_areas.lanes.left_lane_area['bottom_left'][0], lane_areas.lanes.left_lane_area['bottom_right'][0] + 2)
        return "Left Lane"

    # If vehicles near to lane
    elif int(vehicle.curr_bbox[0]) in range(lane_areas.lanes.left_lane_area['bottom_right'][0] + 2,
                                            lane_areas.lanes.right_lane_area['bottom_left'][0] - 2) \
            or int(vehicle.curr_bbox[2]) in range(lane_areas.lanes.left_lane_area['bottom_right'][0] + 2,
                                                  lane_areas.lanes.right_lane_area['bottom_left'][0] - 2):
        return "Within Lane"

    # If vehicles within lanes location range
    elif int(vehicle.curr_bbox[0]) in range(lane_areas.lanes.left_lane_area['top_left'][0],
                                            lane_areas.lanes.left_lane_area['top_right'][0]) \
            and int(vehicle.curr_bbox[2]) in range(lane_areas.lanes.right_lane_area['bottom_left'][0],
                                                   lane_areas.lanes.right_lane_area['bottom_right'][0]):
        return "Overlapping Lane Lines"

    else:
        return "Unknown Location"


def checkToporBottomNear(lane, vehicle):
    """
    check whether top part is near to the vehicle relative to its current location, or the bottom part.
    :param lane: the current active lane for vehicle
    :param vehicle: vehicle object
    :return: Top or Bottom string based on it's location.
    """
    if abs(vehicle.curr_bbox[1] - lane['topy']) < abs(vehicle.curr_bbox[3] - lane['bottomy']):
        return "Top"
    return "Bottom"


def extendLaneLineUptoVehicle(obj, lane, extend_from, upto, up=True):
    """
    Extends Lane Line Upto Vehicle to detect if the current bounding box of the vehicle intersects the lane line or not.

    :param obj: detection object (Lane Violation Object)
    :param lane: which lane line to extend lane line upto vehicle on
    :param extend_from: from which part to extend lane line is passed from here
    :param upto: upto which part to extend lane line upto is mentioned here.
    :param up: Is the line to be extended upwards or downwards.
    :return: tuple of the location of lane line with respect to vehicle's y otherwise None, None
    """
    if upto in range(obj.road_roi_left[1], int(obj.video.height)):
        dy = abs(lane['topy'] - lane['bottomy'])
        dx = abs(lane['topx'] - lane['bottomx'])
        # A function to try and extend the lane line to the y co-ordinate mentioned in upto and return
        # the corresponding x and y for that upto
        if dy > dx:
            steps = dy
        else:
            steps = dx
        yinc = dy / steps
        xinc = dx / steps

        y = extend_from[1]
        x = extend_from[0]

        while y != upto:
            # Extend the line with the help of DDA algorithm.
            if up:
                y -= yinc
                x -= xinc
            else:
                y += yinc
                x += xinc
        return int(x), int(y)
    else:
        return None, None


def checkRetrogress(obj, vehicle, where_is_vehicle):
    """
    this function checks retrogress with the help of average areas of first 5 and previous 5 frames. A retrogressing
    object ought to show opposite characteristics of area increase or decrease according to the lane it is in.

    :param obj: Lane Violation Object
    :param vehicle: Vehicle Object
    :param where_is_vehicle: the current location of the vehicle
    :return: True on retrogress, False otherwise.
    """
    if vehicle.in_frame > 10:
        print(vehicle.id)
        old_area = sum(vehicle.prev_10_areas[:5]) / 5
        new_area = sum(vehicle.prev_10_areas[-5:]) / 5
        print(vehicle.id, where_is_vehicle)
        if where_is_vehicle == "Left Lane":
            # In left lane, the bounding box area of the vehicle shouldn't increase
            if new_area > old_area:
                print("Left lane retrogress")
                return True

        elif where_is_vehicle == "Right Lane":
            # In right lane, the bounding box area of the vehicle shouldn't decrease
            if new_area < old_area:
                print("Right Lane retrogress")
                return True

        # elif where_is_vehicle == "Within Lane":
        #     # If within lane periphery, that is just few distance away from the lane lines, then check much area on which
        #     # lane
        #     if muchAreaOn(obj, vehicle) == "Right":
        #         # If much area is on right, we check if the vehicle has accomplished by retrogressing.
        #         if checkCrossedLaneLineToOtherSide(obj, obj.lanes.right_lane_line1, vehicle, "Right"):
        #             return True
        #     elif muchAreaOn(obj, vehicle) == "Left":
        #         # If much area is on left, we check if the vehicle has accomplished by retrogressing.
        #         if checkCrossedLaneLineToOtherSide(obj, obj.lanes.left_lane_line2, vehicle, "Left"):
        #             return True

    return False


def checkCrossedLaneLineToOtherSide(obj, lane, vehicle, much_area_on):
    """
    :rtype: True if vehicle has retrogressed being near to the lane lines.
    """
    # First, check from which side the vehicle is near to.
    near_from = checkToporBottomNear(lane, vehicle)

    corresp_x, corresp_y, extend_from = None, None, None
    # Try extending line from the top or bottom according to which side is near.
    if near_from == "Top":
        extend_from = (lane['topx'], lane['topy'])
        corresp_x, corresp_y = extendLaneLineUptoVehicle(obj, lane, extend_from, int(vehicle.curr_bbox[1]), up=False)
    elif near_from == "Bottom":
        extend_from = (lane['bottomx'], lane['bottomy'])
        corresp_x, corresp_y = extendLaneLineUptoVehicle(obj, lane, extend_from, int(vehicle.curr_bbox[3]))
    if corresp_x is not None and corresp_y is not None:
        cv2.line(obj.masked_frame, extend_from, (corresp_x, corresp_y), (0, 0, 0), 2)
        if much_area_on == "Right":
            # If the much area is on right and the leftmost part of the vehicle is greater than the x of the extended
            # lane line, then it's obviously retrogress
            if vehicle.curr_bbox[0] > corresp_x:
                return True
        elif much_area_on == "Left":
            # If the much area is on left and the rightmost part of the vehicle is less than the x of the extended lane
            # line, then it's obviously retrogress
            if vehicle.curr_bbox[2] < corresp_x:
                return True

    return False


def muchAreaOn(obj, vehicle):
    """
    checks in which lane area, most of the area portion of the vehicle lies on.

    :param obj: Lane Violation Object
    :param vehicle: Vehicle Object
    :return:
    """
    width = vehicle.curr_bbox[2] - vehicle.curr_bbox[0]
    # The left determiner quarter is in the right 3/4 part of the vehicle
    left_determiner_quarter = int(3 * (width / 4) + vehicle.curr_bbox[0])
    # The right determiner quarter is in the left 1/4 part of the vehicle
    right_determiner_quarter = int(width / 4 + vehicle.curr_bbox[0])

    # If the right quarter of the vehicle is within the range of
    if right_determiner_quarter in range(obj.lanes.right_lane_area['top_left'][0],
                                         obj.lanes.right_lane_area['top_right'][0]):
        return "Right"

    elif left_determiner_quarter in range(obj.lanes.left_lane_area['top_left'][0],
                                          obj.lanes.left_lane_area['top_right'][0]):
        return "Left"

    else:
        return "unknown"
