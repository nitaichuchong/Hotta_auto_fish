import cv2
import win32gui


def print_all_windows():
    """
    打印所有可见窗口的句柄和标题
    """

    def callback(handle, extra):
        if win32gui.IsWindowVisible(handle):
            title = win32gui.GetWindowText(handle)
            if title:
                print(f"句柄：{handle}，标题：{title}")
        return True

    win32gui.EnumWindows(callback, None)

def get_handle_by_title(window_title):
    """
    根据窗口标题获取窗口句柄
    :param window_title: 窗口标题
    :return: 窗口句柄
    """
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        raise ValueError(f"未找到标题为 {window_title} 的窗口")
    return hwnd


def get_window_class_by_title(window_title):
    """
    根据窗口标题获取窗口类名
    :param window_title: 窗口标题
    :return: 窗口类名
    """
    # 先找到窗口句柄
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        raise ValueError(f"未找到标题为 {window_title} 的窗口")

    class_name = win32gui.GetClassName(hwnd)
    print(f"窗口类名：{class_name}，窗口标题：{window_title}")


if __name__ == '__main__':
    print_all_windows()
    # 实际运行游戏后标题后有两个空格，或一个制表符，请根据实际情况调整
    # 请务必注意这一点，一定要在 print_all_windows() 后鼠标复制全名，而不仅仅是可见的标题部分
    # 否则可能会因为空格或制表符导致找不到窗口，或找到错误的窗口
    get_window_class_by_title("幻塔  ")
