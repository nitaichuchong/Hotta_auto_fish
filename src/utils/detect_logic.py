"""检测逻辑模块

提供图像检测功能，包括截图、颜色检测和轮廓识别。
"""
from typing import Optional, Tuple

import cv2
import numpy as np

from config import YELLOW_LOW, YELLOW_HIGH, FISH_GAME_REGION, WHITE_BLOCK_AREA_MIN, WHITE_BLOCK_AREA_MAX, \
    WHITE_BLOCK_SOLIDITY
from src.utils.dxgi_capture_manager import get_dxgi_manager
from src.utils.mss_capture_manager import get_mss_manager
from src.utils.window_manager import is_window_foreground

# 全局截图禁用标志
_screenshot_disabled: bool = False


def disable_screenshots() -> None:
    """禁用所有截图操作
    
    在线程停止时调用此函数，防止新的截图请求。
    """
    global _screenshot_disabled
    _screenshot_disabled = True


def enable_screenshots() -> None:
    """启用截图操作
    
    恢复截图功能，允许进行图像捕获。
    """
    global _screenshot_disabled
    _screenshot_disabled = False


def capture_and_convert(region: Tuple[int, int, int, int] = FISH_GAME_REGION) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[int]]:
    """捕获屏幕图像并转换为所需格式
    
    根据窗口状态选择合适的截图方式（MSS 或 DXGI），并返回 BGR 和 HSV 格式的图像。
    
    Args:
        region (Tuple[int, int, int, int]): 截图区域，格式为 (x, y, width, height)。
        
    Returns:
        Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[int]]: 
            (bgr_frame, hsv_frame, region_x)
            - bgr_frame: BGR 格式的截图（失败时返回 None）
            - hsv_frame: HSV 格式的截图（失败时返回 None）
            - region_x: 截图区域左边界在屏幕上的 x 坐标（失败时返回 None）
            
    Raises:
        ValueError: 当 region 参数格式不正确或包含负数时抛出。
    """
    # 新增参数校验
    if not isinstance(region, (tuple, list)) or len(region) != 4:
        raise ValueError("region 参数必须是 (x, y, width, height) 格式的元组/列表")
    if any(v < 0 for v in region):
        raise ValueError("region 参数的数值不能为负数")

    # 检查是否已禁用截图
    if _screenshot_disabled:
        print("截图已禁用，跳过")
        return None, None, None

    try:
        # 若窗口位于前台，需要使用 mss 进行截图，否则游戏会阻止获取画面，属于防作弊机制
        if is_window_foreground("幻塔  "):
            # 每次创建新的 MSS 实例，用完即销毁
            mss_capture = get_mss_manager()
            bgr_frame = mss_capture.capture(region)
            # 立即清理资源
            mss_capture.cleanup()
        else:
            # 后台使用 dxgi，此时防作弊机制不生效，可以正常获取画面
            # 使用 DXGI 单例管理器
            dxgi_capture = get_dxgi_manager()

            # 检查 DXGI 是否可用
            if not hasattr(dxgi_capture, 'dxgi_capture') or dxgi_capture.dxgi_capture is None:
                # print("DXGI 尚未准备好，跳过本次截图")
                return None, None, None

            bgr_frame = dxgi_capture.capture(region)

        if bgr_frame is None:
            # print("未成功捕获图像，无法进行后续处理")
            return None, None, None

        hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)
        region_x = region[0]
        return bgr_frame, hsv_frame, region_x

    except Exception as e:
        # print(f"截图失败：{e}")
        return None, None, None


def get_yellow_area_range() -> Optional[Tuple[int, int]]:
    """获取黄色区域的左右边界
    
    检测体力条中的黄色区域，返回其左右边界的绝对坐标。
    
    Returns:
        Optional[Tuple[int, int]]: (min_x, max_x) 黄色区域的左右边界绝对坐标，
                                  如果未检测到则返回 None。
    """
    # 截图并转换为 HSV 颜色空间
    _, hsv_frame, region_x = capture_and_convert()

    if hsv_frame is None:
        return None

    # 读取并创建黄色的 mask
    mask = cv2.inRange(hsv_frame, YELLOW_LOW, YELLOW_HIGH)

    # 提取所有黄色像素的 x 坐标（忽略 y 坐标，只看水平方向）
    # 找到所有黄色像素的位置，mask == 255 表示为白色，即匹配到的颜色
    # 我们只关心 x 坐标上，即左右的边界位置，所以忽略 y
    _, x_coordinates = np.where(mask == 255)
    if len(x_coordinates) == 0:  # 无黄色区域
        return None

    # 计算黄色区域的左边界和右边界（最小和最大 x 坐标）
    # 需转换为屏幕绝对坐标，因为返回的是相对于截图区域最左侧的相对坐标
    min_x = np.min(x_coordinates) + region_x
    max_x = np.max(x_coordinates) + region_x

    return min_x, max_x


def get_white_block_pos() -> Optional[int]:
    """获取代表玩家的白色方块的中心点
    
    通过轮廓检测识别代表玩家位置的白色方块，返回其中心点的绝对坐标。
    
    Returns:
        Optional[int]: 白色方块中心点的 x 坐标绝对坐标，如果未检测到则返回 None。
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
        # 计算轮廓的外接矩形（x,y 是相对截图的坐标；w_cnt=宽，h_cnt=高）
        x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(cnt)

        # 面积范围（排除太小/太大的轮廓，单位：像素，在 config 中调整）
        # 目标方块面积通常在 10-200 像素（可微调）
        area = cv2.contourArea(cnt)
        if not (WHITE_BLOCK_AREA_MIN <= area <= WHITE_BLOCK_AREA_MAX):
            continue

        # 轮廓的实心度（排除空心/零散轮廓）
        # 实心度=轮廓面积/外接矩形面积，越接近 1 越接近实心矩形
        # 实心度≥0.5（在 config 中调整）
        solidity = area / (w_cnt * h_cnt) if (w_cnt * h_cnt) > 0 else 0
        if solidity < WHITE_BLOCK_SOLIDITY:
            continue

        # 所有条件满足，确定为目标轮廓
        target_contour = cnt
        break  # 找到目标后直接退出循环

    # 无符合条件的轮廓，返回 None
    if target_contour is None:
        return None

    # 计算目标轮廓相对截图的中心点
    x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(target_contour)
    center_x_rel = x_cnt + w_cnt / 2  # 轮廓外接矩形的中心 x

    # 转换为屏幕绝对坐标
    center_x_abs = region_x + center_x_rel
    return center_x_abs
