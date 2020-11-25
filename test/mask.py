import cv2
import numpy as np

img = cv2.imread("test_from_video.jpg")
vertices = [
    (100, 100),
    (200, 200),
    (200, 100)
]

mask = np.zeros_like(img)
channel_count = img.shape[2]
match_mask_color = (255,) * channel_count
cv2.fillPoly(mask, np.array([vertices], np.int32), match_mask_color)
masked_img = cv2.bitwise_and(img, mask)

cv2.imshow("img", img)
cv2.imshow("mask", mask)
cv2.imshow("masked_img", masked_img)


cv2.waitKey(0)
