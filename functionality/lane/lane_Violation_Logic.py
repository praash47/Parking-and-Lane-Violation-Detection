def laneCross(vehicle_object, detection_object):
    """
    Function that determines if lane has been crossed

    :param vehicle_object:
    :param detection_object:
    :return: boolean
    """
    in_lane = detection_object.lanes.determineLane(vehicle_object)
    print(in_lane)

    if vehicleWithinLanePerifery(vehicle_object, detection_object, in_lane):
        if in_lane == "left":
            dy = abs(detection_object.lanes.left_lane_line2['topy']-detection_object.lanes.left_lane_line2['bottomy'])
            dx = abs(detection_object.lanes.left_lane_line2['topx']-detection_object.lanes.left_lane_line2['bottomx'])
            if crossingLaneLine(vehicle_object.curr_bbox[2], vehicle_object.curr_bbox[3],
                                 detection_object.lanes.left_lane_line2, dy, dx):
                return True, "left"

        elif in_lane == "right":
            dy = abs(detection_object.lanes.right_lane_line1['topy']-detection_object.lanes.right_lane_line1['bottomy'])
            dx = abs(detection_object.lanes.right_lane_line1['topx']-detection_object.lanes.right_lane_line1['bottomx'])
            if crossingLaneLine(vehicle_object.curr_bbox[0], vehicle_object.curr_bbox[1],
                             detection_object.lanes.right_lane_line1, dy, dx, left_lane=False):
                return True, "right"
    if in_lane == "retrogress":
        return True, "likely retrogress"
    return False, None

def vehicleWithinLanePerifery(vehicle_object, detection_object, in_lane):
    """
    Determines when vehicle lies within lane lines periphery

    :param vehicle_object:
    :param detection_object:
    :param in_lane: in which lane is the vehicle
    :return:boolean
    """
    if in_lane == "left":
        if vehicle_object.curr_bbox[2] in range(detection_object.lanes.left_lane_line2['bottomx'],
                                                   detection_object.lanes.left_lane_line2['topx']+
                                                   (vehicle_object.curr_bbox[2]-vehicle_object.curr_bbox[0])):
            return True
    else:
        if int(vehicle_object.curr_bbox[0]) in range(detection_object.lanes.right_lane_line1['bottomx'] -
                                                   int(vehicle_object.curr_bbox[2] - vehicle_object.curr_bbox[0]),
                                                   detection_object.lanes.right_lane_line1['topx']):
            return True
    return False


def checkInLine(lane, dy, dx, upto, up=True):
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
    if up:
        y = lane[1]
        x = lane[0]
    else:
        y = lane[3]
        x = lane[2]
    while (y != upto):
        if up:
            y -= yinc
            x += xinc
        else:
            y += yinc
            x -= xinc
    return int(x), int(y)


def crossingLaneLine(x, y, lane, dy, dx, left_lane=True):
    # Determines whether lane line is crossed or not
    ex, ey = checkInLine(lane, dy, dx, y, up=False)
    if x > ex and left_lane:
        return True
    elif x < ex and not left_lane:
        return True
    return False


def checkRetrogress(vehicle_object, detection_object):
    # A function that confirms retrogress
    in_lane = detection_object.lanes.determineLane(vehicle_object)

    if in_lane == "likely retrogress":
        if (vehicle_object.prev_10_areas[0] < vehicle_object.prev_10_areas[3] or
            vehicle_object.prev_10_areas[0] < vehicle_object.prev_10_areas[5]) and \
            (vehicle_object.prev_10_areas[0] < vehicle_object.prev_10_areas[7] or
             vehicle_object.prev_10_areas[0] < vehicle_object.prev_10_areas[9]):
            return True

    return False
