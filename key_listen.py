import pyautogui


def key_q(event):
    if event.name == 'q':
        pyautogui.click()
