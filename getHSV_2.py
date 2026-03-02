"""
这是我自己写的验证程序，确保我的HSV值范围无误。
本来还有一部分是用来验证从PIL图像先转换为np格式
再转换为HSV图的过程的，但是我已经删了
"""

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