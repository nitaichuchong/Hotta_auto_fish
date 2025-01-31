""" pyautogui 以及 keyboard 联合使用的测试程序"""

import pyautogui
import keyboard

from key_listen import key_q

if __name__ == '__main__':
    pyautogui.PAUSE = 0.2
    pyautogui.FAILSAFE = True

    keyboard.on_press(key_q)

    keyboard.wait("esc")
