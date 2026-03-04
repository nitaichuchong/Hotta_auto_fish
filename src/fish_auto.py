import threading
from time import sleep

import pyautogui

from config import OFFSET_THRESHOLD
from src.detect_logic import get_yellow_area_range, get_white_block_pos

# 按键操作锁
key_lock = threading.Lock()


# 主函数
def fish_game(pause_event, resume_event, stop_flag):
    """通过 x 坐标的偏移差，控制键盘的 A 和 D 进行操作

    :param pause_event: UI类传入的暂停事件标记
    :param resume_event: UI类传入的恢复事件标记
    :param stop_flag: UI类传入的终止事件标记
    """
    print("===== 钓鱼游戏逻辑开始执行 =====")

    current_key = None
    # pycharm 会提示未使用的变量，是因为在后续逻辑中，它被使用前必然已被赋予一个值
    # 但还是需要提前声明
    target_key = None

    # 检测暂停事件，若暂停则等待恢复
    while not stop_flag.is_set():
        if pause_event.is_set():
            # 若暂停标记被激活，松开当前按键
            if current_key is not None:
                with key_lock:  # 加锁
                    pyautogui.keyUp(current_key)
                print(f"暂停操作，松开按键：{current_key}")
                current_key = None
            # 等待恢复信号
            resume_event.wait()
            # 重置恢复信号为 False
            resume_event.clear()

            print("恢复自动操作")
            continue

        # 获取 x 坐标偏移值
        offset_x = calculate_the_offset_x()

        # 未检测到偏移则跳过防止报错
        if offset_x is None:
            print("未检测到黄色区域/玩家方块，跳过本次循环")
            sleep(0.05)
            continue

        if offset_x > OFFSET_THRESHOLD:
            target_key = 'a'  # 偏右，按 A 左移
        elif offset_x < -OFFSET_THRESHOLD:
            target_key = 'd'  # 偏左，按 D 右移
        else:
            target_key = None  # 偏移小到无需处理

        # 只有按键状态变化时才执行操作（避免重复按键或松开）
        if target_key != current_key:
            with key_lock:  # 加锁
                # 松开之前按下的键
                if current_key is not None:
                    pyautogui.keyUp(current_key)
                    print(f"松开按键：{current_key}")
                # 按下新的目标键
                if target_key is not None:
                    pyautogui.keyDown(target_key)
                    print(f"按下按键：{target_key}")

            # 更新当前按键状态
            current_key = target_key

            # 若偏移值小到无需控制，则短暂休眠
            if target_key is None:
                sleep(0.1)

        sleep(0.05)  # 降低CPU占用，且基本对响应速度无影响

    # 退出循环时确保按键已松开
    if current_key is not None:
        with key_lock:  # 加锁
            pyautogui.keyUp(current_key)
        print(f"程序终止，松开按键：{current_key}")


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
