import cv2
import numpy as np


im1 = cv2.imread("123.png")
hsv_im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2HSV)
cv2.imwrite("hsv_123.png", hsv_im1)
print(hsv_im1)


# im2 = cv2.imread("321.png")
# np2 = np.array(im2)
#
# print(np2)