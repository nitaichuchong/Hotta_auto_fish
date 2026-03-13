"""输入管理模块

提供统一的键鼠输入管理功能，支持前台模拟和后台消息两种模式。
"""
import time
from typing import Optional

import pyautogui
import win32con
import win32gui
from ctypes import Structure, windll, c_uint, sizeof, byref, POINTER

from config import USE_BACKGROUND_MODE


class InputManager:
    """统一的键鼠输入管理器
    
    支持前台模拟和后台消息两种模式的输入管理器。
    """

    def __init__(self, window_title: str = "幻塔  ", use_background_mode: bool = True):
        """初始化输入管理器
        
        Args:
            window_title (str): 目标窗口标题。
            use_background_mode (bool): 是否使用后台模式（True=后台，False=前台）。
        """
        self.window_title: str = window_title
        self.use_background_mode: bool = use_background_mode
        self.hwnd: Optional[int] = None

        if self.use_background_mode:
            self._find_window()

        # 虚拟键码映射表（支持大写和小写）
        self.KEY_CODES: dict = {
            # 数字键
            '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
            '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,
            # 字母键（同时支持大小写）
            'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45, 'F': 0x46,
            'G': 0x47, 'H': 0x48, 'I': 0x49, 'J': 0x4A, 'K': 0x4B, 'L': 0x4C,
            'M': 0x4D, 'N': 0x4E, 'O': 0x4F, 'P': 0x50, 'Q': 0x51, 'R': 0x52,
            'S': 0x53, 'T': 0x54, 'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58,
            'Y': 0x59, 'Z': 0x5A,
            'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46,
            'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
            'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52,
            's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
            'y': 0x59, 'z': 0x5A,
            # 特殊键
            'SPACE': 0x20,
            'SHIFT': 0x10,
            'CTRL': 0x11,
            'ALT': 0x12,
        }

    def _find_window(self) -> None:
        """查找并获取窗口句柄
        
        尝试通过窗口标题查找窗口并保存句柄。
        """
        try:
            self.hwnd = win32gui.FindWindow(None, self.window_title)
            if not self.hwnd:
                raise ValueError(f"未找到窗口：{self.window_title}")
        except Exception as e:
            print(f"[警告] 获取窗口句柄失败：{e}")
            self.hwnd = None

    def refresh_window(self) -> None:
        """刷新窗口句柄
        
        当窗口被重建或句柄失效时重新获取窗口句柄。
        """
        self._find_window()

    def set_mode(self, use_background_mode: bool) -> None:
        """设置输入模式
        
        Args:
            use_background_mode (bool): True=后台模式，False=前台模式。
        """
        self.use_background_mode = use_background_mode
        if use_background_mode and not self.hwnd:
            self._find_window()

    def press_key(self, key: str) -> Optional[bool]:
        """按下并松开一个按键
        
        Args:
            key (str): 按键名称，如 '1', 'A', 'SPACE'。
            
        Returns:
            Optional[bool]: 操作是否成功（后台模式），前台模式返回 None。
        """
        if self.use_background_mode:
            return self._background_key_press(key)
        else:
            self._foreground_key_press(key)
            return None

    def _background_key_press(self, key: str) -> bool:
        """后台模式：发送键盘消息到窗口
            
        Args:
            key (str): 按键名称。
                
        Returns:
            bool: 操作是否成功。
        """
        if not self.hwnd:
            self.refresh_window()
            if not self.hwnd:
                return False

        if key not in self.KEY_CODES:
            return False

        key_code = self.KEY_CODES[key]

        try:
            # 使用 PostMessage
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key_code, 0)
            time.sleep(0.05)
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, key_code, 0)
            return True
        except Exception as e:
            print(f"[错误] 发送后台按键失败：{e}")
            return False

    def _foreground_key_press(self, key: str) -> None:
        """前台模式：使用 pyautogui 模拟按键
            
        Args:
            key (str): 按键名称。
        """
        try:
            pyautogui.press(key.lower())
        except Exception as e:
            print(f"[错误] 发送前台按键失败：{e}")

    def click_mouse(self, x: Optional[int] = None, y: Optional[int] = None) -> Optional[bool]:
        """点击鼠标左键
        
        Args:
            x (Optional[int]): x 坐标（相对于窗口客户区），None 表示中心点。
            y (Optional[int]): y 坐标（相对于窗口客户区），None 表示中心点。
            
        Returns:
            Optional[bool]: 操作是否成功（后台模式），前台模式返回 None。
        """
        if self.use_background_mode:
            return self._background_mouse_click(x, y)
        else:
            self._foreground_mouse_click()
            return None

    def _background_mouse_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """后台模式：发送鼠标点击消息到窗口
        
        Args:
            x (Optional[int]): x 坐标（相对于窗口客户区），None 表示中心点。
            y (Optional[int]): y 坐标（相对于窗口客户区），None 表示中心点。
            
        Returns:
            bool: 操作是否成功。
        """

        if not self.hwnd:
            self.refresh_window()
            if not self.hwnd:
                return False

        try:
            # 如果未指定坐标，使用窗口中心点
            if x is None or y is None:
                rect = win32gui.GetClientRect(self.hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                x = width // 2
                y = height // 2

            # 打包坐标为 LPARAM
            lparam = (y << 16) | (x & 0xFFFF)

            # 使用 SendMessage（对前台窗口有效）
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
            time.sleep(0.05)
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lparam)
            return True

        except Exception as e:
            print(f"[错误] SendMessage 失败：{e}")
            return False

    def _foreground_mouse_click(self) -> None:
        """前台模式：使用 pyautogui 点击
        
        通过 pyautogui 模拟前台鼠标左键点击。
        """
        try:
            pyautogui.click()
        except Exception as e:
            print(f"[错误] 发送前台鼠标点击失败：{e}")

    def key_down(self, key: str) -> Optional[bool]:
        """按下按键（不松开）
        
        Args:
            key (str): 按键名称。
            
        Returns:
            Optional[bool]: 操作是否成功（后台模式），前台模式返回 None。
        """
        if self.use_background_mode:
            return self._background_key_down(key)
        else:
            self._foreground_key_down(key)
            return None

    def _background_key_down(self, key: str) -> bool:
        """后台模式：按下按键
        
        Args:
            key (str): 按键名称。
            
        Returns:
            bool: 操作是否成功。
        """
        if not self.hwnd:
            return False

        if key not in self.KEY_CODES:
            return False

        key_code = self.KEY_CODES[key]
        try:
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key_code, 0)
            return True
        except Exception as e:
            print(f"[错误] 发送后台按键按下失败：{e}")
            return False

    def _foreground_key_down(self, key: str) -> None:
        """前台模式：按下按键
        
        Args:
            key (str): 按键名称。
        """
        try:
            pyautogui.keyDown(key.lower())
        except Exception as e:
            print(f"[错误] 发送前台按键按下失败：{e}")

    def key_up(self, key: str) -> Optional[bool]:
        """松开按键
        
        Args:
            key (str): 按键名称。
            
        Returns:
            Optional[bool]: 操作是否成功（后台模式），前台模式返回 None。
        """
        if self.use_background_mode:
            return self._background_key_up(key)
        else:
            self._foreground_key_up(key)
            return None

    def _background_key_up(self, key: str) -> bool:
        """后台模式：松开按键
        
        Args:
            key (str): 按键名称。
            
        Returns:
            bool: 操作是否成功。
        """
        if not self.hwnd:
            return False

        if key not in self.KEY_CODES:
            return False

        key_code = self.KEY_CODES[key]
        try:
            win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, key_code, 0)
            return True
        except Exception as e:
            print(f"[错误] 发送后台按键松开失败：{e}")
            return False

    def _foreground_key_up(self, key: str) -> None:
        """前台模式：松开按键
        
        Args:
            key (str): 按键名称。
        """
        try:
            pyautogui.keyUp(key.lower())
        except Exception as e:
            print(f"[错误] 发送前台按键松开失败：{e}")


# 便捷函数
def create_input_manager(window_title: str = "幻塔  ", use_background_mode: bool = USE_BACKGROUND_MODE) -> InputManager:
    """创建输入管理器的便捷函数
    
    Args:
        window_title (str): 窗口标题。
        use_background_mode (bool): 是否使用后台模式。
        
    Returns:
        InputManager: 配置好的 InputManager 实例。
    """
    return InputManager(window_title, use_background_mode)
