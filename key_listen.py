"""测试程序，按下 q 键就让鼠标单击一次"""

import pyautogui


def key_q(event):
    if event.name == 'q':
        pyautogui.click()
