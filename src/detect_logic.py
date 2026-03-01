import cv2
import numpy as np
import pyautogui

from config import YELLOW_LOW, YELLOW_HIGH


def get_yellow_area_range(region):
    """
    获取黄色区域左和右边界（可忽略玩家的白色方块遮挡）
    :param
        region: 从 config 中读取的预先记录的区域
    :return:
        min_x:  黄色区域的左边界，绝对坐标
        max_x:  黄色区域的右边界，绝对坐标
    """
    # 1.截图并转换为 HSV 颜色空间
    screenshot = pyautogui.screenshot(region=region)
    screenshot = np.array(screenshot)
    frame = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)

    # 2.读取并创建黄色的 mask
    mask = cv2.inRange(frame, YELLOW_LOW, YELLOW_HIGH)

    # 3.提取所有黄色像素的x坐标（忽略y坐标，只看水平方向）
    # 找到所有黄色像素的位置，mask == 255 表示为白色，即匹配的到的颜色
    _, x_coordinates = np.where(mask == 255)    # 我们只关心 X 坐标上，即左右的边界位置，所以忽略 Y
    if len(x_coordinates) == 0:
        return None  # 无黄色区域

    # 4.计算黄色区域的左和右边界（全局最小/最大x坐标）
    # 转换为屏幕绝对坐标，因为返回的是相对于截图区域的左上角的相对坐标
    min_x = np.min(x_coordinates) + region[0]
    max_x = np.max(x_coordinates) + region[0]

    return min_x, max_x

def get_white_block_pos(region):
    """
    获取代表玩家的白色方块的中心点
    :param region:  从 config 中读取的预先记录的区域
    :return:
        center_x:   代表玩家的白色方块的中心点，绝对坐标
    """
    screenshot = pyautogui.screenshot(region=region)
    screenshot = np.array(screenshot)
    frame = np.array(screenshot)

    # 2.提取白色掩码（RGB≥240，先粗筛白色区域）
    white_mask = np.all(frame >= 240, axis=2).astype(np.uint8) * 255

    # 3.形态学开运算（先腐蚀后膨胀）：去除小噪点，保留连续轮廓
    kernel = np.ones((2, 2), np.uint8)
    white_mask_clean = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)

    # 4.查找所有外部轮廓（只找最外层，排除嵌套轮廓）
    contours, _ = cv2.findContours(
        white_mask_clean,
        cv2.RETR_EXTERNAL,  # 只提取最外层轮廓
        cv2.CHAIN_APPROX_SIMPLE  # 压缩轮廓点，减少计算
    )
    if len(contours) == 0:
        return None

    # 5.定义目标白色方块的特征筛选条件（关键！根据游戏画面微调）
    target_contour = None
    h, w = frame.shape[:2]  # 截图的高、宽
    for cnt in contours:
        # 计算轮廓的外接矩形（x,y是相对截图的坐标；w_cnt=宽，h_cnt=高）
        x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(cnt)

        # 筛选条件1：面积范围（排除太小/太大的轮廓，单位：像素）
        area = cv2.contourArea(cnt)
        if not (10 <= area <= 100):  # 目标方块面积通常在10-200像素（可微调）
            continue

        # 筛选条件2：轮廓的实心度（排除空心/零散轮廓）
        # 实心度=轮廓面积/外接矩形面积，越接近1越接近实心矩形
        solidity = area / (w_cnt * h_cnt) if (w_cnt * h_cnt) > 0 else 0
        if solidity < 0.5:  # 实心度≥0.5（可微调）
            continue

        # 所有条件满足，确定为目标轮廓
        target_contour = cnt
        break  # 找到目标后直接退出循环

    # 6.无符合条件的轮廓，返回None
    if target_contour is None:
        return None

    # 7.计算目标轮廓的中心点（相对截图）
    x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(target_contour)
    center_x_rel = x_cnt + w_cnt / 2  # 轮廓外接矩形的中心x

    # 8.转换为屏幕绝对坐标
    center_x_abs = region[0] + center_x_rel
    return center_x_abs

if __name__ == '__main__':
    print("ok")