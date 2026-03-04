import cv2
import numpy as np
import pyautogui

from config import YELLOW_LOW, YELLOW_HIGH, FISH_GAME_REGION, WHITE_BLOCK_AREA_MIN, WHITE_BLOCK_AREA_MAX, \
    WHITE_BLOCK_SOLIDITY


def capture_and_convert(region=FISH_GAME_REGION):
    """为减少重复代码提取的共同方法，截图并返回所需要的格式

    :param region: 从 config 中读取的截图区域
    :returns:
        bgr_frame: 经过 np 处理后的 BGR 格式截图
        hsv_frame: 经过 np 处理后的 HSV 格式截图
        region_x: 截图区域的左边界在屏幕上的位置x，相对坐标下x=0
    """
    # 新增参数校验
    if not isinstance(region, (tuple, list)) or len(region) != 4:
        raise ValueError("region参数必须是(x, y, width, height)格式的元组/列表")
    if any(v < 0 for v in region):
        raise ValueError("region参数的数值不能为负数")

    screenshot = pyautogui.screenshot(region=region)
    screenshot = np.array(screenshot)
    bgr_frame = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    hsv_frame = cv2.cvtColor(screenshot, cv2.COLOR_RGB2HSV)
    region_x = region[0]

    return bgr_frame, hsv_frame, region_x


def get_yellow_area_range():
    """
    获取黄色区域左和右边界（可忽略玩家的白色方块遮挡）
    :returns:
        min_x: 黄色区域的左边界，绝对坐标
        max_x: 黄色区域的右边界，绝对坐标
    """
    # 截图并转换为 HSV 颜色空间
    _, hsv_frame, region_x = capture_and_convert()

    # 读取并创建黄色的 mask
    mask = cv2.inRange(hsv_frame, YELLOW_LOW, YELLOW_HIGH)

    # 提取所有黄色像素的x坐标（忽略y坐标，只看水平方向）
    # 找到所有黄色像素的位置，mask == 255 表示为白色，即匹配的到的颜色
    # 我们只关心 x 坐标上，即左右的边界位置，所以忽略 y
    _, x_coordinates = np.where(mask == 255)
    if len(x_coordinates) == 0:  # 无黄色区域
        return None

    # 计算黄色区域的左边界和右边界（最小和最大 x 坐标）
    # 需转换为屏幕绝对坐标，因为返回的是相对于截图区域最左侧的相对坐标
    min_x = np.min(x_coordinates) + region_x
    max_x = np.max(x_coordinates) + region_x

    return min_x, max_x


def get_white_block_pos():
    """
    获取代表玩家的白色方块的中心点
    :return: center_x: 代表玩家的白色方块的中心点，绝对坐标
    """
    # 白色方块不适用 HSV 格式，改用 BGR
    bgr_frame, _, region_x = capture_and_convert()

    # 提取白色掩码
    white_mask = np.all(bgr_frame >= 240, axis=2).astype(np.uint8) * 255

    # 形态学开运算（先腐蚀后膨胀），去除小噪点，保留连续轮廓
    kernel = np.ones((2, 2), np.uint8)
    white_mask_clean = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)

    # 查找所有外部轮廓（只找最外层，排除嵌套轮廓）
    contours, _ = cv2.findContours(
        white_mask_clean,
        cv2.RETR_EXTERNAL,  # 只提取最外层轮廓
        cv2.CHAIN_APPROX_SIMPLE  # 压缩轮廓点，减少计算
    )
    # 无轮廓
    if len(contours) == 0:
        return None

    # 定义目标白色方块的特征筛选条件
    target_contour = None
    for cnt in contours:
        # 计算轮廓的外接矩形（x,y是相对截图的坐标；w_cnt=宽，h_cnt=高）
        x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(cnt)

        # 面积范围（排除太小/太大的轮廓，单位：像素，在 config 中调整）
        # 目标方块面积通常在10-200像素（可微调）
        area = cv2.contourArea(cnt)
        if not (WHITE_BLOCK_AREA_MIN <= area <= WHITE_BLOCK_AREA_MAX):
            continue

        # 轮廓的实心度（排除空心/零散轮廓）
        # 实心度=轮廓面积/外接矩形面积，越接近1越接近实心矩形
        # 实心度≥0.5（在 config 中调整）
        solidity = area / (w_cnt * h_cnt) if (w_cnt * h_cnt) > 0 else 0
        if solidity < WHITE_BLOCK_SOLIDITY:
            continue

        # 所有条件满足，确定为目标轮廓
        target_contour = cnt
        break  # 找到目标后直接退出循环

    # 无符合条件的轮廓，返回None
    if target_contour is None:
        return None

    # 计算目标轮廓相对截图的中心点
    x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(target_contour)
    center_x_rel = x_cnt + w_cnt / 2  # 轮廓外接矩形的中心x

    # 转换为屏幕绝对坐标
    center_x_abs = region_x + center_x_rel
    return center_x_abs
