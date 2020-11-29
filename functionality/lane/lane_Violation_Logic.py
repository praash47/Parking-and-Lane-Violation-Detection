import cv2

def checkVehicleLocation(lane_areas, vehicle):
    if int(vehicle.curr_bbox[0]) in range(lane_areas.lanes.right_lane_area['top_left'][0], lane_areas.lanes.right_lane_area['top_right'][0]) \
        and int(vehicle.curr_bbox[2]) in range(lane_areas.lanes.right_lane_area['bottom_left'][0], lane_areas.lanes.right_lane_area['bottom_right'][0]):
        return "Right Lane"

    elif int(vehicle.curr_bbox[0]) in range(lane_areas.lanes.left_lane_area['top_left'][0], lane_areas.lanes.left_lane_area['top_right'][0]) \
        and int(vehicle.curr_bbox[2]) in range(lane_areas.lanes.left_lane_area['bottom_left'][0], lane_areas.lanes.left_lane_area['bottom_right'][0]):
        return "Left Lane"

    elif int(vehicle.curr_bbox[0]) in range(lane_areas.lanes.left_lane_area['bottom_right'][0], lane_areas.lanes.right_lane_area['bottom_left'][0]) \
        or int(vehicle.curr_bbox[2]) in range(lane_areas.lanes.left_lane_area['bottom_right'][0], lane_areas.lanes.right_lane_area['bottom_left'][0]):
        return "Within Lane"

    elif int(vehicle.curr_bbox[0]) in range(lane_areas.lanes.left_lane_area['top_left'][0], lane_areas.lanes.left_lane_area['top_right'][0]) \
        and int(vehicle.curr_bbox[2]) in range(lane_areas.lanes.right_lane_area['bottom_left'][0], lane_areas.lanes.right_lane_area['bottom_right'][0]):
        return "Overlapping Lane Lines"

    else:
        return "Unknown Location"

def checkToporBottomNear(lane, vehicle):
    if abs(vehicle.curr_bbox[1]-lane['topy']) < abs(vehicle.curr_bbox[3]-lane['bottomy']):
        return "Top"
    return "Bottom"


def extendLaneLineUptoVehicle(obj, lane, extend_from, upto, up=True):
    if upto in range(obj.road_roi_left[1], int(obj.video.height)):
        dy = abs(lane['topy'] - lane['bottomy'])
        dx = abs(lane['topx'] - lane['bottomx'])
        # TODO: to test
        # A function to try and extend the lane line to the y co-ordinate mentioned in upto and return
        # the corresponding x and y for that upto
        steps = None
        if dy > dx:
            steps = dy
        else:
            steps = dx
        yinc = dy / steps
        xinc = dx / steps

        y = extend_from[1]
        x = extend_from[0]

        while y != upto:
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
    avg_first_5_areas = sum(vehicle.prev_10_areas[:5]) / 5
    avg_prev_5_areas = sum(vehicle.prev_10_areas[-5:]) / 5
    if where_is_vehicle == "Left":
        if avg_first_5_areas < avg_prev_5_areas:
            return True

    elif where_is_vehicle == "Right":
        if avg_first_5_areas > avg_prev_5_areas:
            return True

    elif where_is_vehicle == "Within Lane":
        if muchAreaOn(obj, vehicle) == "Right":
            if checkCrossedLaneLineToOtherSide(obj, obj.lanes.right_lane_line1, vehicle, "Right"):
                return True
        elif muchAreaOn(obj, vehicle) == "Left":
            if checkCrossedLaneLineToOtherSide(obj, obj.lanes.left_lane_line2, vehicle, "Left"):
                return True

    return False

def checkCrossedLaneLineToOtherSide(obj, lane, vehicle, much_area_on):
    near_from = checkToporBottomNear(lane, vehicle)

    if near_from == "Top":
        extend_from = (lane['topx'], lane['topy'])
        corresp_x, corresp_y = extendLaneLineUptoVehicle(obj, lane, extend_from, int(vehicle.curr_bbox[1]), up=False)
    elif near_from == "Bottom":
        extend_from = (lane['bottomx'], lane['bottomy'])
        corresp_x, corresp_y = extendLaneLineUptoVehicle(obj, lane, extend_from, int(vehicle.curr_bbox[3]))
    if corresp_x is not None and corresp_y is not None:
        cv2.line(obj.masked_frame, extend_from, (corresp_x, corresp_y), (0, 0, 0), 2)
        if much_area_on == "Right":
            if vehicle.curr_bbox[2] < corresp_x:
                return True
        elif much_area_on == "Left":
            if vehicle.curr_bbox[2] > corresp_x:
                return True

    return False

