import pygetwindow
import win32con
import win32gui


def set_window_topmost(hwnd, is_topmost=True):
    """
    使用 Windows API 设置窗口置顶，类似 tk 的 -topmost 效果
    这种置顶方式不会阻止其他窗口被激活，是"软置顶"
    
    :param hwnd: int 或 PySide6 窗口对象 : Windows 窗口句柄或 Qt 窗口对象
    :param is_topmost: bool : 是否置顶，True 为置顶，False 为取消置顶
    """
    # 如果是 Qt 窗口对象，转换为 HWND
    if hasattr(hwnd, 'winId'):
        hwnd = int(hwnd.winId())
    
    if is_topmost:
        # HWND_TOPMOST = -1，设置为置顶窗口
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    else:
        # HWND_NOTOPMOST = -2，取消置顶
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


def activate_game_window(game):
    """
    激活游戏窗口，确保操作在游戏窗口上执行
    :param game: str : 需要激活的游戏窗口名
    """
    # 激活游戏窗口
    try:
        print(f"正在激活游戏窗口：{game}")
        game_window = pygetwindow.getWindowsWithTitle(game)[0]
        print(f"游戏窗口已激活：{game_window.title}")
        game_window.activate()
    except (IndexError, Exception) as e:
        print(f"激活游戏窗口失败：{e}")


def is_window_foreground(window_title="幻塔  "):
    """
    检查指定窗口是否在前台
    :param window_title: str : 需要检查的窗口标题
    :return: bool : True 如果窗口在前台，False 否则
    """
    try:
        foreground_window = win32gui.GetForegroundWindow()
        foreground_title = win32gui.GetWindowText(foreground_window)
        return foreground_title == window_title
    except Exception as e:
        print(f"检查窗口是否在前台失败：{e}")
        return False