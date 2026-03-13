"""钓鱼自动控制模块

提供钓鱼自动化控制功能，包括按键检测和偏移计算。
"""
from typing import Optional

from config import OFFSET_THRESHOLD
from src.utils.detect_logic import get_yellow_area_range, get_white_block_pos


def key_to_press() -> str:
    """获取当前需要按下的按键
    
    根据黄色区域中心点与玩家位置的偏移，决定需要按下的方向键。
    
    Returns:
        str: 需要按下的按键（'a'、'd' 或空字符串）。
             空字符串表示未识别到结果，无需按键。
    """
    # 获取 x 坐标偏移值
    offset_x = calculate_the_offset_x()

    # 未识别到目标时的处理
    if offset_x is None:
        return ""

    if offset_x > OFFSET_THRESHOLD:
        press_key = "a"  # 偏右，按 A 左移
    elif offset_x < -OFFSET_THRESHOLD:
        press_key = "d"  # 偏左，按 D 右移
    else:
        press_key = ""  # 偏移小到无需处理

    return press_key


def calculate_the_offset_x() -> Optional[int]:
    """计算黄色区域中心点与玩家位置的 X 坐标偏移值
    
    获取黄色区域的两侧边界，计算其中心点，再用玩家位置减去中心点得到偏移值。
    
    Returns:
        Optional[int]: X 坐标偏移值。如果未检测到黄色区域或玩家位置，返回 None。
    """
    bar_area = get_yellow_area_range()
    player_pos = get_white_block_pos()
    # 防止未检测到时的 None 值中断程序，对 None 值进行处理
    if (bar_area is not None) and (player_pos is not None):
        bar_left, bar_right = bar_area
        fish_x = (bar_right + bar_left) // 2  # 黄色区域中心点
    else:
        return None

    return int(player_pos - fish_x)
