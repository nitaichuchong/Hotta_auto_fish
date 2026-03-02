"""
这是一个简单的确定当前鼠标位置的小程序，
按下 i 键就会在终端中打印这是第几次按下，
以及当前鼠标位置
"""

import keyboard
import pyautogui

a = 0


def mouse_position(event):
    global a
    if event.name == 'i':
        print(pyautogui.position())
        print(a)
        a = a + 1

if __name__ == '__main__':
    pyautogui.PAUSE = 0.2
    pyautogui.FAILSAFE = True

    keyboard.on_press(mouse_position)


    keyboard.wait("esc")
