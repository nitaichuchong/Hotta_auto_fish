from time import sleep

import pyautogui

from config import FISH_GAME_REGION
from src.detect_logic import capture_screen, convert_to_hsv, find_contours, count_yellow_pixels


# 主函数
def fish_game(click_event):
    # 控制按键状态的开关
    left_keydown = False
    right_keydown = False
    # 从配置文件获取对应的region
    fish_region = FISH_GAME_REGION

    while True:
        # 捕获目标区域的截图
        screen = capture_screen(fish_region)
        # 寻找白色方块轮廓
        white_block_rect = find_contours(screen)
        # 将截图转换为HSV颜色空间
        hsv_screen = convert_to_hsv(screen)

        # 若白色方块不为空，即表示已开始游戏，继续执行代码
        if white_block_rect is not None:
            # 获取左右两侧黄色像素数量
            yellow_left, yellow_right = count_yellow_pixels(hsv_screen, white_block_rect)

            # left - right 表示左侧黄色像素比右侧至少多 100，应往左移动
            if (yellow_left - yellow_right) > 100:
                # 利用开关处理用 keyDown 按下按键后何时 KeyUp 的问题
                if right_keydown:
                    pyautogui.keyUp('d')
                    # keyUp 记得重置开关
                    right_keydown = False
                    # 按下按键，并打开开关 left_keyDown
                pyautogui.keyDown('a')
                left_keydown = True
            # right - left 表示右侧黄色像素比左侧至少多 100，应往左移动
            elif (yellow_right - yellow_left) > 100:
                # 相似的逻辑
                if left_keydown:
                    pyautogui.keyUp('a')
                    left_keydown = False
                pyautogui.keyDown('d')
                right_keydown = True
            # 不满足上述任一条件表明在可接受范围内，原地停留
            else:
                # 将所有按键释放，并重置开关
                if left_keydown:
                    pyautogui.keyUp('a')
                    left_keydown = False
                if right_keydown:
                    pyautogui.keyUp('d')
                    right_keydown = False

        # click_event.set() 在鱼耐力识别中进行，当鱼耐力为 0 就会被 set
        # 依照游戏逻辑依次按下不同键即可，并记得 clear
        if click_event.is_set():  # 是否已被 set
            pyautogui.press('1')
            sleep(2)
            pyautogui.click()
            sleep(2)
            pyautogui.press('1')
            click_event.clear()
