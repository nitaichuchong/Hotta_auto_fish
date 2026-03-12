import ctypes
from ctypes import *
import cv2
import numpy as np
import win32gui
import time

# 加载 DLL
try:
    dxgi_capture = ctypes.CDLL("../src/utils/dxgi_capture.dll")
    print("DLL 加载成功")
except Exception as e:
    print(f"DLL 加载失败: {e}")
    exit(1)

# 定义函数原型
dxgi_capture.init_capture.argtypes = (c_void_p,)
dxgi_capture.init_capture.restype = None

dxgi_capture.capture_window.argtypes = (POINTER(c_ubyte), c_int, c_int, c_int, c_int)
dxgi_capture.capture_window.restype = POINTER(c_ubyte)

dxgi_capture.cleanup.argtypes = ()
dxgi_capture.cleanup.restype = None

# 获取窗口句柄
def get_window_handle(window_title):
    """根据窗口标题获取窗口句柄"""
    # 遍历所有窗口，找到标题匹配的窗口
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                windows.append((hwnd, title, width, height))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    
    # 显示所有窗口
    print("可用窗口列表:")
    for hwnd, title, width, height in windows:
        print(f"{hwnd}: {title} ({width}x{height})")
    
    # 查找标题为window_title的窗口
    for hwnd, title, width, height in windows:
        if title == window_title:
            print(f"找到窗口: '{title}' ({width}x{height})")
            return hwnd
    
    # 如果没有找到，尝试模糊匹配
    for hwnd, title, width, height in windows:
        if window_title in title:
            print(f"找到模糊匹配窗口: '{title}' ({width}x{height})")
            return hwnd
    
    print(f"未找到窗口 '{window_title}'")
    return None

# 枚举所有窗口
def enumerate_windows():
    """枚举所有顶级窗口"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append((hwnd, title))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    
    for hwnd, title in windows[:20]:  # 只显示前20个窗口
        print(f"{hwnd}: {title}")

# 获取窗口矩形
def get_window_rect(hwnd):
    """获取窗口的矩形区域"""
    # 尝试使用 DwmGetWindowAttribute 获取窗口真实大小
    try:
        import ctypes
        from ctypes import wintypes
        
        # 定义 RECT 结构
        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", wintypes.LONG),
                ("top", wintypes.LONG),
                ("right", wintypes.LONG),
                ("bottom", wintypes.LONG)
            ]
        
        # 加载 Dwmapi.dll
        dwmapi = ctypes.WinDLL("dwmapi")
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        
        # 获取窗口边界
        rect = RECT()
        result = dwmapi.DwmGetWindowAttribute(
            hwnd, 
            DWMWA_EXTENDED_FRAME_BOUNDS, 
            ctypes.byref(rect), 
            ctypes.sizeof(rect)
        )
        
        if result == 0:  # S_OK
            print(f"使用 DwmGetWindowAttribute 获取窗口大小: {rect.right - rect.left}x{rect.bottom - rect.top}")
            return rect.left, rect.top, rect.right, rect.bottom
    except Exception as e:
        print(f"使用 DwmGetWindowAttribute 失败: {e}")
    
    # 如果失败，使用 GetWindowRect
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    print(f"使用 GetWindowRect 获取窗口大小: {right - left}x{bottom - top}")
    return left, top, right, bottom

# 主函数
def main():
    # 设置目标窗口标题
    window_title = "幻塔"
    # window_title = "设置"
    
    # 获取窗口句柄
    hwnd = get_window_handle(window_title)
    if not hwnd:
        return
    
    # 设置进程 DPI 感知
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        print("DPI 感知设置成功")
    except Exception as e:
        print(f"DPI 感知设置失败: {e}")
    
    # 初始化捕获
    print("初始化捕获...")
    dxgi_capture.init_capture(hwnd)
    print("捕获初始化完成")
    
    # 获取窗口大小
    left, top, right, bottom = get_window_rect(hwnd)
    window_width = right - left
    window_height = bottom - top
    
    # 使用固定大小进行捕获
    capture_width = 1920
    capture_height = 1080
    
    print(f"窗口大小: {window_width}x{window_height}")
    print(f"捕获大小: {capture_width}x{capture_height}")
    
    # 分配缓冲区
    buffer = np.zeros((capture_height, capture_width, 4), dtype=np.uint8)
    buffer_ptr = buffer.ctypes.data_as(POINTER(c_ubyte))
    
    # 捕获一次
    print("开始捕获窗口...")
    result = dxgi_capture.capture_window(buffer_ptr, 0, 0, capture_width, capture_height)
    
    if result:
        # 转换为 OpenCV 格式 (BGRA to BGR)
        img = cv2.cvtColor(buffer, cv2.COLOR_BGRA2BGR)
        
        # 保存截图
        output_path = "result.png"
        cv2.imwrite(output_path, img)
        print(f"截图已保存为: {output_path}")
        print("截图验证完成")
    else:
        print("捕获失败")
    
    # 清理资源
    print("清理资源...")
    dxgi_capture.cleanup()
    print("资源清理完成")

if __name__ == "__main__":
    main()
    # enumerate_windows()