# 捕获屏幕截图
import cv2
import numpy as np
from PIL import ImageGrab


def capture_screen(region=None):
    """
    截取屏幕截图并进行初步处理
    :param region: 需要截取的区域，为空时表示全屏截取
    :return: 返回经过处理后的符合 openCV 格式的截图
    """
    if region:
        # 捕获指定区域的屏幕截图
        screenshot = ImageGrab.grab(bbox=region)
    else:
        # 捕获整个屏幕的截图
        screenshot = ImageGrab.grab()

    # 将PIL图像转换为OpenCV格式
    screenshot_np = np.array(screenshot)
    # 注意：ImageGrab捕获的图像是RGB格式的，但OpenCV默认使用BGR格式
    # 因此，我们需要将RGB转换为BGR
    screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    return screenshot_np


def convert_to_hsv(image):
    """
    将图像转换为HSV颜色空间
    :param image: 需要进行处理的图片，这里为转换后的 screen
    :return: 转换为 HSV 颜色空间的图片
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


def find_contours(image):
    """
    寻找白色方块轮廓
    :param image: 需要进行处理的图片，这里为转换后的 screen
    :return: None 或白色方块的 rect 信息
    """
    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用二值化处理
    _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)

    # 检测轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 过滤轮廓（这里以面积为例）
    min_area = 20  # 设置最小面积阈值
    white_block_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_area:  # 面积大于最小阈值，认为是白色方块的轮廓
            white_block_contour = contour
            break  # 找到第一个符合条件的轮廓即停止搜索（假设只有一个白色方块）

    # 如果找到了白色方块的轮廓，则确定其位置
    if white_block_contour is not None:
        x, y, w, h = cv2.boundingRect(white_block_contour)
        rect = (x, y, w, h)
        return rect


def count_yellow_pixels(hsv_image, rect):
    """
    获取白色方块信息后，先确定左右两侧区域的位置和大小，然后根据测出的
    HSV 范围创建掩码，以计算左右两侧区域的黄色像素数量
    :param hsv_image: 需要进行处理的图片，这里为 HSV 颜色空间处理后的 screen
    :param rect: 白色方块的信息
    :return: 左右两侧黄色像素的数量
    """
    # 提取白色方块左右两侧的区域
    x, y, w, h = rect
    half_w = w // 2
    left_region = hsv_image[0 : y+h, 0 : x+half_w]
    right_region = hsv_image[0 : y+h, x+half_w : 578]

    # 定义黄色像素的HSV范围（这些值可能需要根据实际情况调整）
    lower_yellow = np.array([18, 183, 235], dtype=np.uint8)
    upper_yellow = np.array([19, 191, 255], dtype=np.uint8)


    # 创建黄色像素的掩码
    mask_left = cv2.inRange(left_region, lower_yellow, upper_yellow)
    mask_right = cv2.inRange(right_region, lower_yellow, upper_yellow)

    # 计算左右两侧黄色像素的数量
    yellow_pixels_left = cv2.countNonZero(mask_left)
    yellow_pixels_right = cv2.countNonZero(mask_right)

    return yellow_pixels_left, yellow_pixels_right
