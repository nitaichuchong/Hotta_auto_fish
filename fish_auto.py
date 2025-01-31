from time import sleep

import cv2
import numpy as np
import pyautogui

from config import FISH_GAME_REGION
from utils import capture_screen, convert_to_hsv, find_contours, count_yellow_pixels


# 主函数
if __name__ == "__main__":
    # 控制按键状态的开关
    left_keyDown = False
    right_keyDown = False
    # 从配置文件获取对应的region
    fish_region = FISH_GAME_REGION

    while True:
        # 捕获目标区域的截图
        screen = capture_screen(fish_region)
        # 将截图转换为HSV颜色空间
        hsv_screen = convert_to_hsv(screen)
        # 寻找白色方块轮廓
        white_block_rect = find_contours(screen)

        # 若白色方块不为空，即表示已开始游戏，继续执行代码
        if white_block_rect is not None:
            # 获取左右两侧黄色像素数量
            yellow_left, yellow_right = count_yellow_pixels(hsv_screen, white_block_rect)

            print(yellow_left, yellow_right)

            # left - right 表示左侧黄色像素比右侧至少多 100，应往左移动
            if (yellow_left - yellow_right) > 100:
                # 利用开关处理用 keyDown 按下按键后何时 KeyUp 的问题
                if right_keyDown:
                    pyautogui.keyUp('d')
                    # keyUp 记得重置开关
                    right_keyDown = False
                    # 按下按键，并打开开关 left_keyDown
                pyautogui.keyDown('a')
                left_keyDown = True

            # right - left 表示右侧黄色像素比左侧至少多 100，应往左移动
            elif (yellow_right - yellow_left) > 100:
                # 相似的逻辑
                if left_keyDown:
                    pyautogui.keyUp('a')
                    left_keyDown = False
                pyautogui.keyDown('d')
                right_keyDown = True

            # 不满足上述任一条件表明在可接受范围内，原地停留
            else:
                # 将所有按键释放，并重置开关
                if left_keyDown:
                    pyautogui.keyUp('a')
                    left_keyDown = False
                if right_keyDown:
                    pyautogui.keyUp('d')
                    right_keyDown = False

    # 显示原始截图和HSV截图（可选）
    # cv2.imshow('Original Screen', screen)
    # cv2.imshow('HSV Screen', hsv_screen)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    # sleep(0.2)

    # cv2.destroyAllWindows()