def muchAreaOn(obj, vehicle):
    width = vehicle.curr_bbox[2] - vehicle.curr_bbox[0]
    left_quarter = int(width / 4 + vehicle.curr_bbox[0])
    right_quarter = int(3 * (width / 4) + vehicle.curr_bbox[0])

    if right_quarter in range(obj.lanes.right_lane_area['top_left'][0], obj.lanes.right_lane_area['top_right'][0]):
        return "Right"

    elif left_quarter in range(obj.lanes.left_lane_area['top_left'][0], obj.lanes.left_lane_area['top_right'][0]):
        return "Left"

    else:
        return "unknown"

# def laneCross(vehicle_object, detection_object):
#     """
#     Function that determines if lane has been crossed
#
#     :param vehicle_object:
#     :param detection_object:
#     :return: boolean
#     """
#     in_lane = detection_object.lanes.determineLane(vehicle_object)
#     print(in_lane)
#
#     if vehicleWithinLanePerifery(vehicle_object, detection_object, in_lane):
#         print("vehicle within ")
#         if in_lane == "left":
#             print("left")
#             dy = abs(detection_object.lanes.left_lane_line2['topy']-detection_object.lanes.left_lane_line2['bottomy'])
#             dx = abs(detection_object.lanes.left_lane_line2['topx']-detection_object.lanes.left_lane_line2['bottomx'])
#             # if crossingLaneLine(vehicle_object.curr_bbox[2], vehicle_object.curr_bbox[3],
#             #                      detection_object.lanes.left_lane_line2, dy, dx):
#             #     return True, "left"
#
#         elif in_lane == "right":
#             print("right")
#             dy = abs(detection_object.lanes.right_lane_line1['topy']-detection_object.lanes.right_lane_line1['bottomy'])
#             dx = abs(detection_object.lanes.right_lane_line1['topx']-detection_object.lanes.right_lane_line1['bottomx'])
#             # if crossingLaneLine(vehicle_object.curr_bbox[0], vehicle_object.curr_bbox[1],
#             #                  detection_object.lanes.right_lane_line1, dy, dx, left_lane=False):
#             #     return True, "right"
#         print(" lane periphery.")
#     return False, None
#
# def vehicleWithinLanePerifery(vehicle_object, detection_object, in_lane):
#     """
#     Determines when vehicle lies within lane lines periphery
#
#     :param vehicle_object:
#     :param detection_object:
#     :param in_lane: in which lane is the vehicle
#     :return:boolean
#     """
#     if in_lane == "left":
#         if int(vehicle_object.curr_bbox[2]) in range(detection_object.lanes.left_lane_line2['bottomx'],
#                                                    detection_object.lanes.left_lane_line2['topx']+
#                                                    int(vehicle_object.curr_bbox[2]-vehicle_object.curr_bbox[0])):
#             return True
#     else:
#         if int(vehicle_object.curr_bbox[0]) in range(detection_object.lanes.right_lane_line1['bottomx'] -
#                                                    int(vehicle_object.curr_bbox[2] - vehicle_object.curr_bbox[0]),
#                                                    detection_object.lanes.right_lane_line1['topx']):
#             return True
#     return False
#
#
# def checkInLine(lane, dy, dx, upto, up=True):
#     # TODO: to test
#     # A function to try and extend the lane line to the y co-ordinate mentioned in upto and return
#     # the corresponding x and y for that upto
#     steps = None
#     if dy > dx:
#         steps = dy
#     else:
#         steps = dx
#     yinc = dy / steps
#     xinc = dx / steps
#     if up:
#         y = lane['topy']
#         x = lane['topx']
#     else:
#         y = lane['bottomy']
#         x = lane['bottomx']
#     while (y != upto):
#         if up:
#             y -= yinc
#             x -= xinc
#         else:
#             y += yinc
#             x += xinc
#     return int(x), int(y)
#
#
# def crossingLaneLine(x, y, lane, dy, dx, left_lane=True):
#     # Determines whether lane line is crossed or not
#     ex, ey = checkInLine(lane, dy, dx, y, up=False)
#     if x > ex and left_lane:
#         return True
#     elif x < ex and not left_lane:
#         return True
#     return False
#
#
# def checkRetrogress(vehicle_object, detection_object):
#     # A function that confirms retrogress
#     in_lane = detection_object.lanes.determineLane(vehicle_object)
#
#     if in_lane == "likely retrogress":
#         if (vehicle_object.prev_10_areas[0] < vehicle_object.prev_10_areas[3] or
#             vehicle_object.prev_10_areas[0] < vehicle_object.prev_10_areas[5]) and \
#             (vehicle_object.prev_10_areas[0] < vehicle_object.prev_10_areas[7] or
#              vehicle_object.prev_10_areas[0] < vehicle_object.prev_10_areas[9]):
#             return True
#
#     return False
