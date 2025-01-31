"""
这是一个从别人那里偷来的小程序，首先应该准备一张对应的图片，
然后运行时会弹出一个cv2窗口，鼠标单击任一窗口内区域，
会将该位置的HSV值打印于终端中
"""

import cv2

image = cv2.imread('hsv.png')
HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


def getpos(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # 定义一个鼠标左键按下去的事件
        print(HSV[y, x])


cv2.imshow("imageHSV", HSV)
cv2.setMouseCallback("imageHSV", getpos)
cv2.waitKey(0)

