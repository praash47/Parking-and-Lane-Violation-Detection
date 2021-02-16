import cv2
import numpy as np

def seperateLanes(lanes_list):
    lanes_order = [lanes_list[0][0], lanes_list[1][0], lanes_list[2][0], lanes_list[3][0]]
    lanes_order.sort()
    left_lane1 = getLane(lanes_list, lanes_order.pop(0))
    left_lane2 = getLane(lanes_list, lanes_order.pop(0))
    right_lane1 = getLane(lanes_list, lanes_order.pop(0))
    right_lane2 = getLane(lanes_list, lanes_order.pop(0))
    return left_lane1, left_lane2, right_lane1, right_lane2


def getLane(lanes_list, x):
    found = None
    for index, lane in enumerate(lanes_list):
        if lane[0] == x:
            found = index
    return lanes_list.pop(found)

def extendLine(lane, dy, dx, upto, up=True):
    if dy > dx:
        steps = dy
    else:
        steps = dx
    yinc = dy/steps
    xinc = dx/steps
    if up:        
        y = lane[1]
        x = lane[0]
    else:
        y = lane[3]
        x = lane[2]
    while (y != upto):
        if up:
            print(x,y)
            y -= yinc
            x -= xinc
        else:
            y += yinc
            x += xinc
    return int(x),int(y)

def checkInLine(lane, dy, dx, upto, up=True):
    steps = None
    if dy > dx:
        steps = dy
    else:
        steps = dx
    yinc = dy/steps
    xinc = dx/steps
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
    return (int(x),int(y))
        

def in_line(x, y, lane, dy, dx, left_lane=True):
    top = (lane[2], lane[3])
    ex, ey = checkInLine(lane, dy, dx, y, up=False)
    if x > ex and left_lane:
        return True
    elif x < ex and not left_lane:
        return True
    return False

def seperateLaneArea(top, shape_of_image, top1, bottom1, top2, bottom2):
    print(top, shape_of_image, top1, bottom1, top2, bottom2)
    left_lane_area = [top[0], top1,(1, bottom1[1]), bottom1]
    right_lane_area = [top2, top[1], bottom2, (shape_of_image[0]-1, bottom2[1])]
    return left_lane_area, right_lane_area


x1, y1, x2, y2 = 350, 320, 400, 370
bbox = [x1, y1, x2, y2]

top_left = (200,1)
top_right = (425,1)

img=cv2.imread("test_from_video.jpg")
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
mid_x = int(img.shape[1] / 2)
height = img.shape[0]
crop_x1 = mid_x-65
crop_x2 = mid_x+50
crop_image=img[0:height,crop_x1:crop_x2]
("crop",crop_image)
edges=cv2.Canny(crop_image,50,150,apertureSize=3)
("canny",edges)
lines=cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)
lines_list = []
for index, line in enumerate(lines):
    x1,y1,x2,y2=line[0]
    cv2.line(crop_image,(x1,y1),(x2,y2),(0,255,0),1)
    cv2.line(img,(mid_x-65+x1,y1),(mid_x-65+x2,y2),(0,255,0),1)
    print(mid_x-65+x1, y1, mid_x-65+x2, y2)
    lines_list.append([mid_x-65+x1,y1,mid_x-65+x2,y2])

("before extend image",img)

left_lane1, left_lane2, right_lane1, right_lane2 = seperateLanes(lines_list)
print(left_lane1, left_lane2, right_lane1, right_lane2)
# lanes_list = [left_lane1, left_lane2, right_lane1, right_lane2]
#
# for lane in lanes_list:
#     dy = abs(lane[3]-lane[1])
#     dx = abs(lane[2]-lane[0])
#     if lane[3] > top_left[1]:
#         lane[2], lane[3] = extendLine(lane, dy, dx, top_left[1])
#     if lane[1] < height:
#         lane[0], lane[1] = extendLine(lane, dy, dx, height, up=False)
#
# img2 = cv2.imread("test_from_video.jpg")
# for lane in lanes_list:
#     cv2.line(img2,(lane[0], lane[1]),(lane[2],lane[3]),(0,255,0),1)
#
# ("after extend image",img2)

