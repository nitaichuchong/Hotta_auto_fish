from time import sleep

import pyautogui

from src.detect_logic import get_yellow_area_range, get_white_block_pos


# 主函数
def fish_game():
    """通过 x 坐标的偏移差，控制键盘的 A 和 D 进行操作"""
    # 用来标记当前按键状态（用状态机思想控制，清晰并简化按键逻辑）
    current_key = None
    target_key = None

    while True:
        offset_x = calculate_the_offset_x()

        # 未检测到偏移则跳过防止报错
        if offset_x is None:
            continue

        if offset_x > 5:
            target_key = 'a'  # 偏右，按A左移
        elif offset_x < -5:
            target_key = 'd'  # 偏左，按D右移
        else:
            target_key = None

        # 只有按键状态变化时才执行操作（避免重复按键或松开）
        if target_key != current_key:
            # 松开之前按下的键
            if current_key is not None:
                pyautogui.keyUp(current_key)
            # 按下新的目标键
            if target_key is not None:
                pyautogui.keyDown(target_key)

            # 更新当前按键状态
            current_key = target_key

            # 若偏移值小到无需控制，则短暂休眠
            if target_key is None:
                sleep(0.1)


def calculate_the_offset_x():
    """
    获取黄色区域的两侧边界，并计算其中心点，
    再以玩家位置减去中心点得到 x 坐标偏移值
    :return: x 坐标偏移值
    """
    # 防止未检测到时的 None 值中断程序
    bar_area = get_yellow_area_range()
    player_pos = get_white_block_pos()
    # 对 None 值进行处理
    if (bar_area is not None) and (player_pos is not None):
        bar_left, bar_right = get_yellow_area_range()
        fish_x = (bar_right + bar_left) // 2  # 黄色区域中心点
        player_pos = get_white_block_pos()  # 玩家位置
    else:
        print("None")
        return None

    return int(player_pos - fish_x)


fish_game()
