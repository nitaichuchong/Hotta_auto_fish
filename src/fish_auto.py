from config import OFFSET_THRESHOLD
from src.detect_logic import get_yellow_area_range, get_white_block_pos


# 主函数
def key_to_press():
    """
    获取当前需要按下的按键
    :return: press_key : 当前需要按下的按键
    ""（空字符串）: 未识别到结果
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
        press_key = None  # 偏移小到无需处理

    return press_key


def calculate_the_offset_x():
    """
    获取黄色区域的两侧边界，并计算其中心点，
    再以玩家位置减去中心点得到 x 坐标偏移值
    :return: x 坐标偏移值
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
