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
