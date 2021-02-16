import cv2
import numpy as np
import matplotlib.pylab as plt

def region_of_interest(img,vertices):
    mask=np.zeros_like(img)
    #channel_count=img.shape[2]
    match_mask_color=255
    cv2.fillPoly(mask,vertices,match_mask_color)
    masked_image=cv2.bitwise_and(img,mask)
    return masked_image

def draw_the_lines(img,lines):
    img=np.copy(img)
    blank_image=np.zeros((img.shape[0],img.shape[1],3),dtype=np.uint8)

    if lines is not None:
        for line in lines:
            print(line)
            for x1,y1,x2,y2 in line:
                cv2.line(blank_image,(x1,y1),(x2,y2),(0,255,0),thickness=3)

    img=cv2.addWeighted(img,0.8,blank_image,1,0.0)
    return img

def process(image):
    height=image.shape[0]
    width=image.shape[1]

    region_of_interest_vertices=[
        (700,height),
        (450,300),
        (1100,height)
    ]
    gray_image=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    canny_image=cv2.Canny(gray_image,100,200)
    cropped_image=region_of_interest(canny_image,np.array([region_of_interest_vertices],np.int32))

    lines=cv2.HoughLinesP(cropped_image,
                          rho=6,
                          theta=np.pi/60,
                          threshold=160,
                          lines=np.array([]),
                          minLineLength=40,
                          maxLineGap=25)
    image_with_lines=draw_the_lines(image,lines)
    return image_with_lines

cap=cv2.VideoCapture("acc.mp4")
##
x1, y1, x2, y2 = 100, 100, 150, 150
##x1, x2, y1, y2 = 400, 500, 200, 300
bbox = [x1, y1, x2, y2]
prev_bbox = []

n_frames = 0
while(cap.isOpened()):
    ret,frame=cap.read()
    frame=process(frame)
    start_point = (325, 0)
    start_point2 = (335, 0)
  
    # End coordinate, here (250, 250) 
    # represents the bottom right corner of image 
    end_point = (320, 360) 
    end_point2 = (350, 360) 
      
    # White color in BGR 
    color = (255, 255, 255) 
      
    # Line thickness of 9 px 
    thickness = 9

    frame=cv2.line(frame, start_point, end_point, color, thickness)
    frame=cv2.line(frame, start_point2, end_point2, color, thickness)
    start_point_rect = (bbox[0], bbox[1])
    end_point_rect = (bbox[2], bbox[3])

    color = (255, 0, 255)
    left_lane_pts = np.array([[0,0], [0,360], [start_point[0], start_point[1]], [end_point[0], end_point[1]]])
    left_lane_pts.reshape(-1, 1, 2)
    frame = cv2.polylines(frame, [left_lane_pts], True, color)
    frame = cv2.putText(frame, "Left Lane", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    color = (255, 0, 0)
    right_lane_pts = np.array([[frame.shape[1],0], [frame.shape[1],360], [start_point2[0], start_point2[1]], [end_point2[0], end_point2[1]]])
    right_lane_pts.reshape(-1, 1, 2)
    frame = cv2.polylines(frame, [right_lane_pts], True, color)
    frame = cv2.putText(frame, "Right Lane", (300, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    width = abs(bbox[2]-bbox[0])
    height = abs(bbox[3]-bbox[1])
    area = width * height
    print(area)
    prev_bbox.append([bbox[0],bbox[1],bbox[2],bbox[3]])
    n_frames += 1
    if n_frames>=10:
        n_frames = 0
        bbox[0]-=1
        bbox[1]-=1
        bbox[2]+=1
        bbox[3]+=1
        if prev_bbox[0][0]>bbox[0] and prev_bbox[0][1]>bbox[1] and prev_bbox[0][2]<bbox[2] and prev_bbox[0][3]<bbox[3]:
            print("Vehicle Retrogress in Left Lane")
##        bbox[0]+=1
##        bbox[1]+=1
##        bbox[2]-=1
##        bbox[3]-=1
##        if prev_bbox[0][0]<bbox[0] and prev_bbox[0][1]<bbox[1] and prev_bbox[0][2]>bbox[2] and prev_bbox[0][3]>bbox[3]:
##            print("Vehicle Retrogress in Right Lane")

    color = (255, 255, 0)    
    frame = cv2.rectangle(frame, start_point_rect, end_point_rect, color, thickness)
    ('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