dy1 = abs(right_lane1[3]-right_lane1[1])
dx1 = abs(right_lane1[2]-right_lane1[0])
bottom1 = extendLine(right_lane1, dy1, dx1, height, up=False)
cv2.line(img, (right_lane1[0],right_lane1[1]), bottom1, (255, 0, 255), 1)

dy2 = abs(left_lane1[3]-left_lane1[1])
dx2 = abs(left_lane1[2]-left_lane1[0])
top2 = (left_lane1[0], left_lane1[1])
bottom2 = extendLine(left_lane1, dy2, dx2, height, up=False)
cv2.line(img, top2, bottom2, (255, 0, 255), 1)

dy3 = abs(left_lane2[3]-left_lane2[1])
dx3 = abs(left_lane2[2]-left_lane2[0])
top3 = extendLine(left_lane2, dy3, dx3, 0)
bottom3 = extendLine(left_lane2, dy3, dx3, height, up=False)
cv2.line(img, top3, bottom3, (255, 0, 255), 1)
print(top3)

("after extend image",img)

# start_point_rect = (bbox[0], bbox[1])
# end_point_rect = (bbox[2], bbox[3])
# color = (255, 0, 255)
# thickness = 2
#
# img = cv2.line(img, top_left, top_right,(0,255,255),2)
# img = cv2.rectangle(img, start_point_rect, end_point_rect, color, thickness)
#
# left_lane_area, right_lane_area = seperateLaneArea((top_left, top_right), (img.shape[1], img.shape[0]), (left_lane1[2], left_lane1[3]), (left_lane1[0], left_lane1[1]), top2, bottom2) # width, height
#
# color = (255, 0, 255)
# left_lane_pts = np.array([[left_lane_area[3][0],left_lane_area[3][1]], [left_lane_area[2][0],left_lane_area[2][1]],
#                           [left_lane_area[1][0],left_lane_area[1][1]], [left_lane_area[0][0],left_lane_area[0][1]]])
# left_lane_pts.reshape(-1, 1, 2)
# img = cv2.polylines(img, [left_lane_pts], True, color)
# img = cv2.putText(img, "Left Lane", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
#
# color = (255, 0, 0)
# right_lane_pts = np.array([[right_lane_area[0][0],right_lane_area[0][1]], [right_lane_area[1][0],right_lane_area[1][1]],
#                           [right_lane_area[2][0],right_lane_area[2][1]], [right_lane_area[3][0],right_lane_area[3][1]]])
# right_lane_pts.reshape(-1, 1, 2)
# img = cv2.polylines(img, [right_lane_pts], True, color)
# img = cv2.putText(img, "Right Lane", (350, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
#
# if not bbox[2] in range(left_lane2[2]+(bbox[2]-bbox[0]), img.shape[1]):
#     left_lane_object = True
# else:
#     left_lane_object = False
#
#
# if left_lane_object:
#     print("left lane object")
#     if bbox[2] in range(left_lane2[0], left_lane2[2]+(bbox[2]-bbox[0])):
#         print("within line perifery or crossed")
#         dy = abs(left_lane2[3]-left_lane2[1])
#         dx = abs(left_lane2[2]-left_lane2[0])
#         is_in_line = in_line(bbox[2], bbox[3], left_lane2, dy, dx)
#         if is_in_line:
#             print("crossing left lane")
# else:
#     print("right lane object")
#     if bbox[0] in range(right_lane1[0]-(bbox[2]-bbox[0]), right_lane1[2]):
#         print("within line perifery or crossed")
#         dy = abs(right_lane1[3]-right_lane1[1])
#         dx = abs(right_lane1[2]-right_lane1[0])
#         is_in_line = in_line(bbox[0], bbox[1], right_lane1, dy, dx, left_lane=False)
#         if is_in_line:
#             print("crossing right lane")

k=cv2.waitKey(0)
cv2.destroyAllWindows()
