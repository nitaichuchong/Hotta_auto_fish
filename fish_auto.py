from time import sleep

import cv2
import numpy as np
import pyautogui

from config import FISH_GAME_REGION
from utils import capture_screen, convert_to_hsv, find_contours, count_yellow_pixels


# 主函数
def fish_game(click_event):
    """
    钓鱼游戏的核心逻辑：
    1.如何寻找白色轮廓：先转换为灰度图像，然后做二值化处理，即剔除其它颜色只留白色方框，
                    然后就可以用轮廓检测来得到代表玩家的白框位置
    2.如何简化游戏逻辑：由于钓鱼游戏的进行方式是白框位于黄框内才算成功，而玩家控制白框
                    尽可能满足条件，所以程序逻辑可以被转换为白框向黄框移动。又由于
                    游戏只有 A 和 D 两个键控制方向，因此可以将游戏逻辑简化为计算以
                    白框中心为分界线的左右两块区域的黄色像素数量，哪边更黄就往哪边移动
    3.具体的移动逻辑：一些简单的数量多少判断，并用 pyautogui 库实现相应操作
    4.循环进行钓鱼：通过全局的 event 事件来控制，依然使用 pyautogui
    :param click_event: 控制是否收杆钓下一条鱼的 threading.Event()
    """
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
        if click_event.is_set():    # 是否已被 set
            pyautogui.press('1')
            sleep(2)
            pyautogui.click()
            sleep(2)
            pyautogui.press('1')
            click_event.clear()




    # 显示原始截图和HSV截图（可选）
    # cv2.imshow('Original Screen', screen)
    # cv2.imshow('HSV Screen', hsv_screen)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    # sleep(0.2)

    # cv2.destroyAllWindows()